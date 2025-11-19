"""
Monster AI Targeting System

Implements formation-aware targeting for monsters in combat.
Based on Gold Box game mechanics where formation position affects targeting priority.
"""

import random
from typing import List, Optional
from ..entities.character import Character
from ..entities.monster import Monster
from ..entities.party import Party


class MonsterTargetingAI:
    """Handles monster targeting decisions in combat based on formation and threat assessment"""

    # Targeting probability thresholds
    FRONT_LINE_CHANCE = 70  # 1-70: Target front line
    BACK_LINE_CHANCE = 90   # 71-90: Target back line (if reachable)
    # 91-100: Opportunistic targeting

    # Intelligence thresholds
    LOW_INT = 4   # Animal intelligence - always attack nearest
    HIGH_INT = 12  # Tactical intelligence - can prioritize spellcasters

    def __init__(self):
        """Initialize the targeting AI"""
        pass

    def select_target(self,
                     attacker: Monster,
                     party: Optional[Party],
                     all_targets: List[Character]) -> Character:
        """
        Select best target based on formation, threat, and attacker intelligence

        Args:
            attacker: The attacking monster
            party: The party object (if party combat), or None for solo
            all_targets: List of all valid targets (alive characters)

        Returns:
            Selected target Character

        Priority system:
        1. Front-line targets (70% chance) - prefer lowest HP
        2. Back-line targets (20% chance) - if visible/reachable
        3. Opportunistic targeting (10% chance) - lowest AC or most wounded
        """

        # Solo play fallback - no party formation
        if party is None or not hasattr(party, 'formation'):
            return random.choice(all_targets)

        # Check if party has formation system
        if not hasattr(party, 'get_front_line') or not hasattr(party, 'get_back_line'):
            return random.choice(all_targets)

        # Get formation positions
        front_line = [char for char in party.get_front_line() if char.is_alive]
        back_line = [char for char in party.get_back_line() if char.is_alive]

        # If no clear formation, random selection
        if not front_line and not back_line:
            return random.choice(all_targets)

        # Get attacker intelligence for behavior modification
        intelligence = getattr(attacker, 'int', 10)  # Default to average if not set

        # Low intelligence - always attack nearest (front line bias)
        if intelligence <= self.LOW_INT:
            if front_line:
                return self._select_weakest_target(front_line)
            elif back_line:
                return random.choice(back_line)
            else:
                return random.choice(all_targets)

        # Roll for targeting strategy (d100)
        roll = random.randint(1, 100)

        # 1-70: Attack front line
        if roll <= self.FRONT_LINE_CHANCE:
            return self._target_front_line(front_line, back_line, all_targets)

        # 71-90: Attack back line (if reachable)
        elif roll <= self.BACK_LINE_CHANCE:
            return self._target_back_line(front_line, back_line, all_targets, intelligence)

        # 91-100: Opportunistic targeting
        else:
            return self._opportunistic_targeting(all_targets, intelligence)

    def _target_front_line(self,
                          front_line: List[Character],
                          back_line: List[Character],
                          all_targets: List[Character]) -> Character:
        """
        Target front line - prefer most wounded to finish them off

        Args:
            front_line: Characters in front formation
            back_line: Characters in back formation
            all_targets: All valid targets

        Returns:
            Selected target from front line (or fallback)
        """
        if front_line:
            # Prefer most wounded front-line fighter
            return self._select_weakest_target(front_line)
        elif back_line:
            # No front line standing, attack back line
            return random.choice(back_line)
        else:
            # Fallback
            return random.choice(all_targets)

    def _target_back_line(self,
                         front_line: List[Character],
                         back_line: List[Character],
                         all_targets: List[Character],
                         intelligence: int) -> Character:
        """
        Attempt to target back line

        Only succeeds if:
        - Front line is defeated OR
        - Monster has high intelligence (can prioritize threats)

        Args:
            front_line: Characters in front formation
            back_line: Characters in back formation
            all_targets: All valid targets
            intelligence: Attacker's intelligence score

        Returns:
            Selected target (back line if reachable, else front line)
        """
        # No front line - back line exposed
        if not front_line and back_line:
            return random.choice(back_line)

        # High intelligence - can bypass front line to target spellcasters
        if intelligence >= self.HIGH_INT and back_line:
            # Prioritize spellcasters if intelligent
            spellcasters = [char for char in back_line
                          if hasattr(char, 'char_class') and
                          char.char_class in ['Magic-User', 'Cleric']]

            if spellcasters:
                return random.choice(spellcasters)
            else:
                return random.choice(back_line)

        # Otherwise, blocked by front line
        if front_line:
            return self._select_weakest_target(front_line)

        # Fallback
        return random.choice(all_targets)

    def _opportunistic_targeting(self,
                                all_targets: List[Character],
                                intelligence: int) -> Character:
        """
        Opportunistic targeting - go for weakest target

        Priorities:
        - High INT: Target lowest AC (easier to hit)
        - Low/Med INT: Target most wounded (finish them off)

        Args:
            all_targets: All valid targets
            intelligence: Attacker's intelligence score

        Returns:
            Selected target based on opportunity
        """
        if intelligence >= self.HIGH_INT:
            # Smart monsters target low AC (easier to hit)
            return min(all_targets, key=lambda char: char.ac)
        else:
            # Average monsters target most wounded
            return self._select_weakest_target(all_targets)

    def _select_weakest_target(self, targets: List[Character]) -> Character:
        """
        Select most wounded target (lowest HP percentage)

        Args:
            targets: List of potential targets

        Returns:
            Target with lowest HP percentage
        """
        if not targets:
            raise ValueError("Cannot select from empty target list")

        # Find target with lowest HP percentage
        def hp_percentage(char: Character) -> float:
            if char.hp_max <= 0:
                return 0.0
            return char.hp_current / char.hp_max

        return min(targets, key=hp_percentage)
