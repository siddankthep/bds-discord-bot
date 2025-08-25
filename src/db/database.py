from sqlalchemy import Column, String, DateTime, func, Float, select, BigInteger
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()


class Base(DeclarativeBase):
    pass


class Wallet(Base):
    __tablename__ = "wallet"
    discord_id = Column(BigInteger, primary_key=True)
    wallet_address = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class PriceWatch(Base):
    __tablename__ = "price_watch"
    discord_id = Column(BigInteger, primary_key=True)
    threshold = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


# Build a safe URL for async (using asyncpg driver)
url = URL.create(
    "postgresql+asyncpg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
)


class DatabaseConnection:
    def __init__(self):
        self.engine = create_async_engine(
            url,
            echo=False,
            pool_pre_ping=True,
        )
        self.async_session = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def get_session(self) -> AsyncSession:
        async with self.async_session() as session:
            return session

    def get_engine(self):
        return self.engine

    async def test_connection(self):
        async with self.engine.begin() as conn:
            result = await conn.execute(select(func.version()))
            return result.scalar()

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("Tables created")

    async def insert_ignore_wallet(self, discord_id: int, wallet_address: str):
        """Insert wallet with ignore - if conflict exists, do nothing"""
        async with self.engine.begin() as conn:
            stmt = pg_insert(Wallet).values(discord_id=discord_id, wallet_address=wallet_address)
            stmt = stmt.on_conflict_do_nothing()
            await conn.execute(stmt)

    async def get_wallet(self, discord_id: int) -> Wallet | None:
        async with self.engine.begin() as conn:
            stmt = select(Wallet).where(Wallet.discord_id == discord_id)
            result = await conn.execute(stmt)
            return result.mappings().one_or_none()

    async def get_all_wallets(self) -> list[Wallet]:
        async with self.engine.begin() as conn:
            stmt = select(Wallet)
            result = await conn.execute(stmt)
            return result.mappings().all()

    async def upsert_price_watch(self, discord_id: int, threshold: float):
        """Upsert price watch - insert or update if exists"""
        async with self.engine.begin() as conn:
            stmt = pg_insert(PriceWatch).values(discord_id=discord_id, threshold=threshold, updated_at=func.now())
            stmt = stmt.on_conflict_do_update(index_elements=["discord_id"], set_={"threshold": stmt.excluded.threshold, "updated_at": func.now()})
            await conn.execute(stmt)

    async def get_price_watch(self, discord_id: int) -> PriceWatch | None:
        async with self.engine.begin() as conn:
            stmt = select(PriceWatch).where(PriceWatch.discord_id == discord_id)
            result = await conn.execute(stmt)
            return result.mappings().one_or_none()

    async def get_all_price_watches(self) -> list[PriceWatch]:
        async with self.engine.begin() as conn:
            stmt = select(PriceWatch)
            result = await conn.execute(stmt)
            return result.mappings().all()

    async def close(self):
        """Close the database connection"""
        await self.engine.dispose()
