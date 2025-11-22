## FIXED BUGS (2025-11-22)

### Round 1: Initial Fixes

 **FIXED: Weight conversion issue**
- Converted all weight_gp values to pounds (10 GP = 1 lb)
- Fixed in armor_system.py (armor and shield creation)
- Fixed in character_creation.py (hardcoded starting equipment)
- Updated test expectations in test_armor_system.py
- **Result:** Weights now display correctly in both CLI and Web UI

 **FIXED: Serialization attribute mismatch**
- Fixed character_roster.py serialization/deserialization
- Armor uses `ac` (not `ac_bonus`)
- Shield uses `ac_bonus`
- Added Shield to imports
- **Result:** Characters can be saved and loaded without errors

 **FIXED: Equipment database source - items.json removed**
- **Removed items.json from codebase** (deprecated)
- Removed GameData.items attribute
- Removed create_item_from_data() function from main.py
- Updated test_game_state.py to not check for items.json
- Updated game_state.py with comment about deprecated items.json
- **Web UI NEW GAME uses correct sources:**
  - Character creation via CharacterCreator.quick_create()
  - Uses _add_starting_equipment() which was already fixed
  - armor.json via ArmorSystem (correct weights)
  - weapons.json for detailed weapon data
  - equipment.json for general equipment

**All systems now use proper specialized databases with correct GP�pound conversion:**
-  CLI character creation
-  Web UI character creation
-  Character roster save/load
-  Quick play mode

### Round 2: Web UI Fixes

 **FIXED: Web UI "take item" command error**
- **Error:** `AttributeError: 'GameData' object has no attribute 'items'` when taking items in web UI
- **Fix:** Replaced _create_item_from_name() in game_state.py with simple item factory
- No longer depends on items.json
- Factory creates common dungeon items with pattern matching:
  - Torches (0.1 lbs)
  - Rations (0.1 lbs)
  - Healing potions (0.05 lbs)
  - Gold coins (0.1 lbs)
  - Gems (0.01 lbs)
  - Rope (0.5 lbs)
  - Backpacks (2.0 lbs)
  - Generic items (0.1 lbs default)
- All items use correct GP�pound weight conversion
- **Result:** Can now take items from rooms in web UI without errors

 **FIXED: Unequip command not recognized**
- **Error:** "I don't understand that command" when trying to unequip items
- **Fix:** Added 'unequip' command to parser with synonyms:
  - unequip, remove, doff, unwear, unwield
- Added _handle_unequip() handler in game_state.py
- Properly handles unequipping:
  - Weapons
  - Armor (recalculates AC)
  - Shields (recalculates AC)
  - Light sources
- **Result:** Can now unequip items in both CLI and web UI

### Round 3: Shield Equip/Unequip Fix

✅ **FIXED: Can't equip shield after unequipping**
- **Error:** "You can't equip the Small Shield" after unequipping it
- **Root cause:** Shield is a separate class (not Armor), wasn't checked in _handle_equip()
- **Fix:** Added Shield type check in _handle_equip() handler
  - Added `isinstance(item, Shield)` check
  - Handles shield-specific AC recalculation
  - Added Shield to imports in game_state.py
- **Result:** Can now equip/unequip shields repeatedly

✅ **ADDED: CLI/Web UI Synchronization Rule to CLAUDE.md**
- Added prominent mandatory rule section
- Checklist for all code changes
- Examples of what needs to be synced
- Testing workflow for both UIs
- **Location:** CLAUDE.md lines 113-127

### Round 4: Web UI Combat Buttons

✅ **FIXED: Defend and Pass Turn buttons not working**
- **Error:** "I don't understand that command" for Defend and Pass Turn buttons in web UI
- **Root cause:** Commands 'defend' and 'wait' not defined in parser
- **Fix:**
  - Added 'defend' command to parser with synonyms: defend, parry, block, guard
  - Added 'wait' command to parser with synonyms: wait, pass, skip
  - Implemented _handle_defend() - gives -2 AC bonus for defensive stance in combat
  - Implemented _handle_wait() - passes turn, monsters still attack
  - Both handlers work in and out of combat
- **Files:** `aerthos/engine/parser.py:33-34`, `aerthos/engine/game_state.py:124-125,369-440`
- **Result:** Defend (🛡️) and Pass Turn (⏸️) buttons now work in web UI (and CLI)

