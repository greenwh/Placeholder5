# Feature Implementation Roadmap

## Overview

This document outlines the implementation plan for three major features based on Gold Box game mechanics and AD&D 1e design principles.

**Implementation Order (by priority):**
1. **Formation-Based Combat** (5-7 hours) - Priority 1
2. **Party-Aware Dungeon Generation** (6-9 hours) - Priority 2
3. **Multi-Level Dungeon Integration** (10-13 hours) - Priority 3

**Total Estimated Time: 21-29 hours**

---

## Priority 1: Formation-Based Combat (5-7 hours)

### Problem
Current combat targeting is completely random. Monsters attack any party member with equal probability, making formation cosmetic.

### Solution
Implement Gold Box-style formation mechanics where:
- Monsters preferentially attack front-line (70% of attacks)
- Back-line protected when front-line standing (20% targeting)
- Opportunistic attacks on wounded/low AC targets (10%)
- Monster intelligence affects behavior

### Reference Documents
- `combat_order_resolution.md` - Gold Box combat mechanics

### Detailed Plan
See `FEATURE_PLAN_FORMATION_COMBAT.md`

### Success Metrics
- Front-line characters absorb 70%+ of attacks
- Back-line mages/clerics survive longer
- Formation commands work (`formation`, `formation <name> front/back`)
- Combat narrative shows formation-aware targeting

---

## Priority 2: Party-Aware Dungeon Generation (6-9 hours)

### Problem
Dungeons generated with hardcoded difficulty (party_level 1 or 2) regardless of actual party composition. No scaling to player strength.

### Solution
Implement simple 4-question interview system:
1. Average Party Level (APL) - most important
2. Party Size
3. Party Composition (fighters/mages/clerics/thieves)
4. Magic Item Level (none/low/medium/high)

Accept non-answers, make educated guesses, auto-detect from party if available.

### Reference Documents
- `scenario_generation_difficulty_determination.md` - Gold Box difficulty scaling
- `docs/game_enhancement_docs/DM_Guide_Adventure_Creation.md` - AD&D adventure design

### Detailed Plan
See `FEATURE_PLAN_PARTY_AWARE_DUNGEONS.md`

### Success Metrics
- Interview completes in <2 minutes
- Can skip all questions (smart defaults)
- Party detection pre-fills answers
- Monster pools scale to actual party level
- Warnings shown for underprepared parties

---

## Priority 3: Multi-Level Dungeon Integration (10-13 hours)

### Problem
Multi-level dungeon code exists but not integrated into gameplay. Players stuck with single-level dungeons only.

### Solution
Integrate existing `MultiLevelGenerator` and `MultiLevelDungeon` classes:
- Add stairs navigation (up/down commands)
- Support 2-3 level dungeons
- Difficulty scales with depth (deeper = harder)
- Automap shows current level
- Save/load preserves level position

### Reference Documents
- `docs/game_enhancement_docs/DM_Guide_Adventure_Creation.md` - Appendix A stairs tables

### Detailed Plan
See `FEATURE_PLAN_MULTILEVEL_DUNGEONS.md`

### Success Metrics
- Can select multi-level from dungeon menu
- Stairs navigation works (up/down)
- Deeper levels have harder monsters
- Automap shows level indicator
- Save/load preserves position

---

## Implementation Strategy

### Phase-Based Approach
Each feature broken into phases (1-9 phases per feature):
- Early phases are core functionality
- Later phases are polish and testing
- Can pause between phases to reassess

### Testing Requirements
**Critical:** Every feature phase includes testing
- Unit tests for new systems
- Integration tests for game flow
- Regression tests (all 367 existing tests must pass)
- Manual playthrough validation

### Incremental Delivery
Features can be delivered independently:
- Formation combat works alone
- Party-aware dungeons work alone
- Multi-level dungeons work alone
- But all three together create complete Gold Box experience

---

## Task List (19 Tasks Total)

### Priority 1: Formation-Based Combat (5 tasks)
1. ✅ Create Monster Targeting AI system (2-3 hours)
2. ✅ Implement formation mechanics in Party and Combat (1-2 hours)
3. ✅ Add visual feedback for formation in combat (1 hour)
4. ✅ Add formation commands to parser (30 minutes)
5. ✅ Create tests and verify all pass (1 hour)

### Priority 2: Party-Aware Dungeons (5 tasks)
6. ✅ Create dungeon interview system (2-3 hours)
7. ✅ Create party analyzer system (1-2 hours)
8. ✅ Enhance DungeonConfig for dynamic scaling (1-2 hours)
9. ✅ Integrate interview into main menu flow (1 hour)
10. ✅ Add readiness warnings and testing (1 hour)

