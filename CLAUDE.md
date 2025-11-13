# CLAUDE.md - Aerthos

Advanced Dungeons & Dragons 1st Edition Text Adventure Game

## Project Overview

Aerthos is a faithful recreation of AD&D 1e mechanics as a single-player text adventure game. It features authentic THAC0 combat, Vancian magic, resource management, and both hand-crafted and procedurally generated dungeons.

**Technology Stack:**
- Python 3.10+
- Flask (optional, for web UI only)
- No other external dependencies (core game uses standard library only)

**Project Status:** Active development - core systems complete, recent work on session management and party systems

**Project Location:** `/mnt/c/Users/tofm4/OneDrive/Development/aerthos`

---

## Quick Start Commands

### CLI Game (No Dependencies)

```bash
# Start the text-based game
python main.py

# Main menu options:
# 1. New Game (Quick Play - temp character & dungeon)
# 2. Load Game (Quick Save)
# 3. Character Roster (create, view, delete persistent characters)
# 4. Party Manager (create, view, delete parties)
# 5. Scenario Library (save, view, delete dungeons)
# 6. Session Manager (create, load, delete game sessions)
```

### Web UI (Requires Flask)

```bash
# Install Flask if needed
pip install -r requirements.txt

# Start web server
python web_ui/app.py

# Open browser to http://localhost:5000
# Gold Box style interface with visual party roster
```

### Development & Testing

```bash
# No virtual environment needed - minimal dependencies
# But if you prefer:
python -m venv venv
source venv/bin/activate  # Linux/WSL
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.10+
```

### **Testing - CRITICAL WORKFLOW**

**⚠️ ALWAYS run tests before and after making code changes!**

```bash
# Run all tests (recommended)
python3 run_tests.py --no-web

# Run specific test categories
python3 run_tests.py --unit          # Core systems only
python3 run_tests.py --integration   # End-to-end scenarios
python3 run_tests.py --web           # Flask API (requires Flask)

# Run with verbose output for debugging
python3 run_tests.py --no-web --verbose

# Run individual test file
python3 -m unittest tests.test_parser -v
python3 -m unittest tests.test_combat -v
```

**Testing Workflow:**
1. **BEFORE making changes:** Run `python3 run_tests.py --no-web` to establish baseline
2. **Make your changes:** Implement features, fix bugs, refactor code
3. **AFTER making changes:** Run `python3 run_tests.py --no-web` to verify nothing broke
4. **If tests fail:** Fix the code or update tests to match new behavior
5. **Only commit when all tests pass**

**Why This Matters:**
- CLI and Web UI share 95% of code - changes affect both
- Tests protect the critical boundary between UIs and game logic
- Broken tests = broken game for users
- Passing tests = both UIs work correctly

**Current Test Status:** 86/109 tests passing (79%)
- ✅ Parser tests: 43/43 passing
- ✅ Combat tests: 18/18 passing
- ⚠️ Game state tests: 16/19 passing
- ⚠️ Storage tests: Working (some failures)
- ⚠️ Integration tests: Working (some failures)

**See also:**
- `TESTING.md` - Comprehensive testing guide
- `TEST_SUITE_README.md` - Test suite documentation
- `ARCHITECTURE.md` - How CLI and Web UI connect

---

## Architecture Overview

### Component Structure

