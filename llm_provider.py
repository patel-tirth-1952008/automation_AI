
from langchain_google_genai import ChatGoogleGenerativeAI
from config import Config


class LLMProvider:

    @staticmethod
    def get_llm():

        return ChatGoogleGenerativeAI(

            model=Config.OLLAMA_MODEL,

            base_url=Config.OLLAMA_BASE_URL,

            temperature=0
        )