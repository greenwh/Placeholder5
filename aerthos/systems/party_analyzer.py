"""
Party Analyzer System

Analyzes party composition and capabilities to determine appropriate dungeon difficulty.
Used by dungeon interview system to make informed scaling decisions.
"""

from typing import Dict


class PartyAnalyzer:
    """Analyzes party composition for dungeon scaling"""

    def analyze_party(self, party) -> Dict:
        """
        Analyze party capabilities

        Args:
            party: Party object to analyze

        Returns:
            Dict with analysis results:
            {
                'apl': float,              # Average party level
                'party_size': int,
                'fighters': int,           # Count of melee classes
                'healers': int,            # Count of clerics
                'casters': int,            # Count of magic-users
                'thieves': int,            # Count of rogues
                'hp_pool': int,            # Total party HP
                'has_thief_skills': bool,  # Can handle traps
                'has_healing': bool,       # Can sustain longer
                'has_aoe_magic': bool,     # Can handle swarms
                'magic_level': str,        # 'none', 'low', 'medium', 'high'
                'effective_level': float,  # APL + magic boost
                'composition': str         # 'balanced', 'combat-heavy', etc.
            }
        """
        from ..entities.party import Party

        if not isinstance(party, Party):
            return self._default_analysis()

        # Basic stats
        apl = party.average_level
        party_size = party.size()

        # Count classes
        fighters = 0
        healers = 0
        casters = 0
        thieves = 0
        hp_pool = 0

        for member in party.members:
            hp_pool += member.hp_max

            char_class = member.char_class
            if char_class in ['Fighter', 'Dwarf', 'Paladin', 'Ranger']:
                fighters += 1
            if char_class in ['Cleric']:
                healers += 1
            if char_class in ['Magic-User', 'Elf']:
                casters += 1
            if char_class in ['Thief', 'Halfling']:
                thieves += 1

        # Assess capabilities
        has_thief_skills = thieves > 0
        has_healing = healers > 0
        has_aoe_magic = casters > 0  # Assume casters have AoE spells

        # Assess magic item level
        magic_level = self._assess_magic_items(party)

        # Calculate effective level (APL + magic boost)
        magic_boost = self._get_magic_boost(magic_level)
        effective_level = apl + magic_boost

        # Determine composition type
        composition = self._determine_composition(fighters, casters, healers, thieves, party_size)

        return {
            'apl': apl,
            'party_size': party_size,
            'fighters': fighters,
            'healers': healers,
            'casters': casters,
            'thieves': thieves,
            'hp_pool': hp_pool,
            'has_thief_skills': has_thief_skills,
            'has_healing': has_healing,
            'has_aoe_magic': has_aoe_magic,
            'magic_level': magic_level,
            'effective_level': effective_level,
            'composition': composition
        }

    def _assess_magic_items(self, party) -> str:
        """
        Assess party's magical item level

        Logic:
        - Count +1 or better weapons/armor
        - Check for magical accessories (rings, scrolls, etc.)
        - Return 'none', 'low', 'medium', or 'high'
        """
        magic_count = 0

        for member in party.members:
            if hasattr(member, 'equipment'):
                # Check weapon
                if member.equipment.weapon:
                    weapon_name = getattr(member.equipment.weapon, 'name', '')
                    if '+1' in weapon_name or '+2' in weapon_name or '+3' in weapon_name:
                        magic_count += 1

                # Check armor
                if member.equipment.armor:
                    armor_name = getattr(member.equipment.armor, 'name', '')
                    if '+1' in armor_name or '+2' in armor_name or '+3' in armor_name:
                        magic_count += 1

                # Check shield
                if member.equipment.shield:
                    shield_name = getattr(member.equipment.shield, 'name', '')
                    if '+1' in shield_name or '+2' in shield_name:
                        magic_count += 1

            # Check inventory for scrolls, potions, rings
            if hasattr(member, 'inventory'):
                for item in member.inventory.items:
                    item_name = getattr(item, 'name', '').lower()
                    if any(keyword in item_name for keyword in ['scroll', 'potion', 'ring', 'wand', 'staff']):
                        magic_count += 0.5  # Count consumables/misc as half

        # Classify magic level
        if magic_count == 0:
            return 'none'
        elif magic_count <= 2:
            return 'low'
        elif magic_count <= 5:
            return 'medium'
        else:
            return 'high'

    def _get_magic_boost(self, magic_level: str) -> float:
        """Get effective level boost from magic items"""
        from ..constants import (
            MAGIC_BOOST_LOW,
            MAGIC_BOOST_MEDIUM,
            MAGIC_BOOST_HIGH
        )

        magic_boost_map = {
            'none': 0.0,
            'low': MAGIC_BOOST_LOW,
            'medium': MAGIC_BOOST_MEDIUM,
            'high': MAGIC_BOOST_HIGH
        }

        return magic_boost_map.get(magic_level, 0.0)

    def _determine_composition(self, fighters: int, casters: int, healers: int, thieves: int, party_size: int) -> str:
        """
        Determine party composition type

        Returns: 'balanced', 'combat-heavy', 'magic-heavy', or 'rogue-heavy'
        """
        if party_size == 0:
            return 'balanced'

        # Calculate percentages
        fighter_pct = fighters / party_size
        caster_pct = (casters + healers) / party_size
        thief_pct = thieves / party_size

        # Determine dominant type
        if fighter_pct >= 0.6:
            return 'combat-heavy'
        elif caster_pct >= 0.5:
            return 'magic-heavy'
        elif thief_pct >= 0.5:
            return 'rogue-heavy'
        else:
            return 'balanced'

    def _default_analysis(self) -> Dict:
        """Return default analysis for solo/unknown party"""
        return {
            'apl': 1,
            'party_size': 1,
            'fighters': 1,
            'healers': 0,
            'casters': 0,
            'thieves': 0,
            'hp_pool': 8,
            'has_thief_skills': False,
            'has_healing': False,
            'has_aoe_magic': False,
            'magic_level': 'none',
            'effective_level': 1.0,
            'composition': 'balanced'
        }

    def check_party_readiness(self, analysis: Dict, config) -> list:
        """
        Check if party is ready for dungeon difficulty

        Args:
            analysis: Party analysis dict
            config: DungeonConfig object

        Returns:
            List of warning messages (empty if ready)
        """
        warnings = []

        # Check for magic weapons if needed
        if hasattr(config, 'requires_magic_weapons') and config.requires_magic_weapons():
            if analysis['magic_level'] == 'none':
                warnings.append(
                    "⚠️  WARNING: This dungeon contains creatures requiring "
                    "+1 or better weapons to hit! Your party lacks magic weapons."
                )

        # Check for healing
        if analysis['apl'] >= 3 and not analysis['has_healing']:
            warnings.append(
                "⚠️  WARNING: No healer in party. Consider bringing healing potions!"
            )

        # Check for trap removal
        trap_frequency = getattr(config, 'trap_frequency', 0)
        if trap_frequency > 0.2 and not analysis['has_thief_skills']:
            warnings.append(
                "⚠️  WARNING: High trap density but no thief! "
                "Expect to take damage from traps."
            )

        # Check party size vs difficulty
        if analysis['party_size'] == 1 and analysis['apl'] < 3:
            warnings.append(
                "⚠️  WARNING: Solo adventuring at low level is very dangerous!"
            )

        return warnings
