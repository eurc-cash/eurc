# backend/main.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from backend.parser import SmartParser
from config import Config

app = FastAPI(title="EURC Market API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = SmartParser()

@app.get("/")
async def root():
    return {
        "message": "EURC Market API",
        "wallet": Config.WALLET_ADDRESS,
        "status": "online"
    }

@app.get("/api/search")
async def search_products(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, le=50),
    platform: str = Query("all")
):
    products = await parser.parse_and_convert(q)
    
    if platform != "all":
        products = [p for p in products if p.get('platform') == platform]
    
    # Добавляем наценку 35%
    for p in products:
        p['price_eurc'] = round(p['price_eurc'] * 1.35, 2)
        p['price_rub'] = round(p['price_rub'] * 1.35, 0)
    
    return {
        "status": "success",
        "count": len(products[:limit]),
        "products": products[:limit],
        "currency": "EURC",
        "payment_wallet": Config.WALLET_ADDRESS
    }
