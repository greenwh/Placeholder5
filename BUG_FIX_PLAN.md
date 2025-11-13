# Bug Fix Plan - Aerthos

**Date Created:** 2025-11-13
**Current Status:** All 109 tests passing (100%)
**Total Bugs Identified:** 12

---

## Executive Summary

This document outlines a comprehensive plan to fix 12 bugs identified through systematic code review. Bugs range from **critical security vulnerabilities** to **minor code quality issues**. The plan prioritizes fixes based on severity and impact.

### Bug Severity Distribution
- 🔴 **Critical:** 2 bugs (game-breaking, security issues)
- 🟠 **Major:** 3 bugs (functionality breaking)
- 🟡 **Moderate:** 3 bugs (edge cases)
- 🟢 **Minor:** 4 bugs (code quality)

---

## Phase 1: Critical Fixes (IMMEDIATE)

**Goal:** Eliminate game-breaking bugs and security vulnerabilities
**Timeline:** Complete before any user testing
**Test Strategy:** Run full test suite after each fix

### BUG-001: Division by Zero - XP Distribution (CRITICAL)
**Priority:** P0 - HIGHEST
**Severity:** 🔴 Critical
**Impact:** Game crashes when last party member dies from killing a monster

**Location:**
- `aerthos/engine/game_state.py:221`
- `aerthos/engine/game_state.py:473`

**Current Code:**
```python
xp_per_member = target.xp_value // len(self.party.get_living_members())
```

**Problem:**
If all party members die during combat, `get_living_members()` returns an empty list `[]`, causing:
```
ZeroDivisionError: integer division or modulo by zero
```

**Fix:**
```python
living_members = self.party.get_living_members()
if living_members:
    xp_per_member = target.xp_value // len(living_members)
    for member in living_members:
        level_up_msg = member.gain_xp(xp_per_member)
        if level_up_msg:
            messages.append(f"{member.name}: {level_up_msg}")
    messages.append(f"Party gains {target.xp_value} XP! ({xp_per_member} each)")
else:
    # Party wiped out - no XP awarded
    messages.append(f"The party has fallen! No XP awarded.")
```

**Testing:**
1. Create test case: party with 1 HP member kills monster that deals lethal damage
2. Verify no crash occurs
3. Verify appropriate message shown
4. Add unit test to `test_game_state.py`

**Files to Modify:**
- `aerthos/engine/game_state.py` (2 locations)
- `tests/test_game_state.py` (add test case)

---

### BUG-002: Security Vulnerability - Arbitrary Code Execution (CRITICAL)
**Priority:** P0 - HIGHEST
**Severity:** 🔴 Critical
**Impact:** Malicious JSON data files could execute arbitrary Python code

**Location:**
- `aerthos/engine/combat.py:33`

**Current Code:**
```python
# Handle flat modifiers like "4+1" (hit dice)
if 'd' not in dice_string:
    # It's just a flat number or number+modifier
    if '+' in dice_string or '-' in dice_string:
        return eval(dice_string)  # ⚠️ SECURITY RISK
    return int(dice_string)
```

**Problem:**
Using `eval()` on potentially user-controlled input allows arbitrary code execution. If a malicious JSON file contains:
```json
"hit_dice": "__import__('os').system('rm -rf /')"
```
This would execute on the system.

**Fix:**
```python
# Handle flat modifiers like "4+1" (hit dice)
if 'd' not in dice_string:
    # It's just a flat number or number+modifier
    if '+' in dice_string:
        try:
            parts = dice_string.split('+')
            if len(parts) == 2:
                return int(parts[0]) + int(parts[1])
        except (ValueError, IndexError):
            raise ValueError(f"Invalid dice notation: {dice_string}")
    elif '-' in dice_string:
        try:
            parts = dice_string.split('-')
            if len(parts) == 2:
                return int(parts[0]) - int(parts[1])
        except (ValueError, IndexError):
            raise ValueError(f"Invalid dice notation: {dice_string}")

    # Just a flat number
    try:
        return int(dice_string)
    except ValueError:
        raise ValueError(f"Invalid dice notation: {dice_string}")
```

**Testing:**
1. Test normal cases: "4", "4+1", "4-1"
2. Test malicious input: `"__import__('os').system('echo pwned')"` should raise ValueError
3. Test edge cases: "4+1+1", "abc", ""
4. Add security test to `tests/test_combat.py`

**Files to Modify:**
- `aerthos/engine/combat.py`
- `tests/test_combat.py` (add security tests)

---

## Phase 2: Major Fixes (HIGH PRIORITY)

