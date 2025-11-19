"""
Saving Throw system for AD&D 1e
5 categories: Poison, Rod/Staff/Wand, Petrify/Paralyze, Breath, Spell
"""

import json
import random
from pathlib import Path
from typing import Dict, Optional
from ..entities.character import Character


class SavingThrowResolver:
    """
    Handles saving throw resolution

    In AD&D 1e, saving throws work by rolling d20 and trying to roll
    LESS THAN OR EQUAL TO your save value. Lower save values are better.

    Natural 1 always succeeds
    Natural 20 always fails
    """

    CATEGORIES = {
        'poison': 'save_poison',
        'death': 'save_poison',  # Alias
        'rod': 'save_rod_staff_wand',
        'staff': 'save_rod_staff_wand',
        'wand': 'save_rod_staff_wand',
        'petrify': 'save_petrify_paralyze',
        'petrification': 'save_petrify_paralyze',
        'paralyze': 'save_petrify_paralyze',
        'paralysis': 'save_petrify_paralyze',
        'breath': 'save_breath',
        'dragon_breath': 'save_breath',
        'spell': 'save_spell',
        'magic': 'save_spell'
    }

    # Mental saves are affected by WIS (magic attack adjustment)
    # Per PH: "Applies to saving throw versus mental attack forms
    # (e.g., charm, fear, illusion, suggestion)"
    MENTAL_SAVES = {
        'save_rod_staff_wand',
        'save_petrify_paralyze',
        'save_spell'
    }

    def __init__(self):
        """Load saving throw progression tables"""
        data_path = Path(__file__).parent.parent / 'data' / 'saving_throw_tables.json'
        with open(data_path, 'r') as f:
            self.tables = json.load(f)

    def get_saves_for_level(self, char_class: str, level: int, race_bonus: int = 0) -> Dict[str, int]:
        """
        Get all saving throws for a character of given class and level

        Args:
            char_class: Character class name
            level: Character level (1-based)
            race_bonus: Racial bonus (Dwarf/Halfling/Gnome get +1 per 3.5 CON)

        Returns:
            Dictionary with all five saving throw values
        """
        if char_class not in self.tables:
            # Default to Fighter if class not found
            char_class = 'Fighter'

        class_table = self.tables[char_class]

        # Level is 1-based, arrays are 0-based
        index = max(0, min(level - 1, len(class_table['poison_death']) - 1))

        return {
            'save_poison': class_table['poison_death'][index] - race_bonus,
            'save_rod_staff_wand': class_table['rod_staff_wand'][index] - race_bonus,
            'save_petrify_paralyze': class_table['petrify_paralyze'][index] - race_bonus,
            'save_breath': class_table['breath'][index] - race_bonus,
            'save_spell': class_table['spell'][index] - race_bonus
        }

    def update_character_saves(self, character: Character, race_bonus: int = 0):
        """
        Update a character's saving throws based on their class and level

        Args:
            character: Character to update
            race_bonus: Racial saving throw bonus
        """
        saves = self.get_saves_for_level(character.char_class, character.level, race_bonus)
        character.save_poison = saves['save_poison']
        character.save_rod_staff_wand = saves['save_rod_staff_wand']
        character.save_petrify_paralyze = saves['save_petrify_paralyze']
        character.save_breath = saves['save_breath']
        character.save_spell = saves['save_spell']

    def get_racial_save_bonus(self, character: Character) -> int:
        """
        Calculate racial saving throw bonus

        Dwarves, Gnomes, and Halflings get +1 per 3.5 CON (max +5)
        Applies to saves vs poison, magic, wands, staves, rods, and spells

        Args:
            character: Character to check

        Returns:
            Bonus value (0-5)
        """
        from ..systems.racial_abilities import RacialAbilitiesSystem

        racial_system = RacialAbilitiesSystem()
        return racial_system.get_saving_throw_bonus(character.race, character.constitution)

    def get_wisdom_save_bonus(self, character: Character, save_type: str) -> int:
        """
        Calculate WIS-based saving throw bonus for mental saves

        Per PH: "Applies to saving throw versus mental attack forms"
        Mental saves: Rod/Staff/Wand, Petrification/Paralysis, Spell

        Args:
            character: Character to check
            save_type: Save attribute name (e.g., 'save_spell')

        Returns:
            Bonus value from WIS magic attack adjustment
        """
        # Only apply to mental saves
        if save_type not in self.MENTAL_SAVES:
            return 0

        # Get WIS modifiers from ability system
        from ..systems.ability_modifiers import AbilityModifierSystem

        ability_system = AbilityModifierSystem()
        wis_mods = ability_system.get_wisdom_modifiers(character.wisdom)

        return wis_mods.get('magic_attack_adjustment', 0)

    def get_magic_item_bonus(self, character: Character) -> int:
        """
        Calculate magic item bonuses to saving throws

        Rings of Protection, Cloaks of Resistance, etc.

        Args:
            character: Character to check

        Returns:
            Total magic item bonus
        """
        bonus = 0

        # Check if character has equipment
        if not hasattr(character, 'equipment'):
            return 0

        equipment = character.equipment

        # Check armor for magic bonus
        if hasattr(equipment, 'armor') and equipment.armor:
            armor = equipment.armor
            if hasattr(armor, 'magic_bonus') and armor.magic_bonus > 0:
                bonus += armor.magic_bonus

        # Check shield for magic bonus
        if hasattr(equipment, 'shield') and equipment.shield:
            shield = equipment.shield
            if hasattr(shield, 'magic_bonus') and shield.magic_bonus > 0:
                bonus += shield.magic_bonus

        # TODO: Add support for rings, cloaks, other protective items
        # when those systems are implemented

        return bonus

    def calculate_total_modifier(self, character: Character, save_type: str,
                                  base_modifier: int = 0,
                                  situational: Optional[Dict] = None) -> int:
        """
        Calculate total saving throw modifier from all sources

        Args:
            character: Character making the save
            save_type: Save attribute name
            base_modifier: Base modifier provided by caller
            situational: Optional situational modifiers dict

        Returns:
            Total modifier value
        """
        total = base_modifier

        # Racial bonus (Dwarf/Gnome/Halfling)
        total += self.get_racial_save_bonus(character)

        # WIS bonus for mental saves
        total += self.get_wisdom_save_bonus(character, save_type)

        # Magic item bonuses
        total += self.get_magic_item_bonus(character)

        # Situational modifiers
        if situational:
            if situational.get('cover'):
                total += 2  # Cover vs area effects
            if situational.get('surprised'):
                total -= 2  # Surprised penalty
            if situational.get('blind'):
                total -= 4  # Blind penalty

        return total

    def make_save(self, character: Character, category: str,
                  modifier: int = 0, situational: Optional[Dict] = None) -> Dict:
        """
        Make a saving throw with all applicable modifiers

        Args:
            character: Character making the save
            category: Type of save (poison, rod, petrify, breath, spell)
            modifier: Base bonus/penalty to the save (positive = easier)
            situational: Optional dict with situational modifiers
                        {'cover': True, 'surprised': True, 'blind': True}

        Returns:
            Dict with: success, roll, target, narrative, modifiers_applied
        """

        # Normalize category name
        category_lower = category.lower()
        if category_lower not in self.CATEGORIES:
            # Default to spell save if unknown
            save_attr = 'save_spell'
        else:
            save_attr = self.CATEGORIES[category_lower]

        # Get base target number
        base_target = getattr(character, save_attr)

        # Calculate total modifier from all sources
        total_modifier = self.calculate_total_modifier(
            character, save_attr, modifier, situational
        )

        # Apply modifier to target (lower target = easier save)
        adjusted_target = base_target - total_modifier

        # Roll d20
        roll = random.randint(1, 20)

        # Natural 1 always succeeds
        if roll == 1:
            return {
                'success': True,
                'roll': roll,
                'base_target': base_target,
                'adjusted_target': adjusted_target,
                'modifiers_applied': total_modifier,
                'narrative': f"{character.name} rolls a NATURAL 1! Automatic success!",
                'natural_20_or_1': True
            }

        # Natural 20 always fails
        if roll == 20:
            return {
                'success': False,
                'roll': roll,
                'base_target': base_target,
                'adjusted_target': adjusted_target,
                'modifiers_applied': total_modifier,
                'narrative': f"{character.name} rolls a NATURAL 20! Automatic failure!",
                'natural_20_or_1': True
            }

        # Check if save succeeded (roll <= adjusted_target)
        success = roll <= adjusted_target

        # Build narrative
        if success:
            narrative = f"{character.name} rolls {roll} vs {category} save"
        else:
            narrative = f"{character.name} rolls {roll} vs {category} save"

        # Add target information
        if total_modifier != 0:
            narrative += f" (target {base_target}{total_modifier:+d}={adjusted_target})"
        else:
            narrative += f" (target {adjusted_target})"

        narrative += ": SUCCESS!" if success else ": FAILURE!"

        return {
            'success': success,
            'roll': roll,
            'base_target': base_target,
            'adjusted_target': adjusted_target,
            'modifiers_applied': total_modifier,
            'narrative': narrative,
            'natural_20_or_1': False
        }

    def save_or_die(self, character: Character, save_type: str = 'poison') -> Dict:
        """
        Make a saving throw where failure means death

        Args:
            character: Character making the save
            save_type: Type of save

        Returns:
            Dict with save results plus 'died' boolean
        """

        result = self.make_save(character, save_type)

        if not result['success']:
            character.is_alive = False
            character.hp_current = 0
            result['died'] = True
            result['narrative'] += f" {character.name} dies!"
        else:
            result['died'] = False

        return result

    def save_for_half_damage(self, character: Character, damage: int,
                            save_type: str = 'spell') -> Dict:
        """
        Make a save where success reduces damage by half

        Args:
            character: Character making the save
            damage: Full damage amount
            save_type: Type of save

        Returns:
            Dict with save results plus 'final_damage'
        """

        result = self.make_save(character, save_type)

        if result['success']:
            final_damage = damage // 2
            result['narrative'] += f" Damage reduced to {final_damage}!"
        else:
            final_damage = damage
            result['narrative'] += f" Takes full {final_damage} damage!"

        result['final_damage'] = final_damage
        character.take_damage(final_damage)

        return result
