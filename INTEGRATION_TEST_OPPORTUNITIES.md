# Integration Test Opportunities for Aerthos

Based on the successful implementation of `TestAutomatedDungeonExploration`, here are additional opportunities for integration testing that exercise multiple game systems together.

## Successfully Implemented

### ✅ TestAutomatedDungeonExploration
**What it tests:**
- 4-person party creation and coordination
- Dungeon loading and navigation
- Combat encounter triggering and resolution
- Spell casting (offensive and healing)
- Resource tracking (HP, spell slots, movements)
- Party survival with retry logic

**Test methods:**
- `test_full_dungeon_exploration_with_retry()` - Complete dungeon exploration with combat
- `test_party_coordination()` - 4-character party setup
- `test_resource_tracking_during_exploration()` - HP/spell tracking during combat
- `test_movement_and_navigation()` - Movement commands

**Files:** `tests/test_integration.py` lines 515-900

---

## Recommended Future Integration Tests

### 1. Multi-Level Dungeon Navigation
**Systems exercised:**
- Dungeon generation with multiple levels
- Stairs/portal navigation (up/down transitions)
- State persistence across levels
- Party tracking across level changes

**Proposed test:**
```python
class TestMultiLevelDungeonExploration(unittest.TestCase):
    def test_descend_and_ascend_levels(self):
        """Test navigating between dungeon levels"""
        # Create 3-level dungeon
        # Descend to level 2
        # Descend to level 3
        # Ascend back to level 1
        # Verify party state maintained
```

**Estimated complexity:** Medium (3-4 hours)

---

### 2. Village-to-Dungeon Complete Loop
**Systems exercised:**
- Village navigation (shops, inns, guilds)
- Shopping and equipment purchasing
- Inn resting and spell recovery
- Transition from village to dungeon
- Return to village with loot
- Sell loot and buy better equipment

**Proposed test:**
```python
class TestVillageDungeonLoop(unittest.TestCase):
    def test_complete_adventure_cycle(self):
        """Test village → dungeon → return with loot → upgrade"""
        # Start in village
        # Buy basic equipment
        # Enter dungeon
        # Complete encounter
        # Return to village
        # Sell loot
        # Buy upgrades
        # Verify gold and inventory changes
```

**Estimated complexity:** High (5-6 hours)

---

### 3. Character Progression (Level Up)
**Systems exercised:**
- XP gain from combat
- Level-up mechanics
- HP increase
- Spell slot gain
- THAC0 improvement
- Saving throw improvement

**Proposed test:**
```python
class TestCharacterProgression(unittest.TestCase):
    def test_level_1_to_3_progression(self):
        """Test character leveling from 1 to 3"""
        # Create level 1 character
        # Fight monsters to gain XP
        # Trigger level 2 advancement
        # Verify HP, spells, THAC0 changes
        # Continue to level 3
        # Verify all stats improved correctly
```

**Estimated complexity:** Medium (4-5 hours)

---

### 4. Party Death and Recovery
**Systems exercised:**
- Party member death mechanics
- Death save system (if implemented)
- Party revival (cleric resurrection spells)
- Permanent death handling
- Session state after total party wipe

**Proposed test:**
```python
class TestPartyDeathMechanics(unittest.TestCase):
    def test_partial_party_wipe(self):
        """Test party continues after some deaths"""
        # Create 4-person party
        # Trigger lethal encounter
        # Kill 2 party members
        # Verify remaining 2 can continue
        # Attempt resurrection if available

    def test_total_party_kill(self):
        """Test game over on full party death"""
        # Create party
        # Trigger overwhelming encounter
        # All members die
        # Verify game state marked as ended
```

**Estimated complexity:** Medium (3-4 hours)

---

### 5. Spell System Comprehensive Test
**Systems exercised:**
- All spell types (offensive, healing, buff, utility)
- Spell memorization
- Spell slot management
- Rest-based recovery
- Spell components (if implemented)
- Area-of-effect spells

**Proposed test:**
```python
class TestComprehensiveSpellSystem(unittest.TestCase):
    def test_all_spell_types_in_dungeon(self):
        """Test offensive, healing, buff, utility spells"""
        # Create spellcaster party (Magic-User + Cleric)
        # Memorize diverse spell loadout
        # Use offensive spell in combat
        # Use healing spell after combat
        # Use buff spell before encounter
        # Use utility spell for exploration
        # Rest and recover
        # Verify all spell mechanics work
```

**Estimated complexity:** High (5-6 hours)

---

### 6. Thief Skills Integration
**Systems exercised:**
- Lock picking
- Trap detection
- Trap disarming
- Stealth mechanics
- Backstab mechanics
- Treasure chest opening

**Proposed test:**
```python
class TestThiefSkillsIntegration(unittest.TestCase):
    def test_thief_dungeon_exploration(self):
        """Test thief-specific mechanics in dungeon"""
        # Create party with thief
        # Encounter locked chest
        # Pick lock successfully
        # Encounter trap
        # Detect and disarm trap
        # Use stealth to avoid encounter
        # Backstab enemy
        # Verify all thief skills function
```

