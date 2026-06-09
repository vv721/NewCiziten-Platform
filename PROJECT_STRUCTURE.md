# 市民智慧融合平台 · 项目结构文档

## 1 项目概览

**核心理念**：「对话即服务」—— 以自然语言对话为统一入口，整合政策问答、办事导航、资源地图三大业务能力。

**技术栈**：Vue 3 + FastAPI + SQLite/ChromaDB + DeepSeek API + BGE-base-zh + 高德 JS API

---

## 2 系统架构与数据流

```
┌─ 浏览器 ─────────────────────────────────────────────────────┐
│  Vue 3 SPA                                                    │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │ 左侧栏    │  │  中间对话区   │  │  右侧功能面板（轮播）     │ │
│  │ 历史会话  │  │  MessageList │  │  政策溯源 / 地图 / 办事  │ │
│  │ 新建/切换 │  │  InputBox    │  │  FeatureCarousel        │ │
│  └──────────┘  └──────┬───────┘  └───────────┬─────────────┘ │
│                       │  SSE fetch           │ watch 响应     │
└───────────────────────┼──────────────────────┼───────────────┘
                        │                      │
════════════════════════╪══════════════════════╪════════════════
                        ▼                      ▼
┌─ FastAPI 后端 ───────────────────────────────────────────────┐
│                                                               │
│  main.py (API 入口)                                           │
│  ├─ /api/chat          POST  核心对话接口                      │
│  ├─ /login             POST  用户认证                         │
│  ├─ /api/register      POST  注册                            │
│  └─ /api/conversations CRUD  会话管理                        │
│         │                                                     │
│         ▼                                                     │
│  ┌─────────────────┐                                         │
│  │ classify_intent  │  Function Calling 路由                  │
│  │ → show_process   │  → handle_process_stream               │
│  │ → show_map       │  → handle_map_stream                   │
│  │ → search_policy  │  → handle_rag_stream                   │
│  │ → chat           │  → handle_chat_stream                  │
│  └────────┬────────┘                                         │
│           ▼                                                   │
│  ┌─────────────────┐                                         │
│  │ LLMClient       │  OpenAI SDK → DeepSeek API              │
│  │ ask_stream()    │  流式生成                                │
│  │ classify_intent │  Function Calling                       │
│  │ _build_messages │  拼接 [system, history, user]           │
│  └─────────────────┘                                         │
│                                                               │
│  数据层                                                       │
│  ├─ SQLite (SQLAlchemy)  → users, conversations, messages,   │
│  │                          documents, resources, service_guides
│  ├─ ChromaDB            → 政策文档语义向量                     │
│  └─ VectorEngine        → BGE-base-zh 嵌入 + 检索             │
└───────────────────────────────────────────────────────────────┘
```

---

## 3 核心业务流程

### 3.1 用户消息 → AI 回复（完整链路）

```
InputBox.vue                    main.py                   stream_builder.py
    │ 用户输入                     │                            │
    ├─ sendToAIStream() ────────► POST /api/chat              │
    │                             ├─ 新建/获取 convo_id        │
    │                             ├─ 生成标题 _gen_title()     │
    │                             ├─ 存储 user message         │
    │                             ├─ 构建 history (最近6条)     │
    │                             ├─ classify_intent()         │
    │                             │    ├─ show_process ──────► handle_process_stream()
    │                             │    ├─ show_map     ──────► handle_map_stream()
    │                             │    ├─ search_policy ─────► handle_rag_stream()
    │                             │    └─ chat         ──────► handle_chat_stream()
    │                             │                            │
    │                             │         ┌──────────────────┤
    │                             │         │ 查 DB / 向量库    │
    │                             │         │ 拼 prompt         │
    │                             │         │ llm.ask_stream() │
    │                             │         │ yield meta/token │
    │                             │         └────────┬─────────┘
    │                             │ ◄────────────────┘
    │ ◄── SSE stream ────────────┤
    │  onMeta → uiState 更新      │
    │  onToken → 逐字追加         │
    │  onDone → 存储 AI message   │
```

### 3.2 四种对话模式

| 模式 | LLM 意图 | 处理器 | 数据来源 | Prompt |
|------|----------|--------|----------|--------|
| 智能政策问答 | `search_policy` | `handle_rag_stream` | ChromaDB 向量检索 | `RAG_PROMPT` |
| 办事流程导航 | `show_process` | `handle_process_stream` | SQLite `service_guides` | `PROCESS_GUIDE_PROMPT` |
| 公共资源地图 | `show_map` | `handle_map_stream` | SQLite `resources` | `MAP_GUIDE_PROMPT` |
| 闲聊兜底 | `chat` | `handle_chat_stream` | 无 | 直接使用 `user_query` |

### 3.3 右侧面板联动

