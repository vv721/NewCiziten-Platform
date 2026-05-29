# ── 数据提取层 ──

TEXT_EXTRACT_PROMPT = """
你是一个政务数据提取专家。请从以下网页文本中提取核心办事信息，并严格以 JSON 格式输出。

### 要求提取字段：
- title: 事项全称
- dept_name: 受理部门/实施主体
- conditions: 申请条件列表 (Array of String)
- materials: 申报材料清单 (Array of Objects: {{"name": "...", "type": "原件/复印件", "paper_count": "1份", "form": "纸质/电子"}})
- address: 具体的线下办理地址
- office_time: 办公时间说明
- phone: 咨询电话（若无则填"暂无"）

### 原始文本：
{raw_text}

注意：只输出纯 JSON，不要 Markdown 标签，不要解释。
"""


VISION_STEP_PROMPT = """
分析这张政务办事流程图。将其拆解为逻辑有序的步骤列表。
严格按照以下 JSON 格式输出：
[
  {{"step": 1, "name": "步骤名称", "desc": "具体操作描述"}},
  ...
]
"""
