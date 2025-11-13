"""
Inn system for rest, food, and lodging
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class InnRoom:
    """A room type available at an inn"""
    type: str
    price: int
    description: str


@dataclass
class FoodDrink:
    """Food or drink available at an inn"""
    name: str
    price: int
    description: str


@dataclass
class InnService:
    """A service offered by an inn"""
    name: str
    price: int
    description: str


class Inn:
    """Represents an inn where players can rest and recover"""

    def __init__(self, inn_id: str, data: Dict):
        self.inn_id = inn_id
        self.name = data['name']
        self.quality = data['quality']
        self.description = data['description']
        self.rooms = [InnRoom(**room) for room in data.get('rooms', [])]
        self.food_drink = [FoodDrink(**item) for item in data.get('food_drink', [])]
        self.services = [InnService(**svc) for svc in data.get('services', [])]
        self.rest_benefits = data.get('rest_benefits', {})

    def get_room_price(self, room_type: str) -> Optional[int]:
        """Get the price of a room"""
        for room in self.rooms:
            if room.type == room_type:
                return room.price
        return None

    def get_rest_benefits(self, room_type: str) -> Optional[Dict]:
        """Get the benefits of resting in a room type"""
        return self.rest_benefits.get(room_type)

    def rest(self, room_type: str, character) -> Dict:
        """
        Rest at the inn and apply benefits
        Returns a dict with the results
        """
        benefits = self.get_rest_benefits(room_type)
        if not benefits:
            return {'success': False, 'message': 'Invalid room type'}

        result = {
            'success': True,
            'hp_healed': 0,
            'spells_recovered': False,
            'fatigue_removed': False
        }

        # HP Recovery
        hp_recovery = benefits.get('hp_recovery', 'none')
        if hp_recovery == 'full':
            healed = character.hp_max - character.hp_current
            character.hp_current = character.hp_max
            result['hp_healed'] = healed
        elif hp_recovery == 'half':
            healed = (character.hp_max - character.hp_current) // 2
            character.hp_current = min(character.hp_max, character.hp_current + healed)
            result['hp_healed'] = healed
        elif hp_recovery == 'quarter':
            healed = (character.hp_max - character.hp_current) // 4
            character.hp_current = min(character.hp_max, character.hp_current + healed)
            result['hp_healed'] = healed

        # Bonus HP (luxury inns)
        bonus_hp = benefits.get('bonus_hp', 0)
        if bonus_hp > 0:
            character.hp_current = min(character.hp_max + bonus_hp, character.hp_current + bonus_hp)
            result['bonus_hp'] = bonus_hp

        # Spell Recovery
        if benefits.get('spell_recovery', False):
            # Reset all spell slots
            for slot in character.spells_memorized:
                slot.is_used = False
            result['spells_recovered'] = True

        # Fatigue Removal
        fatigue = benefits.get('fatigue_removal', 'none')
        result['fatigue_removed'] = fatigue in ['partial', 'full']

        return result

    def list_rooms(self) -> List[Dict]:
        """List all room types available"""
        return [
            {
                'type': room.type,
                'price': room.price,
                'description': room.description
            }
            for room in self.rooms
        ]

    def list_food_drink(self) -> List[Dict]:
        """List all food and drink available"""
        return [
            {
                'name': item.name,
                'price': item.price,
                'description': item.description
            }
            for item in self.food_drink
        ]

    def list_services(self) -> List[Dict]:
        """List all services available"""
        return [
            {
                'name': svc.name,
                'price': svc.price,
                'description': svc.description
            }
            for svc in self.services
        ]


class InnManager:
    """Manages all inns in the game"""

    def __init__(self, inns_data_path: str = "aerthos/data/inns.json"):
        with open(inns_data_path, 'r') as f:
            data = json.load(f)

        self.inns = {
            inn_id: Inn(inn_id, inn_data)
            for inn_id, inn_data in data.items()
        }

    def get_inn(self, inn_id: str) -> Optional[Inn]:
        """Get an inn by ID"""
        return self.inns.get(inn_id)

    def list_all_inns(self) -> List[Dict]:
        """List all available inns"""
        return [
            {
                'id': inn_id,
                'name': inn.name,
                'quality': inn.quality,
                'description': inn.description
            }
            for inn_id, inn in self.inns.items()
        ]