**Goal:** Fix functionality-breaking bugs
**Timeline:** Complete within first sprint after critical fixes
**Test Strategy:** Run affected test modules after each fix

### BUG-003: Parameter Order Inconsistency - Session Creation (MAJOR)
**Priority:** P1 - High
**Severity:** 🟠 Major
**Impact:** Tests fail, sessions may be created with swapped data

**Location:**
- `aerthos/storage/session_manager.py:36-37`
- `tests/test_storage.py:513-516`

**Current Code:**
```python
# Function signature
def create_session(self, party_id: str, scenario_id: str,
                  session_name: str = None, session_id: str = None) -> str:

# Test calling it (WRONG ORDER)
session_id = self.session_manager.create_session(
    party_id,
    scenario_id,
    session_name="Session1"
)
```

**Problem:**
The positional arguments create confusion. Tests may be passing incorrect data.

**Fix - Make Keyword-Only:**
```python
def create_session(self, *, party_id: str, scenario_id: str,
                  session_name: str = None, session_id: str = None) -> str:
    """
    Create a new game session

    Args:
        party_id: ID of party to use (keyword-only)
        scenario_id: ID of scenario to play (keyword-only)
        session_name: Optional session name
        session_id: Optional ID (generates UUID if not provided)

    Returns:
        Session ID
    """
```

**Testing:**
1. Update all calls to use keyword arguments
2. Verify test_storage.py passes
3. Verify main.py session creation works
4. Add test for positional argument rejection

**Files to Modify:**
- `aerthos/storage/session_manager.py`
- `tests/test_storage.py`
- `main.py` (if it calls create_session)

---

### BUG-004: Type Hint Incompatibility (MAJOR)
**Priority:** P1 - High
**Severity:** 🟠 Major
**Impact:** Type checking failures on Python < 3.9

**Location:**
- `aerthos/entities/player.py:239`

**Current Code:**
```python
def can_use_weapon(self, weapon: Weapon) -> tuple[bool, str]:
```

**Problem:**
Lowercase `tuple` type hint requires Python 3.9+. Project targets Python 3.10+ but `Tuple` from typing is already imported for clarity.

**Fix:**
```python
def can_use_weapon(self, weapon: Weapon) -> Tuple[bool, str]:
```

**Testing:**
1. Run mypy type checking
2. Verify no type errors
3. Ensure backward compatibility

**Files to Modify:**
- `aerthos/entities/player.py`

---

### BUG-005: Missing File Exception Handling (MAJOR)
**Priority:** P1 - High
**Severity:** 🟠 Major
**Impact:** Corrupted JSON files crash the game instead of graceful handling

**Locations:**
- `aerthos/storage/character_roster.py:98`, `122`, `189`
- `aerthos/storage/party_manager.py:89`, `137`, `189`
- `aerthos/storage/scenario_library.py:125`, `150`, `177`
- `aerthos/storage/session_manager.py:102`, `137`, `154`

**Current Code Pattern:**
```python
with open(filepath, 'r') as f:
    data = json.load(f)
```

**Problem:**
No exception handling for:
- `FileNotFoundError` - File deleted between glob and open
- `json.JSONDecodeError` - Corrupted JSON
- `PermissionError` - File permissions changed
- `OSError` - Disk issues

**Fix Pattern:**
```python
try:
    with open(filepath, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Warning: {filepath} not found (may have been deleted)")
    continue  # or return None
except json.JSONDecodeError as e:
    print(f"Error: {filepath} contains invalid JSON: {e}")
    continue  # or return None
except PermissionError:
    print(f"Error: Permission denied reading {filepath}")
    continue  # or return None
except OSError as e:
    print(f"Error reading {filepath}: {e}")
    continue  # or return None
```

**Testing:**
1. Create corrupted JSON file in test directory
2. Verify graceful handling
3. Create test with permission denied
4. Verify error messages are user-friendly

**Files to Modify:**
- `aerthos/storage/character_roster.py` (3 locations)
- `aerthos/storage/party_manager.py` (3 locations)
- `aerthos/storage/scenario_library.py` (3 locations)
- `aerthos/storage/session_manager.py` (3 locations)
- `tests/test_storage.py` (add corruption tests)

---

## Phase 3: Moderate Fixes (MEDIUM PRIORITY)

**Goal:** Fix edge cases and improve robustness
**Timeline:** Complete in second sprint
**Test Strategy:** Add edge case tests for each fix

### BUG-006: Index Out of Bounds - Party Formation (MODERATE)
**Priority:** P2 - Medium
**Severity:** 🟡 Moderate
**Impact:** Crash when accessing party formation after member removal

**Location:**
- `aerthos/entities/party.py:93`
- `aerthos/entities/party.py:97`

