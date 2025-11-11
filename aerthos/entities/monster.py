"""
Monster class - extends Character with AI and treasure
"""

from typing import List, Optional
from dataclasses import dataclass, field
from .character import Character


@dataclass
class Monster(Character):
    """Monster with AI behavior and treasure"""

    # Monster-specific attributes
    hit_dice: str = "1d8"  # e.g., "2+1" or "4"
    damage: str = "1d6"    # Damage dice
    treasure_type: str = "None"
    xp_value: int = 10
    movement: int = 9
    morale: int = 7

    # Special abilities
    special_abilities: List[str] = field(default_factory=list)

    # AI behavior
    ai_behavior: str = 'aggressive'  # 'aggressive', 'defensive', 'flee_low_hp'

    # Description for display
    description: str = ""

    def should_flee(self) -> bool:
        """Determine if monster should flee based on HP and behavior"""
        if self.ai_behavior == 'flee_low_hp':
            # Flee if below 25% HP
            return self.hp_current <= (self.hp_max * 0.25)
        return False

    def has_special_ability(self, ability: str) -> bool:
        """Check if monster has a specific special ability"""
        return ability in self.special_abilities

    def is_immune_to(self, effect: str) -> bool:
        """Check if monster is immune to an effect"""
        immunities = {
            'sleep': ['immune_to_sleep', 'undead'],
            'charm': ['immune_to_charm', 'undead'],
            'poison': ['immune_to_poison', 'undead'],
            'paralysis': ['immune_to_paralysis', 'undead']
        }

        if effect in immunities:
            return any(ability in self.special_abilities
                      for ability in immunities[effect])
        return False

    def get_attack_description(self) -> str:
        """Get flavor text for monster attack"""
        attack_verbs = {
            'kobold': 'stabs',
            'goblin': 'slashes',
            'orc': 'swings brutally',
            'skeleton': 'strikes',
            'giant_rat': 'bites',
            'ogre': 'smashes',
        }

        # Get verb based on monster type (use lowercase name as key)
        monster_key = self.name.lower().replace(' ', '_')
        verb = attack_verbs.get(monster_key, 'attacks')

        return f"The {self.name} {verb}"
