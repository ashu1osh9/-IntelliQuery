"""
ReAct agent setup for document retrieval and question answering.
"""

import os

from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

from src.config.settings import Config
from src.llms.gemini import llm
from src.rag.retriever_setup import get_retriever

config = Config()

# Create ReAct agent prompt (static, safe to build once)
prompt = ChatPromptTemplate.from_messages([
    ("system", config.prompt("system_prompt")),
    ("human", "{input}"),
    ("ai", "{agent_scratchpad}")
])


def build_agent_executor() -> AgentExecutor:
    """
    Build a fresh ReAct agent executor bound to the CURRENT retriever.

    Rebuilding on every call (instead of caching a module-level singleton)
    matters here because get_retriever() reflects whatever document was
    most recently uploaded. A cached agent would keep pointing at whichever
    vectorstore existed when the module was first imported (often the
    empty "no documents uploaded yet" placeholder), even after a real
    document is uploaded later.

    Returns:
        A ready-to-invoke AgentExecutor wired to the latest retriever tool.
    """
    tools = [get_retriever()]

    react_agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=react_agent,
        tools=tools,
        handle_parsing_errors=True,
        max_iterations=2,
        verbose=True,
        return_intermediate_steps=True
    )