```
后端 meta 事件 { ui_command, data }
        │
        ▼
ChatArea.vue → uiState.dispatchCommand()
        │
        ├─ SHOW_TRACE   → citationList  → InfoTrace.vue 渲染溯源卡片
        ├─ SHOW_MAP     → mapPoints     → MapContainer.vue 动态打点
        ├─ SHOW_PROCESS → activeProcess → ServiceNavigation.vue 步骤清单
        └─ START_NAV    → navigationTarget → MapContainer 路径规划
```

---

## 4 函数目录

### 4.1 后端入口 · `main.py`

| 函数 | 职责 |
|------|------|
| `chat_endpoint(request, db)` | 核心对话 API，编排意图路由 → 流式生成 → SSE 推送 |
| `_sse_wrapper(event_gen, convo_id)` | 生成器 → SSE 格式转换，结束时存储 AI 消息 |
| `login(request, db)` | 用户名/密码验证，签发 JWT |
| `register(user_data, db)` | 用户注册，PBKDF2 密码哈希 |

### 4.2 LLM 客户端 · `llm_client.py`

| 函数 | 职责 |
|------|------|
| `LLMClient.ask_stream(prompt, system_message, history)` | 流式调用 DeepSeek，逐 token yield |
| `LLMClient.ask(prompt, system_message, history)` | 非流式调用，返回完整文本 |
| `LLMClient.classify_intent(user_query, tools, system_message, history)` | Function Calling 路由意图 |
| `LLMClient._build_messages(prompt, system_message, history)` | 构建 `[system, ...history, user]` 消息列表 |

### 4.3 流式处理器 · `stream_builder.py`

| 函数 | 职责 |
|------|------|
| `_haversine(lat1, lng1, lat2, lng2)` | 两点球面距离（公里） |
| `_build_process_text(guide)` | ServiceGuide → LLM 可读的结构化文本 |
| `_build_process_data(guide)` | ServiceGuide → 前端渲染字典 |
| `handle_process_stream(db, …)` | 查 ServiceGuide 匹配事项，拼 prompt 后流式解说 |
| `handle_map_stream(db, …)` | 模糊匹配 Resource 资源点，算距离排序后地图标点 |
| `handle_rag_stream(user_query, …)` | 向量检索政策文档，拼接上下文后 RAG 约束生成 |
| `handle_chat_stream(user_query, …)` | 不查数据，直接交由 LLM 自由回答 |

### 4.4 Prompt 模板 · `prompts/`

| 文件 | 常量 | 用途 |
|------|------|------|
| `intent.py` | `INTENT_ROUTING_PROMPT` | 意图路由 system prompt |
| | `INTENT_TOOL_DEFINITIONS` | Function Calling 工具定义（4 个函数） |
| `generation.py` | `RAG_PROMPT` | 政策问答生成模板（含背景知识） |
| | `PROCESS_GUIDE_PROMPT` | 办事导航生成模板（含办事数据） |
| | `MAP_GUIDE_PROMPT` | 地图搜索生成模板（含网点数据） |
| `utility.py` | `TITLE_GEN_PROMPT` | 会话标题生成模板 |
| `extraction.py` | `TEXT_EXTRACT_PROMPT` | 政务网页文本提取（管理端用） |
| | `VISION_STEP_PROMPT` | 流程图视觉解析（管理端用） |

### 4.5 向量检索引擎 · `vector_engine.py`

| 函数 | 职责 |
|------|------|
| `VectorEngine.search_knowledge(query, top_k)` | BGE 嵌入查询 → ChromaDB 余弦相似度检索 |
| `VectorEngine.file_to_vector(file_path, …)` | 文档加载 → 切片 → 嵌入 → 入库全流水线 |
| `VectorEngine.add_docs(texts, metadata, ids)` | 批量写入向量 |
| `VectorEngine.delete_vector_data(doc_id)` | 按文档 ID 删除全部分片 |
| `VectorEngine.preview_doc_chunks(doc_id, limit)` | 预览文档的前 N 个分片 |

### 4.6 数据模型 · `models.py`

| 模型（表） | 关键字段 | 说明 |
|-----------|----------|------|
| `User` | id, username, password, role | admin / user 双角色 |
| `Conversation` | id, title, user_id | 关联用户的多轮会话 |
| `Message` | id, convo_id, role, content, sources | user / ai 消息，含溯源引用 |
| `Document` | id, filename, file_path, status, chunk_count | 上传的政策文件 |
| `Resource` | id, name, category, latlng, phone, status | 公共服务资源点 |
| `ServiceGuide` | id, title, dept_name, conditions, materials, flow_steps, address, latlng | 办事指南结构化数据 |

### 4.7 认证 · `utils/auth.py`

