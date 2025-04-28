from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from app.core.config import settings
from sqlalchemy import text
from app.core.logger import logger

# Add detailed logging for database URL
logger.info(f"Attempting to create database engine with URL: {settings.DATABASE_URL}")
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Database:
    async def init_db(self):
        from app.db.models import Base  # Import here to avoid circular import
        from app.db.optimizations import DatabaseOptimizations
        
        logger.info("Starting database initialization...")
        try:
            async with engine.begin() as conn:
                logger.info("Successfully connected to database")
                # Create vector extension first
                logger.info("Creating vector extension...")
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                logger.info("Vector extension created successfully")
                # Then create tables
                logger.info("Creating database tables...")
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error during database initialization: {str(e)}")
            logger.error(f"Database URL being used: {settings.DATABASE_URL}")
            raise
        
        # Create indexes in a separate transaction after tables are created
        async with async_session() as session:
            try:
                logger.info("Creating database indexes...")
                db_optimizations = DatabaseOptimizations()
                await db_optimizations.create_optimized_indexes(session)
                await db_optimizations.optimize_vector_search(session)
                await session.commit()
                logger.info("Database indexes created successfully")
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to create indexes: {str(e)}")
                raise Exception(f"Failed to create indexes: {str(e)}")

    async def check_connection(self):
        """Check if the database connection is working."""
        try:
            logger.info(f"Checking database connection with URL: {settings.DATABASE_URL}")
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database connection check successful")
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {str(e)}")
            logger.error(f"Database URL being used: {settings.DATABASE_URL}")
            raise Exception(f"Database connection failed: {str(e)}")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with async_session() as session:
            yield session

db = Database() 