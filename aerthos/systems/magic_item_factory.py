"""
Magic Item Factory

Converts treasure generation dictionaries into functional magic item objects.
Bridges the gap between treasure tables and usable game items.
"""

import json
import re
from pathlib import Path
from typing import Dict, Optional, Union

from ..entities.player import Item, Weapon, Armor
from ..entities.magic_items import Potion, Scroll, Ring, Wand, Staff, MiscMagic


class MagicItemFactory:
    """
    Factory for creating functional magic item objects from treasure data

    Converts treasure generation dicts into actual Item subclass instances
    with proper mechanics and effects.
    """

    def __init__(self, items_path: Optional[Path] = None, magic_items_path: Optional[Path] = None):
        """
        Initialize factory with item data

        Args:
            items_path: Path to items.json (base items)
            magic_items_path: Path to magic_items.json (treasure tables)
        """
        if items_path is None:
            base_dir = Path(__file__).parent.parent
            items_path = base_dir / "data" / "items.json"

        if magic_items_path is None:
            base_dir = Path(__file__).parent.parent
            magic_items_path = base_dir / "data" / "magic_items.json"

        with open(items_path, 'r') as f:
            self.base_items = json.load(f)

        with open(magic_items_path, 'r') as f:
            self.magic_items = json.load(f)

    def create_from_treasure(self, treasure_dict: Dict) -> Union[Item, Potion, Scroll, Ring, Wand, Staff, MiscMagic]:
        """
        Create functional item from treasure generation dict

        Args:
            treasure_dict: Dict from treasure generation with keys:
                - type: item category (potion, scroll, weapon, armor, ring, etc.)
                - name: item name
                - xp_value: XP value
                - gp_value: GP value

        Returns:
            Functional Item subclass instance
        """
        item_type = treasure_dict.get("type", "misc")
        name = treasure_dict.get("name", "Unknown Item")
        xp_value = treasure_dict.get("xp_value", 0)
        gp_value = treasure_dict.get("gp_value", 0)

        if item_type == "potion":
            return self._create_potion(name, xp_value, gp_value)

        elif item_type == "scroll":
            return self._create_scroll(name, xp_value, gp_value)

        elif item_type == "weapon":
            return self._create_magic_weapon(name, xp_value, gp_value)

        elif item_type == "armor":
            return self._create_magic_armor(name, xp_value, gp_value)

        elif item_type == "ring":
            return self._create_ring(name, xp_value, gp_value)

        elif item_type == "wand":
            return self._create_wand(name, xp_value, gp_value)

        elif item_type == "staff":
            return self._create_staff(name, xp_value, gp_value)

        elif item_type == "misc":
            return self._create_misc_magic(name, xp_value, gp_value)

        # Fallback - create generic item
        return Item(
            name=name,
            item_type="magic_item",
            weight=1.0,
            properties={"xp_value": xp_value, "gp_value": gp_value}
        )

    def _create_potion(self, name: str, xp_value: int, gp_value: int) -> Potion:
        """Create potion from name"""
        # Extract potion type from name like "Potion of Healing"
        potion_name = name.replace("Potion of ", "").lower()

        # Map potion names to effects
        effect_mapping = {
            "healing": {"type": "healing", "data": {"heal_dice": "2d4+2"}, "duration": 0},
            "extra-healing": {"type": "healing", "data": {"heal_dice": "3d8"}, "duration": 0},
            "poison": {"type": "poison", "data": {"damage": "3d6"}, "duration": 0},
            "invisibility": {"type": "invisibility", "data": {}, "duration": 24},
            "flying": {"type": "flying", "data": {}, "duration": 30},
            "levitation": {"type": "levitation", "data": {}, "duration": 30},
            "giant strength": {"type": "giant_strength", "data": {"str_bonus": 6}, "duration": 24},
            "heroism": {"type": "heroism", "data": {"hp_bonus": 10, "thac0_bonus": 2}, "duration": 30},
            "speed": {"type": "speed", "data": {"movement_x2": True, "attacks_x2": True}, "duration": 15},
            "gaseous form": {"type": "gaseous_form", "data": {}, "duration": 20},
            "diminution": {"type": "diminution", "data": {}, "duration": 12},
            "growth": {"type": "growth", "data": {}, "duration": 12},
        }

        effect_info = effect_mapping.get(potion_name, {"type": "unknown", "data": {}, "duration": 0})

        return Potion(
            name=name,
            effect_type=effect_info["type"],
            effect_data=effect_info["data"],
            duration_turns=effect_info["duration"],
            xp_value=xp_value,
            gp_value=gp_value,
            weight=0.1,
            description=f"A magical potion with {potion_name} properties"
        )

    def _create_scroll(self, name: str, xp_value: int, gp_value: int) -> Scroll:
        """Create scroll from name"""
        # Determine if protection scroll or spell scroll
        if "Protection" in name or "protection" in name:
            # Protection scroll - extract protection type
            protection_types = {
                "Demons": "demons",
                "Devils": "devils",
                "Undead": "undead",
                "Lycanthropes": "lycanthropes",
                "Elementals": "elementals",
                "Magic": "magic"
            }

            protection_type = "magic"
            for key, value in protection_types.items():
                if key in name:
                    protection_type = value
                    break

            return Scroll(
                name=name,
                scroll_type="protection",
                protection_type=protection_type,
                duration_turns=60,  # 10 minutes per DMG
                xp_value=xp_value,
                gp_value=gp_value,
                weight=0.1,
                description=f"A magical scroll providing protection from {protection_type}"
            )
        else:
            # Spell scroll
            return Scroll(
                name=name,
                scroll_type="spell",
                spell_name=name.replace("Scroll of ", ""),
                spell_level=1,
                xp_value=xp_value,
                gp_value=gp_value,
                weight=0.1,
                description="A spell scroll that crumbles after reading"
            )

    def _create_magic_weapon(self, name: str, xp_value: int, gp_value: int) -> Weapon:
        """Create magic weapon from name"""
        # Extract base weapon type and bonus
        # Examples: "Sword +1", "Sword +2, Dragon Slayer", "Sword +3, Frost Brand"

        # Parse bonus
        bonus_match = re.search(r'\+(\d+)', name)
        magic_bonus = int(bonus_match.group(1)) if bonus_match else 1

        # Determine base weapon type
        base_weapon = "longsword"
        if "Sword" in name:
            base_weapon = "longsword"
        elif "Dagger" in name:
            base_weapon = "dagger"
        elif "Mace" in name:
            base_weapon = "mace"
        elif "Axe" in name:
            base_weapon = "battleaxe"

        # Get base weapon stats
        base_stats = self.base_items.get(base_weapon, {
            "damage_sm": "1d8",
            "damage_l": "1d12",
            "speed_factor": 5,
            "weight": 4
        })

        # Determine special properties
        properties = {"xp_value": xp_value, "gp_value": gp_value}

        if "Flame Tongue" in name or "flame tongue" in name:
            properties["special"] = "flame_tongue"
            properties["fire_damage"] = "1d4+1"
            properties["description"] = "Deals extra fire damage"

        elif "Frost Brand" in name or "frost brand" in name:
            properties["special"] = "frost_brand"
            properties["cold_damage"] = "1d6"
            properties["description"] = "Deals extra cold damage and protects from fire"

        elif "Dragon Slayer" in name or "dragon slayer" in name:
            properties["special"] = "dragon_slayer"
            properties["bonus_vs_dragons"] = 3
            properties["description"] = f"Additional +3 bonus vs dragons (total +{magic_bonus + 3})"

        elif "Lycanthropes" in name or "lycanthropes" in name:
            properties["special"] = "vs_lycanthropes"
            properties["bonus_vs_lycanthropes"] = 2
            properties["description"] = f"Additional +2 bonus vs lycanthropes (total +{magic_bonus + 2})"

        weapon = Weapon(
            name=name,
            damage_sm=base_stats.get("damage_sm", "1d8"),
            damage_l=base_stats.get("damage_l", "1d12"),
            speed_factor=base_stats.get("speed_factor", 5),
            magic_bonus=magic_bonus,
            weight=base_stats.get("weight", 4),
            properties=properties,
            description=properties.get("description", f"A magical {base_weapon} +{magic_bonus}")
        )
        # Add xp and gp values as attributes for easy access
        weapon.xp_value = xp_value
        weapon.gp_value = gp_value
        return weapon

    def _create_magic_armor(self, name: str, xp_value: int, gp_value: int) -> Armor:
        """Create magic armor from name"""
        # Parse bonus and type
        # Examples: "Chain Mail +1", "Plate Mail +2", "Shield +1"

        bonus_match = re.search(r'\+(\d+)', name)
        magic_bonus = int(bonus_match.group(1)) if bonus_match else 1

        # Determine armor type and base AC
        ac_bonus = 0
        is_shield = False

        if "Leather" in name:
            ac_bonus = 2
        elif "Chain" in name:
            ac_bonus = 5
        elif "Plate" in name or "Plate Mail" in name:
            ac_bonus = 8
        elif "Shield" in name:
            ac_bonus = 1
            is_shield = True

        # Check for cursed
        is_cursed = "Cursed" in name or "cursed" in name
        if is_cursed:
            magic_bonus = -1  # Cursed armor makes AC worse

        armor = Armor(
            name=name,
            ac_bonus=ac_bonus,
            magic_bonus=magic_bonus,
            weight=25 if not is_shield else 5,
            properties={
                "xp_value": xp_value,
                "gp_value": gp_value,
                "is_cursed": is_cursed,
                "is_shield": is_shield
            },
            description=f"Magical armor providing AC {ac_bonus + magic_bonus}"
        )
        # Add xp and gp values as attributes for easy access
        armor.xp_value = xp_value
        armor.gp_value = gp_value
        return armor

    def _create_ring(self, name: str, xp_value: int, gp_value: int) -> Ring:
        """Create magic ring from name"""
        # Parse ring type from name
        ring_name = name.replace("Ring of ", "").lower()

        ring_types = {
            "protection": {"type": "protection", "data": {"ac_bonus": 1}, "charges": 0},
            "invisibility": {"type": "invisibility", "data": {}, "charges": 0},
            "regeneration": {"type": "regeneration", "data": {"hp_per_turn": 1}, "charges": 0},
            "fire resistance": {"type": "fire_resistance", "data": {}, "charges": 0},
            "feather falling": {"type": "feather_falling", "data": {}, "charges": 0},
            "spell storing": {"type": "spell_storing", "data": {"spells": []}, "charges": 0},
            "water walking": {"type": "water_walking", "data": {}, "charges": 0},
            "x-ray vision": {"type": "xray_vision", "data": {}, "charges": 0},
        }

        # Handle wishes specially
        if "wishes" in ring_name.lower():
            # Parse number of wishes from name
            if "(1-2)" in name:
                charges = 2
            elif "(3)" in name:
                charges = 3
            else:
                charges = 1

            return Ring(
                name=name,
                ring_type="wishes",
                effect_data={"wish_type": "limited"},
                charges=charges,
                charges_remaining=charges,
                xp_value=xp_value,
                gp_value=gp_value,
                weight=0.1,
                description=f"A ring with {charges} wishes"
            )

        # Handle protection +N
        if "protection" in ring_name:
            bonus_match = re.search(r'\+(\d+)', name)
            bonus = int(bonus_match.group(1)) if bonus_match else 1

            return Ring(
                name=name,
                ring_type="protection",
                effect_data={"ac_bonus": bonus},
                xp_value=xp_value,
                gp_value=gp_value,
                weight=0.1,
                description=f"Provides +{bonus} bonus to AC"
            )

        # Check for cursed rings
        is_cursed = "cursed" in ring_name or "contrariness" in ring_name or "delusion" in ring_name or "weakness" in ring_name

        # Get ring info or default
        ring_info = ring_types.get(ring_name, {"type": "unknown", "data": {}, "charges": 0})

        return Ring(
            name=name,
            ring_type=ring_info["type"],
            effect_data=ring_info["data"],
            is_cursed=is_cursed,
            charges=ring_info["charges"],
            xp_value=xp_value,
            gp_value=gp_value,
            weight=0.1,
            description=f"A magical ring of {ring_name}"
        )

    def _create_wand(self, name: str, xp_value: int, gp_value: int) -> Wand:
        """Create wand from name"""
        import random

        wand_types = {
            "Magic Missiles": {
                "type": "magic_missiles",
                "spell": "magic_missile",
                "data": {"missiles": 3, "damage_per_missile": "1d4+1"}
            },
            "Fear": {
                "type": "fear",
                "spell": "fear",
                "data": {"save": "spell", "duration": 6}
            },
            "Frost": {
                "type": "frost",
                "spell": "cone_of_cold",
                "data": {"damage": "6d6", "save": "spell"}
            },
            "Lightning": {
                "type": "lightning",
                "spell": "lightning_bolt",
                "data": {"damage": "6d6", "save": "spell"}
            }
        }

        wand_type = "magic_missiles"
        wand_info = wand_types["Magic Missiles"]

        for key, value in wand_types.items():
            if key in name:
                wand_type = value["type"]
                wand_info = value
                break

        # Random charges (20-100 typical for wands)
        charges = random.randint(20, 50)

        return Wand(
            name=name,
            wand_type=wand_info["type"],
            charges=charges,
            charges_remaining=charges,
            spell_effect=wand_info["spell"],
            effect_data=wand_info["data"],
            xp_value=xp_value,
            gp_value=gp_value,
            weight=1.0,
            description=f"A wand with {charges} charges"
        )

    def _create_staff(self, name: str, xp_value: int, gp_value: int) -> Staff:
        """Create staff from name"""
        import random

        staff_types = {
            "Striking": {
                "type": "striking",
                "powers": ["striking"],
                "data": {"damage_bonus": "3d6"}
            },
            "Healing": {
                "type": "healing",
                "powers": ["cure_light_wounds", "cure_serious_wounds"],
                "data": {"heal_amount": "2d8+2"}
            },
            "Command": {
                "type": "command",
                "powers": ["command", "charm"],
                "data": {}
            }
        }

        staff_type = "striking"
        staff_info = staff_types["Striking"]

        for key, value in staff_types.items():
            if key in name:
                staff_type = value["type"]
                staff_info = value
                break

        # Staves have more charges than wands
        charges = random.randint(25, 50)

        return Staff(
            name=name,
            staff_type=staff_info["type"],
            charges=charges,
            charges_remaining=charges,
            powers=staff_info["powers"],
            effect_data=staff_info["data"],
            xp_value=xp_value,
            gp_value=gp_value,
            weight=4.0,
            description=f"A staff with {charges} charges and powers: {', '.join(staff_info['powers'])}"
        )

    def _create_misc_magic(self, name: str, xp_value: int, gp_value: int) -> MiscMagic:
        """Create miscellaneous magic item from name"""
        misc_types = {
            "Bag of Holding": {
                "type": "bag_of_holding",
                "data": {"capacity": 500},
                "charges": 0
            },
            "Boots of Levitation": {
                "type": "boots_of_levitation",
                "data": {},
                "charges": 0
            },
            "Boots of Speed": {
                "type": "boots_of_speed",
                "data": {"movement_multiplier": 2},
                "charges": 0
            },
            "Cloak of Protection": {
                "type": "cloak_of_protection",
                "data": {"ac_bonus": 1},
                "charges": 0
            },
            "Cloak of Displacement": {
                "type": "cloak_of_displacement",
                "data": {"ac_bonus": 2, "save_bonus": 2},
                "charges": 0
            },
            "Gauntlets of Ogre Power": {
                "type": "gauntlets_ogre_power",
                "data": {"str_bonus": 6},
                "charges": 0
            },
            "Rope of Entanglement": {
                "type": "rope_of_entanglement",
                "data": {},
                "charges": 10
            }
        }

        magic_type = "unknown"
        effect_data = {}
        charges = 0

        for key, value in misc_types.items():
            if key in name:
                magic_type = value["type"]
                effect_data = value["data"]
                charges = value["charges"]
                break

        return MiscMagic(
            name=name,
            magic_type=magic_type,
            effect_data=effect_data,
            charges=charges,
            charges_remaining=charges,
            xp_value=xp_value,
            gp_value=gp_value,
            weight=1.0,
            description=f"A magical {name}"
        )


# Convenience function
def create_magic_item(treasure_dict: Dict) -> Item:
    """
    Create magic item from treasure dict

    Args:
        treasure_dict: Dict with type, name, xp_value, gp_value

    Returns:
        Functional Item instance
    """
    factory = MagicItemFactory()
    return factory.create_from_treasure(treasure_dict)
