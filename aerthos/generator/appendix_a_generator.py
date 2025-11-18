"""
Appendix A Dungeon Generator

Generates dungeons using authentic AD&D 1e procedural tables from DMG Appendix A.
Creates classic megadungeons with the feel of Gary Gygax's original method.
"""

import json
import random
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class DungeonRoom:
    """A room or chamber in the dungeon"""
    id: str
    room_type: str  # "chamber", "room", "passage"
    shape: str  # "square", "rectangular", "unusual"
    size: str  # "20x30", "10x10", etc.
    contents: str  # "empty", "monster", "treasure", etc.
    exits: Dict[str, str] = field(default_factory=dict)  # direction -> room_id
    doors: Dict[str, str] = field(default_factory=dict)  # direction -> door_type
    dressing: List[str] = field(default_factory=list)
    sounds: List[str] = field(default_factory=list)
    description: str = ""
    light_level: str = "dark"
    position: Tuple[int, int] = (0, 0)  # For mapping
    is_entrance: bool = False


class AppendixAGenerator:
    """
    AD&D 1e Appendix A Dungeon Generator

    Generates dungeons using the procedural tables from DMG pp. 169-173.
    This creates authentic "megadungeon" style layouts.
    """

    def __init__(self, tables_path: Optional[Path] = None):
        """
        Initialize generator with DMG tables

        Args:
            tables_path: Path to appendix_a_dungeon.json
        """
        if tables_path is None:
            base_dir = Path(__file__).parent.parent
            tables_path = base_dir / "data" / "dmg_tables" / "appendix_a_dungeon.json"

        with open(tables_path, 'r') as f:
            self.tables = json.load(f)

        self.rooms: Dict[str, DungeonRoom] = {}
        self.room_counter = 0
        self.current_level = 1

    def _roll_table(self, table_name: str, dice_type: str = "d20") -> Dict:
        """
        Roll on a DMG table

        Args:
            table_name: Name of table in self.tables
            dice_type: Type of die to roll

        Returns:
            Matching table entry
        """
        table = self.tables[table_name]["table"]

        # Roll appropriate die
        if dice_type == "d20":
            roll = random.randint(1, 20)
        elif dice_type == "d6":
            roll = random.randint(1, 6)
        elif dice_type == "d100":
            roll = random.randint(1, 100)
        else:
            roll = random.randint(1, 20)

        # Find matching entry
        for entry in table:
            roll_range = entry["roll"]

            # Handle ranges like "1-2", "11-13", etc.
            if '-' in roll_range:
                parts = roll_range.split('-')
                min_roll = int(parts[0])
                max_roll = int(parts[1])
                if min_roll <= roll <= max_roll:
                    return entry
            # Handle single values like "17", "20"
            elif roll == int(roll_range):
                return entry

        # Fallback - return first entry
        return table[0]

    def _generate_room_id(self) -> str:
        """Generate unique room ID"""
        self.room_counter += 1
        return f"room_{self.room_counter:03d}"

    def _roll_dice(self, formula: str) -> int:
        """Roll dice from formula like '1d4+2'"""
        # Handle simple numbers
        if formula.isdigit():
            return int(formula)

        # Handle dice formula
        match = re.match(r'(\d+)d(\d+)([+-]\d+)?', formula)
        if match:
            num_dice = int(match.group(1))
            die_size = int(match.group(2))
            modifier = int(match.group(3)) if match.group(3) else 0

            total = sum(random.randint(1, die_size) for _ in range(num_dice))
            return total + modifier

        return 1

    def _create_chamber(self, is_room: bool = False) -> DungeonRoom:
        """
        Create a chamber or room using size tables

        Args:
            is_room: If True, use room table; else use chamber table

        Returns:
            DungeonRoom instance
        """
        # Roll for size (chamber_size has special structure)
        roll = random.randint(1, 20)

        if is_room:
            size_table = self.tables["chamber_size"]["room_table"]
        else:
            size_table = self.tables["chamber_size"]["chamber_table"]

        # Find matching entry
        size_data = None
        for entry in size_table:
            roll_range = entry["roll"]
            if '-' in roll_range:
                min_r, max_r = map(int, roll_range.split('-'))
                if min_r <= roll <= max_r:
                    size_data = entry
                    break
            elif roll == int(roll_range):
                size_data = entry
                break

        if not size_data:
            size_data = size_table[0]  # Fallback

        # Roll for contents
        contents_data = self._roll_table("chamber_contents")

        # Roll for number of exits
        exit_data = self._roll_table("exit_count")
        num_exits = exit_data["exits"]
        if isinstance(num_exits, str):
            num_exits = self._roll_dice(num_exits)

        room = DungeonRoom(
            id=self._generate_room_id(),
            room_type="room" if is_room else "chamber",
            shape=size_data["shape"],
            size=size_data["size"],
            contents=contents_data["contents"]
        )

        # Add exits (will be connected later)
        for i in range(num_exits):
            exit_location = self._roll_table("exit_location")
            direction = exit_location["location"]

            # Convert location to compass direction
            compass_dir = self._location_to_direction(direction, i)
            room.exits[compass_dir] = None  # Will be filled in later

        # Add dressing
        room.dressing = self._add_dressing(room)
        room.sounds = self._add_sounds(room)

        return room

    def _location_to_direction(self, location: str, index: int) -> str:
        """Convert exit location to compass direction"""
        directions = ["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest"]

        if location == "opposite_wall":
            return directions[0]  # Default to north for opposite
        elif location == "left_wall":
            return "west" if index == 0 else "northwest"
        elif location == "right_wall":
            return "east" if index == 0 else "southeast"
        elif location == "same_wall":
            return "south"

        # Distribute remaining exits
        return directions[index % len(directions)]

    def _add_dressing(self, room: DungeonRoom) -> List[str]:
        """Add atmospheric dressing to room"""
        if room.contents != "empty":
            # Don't add dressing to occupied rooms
            return []

        dressing_items = []

        # Roll for 1-3 dressing items
        num_items = random.randint(1, 3)

        for _ in range(num_items):
            category = random.choice(["general", "furnishings", "container_contents"])
            items = self.tables["dungeon_dressing"][category]
            dressing_items.append(random.choice(items))

        return dressing_items

    def _add_sounds(self, room: DungeonRoom) -> List[str]:
        """Add unexplained sounds to room"""
        # 30% chance of sounds in any room
        if random.random() > 0.3:
            return []

        sounds = self.tables["dungeon_dressing"]["unexplained_sounds"]
        return [random.choice(sounds)]

    def _create_door(self) -> str:
        """Generate door type"""
        door_data = self._roll_table("door_type")
        return door_data["type"]

    def generate_dungeon(
        self,
        target_rooms: int = 12,
        dungeon_name: str = "Procedural Dungeon",
        start_level: int = 1
    ) -> Dict:
        """
        Generate a complete dungeon using Appendix A tables

        Args:
            target_rooms: Approximate number of rooms to generate
            dungeon_name: Name of the dungeon
            start_level: Starting dungeon level

        Returns:
            Dictionary with dungeon data
        """
        self.rooms = {}
        self.room_counter = 0
        self.current_level = start_level

        # Create entrance
        entrance = self._create_chamber(is_room=True)
        entrance.id = "entrance"
        entrance.is_entrance = True
        entrance.contents = "empty"  # Entrance is always safe
        entrance.description = "The entrance to the dungeon. A passage leads deeper into the darkness."
        self.rooms[entrance.id] = entrance

        # Track rooms to expand
        rooms_to_expand = [entrance]
        rooms_created = 1

        # Generate dungeon by expanding from entrance
        while rooms_to_expand and rooms_created < target_rooms:
            current_room = rooms_to_expand.pop(0)

            # For each exit in current room
            for direction, connection in list(current_room.exits.items()):
                if connection is not None:
                    continue  # Already connected

                if rooms_created >= target_rooms:
                    # Dead end
                    current_room.exits[direction] = "dead_end"
                    continue

                # Roll periodic check to see what's beyond
                check_result = self._roll_table("periodic_check")
                result_type = check_result["result"]

                if result_type == "continue":
                    # Passage continues - could add passage rooms here
                    current_room.exits[direction] = "passage"

                elif result_type == "door":
                    # Door - check what's beyond
                    door_type = self._create_door()
                    current_room.doors[direction] = door_type

                    beyond = self._roll_table("door_space_beyond")

                    if beyond["result"] in ["room", "chamber"]:
                        # Create new room
                        new_room = self._create_chamber(is_room=(beyond["result"] == "room"))
                        self.rooms[new_room.id] = new_room
                        rooms_to_expand.append(new_room)

                        # Connect rooms
                        current_room.exits[direction] = new_room.id
                        opposite_dir = self._opposite_direction(direction)
                        new_room.exits[opposite_dir] = current_room.id
                        new_room.doors[opposite_dir] = door_type

                        rooms_created += 1

                elif result_type == "chamber":
                    # Chamber directly
                    new_chamber = self._create_chamber(is_room=False)
                    self.rooms[new_chamber.id] = new_chamber
                    rooms_to_expand.append(new_chamber)

                    current_room.exits[direction] = new_chamber.id
                    opposite_dir = self._opposite_direction(direction)
                    new_chamber.exits[opposite_dir] = current_room.id

                    rooms_created += 1

                elif result_type == "stairs":
                    # Stairs (future: connect to other levels)
                    stairs_type = self._roll_table("stairs")
                    current_room.exits[direction] = f"stairs_{stairs_type['type']}"

                elif result_type == "dead_end":
                    current_room.exits[direction] = "dead_end"

                elif result_type == "trick_trap":
                    # Add trap to current room or passage
                    trap_data = self._roll_table("trick_trap")
                    current_room.contents = "trick_trap"
                    current_room.description = f"Trap: {trap_data['description']}"

        # Generate descriptions for all rooms
        self._generate_room_descriptions()

        # Convert to format compatible with existing dungeon system
        dungeon_dict = {
            "name": dungeon_name,
            "description": f"A {target_rooms}-room dungeon generated using AD&D Appendix A tables",
            "dungeon_level": start_level,
            "start_room": "entrance",
            "rooms": {}
        }

        for room_id, room in self.rooms.items():
            dungeon_dict["rooms"][room_id] = {
                "id": room_id,
                "title": self._generate_room_title(room),
                "description": room.description,
                "size": room.size,
                "shape": room.shape,
                "contents": room.contents,
                "exits": {k: v for k, v in room.exits.items() if v not in ["dead_end", "passage"]},
                "doors": room.doors,
                "light_level": room.light_level,
                "dressing": room.dressing,
                "sounds": room.sounds,
                "safe_rest": (room.contents == "empty" and not room.sounds),
                "is_entrance": room.is_entrance
            }

        return dungeon_dict

    def _opposite_direction(self, direction: str) -> str:
        """Get opposite compass direction"""
        opposites = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east",
            "northeast": "southwest",
            "southwest": "northeast",
            "northwest": "southeast",
            "southeast": "northwest"
        }
        return opposites.get(direction, "south")

    def _generate_room_title(self, room: DungeonRoom) -> str:
        """Generate a title for the room"""
        if room.is_entrance:
            return "Dungeon Entrance"

        titles = {
            "empty": ["Empty Chamber", "Vacant Hall", "Abandoned Room", "Barren Chamber"],
            "monster": ["Inhabited Chamber", "Lair", "Guard Room", "Den"],
            "monster_treasure": ["Treasure Vault", "Hoard Chamber", "Guarded Treasury"],
            "treasure": ["Hidden Cache", "Treasury", "Vault"],
            "special": ["Strange Chamber", "Unique Room", "Special Area"],
            "trick_trap": ["Trapped Passage", "Dangerous Room", "Hazardous Chamber"]
        }

        title_options = titles.get(room.contents, ["Chamber"])
        return random.choice(title_options)

    def _generate_room_descriptions(self):
        """Generate narrative descriptions for all rooms"""
        for room in self.rooms.values():
            if room.description:
                continue  # Already has description

            parts = []

            # Size and shape
            parts.append(f"This {room.size} {room.shape} {room.room_type}")

            # Contents
            if room.contents == "empty":
                parts.append("appears to be empty")
                if room.dressing:
                    dressing_str = ", ".join(room.dressing[:2])
                    parts.append(f"You see {dressing_str}")
            elif room.contents == "monster":
                parts.append("is inhabited by hostile creatures")
            elif room.contents == "monster_treasure":
                parts.append("contains both monsters and treasure")
            elif room.contents == "treasure":
                parts.append("appears to contain hidden treasure")
            elif room.contents == "special":
                parts.append("has something unusual about it")

            # Sounds
            if room.sounds:
                sound = room.sounds[0]
                parts.append(f"You hear {sound}")

            # Exits
            exit_count = len([e for e in room.exits.values() if e not in ["dead_end", "passage"]])
            if exit_count == 0:
                parts.append("This appears to be a dead end")
            elif exit_count == 1:
                parts.append("There is one obvious exit")
            else:
                parts.append(f"There are {exit_count} visible exits")

            room.description = ". ".join(parts) + "."


