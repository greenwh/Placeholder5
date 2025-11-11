"""
Auto-mapping system - generates ASCII map as player explores
"""

from typing import Dict, Set, Tuple, List
from .dungeon import Dungeon
from .room import Room


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

    def generate_map(self, current_room_id: str, dungeon: Dungeon) -> str:
        """
        Generate ASCII map showing explored areas

        Args:
            current_room_id: Current room ID
            dungeon: Dungeon instance

        Returns:
            ASCII map string
        """

        # Build coordinate system if not already done
        if not self.position_calculated:
            self._calculate_positions(dungeon)
            self.position_calculated = True

        # Build grid of explored rooms
        grid = self._build_grid(current_room_id, dungeon)

        if not grid:
            return "No map data available yet. Explore to reveal the map."

        # Render to ASCII
        return self._render_ascii(grid, current_room_id, dungeon)

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
            y: Y coordinate
            dungeon: Dungeon instance
            visited: Set of visited room IDs
        """

        if room.id in visited:
            return

        visited.add(room.id)
        self.room_positions[room.id] = (x, y)

        # Direction offsets
        direction_offsets = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0),
            'up': (0, 0),      # Show in same position
            'down': (0, 0)     # Show in same position
        }

        # Assign connected rooms
        for direction, next_room_id in room.exits.items():
            next_room = dungeon.get_room(next_room_id)
            if next_room:
                dx, dy = direction_offsets.get(direction, (0, 0))
                # Check if position already assigned (avoid overlaps)
                target_pos = (x + dx, y + dy)
                if target_pos not in [pos for pos in self.room_positions.values()]:
                    self._assign_position(next_room, x + dx, y + dy, dungeon, visited)

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
        return f"\n═══ AUTO-MAP ═══\n\n{map_str}\n\n[X] = Your Location\n[ ] = Explored Room\n"