**Estimated complexity:** Medium (4 hours)

---

### 7. Resource Depletion Survival
**Systems exercised:**
- Ration consumption
- Light source burn-out
- Spell slot exhaustion
- HP attrition without healing
- Forced retreat mechanics

**Proposed test:**
```python
class TestResourceDepletion(unittest.TestCase):
    def test_long_delve_resource_management(self):
        """Test party survives resource scarcity"""
        # Create party with limited resources
        # Explore dungeon systematically
        # Track ration consumption
        # Track light source depletion
        # Use spells sparingly
        # Rest when safe
        # Verify party manages resources to survive
```

**Estimated complexity:** Medium (3-4 hours)

---

### 8. Procedural Dungeon Variety
**Systems exercised:**
- Dungeon generator with different configs
- Different layouts (linear, branching, maze)
- Different encounter densities
- Different treasure distributions
- Monster scaling

**Proposed test:**
```python
class TestProceduralDungeonVariety(unittest.TestCase):
    def test_multiple_generated_dungeons(self):
        """Test party completes different procedural dungeons"""
        # Generate EASY dungeon
        # Complete with basic party
        # Generate STANDARD dungeon
        # Complete with upgraded party
        # Generate HARD dungeon
        # Complete with veteran party
        # Verify all layouts playable
```

**Estimated complexity:** Medium (3-4 hours)

---

### 9. Save/Load State Integrity
**Systems exercised:**
- Session save system
- Character roster persistence
- Party manager persistence
- Dungeon state serialization
- Combat mid-encounter save
- Item inventory persistence

**Proposed test:**
```python
class TestSaveLoadIntegrity(unittest.TestCase):
    def test_save_mid_dungeon_and_restore(self):
        """Test save/load preserves all state"""
        # Create party and enter dungeon
        # Explore 3 rooms
        # Engage in combat (mid-encounter)
        # Save game state
        # Load game state
        # Verify: party HP, spells, inventory, position all match
        # Continue exploration
        # Verify state continuity
```

**Estimated complexity:** High (5-6 hours)

---

### 10. Combat Edge Cases
**Systems exercised:**
- Critical hits (natural 20)
- Critical misses (natural 1)
- Monster special abilities
- Area-of-effect attacks
- Status effects (poison, paralysis, etc.)
- Morale checks (monster fleeing)

**Proposed test:**
```python
class TestCombatEdgeCases(unittest.TestCase):
    def test_critical_hit_mechanics(self):
        """Test critical hits deal max damage"""
        # Mock dice roller to force nat 20
        # Attack enemy
        # Verify max damage dealt

    def test_monster_special_abilities(self):
        """Test monsters use special abilities"""
        # Create encounter with ability-using monster
        # Trigger special ability
        # Verify effect applied correctly
```

**Estimated complexity:** High (6-8 hours)

---

## Implementation Priority

### High Priority (Implement Soon)
1. ✅ **TestAutomatedDungeonExploration** - COMPLETED
2. **TestCharacterProgression** - Core mechanic validation
3. **TestSaveLoadIntegrity** - Data integrity critical

### Medium Priority (Next Phase)
4. **TestThiefSkillsIntegration** - Class-specific features
5. **TestSpellSystemComprehensive** - Magic system validation
6. **TestResourceDepletion** - Survival mechanics

### Lower Priority (Future Enhancement)
7. **TestVillageDungeonLoop** - Full game loop (village not fully implemented)
8. **TestMultiLevelDungeon** - Multi-level dungeons not yet supported
9. **TestProceduralVariety** - Procedural generator already tested separately
10. **TestCombatEdgeCases** - Edge cases, lower impact

---

## Benefits of Integration Testing

1. **Regression Prevention** - Catches breaking changes across system boundaries
2. **System Interaction Validation** - Ensures components work together correctly
3. **Real-World Scenario Testing** - Tests actual gameplay, not isolated units
4. **Documentation** - Serves as executable examples of game mechanics
5. **CI/CD Confidence** - Automated validation on every commit
6. **Refactoring Safety** - Safe to refactor with comprehensive coverage

---

## Current Test Suite Status

**Total Tests:** 158
- Unit Tests: 130 (parser, combat, game state, storage, etc.)
- Integration Tests: 28 (complete game flows, persistence, generation)
- **New Automated Tests:** 4 (dungeon exploration suite)

**Test Execution Time:** ~0.2 seconds (fast!)

**Test Pass Rate:** 100% ✅

---

## Notes for Future Test Implementation

1. **Use retry logic** - RNG variance requires multiple attempts for consistency
2. **Enhanced test parties** - Give 2x HP and 3x spell slots for better survival
3. **Swap game_state.player** - When testing party members casting spells
4. **Track best attempt** - For flaky tests, track the best run across retries
5. **Deterministic paths** - Use fixed exploration paths for reproducibility
6. **Mock RNG sparingly** - Prefer high retry counts over mocking for integration tests

---

**Last Updated:** 2025-11-18
**Test Suite:** Aerthos v1.0
**Test Framework:** Python unittest
