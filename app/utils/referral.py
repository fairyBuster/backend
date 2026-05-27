from decimal import Decimal

from typing import List,Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.product import Product, ProfitType
from app.schemas.product import RabatBreakdown, ProductResponse


def get_referrer_chain (user: User, db:Session, max_level: int = 5) -> List[Optional[User]]:
    """
    Get referral chain
    Menulusui list referral_l1 - referral_l5
    None jika tidak ada referral
    """

    chain = []
    current = user

    for i in range(max_level):
        if current.referral_by == 0:
            chain.append(None)
        else:
            referrer = db.query(User).filter(User.id == current.referral_by).first()
            chain.append(referrer)
            current = referrer if referrer else current

        if current is None or current.referral_by == 0:
            while len(chain) < max_level:
                chain.append(None)
            break
    return chain[:max_level]


# Hitung profit produk
def hitung_base_profit (product: Product) -> Decimal:
    price = Decimal(str(product.price))
    profit_rate = Decimal(str(product.profit_rate))

    if product.profit_type == ProfitType.percentage:
        return round(price * profit_rate / 100, 2) # contoh price = 10000, profit_rate = 10%, maka profit = 1000.00
    else:
        return round(profit_rate, 2) # contoh profit_rate = 1000, maka profit = 1000.00

    
def calculate_rabat_breakdown(product: Product, referrer_chain: List[Optional[User]]) -> List[RabatBreakdown]:
    """
    Calculate rabat breakdown
    """
    price = Decimal(str(product.price))
    base_profit = hitung_base_profit(product)

    #config rabat per level dari product
    purchase_ptcs=[
        Decimal(str(product.purchase_rabat_l1)),
        Decimal(str(product.purchase_rabat_l2)),
        Decimal(str(product.purchase_rabat_l3)),
        Decimal(str(product.purchase_rabat_l4)),
        Decimal(str(product.purchase_rabat_l5)),
    ]
    profit_ptcs=[
        Decimal(str(product.profit_rabat_l1)),
        Decimal(str(product.profit_rabat_l2)),
        Decimal(str(product.profit_rabat_l3)),
        Decimal(str(product.profit_rabat_l4)),
        Decimal(str(product.profit_rabat_l5)),
    ]

    breakdown = [] 
    for i in range(5):
        referrer = referrer_chain[i] if i < len(referrer_chain) else None
        pur_pct = purchase_ptcs[i]
        pro_pct = profit_ptcs[i]

        komisi_harge = round(price * pur_pct / 100, 2)
        komisi_profit = round(base_profit * pro_pct / 100, 2)
        total = komisi_harge + komisi_profit

        breakdown.append(RabatBreakdown(
            level = i+1,
            referrer_id = referrer.id if referrer else None,
            purchase_rabat_pct = pur_pct,
            profit_rabat_pct = pro_pct,
            komisi_harge = komisi_harge,
            komisi_profit = komisi_profit,
            total = total
        ))
    return breakdown


def distribute_referral_commission(
    product : Product,
    referrer_chain: List[Optional[User]],
    breakdown: List[RabatBreakdown],
    db: Session,

    
) -> List[dict]:
    """
    Distribute referral commission
    """
    from app.models.product import BalanceSource

    logs=[]

    for item in breakdown:
        if item.referral_id is None or item.total_komisi <= 0:
            continue
        referrer = referrer_chain[item.level-1]
        if referrer is None:
            continue

        referrer.balance += int(item.total_komisi)

        logs.append({
            "referrer_id": referrer.id,
            "referrer_phone" : referrer.phone,
            "level" : item.level,
            "komisi": int(item.total_komisi),

        })

    db.flush()
    return logs

def to_response(product: Product) -> ProductResponse:
    """
    Convert a Product model to a ProductResponse schema
    """
    data = ProductResponse.model_validate(product)

    return data

def get_product_or_404(product_id: int, db: Session) -> Product:
    """
    Get product or raise 404
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product