import json
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.prompts import RAG_PROMPT
from app.core.vector_engine import engine
from app.core.llm_client import llm
from models import ServiceGuide, Resource


def _parse_payload(intent: str) -> str:
    return intent.split(':', 1)[-1].strip() if ':' in intent else ''


def handle_process(db: Session, intent: str):
    standard_title = _parse_payload(intent)
    guide = db.query(ServiceGuide).filter(ServiceGuide.title == standard_title).first()

    if not guide:
        return (
            f'抱歉,在我的资源库中暂时没有找到与"{standard_title}"相关的办事指南。',
            'SHOW_PROCESS',
            None,
        )

    process_data = {
        'title': guide.title,
        'dept': guide.dept_name,
        'conditions': json.loads(guide.conditions),
        'materials': json.loads(guide.materials),
        'steps': json.loads(guide.flow_steps),
        'address': guide.address,
        'latlng': guide.latlng,
        'office_time': guide.office_time,
        'phone': guide.phone,
    }
    answer = f'没问题,我已为您调取了【{guide.title}】的办事指南,您可以参考右侧的办理流程和材料清单。'
    return answer, 'SHOW_PROCESS', process_data


def handle_map(db: Session, intent: str):
    search_keyword = _parse_payload(intent)

    query = db.query(Resource)

    if search_keyword and search_keyword.upper() != 'NONE':
        query = query.filter(
            or_(
                Resource.name.contains(search_keyword),
                Resource.tags.contains(search_keyword),
                Resource.category.contains(search_keyword),
            )
        )

    resources = query.limit(5).all()

    if not resources:
        return (
            f'抱歉,在我的资源库中暂时没有找到与"{search_keyword}"相关的已认证服务点。',
            'DEFAULT',
            [],
        )

    map_data = [
        {
            'name': r.name,
            'latlng': r.latlng,
            'address': r.address,
            'phone': r.phone,
        }
        for r in resources
    ]
    return '已为您在右侧地图标注了相关的公共服务网点。', 'SHOW_MAP', map_data


def handle_rag(user_query: str):
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

    rag_prompt = RAG_PROMPT.format(
        context_text=context_text, user_query=user_query
    )
    answer = llm.ask(rag_prompt)

    ui_cmd = 'SHOW_TRACE' if docs_info else 'DEFAULT'
    return answer, ui_cmd, docs_info, sources


def handle_chat(user_query: str):
    return llm.ask(user_query)


def handle_rag_stream(user_query: str):
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
        context_text=context_text, user_query=user_query
    )

    def generate():
        yield {'type': 'meta', 'ui_command': ui_cmd, 'docs_info': docs_info, 'sources': sources}
        for token in llm.ask_stream(rag_prompt):
            yield {'type': 'token', 'content': token}
        yield {'type': 'done'}

    return generate()


def handle_chat_stream(user_query: str):
    def generate():
        yield {'type': 'meta', 'ui_command': 'DEFAULT'}
        for token in llm.ask_stream(user_query):
            yield {'type': 'token', 'content': token}
        yield {'type': 'done'}

    return generate()
