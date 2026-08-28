import os
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm(use_cloud=False):

    if use_cloud:
        return ChatOpenAI(
            model="openrouter/openai/gpt-oss-20b",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )

    return OllamaLLM(model="gemma2:2b")