```
aerthos/
├── engine/          # Core game systems
│   ├── game_state.py      # Central game state manager
│   ├── parser.py           # Natural language command parser
│   ├── combat.py           # THAC0 combat resolution
│   └── time_tracker.py     # Turn/time management
│
├── entities/        # Character and monster classes
│   ├── character.py        # Base Character class
│   ├── player.py           # PlayerCharacter with inventory
│   ├── monster.py          # Monster with AI
│   └── party.py            # Party management
│
├── systems/         # Game subsystems
│   ├── magic.py            # Vancian magic system
│   ├── skills.py           # Thief skills & ability checks
│   └── saving_throws.py    # 5-category saving throws
│
├── world/           # Dungeon and location management
│   ├── dungeon.py          # Dungeon map & navigation
│   ├── room.py             # Room class with encounters
│   ├── encounter.py        # Combat/trap/puzzle encounters
│   ├── village.py          # Village with shops, inns, guilds
│   ├── shop.py             # Shop system
│   ├── inn.py              # Inn/tavern system
│   ├── guild.py            # Guild system
│   └── automap.py          # Auto-mapping display
│
├── storage/         # Persistent data management
│   ├── character_roster.py  # Character database
│   ├── party_manager.py     # Party database
│   ├── scenario_library.py  # Saved dungeons
│   └── session_manager.py   # Game sessions
│
├── generator/       # Procedural generation
│   ├── dungeon_generator.py    # Dungeon creation
│   ├── monster_scaling.py      # Monster difficulty scaling
│   └── config.py               # Generator configs (EASY/STANDARD/HARD)
│
├── data/            # JSON data files
│   ├── classes.json        # 4 classes (Fighter, Cleric, Magic-User, Thief)
│   ├── races.json          # 4 races (Human, Elf, Dwarf, Halfling)
│   ├── monsters.json       # Monster stat blocks
│   ├── items.json          # Items & equipment
│   ├── spells.json         # Spell definitions
│   ├── shops.json          # Shop inventories
│   ├── inns.json           # Inn/tavern data
│   ├── guilds.json         # Guild data
│   └── dungeons/
│       └── starter_dungeon.json  # 10-room fixed dungeon
│
└── ui/              # User interface
    ├── display.py              # Text formatting & output
    ├── character_sheet.py      # Character display
    ├── character_creation.py   # Character creator
    ├── party_creation.py       # Party creator
    └── save_system.py          # Save/load system
```

### Data Flow

```
Player Input → Parser → Game State → System Resolution → Display
                           ↓
                    Session Manager
                           ↓
                    Save/Checkpoint System
```

---

## Core Game Systems

### 1. THAC0 Combat System

**Algorithm:**
```
Roll d20
Hit if: roll >= (THAC0 - target AC)
```

**Features:**
- Descending AC (10 = unarmored, 0 = plate+shield, -5 = exceptional)
- Side initiative (d6 for party, d6 for monsters)
- Critical hit on natural 20
- Critical miss on natural 1
- Weapon damage varies by target size (Small/Medium vs Large)

**Implementation:** `aerthos/engine/combat.py`

### 2. Vancian Magic System

**Mechanics:**
- Spell memorization system (daily slots)
- Spells consumed on casting
- Restore all slots on rest
- Abstract components ("standard" vs "rare")
- 7 implemented spells (expandable)

**Key Classes:**
- Cleric: Divine spellcaster
- Magic-User: Arcane spellcaster

**Implementation:** `aerthos/systems/magic.py`

### 3. Saving Throws

**5 Categories (AD&D 1e standard):**
1. Poison/Death
2. Rod/Staff/Wand
3. Petrification/Paralysis
4. Breath Weapon
5. Spell

**Roll:** d20, succeed if `roll <= save value`

**Implementation:** `aerthos/systems/saving_throws.py`

### 4. Thief Skills

**Percentile-based skills:**
- Open Locks
- Find/Remove Traps
- Pick Pockets
- Move Silently
- Hide in Shadows
- Hear Noise
- Climb Walls
- Read Languages

**Implementation:** `aerthos/systems/skills.py`

### 5. Resource Management

**Light Sources:**
- Torches: 6 turns (1 hour)
- Lanterns: 24 turns (4 hours)
- Tracks burn time per turn

**Rations:**
- Consumed during rest
- Required for HP/spell recovery

**Encumbrance:**
- Based on STR
- Affects movement if overloaded

**Implementation:** `aerthos/engine/time_tracker.py`

### 6. Natural Language Parser

**Flexible command handling:**
- "attack orc"
- "attack the orc with sword"
- "carefully search for traps"
- "cast magic missile at kobold"
- "go north" / "n" / "north"

**Implementation:** `aerthos/engine/parser.py`

### 7. Auto-Mapping

**ASCII map generation:**
```
    [ ]
     |
[ ]-[X]-[ ]
     |
    [ ]
```

- X = current position
- [ ] = explored room
- Reveals as you explore

**Implementation:** `aerthos/world/automap.py`

### 8. Persistence Systems

**Three layers:**

1. **Quick Save/Load** (temporary, single slot)
   - For current play session
   - Overwritten each save

2. **Character Roster** (`~/.aerthos/characters/`)
   - Persistent character database
   - Create, view, delete characters
   - JSON files with UUIDs

3. **Party Manager** (`~/.aerthos/parties/`)
   - Persistent party database
   - Create parties from roster characters
   - 4-6 characters per party

4. **Scenario Library** (`~/.aerthos/scenarios/`)
   - Save generated dungeons
   - Reuse custom configurations
   - JSON files with dungeon data

