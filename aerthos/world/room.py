"""
Room class - represents a single location in the dungeon
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Room:
    """A single room in the dungeon"""

    id: str
    title: str
    description: str
    light_level: str = 'dark'  # 'bright', 'dim', 'dark'
    exits: Dict[str, str] = field(default_factory=dict)  # direction: room_id
    items: List[str] = field(default_factory=list)  # item names
    is_explored: bool = False
    is_safe_for_rest: bool = False

    # Encounter tracking
    encounters_completed: List[str] = field(default_factory=list)

    def on_enter(self, has_light: bool) -> str:
        """
        Called when player enters room

        Args:
            has_light: Whether player has a light source

        Returns:
            Description text
        """

        self.is_explored = True

        # Check if player needs light
        if self.light_level == 'dark' and not has_light:
            return self._describe_darkness()

        return self._get_full_description()

    def _describe_darkness(self) -> str:
        """Return description for dark room without light"""

        return f"**{self.title}**\n\nIt is pitch black. You cannot see anything. You need a light source!"

    def _get_full_description(self) -> str:
        """Get the full room description"""

        desc = f"**{self.title}**\n\n{self.description}"

        # Add exits
        if self.exits:
            exit_list = ', '.join(self.exits.keys())
            desc += f"\n\nExits: {exit_list}"

        # Add visible items
        if self.items:
            item_list = ', '.join(self.items)
            desc += f"\n\nYou see: {item_list}"

        return desc

    def has_exit(self, direction: str) -> bool:
        """Check if room has an exit in the given direction"""
        return direction in self.exits

    def get_exit(self, direction: str) -> Optional[str]:
        """Get the room ID for an exit direction"""
        return self.exits.get(direction)

    def add_item(self, item_name: str):
        """Add an item to the room"""
        if item_name not in self.items:
            self.items.append(item_name)

    def remove_item(self, item_name: str) -> bool:
        """Remove an item from the room, return True if successful"""
        if item_name in self.items:
            self.items.remove(item_name)
            return True
        return False

    def has_item(self, item_name: str) -> bool:
        """Check if room contains an item"""
        return any(item.lower() == item_name.lower() for item in self.items)

    def mark_encounter_completed(self, encounter_id: str):
        """Mark an encounter as completed"""
        if encounter_id not in self.encounters_completed:
            self.encounters_completed.append(encounter_id)

    def is_encounter_completed(self, encounter_id: str) -> bool:
        """Check if an encounter has been completed"""
        return encounter_id in self.encounters_completed
