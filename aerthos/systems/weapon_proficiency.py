"""
Weapon Proficiency System

Implements AD&D 1e weapon proficiency mechanics including:
- Proficiency slots by class
- Non-proficiency penalties to hit
- Proficiency gain on level up
- Weapon groups for broader proficiency
"""

import json
import os
from typing import List, Set, Dict
from pathlib import Path


class WeaponProficiencySystem:
    """Handles weapon proficiency calculations and tracking"""

    def __init__(self):
        """Load weapon proficiency data from JSON"""
        data_path = Path(__file__).parent.parent / 'data' / 'weapon_proficiencies.json'
        with open(data_path, 'r') as f:
            self.data = json.load(f)

        self.proficiency_by_class = self.data['proficiency_by_class']
        self.weapon_groups = self.data['weapon_groups']
        self.weapon_categories = self.data['weapon_categories']

    def get_initial_slots(self, char_class: str) -> int:
        """
        Get initial weapon proficiency slots for a class

        Args:
            char_class: Character class name

        Returns:
            Number of initial proficiency slots
        """
        class_data = self.proficiency_by_class.get(char_class, {})
        return class_data.get('initial_slots', 1)

    def get_additional_per_levels(self, char_class: str) -> int:
        """
        Get how many levels between gaining additional proficiency slots

        Args:
            char_class: Character class name

        Returns:
            Levels between new slots (e.g., 3 = gain slot at 4th, 7th, 10th, etc.)
        """
        class_data = self.proficiency_by_class.get(char_class, {})
        return class_data.get('additional_per_levels', 6)

    def get_non_proficiency_penalty(self, char_class: str) -> int:
        """
        Get to-hit penalty for using non-proficient weapon

        Args:
            char_class: Character class name

        Returns:
            Penalty to attack rolls (negative number)
        """
        class_data = self.proficiency_by_class.get(char_class, {})
        return class_data.get('non_proficiency_penalty', -5)

    def calculate_total_slots(self, char_class: str, level: int) -> int:
        """
        Calculate total proficiency slots for a class at a given level

        Args:
            char_class: Character class name
            level: Character level

        Returns:
            Total number of proficiency slots available
        """
        initial = self.get_initial_slots(char_class)
        per_levels = self.get_additional_per_levels(char_class)

        # Gain additional slot every N levels after 1st
        # Example: Fighter with per_levels=3 gains at 4, 7, 10, 13, etc.
        if level <= 1:
            return initial

        additional = (level - 1) // per_levels
        return initial + additional

    def is_proficient(self, proficiencies: List[str], weapon_name: str) -> bool:
        """
        Check if character is proficient with a weapon

        Args:
            proficiencies: List of proficiencies (weapons or groups)
            weapon_name: Name of the weapon to check

        Returns:
            True if proficient (either specific weapon or via group)
        """
        # Direct weapon proficiency
        if weapon_name in proficiencies:
            return True

        # Check if proficient via weapon group
        weapon_group = self.weapon_categories.get(weapon_name)
        if weapon_group and weapon_group in proficiencies:
            return True

        # Check if group name is in proficiencies (e.g., "swords")
        for prof in proficiencies:
            if prof in self.weapon_groups:
                if weapon_name in self.weapon_groups[prof]:
                    return True

        return False

    def get_available_weapons_for_proficiency(self) -> Dict[str, List[str]]:
        """
        Get all available weapons organized by group

        Returns:
            Dict mapping group names to weapon lists
        """
        return self.weapon_groups.copy()

    def get_weapon_group(self, weapon_name: str) -> str:
        """
        Get the weapon group for a specific weapon

        Args:
            weapon_name: Name of the weapon

        Returns:
            Group name (e.g., "swords") or "unknown" if not categorized
        """
        return self.weapon_categories.get(weapon_name, "unknown")

    def get_all_weapons_in_group(self, group_name: str) -> List[str]:
        """
        Get all weapons in a specific group

        Args:
            group_name: Name of the weapon group

        Returns:
            List of weapon names in that group
        """
        return self.weapon_groups.get(group_name, [])

    def format_proficiency_info(self, char_class: str, level: int,
                                current_proficiencies: List[str]) -> str:
        """
        Format proficiency information for display

        Args:
            char_class: Character class
            level: Character level
            current_proficiencies: List of current proficiencies

        Returns:
            Formatted string with proficiency information
        """
        total_slots = self.calculate_total_slots(char_class, level)
        used_slots = len(current_proficiencies)
        available_slots = total_slots - used_slots
        penalty = self.get_non_proficiency_penalty(char_class)
        per_levels = self.get_additional_per_levels(char_class)

        lines = [
            f"Weapon Proficiencies: {used_slots}/{total_slots} slots used",
            f"Non-proficiency penalty: {penalty} to hit",
            f"Next slot at level: {level + (per_levels - ((level - 1) % per_levels))}" if level > 1 else f"Next slot at level: {1 + per_levels}",
            ""
        ]

        if current_proficiencies:
            lines.append("Proficient with:")
            for prof in sorted(current_proficiencies):
                # Check if it's a group or individual weapon
                if prof in self.weapon_groups:
                    weapons = self.weapon_groups[prof]
                    lines.append(f"  - {prof.title()} ({len(weapons)} weapons)")
                else:
                    group = self.get_weapon_group(prof)
                    lines.append(f"  - {prof} ({group})")
        else:
            lines.append("No weapon proficiencies selected")

        if available_slots > 0:
            lines.append(f"\n{available_slots} slot(s) available for selection")

        return '\n'.join(lines)
