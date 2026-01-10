from fastapi import HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from typing import List, AsyncGenerator, Optional, Dict
from app.core.config import settings
from app.core.prompts import Prompts
from app.core.logger import logger
from app.services.article_service import article_service
from app.services.vector_service import vector_service
from app.repositories.chat_repository import chat_repository
from app.schemas.chat import ChatMessage, ConversationSchema, ConversationMessageSchema
import asyncio


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

rewrite_prompt_template = ChatPromptTemplate.from_messages([
    ("system", Prompts.QUERY_REWRITE_SYSTEM),
    MessagesPlaceholder("history"),
    ("human", "{message}")
])

global_chat_prompt_template = ChatPromptTemplate.from_messages([
    ("system", Prompts.GLOBAL_CHAT_SYSTEM_PROMPT),
    MessagesPlaceholder("history"),
    ("human", "{message}")
])

class ChatService:
    
    def _convert_history(self, history: List[ChatMessage]) -> List[BaseMessage]:
        lc_history = []
        for msg in history:
            if msg.role == "user":
                lc_history.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_history.append(AIMessage(content=msg.content))
        return lc_history

    
    async def stream_chat(self, user_id: str, article_id: int, message: str, conversation_id: Optional[str] = None) -> AsyncGenerator[str, None]:
        if not conversation_id:
            conversation_id = await chat_repository.create_conversation(user_id, article_id, title="Chat with Article")
            if not conversation_id:
                logger.error("Failed to create conversation")
                yield f"event: error\ndata: Failed to create conversation\n\n"
                return
            yield f"event: new_conversation\ndata: {conversation_id}\n\n"
        
        await chat_repository.add_message(conversation_id, "user", message)
        await chat_repository.update_conversation_timestamp(conversation_id)

        chain = prompt_template | llm | StrOutputParser()
        
        raw_history_messages = await chat_repository.get_messages(conversation_id)
        history_objs = [ChatMessage(role=msg["role"], content=msg["content"]) for msg in raw_history_messages]
        lc_history = self._convert_history(history_objs)

        article_data = await asyncio.to_thread(article_service.get_article_context, article_id)

        full_ai_response = ""
        async for chunk in chain.astream({
            "original_title": article_data["original_title"],
            "original_text": article_data["original_text"],
            "raw_content": article_data["raw_content"],
            "detailed_analysis": article_data["detailed_analysis"],
            "history": lc_history,
            "message": message
        }):
            full_ai_response += chunk
            clean_chunk = chunk.replace("\n", "\\n")
            yield f"data: {clean_chunk}\n\n"
        
        if full_ai_response:
            await chat_repository.add_message(conversation_id, "assistant", full_ai_response)
        
        yield "event: stop\ndata: [DONE]\n\n"


    async def _rewrite_query(self, message: str, history: List[ChatMessage]) -> str:
        lc_history = self._convert_history(history)

        rewrite_chain = rewrite_prompt_template | llm | StrOutputParser()

        rewritten_query = await rewrite_chain.ainvoke({
            "history": lc_history,
            "message": message
        })

        return rewritten_query.strip()


    def _build_rag_context(self, search_results: List[dict]) -> str:
        if not search_results:
            return "数据库中暂无相关文章涉及此话题。"
            
        context_parts = []
        for i, res in enumerate(search_results):
            meta = res.get("metadata", {})
            title = meta.get("title", "Unknown Title")
            hn_id = meta.get("hn_id", "Unknown ID")
            chunk_content = res.get("content", "")
            
            part = f"--- Document {i+1} (Title: {title}, ID: {hn_id}) ---\n{chunk_content}\n"
            context_parts.append(part)
        
        return "\n".join(context_parts)


    async def stream_global_chat(self, user_id: str, message: str, conversation_id: Optional[str] = None) -> AsyncGenerator[str, None]:
        if not conversation_id:
            conversation_id = await chat_repository.create_conversation(user_id, article_id=None, title="Global Chat")
            if not conversation_id:
                logger.error("Failed to create global conversation")
                yield f"event: error\ndata: Failed to create conversation\n\n"
                return
            yield f"event: new_conversation\ndata: {conversation_id}\n\n"

        await chat_repository.add_message(conversation_id, "user", message)
        await chat_repository.update_conversation_timestamp(conversation_id)

        raw_history_messages = await chat_repository.get_messages(conversation_id)
        history_objs = [ChatMessage(role=msg["role"], content=msg["content"]) for msg in raw_history_messages]

        search_query = await self._rewrite_query(message, history_objs)
        # TODO: use a logger file to store all info
        logger.info(f"[GlobalChat] Original: {message} -> Rewritten: {search_query}")
        # limit can be edited in the frontend
        search_results = await vector_service.search_similar(search_query, limit = 5)
        context_str = self._build_rag_context(search_results)

        chain = global_chat_prompt_template | llm | StrOutputParser()
        lc_history = self._convert_history(history_objs)

        full_ai_response = ""
        async for chunk in chain.astream({
            "context": context_str,
            "history": lc_history,
            "message": message
        }):
            full_ai_response += chunk
            clean_chunk = chunk.replace("\n", "\\n")
            yield f"data: {clean_chunk}\n\n"
        
        if full_ai_response:
            await chat_repository.add_message(conversation_id, "assistant", full_ai_response)
        
        yield "event: stop\ndata: [DONE]\n\n"

    async def get_user_conversations(self, user_id: str, article_id: Optional[int] = None, skip: int = 0, limit: int = 20) -> List[ConversationSchema]:
        data = await chat_repository.get_user_conversations(user_id, article_id, skip, limit)
        return [ConversationSchema.model_validate(item) for item in data]
    
    async def get_conversation_messages_by_id(self, user_id: str, conversation_id: str) -> Optional[ConversationMessageSchema]:
        conversation = await chat_repository.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return None
        messages = await chat_repository.get_messages(conversation_id)
        msg_objs = [ChatMessage.model_validate(msg) for msg in messages]
        
        return ConversationMessageSchema(
            **conversation,
            messages=msg_objs
        )

chat_service = ChatService()