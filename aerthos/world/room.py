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

    def on_enter(self, has_light: bool, player=None) -> str:
        """
        Called when player enters room

        Args:
            has_light: Whether player has a light source
            player: Optional player reference for checking inventory

        Returns:
            Description text
        """

        self.is_explored = True

        # Check if player needs light
        if self.light_level == 'dark' and not has_light:
            return self._describe_darkness(player)

        return self._get_full_description()

    def _describe_darkness(self, player=None) -> str:
        """Return description for dark room without light"""

        msg = f"**{self.title}**\n\nIt is pitch black. You cannot see anything. You need a light source!"

        # Check if player has unlit torches/lanterns
        if player:
            from ..entities.player import LightSource
            has_light_items = any(isinstance(item, LightSource) for item in player.inventory.items)
            if has_light_items:
                msg += "\n\n💡 Hint: Type 'equip torch' to light a torch from your inventory."

        return msg

    def _get_full_description(self) -> str:
        """Get the full room description"""

        # Modify description if combat encounters are completed
        description = self._get_modified_description()

        desc = f"**{self.title}**\n\n{description}"

        # Add exits
        if self.exits:
            exit_list = ', '.join(self.exits.keys())
            desc += f"\n\nExits: {exit_list}"

        # Add visible items
        if self.items:
            item_list = ', '.join(self.items)
            desc += f"\n\nYou see: {item_list}"

        return desc

    def _get_modified_description(self) -> str:
        """Get room description modified for completed encounters"""

        # If there are completed encounters, modify description to reflect defeated monsters
        if not self.encounters_completed:
            return self.description

        # Check if any completed encounters look like combat encounters
        has_completed_combat = any('encounter' in enc_id for enc_id in self.encounters_completed)

        if not has_completed_combat:
            return self.description

        # Modify description to show defeated monsters instead of threatening ones
        modified = self.description

        # Common replacements for defeated monsters
        replacements = {
            # Monster activity -> defeated state
            'guards a pile': 'once guarded a pile',
            'guards the': 'once guarded the',
            'turn their empty eye sockets toward you and advance': 'lie scattered about, their bones still',
            'weapons raised': 'weapons scattered nearby',
            'does not look pleased to see you': 'lies dead on the ground',
            'advance': 'lie defeated',
            'charges': 'lies dead',
            'attacks': 'lies dead',

            # Specific boss/monster descriptions
            'an enormous OGRE guards': 'the corpse of a massive OGRE lies beside',
            'The beast is nine feet tall, with muscles like iron. This is the master of the mine, and it does not look pleased to see you!': 'The defeated beast lies in a pool of its own blood.',

            # Skeleton descriptions
            'They turn their empty eye sockets toward you and advance, weapons raised!': 'The shattered remains of skeletons lie scattered across the floor, their dark magic broken.',
        }

        # Apply replacements
        for old, new in replacements.items():
            if old in modified:
                modified = modified.replace(old, new)

        return modified

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
        """Check if room contains an item (exact match)"""
        return any(item.lower() == item_name.lower() for item in self.items)

    def find_item(self, search_term: str) -> Optional[str]:
        """
        Find an item by partial match

        Args:
            search_term: Partial item name to search for

        Returns:
            Full item name if found, None otherwise
        """
        search_lower = search_term.lower()

        # First try exact match
        for item in self.items:
            if item.lower() == search_lower:
                return item

        # Then try partial match (search term is in item name)
        for item in self.items:
            if search_lower in item.lower().replace('_', ' '):
                return item

        return None

    def mark_encounter_completed(self, encounter_id: str):
        """Mark an encounter as completed"""
        if encounter_id not in self.encounters_completed:
            self.encounters_completed.append(encounter_id)

    def is_encounter_completed(self, encounter_id: str) -> bool:
        """Check if an encounter has been completed"""
        return encounter_id in self.encounters_completed
