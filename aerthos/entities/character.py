"""
Base Character class for all entities (PCs and Monsters)
Implements core AD&D 1e attributes and combat stats
"""

from typing import List, Optional
from dataclasses import dataclass, field


# AD&D 1e Nine-Point Alignment System
ALIGNMENTS = [
    "Lawful Good",
    "Neutral Good",
    "Chaotic Good",
    "Lawful Neutral",
    "True Neutral",
    "Chaotic Neutral",
    "Lawful Evil",
    "Neutral Evil",
    "Chaotic Evil"
]

# Alignment abbreviations for display
ALIGNMENT_ABBREV = {
    "Lawful Good": "LG",
    "Neutral Good": "NG",
    "Chaotic Good": "CG",
    "Lawful Neutral": "LN",
    "True Neutral": "TN",
    "Chaotic Neutral": "CN",
    "Lawful Evil": "LE",
    "Neutral Evil": "NE",
    "Chaotic Evil": "CE"
}


# Lazy-loaded ability modifier system to avoid circular imports
_ability_modifier_system = None


def _get_ability_system():
    """Get singleton AbilityModifierSystem instance"""
    global _ability_modifier_system
    if _ability_modifier_system is None:
        from ..systems.ability_modifiers import AbilityModifierSystem
        _ability_modifier_system = AbilityModifierSystem()
    return _ability_modifier_system


@dataclass
class Character:
    """Base class for all entities (Player Characters and Monsters)"""

    # Identity
    name: str
    race: str
    char_class: str
    level: int = 1
    title: str = "Adventurer"  # Level title (e.g., "Veteran", "Hero")
    alignment: str = "True Neutral"  # AD&D 1e nine-point alignment

    # Core Attributes (3-18 range, 3d6 each)
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    # Exceptional strength (18/01-18/00 for fighters)
    strength_percentile: int = 0  # 1-100 (0 = none)
    exceptional_strength: int = 0  # Alias for strength_percentile

    # Experience Points
    xp: int = 0
    xp_bonus_percent: int = 0  # Prime requisite bonus (usually 10% for 16+)

    # Combat Stats
    hp_current: int = 1
    hp_max: int = 1
    ac: int = 10  # Descending AC (10 = unarmored, 0 = plate+shield)
    thac0: int = 20  # To Hit AC 0
    attacks_per_round: float = 1.0  # Can be 1, 1.5, or 2

    # Size for damage calculations
    size: str = 'M'  # S, M, L

    # State
    is_alive: bool = True
    conditions: List[str] = field(default_factory=list)

    # Saving Throws (roll d20, must roll <= target to succeed)
    save_poison: int = 16
    save_rod_staff_wand: int = 17
    save_petrify_paralyze: int = 15
    save_breath: int = 20
    save_spell: int = 18

    def get_to_hit_bonus(self) -> int:
        """Calculate to-hit bonus from STR (for melee)"""
        system = _get_ability_system()
        mods = system.get_strength_modifiers(self.strength, self.strength_percentile)
        return mods.get('hit_prob', 0)

    def get_damage_bonus(self) -> int:
        """Calculate damage bonus from STR"""
        system = _get_ability_system()
        mods = system.get_strength_modifiers(self.strength, self.strength_percentile)
        return mods.get('damage', 0)

    def get_ac_bonus(self) -> int:
        """Calculate AC bonus from DEX (negative = better AC)"""
        system = _get_ability_system()
        mods = system.get_dexterity_modifiers(self.dexterity)
        return mods.get('defensive_adj', 0)

    def get_hp_bonus_per_level(self) -> int:
        """Calculate HP bonus per level from CON"""
        system = _get_ability_system()
        is_fighter = self.char_class in ['Fighter', 'Paladin', 'Ranger']
        mods = system.get_constitution_modifiers(self.constitution, is_fighter)
        return mods.get('hp_adjustment', 0)

    def take_damage(self, amount: int) -> bool:
        """Apply damage, return True if character died"""
        self.hp_current -= amount
        if self.hp_current <= 0:
            self.hp_current = 0
            self.is_alive = False
            return True
        return False

    def heal(self, amount: int) -> None:
        """Heal damage, cannot exceed max HP"""
        self.hp_current = min(self.hp_current + amount, self.hp_max)

    def has_condition(self, condition: str) -> bool:
        """Check if character has a specific condition"""
        return condition in self.conditions

    def add_condition(self, condition: str) -> None:
        """Add a condition if not already present"""
        if condition not in self.conditions:
            self.conditions.append(condition)

    def remove_condition(self, condition: str) -> None:
        """Remove a condition if present"""
        if condition in self.conditions:
            self.conditions.remove(condition)

    def is_incapacitated(self) -> bool:
        """Check if character can act"""
        return (not self.is_alive or
                self.has_condition('sleeping') or
                self.has_condition('paralyzed') or
                self.has_condition('unconscious'))

    def award_xp(self, xp_amount: int) -> None:
        """Award experience points (with prime requisite bonus)"""
        if self.xp_bonus_percent > 0:
            bonus = int(xp_amount * (self.xp_bonus_percent / 100.0))
            self.xp += xp_amount + bonus
        else:
            self.xp += xp_amount

    def get_xp_to_next_level(self) -> Optional[int]:
        """Get XP needed for next level"""
        # This will be calculated by the experience system
        return None  # Placeholder

    # Property accessors for standard abbreviations
    @property
    def str(self) -> int:
        """Strength (standard abbreviation)"""
        return self.strength

    @property
    def dex(self) -> int:
        """Dexterity (standard abbreviation)"""
        return self.dexterity

    @property
    def con(self) -> int:
        """Constitution (standard abbreviation)"""
        return self.constitution

    @property
    def int(self) -> int:
        """Intelligence (standard abbreviation)"""
        return self.intelligence

    @property
    def wis(self) -> int:
        """Wisdom (standard abbreviation)"""
        return self.wisdom

    @property
    def cha(self) -> int:
        """Charisma (standard abbreviation)"""
        return self.charisma