### Priority 3: Multi-Level Dungeons (9 tasks)
11. ✅ Review existing multi-level code (1 hour)
12. ✅ Add multi-level support to GameState (2-3 hours)
13. ✅ Add stairs commands to parser (30 minutes)
14. ✅ Update Room class for stairs support (1 hour)
15. ✅ Integrate multi-level generation in main menu (2 hours)
16. ✅ Update automap for multi-level display (1-2 hours)
17. ✅ Add save/load multi-level support (1 hour)
18. ✅ Implement depth-based difficulty scaling (1 hour)
19. ✅ Create tests and verify all pass (2 hours)

---

## Files Affected (Summary)

### New Files Created (7)
- `aerthos/systems/monster_ai.py`
- `aerthos/ui/dungeon_interview.py`
- `aerthos/systems/party_analyzer.py`
- `tests/test_formation_combat.py`
- `tests/test_party_aware_dungeons.py`
- `tests/test_multilevel_dungeons.py`
- (This roadmap document)

### Files Modified (12)
- `aerthos/engine/combat.py`
- `aerthos/entities/party.py`
- `aerthos/ui/display.py`
- `aerthos/ui/character_sheet.py`
- `aerthos/engine/parser.py`
- `aerthos/constants.py`
- `aerthos/generator/config.py`
- `main.py`
- `aerthos/engine/game_state.py`
- `aerthos/world/room.py`
- `aerthos/world/automap.py`
- `aerthos/ui/save_system.py`

### Files Reviewed (1)
- `aerthos/generator/multilevel_generator.py`

---

## Risk Assessment

### High Risk Areas
1. **Combat AI complexity** - Could get too complicated
   - Mitigation: Keep to 3 simple targeting modes

2. **Interview tedium** - Too many questions
   - Mitigation: 4 questions max, all skippable

3. **Multi-level backward compatibility** - Breaking saves
   - Mitigation: Check dungeon type, support both formats

### Medium Risk Areas
1. **Monster targeting balance** - Front-line becomes meat grinder
   - Mitigation: 20% back-line targeting, opportunistic attacks

2. **Difficulty scaling** - Wrong calculations
   - Mitigation: Use existing MonsterScaler, test thoroughly

### Low Risk Areas
1. **Parser commands** - Well-established pattern
2. **Display formatting** - Non-critical, easy to fix
3. **Constants** - Safe additions

---

## Testing Strategy

### Unit Test Coverage
- Monster AI target selection (12 tests)
- Party analysis and detection (10 tests)
- Interview defaults and validation (8 tests)
- Multi-level navigation (12 tests)
- **Total new tests: 42+**

### Integration Test Coverage
- Full combat with formation (Priority 1)
- End-to-end party-aware dungeon generation (Priority 2)
- Multi-level dungeon playthrough (Priority 3)

### Regression Testing
- All 367 existing tests must pass after each priority
- No breaking changes to existing gameplay
- Single-player and party modes both work

---

## Success Criteria (Overall)

### Priority 1 Complete When:
✅ Front-line characters take 70%+ of attacks
✅ Formation commands work
✅ Combat narrative reflects targeting logic
✅ All tests pass (367 existing + 12 new)

### Priority 2 Complete When:
✅ Interview completes with smart defaults
✅ Dungeons scale to actual party level
✅ Monster pools appropriate for party
✅ All tests pass (379 existing + 10 new)

### Priority 3 Complete When:
✅ Multi-level dungeons selectable and playable
✅ Stairs navigation works correctly
✅ Difficulty scales with depth
✅ All tests pass (389 existing + 12 new)

### All Features Complete When:
✅ Gold Box-style combat with formation tactics
✅ Dynamic dungeon difficulty matching party
✅ Multi-level exploration with vertical progression
✅ **All 411+ tests passing**
✅ No regression in existing features
✅ Game feels more tactical and balanced

---

## Timeline Estimate

**Minimum (best case): 21 hours**
- Priority 1: 5 hours
- Priority 2: 6 hours
- Priority 3: 10 hours

**Maximum (worst case): 29 hours**
- Priority 1: 7 hours
- Priority 2: 9 hours
- Priority 3: 13 hours

**Realistic (with debugging): 25 hours**
- Priority 1: 6 hours
- Priority 2: 7 hours
- Priority 3: 12 hours

**Estimated completion time: 1-2 weeks of development**

---

## Next Steps

1. Review all three feature plans
2. Begin Priority 1 (Formation-Based Combat)
3. Complete and test Priority 1 before moving to Priority 2
4. Verify no regressions between priorities
5. Document any design decisions or changes

**Ready to start? Begin with:**
```
PRIORITY 1 - Phase 1: Create Monster Targeting AI system
See: FEATURE_PLAN_FORMATION_COMBAT.md
```
