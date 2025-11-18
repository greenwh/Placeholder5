"""
Multi-Level Dungeon Generator

Generates multi-level dungeons using the Appendix A generator for each level,
then connects them with stairs. Implements classic megadungeon architecture
where difficulty and rewards scale with depth.
"""

import random
import sys
from typing import Dict, List, Optional
from pathlib import Path

# Handle both package import and standalone execution
try:
    from .appendix_a_generator import AppendixAGenerator
    from ..world.dungeon import Dungeon
    from ..world.multilevel_dungeon import MultiLevelDungeon
except ImportError:
    # Standalone execution
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from aerthos.generator.appendix_a_generator import AppendixAGenerator
    from aerthos.world.dungeon import Dungeon
    from aerthos.world.multilevel_dungeon import MultiLevelDungeon


class MultiLevelGenerator:
    """
    Generates multi-level dungeons with stairs connecting levels

    Features:
    - Each level generated using Appendix A tables
    - Automatic stair placement
    - Difficulty scaling by depth
    - Thematic level naming
    """

    def __init__(self):
        """Initialize multi-level generator"""
        self.generator = AppendixAGenerator()

    def generate(
        self,
        num_levels: int = 3,
        rooms_per_level: int = 10,
        dungeon_name: str = "The Unknown Depths",
        level_names: Optional[List[str]] = None,
        stairs_per_level: int = 2
    ) -> MultiLevelDungeon:
        """
        Generate a multi-level dungeon

        Args:
            num_levels: Number of levels (1-10)
            rooms_per_level: Approximate rooms per level
            dungeon_name: Overall dungeon name
            level_names: Optional list of level names (one per level)
            stairs_per_level: Number of stairways connecting each level pair

        Returns:
            MultiLevelDungeon instance
        """
        ml_dungeon = MultiLevelDungeon(name=dungeon_name)

        # Generate each level
        for level_num in range(1, num_levels + 1):
            # Determine level name
            if level_names and level_num - 1 < len(level_names):
                level_name = level_names[level_num - 1]
            else:
                level_name = self._generate_level_name(level_num, num_levels)

            # Generate the level using Appendix A
            # Note: Appendix A generator creates sparse dungeons (authentic DMG style)
            # Request 3x target to get approximately the desired number of rooms
            level_dict = self.generator.generate_dungeon(
                target_rooms=rooms_per_level * 3,
                dungeon_name=f"{dungeon_name} - {level_name}",
                start_level=level_num
            )

            # Convert to Dungeon instance
            dungeon = Dungeon.load_from_generator(level_dict)

            # Add to multi-level dungeon
            ml_dungeon.add_level(
                level_number=level_num,
                dungeon=dungeon,
                level_name=level_name,
                difficulty_tier=min(level_num, 4)
            )

        # Connect levels with stairs
        if num_levels > 1:
            self._connect_levels_with_stairs(ml_dungeon, stairs_per_level)

        return ml_dungeon

    def _generate_level_name(self, level_num: int, total_levels: int) -> str:
        """
        Generate a thematic name for a dungeon level

        Args:
            level_num: Current level number (1-based)
            total_levels: Total number of levels

        Returns:
            Level name
        """
        # Depth-based themes
        if level_num == 1:
            themes = [
                "The Entrance Hall",
                "The Upper Chambers",
                "The Gatehouse",
                "The Antechamber"
            ]
        elif level_num == 2:
            themes = [
                "The Warrens",
                "The Crypt",
                "The Guardrooms",
                "The Barracks"
            ]
        elif level_num == 3:
            themes = [
                "The Forgotten Halls",
                "The Dark Passages",
                "The Ancient Tombs",
                "The Vaults"
            ]
        elif level_num == 4:
            themes = [
                "The Deep Caverns",
                "The Nethervaults",
                "The Sunless Depths",
                "The Black Halls"
            ]
        elif level_num >= 5:
            themes = [
                f"The Abyss (Level {level_num})",
                f"The Deepest Dark (Level {level_num})",
                f"The Sunken Realm (Level {level_num})",
                f"The Endless Below (Level {level_num})"
            ]
        else:
            return f"Level {level_num}"

        return random.choice(themes)

    def _connect_levels_with_stairs(
        self,
        ml_dungeon: MultiLevelDungeon,
        stairs_per_level: int = 2
    ):
        """
        Connect dungeon levels with stairs

        Args:
            ml_dungeon: MultiLevelDungeon to modify
            stairs_per_level: Number of stair connections per level pair
        """
        level_numbers = sorted(ml_dungeon.levels.keys())

        for i in range(len(level_numbers) - 1):
            current_level_num = level_numbers[i]
            next_level_num = level_numbers[i + 1]

            current_level = ml_dungeon.levels[current_level_num]
            next_level = ml_dungeon.levels[next_level_num]

            # Create stair connections
            for _ in range(stairs_per_level):
                self._create_stair_connection(
                    current_level.dungeon,
                    next_level.dungeon,
                    current_level_num,
                    next_level_num
                )

    def _create_stair_connection(
        self,
        upper_dungeon: Dungeon,
        lower_dungeon: Dungeon,
        upper_level_num: int,
        lower_level_num: int
    ):
        """
        Create a pair of stairs connecting two levels

        Args:
            upper_dungeon: Upper level dungeon
            lower_dungeon: Lower level dungeon
            upper_level_num: Upper level number
            lower_level_num: Lower level number
        """
        # Pick random rooms (prefer non-entrance, but use entrance if necessary)
        upper_rooms = [
            room for room in upper_dungeon.rooms.values()
            if room.id != upper_dungeon.start_room_id
        ]
        lower_rooms = [
            room for room in lower_dungeon.rooms.values()
            if room.id != lower_dungeon.start_room_id
        ]

        # If no non-entrance rooms, use any available room (including entrance)
        if not upper_rooms:
            upper_rooms = list(upper_dungeon.rooms.values())
        if not lower_rooms:
            lower_rooms = list(lower_dungeon.rooms.values())

        if not upper_rooms or not lower_rooms:
            return  # Can't create stairs without any rooms at all

        upper_room = random.choice(upper_rooms)
        lower_room = random.choice(lower_rooms)

        # Add stairs down in upper level
        upper_room.exits["stairs_down"] = lower_room.id
        upper_room.exits["down"] = lower_room.id  # Alias
        upper_room.exits["d"] = lower_room.id  # Short alias

        # Add stairs up in lower level
        lower_room.exits["stairs_up"] = upper_room.id
        lower_room.exits["up"] = upper_room.id  # Alias
        lower_room.exits["u"] = upper_room.id  # Short alias

        # Update room descriptions to mention stairs
        if "stairs" not in upper_room.description.lower():
            upper_room.description += f" Stone stairs descend into the darkness below."

        if "stairs" not in lower_room.description.lower():
            lower_room.description += f" Stone stairs ascend to the level above."

    def generate_to_dict(
        self,
        num_levels: int = 3,
        rooms_per_level: int = 10,
        dungeon_name: str = "The Unknown Depths",
        level_names: Optional[List[str]] = None,
        stairs_per_level: int = 2
    ) -> Dict:
        """
        Generate multi-level dungeon and return as dictionary

        Args:
            num_levels: Number of levels
            rooms_per_level: Rooms per level
            dungeon_name: Dungeon name
            level_names: Optional level names
            stairs_per_level: Stairs per level

        Returns:
            Dictionary representation
        """
        ml_dungeon = self.generate(
            num_levels=num_levels,
            rooms_per_level=rooms_per_level,
            dungeon_name=dungeon_name,
            level_names=level_names,
            stairs_per_level=stairs_per_level
        )

        return ml_dungeon.to_dict()


