"""
Monster Special Abilities System

Implements AD&D 1e monster special abilities with mechanical effects.
Handles breath weapons, poison, regeneration, level drain, and more.
"""

import random
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AbilityResult:
    """Result of using a special ability"""
    success: bool
    message: str
    damage: int = 0
    effects: List[Dict] = None
    save_allowed: bool = False
    save_type: str = None
    save_dc: int = 0

    def __post_init__(self):
        if self.effects is None:
            self.effects = []


class MonsterSpecialAbilities:
    """
    Handler for monster special abilities

    Implements mechanical effects for:
    - Breath weapons (fire, cold, acid, lightning, gas)
    - Poison (on hit, bite, sting)
    - Regeneration
    - Level drain
    - Magic resistance
    - Special immunities
    - Fear/paralysis auras
    """

    def __init__(self):
        """Initialize abilities system"""
        pass

    def use_ability(self, monster, ability_name: str, targets: List = None) -> AbilityResult:
        """
        Use a monster's special ability

        Args:
            monster: Monster using the ability
            ability_name: Name of ability to use
            targets: List of targets (if applicable)

        Returns:
            AbilityResult with effects
        """
        # Route to appropriate handler
        if "breath" in ability_name.lower():
            return self._breath_weapon(monster, ability_name, targets)

        elif "poison" in ability_name.lower():
            return self._poison_attack(monster, ability_name, targets)

        elif "regenerat" in ability_name.lower():
            return self._regeneration(monster)

        elif "drain" in ability_name.lower() and "level" in ability_name.lower():
            return self._level_drain(monster, targets)

        elif "paralyz" in ability_name.lower() or "paralyze" in ability_name.lower():
            return self._paralysis(monster, targets)

        elif "gaze" in ability_name.lower():
            return self._gaze_attack(monster, ability_name, targets)

        elif "constrict" in ability_name.lower():
            return self._constriction(monster, targets)

        else:
            # Generic ability
            return AbilityResult(
                success=True,
                message=f"{monster.name} uses {ability_name}!",
                effects=[{"type": ability_name}]
            )

    def _breath_weapon(self, monster, ability_name: str, targets: List) -> AbilityResult:
        """
        Breath weapon attack

        Damage typically = monster's current HP
        Save for half damage
        """
        # Determine breath type
        breath_types = {
            "fire": {"damage_multiplier": 1.0, "save": "breath", "element": "fire"},
            "cold": {"damage_multiplier": 1.0, "save": "breath", "element": "cold"},
            "acid": {"damage_multiplier": 1.0, "save": "breath", "element": "acid"},
            "lightning": {"damage_multiplier": 1.0, "save": "breath", "element": "lightning"},
            "gas": {"damage_multiplier": 0.5, "save": "poison", "element": "poison"},
            "chlorine": {"damage_multiplier": 1.0, "save": "poison", "element": "poison"}
        }

        breath_type = "fire"
        for key in breath_types:
            if key in ability_name.lower():
                breath_type = key
                break

        breath_info = breath_types[breath_type]

        # Calculate damage (typically = current HP of dragon)
        base_damage = int(monster.hp_current * breath_info["damage_multiplier"])

        return AbilityResult(
            success=True,
            message=f"{monster.name} breathes {breath_type}! A cone of {breath_type} engulfs the area!",
            damage=base_damage,
            save_allowed=True,
            save_type=breath_info["save"],
            effects=[{
                "type": "breath_weapon",
                "element": breath_info["element"],
                "base_damage": base_damage,
                "save_for_half": True
            }]
        )

    def _poison_attack(self, monster, ability_name: str, targets: List) -> AbilityResult:
        """
        Poison attack

        Can be: instant death, damage, paralysis, weakness
        """
        # Determine poison type
        poison_types = {
            "deadly": {
                "save": "poison",
                "effect": "death",
                "damage": 0,
                "description": "deadly poison - save or die!"
            },
            "paralytic": {
                "save": "paralysis",
                "effect": "paralysis",
                "damage": 0,
                "duration": 24,  # 4 hours
                "description": "paralytic venom - save or be paralyzed!"
            },
            "weakening": {
                "save": "poison",
                "effect": "ability_damage",
                "damage": "2d6",
                "stat": "str",
                "description": "weakening poison - reduces Strength!"
            },
            "damaging": {
                "save": "poison",
                "effect": "damage",
                "damage": "3d6",
                "description": "toxic venom - deals poison damage!"
            }
        }

        # Default to damaging poison
        poison_type = "damaging"
        if "deadly" in ability_name.lower():
            poison_type = "deadly"
        elif "paralyz" in ability_name.lower():
            poison_type = "paralytic"
        elif "weaken" in ability_name.lower():
            poison_type = "weakening"

        poison_info = poison_types[poison_type]

        return AbilityResult(
            success=True,
            message=f"{monster.name} injects {poison_info['description']}",
            damage=0,  # Damage applied after save
            save_allowed=True,
            save_type=poison_info["save"],
            effects=[{
                "type": "poison",
                "poison_type": poison_type,
                "effect": poison_info["effect"],
                "damage": poison_info.get("damage", 0),
                "duration": poison_info.get("duration", 0)
            }]
        )

    def _regeneration(self, monster) -> AbilityResult:
        """
        Regeneration - heal HP each round

        Typically 1-3 HP per round
        """
        regen_rate = 1

        # Some monsters have specific regen rates
        if hasattr(monster, 'regeneration_rate'):
            regen_rate = monster.regeneration_rate
        elif 'troll' in monster.name.lower():
            regen_rate = 3  # Trolls regen 3 HP/round
        elif 'vampire' in monster.name.lower():
            regen_rate = 3

        # Heal the monster
        old_hp = monster.hp_current
        monster.hp_current = min(monster.hp_current + regen_rate, monster.hp_max)
        actual_heal = monster.hp_current - old_hp

        return AbilityResult(
            success=True,
            message=f"{monster.name} regenerates {actual_heal} HP! (Now at {monster.hp_current}/{monster.hp_max})",
            effects=[{
                "type": "regeneration",
                "amount": actual_heal,
                "rate_per_round": regen_rate
            }]
        )

    def _level_drain(self, monster, targets: List) -> AbilityResult:
        """
        Level drain - reduce target's level and max HP

        Typically 1-2 levels per hit
        """
        drain_levels = 1

        if 'vampire' in monster.name.lower():
            drain_levels = 2
        elif 'wight' in monster.name.lower():
            drain_levels = 1
        elif 'wraith' in monster.name.lower():
            drain_levels = 1
        elif 'spectre' in monster.name.lower():
            drain_levels = 2

        return AbilityResult(
            success=True,
            message=f"{monster.name}'s chilling touch drains {drain_levels} level(s) of life force!",
            save_allowed=False,  # No save vs level drain in AD&D 1e
            effects=[{
                "type": "level_drain",
                "levels_lost": drain_levels,
                "permanent": True
            }]
        )

    def _paralysis(self, monster, targets: List) -> AbilityResult:
        """
        Paralysis attack

        Duration typically 3d6 turns (30-180 minutes)
        """
        return AbilityResult(
            success=True,
            message=f"{monster.name} touches you! A wave of paralysis washes over you!",
            save_allowed=True,
            save_type="paralysis",
            effects=[{
                "type": "paralysis",
                "duration": random.randint(3, 18),  # 3d6 turns
                "save_negates": True
            }]
        )

    def _gaze_attack(self, monster, ability_name: str, targets: List) -> AbilityResult:
        """
        Gaze attacks (medusa, basilisk, etc.)

        Effects: petrification, death, charm, etc.
        """
        gaze_types = {
            "petrif": {"effect": "petrification", "save": "petrify", "description": "petrifying gaze"},
            "death": {"effect": "death", "save": "poison", "description": "death gaze"},
            "charm": {"effect": "charm", "save": "spell", "description": "charming gaze"}
        }

        gaze_type = "petrif"
        for key in gaze_types:
            if key in ability_name.lower():
                gaze_type = key
                break

        gaze_info = gaze_types[gaze_type]

        return AbilityResult(
            success=True,
            message=f"{monster.name}'s {gaze_info['description']} meets your eyes!",
            save_allowed=True,
            save_type=gaze_info["save"],
            effects=[{
                "type": "gaze_attack",
                "effect": gaze_info["effect"],
                "save_negates": True
            }]
        )

    def _constriction(self, monster, targets: List) -> AbilityResult:
        """
        Constriction damage (snakes, etc.)

        Automatic damage each round while grappled
        """
        # Constriction damage typically 2d4 for medium snakes, up to 2d8 for large
        constrict_damage = "2d4"

        if hasattr(monster, 'hit_dice'):
            hd = monster.hit_dice
            if '+' in str(hd) or int(str(hd).split('+')[0] if '+' in str(hd) else hd) >= 6:
                constrict_damage = "2d8"

        from ..engine.combat import DiceRoller
        damage = DiceRoller.roll(constrict_damage)

        return AbilityResult(
            success=True,
            message=f"{monster.name} constricts you for {damage} damage!",
            damage=damage,
            save_allowed=False,
            effects=[{
                "type": "constriction",
                "damage_per_round": constrict_damage,
                "grappled": True
            }]
        )

    def check_magic_resistance(self, monster, spell_level: int) -> bool:
        """
        Check if spell is resisted by magic resistance

        Args:
            monster: Monster with magic resistance
            spell_level: Level of spell being cast

        Returns:
            True if spell is resisted, False otherwise
        """
        if not hasattr(monster, 'magic_resistance'):
            return False

        resistance = monster.magic_resistance

        # Roll percentile
        roll = random.randint(1, 100)

        # Magic resistance is a percentage chance to resist
        return roll <= resistance

    def apply_immunity(self, monster, damage_type: str) -> Dict:
        """
        Check if monster is immune to damage type

        Args:
            monster: Monster to check
            damage_type: Type of damage (fire, cold, poison, etc.)

        Returns:
            Dict with immunity info
        """
        immunities = {
            "fire": ["fire_elemental", "efreeti", "fire_giant", "red_dragon"],
            "cold": ["white_dragon", "frost_giant", "ice_toad"],
            "poison": ["undead", "golem", "elemental"],
            "lightning": ["blue_dragon", "air_elemental"],
            "acid": ["black_dragon", "gelatinous_cube"]
        }

        monster_type = monster.name.lower().replace(" ", "_")

        # Check specific immunities
        if damage_type in immunities:
            for immune_type in immunities[damage_type]:
                if immune_type in monster_type:
                    return {
                        "immune": True,
                        "message": f"{monster.name} is immune to {damage_type} damage!"
                    }

        # Check special_abilities list
        if hasattr(monster, 'special_abilities'):
            immune_ability = f"immune_to_{damage_type}"
            if immune_ability in monster.special_abilities:
                return {
                    "immune": True,
                    "message": f"{monster.name} is immune to {damage_type} damage!"
                }

        return {"immune": False, "message": ""}


# Convenience function
def use_monster_ability(monster, ability_name: str, targets: List = None) -> AbilityResult:
    """
    Use a monster's special ability

    Args:
        monster: Monster using ability
        ability_name: Name of ability
        targets: Targets of ability

    Returns:
        AbilityResult
    """
    abilities = MonsterSpecialAbilities()
    return abilities.use_ability(monster, ability_name, targets)
