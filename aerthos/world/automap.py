"""
Auto-mapping system - generates ASCII map as player explores
"""

from typing import Dict, Set, Tuple, List, Union, TYPE_CHECKING
from .dungeon import Dungeon
from .room import Room

if TYPE_CHECKING:
    from .multilevel_dungeon import MultiLevelDungeon


class AutoMap:
    """
    Generates ASCII map of explored areas

    Example output:
        [ ]
         |
    [ ]-[X]-[ ]
         |
        [ ]

    X = current position
    [ ] = explored room
    """

    def __init__(self):
        self.room_positions: Dict[str, Tuple[int, int]] = {}
        self.position_calculated = False
        self.cached_level: int = 1  # Track which level is cached

    def generate_map(self, current_room_id: str, dungeon: Union[Dungeon, "MultiLevelDungeon"],
                     current_level: int = 1) -> str:
        """
        Generate ASCII map showing explored areas

        Args:
            current_room_id: Current room ID
            dungeon: Dungeon or MultiLevelDungeon instance
            current_level: Current level number (for multi-level dungeons)

        Returns:
            ASCII map string
        """

        # Handle multi-level dungeons - show only current level
        level_header = ""
        actual_dungeon = dungeon

        # Check if it's a MultiLevelDungeon by checking for get_current_dungeon method
        if hasattr(dungeon, 'get_current_dungeon'):
            # Multi-level dungeon
            actual_dungeon = dungeon.get_current_dungeon()
            level_header = f"Level {dungeon.current_level_number} of {dungeon.num_levels}\n"

            # Clear cache if level changed
            if dungeon.current_level_number != self.cached_level:
                self.position_calculated = False
                self.room_positions = {}
                self.cached_level = dungeon.current_level_number

        # Build coordinate system if not already done
        if not self.position_calculated:
            self._calculate_positions(actual_dungeon)
            self.position_calculated = True

        # Build grid of explored rooms
        grid = self._build_grid(current_room_id, actual_dungeon)

        if not grid:
            return "No map data available yet. Explore to reveal the map."

        # Render to ASCII
        map_display = self._render_ascii(grid, current_room_id, actual_dungeon)

        # Add level header for multi-level dungeons
        if level_header:
            return level_header + map_display
        return map_display

    def _calculate_positions(self, dungeon: Dungeon):
        """
        Calculate (x, y) coordinates for all rooms

        Args:
            dungeon: Dungeon instance
        """

        start_room = dungeon.get_start_room()
        visited = set()
        self._assign_position(start_room, 0, 0, dungeon, visited)

    def _assign_position(self, room: Room, x: int, y: int,
                        dungeon: Dungeon, visited: Set[str]):
        """
        Recursively assign positions to connected rooms

        Args:
            room: Current room
            x: X coordinate
            y: Y coordinate (north = negative, south = positive)
            dungeon: Dungeon instance
            visited: Set of visited room IDs
        """

        # If room already has position, don't override it
        if room.id in self.room_positions:
            return

        if room.id in visited:
            return

        visited.add(room.id)
        self.room_positions[room.id] = (x, y)

        # Direction offsets (north is up = negative y)
        direction_offsets = {
            'north': (0, -1),   # Up
            'south': (0, 1),    # Down
            'east': (1, 0),     # Right
            'west': (-1, 0),    # Left
            'up': (0, 0),       # Same position (different level)
            'down': (0, 0)      # Same position (different level)
        }

        # Assign connected rooms
        for direction, next_room_id in room.exits.items():
            next_room = dungeon.get_room(next_room_id)
            if next_room and next_room_id not in self.room_positions:
                dx, dy = direction_offsets.get(direction, (0, 0))
                target_pos = (x + dx, y + dy)

                # Check if position is already occupied
                occupied = any(pos == target_pos for pos in self.room_positions.values())

                if not occupied:
                    self._assign_position(next_room, x + dx, y + dy, dungeon, visited)
                else:
                    # If position occupied, try to place in nearest free spot
                    for offset in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
                        alt_pos = (target_pos[0] + offset[0], target_pos[1] + offset[1])
                        if not any(pos == alt_pos for pos in self.room_positions.values()):
                            self._assign_position(next_room, alt_pos[0], alt_pos[1], dungeon, visited)
                            break

    def _build_grid(self, current_room_id: str,
                   dungeon: Dungeon) -> Dict[Tuple[int, int], str]:
        """
        Build grid of explored rooms

        Args:
            current_room_id: Current room ID
            dungeon: Dungeon instance

        Returns:
            Dict mapping (x, y) to room_id
        """

        grid = {}
        explored_rooms = dungeon.get_explored_rooms()

        for room in explored_rooms:
            if room.id in self.room_positions:
                pos = self.room_positions[room.id]
                grid[pos] = room.id

        return grid

    def _render_ascii(self, grid: Dict[Tuple[int, int], str],
                     current_room_id: str, dungeon: Dungeon) -> str:
        """
        Render grid to ASCII art

        Args:
            grid: Grid mapping positions to room IDs
            current_room_id: Current room ID
            dungeon: Dungeon instance

        Returns:
            ASCII map string
        """

        if not grid:
            return "Map is empty."

        # Find bounds
        xs = [pos[0] for pos in grid.keys()]
        ys = [pos[1] for pos in grid.keys()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # Build ASCII representation
        lines = []

        for y in range(min_y, max_y + 1):
            # Room line
            room_line = ""
            for x in range(min_x, max_x + 1):
                if (x, y) in grid:
                    room_id = grid[(x, y)]
                    if room_id == current_room_id:
                        room_line += "[X]"  # Current position
                    else:
                        room_line += "[ ]"  # Explored room
                else:
                    room_line += "   "  # Empty space

                # Add horizontal connector
                if x < max_x:
                    if (x, y) in grid and (x + 1, y) in grid:
                        # Check if rooms are connected
                        room = dungeon.get_room(grid[(x, y)])
                        if room and room.has_exit('east'):
                            room_line += "─"
                        else:
                            room_line += " "
                    else:
                        room_line += " "

            lines.append(room_line)

            # Add vertical connectors
            if y < max_y:
                connector_line = ""
                for x in range(min_x, max_x + 1):
                    if (x, y) in grid and (x, y + 1) in grid:
                        # Check if rooms are connected
                        room = dungeon.get_room(grid[(x, y)])
                        if room and room.has_exit('south'):
                            connector_line += " │ "
                        else:
                            connector_line += "   "
                    else:
                        connector_line += "   "

                    if x < max_x:
                        connector_line += " "

                lines.append(connector_line)

        map_str = "\n".join(lines)
        return f"\n═══ AUTO-MAP ═══\n         N\n         ↑\n     W ← · → E\n         ↓\n         S\n\n{map_str}\n\n[X] = Your Location\n[ ] = Explored Room\n"
