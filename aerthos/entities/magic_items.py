"""
Magic Item Classes

Extended item classes for functional magic items with real mechanical effects.
Implements AD&D 1e magic item mechanics for potions, scrolls, rings, wands, etc.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from .player import Item, Weapon, Armor


@dataclass
class Potion(Item):
    """
    Potion with consumable magical effects

    Effects can be: healing, buff, debuff, transformation, protection
    """
    effect_type: str = "healing"  # healing, invisibility, flying, etc.
    effect_data: Dict = field(default_factory=dict)  # Effect parameters
    duration_turns: int = 0  # 0 = instant, >0 = duration
    xp_value: int = 0
    gp_value: int = 0

    def __post_init__(self):
        self.item_type = 'potion'

    def use(self, character) -> Dict:
        """
        Use potion and apply effects

        Returns:
            Dict with result info: {"success": bool, "message": str, "effects": []}
        """
        if self.effect_type == "healing":
            # Heal HP
            heal_amount = self.effect_data.get("heal_dice", "2d4+2")
            from ..engine.combat import DiceRoller
            healed = DiceRoller.roll(heal_amount)

            old_hp = character.hp_current
            character.hp_current = min(character.hp_current + healed, character.hp_max)
            actual_heal = character.hp_current - old_hp

            return {
                "success": True,
                "message": f"You drink the potion and feel your wounds mending. Restored {actual_heal} HP!",
                "effects": [{"type": "heal", "amount": actual_heal}]
            }

        elif self.effect_type == "poison":
            # Deal damage
            damage = self.effect_data.get("damage", "3d6")
            from ..engine.combat import DiceRoller
            dmg = DiceRoller.roll(damage)

            character.hp_current -= dmg

            return {
                "success": True,
                "message": f"You drink the potion and immediately feel violently ill! You take {dmg} damage from poison!",
                "effects": [{"type": "damage", "amount": dmg}]
            }

        elif self.effect_type in ["invisibility", "flying", "giant_strength", "speed", "levitation"]:
            # Apply temporary buff
            return {
                "success": True,
                "message": f"You drink the potion of {self.effect_type}. The effect will last {self.duration_turns} turns.",
                "effects": [{
                    "type": self.effect_type,
                    "duration": self.duration_turns,
                    "active": True
                }]
            }

        else:
            # Generic potion
            return {
                "success": True,
                "message": f"You drink the potion. {self.effect_data.get('description', 'Strange effects occur...')}",
                "effects": []
            }


@dataclass
class Scroll(Item):
    """
    Magical scroll with spell or protection effect

    Can contain spells (castable) or protection circles
    """
    scroll_type: str = "protection"  # protection, spell
    spell_name: Optional[str] = None
    spell_level: int = 1
    protection_type: Optional[str] = None  # demons, devils, undead, etc.
    duration_turns: int = 0
    xp_value: int = 0
    gp_value: int = 0

    def __post_init__(self):
        self.item_type = 'scroll'

    def use(self, character, target=None) -> Dict:
        """
        Read scroll and activate effect

        Args:
            character: Character reading scroll
            target: Target for spell scrolls

        Returns:
            Dict with result info
        """
        if self.scroll_type == "protection":
            return {
                "success": True,
                "message": f"You read the scroll aloud. A protective circle forms around you, warding against {self.protection_type}! Duration: {self.duration_turns} turns.",
                "effects": [{
                    "type": "protection",
                    "protection_against": self.protection_type,
                    "duration": self.duration_turns
                }]
            }

        elif self.scroll_type == "spell":
            # Spell scroll - cast the spell
            return {
                "success": True,
                "message": f"You read the scroll and cast {self.spell_name}! The scroll crumbles to dust.",
                "effects": [{
                    "type": "spell_cast",
                    "spell": self.spell_name,
                    "level": self.spell_level
                }]
            }

        return {"success": False, "message": "The scroll's magic fizzles.", "effects": []}


@dataclass
class Ring(Item):
    """
    Magic ring with continuous or activated effects

    Must be worn to function. Some rings are cursed.
    """
    ring_type: str = "protection"
    effect_data: Dict = field(default_factory=dict)
    is_cursed: bool = False
    charges: int = 0  # 0 = unlimited, >0 = limited use
    charges_remaining: int = 0
    xp_value: int = 0
    gp_value: int = 0

    def __post_init__(self):
        self.item_type = 'ring'
        if self.charges > 0:
            self.charges_remaining = self.charges

    def get_continuous_effect(self) -> Dict:
        """
        Get continuous effect while worn

        Returns:
            Dict with effect type and bonus
        """
        if self.ring_type == "protection":
            bonus = self.effect_data.get("ac_bonus", 1)
            return {"type": "ac_bonus", "value": bonus}

        elif self.ring_type == "invisibility":
            return {"type": "invisibility", "value": True}

        elif self.ring_type == "regeneration":
            return {"type": "regeneration", "rate": self.effect_data.get("hp_per_turn", 1)}

        elif self.ring_type == "fire_resistance":
            return {"type": "resistance", "element": "fire", "reduction": 0.5}

        return {"type": "none", "value": 0}

    def activate(self, character) -> Dict:
        """
        Activate ring power (for charged/activated rings)

        Returns:
            Dict with activation result
        """
        if self.ring_type == "wishes":
            if self.charges_remaining > 0:
                self.charges_remaining -= 1
                return {
                    "success": True,
                    "message": f"The ring glows with power! You have {self.charges_remaining} wishes remaining.",
                    "effects": [{"type": "wish", "granted": True}]
                }
            else:
                return {
                    "success": False,
                    "message": "The ring is depleted of wishes.",
                    "effects": []
                }

        elif self.ring_type == "spell_storing":
            return {
                "success": True,
                "message": "The ring releases its stored spell!",
                "effects": [{"type": "spell_release", "spells": self.effect_data.get("spells", [])}]
            }

        return {"success": False, "message": "This ring has no active power.", "effects": []}


@dataclass
class Wand(Item):
    """
    Wand with charges that cast spell-like effects

    Limited charges, typically 20-100.
    """
    wand_type: str = "magic_missiles"
    charges: int = 20
    charges_remaining: int = 20
    spell_effect: str = "magic_missile"
    effect_data: Dict = field(default_factory=dict)
    xp_value: int = 0
    gp_value: int = 0

    def __post_init__(self):
        self.item_type = 'wand'
        self.charges_remaining = self.charges

    def use(self, character, target=None) -> Dict:
        """
        Use wand to cast effect

        Args:
            character: Character using wand
            target: Target for effect

        Returns:
            Dict with result
        """
        if self.charges_remaining <= 0:
            return {
                "success": False,
                "message": "The wand is depleted of charges.",
                "effects": []
            }

        self.charges_remaining -= 1

        if self.wand_type == "magic_missiles":
            missiles = self.effect_data.get("missiles", 3)
            damage_per = self.effect_data.get("damage_per_missile", "1d4+1")

            return {
                "success": True,
                "message": f"You wave the wand! {missiles} glowing missiles streak toward your target! ({self.charges_remaining} charges remain)",
                "effects": [{
                    "type": "magic_missiles",
                    "count": missiles,
                    "damage_each": damage_per
                }]
            }

        elif self.wand_type == "fear":
            return {
                "success": True,
                "message": f"You point the wand! A cone of terror emanates from it! ({self.charges_remaining} charges remain)",
                "effects": [{
                    "type": "fear",
                    "save": "spell",
                    "duration": 6
                }]
            }

        return {
            "success": True,
            "message": f"The wand glows with power! ({self.charges_remaining} charges remain)",
            "effects": [{"type": self.wand_type}]
        }


@dataclass
class Staff(Item):
    """
    Magical staff with multiple powers and charges

    More powerful than wands, often with multiple effects.
    """
    staff_type: str = "striking"
    charges: int = 25
    charges_remaining: int = 25
    powers: List[str] = field(default_factory=list)
    effect_data: Dict = field(default_factory=dict)
    xp_value: int = 0
    gp_value: int = 0

    def __post_init__(self):
        self.item_type = 'staff'
        self.charges_remaining = self.charges

    def use(self, character, power_name: str = None, target=None) -> Dict:
        """
        Use staff power

        Args:
            character: Character using staff
            power_name: Which power to use
            target: Target for effect

        Returns:
            Dict with result
        """
        if self.charges_remaining <= 0:
            return {
                "success": False,
                "message": "The staff is depleted of charges.",
                "effects": []
            }

        # Default to first power if not specified
        if not power_name and self.powers:
            power_name = self.powers[0]
        elif not power_name:
            power_name = self.staff_type

        self.charges_remaining -= 1

        if self.staff_type == "striking":
            return {
                "success": True,
                "message": f"You strike with the staff! It crackles with magical energy! ({self.charges_remaining} charges remain)",
                "effects": [{
                    "type": "striking",
                    "damage_bonus": "3d6"
                }]
            }

        elif self.staff_type == "healing":
            heal_amount = self.effect_data.get("heal_amount", "2d8+2")
            return {
                "success": True,
                "message": f"The staff glows with healing light! ({self.charges_remaining} charges remain)",
                "effects": [{
                    "type": "healing",
                    "amount": heal_amount
                }]
            }

        return {
            "success": True,
            "message": f"The staff activates its {power_name} power! ({self.charges_remaining} charges remain)",
            "effects": [{"type": power_name}]
        }


@dataclass
class MiscMagic(Item):
    """
    Miscellaneous magic items (bags, boots, cloaks, etc.)

    Varied effects depending on item type.
    """
    magic_type: str = "bag_of_holding"
    effect_data: Dict = field(default_factory=dict)
    is_activated: bool = False  # For items that need activation
    charges: int = 0  # Some misc items have charges
    charges_remaining: int = 0
    xp_value: int = 0
    gp_value: int = 0

    def __post_init__(self):
        self.item_type = 'misc_magic'
        if self.charges > 0:
            self.charges_remaining = self.charges

    def get_passive_effect(self) -> Dict:
        """Get passive effect while carried/worn"""
        if self.magic_type == "bag_of_holding":
            return {
                "type": "carry_capacity",
                "bonus": self.effect_data.get("capacity", 500)
            }

        elif self.magic_type == "cloak_of_protection":
            return {
                "type": "ac_bonus",
                "value": self.effect_data.get("ac_bonus", 1)
            }

        elif self.magic_type == "boots_of_speed":
            return {
                "type": "movement",
                "multiplier": 2
            }

        return {"type": "none"}

    def activate(self, character) -> Dict:
        """Activate item power"""
        if self.magic_type == "boots_of_levitation":
            return {
                "success": True,
                "message": "You rise into the air, levitating several feet above the ground!",
                "effects": [{"type": "levitation", "duration": 10}]
            }

        elif self.magic_type == "rope_of_entanglement":
            if self.charges_remaining > 0:
                self.charges_remaining -= 1
                return {
                    "success": True,
                    "message": f"The rope animates and wraps around your target! ({self.charges_remaining} uses remain)",
                    "effects": [{"type": "entangle", "save": "paralysis"}]
                }

        return {"success": False, "message": "This item cannot be activated.", "effects": []}
