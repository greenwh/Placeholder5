# Manual Tests - Standalone Test Scripts

This directory contains standalone test scripts for manual testing of specific game systems. Unlike the automated test suite in `tests/`, these are **manual verification tests** that demonstrate functionality but are not integrated into the CI/CD pipeline.

## ✅ All Tests Now Working (Fixed: Armor API Issue)

**Status:** All tests pass as of 2025-11-18
**Issue:** Tests were failing due to old Armor API (`ac_bonus`) incompatibility
**Fix:** Updated `game_state.py` and `magic_item_factory.py` to use new Armor API (`ac` parameter)

---

## Test Files

### 1. `test_magic_items.py` (2.9K)
**Tests:** Treasure generation system with magic items

**What it validates:**
- Treasure Type A, G, F generation
- Magic item inclusion rates (30%, 35%, etc.)
- Direct magic item generation by category
- Statistical validation (100 hoards to verify percentages)

**Run:**
```bash
python3 tests_manual/test_magic_items.py
```

**Expected output:**
- Shows 5 treasure hoards per type
- Lists generated magic items
- Validates ~30% magic item rate for Type A
- Displays example items from each category

**Systems tested:**
- `aerthos/systems/treasure.py`
- `aerthos/systems/magic_item_factory.py`

---

### 2. `test_magic_functionality.py` (18K)
**Tests:** Magic item mechanics and monster special abilities

**What it validates:**
- **Potions:** Healing, Giant Strength, Speed, Invisibility, etc.
- **Scrolls:** Protection scrolls, spell scrolls
- **Rings:** Protection, Regeneration, X-Ray Vision, etc.
- **Wands:** Lightning Bolt, Fireballs, Paralyzation, etc.
- **Staves:** Striking, Power, Wizardry, etc.
- **Misc Magic:** Boots, Cloaks, Bags of Holding, etc.
- **Monster Abilities:** Dragon breath, regeneration, poison, level drain, etc.

**Run:**
```bash
python3 tests_manual/test_magic_functionality.py
```

**Expected output:**
- Detailed test results for each item category
- Damage rolls, healing amounts, effect applications
- Monster ability mechanics
- Success/failure indicators (✓/✗)

**Systems tested:**
- `aerthos/entities/magic_items.py`
- `aerthos/systems/monster_abilities.py`
- `aerthos/systems/magic_item_factory.py`

---

### 3. `test_phase3_integration.py` (8.6K)
**Tests:** Phase 3 enhancement integration

**What it validates:**
- **Trap System:**
  - Trap generation (10+ trap types)
  - Search mechanics (Thief skills)
  - Disarm mechanics with skill checks
  - Trap triggering and damage

- **Magic Item Generation:**
  - Integration with treasure system
  - Multiple treasure types (A, G, H)
  - Statistical validation

- **Multi-Level Dungeons:**
  - 2-3 level dungeon generation
  - Stair connectivity (up/down)
  - Vertical navigation
  - Serialization/deserialization

- **Complete Integration:**
  - All systems working together
  - Traps + treasure + multi-level dungeons
  - Room-based item placement

**Run:**
```bash
python3 tests_manual/test_phase3_integration.py
```

**Expected output:**
```
======================================================================
PHASE 3 ENHANCEMENT INTEGRATION TEST
======================================================================

✓ Trap System: Working
✓ Magic Item Generation: Working
✓ Multi-Level Dungeons: Working
✓ Integration: Working

Phase 3 implementation complete!
```

**Systems tested:**
- `aerthos/systems/traps.py`
- `aerthos/systems/treasure.py`
- `aerthos/generator/multilevel_generator.py`
- `aerthos/world/multilevel_dungeon.py`

---

## Why Not in Automated Test Suite?

These tests are **standalone demonstration/validation scripts** rather than unit tests because:

1. **Different purpose:** Demonstrate functionality visually rather than assert pass/fail
2. **Manual inspection:** Require human review of output to verify correctness
3. **Verbose output:** Print detailed results for debugging/demonstration
4. **Not unittest format:** Use simple functions instead of unittest.TestCase
5. **Development/debugging focus:** Created during feature development as verification tools

---

## Future Work: Integration into Automated Suite

To integrate these into `tests/` directory:

### Option 1: Convert to unittest Format
```python
class TestTreasureGeneration(unittest.TestCase):
    def test_treasure_type_a_magic_rate(self):
        """Test Type A has ~30% magic item rate"""
        generator = TreasureGenerator()
        magic_count = 0
        for _ in range(100):
            hoard = generator.generate_lair_treasure("A")
            if hoard.magic_items:
                magic_count += 1

        # Allow 20-40% range due to RNG
        self.assertGreaterEqual(magic_count, 20)
        self.assertLessEqual(magic_count, 40)
```

### Option 2: Add to Integration Test Suite
- Merge treasure tests into `tests/test_integration.py`
- Add trap tests as new test class
- Add multi-level dungeon tests

**Estimated effort:** 3-4 hours

---

## Running All Manual Tests

```bash
# Run individually
python3 tests_manual/test_magic_items.py
python3 tests_manual/test_magic_functionality.py
python3 tests_manual/test_phase3_integration.py

# Or run all with bash loop
for test in tests_manual/test_*.py; do
    echo "========================================"
    echo "Running: $test"
    echo "========================================"
    python3 "$test" || echo "FAILED: $test"
    echo ""
done
```

---

## Test Coverage Summary

### ✅ Covered by Automated Tests (`tests/`)
- Core parser (43 tests)
- Combat system (18 tests)
- Game state (19 tests)
- Persistence (19 tests)
- Ability modifiers (19 tests)
- Armor system (26 tests)
- Integration flows (14 tests)
- **Total: 158 automated tests**

### ✅ Covered by Manual Tests (`tests_manual/`)
- Treasure generation
- Magic item creation & mechanics
- Monster special abilities
- Trap system
- Multi-level dungeons
- **Total: 3 manual test scripts**

### ⚠️ Not Yet Tested
- Village system (shops, inns, guilds)
- Quest system (if implemented)
- NPC dialogue system (if implemented)
- Wilderness/overworld (if implemented)

---

## Maintenance Notes

**Last Updated:** 2025-11-18
**Armor API Fix:** Both `game_state.py` and `magic_item_factory.py` updated to use `ac` instead of `ac_bonus`
**Status:** All 3 manual tests passing
**Related Files:**
- `aerthos/engine/game_state.py` (line 1084-1096)
- `aerthos/systems/magic_item_factory.py` (line 241-287)

**Future improvements:**
- Convert to unittest format for automation
- Add to CI/CD pipeline
- Expand coverage to untested systems
