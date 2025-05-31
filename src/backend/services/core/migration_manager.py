import asyncio
import logging
from pathlib import Path
from typing import List, Optional
from databases import Database

logger = logging.getLogger(__name__)

class MigrationManager:
    def __init__(self, database: Database, service_name: str):
        self.database = database
        self.service_name = service_name
        self.migrations_dir = Path(__file__).parent.parent / service_name / "migrations"
        
    async def run_migrations(self) -> None:
        """Run all migrations for this service (her komutu ayrı çalıştır, trigger/function dosyalarını tek parça çalıştır)"""
        if not self.migrations_dir.exists():
            logger.info(f"No migrations directory found for {self.service_name}")
            return
        migration_files = sorted(
            self.migrations_dir.glob("*.sql"),
            key=lambda f: f.name
        )
        if not migration_files:
            logger.info(f"No migration files found for {self.service_name}")
            return
        logger.info(f"Running migrations for {self.service_name}")
        for migration in migration_files:
            logger.info(f"Running migration: {migration.name}")
            with open(migration) as f:
                sql = f.read()
                # Eğer dosya adı trigger veya function içeriyorsa tek parça çalıştır
                if 'trigger' in migration.name or 'function' in migration.name:
                    try:
                        await self.database.execute(sql)
                    except Exception as e:
                        logger.error(f"Failed to execute migration file {migration.name} (tek parça) Error: {str(e)}")
                        raise
                else:
                    # Her komutu ';' ile ayırıp ayrı ayrı çalıştır
                    for cmd in sql.split(';'):
                        cmd = cmd.strip()
                        if cmd:
                            try:
                                await self.database.execute(cmd)
                            except Exception as e:
                                logger.error(f"Failed to execute migration command in file {migration.name}: {cmd[:80]}... Error: {str(e)}")
                                raise
        logger.info(f"Migrations completed for {self.service_name}")

    def _extract_table_name(self, create_table_stmt: str) -> Optional[str]:
        """Extract table name from CREATE TABLE statement"""
        try:
            # Simple extraction - assumes standard CREATE TABLE syntax
            parts = create_table_stmt.split()
            if len(parts) >= 3 and parts[0].upper() == 'CREATE' and parts[1].upper() == 'TABLE':
                # Handle IF NOT EXISTS case
                if parts[2].upper() == 'IF' and parts[3].upper() == 'NOT' and parts[4].upper() == 'EXISTS':
                    return parts[5]
                return parts[2]
        except Exception:
            pass
        return None

class ServiceMigrationManager:
    def __init__(self, database: Database):
        self.database = database
        self.services = ["auth", "chat", "model"]  # Add new services here
        
    async def run_all_migrations(self) -> None:
        """Run migrations for all services"""
        for service in self.services:
            try:
                manager = MigrationManager(self.database, service)
                await manager.run_migrations()
            except Exception as e:
                logger.error(f"Failed to run migrations for service {service}: {str(e)}")
                raise
            
    async def run_service_migrations(self, service_name: str) -> None:
        """Run migrations for a specific service"""
        if service_name not in self.services:
            raise ValueError(f"Unknown service: {service_name}")
            
        manager = MigrationManager(self.database, service_name)
        await manager.run_migrations() 