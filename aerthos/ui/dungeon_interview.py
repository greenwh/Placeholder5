"""
Dungeon Interview System

Brief 4-question interview to gather party information for appropriate dungeon scaling.
Keeps questions minimal, accepts defaults, focuses on quick setup.
"""

from typing import Dict, Optional


class DungeonInterview:
    """Simple 4-question interview for dungeon difficulty scaling"""

    def __init__(self):
        """Initialize interview system"""
        pass

    def conduct_interview(self, party=None) -> Dict:
        """
        Ask 4 simple questions to determine dungeon difficulty

        Questions:
        1. Average Party Level (APL) - Most important
        2. Party Size
        3. Party Composition (balanced/combat-heavy/magic-heavy/rogue-heavy)
        4. Magic Item Level (none/low/medium/high)

        Args:
            party: Optional Party object for auto-detection

        Returns:
            Dict with: apl, party_size, composition, magic_level
        """

        print()
        print("═" * 70)
        print("DUNGEON DIFFICULTY SETUP")
        print("═" * 70)
        print()
        print("I'll ask 4 quick questions about your party.")
        print("Press Enter to skip any question for default values.")
        print()

        # Auto-detect from party if provided
        detected = self._detect_from_party(party) if party else {}

        # Question 1: Average Party Level (MOST IMPORTANT)
        apl = self._ask_apl(detected.get('apl', 1))

        # Question 2: Party Size
        party_size = self._ask_party_size(detected.get('party_size', 4))

        # Question 3: Party Composition
        composition = self._ask_composition(detected.get('composition', 'balanced'))

        # Question 4: Magic Item Level
        magic_level = self._ask_magic_level(detected.get('magic_level', 'low'))

        result = {
            'apl': apl,
            'party_size': party_size,
            'composition': composition,
            'magic_level': magic_level
        }

        # Show summary
        self._show_summary(result)

        return result

    def _detect_from_party(self, party) -> Dict:
        """Auto-detect values from Party object"""
        from ..entities.party import Party

        if not isinstance(party, Party):
            return {}

        detected = {}

        # Detect APL
        detected['apl'] = int(party.average_level)

        # Detect party size
        detected['party_size'] = party.size()

        # Detect composition (simple heuristic)
        fighters = sum(1 for m in party.members if m.char_class in ['Fighter', 'Dwarf'])
        casters = sum(1 for m in party.members if m.char_class in ['Magic-User', 'Cleric'])

        if fighters >= casters + 2:
            detected['composition'] = 'combat-heavy'
        elif casters >= fighters + 1:
            detected['composition'] = 'magic-heavy'
        else:
            detected['composition'] = 'balanced'

        # Detect magic level (simple check for +1 items)
        magic_items = 0
        for member in party.members:
            if hasattr(member, 'equipment'):
                if member.equipment.weapon and '+1' in getattr(member.equipment.weapon, 'name', ''):
                    magic_items += 1
                if member.equipment.armor and '+1' in getattr(member.equipment.armor, 'name', ''):
                    magic_items += 1

        if magic_items == 0:
            detected['magic_level'] = 'none'
        elif magic_items <= 2:
            detected['magic_level'] = 'low'
        elif magic_items <= 4:
            detected['magic_level'] = 'medium'
        else:
            detected['magic_level'] = 'high'

        return detected

    def _ask_apl(self, default: int) -> int:
        """Question 1: Average Party Level"""
        print("Question 1 of 4")
        print("─" * 70)
        print("What is your party's AVERAGE LEVEL?")
        print("(This is the most important factor for difficulty)")
        print()

        response = input(f"[Detected: {default}] Press Enter to accept, or type new value: ").strip()

        if not response:
            return default

        try:
            apl = int(response)
            return max(1, min(20, apl))  # Clamp to 1-20
        except ValueError:
            print(f"Invalid input, using default: {default}")
            return default

    def _ask_party_size(self, default: int) -> int:
        """Question 2: Party Size"""
        print()
        print("Question 2 of 4")
        print("─" * 70)
        print("How many characters in the party?")
        print()

        response = input(f"[Detected: {default}] Press Enter to accept, or type new value: ").strip()

        if not response:
            return default

        try:
            size = int(response)
            return max(1, min(6, size))  # Clamp to 1-6
        except ValueError:
            print(f"Invalid input, using default: {default}")
            return default

    def _ask_composition(self, default: str) -> str:
        """Question 3: Party Composition"""
        print()
        print("Question 3 of 4")
        print("─" * 70)
        print("What is your party composition?")
        print()
        print("  1. Balanced (fighters + magic + healing)")
        print("  2. Combat-Heavy (mostly fighters/warriors)")
        print("  3. Magic-Heavy (multiple spellcasters)")
        print("  4. Rogue-Heavy (thieves/rangers)")
        print()

        response = input(f"[Detected: {default}] Press Enter to accept, or choose 1-4: ").strip()

        if not response:
            return default

        composition_map = {
            '1': 'balanced',
            '2': 'combat-heavy',
            '3': 'magic-heavy',
            '4': 'rogue-heavy'
        }

        return composition_map.get(response, default)

    def _ask_magic_level(self, default: str) -> str:
        """Question 4: Magic Item Level"""
        print()
        print("Question 4 of 4")
        print("─" * 70)
        print("What is your magic item level?")
        print()
        print("  1. None/Few - Starting characters, basic equipment")
        print("  2. Low - A few +1 items, some potions")
        print("  3. Medium - Several +1/+2 items, scrolls, rings")
        print("  4. High - Multiple +2/+3 items, powerful artifacts")
        print()

        response = input(f"[Detected: {default}] Press Enter to accept, or choose 1-4: ").strip()

        if not response:
            return default

        magic_map = {
            '1': 'none',
            '2': 'low',
            '3': 'medium',
            '4': 'high'
        }

        return magic_map.get(response, default)

    def _show_summary(self, result: Dict) -> None:
        """Show summary of interview results"""
        print()
        print("═" * 70)
        print("DUNGEON WILL BE GENERATED FOR:")
        print("═" * 70)
        print(f"  Average Party Level: {result['apl']}")
        print(f"  Party Size: {result['party_size']}")
        print(f"  Composition: {result['composition'].replace('-', ' ').title()}")
        print(f"  Magic Items: {result['magic_level'].title()}")
        print("═" * 70)
        print()
