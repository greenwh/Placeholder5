"""
Monster class - extends Character with AI and treasure
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from .character import Character


@dataclass
class Monster(Character):
    """Monster with AI behavior and treasure"""

    # Monster-specific attributes
    hit_dice: str = "1d8"  # e.g., "2+1" or "4"
    damage: str = "1d6"    # Damage dice
    treasure_type: str = "None"
    xp_value: int = 10  # Static fallback, will be calculated dynamically
    movement: int = 9
    morale: int = 7

    # Special abilities
    special_abilities: List[str] = field(default_factory=list)

    # AI behavior
    ai_behavior: str = 'aggressive'  # 'aggressive', 'defensive', 'flee_low_hp'

    # Description for display
    description: str = ""

    # XP formula from monsters_enhanced.json (optional)
    xp_formula: Optional[Dict[str, Any]] = None

    # Flag to control whether to use dynamic XP calculation
    use_dynamic_xp: bool = True

    def __post_init__(self):
        """Calculate dynamic XP after monster creation"""
        if self.use_dynamic_xp:
            self._calculate_xp()

    def _calculate_xp(self):
        """
        Calculate XP value dynamically using AD&D 1e formula

        Priority:
        1. If xp_formula exists, use it (from monsters_enhanced.json)
        2. Otherwise, calculate from hit_dice and hp_max
        3. If calculation fails, keep static xp_value
        """
        try:
            if self.xp_formula:
                # Use pre-computed formula
                from ..systems.xp_calculator import XPCalculator
                self.xp_value = XPCalculator.calculate_xp_from_formula(
                    self.hp_max,
                    self.xp_formula
                )
            else:
                # Calculate from HD and HP
                from ..systems.xp_calculator import XPCalculator
                self.xp_value = XPCalculator.calculate_xp(
                    self.hit_dice,
                    self.hp_max,
                    self.special_abilities
                )
        except Exception as e:
            # If calculation fails, keep the static xp_value
            # This ensures backward compatibility
            pass

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