### Files Modified
1. `aerthos/systems/armor_system.py` - Weight conversion (4 locations)
2. `aerthos/ui/character_creation.py` - Weight conversion (8 locations)
3. `aerthos/storage/character_roster.py` - Serialization fixes (6 locations)
4. `aerthos/engine/game_state.py` - Removed items.json loading, added item factory, added unequip handler, fixed shield equip, added defend/wait handlers
5. `aerthos/engine/parser.py` - Added unequip, defend, and wait commands
6. `main.py` - Removed create_item_from_data()
7. `tests/test_armor_system.py` - Updated weight expectations
8. `tests/test_game_state.py` - Removed items.json checks
9. `CLAUDE.md` - Added mandatory CLI/Web UI sync rule

### Test Results
 **All 374 tests passing**

### Summary
All bugs fixed! The game now:
-  Shows correct item weights in pounds (not GP)
-  Can save and load characters without errors
-  Uses specialized databases (armor.json, weapons.json, equipment.json)
-  Can take items from rooms in web UI
-  Can unequip items in both CLI and web UI
-  No longer depends on deprecated items.json

**Updated Summary (Round 4):**
- ✅ Defend and Pass Turn buttons now work
- ✅ Can equip/unequip shields repeatedly
- ✅ All combat actions functional in web UI

### Round 5: Defend Message Improvements

✅ **FIXED: Defend message shows actual AC change**
- **Issue:** Message said "Your AC improves to 8" when character was at AC 4 (confusing)
- **Root cause:** Message only showed final AC, not the actual change from X to Y
- **Fix:** Changed message to show "AC improves from X to Y for this round"
  - Added character name to clarify which party member is defending
  - Updated docstring to clarify defense applies to active character only
- **File:** `aerthos/engine/game_state.py:369-382`
- **Result:** Players see clear AC transition (e.g., "AC improves from 4 to 2")

✅ **FIXED: AC not calculated when equipping armor**
- **Issue:** Defend showed "AC improves from 10 to 8" even when character had Chain Mail (AC 5) and Shield
- **Root cause 1:** `equip_armor()` method only set equipment slot, never recalculated `self.player.ac`
- **Root cause 2:** Starting equipment in character creation also never calculated AC
- **Discovery:** Shield equip DID recalculate AC, but Armor equip did not
- **Fix 1 - Manual equip during gameplay:** Added AC recalculation to armor equip in `_handle_equip()`
  - Sets `self.player.ac = item.ac` (armor's base AC)
  - Subtracts shield bonus if shield is equipped
  - Mirrors the logic already present in shield equip
- **Fix 2 - Character creation:** Added AC calculation to `_add_starting_equipment()`
  - Fighter/Cleric: `player.ac = chain.ac - shield.ac_bonus` (5 - 1 = AC 4)
  - Thief: `player.ac = leather.ac` (AC 8)
  - Magic-User/Monk: Keep default AC 10 (no armor)
- **Files:**
  - `aerthos/engine/game_state.py:567-573` (manual equip)
  - `aerthos/ui/character_creation.py:419-422, 434-437, 456-458` (starting equipment)
- **Result:** AC now correctly reflects equipped armor and shield
  - Chain Mail (AC 5) + Shield (+1) = AC 4 ✓
  - Defend message now shows correct current AC: "AC improves from 4 to 2" ✓
  - Quick Play characters start with correct AC ✓

✅ **FIXED: Save system crash on corrupted save files**
- **Issue:** JSONDecodeError when trying to save - "Expecting value: line 23 column 19"
- **Root cause:** Old corrupted save file (save_1.json) with incomplete JSON (truncated at "conditions": with no value)
- **Fix:** Added error handling to save system
  - `list_saves()`: Catches JSONDecodeError, KeyError, IOError and skips corrupted saves
  - `load_game()`: Catches JSONDecodeError, IOError and returns None for corrupted saves
  - Logs warnings instead of crashing
- **Files:** `aerthos/ui/save_system.py:82-97, 65-70`
- **Result:** Save system gracefully handles corrupted files instead of crashing
- **Cleanup:** Deleted corrupted save_1.json file

**Updated Summary (Round 5):**
- ✅ Defend message now shows clear AC change (from X to Y)
- ✅ Character name identifies who is defending
- ✅ AC properly calculated when equipping armor (manual + character creation)
- ✅ AC properly calculated when equipping shield (already worked)
- ✅ AC properly restored when unequipping armor or shield (already worked)
- ✅ Save system handles corrupted files gracefully
- ✅ All 374 tests passing