# Convenience function
def generate_appendix_a_dungeon(
    num_rooms: int = 12,
    dungeon_name: str = "The Unknown Depths",
    dungeon_level: int = 1
) -> Dict:
    """
    Generate a dungeon using Appendix A tables

    Args:
        num_rooms: Target number of rooms
        dungeon_name: Name for the dungeon
        dungeon_level: Dungeon level (1-10)

    Returns:
        Dungeon dictionary compatible with game engine
    """
    generator = AppendixAGenerator()
    return generator.generate_dungeon(num_rooms, dungeon_name, dungeon_level)


if __name__ == "__main__":
    # Test generation
    print("="*70)
    print("AD&D APPENDIX A DUNGEON GENERATOR TEST")
    print("="*70)

    dungeon = generate_appendix_a_dungeon(num_rooms=8, dungeon_name="Test Dungeon")

    print(f"\nGenerated: {dungeon['name']}")
    print(f"Description: {dungeon['description']}")
    print(f"Start Room: {dungeon['start_room']}")
    print(f"Total Rooms: {len(dungeon['rooms'])}")

    print("\nRoom Summary:")
    print("-" * 70)
    for room_id, room_data in list(dungeon['rooms'].items())[:5]:  # Show first 5 rooms
        print(f"\n{room_data['title']} ({room_id})")
        print(f"  Size: {room_data['size']} {room_data['shape']}")
        print(f"  Contents: {room_data['contents']}")
        print(f"  Exits: {', '.join(room_data['exits'].keys())}")
        if room_data['dressing']:
            print(f"  Dressing: {', '.join(room_data['dressing'][:3])}")
        print(f"  {room_data['description']}")

    print("\n" + "="*70)
    print(f"Dungeon generation complete! {len(dungeon['rooms'])} rooms created.")
    print("="*70)
