import asyncio
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import Base, create_tables
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
    
    def create_database_if_not_exists(self):
        """Create database if it doesn't exist"""
        try:
            # Extract database name from URL
            db_name = settings.DATABASE_URL.split('/')[-1]
            base_url = settings.DATABASE_URL.rsplit('/', 1)[0]
            
            # Connect to default postgres database
            temp_engine = create_engine(f"{base_url}/postgres")
            
            with temp_engine.connect() as conn:
                # Check if database exists
                result = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                    {"db_name": db_name}
                )
                
                if not result.fetchone():
                    logger.info(f"Creating database: {db_name}")
                    conn.execute(text("COMMIT"))  # End transaction
                    conn.execute(text(f"CREATE DATABASE {db_name}"))
                    logger.info("Database created successfully")
                else:
                    logger.info("Database already exists")
            
            temp_engine.dispose()
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating database: {e}")
            raise
    
    def run_migrations(self):
        """Run database migrations"""
        try:
            logger.info("Creating database tables...")
            create_tables()
            logger.info("Database tables created successfully")
            
            # Run custom migrations
            self._run_custom_migrations()
            
        except SQLAlchemyError as e:
            logger.error(f"Error running migrations: {e}")
            raise
    
    def _run_custom_migrations(self):
        """Run custom migration scripts"""
        migrations = [
            self._create_indexes,
            self._add_performance_optimizations
        ]
        
        for migration in migrations:
            try:
                migration()
            except Exception as e:
                logger.warning(f"Migration {migration.__name__} failed: {e}")
    
    def _create_indexes(self):
        """Create database indexes for performance"""
        with self.engine.connect() as conn:
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_document_url ON document_processing_logs(document_url);",
                "CREATE INDEX IF NOT EXISTS idx_query_created_at ON query_logs(created_at);",
                "CREATE INDEX IF NOT EXISTS idx_system_metrics_created_at ON system_metrics(created_at);"
            ]
            
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Index creation failed: {e}")
    
    def _add_performance_optimizations(self):
        """Add performance optimizations"""
        with self.engine.connect() as conn:
            optimizations = [
                "ANALYZE;",  # Update table statistics
            ]
            
            for opt_sql in optimizations:
                try:
                    conn.execute(text(opt_sql))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Optimization failed: {e}")

async def main():
    """Run database migrations"""
    migrator = DatabaseMigrator()
    
    try:
        # Create database if needed
        migrator.create_database_if_not_exists()
        
        # Run migrations
        migrator.run_migrations()
        
        logger.info("✅ Database migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database migration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())