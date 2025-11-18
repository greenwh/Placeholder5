# Automated Dungeon Exploration Integration Test - Feasibility Analysis

## Executive Summary

**FEASIBILITY: HIGH** ✅

An automated dungeon exploration integration test is highly feasible and would provide excellent end-to-end testing coverage. The existing codebase has all necessary components in place, and the 10-room "Abandoned Mine" starter dungeon provides an ideal test environment with diverse encounters.

---

## Current State Analysis

### Existing Infrastructure

**Demo Game Setup** (`web_ui/app.py`):
- ✅ Automated party creation (4 characters: Fighter, Magic-User, Cleric, Thief)
- ✅ Quick character generation via `CharacterCreator.quick_create()`
- ✅ Party system fully functional
- ✅ Game state initialization

**Starter Dungeon** (`aerthos/data/dungeons/starter_dungeon.json`):
- ✅ 10 rooms with interconnected exits
- ✅ 5 combat encounters (kobolds, rats, goblins, skeletons, ogre)
- ✅ 1 trap encounter (pit trap)
- ✅ 14 items scattered throughout
- ✅ 3 safe rest rooms
- ✅ Mixed light levels (dim, dark)

**Integration Test Framework** (`tests/test_integration.py`):
- ✅ Existing integration tests for basic exploration
- ✅ Command parsing to execution flow
- ✅ Party/character persistence tests
- ✅ Procedural generation tests
- ⚠️ **Missing:** Comprehensive automated exploration test

### Game Mechanics Available for Testing

1. **Movement System**: ✅ Functional
   - Parser supports: north, south, east, west, n, s, e, w
   - Room connections verified
   - Invalid movement handled gracefully

2. **Light & Vision**: ✅ Functional
   - Light levels: bright, dim, dark
   - Torch/lantern mechanics (burn time tracking)
   - Light radius system

3. **Resource Management**: ✅ Functional
   - Ration consumption on rest
   - Light source burn time
   - Inventory weight tracking

4. **Combat System**: ✅ Functional
   - THAC0-based combat
   - Party initiative
   - Monster AI behaviors
   - HP tracking and death

5. **Spell Casting**: ✅ Functional
   - Spell memorization (332 spells available)
   - Spell slot tracking
   - Casting mechanics
   - Rest to restore spells

6. **Item Interaction**: ✅ Functional
   - Take/drop items
   - Equip weapons/armor
   - Use consumables
   - Container support

7. **Trap Detection**: ⚠️ Partially testable
   - Trap data exists in rooms
   - Search command available
   - Thief skill mechanics implemented

8. **Lock Mechanics**: ⚠️ Limited
   - Lock items exist in equipment database
   - Thief lockpick skill exists
   - Few locked doors in starter dungeon

---

## Proposed Test Design

### Test Structure

```python
class TestAutomatedDungeonExploration(unittest.TestCase):
    """Comprehensive automated dungeon exploration test"""

    def test_full_dungeon_exploration(self):
        """
        Automated party explores the entire starter dungeon
        Tests: movement, combat, items, rest, resources, spells
        """
        # 1. Setup
        # 2. Explore all rooms randomly
        # 3. Handle encounters
        # 4. Manage resources
        # 5. Verify completion
```

### Test Phases

**Phase 1: Setup** (5-10 lines)
- Load game data
- Create 4-character party (Fighter, Cleric, Magic-User, Thief)
- Load starter dungeon from JSON
- Initialize game state
- Verify starting conditions

**Phase 2: Automated Exploration Loop** (50-100 lines)
- Random movement selection from available exits
- Track visited rooms (ensure all 10 rooms visited)
- Handle encounters automatically
- Manage light sources (equip/track burn time)
- Collect items encountered
- Rest when needed (HP low or spells depleted)

**Phase 3: Encounter Handling** (30-50 lines)
- **Combat**: Automated combat resolution
  - Party attacks monsters
  - Use spells strategically (e.g., magic missile, cure light wounds)
  - Track HP loss
  - Rest after combat if needed
- **Traps**: Search for traps, attempt to disarm
- **Items**: Take items, equip better gear

**Phase 4: Resource Management** (20-30 lines)
- Track torch/lantern burn time
- Replace light sources when exhausted
- Monitor ration supply
- Track spell slots
- Rest in safe rooms when resources low

