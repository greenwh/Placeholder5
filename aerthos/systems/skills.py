"""
Thief Skills and Ability Check system
"""

import random
from typing import Dict
from ..entities.character import Character
from ..entities.player import PlayerCharacter


class SkillResolver:
    """Handles thief skill checks and ability checks"""

    # Standard thief skills
    THIEF_SKILLS = [
        'pick_pockets',
        'open_locks',
        'find_traps',
        'move_silently',
        'hide_in_shadows',
        'hear_noise',
        'climb_walls',
        'read_languages'
    ]

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

        if not character.can_use_thief_skill(skill_name):
            return {
                'success': False,
                'roll': 0,
                'target': 0,
                'narrative': f"{character.name} doesn't have the {skill_name} skill!",
                'critical_fail': False
            }

        # Get skill percentage
        base_chance = character.get_thief_skill_value(skill_name)
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
