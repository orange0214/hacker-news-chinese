from fastapi import HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from typing import List, AsyncGenerator
from app.core.config import settings
from app.core.prompts import Prompts
from app.repositories.article_repository import article_repository
from app.schemas.chat import ChatMessage


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.gemini_api_key,
    temperature=0.3,
    streaming=True,
    convert_system_message_to_human = False
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", Prompts.SINGLE_CHAT_SYSTEM_PROMPT),
    MessagesPlaceholder("history"),
    ("human", "{message}")
])

class ChatService:
    async def get_article_context(self, article_id: int) -> dict:
        # get article context from database
        data = article_repository.get_article_by_id(article_id)
        if not data:
            raise HTTPException(status_code=404, detail="Article not found")

        return {
            "original_title": data.original_title,
            "original_text": data.original_text or "(No original text)",
            "raw_content": data.raw_content or "(No raw content)",
            "detailed_analysis": data.detailed_analysis.model_dump_json() if data.detailed_analysis else "(No detailed analysis)",
        }
    
    def _convert_history(self, history: List[ChatMessage]) -> List[BaseMessage]:
        lc_history = []
        for msg in history:
            if msg.role == "user":
                lc_history.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_history.append(AIMessage(content=msg.content))
        return lc_history
    
    async def stream_chat(self, article_id: int, message: str, history: List[ChatMessage]) -> AsyncGenerator[str, None]:
        article_data = await self.get_article_context(article_id)

        chain = prompt_template | llm | StrOutputParser()

        lc_history = self._convert_history(history)

        async for chunk in chain.astream({
            "original_title": article_data["original_title"],
            "original_text": article_data["original_text"],
            "raw_content": article_data["raw_content"],
            "detailed_analysis": article_data["detailed_analysis"],
            "history": lc_history,
            "message": message
        }):
            yield chunk

chat_service = ChatService()