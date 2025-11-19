"""
Ability Score Modifier System - Complete AD&D 1e ability score tables

Implements all six ability score modifier tables from the Players Handbook:
- Strength (with exceptional strength for Fighters)
- Intelligence (spell learning, languages, max spell level)
- Wisdom (magic defense, bonus spells, spell failure)
- Dexterity (to-hit, AC, thief skills)
- Constitution (HP, system shock, resurrection)
- Charisma (henchmen, loyalty, reactions)
"""

import json
import random
from pathlib import Path
from typing import Dict, Optional, Tuple


class AbilityModifierSystem:
    """System for looking up ability score modifiers"""

    def __init__(self):
        """Load ability score tables from JSON"""
        data_path = Path(__file__).parent.parent / 'data' / 'ability_score_tables.json'
        with open(data_path, 'r') as f:
            self.tables = json.load(f)

    def get_strength_modifiers(self, strength: int, exceptional: int = 0) -> Dict:
        """
        Get strength modifiers

        Args:
            strength: Strength score (3-18+)
            exceptional: Exceptional strength percentile (1-100, 0 for non-exceptional)

        Returns:
            Dict with: hit_prob, damage, weight_allowance, open_doors, bend_bars_lift_gates
        """
        # Handle exceptional strength for Fighters
        if strength == 18 and exceptional > 0:
            # Map exceptional percentile to table ranges
            if exceptional <= 50:
                key = "18/50"
            elif exceptional <= 75:
                key = "18/75"
            elif exceptional <= 90:
                key = "18/90"
            elif exceptional <= 99:
                key = "18/99"
            else:  # 100
                key = "18/00"
        else:
            key = str(strength)

        if key in self.tables['strength']:
            return self.tables['strength'][key].copy()

        # Cap at maximum
        if strength > 18:
            return self.tables['strength']['18'].copy()

        # Floor at minimum
        return self.tables['strength']['3'].copy()

    def get_intelligence_modifiers(self, intelligence: int) -> Dict:
        """
        Get intelligence modifiers

        Args:
            intelligence: Intelligence score (3-25)

        Returns:
            Dict with: additional_languages, spell_learn_chance, min_spells_per_level,
                      max_spells_per_level, max_spell_level
        """
        key = str(min(25, max(3, intelligence)))

        if key in self.tables['intelligence']:
            return self.tables['intelligence'][key].copy()

        # Default for very high INT
        return self.tables['intelligence']['25'].copy()

    def get_wisdom_modifiers(self, wisdom: int) -> Dict:
        """
        Get wisdom modifiers

        Args:
            wisdom: Wisdom score (3-25)

        Returns:
            Dict with: magic_attack_adjustment, spell_bonus (dict), spell_failure
        """
        key = str(min(25, max(3, wisdom)))

        if key in self.tables['wisdom']:
            return self.tables['wisdom'][key].copy()

        # Default for very high WIS
        return self.tables['wisdom']['25'].copy()

    def get_dexterity_modifiers(self, dexterity: int) -> Dict:
        """
        Get dexterity modifiers

        Args:
            dexterity: Dexterity score (3-25)

        Returns:
            Dict with: reaction_attack_adj, defensive_adj, and all thief skill modifiers
        """
        key = str(min(25, max(3, dexterity)))

        if key in self.tables['dexterity']:
            return self.tables['dexterity'][key].copy()

        # Default for very high DEX
        return self.tables['dexterity']['25'].copy()

    def get_constitution_modifiers(self, constitution: int, is_fighter: bool = False) -> Dict:
        """
        Get constitution modifiers

        Args:
            constitution: Constitution score (3-25)
            is_fighter: Whether character is Fighter (gets higher HP bonus)

        Returns:
            Dict with: hp_adjustment, system_shock, resurrection_survival, regeneration (if CON 20+)
        """
        key = str(min(25, max(3, constitution)))

        if key in self.tables['constitution']:
            mods = self.tables['constitution'][key].copy()

            # Fighters get higher HP bonus
            if is_fighter and 'hp_adjustment_fighter' in mods:
                mods['hp_adjustment'] = mods['hp_adjustment_fighter']

            return mods

        # Default for very high CON
        mods = self.tables['constitution']['25'].copy()
        if is_fighter:
            mods['hp_adjustment'] = mods['hp_adjustment_fighter']
        return mods

    def get_charisma_modifiers(self, charisma: int) -> Dict:
        """
        Get charisma modifiers

        Args:
            charisma: Charisma score (3-25)

        Returns:
            Dict with: max_henchmen, loyalty_base, reaction_adjustment
        """
        key = str(min(25, max(3, charisma)))

        if key in self.tables['charisma']:
            return self.tables['charisma'][key].copy()

        # Default for very high CHA
        return self.tables['charisma']['25'].copy()

    def attempt_spell_learning(self, intelligence: int, spell_name: str = None) -> Tuple[bool, int]:
        """
        Attempt to learn a spell (for Magic-Users)

        Args:
            intelligence: Character's intelligence score
            spell_name: Optional spell name (for logging)

        Returns:
            Tuple of (success: bool, chance: int)
        """
        mods = self.get_intelligence_modifiers(intelligence)
        chance = mods.get('spell_learn_chance', 0)

        if chance == 0:
            return False, 0

        roll = random.randint(1, 100)
        success = roll <= chance

        return success, chance

    def check_system_shock(self, constitution: int) -> Tuple[bool, int]:
        """
        Check system shock survival (aging, polymorph, petrification)

        Args:
            constitution: Character's constitution score

        Returns:
            Tuple of (survived: bool, chance: int)
        """
        mods = self.get_constitution_modifiers(constitution)
        chance = mods.get('system_shock', 0)

        roll = random.randint(1, 100)
        survived = roll <= chance

        return survived, chance

    def check_resurrection_survival(self, constitution: int) -> Tuple[bool, int]:
        """
        Check resurrection survival

        Args:
            constitution: Character's constitution score

        Returns:
            Tuple of (survived: bool, chance: int)
        """
        mods = self.get_constitution_modifiers(constitution)
        chance = mods.get('resurrection_survival', 0)

        roll = random.randint(1, 100)
        survived = roll <= chance

        return survived, chance

    def attempt_bend_bars(self, strength: int, exceptional: int = 0) -> Tuple[bool, int]:
        """
        Attempt to bend bars or lift gates

        Args:
            strength: Strength score
            exceptional: Exceptional strength percentile

        Returns:
            Tuple of (success: bool, chance: int)
        """
        mods = self.get_strength_modifiers(strength, exceptional)
        chance = mods.get('bend_bars_lift_gates', 0)

        roll = random.randint(1, 100)
        success = roll <= chance

        return success, chance

    def attempt_open_doors(self, strength: int, exceptional: int = 0,
                          locked: bool = False, is_fighter: bool = False) -> bool:
        """
        Attempt to force open a door

        Args:
            strength: Strength score
            exceptional: Exceptional strength percentile
            locked: Whether door is locked/barred/magically held
            is_fighter: Whether character is a Fighter

        Returns:
            bool: Success
        """
        mods = self.get_strength_modifiers(strength, exceptional)
        door_chances = mods.get('open_doors', '1-2')

        # Parse door chances (e.g., "1-3" or "2(1)" for exceptional)
        if '(' in door_chances:
            # Exceptional strength format: "2(1)" means 2/6 normal, 1/6 locked
            parts = door_chances.split('(')
            normal_chance = int(parts[0])
            locked_chance = int(parts[1].rstrip(')'))

            if locked and is_fighter:
                max_roll = locked_chance
            else:
                max_roll = normal_chance
        else:
            # Normal format: "1-3" means 1-3 on d6
            range_parts = door_chances.split('-')
            max_roll = int(range_parts[1])

            # Locked doors can't be forced without exceptional strength
            if locked:
                return False

        roll = random.randint(1, 6)
        return roll <= max_roll

    def get_all_modifiers(self, character) -> Dict:
        """
        Get all ability modifiers for a character

        Args:
            character: Character object with ability scores

        Returns:
            Dict with all modifiers organized by ability
        """
        is_fighter = character.char_class in ['Fighter', 'Paladin', 'Ranger']
        exceptional_str = getattr(character, 'exceptional_strength', 0)

        return {
            'strength': self.get_strength_modifiers(character.str, exceptional_str),
            'intelligence': self.get_intelligence_modifiers(character.int),
            'wisdom': self.get_wisdom_modifiers(character.wis),
            'dexterity': self.get_dexterity_modifiers(character.dex),
            'constitution': self.get_constitution_modifiers(character.con, is_fighter),
            'charisma': self.get_charisma_modifiers(character.cha)
        }

    def apply_modifiers_to_character(self, character) -> None:
        """
        Apply all relevant ability modifiers to a character

        This updates the character object with modifiers from their ability scores.
        Called during character creation and when ability scores change.

        Args:
            character: Character object to update
        """
        # Get all modifiers
        mods = self.get_all_modifiers(character)

        # Apply STR modifiers (already handled by existing methods)
        # get_to_hit_bonus() and get_damage_bonus() use these

        # Apply DEX to AC (defensive adjustment)
        dex_def = mods['dexterity']['defensive_adj']
        # AC improvement is negative in AD&D 1e
        # Already handled in Character.ac calculation

        # Apply CON to max HP (hp_adjustment)
        # This should be applied during HP calculation
        # Store for reference
        if not hasattr(character, '_con_hp_bonus'):
            character._con_hp_bonus = mods['constitution']['hp_adjustment']

        # Store other modifiers for reference
        character._ability_modifiers = mods

    def get_bonus_spells(self, wisdom: int, spell_level: int) -> int:
        """
        Get number of bonus spells for clerics based on wisdom

        Args:
            wisdom: Wisdom score
            spell_level: Spell level (1-7)

        Returns:
            Number of bonus spells for that level
        """
        mods = self.get_wisdom_modifiers(wisdom)
        spell_bonus = mods.get('spell_bonus', {})

        return spell_bonus.get(str(spell_level), 0)

    def check_spell_failure(self, wisdom: int) -> Tuple[bool, int]:
        """
        Check if cleric spell fails due to low wisdom

        Args:
            wisdom: Wisdom score

        Returns:
            Tuple of (failed: bool, failure_chance: int)
        """
        mods = self.get_wisdom_modifiers(wisdom)
        failure_chance = mods.get('spell_failure', 0)

        if failure_chance == 0:
            return False, 0

        roll = random.randint(1, 100)
        failed = roll <= failure_chance

        return failed, failure_chance

    def can_learn_spell_level(self, intelligence: int, spell_level: int) -> bool:
        """
        Check if character can learn spells of given level

        Args:
            intelligence: Intelligence score
            spell_level: Spell level (1-9)

        Returns:
            bool: Can learn this level
        """
        mods = self.get_intelligence_modifiers(intelligence)
        max_level = mods.get('max_spell_level', 0)

        return spell_level <= max_level
