"""
Party management system for multiple player characters
"""

from typing import List, Optional
from dataclasses import dataclass, field
from .player import PlayerCharacter


@dataclass
class Party:
    """
    Manages a party of 4-6 player characters

    Handles party roster, combat order, and group actions.
    """

    members: List[PlayerCharacter] = field(default_factory=list)
    max_size: int = 6
    formation: List[str] = field(default_factory=list)  # 'front', 'back'

    def __post_init__(self):
        """Initialize formation based on initial members"""
        if self.members and not self.formation:
            # Default: fighters/clerics in front, others in back
            for member in self.members:
                if member.char_class in ['Fighter', 'Cleric']:
                    self.formation.append('front')
                else:
                    self.formation.append('back')

    def add_member(self, character: PlayerCharacter) -> bool:
        """
        Add a character to the party

        Returns:
            True if successful, False if party is full
        """
        if len(self.members) >= self.max_size:
            return False

        self.members.append(character)

        # Set default formation position
        if character.char_class in ['Fighter', 'Cleric']:
            self.formation.append('front')
        else:
            self.formation.append('back')

        return True

    def remove_member(self, character: PlayerCharacter) -> bool:
        """Remove a character from the party"""
        if character in self.members:
            index = self.members.index(character)
            self.members.remove(character)
            self.formation.pop(index)
            return True
        return False

    def get_member(self, index: int) -> Optional[PlayerCharacter]:
        """Get party member by index (0-based)"""
        if 0 <= index < len(self.members):
            return self.members[index]
        return None

    def get_member_by_name(self, name: str) -> Optional[PlayerCharacter]:
        """Get party member by name (case-insensitive partial match)"""
        search = name.lower()

        # Try exact match
        for member in self.members:
            if member.name.lower() == search:
                return member

        # Try partial match
        for member in self.members:
            if search in member.name.lower():
                return member

        return None

    def get_living_members(self) -> List[PlayerCharacter]:
        """Get all living party members"""
        return [m for m in self.members if m.is_alive]

    def get_dead_members(self) -> List[PlayerCharacter]:
        """Get all dead party members"""
        return [m for m in self.members if not m.is_alive]

    def get_front_line(self) -> List[PlayerCharacter]:
        """Get front-line party members (safe with list sync)"""
        return [member for member, pos in zip(self.members, self.formation) if pos == 'front']

    def get_back_line(self) -> List[PlayerCharacter]:
        """Get back-line party members (safe with list sync)"""
        return [member for member, pos in zip(self.members, self.formation) if pos == 'back']

    def is_front_line_standing(self) -> bool:
        """Check if any front-line members are alive"""
        front_line = self.get_front_line()
        return any(member.is_alive for member in front_line)

    def is_alive(self) -> bool:
        """Check if any party members are alive"""
        return any(m.is_alive for m in self.members)

    def is_full(self) -> bool:
        """Check if party is at maximum size"""
        return len(self.members) >= self.max_size

    def size(self) -> int:
        """Get current party size"""
        return len(self.members)

    @property
    def average_level(self) -> float:
        """Get average party level"""
        if not self.members:
            return 0
        return sum(m.level for m in self.members) / len(self.members)

    def distribute_xp(self, xp_amount: int) -> None:
        """
        Distribute XP equally among living party members

        Args:
            xp_amount: Total XP to distribute
        """
        living = self.get_living_members()
        if not living:
            # No living members to award XP
            return

        xp_per_member = xp_amount // len(living)

        for member in living:
            member.gain_xp(xp_per_member)

    def can_rest(self) -> bool:
        """Check if party can rest (at least one member alive)"""
        return self.is_alive()

    def rest(self, safe_area: bool = True) -> str:
        """
        Party rests to recover HP and spells

        Args:
            safe_area: Whether the rest area is safe

        Returns:
            Message about rest results
        """
        if not self.is_alive():
            return "The party is dead and cannot rest."

        messages = []

        for member in self.get_living_members():
            # HP recovery
            old_hp = member.hp_current
            member.rest()
            hp_recovered = member.hp_current - old_hp

            if hp_recovered > 0:
                messages.append(f"{member.name} recovers {hp_recovered} HP")

            # Spell recovery
            if member.spells_memorized:
                spells_restored = 0
                for slot in member.spells_memorized:
                    if slot.is_used:
                        slot.is_used = False
                        spells_restored += 1

                if spells_restored > 0:
                    messages.append(f"{member.name} restores {spells_restored} spell slot(s)")

        result = "The party rests...\n" + "\n".join(messages) if messages else "The party rests."

        if not safe_area:
            result += "\n(Note: Resting in dangerous areas may trigger random encounters!)"

        return result

    def _validate_formation_sync(self):
        """Ensure members and formation lists are synchronized"""
        if len(self.members) != len(self.formation):
            # Auto-repair: regenerate formation
            self.formation = []
            for member in self.members:
                if member.char_class in ['Fighter', 'Cleric']:
                    self.formation.append('front')
                else:
                    self.formation.append('back')

    def __len__(self) -> int:
        """Get party size"""
        return len(self.members)

    def __iter__(self):
        """Iterate over party members"""
        return iter(self.members)

    def __getitem__(self, index: int) -> PlayerCharacter:
        """Get member by index"""
        return self.members[index]


def create_default_party(characters: List[PlayerCharacter]) -> Party:
    """
    Create a party from a list of characters

    Args:
        characters: List of PlayerCharacter instances (max 6)

    Returns:
        Party instance
    """
    party = Party()

    for char in characters[:6]:  # Max 6
        party.add_member(char)

    return party
