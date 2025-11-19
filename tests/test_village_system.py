"""
Test suite for Village System

Tests shops, inns, and village functionality
Addresses 0% coverage issue from Technical Debt document
"""

import unittest
from aerthos.world.village import (
    ShopItem, Shop, Inn, Village, create_starting_village
)


class TestShopItem(unittest.TestCase):
    """Test ShopItem dataclass"""

    def test_shop_item_creation(self):
        """Test creating shop items"""
        item = ShopItem(
            item_id="torch",
            item_name="Torch",
            price=1,
            stock=10
        )

        self.assertEqual(item.item_id, "torch")
        self.assertEqual(item.item_name, "Torch")
        self.assertEqual(item.price, 1)
        self.assertEqual(item.stock, 10)

    def test_shop_item_unlimited_stock(self):
        """Test unlimited stock (-1)"""
        item = ShopItem(
            item_id="rations",
            item_name="Rations",
            price=5,
            stock=-1
        )

        self.assertEqual(item.stock, -1)


class TestShop(unittest.TestCase):
    """Test Shop functionality"""

    def setUp(self):
        """Set up test shop"""
        self.shop = Shop(
            name="Test Shop",
            description="A test shop",
            inventory=[
                ShopItem("torch", "Torch", 10, 5),
                ShopItem("rope", "Rope", 20, -1),
                ShopItem("sword", "Sword", 100, 1)
            ]
        )

    def test_shop_creation(self):
        """Test shop creation"""
        self.assertEqual(self.shop.name, "Test Shop")
        self.assertEqual(len(self.shop.inventory), 3)
        self.assertEqual(self.shop.buy_price_multiplier, 0.5)
        self.assertEqual(self.shop.sell_price_multiplier, 1.0)

    def test_get_sell_price(self):
        """Test calculating sell price to player"""
        price = self.shop.get_sell_price("torch", "Torch", 100)
        self.assertEqual(price, 100)  # 1.0 multiplier

    def test_get_buy_price(self):
        """Test calculating buy price from player"""
        price = self.shop.get_buy_price("torch", "Torch", 100)
        self.assertEqual(price, 50)  # 0.5 multiplier

    def test_has_item_in_stock(self):
        """Test checking if item is in stock"""
        self.assertTrue(self.shop.has_item("torch"))
        self.assertTrue(self.shop.has_item("rope"))
        self.assertFalse(self.shop.has_item("nonexistent"))

    def test_has_item_out_of_stock(self):
        """Test item with 0 stock"""
        out_of_stock = Shop(
            name="Empty Shop",
            description="Test",
            inventory=[ShopItem("item", "Item", 10, 0)]
        )

        self.assertFalse(out_of_stock.has_item("item"))

    def test_purchase_item_limited_stock(self):
        """Test purchasing item with limited stock"""
        # Shop has 5 torches
        item = self.shop.purchase_item("torch")
        self.assertIsNotNone(item)
        self.assertEqual(item.item_name, "Torch")

        # Check stock reduced
        torch_item = next(i for i in self.shop.inventory if i.item_id == "torch")
        self.assertEqual(torch_item.stock, 4)

    def test_purchase_item_unlimited_stock(self):
        """Test purchasing item with unlimited stock"""
        item = self.shop.purchase_item("rope")
        self.assertIsNotNone(item)
        self.assertEqual(item.item_name, "Rope")

        # Stock should still be -1 (unlimited)
        rope_item = next(i for i in self.shop.inventory if i.item_id == "rope")
        self.assertEqual(rope_item.stock, -1)

    def test_purchase_item_last_in_stock(self):
        """Test purchasing last item in stock"""
        # Shop has 1 sword
        item = self.shop.purchase_item("sword")
        self.assertIsNotNone(item)

        # Try to purchase again - should fail
        item2 = self.shop.purchase_item("sword")
        self.assertIsNone(item2)

    def test_purchase_nonexistent_item(self):
        """Test purchasing item not in inventory"""
        item = self.shop.purchase_item("nonexistent")
        self.assertIsNone(item)

    def test_magic_shop_premium_pricing(self):
        """Test magic shop with premium pricing"""
        magic_shop = Shop(
            name="Magic Shop",
            description="Magical items",
            inventory=[ShopItem("wand", "Wand", 1000, 1)],
            sell_price_multiplier=1.2  # 20% premium
        )

        price = magic_shop.get_sell_price("wand", "Wand", 1000)
        self.assertEqual(price, 1200)  # 1000 * 1.2


class TestInn(unittest.TestCase):
    """Test Inn functionality"""

    def setUp(self):
        """Set up test inn"""
        self.inn = Inn(
            name="Test Inn",
            description="A cozy inn",
            room_cost=10,
            healing_per_rest="1d4+1",
            meal_cost=1
        )

    def test_inn_creation(self):
        """Test inn creation"""
        self.assertEqual(self.inn.name, "Test Inn")
        self.assertEqual(self.inn.room_cost, 10)
        self.assertEqual(self.inn.healing_per_rest, "1d4+1")
        self.assertEqual(self.inn.meal_cost, 1)

    def test_can_afford_room(self):
        """Test checking if player can afford room"""
        self.assertTrue(self.inn.can_afford_room(10))
        self.assertTrue(self.inn.can_afford_room(100))
        self.assertFalse(self.inn.can_afford_room(9))
        self.assertFalse(self.inn.can_afford_room(0))

    def test_can_afford_meal(self):
        """Test checking if player can afford meal"""
        self.assertTrue(self.inn.can_afford_meal(1))
        self.assertTrue(self.inn.can_afford_meal(100))
        self.assertFalse(self.inn.can_afford_meal(0))


