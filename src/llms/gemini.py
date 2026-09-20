"""
Google Gemini LLM initialization and configuration.
"""

import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY", "")

llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_CHAT_MODEL", "gemini-3.6-flash"),
    temperature=0,
)

# """
# LLM initialization and configuration.

# Uses Groq (fast inference, generous free tier) for chat/reasoning instead
# of Gemini, to avoid slow responses and Gemini's tight free-tier rate limits.
# Embeddings (for the retriever) still use Gemini separately in
# src/rag/retriever_setup.py — Groq doesn't offer an embeddings API.
# """

# import os

# from dotenv import load_dotenv
# from langchain_groq import ChatGroq

# load_dotenv()

# llm = ChatGroq(
#     model=os.getenv("GROQ_CHAT_MODEL", "openai/gpt-oss-20b"),
#     temperature=0,
#     api_key=os.getenv("GROQ_API_KEY", ""),
# )