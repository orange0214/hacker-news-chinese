from re import L
from app.db.supabase import get_supabase
from typing import Optional, List, Dict, Any
from app.core.logger import logger
from datetime import datetime

class ChatRepository:
    def __init__(self):
        self.conversation_table = "conversations"
        self.messages_table = "messages"
    
    @property
    def supabase(self):
        return get_supabase()
    
    # --- Conversations ---
    
    def create_conversation(self, user_id: str, article_id: Optional[int], title: Optional[str] = "New Chat") -> Optional[str]:
        try:
            payload = {
                "user_id": user_id,
                "article_id": article_id,
                "title": title,
            }
            result = self.supabase.table(self.conversation_table)\
                .insert(payload)\
                .select("id")\
                .single()\
                .execute()
            
            if result.data and "id" in result.data:
                return result.data["id"]
            return None
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            return None
    
    def get_user_conversations(self, user_id: str, article_id: Optional[int] = None, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            query = self.supabase.table(self.conversation_table)\
                .select("*")\
                .eq("user_id", user_id)
            
            if article_id:
                query = query.eq("article_id", article_id)

            result = query.order("updated_at", desc=True)\
                .range(skip, skip + limit - 1)\
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error fetching conversations: {e}")
            return []

    def get_conversation_by_id(self, conversation_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            result = self.supabase.table(self.conversation_table)\
                .select("*")\
                .eq("id", conversation_id)\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            return result.data if result.data else None
        except Exception as e:
            logger.error(f"Error fetching conversation by id: {e}")
            return None
    
    def update_conversation_timestamp(self, conversation_id: str) -> bool:
        try:
            self.supabase.table(self.conversation_table)\
                .update({"updated_at": datetime.now().isoformat()})\
                .eq("id", conversation_id)\
                .execute()
            return True
        except Exception as e:
            logger.error(f"Error updating conversation timestamp: {e}")
            return False

    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        try:
            self.supabase.table(self.conversation_table)\
                .delete()\
                .eq("id", conversation_id)\
                .eq("user_id", user_id)\
                .execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False
    
    # --- Messages ---

    def add_message(self, conversation_id: str, role: str, content: str) -> bool:
        try:
            payload = {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
            }
            self.supabase.table(self.messages_table)\
                .insert(payload)\
                .execute()
            return True
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            return False

    def get_messages(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            result = self.supabase.table(self.messages_table)\
                .select("*")\
                .eq("conversation_id", conversation_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
            return []