| 函数 | 职责 |
|------|------|
| `AuthHandler.create_access_token(data)` | 生成 JWT（24h 过期） |
| `AuthHandler.verify_token(token)` | 验证并解码 JWT |

### 4.8 数据库连接 · `database.py`

| 函数 | 职责 |
|------|------|
| `get_db()` | FastAPI 依赖注入，yield SQLAlchemy session |

### 4.9 管理端路由 · `routers/admin.py`

| 函数 | 职责 |
|------|------|
| `verify_admin(authorization)` | JWT + role 校验，仅 admin 可访问 |
| `uploadDocs(…)` | 文件上传 + 自动向量化入库 |
| `get_docs(db)` | 知识文档列表 |
| `delete_doc(doc_id, db)` | 删除文档及关联向量数据 |
| `preview_doc(doc_id)` | 预览文档分片内容 |
| `get_all_users(…)` | 用户列表（含会话/消息统计） |
| `del_user(user_id, db)` | 删除用户 |
| `reset_user_password(user_id, data, db)` | 管理员重置用户密码 |
| `get_admin_resources(…)` | 资源点分页查询 |
| `search_amap_poi(…)` | 代理高德 POI 搜索 |
| `batch_import_resources(…)` | 批量导入资源点到待审核池 |
| `update_resource(res_id, …)` | 更新资源点信息 |
| `delete_resource(resource_id, …)` | 删除资源点 |

---

### 4.10 前端 API 层 · `api/`

| 文件 | 函数 | 职责 |
|------|------|------|
| `chat.js` | `sendToAIStream(msg, convoId, userId, callbacks)` | SSE 流式请求，fetch + ReadableStream 手动解析 |
| | `sendToAI(msg, convoId, userId)` | 非流式请求（标题生成等） |
| | `getConvos(userId)` | 获取历史会话列表 |
| | `createConvo(userId)` | 创建新会话 |
| | `getHistoryMessages(convoId)` | 获取会话历史消息 |
| | `renameConvo(id, title)` | 重命名会话 |
| | `deleteConvo(id)` | 删除会话 |
| `login.js` | `roleLogin(username, password)` | 登录请求 |
| `request.js` | `request` (axios 实例) | 基础请求封装 |
| `admin.js` | (admin 端 CRUD) | 知识库 / 用户 / 资源管理请求 |

### 4.11 前端全局状态 · `store/`

| 文件 | 导出 | 职责 |
|------|------|------|
| `uiState.js` | `uiState` (reactive) | 核心状态机：`activeMode`、`mapPoints`、`citationList`、`activeProcess`、`dispatchCommand()` |
| `userState.js` | `userState`, `login()`, `logout()` | 用户认证状态 + JWT 持久化 + 路由守卫 |
| `convoSwitch.js` | (会话状态) | 历史会话切换与管理 |
| `ragState.js` | (RAG 状态) | 溯源引用数据 |
| `resWinState.js` | (资源窗口状态) | 右侧面板窗口管理 |

### 4.12 前端核心组件

| 组件 | 文件 | 职责 |
|------|------|------|
| `ChatArea` | `ChatArea.vue` | 对话区主控：接收 SSE、调度 uiState、渲染消息 |
| `MessageList` | `MessageList.vue` | AI 回复 Markdown 渲染（DOMPurify 防 XSS） |
| `InputBox` | `InputBox.vue` | 用户输入框 + 发送触发 |
| `MapContainer` | `MapContainer.vue` | 高德地图：`watch mapPoints` → 动态打点、路径规划 |
| `ServiceNavigation` | `ServiceNavigation.vue` | 办事步骤清单 + 材料列表 + 导航触发 |
| `InfoTrace` | `InfoTrace.vue` | 政策溯源卡片列表 + 原文展开 |
| `LeftSidebar` | `LeftSidebar.vue` | 历史会话列表、新建/切换/删除 |
| `FeatureCarousel` | `FeatureCarousel.vue` | 右侧面板轮播容器 |
| `GreetingView` | `GreetingView.vue` | 新对话欢迎页（4 个模式入口胶囊） |

---

## 5 关键技术决策

| 决策点 | 方案 | 原因 |
|--------|------|------|
| 记忆机制 | 多轮对话历史直接注入 messages | 比查询重写更可靠，LLM 可见完整上下文 |
| 意图路由 | DeepSeek Function Calling | 替代手写规则，4 个 tools 覆盖全部模式 |
| 向量嵌入 | BGE-base-zh 本地 CPU 运行 | 中文语义优势，无需 GPU，数据不外传 |
| 前端渲染 | DOMPurify 净化 Markdown | 防范 LLM 输出中的 XSS |
| 认证 | JWT + PBKDF2 密码哈希 | 无状态认证，前后端分离友好 |