5. **Session Manager** (`~/.aerthos/sessions/`)
   - Full game state snapshots
   - Party + dungeon + progress
   - Multiple concurrent sessions

**Implementation:** `aerthos/storage/`, `aerthos/ui/save_system.py`

---

## Dungeon Types

### 1. Fixed Dungeon: "The Abandoned Mine"

**Features:**
- Hand-crafted 10-room dungeon
- Linear progression with branching paths
- Multiple enemy types (kobolds, goblins, skeletons, giant rats, ogre boss)
- Traps, puzzles, treasure
- Safe rooms for resting
- Recommended for first playthrough

**Location:** `aerthos/data/dungeons/starter_dungeon.json`

### 2. Generated Dungeons

**Presets:**
- **Easy:** 8 rooms, low encounter density
- **Standard:** 12 rooms, balanced encounters
- **Hard:** 15 rooms, high danger

**Configurable Parameters:**
- Room count
- Layout type (linear, branching, network)
- Encounter density (combat/traps/treasure frequency)
- Monster pool selection
- Difficulty scaling

**Implementation:** `aerthos/generator/dungeon_generator.py`

**Configuration:** `aerthos/generator/config.py`

---

## Key Data Structures

### Character Attributes

```python
# Core Stats (3-18 range, +percentile for STR 18)
str, dex, con, int, wis, cha

# Combat
hp_current, hp_max, ac, thac0, level

# Identity
name, race, char_class

# State
is_alive, conditions

# Saving Throws
save_poison, save_rod_staff_wand, save_petrify_paralyze
save_breath, save_spell
```

### PlayerCharacter (extends Character)

```python
inventory: Inventory
equipment: Equipment  # Worn/wielded items
spells_known: List[Spell]
spells_memorized: List[Spell]
thief_skills: Dict[str, int]  # skill_name: percentage
xp: int
```

### Monster (extends Character)

```python
hit_dice: str  # e.g., "2+1" or "4"
treasure_type: str
ai_behavior: str  # 'aggressive', 'defensive', 'flee_low_hp'
special_abilities: List[str]
```

---

## Common Development Tasks

### Adding a New Spell

1. Edit `aerthos/data/spells.json`:
```json
{
  "spell_name": {
    "name": "Spell Name",
    "level": 1,
    "school": "evocation",
    "casting_time": "1 segment",
    "range": "60 feet",
    "duration": "1 turn/level",
    "area_of_effect": "20-foot radius",
    "saving_throw": "Negates",
    "components": "standard",
    "description": "Effect description"
  }
}
```

2. Implement handler in `aerthos/systems/magic.py`

### Adding a New Monster

1. Edit `aerthos/data/monsters.json`:
```json
{
  "monster_id": {
    "name": "Monster Name",
    "hit_dice": "2+1",
    "ac": 6,
    "thac0": 19,
    "damage": "1d8",
    "size": "M",
    "movement": 9,
    "xp_value": 35,
    "ai_behavior": "aggressive"
  }
}
```

2. Monster automatically loaded by `aerthos/entities/monster.py`

### Adding a New Item

Edit `aerthos/data/items.json`:
```json
{
  "item_id": {
    "name": "Item Name",
    "type": "weapon",  // or 'armor', 'consumable', 'treasure'
    "weight": 3.0,
    "cost": 10,
    "properties": {
      "damage_sm": "1d8",
      "damage_l": "1d12",
      "speed_factor": 7
    }
  }
}
```

### Creating a New Dungeon

**Option 1: Hand-craft JSON**
```json
{
  "name": "Dungeon Name",
  "description": "Dungeon description",
  "rooms": {
    "room_001": {
      "title": "Entry Hall",
      "description": "Room description",
      "exits": {"north": "room_002", "east": "room_003"},
      "light_level": "dim",
      "encounters": [],
      "items": [],
      "safe_rest": false
    }
  },
  "start_room": "room_001"
}
```

**Option 2: Use Generator**
```python
from aerthos.generator.dungeon_generator import DungeonGenerator
from aerthos.generator.config import DungeonConfig

config = DungeonConfig(
    num_rooms=10,
    layout_type='branching',
    combat_frequency=0.6,
    monster_pool=['kobold', 'goblin', 'orc']
)

generator = DungeonGenerator()
dungeon = generator.generate(config)
```

### Debugging Combat

Enable combat logging in `aerthos/engine/combat.py`:

