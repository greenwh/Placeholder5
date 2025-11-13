# Aerthos API Reference

## Quick Reference for Test Writing

This document provides the actual API signatures for key classes to help write accurate tests.

**Last Updated:** January 2025
**Purpose:** Prevent test failures due to API mismatches

---

## Core Classes

### Command (parser.py)

```python
@dataclass
class Command:
    action: str
    target: Optional[str] = None
    modifier: Optional[str] = None
    instrument: Optional[str] = None
```

**NOT included:** `raw_input`, `direction`, `item`, `spell_name`

**Usage:**
```python
cmd = parser.parse("attack orc")
cmd.action  # "attack"
cmd.target  # "orc"

cmd = parser.parse("north")
cmd.action  # "move"
cmd.target  # "north"
```

---

### Room (world/room.py)

```python
@dataclass
class Room:
    id: str  # NOT room_id!
    title: str
    description: str
    light_level: str = 'dark'
    exits: Dict[str, str] = field(default_factory=dict)
    items: List[str] = field(default_factory=list)
    is_explored: bool = False
    is_safe_for_rest: bool = False
    encounters_completed: List[str] = field(default_factory=list)
```

**Usage:**
```python
room = Room(
    id="room_001",  # NOT room_id!
    title="Entry Hall",
    description="A large hall",
    light_level="bright",
    exits={"north": "room_002"}
)
```

---

### PlayerCharacter (entities/player.py)

**Constructor signature varies - check actual implementation!**

Likely uses properties like:
- `name`
- `race`
- `char_class` (NOT `class` - reserved keyword)
- `strength` or `str` (check actual)
- `dex`, `con`, `int`, `wis`, `cha`

**Always check the actual __init__() signature before writing tests!**

---

### CharacterRoster (storage/character_roster.py)

**Constructor signature:**
```python
def __init__(self, save_dir: Optional[str] = None):
    # NOT storage_dir!
```

**Usage:**
```python
roster = CharacterRoster(save_dir=temp_dir)  # NOT storage_dir!
```

---

### DungeonConfig (generator/config.py)

```python
@dataclass
class DungeonConfig:
    num_rooms: int = 10
    layout_type: str = 'branching'
    combat_frequency: float = 0.4
    trap_frequency: float = 0.2
    treasure_frequency: float = 0.3
    # ... more fields

    def __post_init__(self):
        # Validates that frequencies don't exceed 1.0
        if combat_frequency + trap_frequency + treasure_frequency > 1.0:
            raise ValueError("Encounter frequencies sum to more than 1.0")
```

**Usage:**
```python
# Valid
config = DungeonConfig(
    num_rooms=10,
    combat_frequency=0.4,
    trap_frequency=0.2,
    treasure_frequency=0.3  # Total = 0.9, OK
)

# Invalid - raises ValueError!
config = DungeonConfig(
    num_rooms=15,
    combat_frequency=0.8  # Default trap+treasure will exceed 1.0
)
```

---

## Common Test Patterns

### Create Test Dungeon

```python
def create_test_dungeon(self):
    room = Room(
        id="test_001",  # Use 'id' not 'room_id'
        title="Test Room",
        description="A test room",
        light_level="bright",
        exits={}
    )

    dungeon_data = {
        "name": "Test Dungeon",
        "description": "Test",
        "start_room": "test_001",
        "rooms": {
            "test_001": {
                "id": "test_001",
                "title": room.title,
                "description": room.description,
                "light_level": room.light_level,
                "exits": room.exits,
                "items": [],
                "is_explored": False,
                "is_safe_for_rest": False
            }
        }
    }

    dungeon = Dungeon()
    dungeon.load_from_dict(dungeon_data)
    return dungeon
```

### Create Test Character

**WARNING:** Check actual PlayerCharacter.__init__() signature first!

The constructor may use properties or may require specific field names.

```python
# VERIFY THIS MATCHES ACTUAL CODE:
def create_test_character(self, name="Fighter"):
    # Option 1: If using property names
    char = PlayerCharacter(
        name=name,
        race="human",
        char_class="fighter",
        strength=16,  # or str_val, or str - check actual
        dexterity=14,
        constitution=15,
        intelligence=10,
        wisdom=12,
        charisma=10
    )

    # Option 2: Create empty and set attributes
    char = PlayerCharacter()
    char.name = name
    char.race = "human"
    char.char_class = "fighter"
    char.strength = 16
    # etc...

    return char
```

### Test Command Parsing

```python
def test_attack_command(self):
    parser = CommandParser()
    cmd = parser.parse("attack orc")

    # Correct assertions:
    self.assertEqual(cmd.action, "attack")
    self.assertEqual(cmd.target, "orc")

    # WRONG assertions:
    # self.assertEqual(cmd.item, "orc")  # NO 'item' attribute
    # self.assertEqual(cmd.direction, "north")  # NO 'direction' attribute
```

### Test Storage

```python
def test_save_character(self):
    temp_dir = tempfile.mkdtemp()
    roster = CharacterRoster(save_dir=temp_dir)  # NOT storage_dir!

    char = create_test_character()
    char_id = roster.save_character(char)

    self.assertIsNotNone(char_id)

    shutil.rmtree(temp_dir)
```

---

## Debugging Tips

### When Tests Fail with AttributeError

```
AttributeError: 'Command' object has no attribute 'spell_name'
```

**Fix:** The Command class doesn't have that attribute. Check API_REFERENCE.md for actual attributes.

### When Tests Fail with TypeError

```
TypeError: Room.__init__() got an unexpected keyword argument 'room_id'
```

**Fix:** The constructor parameter is `id` not `room_id`. Check API_REFERENCE.md.

### When Tests Fail with KeyError

```
KeyError: 'fighter'
```

**Fix:** GameData expects lowercase keys. Check data/classes.json for exact key names.

### When Tests Fail with ValueError

```
ValueError: Encounter frequencies sum to more than 1.0
```

**Fix:** DungeonConfig validates that combat + trap + treasure frequencies <= 1.0. Adjust values.

---

## How to Find Actual API

### Method 1: Read the Source

```bash
# Find class definition
grep -n "^class Room" aerthos/world/room.py

# Find __init__ signature
grep -A 20 "def __init__" aerthos/world/room.py
```

### Method 2: Python REPL

```python
from aerthos.world.room import Room
import inspect

# Get signature
print(inspect.signature(Room.__init__))

# Get fields (for dataclasses)
print(Room.__dataclass_fields__)
```

### Method 3: Check Existing Usage

```bash
# Find how Room is actually used
grep -r "Room(" aerthos/ | head -10
```

---

## Test Template

When writing new tests, use this template:

```python
import unittest
from aerthos.module import Class

class TestSomething(unittest.TestCase):
    """Test something"""

    def setUp(self):
        """ALWAYS check actual API before setting up!"""
        pass

    def test_something(self):
        """
        Step 1: Read the actual module
        Step 2: Verify constructor signature
        Step 3: Write test with correct API
        """
        # Correct usage:
        obj = Class(actual_param="value")  # Not assumed_param!

        self.assertEqual(obj.actual_field, "value")  # Not assumed_field!
```

---

## When to Update This Document

Update API_REFERENCE.md when:
- Constructor signatures change
- New required fields added
- Field names renamed
- Validation logic added (like DungeonConfig)
- Tests consistently fail due to API mismatches

**Keep this document in sync with code!**

---

Last updated: January 2025