**Current Code:**
```python
def get_front_line(self) -> List[PlayerCharacter]:
    return [self.members[i] for i, pos in enumerate(self.formation) if pos == 'front']

def get_back_line(self) -> List[PlayerCharacter]:
    return [self.members[i] for i, pos in enumerate(self.formation) if pos == 'back']
```

**Problem:**
If `formation` and `members` lists get out of sync (bug in remove_member, save/load corruption), IndexError occurs.

**Fix:**
```python
def get_front_line(self) -> List[PlayerCharacter]:
    """Get front-line party members (safe with list sync)"""
    return [member for member, pos in zip(self.members, self.formation) if pos == 'front']

def get_back_line(self) -> List[PlayerCharacter]:
    """Get back-line party members (safe with list sync)"""
    return [member for member, pos in zip(self.members, self.formation) if pos == 'back']
```

**Additional Fix - Add Validation:**
```python
def _validate_formation_sync(self):
    """Ensure members and formation lists are synchronized"""
    if len(self.members) != len(self.formation):
        # Auto-repair: regenerate formation
        self.formation = []
        for member in self.members:
            if member.char_class in ['Fighter', 'Cleric']:
                self.formation.append('front')
            else:
                self.formation.append('back')
```

**Testing:**
1. Create test with mismatched formation/members
2. Verify no crash
3. Test remove_member maintains sync
4. Add validation tests

**Files to Modify:**
- `aerthos/entities/party.py`
- `tests/test_game_state.py` (add party formation tests)

---

### BUG-007: Empty Party XP Distribution (MODERATE)
**Priority:** P2 - Medium
**Severity:** 🟡 Moderate
**Impact:** Crash if all party members dead when XP awarded

**Location:**
- `aerthos/entities/party.py:129`

**Current Code:**
```python
def distribute_xp(self, xp_amount: int):
    living = self.get_living_members()
    if not living:
        return

    xp_per_member = xp_amount // len(living)  # Already has check above
```

**Status:**
Check exists on lines 126-127, but could be more defensive for clarity.

**Fix:**
```python
def distribute_xp(self, xp_amount: int):
    """
    Distribute XP equally among living party members

    Args:
        xp_amount: Total XP to distribute
    """
    living = self.get_living_members()
    if not living:
        # No living members to award XP
        return

    xp_per_member = xp_amount // len(living)

    for member in living:
        member.gain_xp(xp_per_member)
```

**Testing:**
1. Test with all dead party
2. Test with 1 living member
3. Verify XP distributed correctly

**Files to Modify:**
- `aerthos/entities/party.py` (minor comment improvement)
- `tests/test_game_state.py` (ensure test coverage)

---

### BUG-008: Cast Spell Parser Edge Case (MODERATE)
**Priority:** P2 - Medium
**Severity:** 🟡 Moderate
**Impact:** Multi-word spell names only match first word

**Location:**
- `aerthos/engine/parser.py:187-189`

**Current Code:**
```python
if cast_idx >= 0 and cast_idx + 1 < len(tokens):
    spell_name = tokens[cast_idx + 1]  # Only gets first word
    return spell_name
```

**Problem:**
For "cast cure light wounds", only returns "cure" instead of "cure light wounds"

**Investigation Needed:**
Check if this is intentional design or bug. The spell matching system uses partial matching:
- `player.py:346` - `search_lower in slot.spell.name.lower()`

So "cure" would match "Cure Light Wounds". This may be WORKING AS INTENDED.

**Recommendation:**
Document this behavior and ensure it's consistent. If multi-word support needed:

**Fix (if needed):**
```python
if cast_idx >= 0 and cast_idx + 1 < len(tokens):
    # Get all tokens after 'cast' until 'on' or 'at'
    spell_tokens = []
    for i in range(cast_idx + 1, len(tokens)):
        if tokens[i] in ['on', 'at']:
            break
        spell_tokens.append(tokens[i])
    spell_name = ' '.join(spell_tokens)
    return spell_name
```

**Testing:**
1. Test "cast cure"
2. Test "cast cure light wounds"
3. Test "cast magic missile at goblin"
4. Determine if current behavior is acceptable

**Files to Modify:**
- `aerthos/engine/parser.py` (potentially)
- Document spell naming convention

---

## Phase 4: Minor Fixes (LOW PRIORITY)

**Goal:** Improve code quality and maintainability
**Timeline:** Complete in third sprint or as time permits
**Test Strategy:** Add validation tests

### BUG-009: No Validation - Party Size on Load (MINOR)
**Priority:** P3 - Low
**Severity:** 🟢 Minor
**Impact:** Corrupted save files could create invalid party states

