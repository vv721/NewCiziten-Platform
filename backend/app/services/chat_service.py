import json
from math import radians, sin, cos, sqrt, asin

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.prompts import RAG_PROMPT, PROCESS_GUIDE_PROMPT, MAP_GUIDE_PROMPT
from app.core.vector_engine import engine
from app.core.llm_client import llm
from models import ServiceGuide, Resource


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """返回两点间的球面距离（公里）。"""
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return r * (2 * asin(sqrt(a)))


def _build_process_text(guide) -> str:
    """将 ServiceGuide 序列化为 LLM 可读的结构化文本。"""
    conditions = json.loads(guide.conditions) if guide.conditions else []
    materials = json.loads(guide.materials) if guide.materials else []
    steps = json.loads(guide.flow_steps) if guide.flow_steps else []

    lines = [f"事项名称：{guide.title}"]
    if guide.dept_name:
        lines.append(f"受理部门：{guide.dept_name}")
    if conditions:
        lines.append(f"申请条件：{'；'.join(conditions)}")
    if steps:
        step_texts = [f"第{s['step']}步「{s['name']}」{s['desc']}" for s in steps]
        lines.append("办理流程：" + " → ".join(step_texts))
    if materials:
        mat_texts = [f"{m['name']}（{m.get('type', '')}，{m.get('paper_count', '')}）" for m in materials]
        lines.append("所需材料：" + "；".join(mat_texts))
    if guide.address:
        addr_line = f"办理地址：{guide.address}"
        if guide.office_time:
            addr_line += f"（办公时间：{guide.office_time}）"
        lines.append(addr_line)
    if guide.phone:
        lines.append(f"咨询电话：{guide.phone}")

    return '\n'.join(lines)


def _build_process_data(guide) -> dict:
    """从 ServiceGuide 构建前端所需的 process_data 字典。"""
    return {
        'title': guide.title,
        'dept': guide.dept_name,
        'conditions': json.loads(guide.conditions) if guide.conditions else [],
        'materials': json.loads(guide.materials) if guide.materials else [],
        'steps': json.loads(guide.flow_steps) if guide.flow_steps else [],
        'address': guide.address,
        'latlng': guide.latlng,
        'office_time': guide.office_time,
        'phone': guide.phone,
    }


# ── stream generators (unified interface) ──

def handle_process_stream(db: Session, service_name: str, user_query: str, active_mode: str, history: list[dict] = None):
    guide = db.query(ServiceGuide).filter(ServiceGuide.title == service_name).first()

    if not guide:
        def generate():
            yield {'type': 'meta', 'ui_command': 'SHOW_PROCESS', 'process_data': None}
            yield {'type': 'token', 'content': f'抱歉，在我的资源库中暂时没有找到与"{service_name}"相关的办事指南。'}
            yield {'type': 'done'}
        return generate()

    process_data = _build_process_data(guide)
    process_text = _build_process_text(guide)
    prompt = PROCESS_GUIDE_PROMPT.format(process_data=process_text, user_query=user_query, active_mode=active_mode)

    def generate():
        yield {'type': 'meta', 'ui_command': 'SHOW_PROCESS', 'process_data': process_data}
        for token in llm.ask_stream(prompt, history=history):
            yield {'type': 'token', 'content': token}
        yield {'type': 'done'}

    return generate()


def handle_map_stream(db: Session, keyword: str, user_query: str, active_mode: str, user_lat: float = None, user_lng: float = None, history: list[dict] = None):
    query = db.query(Resource)

    if keyword and keyword.upper() != 'NONE':
        query = query.filter(
            or_(
                Resource.name.contains(keyword),
                Resource.tags.contains(keyword),
                Resource.category.contains(keyword),
            )
        )

    resources = query.limit(5).all()

    if not resources:
        def generate():
            yield {'type': 'meta', 'ui_command': 'SHOW_MAP', 'map_data': []}
            yield {'type': 'token', 'content': f'抱歉，在我的资源库中暂时没有找到与"{keyword}"相关的已认证服务点。'}
            yield {'type': 'done'}
        return generate()

    has_user_pos = user_lat is not None and user_lng is not None

    map_data = []
    for r in resources:
        entry = {
            'name': r.name,
            'latlng': r.latlng,
            'address': r.address,
            'phone': r.phone,
        }
        if has_user_pos and r.latlng:
            try:
                lng, lat = map(float, r.latlng.split(','))
                entry['distance'] = round(_haversine(user_lat, user_lng, lat, lng), 1)
            except (ValueError, TypeError):
                entry['distance'] = None
        else:
            entry['distance'] = None
        map_data.append(entry)

    # 按距离排序（有位置时近的在前）
    if has_user_pos:
        map_data.sort(key=lambda m: m.get('distance') if m.get('distance') is not None else float('inf'))

    map_lines = []
    for m in map_data:
        line = f"{m['name']}（{m['address']}）"
        if m.get('distance') is not None:
            line = f"{m['name']}（{m['address']}，距您约{m['distance']}公里）"
        if m.get('phone'):
            line += f" 电话：{m['phone']}"
        map_lines.append(line)
    map_text = '\n'.join(map_lines)

    prompt = MAP_GUIDE_PROMPT.format(map_data=map_text, user_query=user_query, active_mode=active_mode)

    def generate():
        yield {'type': 'meta', 'ui_command': 'SHOW_MAP', 'map_data': map_data}
        for token in llm.ask_stream(prompt, history=history):
            yield {'type': 'token', 'content': token}
        yield {'type': 'done'}

    return generate()


def handle_rag_stream(user_query: str, active_mode: str, history: list[dict] = None):
    context_docs = engine.search_knowledge(user_query, top_k=5)

    docs_info = []
    context_chunks = []
    source_set = set()

    for doc in context_docs:
        content = doc['content']
        source_name = doc['metadata'].get('source', '未知文件')
        page_num = doc['metadata'].get('page', 0) + 1

        docs_info.append(
            {'content': content, 'source': source_name, 'page': page_num}
        )
        context_chunks.append(content)
        source_set.add(source_name)

    context_text = '\n'.join(context_chunks)
    sources = list(source_set)
    ui_cmd = 'SHOW_TRACE' if docs_info else 'DEFAULT'

    rag_prompt = RAG_PROMPT.format(
        context_text=context_text, user_query=user_query, active_mode=active_mode
    )

    def generate():
        yield {'type': 'meta', 'ui_command': ui_cmd, 'docs_info': docs_info, 'sources': sources}
        for token in llm.ask_stream(rag_prompt, history=history):
            yield {'type': 'token', 'content': token}
        yield {'type': 'done'}

    return generate()


def handle_chat_stream(user_query: str, active_mode: str, history: list[dict] = None):
    def generate():
        yield {'type': 'meta', 'ui_command': 'DEFAULT'}
        for token in llm.ask_stream(user_query, history=history):
            yield {'type': 'token', 'content': token}
        yield {'type': 'done'}

    return generate()
