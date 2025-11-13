"""
Dungeon class - manages the game world and navigation
"""

import json
from typing import Dict, Optional, List
from pathlib import Path
from .room import Room


class Dungeon:
    """Manages the dungeon layout and navigation"""

    def __init__(self, name: str, start_room_id: str, rooms: Dict[str, Room], room_data: Dict = None):
        self.name = name
        self.start_room_id = start_room_id
        self.rooms = rooms
        self.room_data = room_data or {}  # Store raw room data for encounter info

    @classmethod
    def load_from_file(cls, filepath: str) -> 'Dungeon':
        """
        Load dungeon from JSON file

        Args:
            filepath: Path to dungeon JSON file

        Returns:
            Dungeon instance
        """

        with open(filepath, 'r') as f:
            data = json.load(f)

        name = data.get('name', 'Unknown Dungeon')
        start_room_id = data['start_room']

        # Load all rooms
        rooms = {}
        for room_id, room_data in data['rooms'].items():
            room = Room(
                id=room_data['id'],
                title=room_data['title'],
                description=room_data['description'],
                light_level=room_data.get('light_level', 'dark'),
                exits=room_data.get('exits', {}),
                items=room_data.get('items', []),
                is_safe_for_rest=room_data.get('safe_rest', False)
            )
            rooms[room_id] = room

        return cls(name, start_room_id, rooms, data['rooms'])

    @classmethod
    def load_from_generator(cls, dungeon_data: Dict) -> 'Dungeon':
        """
        Load dungeon from generator output

        Args:
            dungeon_data: Dictionary from DungeonGenerator.generate()

        Returns:
            Dungeon instance
        """
        name = dungeon_data.get('name', 'Generated Dungeon')
        start_room_id = dungeon_data['start_room']

        # Load all rooms
        rooms = {}
        for room_id, room_data in dungeon_data['rooms'].items():
            room = Room(
                id=room_data['id'],
                title=room_data['title'],
                description=room_data['description'],
                light_level=room_data.get('light_level', 'dark'),
                exits=room_data.get('exits', {}),
                items=room_data.get('items', []),
                is_safe_for_rest=room_data.get('safe_rest', False)
            )
            rooms[room_id] = room

        return cls(name, start_room_id, rooms, dungeon_data['rooms'])

    def get_room(self, room_id: str) -> Optional[Room]:
        """Get a room by ID"""
        return self.rooms.get(room_id)

    def get_start_room(self) -> Room:
        """Get the starting room"""
        return self.rooms[self.start_room_id]

    def move(self, current_room_id: str, direction: str) -> Optional[Room]:
        """
        Move from current room in a direction

        Args:
            current_room_id: Current room ID
            direction: Direction to move

        Returns:
            New room or None if move invalid
        """

        current_room = self.get_room(current_room_id)
        if not current_room:
            return None

        if not current_room.has_exit(direction):
            return None

        next_room_id = current_room.get_exit(direction)
        return self.get_room(next_room_id)

    def get_explored_rooms(self) -> List[Room]:
        """Get all explored rooms"""
        return [room for room in self.rooms.values() if room.is_explored]

    def get_room_encounters(self, room_id: str) -> List[Dict]:
        """Get encounter data for a room"""
        if room_id in self.room_data:
            return self.room_data[room_id].get('encounters', [])
        return []

    def serialize(self) -> Dict:
        """Serialize dungeon state for saving"""
        return {
            'name': self.name,
            'start_room_id': self.start_room_id,
            'room_states': {
                room_id: {
                    'is_explored': room.is_explored,
                    'items': room.items,
                    'encounters_completed': room.encounters_completed
                }
                for room_id, room in self.rooms.items()
            }
        }

    def to_dict(self) -> Dict:
        """
        Convert dungeon to full dictionary representation for scenario saving

        Returns:
            Dictionary with complete dungeon structure
        """
        return {
            'name': self.name,
            'start_room': self.start_room_id,  # Note: 'start_room' for compatibility with load_from_generator
            'rooms': {
                room_id: {
                    'id': room.id,
                    'title': room.title,
                    'description': room.description,
                    'light_level': room.light_level,
                    'exits': room.exits,
                    'items': room.items,
                    'safe_rest': room.is_safe_for_rest,
                    'encounters': self.room_data.get(room_id, {}).get('encounters', []) if self.room_data else []
                }
                for room_id, room in self.rooms.items()
            }
        }

    @classmethod
    def deserialize(cls, data: Dict, original_dungeon_file: str) -> 'Dungeon':
        """
        Restore dungeon from saved state

        Args:
            data: Serialized dungeon data
            original_dungeon_file: Path to original dungeon definition

        Returns:
            Dungeon instance with restored state
        """

        # Load base dungeon
        dungeon = cls.load_from_file(original_dungeon_file)

        # Restore room states
        room_states = data.get('room_states', {})
        for room_id, state in room_states.items():
            if room_id in dungeon.rooms:
                room = dungeon.rooms[room_id]
                room.is_explored = state.get('is_explored', False)
                room.items = state.get('items', [])
                room.encounters_completed = state.get('encounters_completed', [])

        return dungeon
