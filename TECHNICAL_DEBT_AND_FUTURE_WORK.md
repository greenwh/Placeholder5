# Technical Debt & Future Work

**Last Updated:** 2025-11-18
**Project:** Aerthos - AD&D 1e Text Adventure
**Status:** Active Development

This document consolidates all known technical debt, cleanup tasks, and future enhancement plans.

---

## 🚨 Critical Issues (Fix ASAP)

### None Currently ✅

All critical issues have been resolved as of 2025-11-18.

---

## ⚠️ High Priority Technical Debt

### 1. Flaky Test: Procedural Dungeon Generation
**File:** `tests/test_integration.py` line 442
**Issue:** Test expects ≥12 rooms from HARD config, but RNG sometimes generates 11
**Impact:** 1/158 tests fails intermittently
**Fix:** Either:
- Reduce expectation to ≥11 rooms
- Use seed for deterministic generation
- Add retry logic like automated exploration test

**Estimated effort:** 15 minutes

---

### 2. Armor API Inconsistency in Data Files
**Files:** `aerthos/data/items.json`, `aerthos/data/equipment.json`
**Issue:** JSON files use `ac_bonus`, but Armor class expects `ac`
**Current workaround:** Conversion layer in `game_state.py` (line 1085-1087)
**Impact:** Confusion for developers, extra conversion code
**Fix:** Either:
- Update all JSON files to use `ac` directly
- OR update Armor class to accept both formats

**Estimated effort:** 1-2 hours (requires updating 65+ items)

---

### 3. Debug Print Statements in Production Code
**Files:** `aerthos/engine/game_state.py`, `aerthos/systems/magic.py`
**Issue:** Multiple `[DEBUG]` and `[DEBUG MAGIC]` print statements left in code
**Impact:** Verbose console output during normal gameplay
**Examples:**
```python
# game_state.py line 420
print(f"[DEBUG] _handle_cast received command.target: '{command.target}'")

# magic.py (multiple locations)
print(f"[DEBUG MAGIC] Executing spell...")
```

**Fix:** Remove or convert to proper logging
**Estimated effort:** 30 minutes

---

## 📋 Medium Priority Cleanup

### 4. Manual Test Integration
**Files:** `tests_manual/test_*.py` (3 files)
**Issue:** Valuable tests exist but aren't part of automated suite
**Current state:** Fixed Armor API issues, all tests passing
**Systems tested:** Treasure, magic items, traps, multi-level dungeons
**Fix:** Convert to unittest format and integrate into `tests/`

**Estimated effort:** 3-4 hours
**Benefits:**
- Automated regression testing
- CI/CD integration
- Better coverage metrics

---

### 5. Incomplete Test Coverage
**Not tested:** Village system, shops, inns, guilds
**Impact:** Changes to these systems could break without detection
**Fix:** Add integration tests for village loop

**Estimated effort:** 4-5 hours
**See:** `INTEGRATION_TEST_OPPORTUNITIES.md` #2 (Village-to-Dungeon Complete Loop)

---

### 6. Old Data Files (Possible Cleanup)
**Files in root:**
- `AUTOMATED_EXPLORATION_SUMMARY.md` (8KB)
- `AUTOMATED_EXPLORATION_TEST_FEASIBILITY.md` (6.5KB)

**Issue:** Feasibility documents for completed work
**Fix:** Either:
- Move to `docs/` directory
- Delete (info now in `INTEGRATION_TEST_OPPORTUNITIES.md`)

**Estimated effort:** 5 minutes

---

## 🔮 Future Enhancements (Planned)

### Phase 1: Players Handbook Integration (In Progress)

**Location:** `PLAYERS_HANDBOOK_INTEGRATION_PLAN.md`

**Completed:**
- ✅ Task 1.1: Ability Score Tables (2024-11-18)
- ✅ Task 1.2: Complete Armor System (2024-11-18)
- ✅ Task 1.3: Spell Database Expansion - 332 spells (2024-11-18)
- ✅ Task 1.4: Equipment & Gear Database - 65 items (2024-11-18)