class TestVillage(unittest.TestCase):
    """Test Village functionality"""

    def setUp(self):
        """Set up test village"""
        shop1 = Shop("General Store", "Basic supplies", [])
        shop2 = Shop("Armory", "Weapons and armor", [])

        self.village = Village(
            name="Test Village",
            description="A small village",
            shops={
                'general': shop1,
                'armory': shop2
            },
            inn=Inn("Test Inn", "Cozy inn", 10, "1d4+1", 1),
            tavern_rumors=["Rumor 1", "Rumor 2"]
        )

    def test_village_creation(self):
        """Test village creation"""
        self.assertEqual(self.village.name, "Test Village")
        self.assertEqual(len(self.village.shops), 2)
        self.assertIsNotNone(self.village.inn)
        self.assertEqual(len(self.village.tavern_rumors), 2)

    def test_get_shop_exact_match(self):
        """Test getting shop by exact name"""
        shop = self.village.get_shop("general")
        self.assertIsNotNone(shop)
        self.assertEqual(shop.name, "General Store")

    def test_get_shop_partial_match(self):
        """Test getting shop by partial name"""
        shop = self.village.get_shop("armor")
        self.assertIsNotNone(shop)
        self.assertEqual(shop.name, "Armory")

    def test_get_shop_case_insensitive(self):
        """Test shop search is case-insensitive"""
        shop = self.village.get_shop("GENERAL")
        self.assertIsNotNone(shop)
        self.assertEqual(shop.name, "General Store")

    def test_get_shop_not_found(self):
        """Test getting nonexistent shop"""
        shop = self.village.get_shop("nonexistent")
        self.assertIsNone(shop)

    def test_list_shops(self):
        """Test listing all shops"""
        shops = self.village.list_shops()
        self.assertEqual(len(shops), 2)
        self.assertIn("General Store", shops)
        self.assertIn("Armory", shops)


class TestStartingVillage(unittest.TestCase):
    """Test the preset starting village"""

    def setUp(self):
        """Create starting village"""
        self.village = create_starting_village()

    def test_starting_village_exists(self):
        """Test starting village is created"""
        self.assertIsNotNone(self.village)
        self.assertEqual(self.village.name, "Thornwood Village")

    def test_starting_village_has_shops(self):
        """Test starting village has all required shops"""
        self.assertEqual(len(self.village.shops), 3)
        self.assertIn('general', self.village.shops)
        self.assertIn('armory', self.village.shops)
        self.assertIn('magic', self.village.shops)

    def test_general_store_inventory(self):
        """Test general store has basic items"""
        general = self.village.shops['general']
        self.assertEqual(general.name, "Thornwood General Store")
        self.assertGreater(len(general.inventory), 0)

        # Check for specific items
        item_ids = [item.item_id for item in general.inventory]
        self.assertIn('torch', item_ids)
        self.assertIn('rations', item_ids)

    def test_armory_inventory(self):
        """Test armory has weapons and armor"""
        armory = self.village.shops['armory']
        self.assertEqual(armory.name, "Ironforge Armory")
        self.assertGreater(len(armory.inventory), 0)

        # Check for specific items
        item_ids = [item.item_id for item in armory.inventory]
        self.assertIn('longsword', item_ids)
        self.assertIn('chain_mail', item_ids)
        self.assertIn('shield', item_ids)

    def test_magic_shop_inventory(self):
        """Test magic shop has magic items"""
        magic = self.village.shops['magic']
        self.assertEqual(magic.name, "Mystical Emporium")
        self.assertGreater(len(magic.inventory), 0)

        # Check for specific items
        item_ids = [item.item_id for item in magic.inventory]
        self.assertIn('longsword_plus1', item_ids)
        self.assertIn('chain_mail_plus1', item_ids)

    def test_magic_shop_premium_pricing(self):
        """Test magic shop charges premium"""
        magic = self.village.shops['magic']
        self.assertEqual(magic.sell_price_multiplier, 1.2)

    def test_starting_village_has_inn(self):
        """Test starting village has inn"""
        self.assertIsNotNone(self.village.inn)
        self.assertEqual(self.village.inn.name, "The Prancing Pony Inn")
        self.assertEqual(self.village.inn.room_cost, 10)
        self.assertEqual(self.village.inn.meal_cost, 1)

    def test_starting_village_has_rumors(self):
        """Test starting village has tavern rumors"""
        self.assertGreater(len(self.village.tavern_rumors), 0)
        # All rumors should be strings
        for rumor in self.village.tavern_rumors:
            self.assertIsInstance(rumor, str)
            self.assertGreater(len(rumor), 0)

    def test_plate_mail_limited_stock(self):
        """Test that plate mail has limited stock"""
        armory = self.village.shops['armory']
        plate_mail = next((i for i in armory.inventory if i.item_id == 'plate_mail'), None)

        self.assertIsNotNone(plate_mail)
        self.assertEqual(plate_mail.stock, 2)

    def test_healing_potion_availability(self):
        """Test that healing potions are available in multiple shops"""
        general = self.village.shops['general']
        magic = self.village.shops['magic']

        general_ids = [item.item_id for item in general.inventory]
        magic_ids = [item.item_id for item in magic.inventory]

        self.assertIn('potion_healing', general_ids)
        self.assertIn('potion_healing', magic_ids)


if __name__ == '__main__':
    unittest.main()
