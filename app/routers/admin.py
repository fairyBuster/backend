from itertools import product
from operator import ge

from app.models.product import Product
from app.routers.auth import router
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, query
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.schemas.product import ProductCreate, ProductListResponse, ProductResponse, ProductUpdate
from app.schemas.user import UserResponse,UserUpdate,UserRegister
from app.utils.auth import get_admin_user, hash_password
from app.utils.referral import get_product_or_404, to_response
import shutil
import uuid
import os
from fastapi import UploadFile, File
import math

router = APIRouter(prefix="/admin",tags=["admin"])

@router.get("/users", response_model = List[UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin : User = Depends(get_admin_user)
):
    return db.query(User).offset(skip).limit(limit).all()


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id:int,
    db: Session = Depends(get_db),
    admin : User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
   user_id: int,
   user_update: UserUpdate,
   db: Session = Depends(get_db),
   admin : User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    update_data = user_update.model_dump(exclude_unset=True) # mengabaikan field yang tidak diupdate
    print(update_data)
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
  
    return user

@router.delete("/users/{user_id}")
def delete_user(
    user_id:int,
    db: Session = Depends(get_db),
    admin : User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.role == "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin user cannot be deleted")

    db.delete(user)
    db.commit()
    return {"message":f"User {user.phone} deleted successfully"}


@router.patch("/users/{user_id}/toggle-active")
def toggle_active(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Suspend atau aktifkan kembali akun user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User ID {user_id} not found")

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return {"message":f"User {user.phone} active status toggled successfully"}


@router.get("/products", response_model = ProductListResponse, summary="Get all products")
def admin_list_products(
    page: int = Query (1, ge=1),
    size: int = Query (10, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter products by status"),
    type: Optional[str] = Query(None, description="Filter products by type"),
    search: Optional[str] = Query(None, description="Search products by name or description"),
    db: Session = Depends(get_db),
    admin : User = Depends(get_admin_user)
):

    """
    Get all products.
    """
    query = db.query(Product)
    if status:
        valid_status = [s.value for s in ProductStatus]
        if status not in valid_status:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid product status")
        query = query.filter(Product.status == status)

    if type:
        query = query.filter(Product.type == type)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    total = query.count()
    products = query.order_by(Product.created_at.desc()).offset((page - 1) * size).limit(size).all()

    return {
        "items" : [to_response(p) for p in products],
        "total" : total,
        "page" : page,
        "size" : size,
        "pages" : math.ceil(total / size) if total else 1,
    }


@router.get("/products/{product_id}", response_model=ProductResponse, summary="Get product by ID")
def admin_get_product_by_id(
    product_id: int,
    db: Session = Depends(get_db),
    admin : User = Depends(get_admin_user)
):

    """
    Get product by ID.
    """
    product = get_product_or_404(product_id, db)
    return to_response(product)

@router.post("/upload-image", summary="Upload image")
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin : User = Depends(get_admin_user)
):
    """
    Upload image.
    """
    os.makedirs("images/products", exist_ok=True)
    ext = file.filename.split(".")[-1] # mengambil ekstensi file caranya pisahkan dengan . lalu ambil yang terakhir
    filename = f"{uuid.uuid4().hex}.{ext}" # membuat nama file yang unik dari uuid4().hex dan ext
    
    if ext not in ["jpg", "jpeg", "png"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image format. Only JPG, JPEG, and PNG are allowed.")
    file_path = f"images/products/{filename}" 
    with open(file_path, "wb") as bufer: # with ada;a
        shutil.copyfileobj(file.file, bufer) 
    
    return{
        "path" : file_path
    }

@router.post("/products", response_model=ProductResponse,status_code=status.HTTP_201_CREATED,summary="Create a new product")
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    admin : User = Depends(get_admin_user)
):
    """
    Create a new product.
    Contoh config rabat multi-level
    {
        "purchase_rabat_l1": 5.00,
        "purchase_rabat_l2": 10.00,
        "purchase_rabat_l3": 15.00,
        "purchase_rabat_l4": 20.00,
        "purchase_rabat_l5": 25.00,
        "profit_rabat_l1": 10.00,
        "profit_rabat_l2": 20.00,
        "profit_rabat_l3": 30.00,
        "profit_rabat_l4": 40.00,
        "profit_rabat_l5": 50.00,
    }
    """

    product = Product(**data.model_dump()) # ini adalah keyword arguments ** itu artinya semua field dari data akan diisi ke product
    print(data)
    db.add(product)
    db.commit()
    db.refresh(product)
    return to_response(product)

@router.patch("/products/{product_id}", response_model=ProductResponse, summary="Update product by ID")
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    admin : User = Depends(get_admin_user)
):
    """
    Update product by ID.
    """
    product = get_product_or_404(product_id, db)
    update_data = data.model_dump(exclude_unset=True) #exclude_unset=True untuk mengabaikan field yang tidak diupdate
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one field must be updated")
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return to_response(product)


@router.delete("/products/{product_id}", summary="Delete product by ID")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin : User = Depends(get_admin_user)
):
    """
    Delete product by ID.
    """
    product = get_product_or_404(product_id, db)
    db.delete(product)
    db.commit()
    return {"message":f"Product {product.name} deleted successfully"}