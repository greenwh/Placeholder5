"""
Ability Score System - AD&D 1e
Provides comprehensive ability score modifiers and lookups
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class AbilityScoreSystem:
    """Manages all ability score modifiers and effects"""

    def __init__(self):
        """Load ability modifier data from JSON"""
        data_path = Path(__file__).parent.parent / 'data' / 'ability_modifiers.json'
        with open(data_path, 'r') as f:
            self.modifiers = json.load(f)

    def _find_range(self, ability: str, score: int, percentile: int = 0) -> Optional[str]:
        """Find the appropriate range key for a given score"""
        # Handle exceptional strength
        if ability == 'strength' and score == 18 and percentile > 0:
            if percentile <= 50:
                return "18/01-50"
            elif percentile <= 75:
                return "18/51-75"
            elif percentile <= 90:
                return "18/76-90"
            elif percentile <= 99:
                return "18/91-99"
            else:
                return "18/00"

        # Try exact match first
        if str(score) in self.modifiers[ability]:
            return str(score)

        # Try range match
        for key in self.modifiers[ability].keys():
            if '-' in key:
                parts = key.split('-')
                try:
                    low, high = int(parts[0]), int(parts[1])
                    if low <= score <= high:
                        return key
                except ValueError:
                    continue

        return None

    def get_strength_mods(self, score: int, percentile: int = 0) -> Dict[str, Any]:
        """Get all strength modifiers"""
        key = self._find_range('strength', score, percentile)
        if key:
            return self.modifiers['strength'][key]
        return {"hit_prob": 0, "damage": 0, "weight_allowance": 0, "open_doors": "1-2", "bend_bars": 13}

    def get_intelligence_mods(self, score: int) -> Dict[str, Any]:
        """Get all intelligence modifiers"""
        key = self._find_range('intelligence', score)
        if key:
            return self.modifiers['intelligence'][key]
        return {"languages": 1, "spell_chance": 45, "min_spells": 5, "max_spells": 7}

    def get_wisdom_mods(self, score: int) -> Dict[str, Any]:
        """Get all wisdom modifiers"""
        key = self._find_range('wisdom', score)
        if key:
            return self.modifiers['wisdom'][key]
        return {"magic_defense": 0, "bonus_spells": {}, "spell_failure": 0}

    def get_dexterity_mods(self, score: int) -> Dict[str, Any]:
        """Get all dexterity modifiers"""
        key = self._find_range('dexterity', score)
        if key:
            return self.modifiers['dexterity'][key]
        return {"reaction": 0, "ac_bonus": 0, "pick_pockets": 0, "open_locks": 0,
                "find_traps": 0, "move_silently": 0, "hide_shadows": 0, "hear_noise": 0,
                "climb_walls": 0, "read_languages": 0}

    def get_constitution_mods(self, score: int) -> Dict[str, Any]:
        """Get all constitution modifiers"""
        key = self._find_range('constitution', score)
        if key:
            return self.modifiers['constitution'][key]
        return {"hp_adj": 0, "system_shock": 65, "resurrection": 70}

    def get_charisma_mods(self, score: int) -> Dict[str, Any]:
        """Get all charisma modifiers"""
        key = self._find_range('charisma', score)
        if key:
            return self.modifiers['charisma'][key]
        return {"max_henchmen": 4, "loyalty": 0, "reaction": 0}

    def get_xp_bonus(self, char_class: str, **ability_scores) -> int:
        """
        Calculate XP bonus based on prime requisite
        Returns percentage bonus (e.g., 10 for +10%)
        """
        prime_requisites = {
            'Fighter': 'strength',
            'Ranger': 'strength',
            'Paladin': 'strength',
            'Cleric': 'wisdom',
            'Druid': 'wisdom',
            'Magic-User': 'intelligence',
            'Illusionist': 'intelligence',
            'Thief': 'dexterity',
            'Assassin': 'dexterity',
            'Monk': 'strength',
            'Bard': 'charisma'
        }

        prime = prime_requisites.get(char_class)
        if not prime:
            return 0

        score = ability_scores.get(prime, 10)
        percentile = ability_scores.get('strength_percentile', 0) if prime == 'strength' else 0

        # Get mods for the prime requisite
        if prime == 'strength':
            mods = self.get_strength_mods(score, percentile)
        elif prime == 'intelligence':
            mods = self.get_intelligence_mods(score)
        elif prime == 'wisdom':
            mods = self.get_wisdom_mods(score)
        elif prime == 'dexterity':
            mods = self.get_dexterity_mods(score)
        elif prime == 'charisma':
            mods = self.get_charisma_mods(score)
        else:
            return 0

        return mods.get('xp_bonus', 0)

    def get_weight_allowance(self, strength: int, percentile: int = 0) -> int:
        """Get weight allowance in gold pieces"""
        base = 400  # Base for STR 9-12
        mods = self.get_strength_mods(strength, percentile)
        return base + mods.get('weight_allowance', 0)

    def can_open_doors(self, strength: int, percentile: int = 0) -> str:
        """Get door opening chance (e.g., '1-2' means 1-2 on d6)"""
        mods = self.get_strength_mods(strength, percentile)
        return mods.get('open_doors', '1-2')

    def get_bend_bars_chance(self, strength: int, percentile: int = 0) -> int:
        """Get bend bars/lift gates percentage chance"""
        mods = self.get_strength_mods(strength, percentile)
        return mods.get('bend_bars', 13)

    def get_languages_known(self, intelligence: int) -> int:
        """Get number of additional languages that can be learned"""
        mods = self.get_intelligence_mods(intelligence)
        return mods.get('languages', 1)

    def get_spell_learning_chance(self, intelligence: int) -> int:
        """Get % chance to learn a spell (for MU/Illusionist)"""
        mods = self.get_intelligence_mods(intelligence)
        return mods.get('spell_chance', 45)

    def get_spell_limits(self, intelligence: int) -> tuple:
        """Get (min, max) spells per level for MU/Illusionist"""
        mods = self.get_intelligence_mods(intelligence)
        return (mods.get('min_spells', 5), mods.get('max_spells', 7))

    def get_bonus_spells(self, wisdom: int) -> Dict[int, int]:
        """Get bonus spell slots by level for clerics (wisdom-based)"""
        mods = self.get_wisdom_mods(wisdom)
        return mods.get('bonus_spells', {})

    def get_spell_failure_chance(self, wisdom: int) -> int:
        """Get spell failure % for low wisdom clerics"""
        mods = self.get_wisdom_mods(wisdom)
        return mods.get('spell_failure', 0)

    def get_magic_defense_adjustment(self, wisdom: int) -> int:
        """Get save bonus vs mental attacks"""
        mods = self.get_wisdom_mods(wisdom)
        return mods.get('magic_defense', 0)

    def get_system_shock_chance(self, constitution: int) -> int:
        """Get % chance to survive system shock (polymorph, petrification, etc.)"""
        mods = self.get_constitution_mods(constitution)
        return mods.get('system_shock', 65)

    def get_resurrection_chance(self, constitution: int) -> int:
        """Get % chance to survive resurrection"""
        mods = self.get_constitution_mods(constitution)
        return mods.get('resurrection', 70)

    def get_hp_adjustment(self, constitution: int, is_fighter_class: bool = False) -> int:
        """Get HP bonus per level from constitution"""
        mods = self.get_constitution_mods(constitution)
        if is_fighter_class and 'hp_adj_fighter' in mods:
            return mods['hp_adj_fighter']
        return mods.get('hp_adj', 0)

    def get_max_henchmen(self, charisma: int) -> int:
        """Get maximum number of henchmen"""
        mods = self.get_charisma_mods(charisma)
        return mods.get('max_henchmen', 4)

    def get_loyalty_base(self, charisma: int) -> int:
        """Get loyalty modifier percentage"""
        mods = self.get_charisma_mods(charisma)
        return mods.get('loyalty', 0)

    def get_reaction_adjustment(self, charisma: int) -> int:
        """Get reaction modifier percentage"""
        mods = self.get_charisma_mods(charisma)
        return mods.get('reaction', 0)

    def get_thief_skill_adjustments(self, dexterity: int) -> Dict[str, int]:
        """Get dexterity modifiers for all thief skills"""
        mods = self.get_dexterity_mods(dexterity)
        return {
            'pick_pockets': mods.get('pick_pockets', 0),
            'open_locks': mods.get('open_locks', 0),
            'find_traps': mods.get('find_traps', 0),
            'move_silently': mods.get('move_silently', 0),
            'hide_in_shadows': mods.get('hide_shadows', 0),
            'hear_noise': mods.get('hear_noise', 0),
            'climb_walls': mods.get('climb_walls', 0),
            'read_languages': mods.get('read_languages', 0)
        }


# Global instance
ability_system = AbilityScoreSystem()
