"""
Google Gemini LLM initialization and configuration.
"""

import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY", "")

llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash"),
    temperature=0,
)