**Location:**
- `aerthos/storage/party_manager.py:50-54` (validation in save)
- `aerthos/storage/party_manager.py:73-125` (no validation in load)

**Current Code:**
```python
def save_party(self, ...):
    # Validation exists here
    if len(character_ids) != len(formation):
        raise ValueError("...")
    if len(character_ids) < 1 or len(character_ids) > 6:
        raise ValueError("...")

def load_party(self, ...):
    # No validation here
```

**Fix:**
```python
def load_party(self, party_id: str = None, party_name: str = None):
    # ... existing load code ...

    if not party_data:
        return None

    # Validate loaded data
    character_ids = party_data.get('character_ids', [])
    formation = party_data.get('formation', [])

    if len(character_ids) != len(formation):
        print(f"Warning: Party {party_data['name']} has mismatched formation. Auto-repairing...")
        # Auto-repair formation
        formation = ['front' if i < 2 else 'back' for i in range(len(character_ids))]
        party_data['formation'] = formation

    if not (1 <= len(character_ids) <= 6):
        print(f"Warning: Party {party_data['name']} has invalid size {len(character_ids)}")
        if len(character_ids) > 6:
            print(f"Truncating party to 6 members")
            character_ids = character_ids[:6]
            formation = formation[:6]
        elif len(character_ids) == 0:
            print(f"Error: Party is empty, cannot load")
            return None

    # ... continue with load ...
```

**Testing:**
1. Create corrupted party JSON
2. Verify auto-repair works
3. Test edge cases (0 members, 10 members)

**Files to Modify:**
- `aerthos/storage/party_manager.py`
- `tests/test_storage.py`

---

### BUG-010: GameData Not Loaded Warning (MINOR)
**Priority:** P3 - Low
**Severity:** 🟢 Minor
**Impact:** Silent failure - monsters don't spawn, no error shown

**Location:**
- `aerthos/engine/game_state.py:958`
- `aerthos/engine/game_state.py:992`

**Current Code:**
```python
def _create_monster_from_id(self, monster_id: str) -> Optional[Monster]:
    if not self.game_data or monster_id not in self.game_data.monsters:
        return None  # Silent failure
```

**Fix:**
```python
import logging

def _create_monster_from_id(self, monster_id: str) -> Optional[Monster]:
    if not self.game_data:
        logging.error("GameData not loaded! Call load_game_data() first.")
        return None

    if monster_id not in self.game_data.monsters:
        logging.warning(f"Monster '{monster_id}' not found in game data.")
        return None
```

**Testing:**
1. Test with game_data not loaded
2. Test with invalid monster_id
3. Verify appropriate warnings shown

**Files to Modify:**
- `aerthos/engine/game_state.py`
- Add logging configuration to game initialization

---

### BUG-011: Missing Null Checks - Current Room (MINOR)
**Priority:** P3 - Low
**Severity:** 🟢 Minor
**Impact:** Crash if dungeon state corrupted

**Location:**
- `aerthos/engine/game_state.py:152` and many other locations

**Current Code:**
```python
room_desc = self.current_room.on_enter(self.player.has_light(), self.player)
```

**Problem:**
No check if `self.current_room` is None. Could happen if:
- Save file corrupted
- Dungeon loading failed
- Room deleted from dungeon

**Fix - Add Property:**
```python
@property
def current_room(self) -> Room:
    """Get current room with null safety"""
    if self._current_room is None:
        raise RuntimeError("No current room set! Game state is corrupted.")
    return self._current_room

@current_room.setter
def current_room(self, room: Room):
    """Set current room"""
    if room is None:
        raise ValueError("Cannot set current room to None")
    self._current_room = room
```

**Testing:**
1. Test with None current_room
2. Verify clear error message
3. Test save/load maintains room reference

**Files to Modify:**
- `aerthos/engine/game_state.py`

---

### BUG-012: JSON Load Race Condition (MINOR)
**Priority:** P3 - Low
**Severity:** 🟢 Minor
**Impact:** Potential race condition if file system changes during iteration

**Location:**
- `aerthos/storage/character_roster.py:189-194`
- `aerthos/storage/party_manager.py:189-194`
- Similar pattern in all storage files

**Current Code:**
```python
for filepath in self.roster_dir.glob('*.json'):
    with open(filepath, 'r') as f:
        data = json.load(f)
        if data['id'] == character_id:
            filepath.unlink()  # Delete while iterating
            return True
```

**Problem:**
Deleting file during iteration over glob results could cause issues on some filesystems.

