import logging
from typing import List, Dict, Optional
from uuid import UUID
from databases import Database
from backend.models import ChatMessage
import json

class ChatStorageService:
    def __init__(self, database: Database, redis=None):
        self.database = database
        self.redis = redis
        self.logger = logging.getLogger(__name__)
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'errors': 0
        }

    async def create_chat(self, label: Optional[str] = None) -> UUID:
        """Create a new chat session"""
        query = """
            INSERT INTO chats (label)
            VALUES (:label)
            RETURNING chat_id
        """
        values = {"label": label}
        chat_id = await self.database.execute(query=query, values=values)
        return chat_id

    async def add_message(
        self,
        chat_id: UUID,
        role: str,
        content: str,
        usage: Optional[Dict] = None,
        chat_name: Optional[str] = None
    ) -> int:
        """Add a message to an existing chat"""
        query = """
            INSERT INTO messages (chat_id, role, content, usage, chat_name)
            VALUES (:chat_id, :role, :content, :usage, :chat_name)
            RETURNING message_id
        """
        values = {
            "chat_id": str(chat_id),
            "role": role,
            "content": content,
            "usage": json.dumps(usage) if usage else None,
            "chat_name": chat_name
        }
        message_id = await self.database.execute(query=query, values=values)
        
        # Invalidate cache
        if self.redis:
            await self.redis.delete(f"chat:{chat_id}:messages")
            
        return message_id

    async def get_chat_history(
        self,
        chat_id: Optional[UUID] = None,
        chat_name: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """Retrieve chat message history by either chat_id or chat_name"""
        if not chat_id and not chat_name:
            raise ValueError("Either chat_id or chat_name must be provided")

        identifier = str(chat_id) if chat_id else chat_name
        cache_key = f"chat:{identifier}:messages:{limit or 'all'}"
        
        # Try cache first
        if self.redis:
            try:
                cached = await self.redis.get(cache_key)
                if cached:
                    await self.redis.expire(cache_key, 86400)  # Refresh TTL
                    return [ChatMessage(**msg) for msg in json.loads(cached)]
            except Exception as e:
                self.logger.warning(f"Cache read failed: {str(e)}")

        # Query database
        query = """
            SELECT role, content, usage, created_at
            FROM messages
            WHERE {condition}
            ORDER BY created_at DESC
            {limit}
        """.format(
            condition="chat_id = :identifier" if chat_id else "chat_name = :identifier",
            limit=f"LIMIT {limit}" if limit else ""
        )
        
        values = {"identifier": str(chat_id) if chat_id else chat_name}
        rows = await self.database.fetch_all(query=query, values=values)
        
        # Cache results
        if self.redis and rows:
            await self.redis.set(
                f"chat:{chat_id}:messages",
                json.dumps([dict(row) for row in rows]),
                expire=86400  # 24 hours
            )
            
        return [ChatMessage(**row) for row in rows]

    async def update_chat_label(self, chat_id: UUID, label: str) -> None:
        """Update chat session label"""
        query = """
            UPDATE chats
            SET label = :label
            WHERE chat_id = :chat_id
        """
        values = {"chat_id": str(chat_id), "label": label}
        await self.database.execute(query=query, values=values)

    async def list_chats(self) -> List[Dict]:
        """List all chat sessions with metadata"""
        cache_key = "chat:list:all"
        
        # Try cache first
        if self.redis:
            try:
                cached = await self.redis.get(cache_key)
                if cached:
                    await self.redis.expire(cache_key, 3600)  # Refresh TTL (1 hour)
                    return json.loads(cached)
            except Exception as e:
                self.logger.warning(f"Cache read failed: {str(e)}")

        # Query database
        query = """
            SELECT c.chat_id, c.label, c.created_at,
                   MAX(m.created_at) as last_message_time,
                   COUNT(m.message_id) as message_count
            FROM chats c
            LEFT JOIN messages m ON c.chat_id = m.chat_id
            GROUP BY c.chat_id
            ORDER BY last_message_time DESC
        """
        rows = await self.database.fetch_all(query=query)
        result = [dict(row) for row in rows]
        
        # Cache results
        if self.redis and result:
            try:
                await self.redis.set(
                    cache_key,
                    json.dumps(result),
                    expire=3600  # 1 hour
                )
            except Exception as e:
                self.logger.warning(f"Cache write failed: {str(e)}")
                
        return result

    async def update_chat(
        self,
        chat_id: Optional[UUID] = None,
        chat_name: Optional[str] = None,
        update_data: Optional[Dict] = None
    ) -> Dict:
        """Update chat metadata (label, tags, etc.)"""
        if not update_data:
            raise ValueError("No update data provided")
            
        if not chat_id and not chat_name:
            raise ValueError("Either chat_id or chat_name must be provided")

        # Build SET clause
        set_clause = ", ".join(f"{k} = :{k}" for k in update_data.keys())
        
        # Update chats table
        if 'label' in update_data:
            await self.database.execute(
                f"UPDATE chats SET {set_clause} WHERE chat_id = :identifier",
                {"identifier": str(chat_id) if chat_id else chat_name, **update_data}
            )

        # Update messages table if chat_name is being updated
        if 'chat_name' in update_data:
            await self.database.execute(
                "UPDATE messages SET chat_name = :new_name WHERE chat_id = :identifier",
                {
                    "identifier": str(chat_id) if chat_id else chat_name,
                    "new_name": update_data['chat_name']
                }
            )

        return await self.get_chat_metadata(chat_id or chat_name)

    async def delete_chat(
        self,
        chat_id: Optional[UUID] = None,
        chat_name: Optional[str] = None
    ) -> Dict:
        """Delete a chat session and all its messages"""
        if not chat_id and not chat_name:
            raise ValueError("Either chat_id or chat_name must be provided")

        # Get metadata before deletion
        metadata = await self.get_chat_metadata(chat_id or chat_name)
        
        # Delete messages first (due to foreign key constraint)
        await self.database.execute(
            "DELETE FROM messages WHERE chat_id = :identifier",
            {"identifier": str(chat_id) if chat_id else chat_name}
        )
        
        # Delete chat
        await self.database.execute(
            "DELETE FROM chats WHERE chat_id = :identifier",
            {"identifier": str(chat_id) if chat_id else chat_name}
        )
        
        # Invalidate cache
        if self.redis:
            await self.redis.delete(f"chat:{chat_id or chat_name}:messages")
            
        return {"status": "deleted", **metadata}

    async def get_chat_metadata(self, identifier: str) -> Dict:
        """Get chat metadata by ID or name"""
        try:
            from uuid import UUID
            chat_id = UUID(identifier)
            condition = "chat_id = :identifier"
        except ValueError:
            condition = "label = :identifier"
            
        query = f"""
            SELECT c.chat_id, c.label, c.created_at,
                   COUNT(m.message_id) as message_count
            FROM chats c
            LEFT JOIN messages m ON c.chat_id = m.chat_id
            WHERE {condition}
            GROUP BY c.chat_id
        """
        row = await self.database.fetch_one(query=query, values={"identifier": identifier})
        if not row:
            raise ValueError(f"Chat not found: {identifier}")
        return dict(row)