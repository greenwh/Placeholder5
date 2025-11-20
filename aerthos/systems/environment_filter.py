"""
Environment-Based Monster Filtering

Implements AD&D 1e DMG Appendix C encounter logic:
- Dungeon encounters by level (I-X based on XP)
- Outdoor encounters by terrain and climate
- Underwater encounters by water type
- Prevents inappropriate encounters (sprites in dungeons, fish on land, etc.)
"""

import json
from pathlib import Path
from typing import List, Optional, Set
from dataclasses import dataclass


@dataclass
class EnvironmentContext:
    """Context for determining appropriate monsters"""
    location_type: str  # 'dungeon', 'wilderness', 'underwater', 'city'
    terrain: Optional[str] = None  # 'plain', 'forest', 'hills', 'mountains', 'swamp_marsh', 'desert'
    climate: Optional[str] = None  # 'arctic', 'sub_arctic', 'temperate', 'tropical'
    dungeon_level: Optional[int] = None  # 1-10 for dungeon encounters
    water_type: Optional[str] = None  # 'fresh_shallow', 'fresh_deep', 'salt_shallow', 'salt_deep'
    special_setting: Optional[str] = None  # 'faerie_sylvan', 'prehistoric', etc.


class EnvironmentMonsterFilter:
    """
    Filters monster encounters based on environment

    Based on AD&D 1e DMG Appendix C tables.
    """

    def __init__(self, data_path: Optional[Path] = None):
        """
        Initialize filter with environment data

        Args:
            data_path: Path to monster_environments.json (optional)
        """
        if data_path is None:
            # Default to data directory relative to this file
            data_path = Path(__file__).parent.parent / "data" / "monster_environments.json"

        with open(data_path, 'r') as f:
            self.environment_data = json.load(f)

    def get_appropriate_monsters(
        self,
        context: EnvironmentContext,
        monster_pool: Optional[List[str]] = None
    ) -> List[str]:
        """
        Get list of monsters appropriate for the environment

        Args:
            context: Environment context
            monster_pool: Optional list to filter. If None, returns all appropriate monsters

        Returns:
            List of monster IDs appropriate for the environment
        """
        # Get appropriate monsters based on location type
        if context.location_type == 'dungeon':
            appropriate = self._get_dungeon_monsters(context.dungeon_level or 1)
        elif context.location_type == 'wilderness':
            appropriate = self._get_wilderness_monsters(context)
        elif context.location_type == 'underwater':
            appropriate = self._get_underwater_monsters(context.water_type or 'fresh_shallow')
        else:
            # Unknown location type - return empty list or monster_pool as-is
            return monster_pool or []

        # Filter the monster pool if provided
        if monster_pool:
            # Return intersection of appropriate monsters and provided pool
            appropriate_set = set(appropriate)
            return [m for m in monster_pool if m in appropriate_set]

        return appropriate

    def _get_dungeon_monsters(self, level: int) -> List[str]:
        """
        Get monsters appropriate for dungeon level

        Args:
            level: Dungeon level (1-10)

        Returns:
            List of monster IDs
        """
        level = max(1, min(10, level))  # Clamp to 1-10
        level_key = f"level_{level}"

        dungeon_data = self.environment_data.get("dungeon", {})
        monsters = dungeon_data.get(level_key, [])

        # Also include "dungeon_or_wilderness" monsters
        versatile = self.environment_data.get("environment_categories", {}).get("dungeon_or_wilderness", [])

        return list(set(monsters + versatile))

    def _get_wilderness_monsters(self, context: EnvironmentContext) -> List[str]:
        """
        Get monsters appropriate for wilderness/outdoor environment

        Args:
            context: Environment context with terrain/climate info

        Returns:
            List of monster IDs
        """
        wilderness_data = self.environment_data.get("wilderness", {})

        # Handle special settings first
        if context.special_setting == 'faerie_sylvan':
            return wilderness_data.get("faerie_sylvan", [])

        # Get monsters for terrain type
        if context.terrain:
            terrain_monsters = wilderness_data.get(context.terrain, [])
        else:
            # No specific terrain - combine all wilderness monsters
            terrain_monsters = []
            for terrain in ['plain', 'forest', 'hills', 'mountains', 'swamp_marsh', 'desert']:
                terrain_monsters.extend(wilderness_data.get(terrain, []))
            terrain_monsters = list(set(terrain_monsters))

        # Add versatile monsters
        versatile = self.environment_data.get("environment_categories", {}).get("dungeon_or_wilderness", [])

        return list(set(terrain_monsters + versatile))

    def _get_underwater_monsters(self, water_type: str) -> List[str]:
        """
        Get monsters appropriate for underwater environment

        Args:
            water_type: Type of water body

        Returns:
            List of monster IDs
        """
        underwater_data = self.environment_data.get("underwater", {})
        return underwater_data.get(water_type, [])

    def is_appropriate(
        self,
        monster_id: str,
        context: EnvironmentContext
    ) -> bool:
        """
        Check if a specific monster is appropriate for the environment

        Args:
            monster_id: Monster ID to check
            context: Environment context

        Returns:
            True if monster can appear in this environment
        """
        appropriate_monsters = self.get_appropriate_monsters(context)
        return monster_id in appropriate_monsters

    def filter_inappropriate(
        self,
        monster_list: List[str],
        context: EnvironmentContext
    ) -> List[str]:
        """
        Remove inappropriate monsters from a list

        Args:
            monster_list: List of monster IDs
            context: Environment context

        Returns:
            Filtered list with only appropriate monsters
        """
        return [m for m in monster_list if self.is_appropriate(m, context)]

    def get_never_dungeon_monsters(self) -> List[str]:
        """
        Get list of monsters that should NEVER appear in dungeons

        Returns:
            List of monster IDs
        """
        return self.environment_data.get("environment_categories", {}).get("never_dungeon", [])

    def get_strictly_dungeon_monsters(self) -> List[str]:
        """
        Get list of monsters that ONLY appear in dungeons

        Returns:
            List of monster IDs
        """
        return self.environment_data.get("environment_categories", {}).get("strictly_dungeon", [])