# Convenience function
def generate_multilevel_dungeon(
    num_levels: int = 3,
    rooms_per_level: int = 10,
    dungeon_name: str = "The Unknown Depths",
    level_names: Optional[List[str]] = None,
    stairs_per_level: int = 2
) -> Dict:
    """
    Generate a multi-level dungeon

    Args:
        num_levels: Number of levels (1-10)
        rooms_per_level: Approximate rooms per level
        dungeon_name: Overall dungeon name
        level_names: Optional list of level names
        stairs_per_level: Number of stairways per level

    Returns:
        Dictionary representation of multi-level dungeon
    """
    generator = MultiLevelGenerator()
    return generator.generate_to_dict(
        num_levels=num_levels,
        rooms_per_level=rooms_per_level,
        dungeon_name=dungeon_name,
        level_names=level_names,
        stairs_per_level=stairs_per_level
    )


if __name__ == "__main__":
    # Test multi-level generation
    print("="*70)
    print("MULTI-LEVEL DUNGEON GENERATOR TEST")
    print("="*70)

    generator = MultiLevelGenerator()

    # Test 1: Simple 3-level dungeon
    print("\n1. Generating 3-level dungeon with 8 rooms per level...")
    ml_dungeon = generator.generate(
        num_levels=3,
        rooms_per_level=8,
        dungeon_name="The Abandoned Fortress"
    )

    stats = ml_dungeon.get_stats()
    print(f"\nDungeon: {stats['name']}")
    print(f"Total Levels: {stats['total_levels']}")
    print(f"Total Rooms: {stats['total_rooms']}")
    print(f"\nLevel Names:")
    for name in ml_dungeon.get_level_names():
        print(f"  - {name}")

    # Test 2: Check stair connections
    print("\n2. Verifying stair connections...")
    for level_num in sorted(ml_dungeon.levels.keys()):
        level = ml_dungeon.levels[level_num]
        dungeon = level.dungeon

        stairs_down = 0
        stairs_up = 0

        for room in dungeon.rooms.values():
            if "stairs_down" in room.exits or "down" in room.exits:
                stairs_down += 1
            if "stairs_up" in room.exits or "up" in room.exits:
                stairs_up += 1

        print(f"\n{level.name} (Level {level_num}):")
        print(f"  Rooms: {len(dungeon.rooms)}")
        print(f"  Stairs Down: {stairs_down}")
        print(f"  Stairs Up: {stairs_up}")

    # Test 3: Navigation test
    print("\n3. Testing vertical navigation...")
    current_level = 1
    current_room_id = ml_dungeon.levels[1].dungeon.start_room_id

    print(f"Starting at: Level {current_level}, Room {current_room_id}")

    # Try to find stairs down
    current_dungeon = ml_dungeon.levels[current_level].dungeon
    for room in current_dungeon.rooms.values():
        if "stairs_down" in room.exits:
            print(f"\nFound stairs down in room {room.id}")
            next_room, next_level, message = ml_dungeon.move(room.id, "stairs_down")
            if next_room:
                print(f"Success! {message}")
                print(f"Now at: Level {next_level}, Room {next_room.id}")
            break

    # Test 4: Serialize/deserialize
    print("\n4. Testing serialization...")
    ml_dict = ml_dungeon.to_dict()
    print(f"Serialized to dict with {len(ml_dict['levels'])} levels")

    ml_dungeon2 = MultiLevelDungeon.from_dict(ml_dict)
    print(f"Deserialized successfully: {ml_dungeon2.name}")
    print(f"Levels match: {len(ml_dungeon2.levels) == len(ml_dungeon.levels)}")

    print("\n" + "="*70)
    print("Multi-level dungeon generation test complete!")
    print("="*70)
