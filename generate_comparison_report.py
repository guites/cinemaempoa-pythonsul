import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core.base.llms.types import ChatMessage
from llama_index.llms.deepseek import DeepSeek
from llama_index.llms.google_genai import GoogleGenAI

from comparison_data_loader import load_and_clean_movies_docs
from comparison_prompt import build_comparison_prompt

POSTS_DIR = Path("./posts")
FIELDS_TO_REMOVE = ["image_url", "general_info", "director", "classification", "excerpt"]

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
MISTRAL_AI_API_KEY = os.getenv("MISTRAL_AI_API_KEY")

MODELS = {
    "deepseek": "deepseek-chat",
    "gemini": "gemini-2.5-flash",
}

for post_dir in POSTS_DIR.iterdir():
    JSON_DIR = post_dir
    cleaned_documents = load_and_clean_movies_docs(JSON_DIR, FIELDS_TO_REMOVE)

    comparison_prompt = build_comparison_prompt(cleaned_documents)

    messages = [
        ChatMessage(
            role="system",
            content="You are an expert data analyst specializing in comparing LLM outputs.",
        ),
        ChatMessage(
            role="user",
            content=comparison_prompt,
        ),
    ]

    # deepseek = DeepSeek(model=MODELS.get("deepseek"), api_key=DEEPSEEK_API_KEY)
    # deepseek_response = deepseek.chat(messages)

    gemini = GoogleGenAI(model=MODELS.get("gemini"), api_key=GEMINI_API_KEY)
    gemini_response = gemini.chat(messages)

    # Get the markdown report
    # markdown_report = deepseek_response.message.content
    markdown_report = gemini_response.message.content

    # Print to console
    print(markdown_report + "\n")

    # Numeric-only time (hours, minutes, seconds)
    timestamp = datetime.now().strftime("%H%M%S")

    # Save to file
    # with open(f"results/llm_comparison_report_{timestamp}.md", "w", encoding="utf-8") as file:
    #     file.write(markdown_report)

    # with open(f"results/llm_comparison_report.md", "a", encoding="utf-8") as file:
    #     file.write(markdown_report)
