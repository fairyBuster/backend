from os import name

from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from datetime import datetime
from typing import List,Optional
from app.models.product import ProductStatus,ProfitType,ProfitMethod,ClaimReset,BalanceSource


def rabat_field(description: str):
    return Field(default= Decimal(0.00), ge=0, le=100,description= description) #tujuan: validasi rabat ge a dan le 100 adalah untuk validasi rabat antara 0 dan 100 persen

class ProductBase(BaseModel):
    name : str
    type : str
    description : Optional[str] = None
    price : Decimal = Field(ge=0, description="Harga produk")
    image : Optional[str] = None
    status : ProductStatus = ProductStatus.active
    stock : int = Field(ge=0,default=0, description="Stok produk")
    purchase_limit: int = Field(ge=0,default=0, description="Batas pembelian per pengguna")
    duration: int = Field(ge=0,default=0, description="Durasi keuntungan")
    claim_reset: ClaimReset = ClaimReset.midnight
    profit_type: ProfitType
    profit_method: ProfitMethod
    profit_rate: Decimal = Field(ge=0.00, description="Persen keuntungan")

    balance_source: BalanceSource = BalanceSource.balance_deposit

    purchase_rabat_l1: Decimal = rabat_field("Persen rabat level 1")
    purchase_rabat_l2: Decimal = rabat_field("Persen rabat level 2")
    purchase_rabat_l3: Decimal = rabat_field("Persen rabat level 3")
    purchase_rabat_l4: Decimal = rabat_field("Persen rabat level 4")
    purchase_rabat_l5: Decimal = rabat_field("Persen rabat level 5")
    profit_rabat_l1: Decimal = rabat_field("Persen keuntungan level 1")
    profit_rabat_l2: Decimal = rabat_field("Persen keuntungan level 2")
    profit_rabat_l3: Decimal = rabat_field("Persen keuntungan level 3")
    profit_rabat_l4: Decimal = rabat_field("Persen keuntungan level 4")
    profit_rabat_l5: Decimal = rabat_field("Persen keuntungan level 5")

    specific: dict = {}

    @field_validator("profit_rate")
    @classmethod

    def validate_profit_rate(cls , v, info):
        if "profit_type" in (info.data or {}):
            if info.data["profit_type"] == ProfitType.percentage and v > 100:
                raise ValueError("Profit rate tidak boleh > 100%")
            return v

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name : Optional[str] = None
    type : Optional[str] = None
    description : Optional[str] = None
    price : Optional[Decimal] = None
    image : Optional[str] = None
    status : Optional[ProductStatus] = None
    stock : Optional[int] = None
    purchase_limit: Optional[int] = None
    profit_type: Optional[ProfitType] = None
    profit_method: Optional[ProfitMethod] = None
    profit_rate: Optional[Decimal] = None
    balance_source: Optional[BalanceSource] = None
    specific: Optional[dict] = None
    duration: Optional[int] = None
    claim_reset: Optional[ClaimReset] = None

    purchase_rabat_l1: Optional[Decimal] = None
    purchase_rabat_l2: Optional[Decimal] = None
    purchase_rabat_l3: Optional[Decimal] = None
    purchase_rabat_l4: Optional[Decimal] = None
    purchase_rabat_l5: Optional[Decimal] = None
    profit_rabat_l1: Optional[Decimal] = None
    profit_rabat_l2: Optional[Decimal] = None
    profit_rabat_l3: Optional[Decimal] = None
    profit_rabat_l4: Optional[Decimal] = None
    profit_rabat_l5: Optional[Decimal] = None

class RabatBreakdown(BaseModel):
    """
    Rabat breakdown
    """
    level: int
    referral_id: Optional[int] = None
    purchase_rabat_pct: Decimal
    profit_rabat_pct: Decimal
    komisi_dari_harge: Decimal
    total_komisi: Decimal


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):

    items: List[ProductResponse] = []
    total: int 
    page: int
    size: int
    pages: int