**Phase 5: Verification** (10-20 lines)
- Verify all rooms explored
- Verify encounters resolved
- Verify items collected
- Verify party survival (or expected deaths)
- Verify resource tracking accuracy

---

## Implementation Approach

### Option A: Deterministic Exploration (Recommended)

**Strategy**: Follow a predetermined exploration path that visits all rooms

**Advantages**:
- Predictable, reproducible results
- Easier to debug failures
- Tests specific scenarios (e.g., "always explore north first")
- Fast execution (~5-10 seconds)

**Example Path**:
```
room_001 → room_002 (combat) → room_004 (trap) → room_005
→ room_006 (combat) → room_007 → room_008 (combat)
→ room_009 (combat) → room_010 (combat) → backtrack to room_001
→ room_003 (combat) → complete
```

**Code Sketch**:
```python
def test_deterministic_dungeon_exploration(self):
    # Setup
    party = self._create_demo_party()
    dungeon = Dungeon.load_from_json("starter_dungeon.json")
    game_state = GameState(party=party, dungeon=dungeon)

    # Predetermined path
    exploration_path = [
        ("north", "room_002"),
        ("north", "room_004"),
        ("north", "room_005"),
        ("east", "room_006"),
        # ... etc
    ]

    for direction, expected_room in exploration_path:
        # Move
        result = game_state.execute_command(parse(direction))
        self.assertEqual(game_state.current_room.id, expected_room)

        # Handle encounters
        self._handle_encounters(game_state)

        # Manage resources
        self._manage_resources(game_state)

        # Collect items
        self._collect_items(game_state)
```

### Option B: Random Exploration with Constraints

**Strategy**: Randomly choose exits, but ensure full coverage

**Advantages**:
- Tests edge cases and random behavior
- More realistic player behavior simulation
- Finds unexpected bugs

**Disadvantages**:
- Less reproducible (use seed for consistency)
- Slower (may backtrack)
- Harder to debug

**Code Sketch**:
```python
def test_random_dungeon_exploration(self):
    random.seed(42)  # Reproducible randomness

    visited = set()
    target_rooms = set(dungeon.rooms.keys())

    while visited != target_rooms:
        # Choose random exit
        exits = list(game_state.current_room.exits.keys())
        direction = random.choice(exits)

        # Move
        game_state.execute_command(parse(direction))
        visited.add(game_state.current_room.id)

        # Handle encounters, etc.
```

### Option C: Hybrid Approach (Best of Both)

**Strategy**: Use deterministic path for main coverage, add random tests for edge cases

**Advantages**:
- Fast, reliable main test
- Additional random tests catch edge cases
- Best code coverage

**Structure**:
```python
def test_full_dungeon_deterministic(self):
    # Main test - deterministic path

def test_random_exploration_100_moves(self):
    # Stress test - random movements

def test_combat_all_encounters(self):
    # Focused test - ensure all combat works
```

---

## Specific Test Cases

### 1. Movement & Exploration
```python
def test_explore_all_rooms(self):
    """Verify party can reach all 10 rooms"""
    # Track visited rooms
    # Ensure no unreachable rooms
    # Verify map updates correctly
```

### 2. Light Source Mechanics
```python
def test_light_management(self):
    """Test torch/lantern burn time and replacement"""
    # Enter dark room without light (should warn)
    # Equip torch
    # Track burn time (6 turns)
    # Replace when exhausted
    # Test lantern (24 turns)
```

### 3. Combat Encounters
```python
def test_all_combat_encounters(self):
    """Resolve all 5 combat encounters"""
    # Room 002: 3 kobolds
    # Room 003: 2 giant rats
    # Room 006: 4 goblins
    # Room 008: 3 skeletons
    # Room 010: 1 ogre (boss)

    # Verify:
    # - Combat resolution works
    # - HP loss tracked
    # - XP gain tracked
    # - Loot dropped
```

### 4. Spell Casting
```python
def test_spell_casting_in_combat(self):
    """Test spell usage during exploration"""
    # Magic-User casts magic missile
    # Cleric casts cure light wounds
    # Track spell slot depletion
    # Rest to restore spells
```

### 5. Resource Management
```python
def test_resource_depletion(self):
    """Test ration and light consumption"""
    # Start with 2 rations per character
    # Rest multiple times
    # Verify ration consumption
    # Test "out of rations" scenario
```

