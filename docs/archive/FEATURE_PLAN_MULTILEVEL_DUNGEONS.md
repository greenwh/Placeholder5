# Feature Plan: Multi-Level Dungeon Integration (Priority 3)

## Overview
Integrate existing multi-level dungeon code into main game flow, allowing players to explore dungeons with stairs, multiple floors, and vertical progression.

## Current State
- Code exists: `aerthos/generator/multilevel_generator.py`
- Code exists: `aerthos/world/multilevel_dungeon.py`
- **NOT integrated**: main.py only uses single-level `Dungeon`
- Appendix A tables implemented in DM Guide docs
- Stairs generation exists but unused

## Design Goals
- Integrate existing multi-level dungeon system
- Add stairs as navigation mechanic (up/down)
- Preserve existing single-level dungeon support
- Make multi-level optional (not required)
- Support 1-3 level dungeons initially

## Implementation Plan

### Phase 1: Review Existing Multi-Level Code (1 hour)

**Files to Review:**
- `aerthos/generator/multilevel_generator.py`
- `aerthos/world/multilevel_dungeon.py`

**Check for:**
- API compatibility with current game_state
- Navigation commands (stairs up/down)
- Save/load compatibility
- Room ID format across levels

**Document gaps and required changes**

### Phase 2: GameState Multi-Level Support (2-3 hours)

**File: `aerthos/engine/game_state.py` (MODIFY)**

Add multi-level navigation:

```python
class GameState:
    def __init__(self, player: PlayerCharacter, dungeon: Union[Dungeon, MultiLevelDungeon]):
        self.player = player
        self.dungeon = dungeon
        self.current_level = 0  # NEW: Track current level (0-indexed)
        self.current_room = dungeon.get_start_room(level=0)  # NEW: Level-aware

    def _handle_stairs_up(self, command: Command) -> Dict:
        """Handle going up stairs"""
        if not self.current_room.has_stairs_up():
            return {'success': False, 'message': "There are no stairs going up here."}

        if self.current_level == 0:
            return {'success': False, 'message': "You're already on the top level."}

        # Ascend
        self.current_level -= 1
        new_room = self.dungeon.get_room_at_stairs_up(self.current_level, self.current_room.id)

        self.current_room = new_room
        return {'success': True, 'message': f"You climb the stairs up to Level {self.current_level + 1}.\n\n{new_room.description}"}

    def _handle_stairs_down(self, command: Command) -> Dict:
        """Handle going down stairs"""
        if not self.current_room.has_stairs_down():
            return {'success': False, 'message': "There are no stairs going down here."}

        if self.current_level >= self.dungeon.num_levels - 1:
            return {'success': False, 'message': "There are no deeper levels below."}

        # Descend
        self.current_level += 1
        new_room = self.dungeon.get_room_at_stairs_down(self.current_level, self.current_room.id)

        self.current_room = new_room
        return {'success': True, 'message': f"You descend the stairs to Level {self.current_level + 1}.\n\n{new_room.description}"}
```

**Command Routing (modify execute_command):**
```python
handlers = {
    # [existing handlers]
    'stairs_up': self._handle_stairs_up,
    'stairs_down': self._handle_stairs_down,
    'up': self._handle_stairs_up,      # Shorthand
    'down': self._handle_stairs_down,  # Shorthand
}
```

### Phase 3: Parser Commands for Stairs (30 minutes)

**File: `aerthos/engine/parser.py` (MODIFY)**

Add stair navigation commands:

```python
VERBS = {
    # [existing verbs]
    'stairs_up': ['up', 'u', 'upstairs', 'ascend', 'climb up'],
    'stairs_down': ['down', 'd', 'downstairs', 'descend', 'climb down'],
}
```

**Update help text:**
```
MOVEMENT:
  go <direction>    - Move in a direction (north, south, east, west)
  up / u            - Climb stairs up (to higher level)
  down / d          - Climb stairs down (to deeper level)
```

### Phase 4: Room Stairs Support (1 hour)

**File: `aerthos/world/room.py` (MODIFY)**

Add stair tracking:

```python
@dataclass
class Room:
    # [existing fields]
    has_stairs_up: bool = False    # NEW
    has_stairs_down: bool = False  # NEW
    stairs_up_to: Optional[str] = None    # NEW: Room ID on level above
    stairs_down_to: Optional[str] = None  # NEW: Room ID on level below

    def on_enter(self, has_light: bool, player: PlayerCharacter) -> str:
        """Get room description on entry"""

        # [existing description code]

        # Add stair info
        if self.has_stairs_up:
            description += "\n\nA stairway leads UP to a higher level."
        if self.has_stairs_down:
            description += "\n\nA stairway descends DOWN into darkness."

        return description
```

### Phase 5: Multi-Level Generation Integration (2 hours)

**File: `main.py` (MODIFY)**