```python
# Add debug prints to see calculations
print(f"Roll: {roll}, THAC0: {thac0}, AC: {ac}, Target: {thac0 - ac}")
```

### Testing Save/Load

```bash
# Save files stored in:
~/.aerthos/saves/           # Quick saves
~/.aerthos/characters/      # Character roster
~/.aerthos/parties/         # Party manager
~/.aerthos/scenarios/       # Scenario library
~/.aerthos/sessions/        # Session manager

# View save data
cat ~/.aerthos/saves/quick_save.json
cat ~/.aerthos/characters/*.json
cat ~/.aerthos/sessions/*.json
```

---

## Game Commands (CLI)

### Movement
- `north`, `south`, `east`, `west` (or `n`, `s`, `e`, `w`)
- `go [direction]`

### Combat
- `attack [monster]`
- `cast [spell]` or `cast [spell] on [target]`

### Items
- `take [item]` / `get [item]`
- `equip [item]` / `wear [item]`
- `use [item]` / `drink [item]`
- `drop [item]`

### Exploration
- `search` - Find traps, hidden items
- `look` / `examine` - Re-read room description
- `open [object]` - Open chests, doors

### Character
- `status` / `stats` - Character sheet
- `inventory` / `i` - View items
- `spells` - View available spells
- `rest` / `sleep` - Restore HP and spells (requires safe room)

### Navigation
- `map` / `m` - Show auto-map
- `help` - Command list
- `save` - Save game
- `quit` / `exit` - Exit game

---

## Recent Development

### Latest Changes (from git log)

```
42b2e8d - Fix save_party parameter order in solo session creation
07dc4c3 - Improve solo session error messages and input validation
c0729ea - Fix solo session creation - show actual errors
9c46e3b - Add solo character session creation to CLI
72baf4c - Align party gameplay with single-player gameplay
```

**Focus Areas:**
- Session management system refinement
- Party system integration
- Error handling and validation improvements
- CLI gameplay consistency

### Active Features

**Implemented:**
- ✅ Complete core systems (combat, magic, saves, skills)
- ✅ Character creation (4 classes, 4 races)
- ✅ 10-room hand-crafted starter dungeon
- ✅ Procedural dungeon generator with presets
- ✅ Auto-mapping
- ✅ Save/load system (5-tier persistence)
- ✅ Character roster management
- ✅ Party management
- ✅ Session management
- ✅ Web UI with Gold Box style interface
- ✅ Village system (shops, inns, guilds)

**Potential Expansions:**
- Additional dungeons
- More spells and monsters
- Higher character levels (currently level 1-3)
- Additional classes (Ranger, Paladin, Druid, Bard)
- Wilderness/overworld map
- Multi-level dungeons
- Quest system

---

## Design Philosophy

### AD&D 1e Authenticity

**Faithful Recreation:**
- THAC0 calculation (not d20 modern)
- Descending AC (not ascending)
- Vancian magic (not spell points)
- Percentage thief skills (not d20 checks)
- 5-category saves (not single save bonus)
- Turn-based time (10-minute turns)

**Old School Challenge:**
- Lethal combat - HP is precious
- Resource management matters
- No hand-holding or quest markers
- Exploration and caution rewarded
- Character death is permanent (restore from saves)
- Dice control your fate (3d6 in order, no rerolls)

### Combat Philosophy

**Quick Resolution:**
- Summary narratives, not turn-by-turn detail
- Example: "You strike the orc for 6 damage. It retaliates, missing you!"
- Monster HP hidden from player
- Maintains mystery and tension

### Magic System

**Abstract Components:**
- "Standard" components assumed available
- "Rare" components only for high-level spells (future)
- No granular tracking of bat guano, etc.
- Focus on strategic spell use, not inventory micromanagement

---

## File Organization

### Configuration Files

```
requirements.txt                    # Flask only (optional)
.gitignore                         # Excludes save files, __pycache__
aerthos-MS_Client_ID.txt          # MS client ID (gitignored)
```

### Documentation Files

```
README.md                    # Player-facing documentation
SETUP.md                     # Installation guide
ITEMS_REFERENCE.md          # Item database reference
aerthos_tech_spec.md        # Technical specification
aerthos_claude_code_prompt.md  # Implementation guide
CLAUDE.md                    # This file - development guide
```

### Main Entry Points

```
main.py                      # CLI game entry point
web_ui/app.py               # Flask web UI entry point
```

---

## Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'flask'"**
```bash
pip install Flask
# Or: pip install -r requirements.txt
```

