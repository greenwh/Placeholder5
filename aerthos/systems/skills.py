"""
Thief Skills and Ability Check system
"""

import random
import json
import os
from typing import Dict, Optional
from ..entities.character import Character
from ..entities.player import PlayerCharacter


class SkillResolver:
    """Handles thief skill checks and ability checks"""

    # Standard thief skills
    THIEF_SKILLS = [
        'pick_pockets',
        'open_locks',
        'find_remove_traps',  # Note: canonical name is find_remove_traps, not find_traps
        'move_silently',
        'hide_in_shadows',
        'hear_noise',
        'climb_walls',
        'read_languages'
    ]

    def __init__(self):
        """Load thief skills tables from JSON"""
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        tables_path = os.path.join(data_dir, 'thief_skills_tables.json')

        with open(tables_path, 'r') as f:
            self.tables = json.load(f)

        self.base_skills_by_level = self.tables['base_skills_by_level']
        self.racial_adjustments = self.tables['racial_adjustments']
        self.dexterity_adjustments = self.tables['dexterity_adjustments']
        self.armor_penalties = self.tables['armor_penalties']

    def calculate_thief_skill(self, character: PlayerCharacter, skill_name: str) -> int:
        """
        Calculate final thief skill value with all modifiers

        Args:
            character: The thief character
            skill_name: Name of the skill

        Returns:
            Final skill percentage (1-99)
        """
        # Normalize skill name (allow both find_traps and find_remove_traps)
        if skill_name == 'find_traps':
            skill_name = 'find_remove_traps'

        # 1. Get base value from level
        level = min(character.level, 23)  # Max level in tables
        base_value = self.base_skills_by_level[str(level)].get(skill_name, 0)

        # 2. Add racial adjustment
        racial_mod = self.racial_adjustments.get(character.race, {}).get(skill_name, 0)

        # 3. Add DEX adjustment
        dex_mod = 0
        dex_str = str(character.dexterity)
        if dex_str in self.dexterity_adjustments:
            dex_table = self.dexterity_adjustments[dex_str]
            dex_mod = dex_table.get(skill_name, dex_table.get('all_skills', 0))

        # 4. Subtract armor penalty
        armor_penalty = 0
        if hasattr(character, 'equipment') and character.equipment.armor:
            armor_name = character.equipment.armor.name
            armor_penalty = self.armor_penalties.get(armor_name, 0)
            if armor_penalty >= 100:
                # Cannot use thief skills in heavy armor
                return 0

        # Calculate final value
        final_value = base_value + racial_mod + dex_mod - armor_penalty

        # Minimum is 0% if base was 0, otherwise 1% (can't have negative skills)
        # Maximum is always 99%
        if base_value == 0 and final_value <= 0:
            return 0
        return max(1, min(99, final_value))

    def thief_skill_check(self, character: PlayerCharacter,
                         skill_name: str, modifier: int = 0) -> Dict:
        """
        Make a thief skill check (percentile roll)

        Args:
            character: Character attempting the skill
            skill_name: Name of the skill
            modifier: Bonus/penalty to the roll (positive = easier)

        Returns:
            Dict with: success, roll, target, narrative, critical_fail
        """

        # Normalize skill name
        if skill_name == 'find_traps':
            skill_name = 'find_remove_traps'

        if not character.can_use_thief_skill(skill_name):
            return {
                'success': False,
                'roll': 0,
                'target': 0,
                'narrative': f"{character.name} doesn't have the {skill_name} skill!",
                'critical_fail': False
            }

        # Get skill percentage with all modifiers (racial, DEX, armor)
        base_chance = self.calculate_thief_skill(character, skill_name)
        target = min(95, base_chance + modifier)  # Max 95%

        # Roll d100
        roll = random.randint(1, 100)

        # Critical failure on 96-100
        if roll >= 96:
            return {
                'success': False,
                'roll': roll,
                'target': target,
                'narrative': f"{character.name} critically fails {skill_name}! ({roll}%)",
                'critical_fail': True
            }

        success = roll <= target

        if success:
            narrative = f"{character.name} succeeds at {skill_name}! (rolled {roll}%, needed {target}%)"
        else:
            narrative = f"{character.name} fails at {skill_name}. (rolled {roll}%, needed {target}%)"

        return {
            'success': success,
            'roll': roll,
            'target': target,
            'narrative': narrative,
            'critical_fail': False
        }

    def ability_check(self, character: Character, ability: str,
                     difficulty: int = 0) -> Dict:
        """
        Make an ability check (roll under ability score on d20)

        Args:
            character: Character making the check
            ability: Ability name (str, dex, con, int, wis, cha)
            difficulty: Modifier to the roll (positive = harder)

        Returns:
            Dict with: success, roll, target, narrative
        """

        ability_map = {
            'str': character.strength,
            'strength': character.strength,
            'dex': character.dexterity,
            'dexterity': character.dexterity,
            'con': character.constitution,
            'constitution': character.constitution,
            'int': character.intelligence,
            'intelligence': character.intelligence,
            'wis': character.wisdom,
            'wisdom': character.wisdom,
            'cha': character.charisma,
            'charisma': character.charisma
        }

        ability_lower = ability.lower()
        if ability_lower not in ability_map:
            return {
                'success': False,
                'roll': 0,
                'target': 0,
                'narrative': f"Unknown ability: {ability}"
            }

        target = ability_map[ability_lower]
        roll = random.randint(1, 20)
        adjusted_roll = roll + difficulty

        # Natural 1 always succeeds
        if roll == 1:
            return {
                'success': True,
                'roll': roll,
                'target': target,
                'narrative': f"{character.name} rolls natural 1 on {ability} check! Auto-success!"
            }

        # Natural 20 always fails
        if roll == 20:
            return {
                'success': False,
                'roll': roll,
                'target': target,
                'narrative': f"{character.name} rolls natural 20 on {ability} check! Auto-fail!"
            }

        success = adjusted_roll <= target

        if success:
            narrative = f"{character.name} succeeds at {ability} check! (rolled {roll}, target {target})"
        else:
            narrative = f"{character.name} fails {ability} check. (rolled {roll}, target {target})"

        if difficulty != 0:
            narrative += f" (difficulty: {difficulty:+d})"

        return {
            'success': success,
            'roll': roll,
            'target': target,
            'narrative': narrative
        }

    def hear_noise_check(self, character: PlayerCharacter) -> Dict:
        """
        Special hear noise check (uses d6 in AD&D 1e)

        Non-thieves: 1 in 6
        Thieves: use hear_noise skill

        Returns:
            Dict with: success, narrative
        """

        if character.char_class == 'Thief' and 'hear_noise' in character.thief_skills:
            # Use thief skill
            return self.thief_skill_check(character, 'hear_noise')
        else:
            # Standard 1 in 6 chance
            roll = random.randint(1, 6)
            success = (roll == 1)

            if success:
                narrative = f"{character.name} hears something! (rolled {roll})"
            else:
                narrative = f"{character.name} hears nothing unusual. (rolled {roll})"

            return {
                'success': success,
                'roll': roll,
                'target': 1,
                'narrative': narrative
            }
