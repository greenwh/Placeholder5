"""
Time tracking system - manages turns, light sources, and resource consumption
"""

from typing import List, Optional, Dict
from ..entities.player import PlayerCharacter, LightSource


class TimeTracker:
    """
    Tracks game time in 10-minute turns (AD&D standard)

    1 turn = 10 minutes
    6 turns = 1 hour
    """

    def __init__(self):
        self.turns_elapsed = 0
        self.total_hours = 0

    def advance_turn(self, player: PlayerCharacter) -> List[str]:
        """
        Advance time by 1 turn (10 minutes)

        Args:
            player: The player character

        Returns:
            List of event messages
        """

        self.turns_elapsed += 1
        messages = []

        # Consume light
        light_msg = self._consume_light(player)
        if light_msg:
            messages.append(light_msg)

        # Every 6 turns (1 hour)
        if self.turns_elapsed % 6 == 0:
            self.total_hours += 1

            # Check hunger
            hunger_msg = self._check_hunger(player)
            if hunger_msg:
                messages.append(hunger_msg)

        return messages

    def _consume_light(self, player: PlayerCharacter) -> Optional[str]:
        """
        Decrease active light source duration and auto-equip new light sources

        Args:
            player: The player character

        Returns:
            Message if light status changed
        """

        light_source = player.equipment.light_source

        if light_source:
            light_source.turns_remaining -= 1

            if light_source.turns_remaining <= 0:
                # Light goes out - try to auto-equip a new one
                player.equipment.light_source = None

                # Look for another light source in inventory
                new_light = self._find_light_source(player)
                if new_light:
                    player.equip_light(new_light)
                    return f"⚠️  Your {light_source.name} burns out! Automatically lighting a new {new_light.name}."
                else:
                    return "⚠️  Your light source sputters and dies! You are in darkness. (No spare light sources!)"
            elif light_source.turns_remaining == 1:
                return "⚠️  Your light source is almost exhausted!"
            elif light_source.turns_remaining == 3:
                return "⚠️  Your light source is burning low."

        return None

    def _find_light_source(self, player: PlayerCharacter) -> Optional[LightSource]:
        """
        Find an available light source in inventory

        Args:
            player: The player character

        Returns:
            LightSource if found, None otherwise
        """
        for item in player.inventory.items:
            if isinstance(item, LightSource) and item != player.equipment.light_source:
                return item
        return None

    def _check_hunger(self, player: PlayerCharacter) -> Optional[str]:
        """
        Check if player needs to eat

        In a more complete implementation, this would track
        actual ration consumption and apply penalties for starvation

        Args:
            player: The player character

        Returns:
            Hunger warning message
        """

        if self.total_hours % 8 == 0:
            return "You're getting hungry and tired. Consider resting and eating soon."

        return None

    def get_time_string(self) -> str:
        """Get a human-readable time string"""

        hours = self.total_hours
        days = hours // 24
        hours_today = hours % 24

        if days > 0:
            return f"Day {days + 1}, Hour {hours_today} ({self.turns_elapsed} turns total)"
        else:
            return f"Hour {hours_today} ({self.turns_elapsed} turns)"


class RestSystem:
    """Handles resting and recovery"""

    def attempt_rest(self, player: PlayerCharacter, is_safe: bool) -> Dict:
        """
        Attempt to rest for 8 hours

        Args:
            player: The player character
            is_safe: Whether the location is safe for rest

        Returns:
            Dict with: success, hp_recovered, spells_restored, interrupted, narrative
        """

        if not is_safe:
            return {
                'success': False,
                'hp_recovered': 0,
                'spells_restored': False,
                'interrupted': False,
                'narrative': "This area is too dangerous to rest! You need to find a safer location."
            }

        # Consume rations
        if not player.consume_ration():
            return {
                'success': False,
                'hp_recovered': 0,
                'spells_restored': False,
                'interrupted': False,
                'narrative': "You have no rations to eat! You need food to rest properly."
            }

        # Random encounter check (15% chance of interruption)
        import random
        if random.random() < 0.15:
            return {
                'success': False,
                'hp_recovered': 0,
                'spells_restored': False,
                'interrupted': True,
                'narrative': "Your rest is interrupted by wandering monsters!"
            }

        # Successful rest
        hp_recovered = self._recover_hp(player)
        player.restore_spells()

        # Remove some conditions
        if 'exhausted' in player.conditions:
            player.remove_condition('exhausted')

        narrative = f"You rest for 8 hours and eat your rations.\n"
        narrative += f"HP restored: {hp_recovered}\n"
        if player.spells_memorized:
            narrative += f"Spells memorized and ready.\n"
        narrative += f"You feel refreshed and ready to continue."

        return {
            'success': True,
            'hp_recovered': hp_recovered,
            'spells_restored': True,
            'interrupted': False,
            'narrative': narrative
        }

    def _recover_hp(self, player: PlayerCharacter) -> int:
        """
        Recover HP during rest

        AD&D 1e: 1 HP per day of rest
        (We'll be generous and give 1d4 for 8 hours)

        Args:
            player: The player character

        Returns:
            Amount of HP recovered
        """

        import random

        if player.hp_current >= player.hp_max:
            return 0

        # Recover 1d4 HP (or up to max)
        recovery = random.randint(1, 4)
        old_hp = player.hp_current
        player.heal(recovery)
        actual_recovery = player.hp_current - old_hp

        return actual_recovery
