from itertools import product
from optparse import Option
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, query
from decimal import Decimal
import math
from app.database import get_db
from app.models.product import Product, ProfitType, ProductStatus
from app.schemas.product import ProductCreate, ProductListResponse, ProductUpdate, ProductResponse, RabatBreakdown, BalanceSource
from app.utils.auth import get_current_active_user
from app.utils.referral import hitung_base_profit, calculate_rabat_breakdown, to_response



router = APIRouter(tags=["Product"])

@router.get("/product", response_model=ProductListResponse, summary="Get product list")
def list_product(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),

    type: Optional[str] = Query(None, description="category"),
    search: Optional[str] = Query(None, description="Search"),
    db: Session = Depends(get_db)
):
    """
    Get product list
    """

    query = db.query(Product).filter(Product.status == ProductStatus.active)
    if type:
        query = query.filter(Product.type == type)
    

    if search:
        query = query.filter(Product.name.like(f"%{search}%"))

    total = query.count()
    products = query.order_by(Product.created_at.desc()).offset((page - 1) * size).limit(size).all()
    return {
        "items" : [to_response(p) for p in products],
        "total" : total,
        "page" : page,
        "size" : size,
        "pages" : math.ceil(total / size) if total else 1,
    }


@router.get("/products/{product_id}", response_model=ProductResponse, summary="Get product detail")
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.status == ProductStatus.active,
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return to_response(product)
  