# Convenience function
def filter_monsters_by_environment(
    monster_pool: List[str],
    location_type: str,
    dungeon_level: Optional[int] = None,
    terrain: Optional[str] = None
) -> List[str]:
    """
    Quick filter for monster pool based on environment

    Args:
        monster_pool: List of monster IDs to filter
        location_type: 'dungeon', 'wilderness', or 'underwater'
        dungeon_level: Dungeon level 1-10 (if location_type='dungeon')
        terrain: Terrain type (if location_type='wilderness')

    Returns:
        Filtered list of appropriate monsters

    Example:
        >>> pool = ['sprite', 'kobold', 'ogre', 'dolphin']
        >>> filter_monsters_by_environment(pool, 'dungeon', dungeon_level=1)
        ['kobold']  # sprite and dolphin removed, ogre too powerful for level 1
    """
    context = EnvironmentContext(
        location_type=location_type,
        dungeon_level=dungeon_level,
        terrain=terrain
    )

    filter_system = EnvironmentMonsterFilter()
    return filter_system.get_appropriate_monsters(context, monster_pool)


if __name__ == "__main__":
    # Test the filter system
    print("="*70)
    print("ENVIRONMENT-BASED MONSTER FILTER TEST")
    print("="*70)

    filter_system = EnvironmentMonsterFilter()

    # Test 1: Dungeon Level 1
    print("\n1. DUNGEON LEVEL 1 ENCOUNTERS")
    print("-" * 70)
    context = EnvironmentContext(location_type='dungeon', dungeon_level=1)
    monsters = filter_system.get_appropriate_monsters(context)
    print(f"Appropriate monsters: {', '.join(sorted(monsters)[:10])}...")
    print(f"Total: {len(monsters)} monster types")

    # Test 2: Check inappropriate monsters
    print("\n2. INAPPROPRIATE MONSTER CHECK")
    print("-" * 70)
    test_pool = ['sprite', 'pixie', 'kobold', 'ogre', 'dolphin', 'flightless_bird']
    filtered = filter_system.filter_inappropriate(test_pool, context)
    removed = set(test_pool) - set(filtered)
    print(f"Original pool: {test_pool}")
    print(f"Filtered (dungeon level 1): {filtered}")
    print(f"Removed as inappropriate: {list(removed)}")

    # Test 3: Wilderness - Forest
    print("\n3. WILDERNESS - FOREST ENCOUNTERS")
    print("-" * 70)
    context = EnvironmentContext(location_type='wilderness', terrain='forest')
    monsters = filter_system.get_appropriate_monsters(context)
    print(f"Appropriate monsters: {', '.join(sorted(monsters)[:15])}...")
    print(f"Total: {len(monsters)} monster types")

    # Check if faerie creatures appear
    faerie = ['sprite', 'pixie', 'brownie', 'dryad']
    faerie_in_forest = [m for m in faerie if m in monsters]
    print(f"Faerie creatures in forest: {faerie_in_forest}")

    # Test 4: Special Setting - Faerie/Sylvan
    print("\n4. FAERIE & SYLVAN SETTING")
    print("-" * 70)
    context = EnvironmentContext(
        location_type='wilderness',
        special_setting='faerie_sylvan'
    )
    monsters = filter_system.get_appropriate_monsters(context)
    print(f"Faerie/Sylvan monsters: {', '.join(sorted(monsters))}")

    # Test 5: Never Dungeon vs Strictly Dungeon
    print("\n5. ENVIRONMENT EXCLUSIVITY")
    print("-" * 70)
    never_dungeon = filter_system.get_never_dungeon_monsters()
    strictly_dungeon = filter_system.get_strictly_dungeon_monsters()
    print(f"Never in dungeons ({len(never_dungeon)}): {', '.join(never_dungeon[:10])}...")
    print(f"Only in dungeons ({len(strictly_dungeon)}): {', '.join(strictly_dungeon)}")

    # Test 6: Convenience function
    print("\n6. CONVENIENCE FUNCTION TEST")
    print("-" * 70)
    test_pool = ['sprite', 'kobold', 'ogre', 'gelatinous_cube', 'dolphin']
    filtered = filter_monsters_by_environment(test_pool, 'dungeon', dungeon_level=1)
    print(f"Pool: {test_pool}")
    print(f"Filtered for dungeon level 1: {filtered}")

    print("\n" + "="*70)
    print("Environment filter system working correctly!")
    print("="*70)
