"""
Village system - Towns with shops, inns, and services
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class ShopItem:
    """Item available for purchase in a shop"""
    item_id: str
    item_name: str
    price: int  # in GP
    stock: int = -1  # -1 means unlimited


@dataclass
class Shop:
    """
    Shop that buys and sells items

    Shops have inventory and will buy items from players
    at a discount (50% of retail price)
    """

    name: str
    description: str
    inventory: List[ShopItem] = field(default_factory=list)
    buy_price_multiplier: float = 0.5  # Shops buy at 50% of retail
    sell_price_multiplier: float = 1.0  # Shops sell at full price

    def get_sell_price(self, item_id: str, item_name: str, base_cost: int) -> int:
        """Get price to sell this item to player"""
        return int(base_cost * self.sell_price_multiplier)

    def get_buy_price(self, item_id: str, item_name: str, base_cost: int) -> int:
        """Get price to buy this item from player"""
        return int(base_cost * self.buy_price_multiplier)

    def has_item(self, item_id: str) -> bool:
        """Check if shop has this item in stock"""
        for shop_item in self.inventory:
            if shop_item.item_id == item_id:
                return shop_item.stock != 0
        return False

    def purchase_item(self, item_id: str) -> Optional[ShopItem]:
        """
        Purchase item from shop (reduces stock)

        Returns:
            ShopItem if successful, None if out of stock
        """
        for shop_item in self.inventory:
            if shop_item.item_id == item_id:
                if shop_item.stock == -1:  # Unlimited
                    return shop_item
                elif shop_item.stock > 0:
                    shop_item.stock -= 1
                    return shop_item
                else:
                    return None
        return None


@dataclass
class Inn:
    """
    Inn offering rest and healing services

    Players can rest overnight to restore HP and spells
    """

    name: str
    description: str
    room_cost: int = 10  # Cost to rest for the night
    healing_per_rest: str = "1d4+1"  # HP restored
    meal_cost: int = 1  # Cost of a meal

    def can_afford_room(self, player_gold: int) -> bool:
        """Check if player can afford to rest"""
        return player_gold >= self.room_cost

    def can_afford_meal(self, player_gold: int) -> bool:
        """Check if player can afford a meal"""
        return player_gold >= self.meal_cost


@dataclass
class Village:
    """
    A village location with shops and services

    Villages provide a safe place to rest, buy/sell items,
    and access healing services.
    """

    name: str
    description: str
    shops: Dict[str, Shop] = field(default_factory=dict)
    inn: Optional[Inn] = None
    tavern_rumors: List[str] = field(default_factory=list)

    def get_shop(self, shop_name: str) -> Optional[Shop]:
        """Get a shop by name (case-insensitive partial match)"""
        search = shop_name.lower()

        # Try exact match
        for name, shop in self.shops.items():
            if name.lower() == search:
                return shop

        # Try partial match
        for name, shop in self.shops.items():
            if search in name.lower() or search in shop.name.lower():
                return shop

        return None

    def list_shops(self) -> List[str]:
        """Get list of shop names"""
        return [shop.name for shop in self.shops.values()]


# Preset Villages
def create_starting_village() -> Village:
    """Create the starting village"""

    # General Store
    general_store = Shop(
        name="Thornwood General Store",
        description="A well-stocked shop selling basic adventuring supplies.",
        inventory=[
            ShopItem("torch", "Torch", 1, -1),
            ShopItem("rations", "Rations (1 day)", 5, -1),
            ShopItem("rope_50ft", "Rope (50 ft)", 10, -1),
            ShopItem("lantern", "Lantern", 100, -1),
            ShopItem("potion_healing", "Potion of Healing", 500, 5),
        ]
    )

    # Armory
    armory = Shop(
        name="Ironforge Armory",
        description="A smithy and armorer selling weapons and armor.",
        inventory=[
            ShopItem("dagger", "Dagger", 20, -1),
            ShopItem("shortsword", "Shortsword", 100, -1),
            ShopItem("longsword", "Longsword", 150, -1),
            ShopItem("mace", "Mace", 80, -1),
            ShopItem("staff", "Staff", 10, -1),
            ShopItem("leather_armor", "Leather Armor", 50, -1),
            ShopItem("chain_mail", "Chain Mail", 750, -1),
            ShopItem("plate_mail", "Plate Mail", 4000, 2),
            ShopItem("shield", "Shield", 100, -1),
        ]
    )

    # Magic Shop (rare items)
    magic_shop = Shop(
        name="Mystical Emporium",
        description="A mysterious shop dealing in magical items and curiosities.",
        inventory=[
            ShopItem("potion_healing", "Potion of Healing", 500, 10),
            ShopItem("longsword_plus1", "Longsword +1", 2000, 1),
            ShopItem("shortsword_plus1", "Shortsword +1", 1500, 1),
            ShopItem("dagger_plus1", "Dagger +1", 1000, 2),
            ShopItem("chain_mail_plus1", "Chain Mail +1", 3000, 1),
            ShopItem("shield_plus1", "Shield +1", 1500, 1),
        ],
        sell_price_multiplier=1.2  # Magic shop charges 20% premium
    )

    # Inn
    inn = Inn(
        name="The Prancing Pony Inn",
        description="A cozy inn with a warm fire and comfortable beds.",
        room_cost=10,
        healing_per_rest="1d4+1",
        meal_cost=1
    )

    # Tavern rumors
    rumors = [
        "I heard there's an abandoned mine to the north. They say it's full of treasure!",
        "A band of goblins has been raiding caravans on the old trade road.",
        "The crypts beneath the old temple are said to be haunted by restless dead.",
        "A wizard's tower collapsed years ago. Who knows what magical items remain?",
        "They say the sewers beneath the city are infested with giant rats.",
        "A dragon was spotted flying over the mountains last week!",
    ]

    return Village(
        name="Thornwood Village",
        description=(
            "A small but prosperous village at the edge of the wilderness. "
            "Well-maintained shops line the main street, and the smell of fresh bread "
            "wafts from the bakery. Adventurers frequent the tavern, sharing tales "
            "of dungeons explored and treasures won."
        ),
        shops={
            'general': general_store,
            'armory': armory,
            'magic': magic_shop
        },
        inn=inn,
        tavern_rumors=rumors
    )
