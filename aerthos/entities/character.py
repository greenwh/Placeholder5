"""
Base Character class for all entities (PCs and Monsters)
Implements core AD&D 1e attributes and combat stats
"""

from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class Character:
    """Base class for all entities (Player Characters and Monsters)"""

    # Identity
    name: str
    race: str
    char_class: str
    level: int = 1

    # Core Attributes (3-18 range, 3d6 each)
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    # Exceptional strength (18/xx for fighters)
    strength_percentile: int = 0

    # Combat Stats
    hp_current: int = 1
    hp_max: int = 1
    ac: int = 10  # Descending AC (10 = unarmored, 0 = plate+shield)
    thac0: int = 20  # To Hit AC 0

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
        if self.strength >= 18:
            if self.strength_percentile >= 91:
                return 3
            elif self.strength_percentile >= 51:
                return 2
            else:
                return 1
        elif self.strength >= 17:
            return 1
        elif self.strength <= 5:
            return -2
        elif self.strength <= 6:
            return -1
        return 0

    def get_damage_bonus(self) -> int:
        """Calculate damage bonus from STR"""
        if self.strength >= 18:
            if self.strength_percentile >= 91:
                return 5
            elif self.strength_percentile >= 76:
                return 4
            elif self.strength_percentile >= 51:
                return 3
            else:
                return 2
        elif self.strength >= 17:
            return 1
        elif self.strength <= 5:
            return -2
        elif self.strength <= 6:
            return -1
        return 0

    def get_ac_bonus(self) -> int:
        """Calculate AC bonus from DEX (negative = better AC)"""
        if self.dexterity >= 18:
            return -4
        elif self.dexterity >= 17:
            return -3
        elif self.dexterity >= 16:
            return -2
        elif self.dexterity >= 15:
            return -1
        elif self.dexterity <= 5:
            return 4
        elif self.dexterity <= 6:
            return 3
        elif self.dexterity <= 7:
            return 2
        elif self.dexterity <= 8:
            return 1
        return 0

    def get_hp_bonus_per_level(self) -> int:
        """Calculate HP bonus per level from CON"""
        if self.constitution >= 17:
            return 3
        elif self.constitution >= 16:
            return 2
        elif self.constitution >= 15:
            return 1
        elif self.constitution <= 6:
            return -1
        elif self.constitution <= 3:
            return -2
        return 0

    def take_damage(self, amount: int) -> bool:
        """Apply damage, return True if character died"""
        self.hp_current -= amount
        if self.hp_current <= 0:
            self.hp_current = 0
            self.is_alive = False
            return True
        return False

    def heal(self, amount: int):
        """Heal damage, cannot exceed max HP"""
        self.hp_current = min(self.hp_current + amount, self.hp_max)

    def has_condition(self, condition: str) -> bool:
        """Check if character has a specific condition"""
        return condition in self.conditions

    def add_condition(self, condition: str):
        """Add a condition if not already present"""
        if condition not in self.conditions:
            self.conditions.append(condition)

    def remove_condition(self, condition: str):
        """Remove a condition if present"""
        if condition in self.conditions:
            self.conditions.remove(condition)

    def is_incapacitated(self) -> bool:
        """Check if character can act"""
        return (not self.is_alive or
                self.has_condition('sleeping') or
                self.has_condition('paralyzed') or
                self.has_condition('unconscious'))