### 6. Item Collection & Equipment
```python
def test_item_progression(self):
    """Test looting and equipment upgrades"""
    # Start with basic gear
    # Find +1 shortsword in room 006
    # Find +1 chain mail in room 008
    # Find +2 dagger in room 009
    # Equip better items
    # Verify AC/damage improvements
```

### 7. Trap Detection
```python
def test_trap_search_and_disarm(self):
    """Test thief trap mechanics in room 004"""
    # Enter room 004
    # Thief searches for traps
    # Detect pit trap
    # Attempt to disarm
    # Verify success/failure
```

### 8. Safe Rest Mechanics
```python
def test_safe_rest_rooms(self):
    """Test resting in safe vs unsafe rooms"""
    # Rest in room 004 (safe) - no interruption
    # Rest in room 005 (unsafe) - potential wandering monster
    # Verify HP/spell restoration
```

---

## Expected Test Metrics

### Coverage Targets

- **Rooms Visited**: 10/10 (100%)
- **Combat Encounters**: 5/5 (100%)
- **Trap Encounters**: 1/1 (100%)
- **Items Found**: 14/14 (100%)
- **Safe Rooms Tested**: 3/3 (100%)
- **Commands Tested**:
  - Movement: north, south, east, west
  - Combat: attack, cast spell
  - Items: take, equip, drop
  - Resources: rest, search
  - Info: look, status, inventory, map

### Execution Time

- **Deterministic Test**: ~5-10 seconds
- **Random Test (100 moves)**: ~15-30 seconds
- **Full Suite**: ~30-60 seconds

### Pass Criteria

✅ **Must Pass**:
- All rooms reachable and explorable
- All combat encounters resolvable
- Party survives (or dies predictably)
- No crashes or exceptions
- Resource tracking accurate

⚠️ **May Vary** (RNG-dependent):
- Combat damage rolls
- Trap detection success
- Random exploration path
- Wandering monster encounters

---

## Implementation Complexity

### Difficulty: **MEDIUM** (3-4 hours)

**Easy Parts** (60%):
- Setup (party, dungeon, game state)
- Movement commands
- Item collection
- Basic assertions

**Medium Parts** (30%):
- Combat automation (need to handle multi-round combat)
- Resource tracking (light, rations, spells)
- Smart rest decisions

**Hard Parts** (10%):
- Trap handling edge cases
- Spell selection logic (which spell to cast when)
- Random exploration with guaranteed coverage

---

## Recommended Implementation Plan

### Phase 1: Basic Test (1-2 hours)
1. Create party and load starter dungeon
2. Implement deterministic path through all rooms
3. Basic movement assertions
4. **Deliverable**: test_basic_dungeon_exploration()

### Phase 2: Combat & Resources (1 hour)
1. Automate combat resolution
2. Add spell casting logic
3. Track HP, spell slots, rations, light
4. **Deliverable**: test_combat_and_resources()

### Phase 3: Items & Traps (30 min)
1. Implement item collection
2. Add equipment upgrades
3. Trap search/disarm
4. **Deliverable**: test_items_and_traps()

### Phase 4: Random Exploration (30 min)
1. Implement random movement
2. Coverage verification
3. Stress testing
4. **Deliverable**: test_random_exploration()

---

## Code Example Skeleton

