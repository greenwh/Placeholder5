# Bug Fixes - 2025-11-20

## Issue 1: JSON Serialization Error ✓ FIXED

**Problem:**
```
TypeError: Object of type set is not JSON serializable
```

When saving the game, the save system tried to serialize `player.conditions` which is a Python `set`. JSON doesn't support sets, only lists and dicts.

**Root Cause:**
- `aerthos/ui/save_system.py` line 135: `'conditions': player.conditions`
- `player.conditions` is implemented as a set for efficient lookup
- JSON encoder cannot serialize sets

**Fix:**
- Modified `aerthos/ui/save_system.py` line 135
- Changed: `'conditions': player.conditions`
- To: `'conditions': list(player.conditions)  # Convert set to list for JSON`

**Verification:**
- All 472 tests pass
- No regression

**Files Changed:**
- `aerthos/ui/save_system.py` (1 line)

---

## Issue 2: No Way to Switch Active Character in CLI Party Mode ✓ FIXED

**Problem:**
When playing with a party in CLI mode, the game shows `[Active: CharacterName]` but provides no way to switch control to other party members.

**Root Cause:**
- Party gameplay was implemented but character switching was never added
- The `run_game_with_party()` function sets `player = party.members[0]` but has no mechanism to change it

**Fix:**
Added character switching directly in the party game loop (`main.py` lines 1323-1336):
- Press **1-6** to switch to party member 1-6
- Validates member exists in party
- Checks if character is alive before switching
- Updates both local `player` variable and `game_state.player` reference
- Shows confirmation message: `✓ Switched to {player.name}`

**Enhancement:**
Added helpful tip to party roster display (line 1296):
```
Tip: Press 1-6 to switch active character during gameplay.
```

**Usage:**
```
YOUR PARTY:
  1. Thorin (Dwarf Fighter) [FRONT]
  2. Elara (Elf Magic-User) [REAR]
  3. Gimble (Halfling Thief) [FRONT]
  4. Brother Marcus (Human Cleric) [REAR]

Tip: Press 1-6 to switch active character during gameplay.

[Active: Thorin]
> 2
✓ Switched to Elara

[Active: Elara]
> cast magic missile
...
```

**Verification:**
- All 472 tests pass
- Feature works as expected in manual testing

**Files Changed:**
- `main.py` (2 sections: game loop + party roster display)

---

## Test Results

All tests passing: **472/472** ✓

```
Total Tests Run:    472
Passed:            472
Failed:            0
Errors:            0
Skipped:           0
```

Both fixes are production-ready and tested.
