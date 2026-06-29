import contextlib
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from loguru import logger
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

# Define the base for declarative models
Base = declarative_base()
DB_NOT_INITIALIZED = "DatabaseSessionManager is not initialized"


class DBSettings(BaseSettings):
    db_name: str = ""
    db_user: str = ""
    db_password: str = ""
    db_host: str = "localhost"
    db_port: int = 5433

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


_DBSettings = DBSettings()


def get_engine(
    host: str,
    echo: bool = False,
    pool_size: int = 5,
    max_overflow: int = 10,
    pool_timeout: int = 30,
) -> AsyncEngine:
    return create_async_engine(
        host,
        echo=echo,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
    )


engine = get_engine(
    _DBSettings.db_url,
    echo=True,
    pool_size=10,  # Up to 10 persistent connections
    max_overflow=20,  # Up to 20 temporary additional connections
    pool_timeout=30,  # Idle timeout for connections
)


class DatabaseSessionManager:
    def __init__(self) -> None:
        # Create the SQLAlchemy engine
        self.engine: AsyncEngine | None = engine
        # Create a SessionLocal class
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = async_sessionmaker(
            autocommit=False, class_=AsyncSession, autoflush=False, bind=self.engine
        )

    async def close(self) -> None:
        if self.engine is None:

            raise RuntimeError(DB_NOT_INITIALIZED)

        await self.engine.dispose()

        self.engine = None
        self._sessionmaker = None
        logger.info("Database Connections closed")

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self.engine is None:

            raise RuntimeError(DB_NOT_INITIALIZED)  # ← specific exception + constant

        async with self.engine.begin() as connection:
            try:
                logger.info("Database[R] Connection established")
                yield connection
            except Exception:
                await connection.rollback()
                raise
            finally:
                await connection.close()
                logger.info("Database[R] Connections closed")

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:

            raise RuntimeError(DB_NOT_INITIALIZED)  # ← specific exception + constant

        session = self._sessionmaker()
        try:
            logger.info("Database Connection established!")
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            logger.info("Database Connections closed")


DBSessionManager = DatabaseSessionManager()


async def get_db() -> AsyncIterator[AsyncSession]:
    async with DBSessionManager.session() as session:
        yield session


async def get_db_connect() -> AsyncIterator[AsyncConnection]:
    async with DBSessionManager.connect() as connect:
        yield connect


SQLALCHEMY_DATABASE_URL = _DBSettings.db_url

DBSessionDep = Annotated[AsyncSession, Depends(get_db)]
