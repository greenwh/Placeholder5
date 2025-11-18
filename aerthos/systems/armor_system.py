"""
Armor System - AD&D 1e armor and shield management

Loads armor database, validates class restrictions, creates armor/shield objects.
Handles AC calculations, movement rates, and encumbrance from armor.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from ..entities.player import Armor, Shield, Item


class ArmorSystem:
    """System for managing armor and shields"""

    def __init__(self):
        """Load armor database from JSON"""
        data_path = Path(__file__).parent.parent / 'data' / 'armor.json'
        with open(data_path, 'r') as f:
            self.data = json.load(f)

        self.armor_data = self.data['armor']
        self.shield_data = self.data['shields']
        self.helmet_data = self.data.get('helmets', {})
        self.class_restrictions = self.data['class_restrictions']

    def create_armor(self, armor_id: str, magic_bonus: int = 0) -> Optional[Armor]:
        """
        Create an Armor object from the database

        Args:
            armor_id: Armor identifier (e.g., 'leather', 'plate_mail')
            magic_bonus: Magic bonus (+1, +2, etc.)

        Returns:
            Armor object or None if not found
        """
        if armor_id not in self.armor_data:
            return None

        data = self.armor_data[armor_id]

        return Armor(
            name=data['name'] + (f" +{magic_bonus}" if magic_bonus > 0 else ""),
            item_type='armor',
            weight=data['weight_gp'],
            properties={'armor_id': armor_id},
            description=data.get('description', ''),
            ac=data['ac'],
            armor_type=data['armor_type'],
            movement_rate=data['movement_rate'],
            magic_bonus=magic_bonus,
            allowed_classes=data['allowed_classes']
        )

    def create_shield(self, shield_id: str, magic_bonus: int = 0) -> Optional[Shield]:
        """
        Create a Shield object from the database

        Args:
            shield_id: Shield identifier (e.g., 'shield_small', 'shield_large')
            magic_bonus: Magic bonus (+1, +2, etc.)

        Returns:
            Shield object or None if not found
        """
        if shield_id not in self.shield_data:
            return None

        data = self.shield_data[shield_id]

        return Shield(
            name=data['name'] + (f" +{magic_bonus}" if magic_bonus > 0 else ""),
            item_type='shield',
            weight=data['weight_gp'],
            properties={'shield_id': shield_id},
            description=data.get('description', ''),
            ac_bonus=data['ac_bonus'],
            max_attacks_blocked=data['max_attacks_blocked'],
            magic_bonus=magic_bonus,
            allowed_classes=data['allowed_classes']
        )

    def can_wear_armor(self, char_class: str, armor_id: str) -> bool:
        """
        Check if a class can wear specific armor

        Args:
            char_class: Character class name
            armor_id: Armor identifier

        Returns:
            bool: Can wear this armor
        """
        if char_class not in self.class_restrictions:
            return False

        restrictions = self.class_restrictions[char_class]
        armor_allowed = restrictions['armor']

        # "any" means all armor
        if armor_allowed == "any":
            return True

        # "none" means no armor
        if armor_allowed == "none":
            return False

        # List of specific allowed armor
        if isinstance(armor_allowed, list):
            return armor_id in armor_allowed

        return False

    def can_use_shield(self, char_class: str, shield_id: str) -> bool:
        """
        Check if a class can use specific shield

        Args:
            char_class: Character class name
            shield_id: Shield identifier

        Returns:
            bool: Can use this shield
        """
        if char_class not in self.class_restrictions:
            return False

        restrictions = self.class_restrictions[char_class]
        shield_allowed = restrictions['shields']

        # "any" means all shields
        if shield_allowed == "any":
            return True

        # "none" means no shields
        if shield_allowed == "none":
            return False

        # List of specific allowed shields
        if isinstance(shield_allowed, list):
            return shield_id in shield_allowed

        return False

    def get_armor_list(self, char_class: Optional[str] = None) -> List[Dict]:
        """
        Get list of available armor

        Args:
            char_class: Optional class to filter by restrictions

        Returns:
            List of armor data dicts
        """
        armor_list = []

        for armor_id, data in self.armor_data.items():
            if char_class is None or self.can_wear_armor(char_class, armor_id):
                armor_list.append({
                    'id': armor_id,
                    'name': data['name'],
                    'ac': data['ac'],
                    'cost': data['cost_gp'],
                    'weight': data['weight_gp'],
                    'type': data['armor_type'],
                    'movement': data['movement_rate']
                })

        return armor_list

    def get_shield_list(self, char_class: Optional[str] = None) -> List[Dict]:
        """
        Get list of available shields

        Args:
            char_class: Optional class to filter by restrictions

        Returns:
            List of shield data dicts
        """
        shield_list = []

        for shield_id, data in self.shield_data.items():
            if char_class is None or self.can_use_shield(char_class, shield_id):
                shield_list.append({
                    'id': shield_id,
                    'name': data['name'],
                    'ac_bonus': data['ac_bonus'],
                    'cost': data['cost_gp'],
                    'weight': data['weight_gp'],
                    'blocks': data['max_attacks_blocked']
                })

        return shield_list

    def get_class_restrictions_description(self, char_class: str) -> str:
        """
        Get readable description of class armor restrictions

        Args:
            char_class: Character class name

        Returns:
            Description string
        """
        if char_class not in self.class_restrictions:
            return "Unknown class"

        return self.class_restrictions[char_class].get('description', '')

    def calculate_ac(self, armor: Optional[Armor], shield: Optional[Shield],
                    dex_modifier: int = 0, base_ac: int = 10) -> int:
        """
        Calculate final AC from armor, shield, and DEX

        Args:
            armor: Equipped armor (None = unarmored)
            shield: Equipped shield (None = no shield)
            dex_modifier: DEX defensive adjustment
            base_ac: Base AC for unarmored (10)

        Returns:
            Final AC (lower is better)
        """
        # Start with armor AC or base
        if armor:
            ac = armor.get_effective_ac()
        else:
            ac = base_ac

        # Add shield bonus
        if shield:
            ac -= shield.get_effective_bonus()

        # Add DEX modifier (negative improves AC)
        ac += dex_modifier

        return ac

    def get_armor_by_ac(self, target_ac: int) -> List[str]:
        """
        Get list of armor IDs that provide specific AC

        Args:
            target_ac: Target AC value

        Returns:
            List of armor IDs
        """
        results = []
        for armor_id, data in self.armor_data.items():
            if data['ac'] == target_ac:
                results.append(armor_id)
        return results

    def get_best_armor_for_class(self, char_class: str) -> Optional[str]:
        """
        Get the best (lowest AC) armor a class can wear

        Args:
            char_class: Character class name

        Returns:
            Armor ID or None
        """
        available = self.get_armor_list(char_class)
        if not available:
            return None

        # Sort by AC (lowest is best)
        available.sort(key=lambda x: x['ac'])
        return available[0]['id']

    def is_magic_armor_negates_weight(self, armor: Armor) -> bool:
        """
        Check if magic armor negates weight penalty

        Magic armor in AD&D 1e negates weight for movement purposes

        Args:
            armor: Armor object

        Returns:
            bool: Whether weight penalty is negated
        """
        return armor.magic_bonus > 0
