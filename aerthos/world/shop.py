"""
Shop system for buying and selling items
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ShopItem:
    """An item available in a shop"""
    id: str
    price: int
    stock: int


@dataclass
class ShopService:
    """A service offered by a shop"""
    name: str
    price: int
    description: str


class Shop:
    """Represents a shop where players can buy/sell items"""

    def __init__(self, shop_id: str, data: Dict):
        self.shop_id = shop_id
        self.name = data['name']
        self.shop_type = data['type']
        self.description = data['description']
        self.items = [ShopItem(**item) for item in data.get('items', [])]
        self.services = [ShopService(**svc) for svc in data.get('services', [])]

    def get_item_price(self, item_id: str) -> Optional[int]:
        """Get the price of an item"""
        for item in self.items:
            if item.id == item_id:
                return item.price
        return None

    def has_item(self, item_id: str) -> bool:
        """Check if shop has an item in stock"""
        for item in self.items:
            if item.id == item_id and item.stock > 0:
                return True
        return False

    def buy_item(self, item_id: str) -> bool:
        """Buy an item from the shop (reduces stock)"""
        for item in self.items:
            if item.id == item_id and item.stock > 0:
                item.stock -= 1
                return True
        return False

    def sell_item(self, item_id: str, value: int) -> int:
        """
        Sell an item to the shop
        Returns the gold received (typically 50% of item value)
        """
        return value // 2

    def get_service_price(self, service_name: str) -> Optional[int]:
        """Get the price of a service"""
        for service in self.services:
            if service.name == service_name:
                return service.price
        return None

    def list_items(self) -> List[Dict]:
        """List all items available for purchase"""
        return [
            {
                'id': item.id,
                'price': item.price,
                'stock': item.stock,
                'in_stock': item.stock > 0
            }
            for item in self.items
        ]

    def list_services(self) -> List[Dict]:
        """List all services available"""
        return [
            {
                'name': svc.name,
                'price': svc.price,
                'description': svc.description
            }
            for svc in self.services
        ]


class ShopManager:
    """Manages all shops in the game"""

    def __init__(self, shops_data_path: str = "aerthos/data/shops.json"):
        with open(shops_data_path, 'r') as f:
            data = json.load(f)

        self.shops = {
            shop_id: Shop(shop_id, shop_data)
            for shop_id, shop_data in data.items()
        }

    def get_shop(self, shop_id: str) -> Optional[Shop]:
        """Get a shop by ID"""
        return self.shops.get(shop_id)

    def list_all_shops(self) -> List[Dict]:
        """List all available shops"""
        return [
            {
                'id': shop_id,
                'name': shop.name,
                'type': shop.shop_type,
                'description': shop.description
            }
            for shop_id, shop in self.shops.items()
        ]
