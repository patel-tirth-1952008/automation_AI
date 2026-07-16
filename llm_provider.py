
from langchain_google_genai import ChatGoogleGenerativeAI
from config import Config


class LLMProvider:

    @staticmethod
    def get_llm():

        return ChatGoogleGenerativeAI(

            model="gemini-2.5-flash",
            google_api_key=Config.GOOGLE_API_KEY,

            

            temperature=0
        )