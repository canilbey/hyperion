import asyncio
from databases import Database
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
async def run_migrations(database_url: str):
    """Run database migrations from SQL files"""
    db = Database(database_url)
    await db.connect()
    
    try:
        # Get all migration files in order
        migration_files = sorted(
            Path(__file__).parent.glob("*.sql"),
            key=lambda f: f.name
        )
        
        for migration in migration_files:
            logger.info(f"Running migration: {migration.name}")
            with open(migration) as f:
                sql = f.read()
                # Remove transaction blocks and split into individual statements
                sql = sql.replace('BEGIN;', '').replace('COMMIT;', '')
                statements = [
                    stmt.strip()
                    for stmt in sql.split(';')
                    if stmt.strip() and not stmt.strip().startswith('--')
                ]
                for stmt in statements:
                    try:
                        if stmt:  # Skip empty statements
                            await db.execute(stmt)
                    except Exception as e:
                        logger.error(f"Failed to execute statement in {migration.name}: {stmt[:50]}... Error: {str(e)}")
                        raise
                
        logger.info("Migrations completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise
    finally:
        await db.disconnect()

if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_migrations(os.getenv("DATABASE_URL")))