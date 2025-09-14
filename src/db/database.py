from sqlalchemy import Column, String, DateTime, func, Float, select, BigInteger, create_engine
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
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


# Build a safe URL for sync (using psycopg2 driver)
url = URL.create(
    "postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
)


class DatabaseConnection:
    def __init__(self):
        self.engine = create_engine(url, connect_args={"sslmode": "require"})

    def test_connection(self):
        with self.engine.begin() as conn:
            result = conn.execute(select(func.version()))
            return result.scalar()

    def create_tables(self):
        Base.metadata.create_all(self.engine)
        print("Tables created")

    def upsert_wallet(self, discord_id: int, wallet_address: str):
        """Upsert wallet - insert or update if exists"""
        with self.engine.begin() as conn:
            stmt = pg_insert(Wallet).values(discord_id=discord_id, wallet_address=wallet_address, updated_at=func.now())
            stmt = stmt.on_conflict_do_update(
                index_elements=["discord_id"], set_={"wallet_address": stmt.excluded.wallet_address, "updated_at": func.now()}
            )
            conn.execute(stmt)

    def get_wallet(self, discord_id: int) -> Wallet | None:
        with self.engine.begin() as conn:
            stmt = select(Wallet).where(Wallet.discord_id == discord_id)
            result = conn.execute(stmt)
            return result.mappings().one_or_none()

    def get_all_wallets(self) -> list[Wallet]:
        with self.engine.begin() as conn:
            stmt = select(Wallet)
            result = conn.execute(stmt)
            return result.mappings().all()

    def upsert_price_watch(self, discord_id: int, threshold: float):
        """Upsert price watch - insert or update if exists"""
        with self.engine.begin() as conn:
            stmt = pg_insert(PriceWatch).values(discord_id=discord_id, threshold=threshold, updated_at=func.now())
            stmt = stmt.on_conflict_do_update(index_elements=["discord_id"], set_={"threshold": stmt.excluded.threshold, "updated_at": func.now()})
            conn.execute(stmt)

    def get_price_watch(self, discord_id: int) -> PriceWatch | None:
        with self.engine.begin() as conn:
            stmt = select(PriceWatch).where(PriceWatch.discord_id == discord_id)
            result = conn.execute(stmt)
            return result.mappings().one_or_none()

    def get_all_price_watches(self) -> list[PriceWatch]:
        with self.engine.begin() as conn:
            stmt = select(PriceWatch)
            result = conn.execute(stmt)
            return result.mappings().all()

    def close(self):
        """Close the database connection"""
        self.engine.dispose()
