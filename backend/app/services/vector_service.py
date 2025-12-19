from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings


class VectorService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model = "text-embedding-3-small",
            openai_api_key=settings.openai_api_key
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1200,
            chunk_overlap = 300,
            length_function = lambda x: len(x.encode("utf-8")),
            separators=["\n\n", "\n", "。", "！", "？", ".", " ", ""]
        )