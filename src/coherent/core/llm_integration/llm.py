import getpass
import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Any
    
def get_llm(provider: str = "google"):
    if provider == "groq":
        if "GROQ_API_KEY" not in os.environ:
            os.environ["GROQ_API_KEY"] = getpass.getpass("Enter your Groq API key: ")
    
        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=1,
            max_tokens=8192,
            top_p=1,
        reasoning_format="parsed",
        timeout=None,
        max_retries=2
    )
    elif provider == "google":
        if "GEMINI_API_KEY" not in os.environ:
            os.environ["GEMINI_API_KEY"] = getpass.getpass("Enter your Google Gemini API key: ")
    
        llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite",
            temperature = 1,
            #max_output_tokens=8192,
            #top_p=1,
            timeout=30,
            thinking_level="low",
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    return llm


def extract_text_content(content: Any) -> str:
    """Extracts plain text safely whether content is str, list of parts, or dicts."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
            elif hasattr(block, "text"):
                parts.append(block.text)
        return "".join(parts)
    return str(content)