Add multi-level option to dungeon menu:

```python
def choose_dungeon_type() -> str:
    """Ask player to choose between fixed or generated dungeon"""

    print("\n" + "═" * 70)
    print("DUNGEON SELECTION")
    print("═" * 70)
    print()
    print("SINGLE-LEVEL DUNGEONS")
    print("  1. The Abandoned Mine (Fixed - 10 rooms, recommended for first game)")
    print("  2. Generate Random Dungeon (Easy - 8 rooms)")
    print("  3. Generate Random Dungeon (Standard - 12 rooms)")
    print("  4. Generate Random Dungeon (Hard - 15 rooms)")
    print()
    print("MULTI-LEVEL DUNGEONS")
    print("  5. Small Multi-Level (2 levels, 8 rooms per level)")
    print("  6. Medium Multi-Level (3 levels, 10 rooms per level)")
    print("  7. Large Multi-Level (3 levels, 12 rooms per level)")
    print()
    print("  8. Custom Generated Dungeon (Advanced)")
    print()

    while True:
        choice = input("Choose dungeon (1-8): ").strip()
        if choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
            return choice
        print("Invalid choice. Please enter 1-8.")
```

**Generation Logic:**
```python
def start_new_game(game_data: GameData) -> tuple:
    """Start a new game with character creation"""

    # [existing character creation]

    dungeon_choice = choose_dungeon_type()

    if dungeon_choice == '1':
        # Fixed starter dungeon
        dungeon = Dungeon.load_from_file('aerthos/data/dungeons/starter_dungeon.json')

    elif dungeon_choice in ['2', '3', '4']:
        # Single-level generated dungeons
        # [existing single-level generation]

    elif dungeon_choice in ['5', '6', '7']:
        # NEW: Multi-level generated dungeons
        from aerthos.generator.multilevel_generator import MultiLevelGenerator

        generator = MultiLevelGenerator(game_data)

        if dungeon_choice == '5':
            config = {
                'num_levels': 2,
                'rooms_per_level': 8,
                'difficulty': 'easy'
            }
        elif dungeon_choice == '6':
            config = {
                'num_levels': 3,
                'rooms_per_level': 10,
                'difficulty': 'standard'
            }
        else:  # '7'
            config = {
                'num_levels': 3,
                'rooms_per_level': 12,
                'difficulty': 'hard'
            }

        print(f"✓ Generating {config['num_levels']}-level dungeon...")
        dungeon_data = generator.generate(config)
        dungeon = MultiLevelDungeon.load_from_generator(dungeon_data)
        print(f"✓ Generated: {dungeon.name}")

    else:  # '8' - Custom
        # [existing custom generation]
```

### Phase 6: Automap Multi-Level Support (1-2 hours)

**File: `aerthos/world/automap.py` (MODIFY)**

Support multiple level displays:

```python
class AutoMap:
    def generate_map_multilevel(self, current_level: int, all_levels: Dict) -> str:
        """
        Generate ASCII map for multi-level dungeon

        Shows:
        - Current level in detail
        - Level indicator (e.g., "=== LEVEL 2 of 3 ===")
        - Stairs up/down markers
        """

        map_str = f"{'═' * 40}\n"
        map_str += f"LEVEL {current_level + 1}\n"
        map_str += f"{'═' * 40}\n\n"

        # Generate map for current level
        map_str += self.generate_map(all_levels[current_level])

        # Add legend
        map_str += "\n\nLEGEND:\n"
        map_str += "  [X] = Your current position\n"
        map_str += "  [ ] = Explored room\n"
        map_str += "  [^] = Stairs up\n"
        map_str += "  [v] = Stairs down\n"

        return map_str
```

**Room markers for stairs:**
- `[^]` = Has stairs up
- `[v]` = Has stairs down
- `[↕]` = Has both stairs

### Phase 7: Save/Load Multi-Level Support (1 hour)

**File: `aerthos/ui/save_system.py` (MODIFY)**

Ensure save format includes:
```json
{
    "player": {...},
    "dungeon": {
        "type": "multilevel",
        "num_levels": 3,
        "levels": [...],
        "current_level": 1
    },
    "game_state": {
        "current_level": 1,
        "current_room_id": "level1_room005"
    }
}
```

**Load logic:**
```python
def load_game(self) -> Optional[Tuple[PlayerCharacter, Dungeon, GameState]]:
    """Load game from save file"""

    # [existing load code]

    # Check dungeon type
    if dungeon_data.get('type') == 'multilevel':
        from aerthos.world.multilevel_dungeon import MultiLevelDungeon
        dungeon = MultiLevelDungeon.from_save_data(dungeon_data)
    else:
        dungeon = Dungeon.from_save_data(dungeon_data)

    # Restore level position
    game_state = GameState(player, dungeon)
    game_state.current_level = save_data['game_state'].get('current_level', 0)
    # [continue loading]
```