**"Python not found"**
```bash
# Try different Python invocations
python3 main.py
python main.py

# Check version
python --version  # Need 3.10+
```

**Game won't start**
```bash
# Ensure correct directory
pwd  # Should end in aerthos
cd /mnt/c/Users/tofm4/OneDrive/Development/aerthos

# Check file exists
ls main.py
```

**Save files not persisting**
```bash
# Check save directory
ls -la ~/.aerthos/
ls -la ~/.aerthos/saves/
ls -la ~/.aerthos/characters/
ls -la ~/.aerthos/sessions/

# Create if missing
mkdir -p ~/.aerthos/{saves,characters,parties,scenarios,sessions}
```

**Combat calculations seem wrong**
```bash
# Remember: THAC0 is descending AC
# Hit if: d20 roll >= (THAC0 - target AC)
# Lower AC is better!
# AC 10 = unarmored
# AC 0 = plate + shield
# AC -5 = exceptional
```

**Spell slots not restoring**
- Must rest in a safe room
- Requires consuming rations
- 15% chance of wandering monster interrupt

### Debug Mode

Add to code temporarily:
```python
# In combat.py
DEBUG = True
if DEBUG:
    print(f"Combat debug: roll={roll}, thac0={thac0}, ac={ac}")

# In magic.py
DEBUG = True
if DEBUG:
    print(f"Spell slots: {character.spells_memorized}")
```

---

## Testing Strategy

### Manual Testing Checklist

**Character Creation:**
- [ ] Roll 3d6 for each ability
- [ ] Apply race modifiers
- [ ] Class restrictions enforced
- [ ] Starting equipment assigned
- [ ] HP calculated with CON modifier

**Combat:**
- [ ] THAC0 calculation correct
- [ ] AC properly subtracted
- [ ] Damage dice rolled correctly
- [ ] Critical hits deal max damage
- [ ] Critical misses handled
- [ ] Death at 0 HP

**Magic:**
- [ ] Spell slots tracked per level
- [ ] Casting consumes slot
- [ ] Rest restores all slots
- [ ] Spell effects apply correctly

**Thief Skills:**
- [ ] Percentile rolls work
- [ ] Skill success/failure narrative
- [ ] DEX modifiers apply

**Resources:**
- [ ] Torches burn for 6 turns
- [ ] Darkness warnings before burnout
- [ ] Rations consumed on rest
- [ ] Encumbrance affects movement

**Dungeon:**
- [ ] Room connections work
- [ ] Auto-map updates on exploration
- [ ] Encounters trigger correctly
- [ ] Items can be taken
- [ ] Traps can be found/disarmed

**Save/Load:**
- [ ] Save creates file
- [ ] Load restores exact state
- [ ] Character roster CRUD works
- [ ] Party manager CRUD works
- [ ] Session manager CRUD works

### Unit Tests (Future)

Planned test coverage:
- `tests/test_combat.py` - THAC0 calculations
- `tests/test_magic.py` - Spell system
- `tests/test_parser.py` - Command parsing
- `tests/test_generator.py` - Dungeon generation
- `tests/test_saves.py` - Saving throw mechanics

---

## Development Guidelines

### Code Style

**Python Conventions:**
- PEP 8 style
- Type hints preferred
- Docstrings for classes and public methods
- Descriptive variable names

**OOP Principles:**
- Composition over inheritance where appropriate
- Single Responsibility Principle
- Avoid god classes

### Adding New Features

**Workflow:**
1. Read relevant documentation (tech spec, prompt)
2. Understand existing patterns in similar code
3. Update JSON data files if needed
4. Implement core logic
5. Add to parser if new command
6. Test manually with multiple scenarios
7. Update documentation

**Example: Adding new character class**

1. Add to `aerthos/data/classes.json`
2. Implement any special abilities in `aerthos/entities/character.py`
3. Update character creation UI in `aerthos/ui/character_creation.py`
4. Test character creation, combat, leveling
5. Update README.md feature list

### Working with JSON Data

**All game data is external:**
- Classes, races, monsters, items, spells = JSON files
- Easy to modify without changing code
- Supports modding and content expansion

**Validation:**
- Schema checking on load
- Fail fast with clear error messages
- Example: "Missing 'damage' field in weapon 'longsword'"

---

## Performance Considerations

### Current Scope

**Target Performance:**
- Instant command response (< 100ms)
- Room generation < 1 second
- Save/load < 1 second

