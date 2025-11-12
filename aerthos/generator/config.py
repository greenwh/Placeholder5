"""
Dungeon Generator Configuration
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DungeonConfig:
    """
    Configuration for procedural dungeon generation

    Controls all aspects of dungeon layout, difficulty, and content.
    Use seed for fixed/reproducible dungeons.
    """

    # Generation control
    seed: Optional[int] = None  # If set, generates same dungeon every time

    # Size parameters
    num_rooms: int = 10
    num_levels: int = 1

    # Layout style
    layout_type: str = 'branching'  # 'linear', 'branching', 'network'
    dead_ends: int = 2  # Number of dead-end branches
    loops: int = 0  # Number of loops/alternate paths (for 'network' style)

    # Encounter density (0.0 to 1.0)
    combat_frequency: float = 0.6  # 60% of rooms have combat
    trap_frequency: float = 0.2
    empty_room_frequency: float = 0.2

    # Difficulty
    party_level: int = 1
    lethality_factor: float = 1.0  # Multiplier for encounter difficulty

    # Monster selection
    monster_pool: List[str] = field(default_factory=lambda: [
        'kobold', 'goblin', 'giant_rat', 'skeleton'
    ])

    # Rewards
    treasure_frequency: float = 0.4
    treasure_level: str = 'low'  # 'low', 'medium', 'high'
    magic_item_chance: float = 0.1

    # Boss encounter
    include_boss: bool = True
    boss_monster: Optional[str] = None  # If None, auto-select based on party level

    # Rest areas
    safe_rooms: int = 2  # Number of safe rest rooms

    # Theme/flavor
    dungeon_theme: str = 'mine'  # 'mine', 'crypt', 'cave', 'ruins', 'sewer'

    # Item placement
    starting_items: List[str] = field(default_factory=lambda: ['torch'])
    guaranteed_items: List[str] = field(default_factory=list)  # Always include these

    def __post_init__(self):
        """Validate configuration"""
        if self.num_rooms < 3:
            raise ValueError("Must have at least 3 rooms")

        if self.combat_frequency + self.trap_frequency + self.empty_room_frequency > 1.0:
            raise ValueError("Encounter frequencies sum to more than 1.0")

        if self.layout_type not in ['linear', 'branching', 'network']:
            raise ValueError(f"Invalid layout_type: {self.layout_type}")

        if self.treasure_level not in ['low', 'medium', 'high']:
            raise ValueError(f"Invalid treasure_level: {self.treasure_level}")


# Preset configurations
EASY_DUNGEON = DungeonConfig(
    num_rooms=8,
    layout_type='linear',
    combat_frequency=0.5,
    trap_frequency=0.1,
    party_level=1,
    lethality_factor=0.8,
    monster_pool=['kobold', 'giant_rat'],
    treasure_level='low',
    magic_item_chance=0.05
)

STANDARD_DUNGEON = DungeonConfig(
    num_rooms=12,
    layout_type='branching',
    combat_frequency=0.6,
    trap_frequency=0.2,
    party_level=1,
    lethality_factor=1.0,
    monster_pool=['kobold', 'goblin', 'giant_rat', 'skeleton'],
    treasure_level='medium',
    magic_item_chance=0.1
)

HARD_DUNGEON = DungeonConfig(
    num_rooms=15,
    layout_type='network',
    combat_frequency=0.7,
    trap_frequency=0.3,
    party_level=2,
    lethality_factor=1.3,
    monster_pool=['goblin', 'orc', 'skeleton', 'ogre'],
    treasure_level='high',
    magic_item_chance=0.15,
    loops=2
)
