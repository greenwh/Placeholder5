"""
Multi-Level Dungeon System

Extends the basic Dungeon class to support multiple dungeon levels/floors
connected by stairs. Implements classic megadungeon architecture where
difficulty increases with depth.
"""

from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field
from .dungeon import Dungeon
from .room import Room


@dataclass
class DungeonLevel:
    """A single level within a multi-level dungeon"""
    level_number: int  # 1, 2, 3, etc. (deeper = higher number)
    name: str  # "Level 1: The Entrance", "Level 2: Kobold Warrens", etc.
    dungeon: Dungeon  # The actual dungeon data for this level
    difficulty_tier: int = 1  # 1=Easy, 2=Standard, 3=Hard, 4=Deadly


class MultiLevelDungeon:
    """
    Multi-level dungeon with vertical navigation via stairs

    Features:
    - Multiple connected levels accessed via stairs
    - Difficulty scaling by depth
    - Unified save/load support
    - Cross-level state tracking
    """

    def __init__(self, name: str):
        """
        Initialize multi-level dungeon

        Args:
            name: Overall dungeon name
        """
        self.name = name
        self.levels: Dict[int, DungeonLevel] = {}  # level_number -> DungeonLevel
        self.current_level_number = 1
        self.description = ""

    def add_level(
        self,
        level_number: int,
        dungeon: Dungeon,
        level_name: str = None,
        difficulty_tier: int = None
    ):
        """
        Add a level to the dungeon

        Args:
            level_number: Level number (1, 2, 3, etc.)
            dungeon: Dungeon instance for this level
            level_name: Optional name for this level
            difficulty_tier: Difficulty tier (1-4), defaults to level_number
        """
        if level_name is None:
            level_name = f"Level {level_number}"

        if difficulty_tier is None:
            difficulty_tier = min(level_number, 4)  # Cap at 4 (Deadly)

        level = DungeonLevel(
            level_number=level_number,
            name=level_name,
            dungeon=dungeon,
            difficulty_tier=difficulty_tier
        )

        self.levels[level_number] = level

    def get_current_level(self) -> Optional[DungeonLevel]:
        """Get the current dungeon level"""
        return self.levels.get(self.current_level_number)

    def get_level(self, level_number: int) -> Optional[DungeonLevel]:
        """Get a specific dungeon level by number"""
        return self.levels.get(level_number)

    def get_current_dungeon(self) -> Optional[Dungeon]:
        """Get the Dungeon instance for the current level"""
        level = self.get_current_level()
        return level.dungeon if level else None

    def get_room(self, room_id: str, level_number: Optional[int] = None) -> Optional[Room]:
        """
        Get a room by ID, optionally from a specific level

        Args:
            room_id: Room ID
            level_number: Specific level to search (None = current level)

        Returns:
            Room instance or None
        """
        if level_number is None:
            level_number = self.current_level_number

        level = self.get_level(level_number)
        if level and level.dungeon:
            return level.dungeon.get_room(room_id)
        return None

    def move(
        self,
        current_room_id: str,
        direction: str
    ) -> Tuple[Optional[Room], Optional[int], Optional[str]]:
        """
        Move from current room in a direction

        Handles both horizontal movement and vertical (stairs)

        Args:
            current_room_id: Current room ID
            direction: Direction to move (or "stairs_up"/"stairs_down")

        Returns:
            Tuple of (new_room, new_level_number, message)
            Returns (None, None, error_message) if move invalid
        """
        dungeon = self.get_current_dungeon()
        if not dungeon:
            return None, None, "Invalid dungeon state"

        current_room = dungeon.get_room(current_room_id)
        if not current_room:
            return None, None, "Invalid current room"

        # Check if the direction is valid
        if not current_room.has_exit(direction):
            return None, None, f"No exit {direction}"

        # Get destination
        dest_room_id = current_room.get_exit(direction)

        # Check if this is a stair exit (cross-level movement)
        if direction in ["stairs_up", "up", "u"]:
            return self._move_stairs_up(dest_room_id)
        elif direction in ["stairs_down", "down", "d"]:
            return self._move_stairs_down(dest_room_id)
        else:
            # Regular horizontal movement on same level
            next_room = dungeon.get_room(dest_room_id)
            if next_room:
                return next_room, self.current_level_number, None
            else:
                return None, None, f"Destination room {dest_room_id} not found"

    def _move_stairs_up(self, dest_room_id: str) -> Tuple[Optional[Room], Optional[int], Optional[str]]:
        """Move up stairs to previous level"""
        target_level = self.current_level_number - 1

        if target_level < 1:
            return None, None, "You've reached the surface - can't go higher!"

        if target_level not in self.levels:
            return None, None, f"Level {target_level} does not exist"

        # Change to target level
        self.current_level_number = target_level
        target_dungeon = self.levels[target_level].dungeon

        # Get destination room
        dest_room = target_dungeon.get_room(dest_room_id)
        if not dest_room:
            return None, None, f"Stairway destination {dest_room_id} not found on level {target_level}"

        level_name = self.levels[target_level].name
        return dest_room, target_level, f"You ascend the stairs to {level_name}"

    def _move_stairs_down(self, dest_room_id: str) -> Tuple[Optional[Room], Optional[int], Optional[str]]:
        """Move down stairs to next level"""
        target_level = self.current_level_number + 1

        if target_level not in self.levels:
            return None, None, f"Level {target_level} does not exist - the stairway may be blocked or collapsed"

        # Change to target level
        self.current_level_number = target_level
        target_dungeon = self.levels[target_level].dungeon

        # Get destination room
        dest_room = target_dungeon.get_room(dest_room_id)
        if not dest_room:
            return None, None, f"Stairway destination {dest_room_id} not found on level {target_level}"

        level_name = self.levels[target_level].name
        return dest_room, target_level, f"You descend the stairs to {level_name}"

    def get_total_rooms(self) -> int:
        """Get total number of rooms across all levels"""
        total = 0
        for level in self.levels.values():
            total += len(level.dungeon.rooms)
        return total

    def get_explored_rooms(self) -> int:
        """Get count of explored rooms across all levels"""
        total = 0
        for level in self.levels.values():
            total += len(level.dungeon.get_explored_rooms())
        return total

    def get_level_names(self) -> List[str]:
        """Get list of all level names in order"""
        return [
            self.levels[num].name
            for num in sorted(self.levels.keys())
        ]

    def to_dict(self) -> Dict:
        """
        Serialize multi-level dungeon to dictionary

        Returns:
            Dictionary with complete dungeon structure
        """
        return {
            "name": self.name,
            "description": self.description,
            "current_level": self.current_level_number,
            "levels": [
                {
                    "level_number": level.level_number,
                    "name": level.name,
                    "difficulty_tier": level.difficulty_tier,
                    "dungeon": level.dungeon.to_dict()
                }
                for level_number, level in sorted(self.levels.items())
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'MultiLevelDungeon':
        """
        Deserialize multi-level dungeon from dictionary

        Args:
            data: Dictionary from to_dict()

        Returns:
            MultiLevelDungeon instance
        """
        ml_dungeon = cls(name=data["name"])
        ml_dungeon.description = data.get("description", "")
        ml_dungeon.current_level_number = data.get("current_level", 1)

        for level_data in data["levels"]:
            dungeon = Dungeon.load_from_generator(level_data["dungeon"])
            ml_dungeon.add_level(
                level_number=level_data["level_number"],
                dungeon=dungeon,
                level_name=level_data["name"],
                difficulty_tier=level_data.get("difficulty_tier", level_data["level_number"])
            )

        return ml_dungeon

    def serialize(self) -> Dict:
        """Serialize for game save"""
        return {
            "name": self.name,
            "description": self.description,
            "current_level": self.current_level_number,
            "levels": {
                level_number: {
                    "level_number": level.level_number,
                    "name": level.name,
                    "difficulty_tier": level.difficulty_tier,
                    "dungeon_state": level.dungeon.serialize()
                }
                for level_number, level in self.levels.items()
            }
        }

    def get_stats(self) -> Dict:
        """Get dungeon statistics"""
        return {
            "name": self.name,
            "total_levels": len(self.levels),
            "current_level": self.current_level_number,
            "current_level_name": self.get_current_level().name if self.get_current_level() else "",
            "total_rooms": self.get_total_rooms(),
            "explored_rooms": self.get_explored_rooms(),
            "exploration_percentage": int((self.get_explored_rooms() / self.get_total_rooms() * 100)) if self.get_total_rooms() > 0 else 0
        }


# Convenience function for creating simple multi-level dungeons
def create_simple_multilevel(
    name: str,
    level_dungeons: List[Dungeon],
    level_names: Optional[List[str]] = None
) -> MultiLevelDungeon:
    """
    Create a simple multi-level dungeon from a list of dungeons

    Args:
        name: Overall dungeon name
        level_dungeons: List of Dungeon instances (in order from top to bottom)
        level_names: Optional list of level names

    Returns:
        MultiLevelDungeon instance
    """
    ml_dungeon = MultiLevelDungeon(name)

    for i, dungeon in enumerate(level_dungeons):
        level_number = i + 1
        level_name = level_names[i] if level_names and i < len(level_names) else f"Level {level_number}"
        ml_dungeon.add_level(level_number, dungeon, level_name)

    return ml_dungeon