```python
class TestAutomatedDungeonExploration(unittest.TestCase):
    """Automated exploration of the 10-room starter dungeon"""

    def setUp(self):
        """Load game data and create test fixtures"""
        self.game_data = GameData.load_all()
        self.parser = CommandParser()

    def _create_demo_party(self):
        """Create standard 4-person demo party"""
        creator = CharacterCreator(self.game_data)

        fighter = creator.quick_create("Thorin", "Dwarf", "Fighter")
        mage = creator.quick_create("Elara", "Elf", "Magic-User")
        cleric = creator.quick_create("Cedric", "Human", "Cleric")
        thief = creator.quick_create("Shadow", "Halfling", "Thief")

        return Party(members=[fighter, mage, cleric, thief])

    def _load_starter_dungeon(self):
        """Load the 10-room starter dungeon"""
        import json
        dungeon_path = "aerthos/data/dungeons/starter_dungeon.json"
        with open(dungeon_path) as f:
            data = json.load(f)
        return Dungeon.load_from_json_data(data)

    def _handle_combat(self, game_state):
        """Automate combat resolution"""
        if not game_state.in_combat:
            return

        while game_state.in_combat:
            # Party attacks
            for member in game_state.party.members:
                if member.is_alive:
                    if member.char_class == "Magic-User" and member.has_spell("magic_missile"):
                        cmd = self.parser.parse("cast magic missile")
                    else:
                        cmd = self.parser.parse("attack")
                    game_state.execute_command(cmd)

            # Check if combat ended
            if all(not m.is_alive for m in game_state.active_monsters):
                break

    def _manage_resources(self, game_state):
        """Check and manage party resources"""
        # Check if anyone needs healing
        for member in game_state.party.members:
            if member.hp_current < member.hp_max / 2:
                # Try to rest in safe room
                if game_state.current_room.safe_rest:
                    cmd = self.parser.parse("rest")
                    game_state.execute_command(cmd)
                    break

    def _collect_items(self, game_state):
        """Pick up items in current room"""
        for item in game_state.current_room.items:
            cmd = self.parser.parse(f"take {item}")
            game_state.execute_command(cmd)

    def test_full_dungeon_exploration(self):
        """Main test: explore entire starter dungeon"""
        # Setup
        party = self._create_demo_party()
        dungeon = self._load_starter_dungeon()
        game_state = GameState(party=party, dungeon=dungeon)

        # Track progress
        visited_rooms = set()

        # Predetermined exploration path
        path = [
            "north",  # room_001 -> room_002 (kobolds)
            "north",  # room_002 -> room_004 (trap)
            "north",  # room_004 -> room_005
            "east",   # room_005 -> room_006 (goblins)
            "west",   # room_006 -> room_005
            "north",  # room_005 -> room_007
            "north",  # room_007 -> room_008 (skeletons)
            "east",   # room_008 -> room_009
            "north",  # room_009 -> room_010 (ogre)
            "south",  # room_010 -> room_009
            "west",   # room_009 -> room_008
            "south",  # room_008 -> room_007
            "south",  # room_007 -> room_005
            "south",  # room_005 -> room_004
            "south",  # room_004 -> room_002
            "south",  # room_002 -> room_001
            "east",   # room_001 -> room_003 (rats)
        ]

        # Execute path
        for direction in path:
            visited_rooms.add(game_state.current_room.id)

            # Move
            cmd = self.parser.parse(direction)
            result = game_state.execute_command(cmd)

            # Handle encounters
            self._handle_combat(game_state)

            # Collect items
            self._collect_items(game_state)

            # Manage resources
            self._manage_resources(game_state)

        # Final room
        visited_rooms.add(game_state.current_room.id)

        # Assertions
        self.assertEqual(len(visited_rooms), 10, "Should visit all 10 rooms")
        self.assertTrue(all(m.is_alive for m in party.members), "Party should survive")
        self.assertGreater(party.members[0].xp, 0, "Should gain XP from combat")
```

---

## Risks & Mitigations

### Risk 1: Combat Takes Too Long
**Mitigation**: Simplify combat automation, use quick resolution

### Risk 2: RNG Makes Test Flaky
**Mitigation**: Use seeded random, focus on deterministic tests

### Risk 3: Party Dies During Exploration
**Mitigation**: Either accept failure or give party better stats/healing

### Risk 4: Test Becomes Too Complex
**Mitigation**: Break into smaller focused tests

---

## Benefits of Implementation

✅ **Regression Prevention**: Catch breaking changes across systems
✅ **Integration Verification**: Ensures all systems work together
✅ **Performance Baseline**: Track execution time changes
✅ **Documentation**: Serves as usage example
✅ **Confidence**: Validates core gameplay loop
✅ **CI/CD Ready**: Can run automatically on every commit

---

## Conclusion

**RECOMMENDATION: IMPLEMENT**

This test would provide significant value with moderate effort. The existing infrastructure is excellent, and the starter dungeon is perfect for automated testing.

**Suggested Approach**:
1. Start with Phase 1 (basic deterministic exploration)
2. Add Phase 2 (combat automation) if Phase 1 succeeds
3. Expand with Phases 3-4 as time permits

**Expected ROI**: HIGH - Catches integration bugs that unit tests miss.

**Timeline**: 3-4 hours for full implementation, 1-2 hours for minimal viable test.