**Next up:**
- Task 1.5: Saving Throw Tables (All Classes)
- Task 1.6: THAC0 Progression Tables
- Task 1.7: Experience Tables & Leveling
- Task 1.8: Racial Ability Adjustments
- Task 1.9: Class Restrictions & Requirements
- Task 1.10: Hit Point Progression

**Status:** 4/10 tasks complete (40%)
**Estimated remaining:** 15-20 hours

---

### Phase 2: Additional Integration Tests

**Location:** `INTEGRATION_TEST_OPPORTUNITIES.md`

**Implemented:**
1. ✅ TestAutomatedDungeonExploration (2024-11-18)

**Recommended priority:**
2. TestCharacterProgression (level 1→3)
3. TestSaveLoadIntegrity
4. TestThiefSkillsIntegration
5. TestSpellSystemComprehensive

**Estimated effort:** 15-20 hours total

---

### Phase 3: System Expansions

**Already implemented but not in automated tests:**
- Trap system (`aerthos/systems/traps.py`)
- Treasure generation (`aerthos/systems/treasure.py`)
- Magic item factory (`aerthos/systems/magic_item_factory.py`)
- Monster special abilities (`aerthos/systems/monster_abilities.py`)
- Multi-level dungeons (`aerthos/world/multilevel_dungeon.py`)

**Future systems:**
- Wilderness/overworld map
- Quest system
- NPC dialogue trees
- Faction reputation
- Crafting/alchemy

---

## 🐛 Known Bugs

### None Currently ✅

All known bugs have been fixed as of 2025-11-18.

---

## 🧹 Code Quality Improvements

### 1. Type Hints Coverage
**Current:** ~60% of functions have type hints
**Goal:** 90%+ coverage
**Benefits:** Better IDE support, fewer runtime errors
**Estimated effort:** 4-6 hours

---

### 2. Docstring Coverage
**Current:** Classes have docstrings, many methods don't
**Goal:** All public methods documented
**Benefits:** Better maintainability, auto-generated docs
**Estimated effort:** 3-4 hours

---

### 3. Magic Number Elimination
**Examples:**
- Hard-coded `10` for base AC in multiple places
- Hard-coded spell slot counts
- Hard-coded room counts in dungeon generation

**Fix:** Create constants module
**Estimated effort:** 2 hours

---

## 📊 Technical Debt Metrics

### Current State (2025-11-18)

**Code Health:**
- ✅ 158 automated tests (157/158 passing - 1 flaky)
- ✅ 3 manual tests (all passing)
- ✅ No critical bugs
- ✅ Core systems functional
- ⚠️ Debug print statements present
- ⚠️ Manual tests not integrated

**Test Coverage:**
| System | Automated Tests | Manual Tests | Total Coverage |
|--------|----------------|--------------|----------------|
| Parser | ✅ 43 tests | - | Excellent |
| Combat | ✅ 18 tests | - | Excellent |
| Game State | ✅ 19 tests | - | Good |
| Storage | ✅ 19 tests | - | Good |
| Armor System | ✅ 26 tests | - | Excellent |
| Ability Scores | ✅ 19 tests | - | Excellent |
| Integration | ✅ 14 tests | - | Good |
| Treasure | - | ✅ Manual | Fair |
| Magic Items | - | ✅ Manual | Fair |
| Traps | - | ✅ Manual | Fair |
| Multi-level | - | ✅ Manual | Fair |
| Village | - | - | None |
| Shops/Inns | - | - | None |

**Code Quality Metrics:**
- Lines of code: ~15,000
- Files: ~60
- Test files: 12 (9 automated + 3 manual)
- Documentation files: 12
- Data files: 10+ JSON files

---

## 🎯 Prioritized Action Plan

### Sprint 1: Cleanup & Stability (4-6 hours)
1. ✅ Fix Armor API issue (DONE)
2. ✅ Organize manual tests (DONE)
3. Fix flaky procedural test (15 min)
4. Remove debug print statements (30 min)
5. Archive/move feasibility docs (5 min)

### Sprint 2: Test Integration (8-10 hours)
1. Convert manual tests to unittest (3-4 hours)
2. Add village system tests (4-5 hours)
3. Integrate into CI/CD (1 hour)

