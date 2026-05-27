import enum

from sqlalchemy import Column,Integer,String,Text,Boolean,Numeric,DateTime,JSON ,Enum as saEnum
from sqlalchemy.sql import func
from app.database import Base


class ProductStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
class ProfitType(str, enum.Enum):
    fixed = "fixed"
    percentage = "percentage"
class ProfitMethod(str, enum.Enum):
    manual = "manual"
    auto = "auto"
class ClaimReset(str, enum.Enum):
    midnight = "midnight"
    purchase = "purchase"
class BalanceSource(str, enum.Enum):
    balance = "balance"
    balance_deposit = "balance_deposit"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=False, nullable=False)
    type = Column(String(255), index=False, nullable=False)
    description = Column(Text, index=False, nullable=False)
    price = Column(Numeric(15,2), index=False, nullable=False)
    image = Column(String(255), default="", nullable=False)
    status = Column(saEnum(ProductStatus), default=ProductStatus.active, index=False, nullable=False)
    stock = Column(Integer, default=0, index=False, nullable=False)
    purchase_limit = Column(Integer, nullable=True)
    profit_type = Column(saEnum(ProfitType), default=ProfitType.fixed, index=False, nullable=False)
    profit_rate = Column(Numeric(5,2), nullable=True)
    profit_method = Column(saEnum(ProfitMethod), default=ProfitMethod.auto, index=False, nullable=False)
    duration = Column(Integer, nullable=True)
    claim_reset = Column(saEnum(ClaimReset), default=ClaimReset.midnight, index=False, nullable=False)
    balance_source = Column(saEnum(BalanceSource), default=BalanceSource.balance_deposit, index=False, nullable=False)
    purchase_rabat_l1 = Column(Numeric(5,2), nullable=True)
    purchase_rabat_l2 = Column(Numeric(5,2), nullable=True)
    purchase_rabat_l3 = Column(Numeric(5,2), nullable=True)
    purchase_rabat_l4 = Column(Numeric(5,2), nullable=True)
    purchase_rabat_l5 = Column(Numeric(5,2), nullable=True)
    profit_rabat_l1 = Column(Numeric(5,2), nullable=True)
    profit_rabat_l2 = Column(Numeric(5,2), nullable=True)
    profit_rabat_l3 = Column(Numeric(5,2), nullable=True)
    profit_rabat_l4 = Column(Numeric(5,2), nullable=True)
    profit_rabat_l5 = Column(Numeric(5,2), nullable=True)
    specific = Column(JSON, default=dict, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    