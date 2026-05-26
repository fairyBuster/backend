from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router
from app.routers.product import router as product_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(product_router)

@app.get("/")
def read_root():
    return {"Message": f"Hello {settings.app_name} {settings.app_version}!"}

@app.get("/health" , tags=["Health"])
def read_health():
    return {"Message": "Healthy"}