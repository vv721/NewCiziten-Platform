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

llm = LLMClient()
