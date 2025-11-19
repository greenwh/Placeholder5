"""
Movement and Encumbrance System

Implements AD&D 1e movement rates, encumbrance effects, armor penalties,
and special movement actions (running, charging).
"""

from typing import Optional
from ..entities.character import Character
from ..entities.player import PlayerCharacter, Armor
from .ability_modifiers import AbilityModifierSystem


class MovementSystem:
    """Handles movement rate calculations and encumbrance effects"""

    # Base movement rates by race (in inches per round, indoor)
    BASE_MOVEMENT_BY_RACE = {
        'Human': 12,
        'Elf': 12,
        'Half-Elf': 12,
        'Half-Orc': 12,
        'Dwarf': 6,
        'Gnome': 6,
        'Halfling': 6
    }

    # Armor movement modifiers (overrides base if worn)
    # Format: armor_name: movement_rate
    ARMOR_MOVEMENT_RATES = {
        # No armor / Light armor: Normal movement (12")
        'none': 12,
        'Padded Armor': 12,
        'Leather Armor': 12,
        'Studded Leather': 12,
        'Ring Mail': 12,

        # Heavy armor: Slowed movement (9")
        'Scale Mail': 9,
        'Chain Mail': 9,
        'Splinted Mail': 9,
        'Banded Mail': 9,

        # Very heavy armor: Greatly slowed (6")
        'Plate Mail': 6
    }

    # Encumbrance thresholds as percentage of max weight
    ENCUMBRANCE_THRESHOLDS = {
        'unencumbered': (0.0, 1.0),      # 0% to 100% of base = full movement
        'lightly': (1.0, 1.5),            # 100% to 150% = 3/4 movement
        'heavily': (1.5, 2.0),            # 150% to 200% = 1/2 movement
        'severely': (2.0, float('inf'))  # Over 200% = 1/4 movement
    }

    ENCUMBRANCE_MULTIPLIERS = {
        'unencumbered': 1.0,
        'lightly': 0.75,
        'heavily': 0.5,
        'severely': 0.25
    }

    def __init__(self):
        """Initialize movement system with ability modifier system"""
        self.ability_system = AbilityModifierSystem()

    def get_base_movement(self, race: str) -> int:
        """
        Get base movement rate by race

        Args:
            race: Character race

        Returns:
            Base movement rate in inches per round
        """
        return self.BASE_MOVEMENT_BY_RACE.get(race, 12)

    def get_armor_movement_rate(self, armor: Optional[Armor]) -> int:
        """
        Get movement rate imposed by armor

        Args:
            armor: Equipped armor (None if no armor)

        Returns:
            Movement rate in inches per round
        """
        if armor is None:
            return 12

        # Magic armor negates weight penalties
        if hasattr(armor, 'magic_bonus') and armor.magic_bonus > 0:
            return 12

        armor_name = armor.name
        return self.ARMOR_MOVEMENT_RATES.get(armor_name, 12)

    def get_encumbrance_category(self, current_weight: float, max_weight: float) -> str:
        """
        Determine encumbrance category based on weight

        Args:
            current_weight: Current carried weight
            max_weight: Maximum weight capacity (from STR)

        Returns:
            Encumbrance category name
        """
        if max_weight <= 0:
            return 'severely'

        ratio = current_weight / max_weight

        # Check each category (order matters - check from least to most encumbered)
        if ratio <= 1.0:
            return 'unencumbered'
        elif ratio <= 1.5:
            return 'lightly'
        elif ratio <= 2.0:
            return 'heavily'
        else:
            return 'severely'

    def get_encumbrance_modifier(self, current_weight: float, max_weight: float) -> float:
        """
        Get movement multiplier based on encumbrance

        Args:
            current_weight: Current carried weight
            max_weight: Maximum weight capacity

        Returns:
            Movement multiplier (1.0 = full, 0.5 = half, etc.)
        """
        category = self.get_encumbrance_category(current_weight, max_weight)
        return self.ENCUMBRANCE_MULTIPLIERS[category]

    def calculate_movement_rate(self, character: PlayerCharacter) -> int:
        """
        Calculate final movement rate with all modifiers

        Args:
            character: The character

        Returns:
            Final movement rate in inches per round
        """
        # 1. Start with racial base movement
        base_movement = self.get_base_movement(character.race)

        # 2. Apply armor penalty (armor overrides base for most races)
        armor = character.equipment.armor if hasattr(character, 'equipment') else None
        armor_movement = self.get_armor_movement_rate(armor)

        # Use the more restrictive of armor or race
        # (Dwarves with plate still move 6", not slowed further)
        current_movement = min(base_movement, armor_movement)

        # 3. Apply encumbrance modifier
        if hasattr(character, 'inventory'):
            current_weight = character.inventory.current_weight

            # Get STR weight allowance
            str_mods = self.ability_system.get_strength_modifiers(character.strength)
            base_capacity = 500  # Base capacity in GP (50 lbs at 10 GP = 1 lb)
            max_weight = base_capacity + str_mods['weight_allowance']

            encumbrance_mod = self.get_encumbrance_modifier(current_weight, max_weight)
            current_movement = int(current_movement * encumbrance_mod)

        return max(1, current_movement)  # Minimum 1" movement

    def can_run(self, character: Character) -> bool:
        """
        Check if character can run (3x movement for CON rounds)

        Args:
            character: The character

        Returns:
            True if character can run
        """
        # Cannot run in plate armor
        if hasattr(character, 'equipment') and character.equipment.armor:
            if 'Plate' in character.equipment.armor.name:
                return False

        # Cannot run if severely encumbered
        if hasattr(character, 'inventory'):
            current_weight = character.inventory.current_weight
            str_mods = self.ability_system.get_strength_modifiers(character.strength)
            max_weight = 500 + str_mods['weight_allowance']
            category = self.get_encumbrance_category(current_weight, max_weight)

            if category == 'severely':
                return False

        return True

    def calculate_run_movement(self, character: PlayerCharacter) -> int:
        """
        Calculate running movement (3x normal)

        Args:
            character: The character

        Returns:
            Running movement rate (0 if cannot run)
        """
        if not self.can_run(character):
            return 0

        base_movement = self.calculate_movement_rate(character)
        return base_movement * 3

    def calculate_run_duration(self, character: Character) -> int:
        """
        Calculate how many rounds character can run

        Args:
            character: The character

        Returns:
            Number of rounds (equal to CON score)
        """
        return character.constitution

    def can_charge(self, character: Character) -> bool:
        """
        Check if character can charge (2x movement, +2 to hit)

        Args:
            character: The character

        Returns:
            True if character can charge
        """
        # Same restrictions as running, but charging is 2x instead of 3x
        return self.can_run(character)

    def calculate_charge_movement(self, character: PlayerCharacter) -> int:
        """
        Calculate charging movement (2x normal)

        Args:
            character: The character

        Returns:
            Charging movement rate (0 if cannot charge)
        """
        if not self.can_charge(character):
            return 0

        base_movement = self.calculate_movement_rate(character)
        return base_movement * 2

    def get_movement_description(self, character: PlayerCharacter) -> str:
        """
        Get a textual description of character's movement capabilities

        Args:
            character: The character

        Returns:
            Formatted movement description
        """
        base_rate = self.calculate_movement_rate(character)
        run_rate = self.calculate_run_movement(character)
        charge_rate = self.calculate_charge_movement(character)

        lines = [
            f"Movement Rate: {base_rate}\" per round",
        ]

        # Add encumbrance info
        if hasattr(character, 'inventory'):
            current_weight = character.inventory.current_weight
            str_mods = self.ability_system.get_strength_modifiers(character.strength)
            max_weight = 500 + str_mods['weight_allowance']
            category = self.get_encumbrance_category(current_weight, max_weight)

            lines.append(f"Encumbrance: {category.capitalize()} ({current_weight:.0f}/{max_weight:.0f} GP)")

        # Add special movement
        if run_rate > 0:
            run_duration = self.calculate_run_duration(character)
            lines.append(f"Can run: {run_rate}\" per round (for {run_duration} rounds)")

        if charge_rate > 0:
            lines.append(f"Can charge: {charge_rate}\" per round (+2 to hit)")

        return '\n'.join(lines)
