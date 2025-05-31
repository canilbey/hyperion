import logging
from typing import List, Dict, Optional
from uuid import UUID
from databases import Database
import json
from datetime import datetime
from .context_types import Context, ContextMetadata, Message

class ContextStorageService:
    def __init__(self, database: Database, redis=None):
        self.database = database
        self.redis = redis
        self.logger = logging.getLogger(__name__)

    def _serialize_context_messages(self, messages):
        serialized = []
        for m in messages:
            d = m.dict() if hasattr(m, 'dict') else dict(m)
            if hasattr(d['role'], 'value'):
                d['role'] = d['role'].value
            if d.get('timestamp'):
                if hasattr(d['timestamp'], 'isoformat'):
                    d['timestamp'] = d['timestamp'].isoformat()
                else:
                    d['timestamp'] = str(d['timestamp'])
            serialized.append({k: v for k, v in d.items() if v is not None})
        return serialized

    async def create_context(
        self,
        chat_id: UUID,
        context: Context,
        metadata: Optional[Dict] = None
    ) -> UUID:
        """Yeni bir context oluştur"""
        query = """
            INSERT INTO chat_contexts (
                chat_id, context_window, token_count, metadata
            ) VALUES (
                :chat_id, :context_window, :token_count, :metadata
            ) RETURNING id
        """
        values = {
            "chat_id": str(chat_id),
            "context_window": json.dumps(
                self._serialize_context_messages(context.messages),
                default=str
            ),
            "token_count": context.metadata.max_tokens,
            "metadata": json.dumps(metadata or {})
        }
        context_id = await self.database.execute(query=query, values=values)
        await self._store_context_messages(context_id, context.messages)
        if self.redis:
            await self.redis.delete(f"chat:{chat_id}:context")
        return context_id

    async def get_context(self, chat_id: UUID) -> Optional[Context]:
        """Chat için context'i getir"""
        cache_key = f"chat:{chat_id}:context"
        
        # Cache'den dene
        if self.redis:
            try:
                cached = await self.redis.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    return Context(**data)
            except Exception as e:
                self.logger.warning(f"Cache okuma hatası: {str(e)}")

        # Veritabanından al
        query = """
            SELECT c.id, c.context_window, c.token_count, c.metadata, c.created_at
            FROM chat_contexts c
            WHERE c.chat_id = :chat_id
            ORDER BY c.created_at DESC
            LIMIT 1
        """
        row = await self.database.fetch_one(
            query=query,
            values={"chat_id": str(chat_id)}
        )
        
        if not row:
            return None
            
        # Context mesajlarını al
        messages = await self._get_context_messages(row["id"])
        
        # Parse metadata JSON string to dict
        metadata_dict = json.loads(row["metadata"]) if isinstance(row["metadata"], str) else row["metadata"]
        
        # Context oluştur
        context = Context(
            session_id=str(chat_id),
            messages=messages,
            metadata=ContextMetadata(
                model=metadata_dict.get("model"),
                temperature=metadata_dict.get("temperature", 0.7),
                max_tokens=row["token_count"],
                created_at=row["created_at"]
            )
        )
        
        # Cache'e kaydet
        if self.redis:
            try:
                await self.redis.setex(
                    cache_key,
                    3600,  # 1 saat TTL
                    json.dumps(context.dict())
                )
            except Exception as e:
                self.logger.warning(f"Cache yazma hatası: {str(e)}")
                
        return context

    async def update_context(
        self,
        chat_id: UUID,
        context: Context,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Context'i güncelle"""
        query = """
            SELECT id FROM chat_contexts
            WHERE chat_id = :chat_id
            ORDER BY created_at DESC
            LIMIT 1
        """
        row = await self.database.fetch_one(
            query=query,
            values={"chat_id": str(chat_id)}
        )
        if not row:
            await self.create_context(chat_id, context, metadata)
            return True
        update_query = """
            UPDATE chat_contexts
            SET context_window = :context_window,
                token_count = :token_count,
                metadata = :metadata,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :id
        """
        values = {
            "id": row["id"],
            "context_window": json.dumps(self._serialize_context_messages(context.messages)),
            "token_count": context.metadata.max_tokens,
            "metadata": json.dumps(metadata or {})
        }
        await self.database.execute(query=update_query, values=values)
        await self._update_context_messages(row["id"], context.messages)
        if self.redis:
            await self.redis.delete(f"chat:{chat_id}:context")
        return True

    async def _store_context_messages(self, context_id: UUID, messages: List[Message]):
        """Context mesajlarını kaydet"""
        query = """
            INSERT INTO chat_context_messages (
                context_id, role, content, token_count, created_at
            ) VALUES (
                :context_id, :role, :content, :token_count, :created_at
            )
        """
        for msg in messages:
            values = {
                "context_id": str(context_id),
                "role": msg.role,
                "content": msg.content,
                "token_count": len(msg.content.split()) * 2,  # Yaklaşık token sayısı
                "created_at": msg.timestamp or datetime.utcnow()
            }
            await self.database.execute(query=query, values=values)

    async def _get_context_messages(self, context_id: UUID) -> List[Message]:
        """Context mesajlarını getir"""
        query = """
            SELECT role, content, created_at
            FROM chat_context_messages
            WHERE context_id = :context_id
            ORDER BY created_at ASC
        """
        rows = await self.database.fetch_all(
            query=query,
            values={"context_id": str(context_id)}
        )
        
        return [
            Message(
                role=row["role"],
                content=row["content"],
                timestamp=row["created_at"]
            )
            for row in rows
        ]

    async def _update_context_messages(self, context_id: UUID, messages: List[Message]):
        """Context mesajlarını güncelle"""
        # Önce eski mesajları sil
        await self.database.execute(
            "DELETE FROM chat_context_messages WHERE context_id = :context_id",
            {"context_id": str(context_id)}
        )
        
        # Yeni mesajları ekle
        await self._store_context_messages(context_id, messages)

    async def delete_context(self, chat_id: UUID) -> bool:
        """Chat için context'i sil"""
        # Önce context ID'yi bul
        query = """
            SELECT id FROM chat_contexts
            WHERE chat_id = :chat_id
        """
        rows = await self.database.fetch_all(
            query=query,
            values={"chat_id": str(chat_id)}
        )
        
        if not rows:
            return False
            
        # Context mesajlarını sil
        for row in rows:
            await self.database.execute(
                "DELETE FROM chat_context_messages WHERE context_id = :context_id",
                {"context_id": str(row["id"])}
            )
        
        # Context'i sil
        await self.database.execute(
            "DELETE FROM chat_contexts WHERE chat_id = :chat_id",
            {"chat_id": str(chat_id)}
        )
        
        # Cache'i temizle
        if self.redis:
            await self.redis.delete(f"chat:{chat_id}:context")
            
        return True 