import os

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router
from app.routers.product import router as product_router
from fastapi.staticfiles import StaticFiles

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
os.makedirs("images/products", exist_ok=True)
app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/static", StaticFiles(directory="images"), name="static")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

@app.get("/")
def read_root():
    return {"Message": f"Hello {settings.app_name} {settings.app_version}!"}

@app.get("/health" , tags=["Health"])
def read_health():
    return {"Message": "Healthy"}
