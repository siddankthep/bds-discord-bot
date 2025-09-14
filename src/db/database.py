from typing import Optional
from sqlalchemy import URL, BigInteger, Column, Float, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv
import os

load_dotenv()


class Base(DeclarativeBase):
    pass


class Wallet(Base):
    __tablename__ = "wallet"
    discord_id = Column(BigInteger, primary_key=True)
    wallet_address = Column(String(100), nullable=False)


class PriceWatch(Base):
    __tablename__ = "price_watch"
    discord_id = Column(BigInteger, primary_key=True)
    threshold = Column(Float, nullable=False)


url = URL.create(
    "postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
)


class DatabaseConnection:
    def __init__(self) -> None:
        self.engine = create_engine(url=url, connect_args={"sslmode": "require"})
        self.create_tables()

    def create_tables(self):
        Base.metadata.create_all(self.engine)
        print("All tables created!")

    def upsert_wallet(self, discord_id: int, wallet_address: str):
        with self.engine.begin() as conn:
            stmt = insert(Wallet).values(discord_id=discord_id, wallet_address=wallet_address)
            stmt = stmt.on_conflict_do_update(index_elements=["discord_id"], set_={"wallet_address": stmt.excluded.wallet_address})
            conn.execute(stmt)

    def get_wallet(self, discord_id: int) -> Optional[Wallet]:
        with self.engine.begin() as conn:
            stmt = select(Wallet).where(Wallet.discord_id == discord_id)
            result = conn.execute(stmt)
            return result.mappings().one_or_none()

    def upsert_price_watch(self, discord_id: int, threshold: float):
        with self.engine.begin() as conn:
            stmt = insert(PriceWatch).values(discord_id=discord_id, threshold=threshold)
            stmt = stmt.on_conflict_do_update(index_elements=["discord_id"], set_={"threshold": stmt.excluded.threshold})
            conn.execute(stmt)

    def get_price_watch(self, discord_id: int) -> Optional[PriceWatch]:
        with self.engine.begin() as conn:
            stmt = select(PriceWatch).where(PriceWatch.discord_id == discord_id)
            result = conn.execute(stmt)
            return result.mappings().one_or_none()