**Fix:**
```python
for filepath in self.roster_dir.glob('*.json'):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            if data['id'] == character_id:
                # Store path, delete after iteration
                found_path = filepath
                break
    except (FileNotFoundError, json.JSONDecodeError):
        continue

if found_path:
    found_path.unlink()
    return True

return False
```

**Testing:**
1. Test deletion while files are being created
2. Stress test with concurrent access
3. Verify no filesystem errors

**Files to Modify:**
- `aerthos/storage/character_roster.py`
- `aerthos/storage/party_manager.py`
- `aerthos/storage/scenario_library.py`
- `aerthos/storage/session_manager.py`

---

## Implementation Strategy

### Sprint 1: Critical & Major Fixes (Week 1)
**Goal:** Eliminate all critical and major bugs

**Day 1-2:**
- BUG-001: Division by zero (P0)
- BUG-002: Security eval() (P0)
- Run full test suite after each fix

**Day 3-4:**
- BUG-003: Parameter order (P1)
- BUG-004: Type hints (P1)
- Run full test suite

**Day 5:**
- BUG-005: Exception handling (P1)
- Add comprehensive error handling tests
- Run full test suite
- **Sprint 1 Complete**

### Sprint 2: Moderate Fixes (Week 2)
**Goal:** Fix edge cases and improve robustness

**Day 1-2:**
- BUG-006: Party formation (P2)
- BUG-007: Empty party XP (P2)

**Day 3-4:**
- BUG-008: Spell parser investigation and fix (P2)
- Add edge case tests

**Day 5:**
- Full regression testing
- Performance testing
- **Sprint 2 Complete**

### Sprint 3: Minor Fixes & Polish (Week 3)
**Goal:** Code quality improvements

**Day 1:**
- BUG-009: Party validation (P3)
- BUG-010: GameData logging (P3)

**Day 2:**
- BUG-011: Null checks (P3)
- BUG-012: Race conditions (P3)

**Day 3-5:**
- Code review
- Documentation updates
- Final testing
- **Sprint 3 Complete**

---

## Testing Strategy

### After Each Fix:
1. Run unit tests for affected module
2. Run integration tests
3. Run full test suite (all 109 tests)
4. Manual smoke test

### After Each Phase:
1. Full regression test
2. Performance benchmarking
3. Memory leak checks
4. User acceptance testing

### Quality Gates:
- **Phase 1:** 100% tests passing, no security vulnerabilities
- **Phase 2:** 100% tests passing, edge cases covered
- **Phase 3:** 100% tests passing, code coverage > 80%

---

## Risk Mitigation

### High-Risk Changes:
- BUG-002 (eval replacement): Extensive testing of dice notation
- BUG-005 (exception handling): Verify error messages are user-friendly
- BUG-006 (party formation): Ensure backward compatibility with saves

### Rollback Plan:
- Each fix committed separately with descriptive message
- Tag each phase completion
- Maintain bug-fix branch separate from main
- Can revert individual commits if regression detected

---

## Success Criteria

### Phase 1 Complete:
- ✅ No critical bugs remaining
- ✅ No security vulnerabilities
- ✅ All 109 tests passing

### Phase 2 Complete:
- ✅ No major bugs remaining
- ✅ Edge cases handled gracefully
- ✅ All 109+ tests passing (added edge case tests)

### Phase 3 Complete:
- ✅ All bugs fixed
- ✅ Code quality improved
- ✅ Documentation updated
- ✅ All 120+ tests passing

---

## Appendix: Bug Reference Table

| ID | Severity | Priority | Location | Status |
|----|----------|----------|----------|--------|
| BUG-001 | 🔴 Critical | P0 | game_state.py:221, 473 | Pending |
| BUG-002 | 🔴 Critical | P0 | combat.py:33 | Pending |
| BUG-003 | 🟠 Major | P1 | session_manager.py:36 | Pending |
| BUG-004 | 🟠 Major | P1 | player.py:239 | Pending |
| BUG-005 | 🟠 Major | P1 | All storage files | Pending |
| BUG-006 | 🟡 Moderate | P2 | party.py:93, 97 | Pending |
| BUG-007 | 🟡 Moderate | P2 | party.py:129 | Pending |
| BUG-008 | 🟡 Moderate | P2 | parser.py:187 | Pending |
| BUG-009 | 🟢 Minor | P3 | party_manager.py:73 | Pending |
| BUG-010 | 🟢 Minor | P3 | game_state.py:958, 992 | Pending |
| BUG-011 | 🟢 Minor | P3 | game_state.py:152 | Pending |
| BUG-012 | 🟢 Minor | P3 | All storage files | Pending |

---

**Document Version:** 1.0
**Last Updated:** 2025-11-13
**Next Review:** After Phase 1 completion