**Limitations:**
- Single-player only (no networking overhead)
- Small dungeon size (10-30 rooms typical)
- Limited monster count per encounter (1-10)

**Not Optimized For:**
- Massive dungeons (100+ rooms)
- Concurrent multiplayer
- Real-time graphics

### If Performance Issues Arise

**Profile first:**
```python
import cProfile
cProfile.run('start_game()')
```

**Likely bottlenecks:**
- JSON parsing on every load (cache loaded data)
- Recursive dungeon generation (limit depth)
- Combat with many monsters (batch calculations)

---

## Integration Points

### Web UI (`web_ui/app.py`)

**Architecture:**
- Flask backend serves REST API
- HTML/CSS/JS frontend (Gold Box style)
- JSON communication between layers

**Endpoints:**
- `/api/new_game` - Start new session
- `/api/command` - Process player command
- `/api/state` - Get current game state
- `/api/save` - Save game
- `/api/load` - Load game

**Frontend Features:**
- Visual party roster with HP bars
- 2D map display
- Real-time updates
- Demo party included

### Future Integration Possibilities

**Discord Bot:**
- Natural language parser already flexible
- Game state serializable to JSON
- Could support play-by-post style

**Web Version (Full):**
- Current web UI is basic
- Could expand to full SPA with React
- Character builder as separate tool

**Mobile App:**
- Python backend via Flask
- React Native or similar frontend
- Cloud save sync

---

## Known Limitations

### By Design

- Single player only (party management is player controlling multiple PCs)
- Turn-based only (no real-time mode)
- Text-only (no graphics except ASCII map)
- Limited to low-level play (1-3 currently)
- Simplified components system
- Monster HP hidden from player

### Technical Debt

- No comprehensive unit tests yet
- Parser could be more sophisticated (ML-based?)
- Dungeon generator is basic (room+corridor, no complex shapes)
- No multi-level dungeon support yet
- Save system doesn't compress (JSON text files)

### Future Enhancements

**High Priority:**
- Multi-level dungeons
- More character levels (4-10)
- Additional classes/races
- Wilderness exploration

**Medium Priority:**
- Quest system
- NPC dialogue
- Faction reputation
- Crafting system

**Low Priority:**
- Multiplayer support
- Graphical tile-based mode
- Sound effects
- Achievements

---

## External Resources

### AD&D 1e References

**Core Rulebooks:**
- Players Handbook (PHB)
- Dungeon Masters Guide (DMG)
- Monster Manual (MM)

**Online Resources:**
- OSR community forums
- AD&D 1e wikis
- Tabletop simulator tools

### Python Resources

**Libraries Used:**
- `json` - Data file parsing
- `random` - Dice rolling, procedural generation
- `pathlib` - File path handling
- `dataclasses` - Data structures
- `typing` - Type hints
- `flask` - Web UI (optional)

---

## Project History

**Initial Vision:**
- Faithful AD&D 1e recreation
- Solo play text adventure
- Low-dependency Python project

**Evolution:**
- Started with combat and character systems
- Added dungeon generator with configuration
- Implemented persistence layers (roster, party, sessions)
- Created web UI for visual interface
- Expanded to village/shop/inn systems

**Current State:**
- Fully playable core game
- Multiple play modes (quick play, persistent)
- CLI and web UI options
- Active refinement of session management

---

## Contributing Guidelines

(If this were open source)

**Code Contributions:**
1. Fork repository
2. Create feature branch
3. Follow existing code style
4. Add tests for new features
5. Update documentation
6. Submit pull request

**Content Contributions:**
- New monsters, spells, items welcome
- Submit as JSON additions
- Follow existing schema
- Provide balanced stats

**Bug Reports:**
- Describe steps to reproduce
- Include save file if possible
- Note Python version and OS

---

## Contact & Support

**Developer:** Working project in active development

**Documentation:**
- Technical Spec: `aerthos_tech_spec.md`
- Implementation Guide: `aerthos_claude_code_prompt.md`
- Player Guide: `README.md`
- Setup: `SETUP.md`
- Items Reference: `ITEMS_REFERENCE.md`

---

## License & Credits

**Credits:**
- Designed to capture the spirit of Gary Gygax and Dave Arneson's original Advanced Dungeons & Dragons
- Built with Python 3 and nostalgia for classic dice-rolling adventures

**Legal:**
- Fan project for educational and entertainment purposes
- Dungeons & Dragons is a trademark of Wizards of the Coast

---

**May your hits be critical and your saves be high!**