### Phase 8: Difficulty Scaling by Level (1 hour)

**File: `aerthos/generator/multilevel_generator.py` (MODIFY)**

Implement depth-based difficulty:

```python
def generate(self, config: Dict) -> Dict:
    """Generate multi-level dungeon with increasing difficulty"""

    levels = []
    base_party_level = config.get('party_level', 1)

    for level_num in range(config['num_levels']):
        # Increase difficulty with depth
        # Level 0 (surface): party_level
        # Level 1: party_level + 0.5
        # Level 2: party_level + 1.0
        adjusted_party_level = base_party_level + (level_num * 0.5)

        level_config = DungeonConfig(
            num_rooms=config['rooms_per_level'],
            party_level=int(adjusted_party_level),
            lethality_factor=1.0 + (level_num * 0.2),
            # Get harder monsters for deeper levels
            monster_pool=self.get_monsters_for_depth(adjusted_party_level)
        )

        level_data = self.generate_single_level(level_config)
        levels.append(level_data)

    # Connect levels with stairs
    self.connect_levels_with_stairs(levels)

    return {
        'name': f"{config['num_levels']}-Level Dungeon",
        'num_levels': config['num_levels'],
        'levels': levels
    }
```

### Phase 9: Testing (2 hours)

**File: `tests/test_multilevel_dungeons.py` (NEW)**

Test cases:
- Multi-level dungeon generation (2-3 levels)
- Stairs navigation (up/down commands)
- Level boundaries (can't go up from top, down from bottom)
- Room descriptions show stair indicators
- Automap shows current level correctly
- Save/load preserves level position
- Difficulty increases with depth
- Stair connections valid between levels
- Parser handles stair commands correctly

**Integration tests:**
- Play through multi-level dungeon
- Navigate all levels
- Combat on different levels
- Save on level 2, load, verify position

## Configuration Constants

Add to `aerthos/constants.py`:
```python
# Multi-Level Dungeons
MAX_DUNGEON_LEVELS = 5           # Maximum depth
DIFFICULTY_PER_LEVEL = 0.5       # Party level increase per depth
LETHALITY_PER_LEVEL = 0.2        # Lethality factor increase per depth
STAIRS_PER_LEVEL_MIN = 1         # Minimum connections between levels
STAIRS_PER_LEVEL_MAX = 3         # Maximum connections between levels
```

## Success Criteria

✅ Multi-level dungeons can be selected from menu
✅ 2-3 level dungeons generate correctly
✅ Stairs navigation works (up/down commands)
✅ Room descriptions show stair indicators
✅ Automap displays current level with stair markers
✅ Can't navigate beyond dungeon boundaries
✅ Difficulty scales with depth (harder monsters deeper)
✅ Save/load preserves level and position
✅ All existing single-level functionality preserved
✅ All existing tests still pass
✅ New multi-level tests pass (12+ test cases)

## Risks & Mitigations

**Risk**: Existing code incompatible with current game_state
**Mitigation**: Review in Phase 1, refactor MultiLevelDungeon to match Dungeon API

**Risk**: Save format breaks backward compatibility
**Mitigation**: Check dungeon type in save, support both single and multi-level

**Risk**: Navigation confusing (which level am I on?)
**Mitigation**: Clear level indicators in descriptions, map shows level number

**Risk**: Difficulty scaling too steep (deeper levels too hard)
**Mitigation**: Use conservative 0.5 level increase per depth, test balance

## Estimated Time: 10-13 hours total

## Files Created/Modified
- **NEW**: `tests/test_multilevel_dungeons.py`
- **MODIFY**: `aerthos/engine/game_state.py` (~80 lines added)
- **MODIFY**: `aerthos/engine/parser.py` (~15 lines added)
- **MODIFY**: `aerthos/world/room.py` (~30 lines added)
- **MODIFY**: `main.py` (~60 lines added)
- **MODIFY**: `aerthos/world/automap.py` (~50 lines added)
- **MODIFY**: `aerthos/ui/save_system.py` (~40 lines added)
- **MODIFY**: `aerthos/generator/multilevel_generator.py` (~40 lines modified)
- **MODIFY**: `aerthos/constants.py` (~10 lines added)
- **REVIEW**: `aerthos/world/multilevel_dungeon.py` (compatibility check)

## Dependencies
- This feature is independent (can be implemented first, second, or third)
- Works with existing single-level dungeons
- Compatible with party-aware generation (Priority 2)
- Compatible with formation combat (Priority 1)

## Optional Future Enhancements
- 4-5 level mega-dungeons
- Special features per level (water level, lava level, etc.)
- Boss on deepest level
- Shortcuts/secret passages between non-adjacent levels
- Level names/themes (Catacombs, Deep Mines, Underdark)
