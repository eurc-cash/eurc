# backend/parser.py
import aiohttp
import asyncio
from typing import List, Dict, Any
import re

class SmartParser:
    """Реальный парсер товаров с маркетплейсов"""
    
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=10)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    async def parse_and_convert(self, query: str) -> List[Dict[str, Any]]:
        """Парсит товары со всех платформ и конвертирует цены в EURC"""
        results = []
        
        # Парсим с AliExpress
        results += await self._parse_aliexpress(query)
        
        # Парсим с Ozon
        results += await self._parse_ozon(query)
        
        # Парсим с Wildberries
        results += await self._parse_wildberries(query)
        
        return results

    async def _parse_aliexpress(self, query: str) -> List[Dict]:
        """Парсинг AliExpress через публичное API"""
        try:
            url = f"https://api.alisearch.ae/pub/v1/search/ae?q={query}&limit=20"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=self.timeout) as resp:
                    data = await resp.json()
                    items = data.get('items', [])
                    
                    parsed = []
                    for item in items[:20]:
                        price_usd = float(item.get('price', {}).get('min', 0))
                        parsed.append({
                            'name': item.get('title', ''),
                            'price_eurc': round(price_usd * 0.87, 2),  # USD → EURC
                            'price_rub': round(price_usd * 90, 0),
                            'platform': 'aliexpress',
                            'image': item.get('image', {}).get('url', ''),
                            'url': item.get('url', '')
                        })
                    return parsed
        except Exception as e:
            print(f"❌ AliExpress error: {e}")
            return []

    async def _parse_ozon(self, query: str) -> List[Dict]:
        """Парсинг Ozon через публичное API"""
        try:
            # Используем публичный API Ozon
            url = f"https://api.ozon.ru/composer-api/1.0/search?q={query}&limit=20"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=self.timeout) as resp:
                    data = await resp.json()
                    items = data.get('items', [])
                    
                    parsed = []
                    for item in items[:20]:
                        price_rub = float(item.get('price', {}).get('value', 0))
                        parsed.append({
                            'name': item.get('title', ''),
                            'price_eurc': round(price_rub / 90 / 1.15, 2),
                            'price_rub': round(price_rub, 0),
                            'platform': 'ozon',
                            'image': item.get('image', {}).get('url', ''),
                            'url': item.get('url', '')
                        })
                    return parsed
        except Exception as e:
            print(f"❌ Ozon error: {e}")
            return []

    async def _parse_wildberries(self, query: str) -> List[Dict]:
        """Парсинг Wildberries через публичное API"""
        try:
            url = f"https://search.wb.ru/exactmatch/ru/common/v4/search?query={query}&limit=20"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=self.timeout) as resp:
                    data = await resp.json()
                    items = data.get('data', {}).get('products', [])
                    
                    parsed = []
                    for item in items[:20]:
                        price_rub = float(item.get('priceU', 0)) / 100
                        parsed.append({
                            'name': item.get('name', ''),
                            'price_eurc': round(price_rub / 90 / 1.15, 2),
                            'price_rub': round(price_rub, 0),
                            'platform': 'wildberries',
                            'image': f"https://basket-{item.get('basket', '01')}.wbbasket.ru/images/{item.get('id', '')}.jpg",
                            'url': f"https://www.wildberries.ru/catalog/{item.get('id', '')}"
                        })
                    return parsed
        except Exception as e:
            print(f"❌ Wildberries error: {e}")
            return []
