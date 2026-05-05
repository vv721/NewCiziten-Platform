import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatOpenAI(
    model_name="deepseek-chat",
    api_key=os.getenv("DeepSeek_API_Key"),
    base_url=os.getenv("DeepSeek_Base_URL")
)

prompttemplate = ChatPromptTemplate.from_messages([
    ("system", "你是一个服务助理，服务内容是为城市的新市民提供相关问题解答，你需要尽自己所能为用户提供合适的答案或者建议"),
    ("human", "{question}"),
])

async def ai_reply(question: str):
    chain = prompttemplate | llm
    resp = await chain.ainvoke({"question": question})
    return resp.content