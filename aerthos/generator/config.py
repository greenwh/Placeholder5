"""
Dungeon Generator Configuration
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from .monster_scaling import MonsterScaler


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

    @classmethod
    def for_party(cls, party_level: int, party_size: int = 4, difficulty: str = 'standard', **kwargs):
        """
        Create a DungeonConfig automatically scaled for a party

        Args:
            party_level: Average party level
            party_size: Number of party members
            difficulty: 'easy', 'standard', or 'hard'
            **kwargs: Override any config parameters

        Returns:
            DungeonConfig instance with appropriate monster pool and settings
        """
        scaler = MonsterScaler()

        # Get appropriate monster pool
        monster_pool = scaler.get_monster_pool_for_party(party_level, party_size)

        # Get appropriate boss
        boss_monster = scaler.get_boss_for_party(party_level, party_size)

        # Set base parameters based on difficulty
        if difficulty == 'easy':
            base_config = {
                'num_rooms': 8,
                'layout_type': 'linear',
                'combat_frequency': 0.5,
                'trap_frequency': 0.1,
                'lethality_factor': 0.8,
                'treasure_level': 'low',
                'magic_item_chance': 0.05
            }
        elif difficulty == 'hard':
            base_config = {
                'num_rooms': 15,
                'layout_type': 'network',
                'combat_frequency': 0.6,
                'trap_frequency': 0.3,
                'empty_room_frequency': 0.1,
                'lethality_factor': 1.3,
                'treasure_level': 'high',
                'magic_item_chance': 0.15,
                'loops': 2
            }
        else:  # standard
            base_config = {
                'num_rooms': 12,
                'layout_type': 'branching',
                'combat_frequency': 0.6,
                'trap_frequency': 0.2,
                'lethality_factor': 1.0,
                'treasure_level': 'medium',
                'magic_item_chance': 0.1
            }

        # Merge with overrides
        config_params = {
            **base_config,
            'party_level': party_level,
            'monster_pool': monster_pool,
            'boss_monster': boss_monster,
            **kwargs
        }

        return cls(**config_params)

    @classmethod
    def from_interview(cls, interview_results: Dict, **kwargs):
        """
        Create DungeonConfig from interview results

        This method wraps for_party() to accept interview result format.
        Uses party analyzer insights to adjust encounter types and difficulty.

        Args:
            interview_results: Dict from DungeonInterview with keys:
                - apl: Average party level
                - party_size: Number of characters
                - composition: 'balanced', 'combat-heavy', 'magic-heavy', 'rogue-heavy'
                - magic_level: 'none', 'low', 'medium', 'high'
            **kwargs: Override any parameters

        Returns:
            DungeonConfig scaled to party via for_party()
        """

        # Extract interview data
        apl = int(interview_results.get('apl', 1))
        party_size = interview_results.get('party_size', 4)
        composition = interview_results.get('composition', 'balanced')
        magic_level = interview_results.get('magic_level', 'low')

        # Start with standard difficulty
        difficulty = 'standard'

        # Adjust encounter frequencies based on composition
        config_overrides = {}

        if composition == 'combat-heavy':
            # More combat, fewer traps (they can tank damage)
            config_overrides['combat_frequency'] = 0.7
            config_overrides['trap_frequency'] = 0.1
        elif composition == 'magic-heavy':
            # Fewer combats (conserve spells), standard traps
            config_overrides['combat_frequency'] = 0.5
            config_overrides['trap_frequency'] = 0.2
        elif composition == 'rogue-heavy':
            # More traps (they can handle them), moderate combat
            config_overrides['trap_frequency'] = 0.3
            config_overrides['combat_frequency'] = 0.5
        # Balanced uses defaults from for_party

        # Adjust lethality based on magic level and healing
        if magic_level in ['medium', 'high']:
            # Well-equipped party can handle more
            config_overrides['lethality_factor'] = 1.2
        elif magic_level == 'none':
            # Low-magic party needs easier encounters
            config_overrides['lethality_factor'] = 0.8

        # Merge with any explicit kwargs
        config_overrides.update(kwargs)

        # Call for_party() internally with adjusted params
        return cls.for_party(
            party_level=apl,
            party_size=party_size,
            difficulty=difficulty,
            **config_overrides
        )


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
    combat_frequency=0.6,
    trap_frequency=0.3,
    empty_room_frequency=0.1,
    party_level=2,
    lethality_factor=1.3,
    monster_pool=['goblin', 'orc', 'skeleton', 'ogre'],
    treasure_level='high',
    magic_item_chance=0.15,
    loops=2
)
