# Aerthos Architecture Documentation

## Executive Summary

Aerthos is a text-based AD&D 1e game with **two user interfaces (CLI and Web) sharing a common core**. The Web UI is a thin Flask wrapper around the same game logic that powers the CLI.

**Key Insight:** 95% of the code is shared. Only input/output differs between UIs.

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACES                          │
│  ┌──────────────────┐              ┌─────────────────────┐  │
│  │   CLI (main.py)  │              │ Web UI (app.py)     │  │
│  │  Terminal I/O    │              │  Flask REST API     │  │
│  └────────┬─────────┘              └──────────┬──────────┘  │
│           │                                   │             │
│           └───────────┬───────────────────────┘             │
│                       │                                     │
│                       ▼                                     │
│           ┌───────────────────────┐                         │
│           │   SHARED GAME CORE    │                         │
│           │  - GameState          │                         │
│           │  - Parser             │                         │
│           │  - Combat             │                         │
│           │  - Magic              │                         │
│           │  - Storage            │                         │
│           │  - Generator          │                         │
│           └───────────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## Table of Contents

1. [Architecture Layers](#architecture-layers)
2. [Component Dependency Map](#component-dependency-map)
3. [Data Flow](#data-flow)
4. [CLI vs Web UI](#cli-vs-web-ui)
5. [Critical Integration Points](#critical-integration-points)
6. [Module Catalog](#module-catalog)
7. [Storage Architecture](#storage-architecture)
8. [Extension Points](#extension-points)

---

## Architecture Layers

### Layer 0: Data (JSON Files)

```
aerthos/data/
├── classes.json          # 4 character classes
├── races.json            # 4 character races
├── monsters.json         # Monster stat blocks
├── items.json            # Equipment database
├── spells.json           # Spell definitions
├── shops.json            # Shop inventories
├── inns.json             # Inn/tavern data
├── guilds.json           # Guild data
└── dungeons/
    └── starter_dungeon.json
```

**Role:** External configuration, easily modifiable without code changes

**Loaded by:** `GameData.load_all()`

**Used by:** All systems

---

### Layer 1: Entities (Data Models)

```
aerthos/entities/
├── character.py          # Base Character class
├── player.py             # PlayerCharacter + inventory + spells
├── monster.py            # Monster with AI
└── party.py              # Party management
```

**Dependencies:** None (except character.py)

**Role:** Core data structures for all game entities

**Used by:** All upper layers

---

### Layer 2: World (Spatial Systems)

```
aerthos/world/
├── room.py               # Individual location
├── dungeon.py            # Room graph + navigation
├── encounter.py          # Combat/trap/puzzle encounters
├── automap.py            # ASCII map generation
├── village.py            # Village locations
├── shop.py               # Shop system
├── inn.py                # Inn/tavern system
└── guild.py              # Guild system
```

**Dependencies:** Entities (room, dungeon use Room objects)

**Role:** Spatial game world representation

**Used by:** GameState, Generator

---

### Layer 3: Systems (Game Mechanics)

```
aerthos/systems/
├── magic.py              # Vancian spell system
├── skills.py             # Thief skills + ability checks
└── saving_throws.py      # 5-category saves
```

**Dependencies:** Entities (operate on Character/PlayerCharacter)

**Role:** Game rule implementation

**Used by:** GameState

---

### Layer 4: Engine (Core Logic)

```
aerthos/engine/
├── parser.py             # Natural language → Command
├── combat.py             # THAC0 resolution + dice
├── time_tracker.py       # Turn management + resources
└── game_state.py         # Central coordinator ★
```

**Dependencies:** All lower layers

**Role:** Game logic coordination and execution

**Used by:** Both entry points (main.py, web_ui/app.py)

---

### Layer 5: Generator (Procedural Content)

```
aerthos/generator/
├── config.py             # Generation configurations
├── dungeon_generator.py  # Procedural dungeons
└── monster_scaling.py    # Difficulty balancing
```

**Dependencies:** Engine (uses GameData), World (creates Dungeon)

**Role:** Procedural content creation

**Used by:** Both entry points

---

### Layer 6: Storage (Persistence)

```
aerthos/storage/
├── character_roster.py   # Character database
├── party_manager.py      # Party database
├── scenario_library.py   # Dungeon database
└── session_manager.py    # Game session database
```

**Dependencies:** Entities, World (serializes/deserializes)

**Role:** Persistent data management

**Storage:** `~/.aerthos/` directory

**Used by:** Both entry points

---

### Layer 7: UI (Interface Layer)

```
aerthos/ui/                    # Shared or CLI-specific
├── character_creation.py      # Character wizard (shared)
├── character_sheet.py         # Character display (shared)
├── party_creation.py          # Party wizard (shared)
├── display.py                 # Terminal formatting (CLI only)
└── save_system.py             # Quick saves (CLI only)

web_ui/                        # Web UI specific
├── app.py                     # Flask REST API
├── templates/                 # HTML templates
└── static/                    # CSS/JS
```

**Dependencies:** All layers

**Role:** User interaction

**Entry Points:**
- `main.py` (CLI)
- `web_ui/app.py` (Web)

---

## Component Dependency Map

### Levels (Bottom to Top)

```
Level 0: Data JSON files
         ↑
Level 1: character.py
         ↑
         ├─ player.py, monster.py
         ├─ room.py, encounter.py
         ├─ saving_throws.py
         ├─ parser.py, combat.py
         ↑
Level 2: party.py, dungeon.py, skills.py, magic.py
         time_tracker.py
         ↑
Level 3: character_roster.py, automap.py
         character_creation.py
         ↑
Level 4: party_manager.py, scenario_library.py
         dungeon_generator.py
         ↑
Level 5: game_state.py (THE HUB)
         ↑
Level 6: session_manager.py
         ↑
Level 7: main.py, web_ui/app.py
```

### No Circular Dependencies ✓

The architecture maintains clean one-way dependencies:
- Lower layers never import from upper layers
- `game_state.py` is the central hub that imports from all subsystems
- Entry points (main.py, app.py) only import what they need

---

## Data Flow

### CLI Flow

```
1. User types command in terminal
   ↓
2. main.py reads via input()
   ↓
3. CommandParser.parse() → Command object
   ↓
4. GameState.execute_command(Command) → Dict
   ↓
5. Display.show_message(result['message'])
   ↓
6. User sees output in terminal
```

### Web UI Flow

```
1. Browser sends HTTP POST /api/command
   ↓
2. Flask route in app.py receives JSON
   ↓
3. CommandParser.parse() → Command object
   ↓
4. GameState.execute_command(Command) → Dict
   ↓
5. jsonify(result) → HTTP response
   ↓
6. Browser renders JSON data
```

### Key Observation

**Steps 3-4 are IDENTICAL** between CLI and Web UI. This is the shared core.

---

## CLI vs Web UI

### What's Shared (95% of code)

| Module | Used By | Purpose |
|--------|---------|---------|
| game_state.py | Both | Core game logic |
| parser.py | Both | Command parsing |
| combat.py | Both | Combat resolution |
| magic.py | Both | Spell system |
| time_tracker.py | Both | Turn management |
| character.py | Both | Character model |
| player.py | Both | Player character |
| monster.py | Both | Monster AI |
| party.py | Both | Party management |
| dungeon.py | Both | Dungeon structure |
| room.py | Both | Room data |
| encounter.py | Both | Encounters |
| automap.py | Both | Map generation |
| skills.py | Both | Skill checks |
| saving_throws.py | Both | Saving throws |
| dungeon_generator.py | Both | Procedural generation |
| character_roster.py | Both | Character persistence |
| party_manager.py | Both | Party persistence |
| scenario_library.py | Both | Dungeon persistence |
| session_manager.py | Both | Session persistence |
| character_creation.py | Both | Character wizard |
| character_sheet.py | Both | Character display |

### What's Different (5% of code)

| Module | CLI Only | Web UI Only |
|--------|----------|-------------|
| Input | `input()` in main.py | HTTP POST in app.py |
| Output | `print()` via display.py | `jsonify()` in app.py |
| Game Loop | while loop in main.py | Stateless per-request |
| State Storage | Function scope | `active_games` dict |
| Save System | SaveSystem (quick saves) | SessionManager |
| UI | Terminal text | HTML + JSON API |

---

## Critical Integration Points

### Where Web UI Wraps CLI Functionality

#### 1. Command Processing

**CLI:**
```python
# main.py
user_input = input("> ")
cmd = parser.parse(user_input)
result = game_state.execute_command(cmd)
print(result['message'])
```

**Web UI:**
```python
# web_ui/app.py
@app.route('/api/command', methods=['POST'])
def execute_command():
    data = request.json
    cmd = parser.parse(data['command'])
    result = game_state.execute_command(cmd)
    return jsonify(result)
```

**Integration Point:** `GameState.execute_command()` - THE critical boundary

---

#### 2. Session State

**CLI:**
```python
# main.py run_game()
game_state = GameState(player, dungeon)
while game_state.is_active:
    # game loop
```

**Web UI:**
```python
# web_ui/app.py
active_games = {}  # session_id → GameState

@app.route('/api/new_game', methods=['POST'])
def new_game():
    session_id = str(uuid.uuid4())
    game_state = GameState(player, dungeon)
    active_games[session_id] = game_state
    return jsonify({'session_id': session_id})
```

**Integration Point:** GameState creation and management

---

#### 3. Output Formatting

**CLI:**
```python
# Uses Display.show_message()
result = game_state.execute_command(cmd)
Display.show_message(result['message'])
```

**Web UI:**
```python
# Returns JSON directly
result = game_state.execute_command(cmd)
return jsonify(result)
```

**Integration Point:** `result` dict from `execute_command()` must have consistent structure

---

#### 4. Persistence

**CLI Quick Saves:**
```python
# ui/save_system.py
SaveSystem.save_game(game_state, slot=1)
```

**Web UI Sessions:**
```python
# storage/session_manager.py
session_manager.create_session(name, party_id, scenario_id)
```

**Integration Point:** Both serialize GameState, but different storage mechanisms

---

## Module Catalog

### Core Engine

#### `game_state.py` (1059 lines) ★ CENTRAL HUB

**The most important file in the codebase.**

**Key Classes:**
- `GameData` - Loads all JSON data
- `GameState` - Central game coordinator

**Responsibilities:**
- Load game data (classes, races, monsters, items, spells)
- Maintain current game state (player, dungeon, room, combat)
- Route commands to appropriate handlers
- Coordinate subsystems (combat, magic, skills, time, encounters)
- Provide game state for saves

**Command Handlers (20+):**
- Movement (north, south, east, west)
- Combat (attack)
- Magic (cast)
- Items (take, drop, use, equip)
- Exploration (search, look, open)
- Character (inventory, status, spells, rest)
- Navigation (map, help)

**Key Methods:**
```python
def execute_command(self, cmd: Command) -> Dict
def _handle_move(self, cmd: Command) -> Dict
def _handle_attack(self, cmd: Command) -> Dict
def _handle_cast(self, cmd: Command) -> Dict
# ... 20+ command handlers
```

**Used By:** Both main.py and web_ui/app.py

---

#### `parser.py` (299 lines)

**Purpose:** Natural language command parsing

**Key Classes:**
- `Command` - Dataclass for parsed command
- `CommandParser` - Flexible NL parser

**Features:**
- Synonym mapping ("attack" = "hit" = "strike")
- Direction shortcuts ("n" → "north")
- Stopword filtering ("the", "a", "an")
- Modifier extraction ("carefully search")

**Key Methods:**
```python
def parse(self, raw_input: str) -> Command
```

**Dependencies:** None

**Used By:** GameState, both entry points

---

#### `combat.py` (296 lines)

**Purpose:** THAC0 combat system

**Key Classes:**
- `DiceRoller` - All dice operations
- `CombatResolver` - Combat resolution

**Algorithm:**
```python
roll_d20 >= (attacker_THAC0 - defender_AC)
```

**Key Methods:**
```python
def roll_d20(self) -> int
def roll_dice(self, num: int, sides: int, mod: int = 0) -> int
def resolve_attack(self, attacker: Character, defender: Character) -> Dict
```

**Dependencies:** character.py, player.py

**Used By:** GameState, character creation

---

#### `time_tracker.py` (226 lines)

**Purpose:** Turn-based time management

**Key Classes:**
- `TimeTracker` - Turn/hour tracking
- `RestSystem` - Rest mechanics

**Features:**
- Light source burnout tracking
- Hunger/exhaustion warnings
- Rest validation (safe rooms, rations required)

**Key Methods:**
```python
def advance_turn(self)
def attempt_rest(self, character: PlayerCharacter) -> Dict
```

**Dependencies:** player.py

**Used By:** GameState

---

### Entities

#### `character.py`

**Purpose:** Base character class

**Key Classes:**
- `Character` - Abstract base with stats, saves, combat

**Attributes:**
```python
name, race, char_class
str_score, dex, con, int_score, wis, cha
hp_current, hp_max, ac, thac0, level, xp
save_poison, save_rod_staff_wand, save_petrify_paralyze,
save_breath, save_spell
```

**Dependencies:** None

**Used By:** player.py, monster.py

---

#### `player.py` (488 lines)

**Purpose:** Player character with inventory and spells

**Key Classes:**
- `Item`, `Weapon`, `Armor`, `LightSource` - Item types
- `Spell`, `SpellSlot` - Magic system data
- `Inventory` - Weight-based inventory
- `Equipment` - Equipped items tracker
- `PlayerCharacter` - Full player model

**Features:**
- Inventory management (weight limits)
- Equipment slots (weapon, armor, shield)
- Spell memorization (Vancian)
- Thief skills
- Level progression

**Dependencies:** character.py

**Used By:** GameState, Party, storage, character_creation

---

#### `monster.py`

**Purpose:** Enemy creatures with AI

**Key Classes:**
- `Monster` - Extends Character with hit dice, treasure, AI

**AI Behaviors:**
- `aggressive` - Always attacks
- `defensive` - Only attacks if attacked
- `flee_low_hp` - Flees when injured

**Dependencies:** character.py

**Used By:** GameState, encounter system

---

#### `party.py` (208 lines)

**Purpose:** Multi-character party management

**Key Classes:**
- `Party` - Manages 4-6 PlayerCharacters

**Features:**
- Formation tracking (front/back rows)
- XP distribution
- Group rest
- Member queries (get by name/class)

**Dependencies:** player.py

**Used By:** GameState, PartyManager, SessionManager

---

### World

#### `dungeon.py`

**Purpose:** Dungeon structure and navigation

**Key Classes:**
- `Dungeon` - Room graph with navigation

**Features:**
- Load from JSON (fixed dungeons)
- Load from generator (procedural)
- Room connections (graph structure)
- Movement validation
- Serialization for saves

**Key Methods:**
```python
def load_from_dict(self, data: dict)
def get_room(self, room_id: str) -> Room
def move(self, current_room_id: str, direction: str) -> Optional[Room]
```

**Dependencies:** room.py

**Used By:** GameState, generator, scenario_library

---

#### `room.py` (177 lines)

**Purpose:** Individual dungeon location

**Key Classes:**
- `Room` - Single location with exits, items, encounters

**Attributes:**
```python
room_id, title, description
exits: Dict[str, str]  # direction → room_id
items: List[Item]
encounters: List[Encounter]
light_level: str  # bright, dim, dark
safe_rest: bool
explored: bool
```

**Dependencies:** None

**Used By:** Dungeon, generator

---

#### `encounter.py`

**Purpose:** Combat, trap, and puzzle encounters

**Key Classes:**
- `Encounter` (base)
- `CombatEncounter` - Monster fights
- `TrapEncounter` - Traps to disarm
- `PuzzleEncounter` - Puzzles to solve
- `EncounterManager` - Loads and triggers encounters

**Dependencies:** None (data only)

**Used By:** GameState

---

#### `automap.py` (216 lines)

**Purpose:** ASCII map visualization

**Features:**
- Explored room tracking
- Current position marking (X)
- Directional connections
- Compact grid layout

**Example Output:**
```
    [ ]
     |
[ ]-[X]-[ ]
     |
    [ ]
```

**Dependencies:** None

**Used By:** GameState (map command)

---

### Systems

#### `magic.py` (268 lines)

**Purpose:** Vancian spell system

**Key Classes:**
- `MagicSystem` - Spell casting and effects

**Implemented Spells (7):**
1. Magic Missile (arcane damage)
2. Cure Light Wounds (healing)
3. Sleep (crowd control)
4. Shield (AC buff)
5. Bless (attack buff)
6. Burning Hands (area damage)
7. Command (single target control)

**Key Methods:**
```python
def cast_spell(self, caster: PlayerCharacter, spell: Spell, target: Character) -> Dict
```

**Dependencies:** player.py, character.py, saving_throws.py

**Used By:** GameState

---

#### `skills.py` (187 lines)

**Purpose:** Thief skills and ability checks

**Key Classes:**
- `SkillResolver` - Percentile skill resolution

**Thief Skills (8):**
- Open Locks
- Find/Remove Traps
- Pick Pockets
- Move Silently
- Hide in Shadows
- Hear Noise
- Climb Walls
- Read Languages

**Key Methods:**
```python
def resolve_skill_check(self, character: PlayerCharacter, skill_name: str) -> Dict
def resolve_ability_check(self, character: Character, ability: str, difficulty: str) -> Dict
```

**Dependencies:** character.py, player.py

**Used By:** GameState

---

#### `saving_throws.py`

**Purpose:** AD&D 1e 5-category saves

**Key Classes:**
- `SavingThrowResolver` - d20 save rolls

**Categories:**
1. Poison/Death
2. Rod/Staff/Wand
3. Petrification/Paralysis
4. Breath Weapon
5. Spell

**Algorithm:**
```python
roll_d20 <= save_value → success
```

**Dependencies:** character.py

**Used By:** MagicSystem, GameState

---

### Generator

#### `dungeon_generator.py` (635 lines)

**Purpose:** Procedural dungeon creation

**Key Classes:**
- `DungeonGenerator` - Creates randomized dungeons

**Layout Types:**
- `linear` - Straight path
- `branching` - Tree structure
- `network` - Interconnected

**Room Themes:**
- Mine (ore veins, cave-ins)
- Crypt (tombs, undead)
- Cave (natural formations)
- Ruins (ancient structures)
- Sewer (underground waterways)

**Key Methods:**
```python
def generate(self, config: DungeonConfig) -> Dungeon
```

**Dependencies:** GameData, DungeonConfig, Dungeon, Room

**Used By:** Both entry points

---

#### `config.py` (183 lines)

**Purpose:** Generation configuration presets

**Key Classes:**
- `DungeonConfig` - Dataclass with all generation parameters

**Presets:**
- `EASY_DUNGEON` - 8 rooms, low danger
- `STANDARD_DUNGEON` - 12 rooms, balanced
- `HARD_DUNGEON` - 15 rooms, high danger

**Dependencies:** None

**Used By:** DungeonGenerator, entry points

---

#### `monster_scaling.py` (250 lines)

**Purpose:** Dynamic encounter difficulty

**Key Classes:**
- `MonsterScaler` - Balances encounters to party level

**Features:**
- Challenge Rating calculation
- Monster group size determination
- Treasure scaling

**Dependencies:** None

**Used By:** DungeonGenerator

---

### Storage

All storage modules follow similar patterns:
- JSON file persistence
- UUID-based IDs
- CRUD operations (Create, Read, Update, Delete)
- Storage in `~/.aerthos/`

#### `character_roster.py` (433 lines)

**Storage:** `~/.aerthos/characters/*.json`

**Methods:**
```python
def save_character(self, character: PlayerCharacter) -> str
def load_character(self, char_id: str) -> Optional[PlayerCharacter]
def list_characters(self) -> List[Dict]
def delete_character(self, char_id: str) -> bool
```

---

#### `party_manager.py` (192 lines)

**Storage:** `~/.aerthos/parties/*.json`

**Methods:**
```python
def save_party(self, party: Party, character_ids: List[str]) -> str
def load_party(self, party_id: str) -> Optional[Party]
def list_parties(self) -> List[Dict]
def delete_party(self, party_id: str) -> bool
```

---

#### `scenario_library.py` (203 lines)

**Storage:** `~/.aerthos/scenarios/*.json`

**Methods:**
```python
def save_scenario(self, name: str, dungeon: Dungeon) -> str
def load_scenario(self, scenario_id: str) -> Optional[Dict]
def create_dungeon_from_scenario(self, scenario_id: str) -> Dungeon
def list_scenarios(self) -> List[Dict]
def delete_scenario(self, scenario_id: str) -> bool
```

---

#### `session_manager.py` (214 lines)

**Storage:** `~/.aerthos/sessions/*.json`

**Methods:**
```python
def create_session(self, session_name: str, party_id: str, scenario_id: str) -> str
def load_session(self, session_id: str) -> Optional[Tuple[Party, Dungeon, Dict]]
def list_sessions(self) -> List[Dict]
def delete_session(self, session_id: str) -> bool
```

---

### UI Layer

#### `character_creation.py` (685 lines) - SHARED

**Purpose:** Character generation wizard

**Key Classes:**
- `CharacterCreator` - Interactive character builder

**Methods:**
- `create_character()` - Interactive wizard
- `quick_create()` - Fast creation with defaults
- Roll stats, choose class/race, assign equipment, memorize spells

**Dependencies:** player.py, combat.py (dice roller)

**Used By:** Both main.py and web_ui/app.py

---

#### `display.py` (138 lines) - CLI ONLY

**Purpose:** Terminal text formatting

**Key Classes:**
- `Display` - Static methods for formatted output

**Methods:**
```python
@staticmethod
def show_title()
def show_message(message: str)
def show_death_screen()
def prompt_input(prompt: str) -> str
```

**Dependencies:** None

**Used By:** main.py only

---

#### `save_system.py` - CLI ONLY

**Purpose:** Quick save/load (3 slots)

**Storage:** `~/.aerthos/saves/save_slot_N.json`

**Note:** Different from SessionManager (quick vs persistent)

**Dependencies:** None (operates on GameState dict)

**Used By:** main.py only

---

## Storage Architecture

### File Structure

```
~/.aerthos/
├── characters/
│   ├── {uuid}.json
│   └── ...
├── parties/
│   ├── {uuid}.json
│   └── ...
├── scenarios/
│   ├── {uuid}.json
│   └── ...
├── sessions/
│   ├── {uuid}.json
│   └── ...
└── saves/
    ├── save_slot_1.json
    ├── save_slot_2.json
    └── save_slot_3.json
```

### Persistence Layers

**5 Independent Systems:**

1. **Quick Saves** (CLI only)
   - 3 slots
   - Temporary (overwritten)
   - Full game state snapshot

2. **Character Roster** (Both UIs)
   - Persistent character database
   - UUID-based
   - CRUD operations

3. **Party Manager** (Both UIs)
   - Persistent party database
   - References character IDs
   - Formation tracking

4. **Scenario Library** (Both UIs)
   - Saved dungeon database
   - Reusable configurations
   - Full dungeon serialization

5. **Session Manager** (Both UIs)
   - Active game sessions
   - Links party + scenario + progress
   - Full checkpoint system

---

## Extension Points

### Adding New Features

#### 1. New Command

**Steps:**
1. Add to `parser.py` synonym map
2. Add handler to `game_state.py`
3. Test with both CLI and Web UI

**Example:**
```python
# parser.py
'swim': 'swim',

# game_state.py
def _handle_swim(self, cmd: Command) -> Dict:
    return {'message': 'You swim across the river.'}

# In execute_command():
'swim': self._handle_swim,
```

---

#### 2. New Spell

**Steps:**
1. Add to `data/spells.json`
2. Add implementation to `magic.py`
3. Works automatically in both UIs

**Example:**
```json
// data/spells.json
{
  "fireball": {
    "name": "Fireball",
    "level": 3,
    "school": "evocation",
    "damage": "1d6/level"
  }
}
```

```python
# magic.py
def _cast_fireball(self, caster, target):
    damage = self.dice_roller.roll_dice(caster.level, 6)
    # ...
```

---

#### 3. New Monster

**Steps:**
1. Add to `data/monsters.json`
2. Automatically loaded by `GameData`
3. Works in both UIs

---

#### 4. New REST API Endpoint (Web UI Only)

**Steps:**
1. Add route to `web_ui/app.py`
2. Call existing GameState methods
3. Return JSON response

**Example:**
```python
@app.route('/api/custom_action', methods=['POST'])
def custom_action():
    data = request.json
    session_id = data['session_id']
    game_state = active_games.get(session_id)

    # Call existing methods
    result = game_state.some_method()

    return jsonify(result)
```

---

### Safe Refactoring

**When changing shared code:**
1. Run tests before (`python run_tests.py`)
2. Make changes
3. Run tests after
4. If tests fail, both UIs might be broken

**When changing CLI-only:**
- Only affects `main.py` and `display.py`
- Web UI unaffected

**When changing Web UI-only:**
- Only affects `web_ui/app.py`
- CLI unaffected

---

## Summary

### Key Takeaways

1. **95% of code is shared** between CLI and Web UI
2. **GameState.execute_command()** is the critical boundary
3. **Both UIs call identical methods**, only I/O differs
4. **No circular dependencies** - clean layered architecture
5. **Easily testable** - each layer can be tested independently
6. **Easily extensible** - add new commands/spells/monsters via JSON + handlers

### Safe Changes

**Won't break anything:**
- Adding new JSON data (monsters, items, spells)
- Adding new commands (add handler + parser entry)
- Changing UI-specific code (display.py, app.py templates)

**Might break both UIs:**
- Changing GameState.execute_command() signature
- Changing Command dataclass structure
- Changing return value format from handlers
- Changing storage file formats

### Testing Strategy

**Before changing shared code:**
```bash
python run_tests.py
```

**After changes:**
```bash
python run_tests.py
```

If tests pass, both UIs work. If tests fail, check what broke.

---

This architecture document should be updated when:
- Major refactoring occurs
- New layers are added
- Integration points change
- Dependencies change significantly

Last updated: January 2025
