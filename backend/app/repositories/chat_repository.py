from app.db.supabase import get_supabase
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.core.logger import logger
from datetime import datetime
import asyncio
import json
from app.db.redis import get_redis

class ChatRepository:
    def __init__(self):
        self.conversation_table = "conversations"
        self.messages_table = "messages"
    
    @property
    def supabase(self):
        return get_supabase()
    
    # --- Conversations ---
    
    async def create_conversation(self, user_id: str, article_id: Optional[int], title: Optional[str] = "New Chat") -> Optional[str]:
        try:
            payload = {
                "user_id": user_id,
                "article_id": article_id,
                "title": title,
            }

            query = self.supabase.table(self.conversation_table)\
                .insert(payload)\
                .select("id")\
                .single()

            result = await asyncio.to_thread(query.execute())
            
            if result.data and "id" in result.data:
                return result.data["id"]
            return None
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            return None
    
    async def get_user_conversations(self, user_id: str, article_id: Optional[int] = None, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            query = self.supabase.table(self.conversation_table)\
                .select("*")\
                .eq("user_id", user_id)
            
            if article_id:
                query = query.eq("article_id", article_id)
            
            query = query.order("updated_at", desc=True)\
                .range(skip, skip + limit - 1)

            result = await asyncio.to_thread(query.execute)
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error fetching conversations: {e}")
            return []

    async def get_conversation_by_id(self, conversation_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            query = self.supabase.table(self.conversation_table)\
                .select("*")\
                .eq("id", conversation_id)\
                .eq("user_id", user_id)\
                .single()
            result = await asyncio.to_thread(query.execute)
            return result.data if result.data else None
        except Exception as e:
            logger.error(f"Error fetching conversation by id: {e}")
            return None
    
    async def update_conversation_timestamp(self, conversation_id: str) -> bool:
        try:
            query = self.supabase.table(self.conversation_table)\
                .update({"updated_at": datetime.now().isoformat()})\
                .eq("id", conversation_id)
            result = await asyncio.to_thread(query.execute)
            return True
        except Exception as e:
            logger.error(f"Error updating conversation timestamp: {e}")
            return False

    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        try:
            query = self.supabase.table(self.conversation_table)\
                .delete()\
                .eq("id", conversation_id)\
                .eq("user_id", user_id)
            await asyncio.to_thread(query.execute)

            redis = await get_redis()
            cache_key = f"chat:{conversation_id}"
            await redis.delete(cache_key)

            return True
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False
    
    # --- Messages ---

    async def add_message(self, conversation_id: str, role: str, content: str) -> bool:
        try:
            payload = {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
            }
            query = self.supabase.table(self.messages_table)\
                .insert(payload)
            await asyncio.to_thread(query.execute)

            redis = await get_redis()
            cache_key = f"chat:{conversation_id}"
            msg_data = json.dumps({"role": role, "content": content})
            await redis.rpush(cache_key, msg_data)
            await redis.expire(cache_key, settings.redis_cache_expire_seconds)
            
            return True
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            return False

    async def get_messages(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            redis = await get_redis()
            cache_key = f"chat:{conversation_id}"

            cached_data = await redis.lrange(cache_key, 0, -1)
            if cached_data:
                messages = [json.loads(msg) for msg in cached_data]
                if len(messages) > limit:
                    messages = messages[-limit:]
                return messages

            query = self.supabase.table(self.messages_table)\
                .select("*")\
                .eq("conversation_id", conversation_id)\
                .order("created_at", desc=True)\
                .limit(limit)
            result = await asyncio.to_thread(query.execute)

            messages = result.data if result.data else []

            if messages:
                # DB desc=True returns [latest, ..., oldest]
                # Redis needs [oldest, ..., latest] to append
                messages.reverse() 
                json_msgs = [json.dumps({"role": msg["role"], "content": msg["content"]}) for msg in messages]
                
                # To prevent data duplication or disorder, clear old cache first
                await redis.delete(cache_key) 
                await redis.rpush(cache_key, *json_msgs)
                await redis.expire(cache_key, settings.redis_cache_expire_seconds)
            
            return messages

        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
            return []

chat_repository = ChatRepository()