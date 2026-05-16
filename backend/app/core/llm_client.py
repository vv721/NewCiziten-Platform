import json
import openai
import os

from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("DeepSeek_API_Key"),
            base_url=os.getenv("DeepSeek_Base_URL")
        )

    def ask(self, prompt: str, system_message: str = "你是一个市民智慧服务助手"):
        response = self.client.chat.completions.create(
            model = "deepseek-chat",
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content

    def ask_stream(self, prompt: str, system_message: str = "你是一个市民智慧服务助手"):
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def classify_intent(self, user_query: str, tools: list, system_message: str = "你是一个政务服务调度专家"):
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_query},
            ],
            tools=tools,
            tool_choice="required",
            temperature=0,
        )
        tool_call = response.choices[0].message.tool_calls[0]
        return {
            "name": tool_call.function.name,
            "arguments": json.loads(tool_call.function.arguments),
        }

llm = LLMClient()