### Sprint 3: Continue PH Integration (15-20 hours)
1. Task 1.5: Saving Throw Tables (3 hours)
2. Task 1.6: THAC0 Tables (2 hours)
3. Task 1.7: Experience/Leveling (4 hours)
4. Task 1.8: Racial Adjustments (2 hours)
5. Task 1.9: Class Restrictions (2 hours)
6. Task 1.10: HP Progression (2 hours)

### Sprint 4: Code Quality (6-8 hours)
1. Add type hints to remaining functions (4 hours)
2. Add docstrings to public methods (3 hours)
3. Extract magic numbers to constants (1 hour)

---

## 🔄 Refactoring Opportunities

### 1. Dungeon Generation
**Current:** Single-level focus, multi-level is separate
**Goal:** Unified multi-level system
**Benefits:** Consistent API, better architecture
**Estimated effort:** 6-8 hours
**Risk:** Medium (breaks existing saves)

---

### 2. Magic System
**Current:** spell effects scattered across multiple files
**Goal:** Centralized spell effect registry
**Benefits:** Easier to add new spells, better testability
**Estimated effort:** 4-6 hours
**Risk:** Low (internal refactor)

---

### 3. Item System
**Current:** Multiple item types with different APIs
**Goal:** Unified item interface with effect system
**Benefits:** Consistent behavior, easier to add items
**Estimated effort:** 8-10 hours
**Risk:** High (touches everything)

---

## 📝 Documentation Debt

### Missing Documentation
1. ~~API documentation for game systems~~ (covered in CLAUDE.md)
2. Dungeon JSON format specification
3. Save file format specification
4. Magic item creation guide
5. Monster creation guide

### Outdated Documentation
1. None identified (recent docs are up-to-date)

---

## 🚀 Performance Considerations

### Current Performance
- Test suite: 0.2 seconds (excellent)
- Game startup: < 1 second
- Command response: < 100ms
- Save/load: < 1 second

### No Performance Issues Identified ✅

---

## 🔒 Security Considerations

### Potential Issues
1. **Save file manipulation:** No validation of save file integrity
2. **JSON injection:** Dungeon/character JSON files could be maliciously crafted
3. **Path traversal:** File paths not sanitized in load operations

### Mitigation Priority: Low
**Reason:** Single-player game, local files only, no network component
**If network play added:** These become HIGH priority

---

## 📚 Related Documents

- `PLAYERS_HANDBOOK_INTEGRATION_PLAN.md` - Feature implementation roadmap
- `INTEGRATION_TEST_OPPORTUNITIES.md` - Test expansion ideas
- `tests_manual/README.md` - Manual test documentation
- `CLAUDE.md` - Development guide
- `TESTING.md` - Testing strategy
- `ARCHITECTURE.md` - System architecture

---

## 📊 Progress Tracking

### Recent Achievements (Last 7 Days)
- ✅ Implemented ability score tables with bonuses
- ✅ Completed armor system with class restrictions
- ✅ Expanded spell database from 7 to 332 spells
- ✅ Created equipment database (65 items)
- ✅ Built automated dungeon exploration tests (4 tests)
- ✅ Fixed Armor API compatibility issues
- ✅ Organized manual test files

### Test Count Growth
- 2024-11-11: 86 tests (79% passing)
- 2024-11-18: 158 tests (99% passing) - **83% growth!**

### Code Growth
- **+2,000 lines** of production code (spells, items, armor system)
- **+1,500 lines** of test code (integration tests)
- **+15 KB** of documentation

---

## 💡 Lessons Learned

### What Went Well
1. **Incremental integration:** Adding systems one at a time prevents breakage
2. **Test-first approach:** Writing tests first caught many issues early
3. **Documentation:** Comprehensive docs made onboarding easy
4. **Retry logic in tests:** Handles RNG variance effectively

### What Needs Improvement
1. **API consistency:** Armor API change broke compatibility
2. **Debug cleanup:** Should remove debug prints before committing
3. **Test organization:** Should integrate manual tests immediately
4. **Data validation:** Need JSON schema validation for data files

---

**Maintained by:** Development Team
**Review Schedule:** Weekly during active development
**Last Major Update:** 2025-11-18 (Armor API fix, test organization)
