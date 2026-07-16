
from langchain_google_genai import ChatGoogleGenerativeAI
from config import Config


class LLMProvider:

    @staticmethod
    def get_llm():

        return ChatGoogleGenerativeAI(

            model="gemini-2.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),

            base_url=Config.OLLAMA_BASE_URL,

            temperature=0
        )