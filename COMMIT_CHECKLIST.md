# Commit Checklist for Aerthos

## Before Committing ANY Code Changes

### 🔴 CRITICAL: CLI and Web UI Synchronization

**IF** you modified code in **ANY** of these areas:
- Character creation (`aerthos/ui/character_creation.py`)
- Combat resolution (`aerthos/engine/combat.py`)
- Item/equipment handling (`aerthos/entities/player.py`, equipment systems)
- Spell casting (`aerthos/systems/magic.py`)
- Dungeon generation (`aerthos/generator/`)
- Game state management (`aerthos/engine/game_state.py`)
- Save/load systems (`aerthos/storage/`, `aerthos/ui/save_system.py`)

**THEN** you MUST:

1. ✅ **Check if Web UI uses this code**
   ```bash
   grep -r "function_name" web_ui/app.py main.py
   ```

2. ✅ **If Web UI has duplicate logic, update BOTH or refactor to shared function**
   - Example: If you changed `_add_starting_spells()`, search for spell assignment in `web_ui/app.py`

3. ✅ **Run ALL tests**
   ```bash
   python3 run_tests.py --no-web
   ```

4. ✅ **Run UI parity tests specifically**
   ```bash
   python3 -m unittest tests.test_ui_parity -v
   ```

5. ✅ **Manual verification (if possible)**
   - Test the change in CLI: `python3 main.py`
   - Test the change in Web UI: `python3 web_ui/app.py` (if Flask installed)

---

## General Checklist

### Code Quality
- [ ] No commented-out code blocks (remove or explain why kept)
- [ ] No debug print statements left in production code
- [ ] Docstrings updated if function signature changed
- [ ] Type hints added for new functions (Python 3.10+)

### Testing
- [ ] All existing tests pass (`python3 run_tests.py --no-web`)
- [ ] New tests added for new functionality
- [ ] Edge cases considered and tested

### Documentation
- [ ] `CLAUDE.md` updated if:
  - New commands added
  - New data files added
  - New systems implemented
  - Architecture changed
- [ ] `README.md` updated if user-facing features changed
- [ ] Comments added for complex logic

### Data Files
- [ ] If modified JSON data files (`aerthos/data/*.json`):
  - [ ] Validate JSON syntax: `python3 -m json.tool aerthos/data/file.json`
  - [ ] Verify backward compatibility with existing save files
  - [ ] Update schema documentation if structure changed

### Breaking Changes
- [ ] If save file format changed:
  - [ ] Add migration code in `aerthos/storage/`
  - [ ] Test loading old save files
  - [ ] Document migration in commit message
- [ ] If command syntax changed:
  - [ ] Update parser tests
  - [ ] Update help text
  - [ ] Document in README.md

---

## Commit Message Format

```
[Component] Brief description (max 50 chars)

Detailed explanation of what changed and why.

CRITICAL CHANGES:
- List any breaking changes
- List any UI synchronization updates
- List any save file format changes

Tests:
- All tests passing: YES/NO
- UI parity tests passing: YES/NO
- Manual testing completed: YES/NO

Affects:
- CLI: YES/NO
- Web UI: YES/NO
- Save files: YES/NO
```

### Example Good Commit Message

```
[Magic] Fix spell assignment in character creation

Web UI character creation was missing call to _add_starting_spells(),
causing Clerics and Magic-Users to be created without spells.

CRITICAL CHANGES:
- Added creator._add_starting_spells() call in web_ui/app.py:783
- Synchronized spell assignment logic between CLI and Web UI
- No save file format changes

Tests:
- All tests passing: YES
- UI parity tests passing: YES
- Manual testing completed: YES (created Cleric in both UIs)

Affects:
- CLI: NO
- Web UI: YES (character creation)
- Save files: NO (but fixes future saves)
```

---

## Red Flags 🚩

**STOP and review if you see:**

1. **Duplicated code between `main.py` and `web_ui/app.py`**
   - Should be refactored to shared function
   - If duplication is unavoidable, add comment explaining why

2. **Skipping tests because "they'll probably pass"**
   - Tests exist to catch exactly these mistakes
   - Run them EVERY time

3. **"Quick fix" that bypasses normal code paths**
   - These cause divergence
   - Refactor properly instead

4. **Hard-coded values instead of using game data**
   - Should use `game_data.classes`, `game_data.spells`, etc.
   - Keeps logic consistent across UIs

5. **Different parameter order in CLI vs Web UI**
   - Example: `create_dungeon(config, level)` vs `create_dungeon(level, config)`
   - Harmonize immediately

---

## Recovery from UI Divergence

**If you discover CLI and Web UI are producing different results:**

1. **File a bug** (create issue or add to bugs.md)

2. **Write a failing test** in `tests/test_ui_parity.py` that demonstrates the divergence

3. **Fix the root cause** (usually in Web UI, since CLI is more complete)

4. **Add parity test** to prevent regression

5. **Document the fix** in commit message

---

## Why This Matters

From `CLAUDE.md`:

> **THE GOLDEN RULE:** Both `main.py` (CLI) and `web_ui/app.py` (Web UI) must use identical calls to core engine functions.
>
> **Before committing ANY change, ask:** *"Does this affect the other UI?"*
>
> If yes → Update both UIs
> If unsure → Test both UIs

**Recent bugs caused by UI divergence:**
- ❌ Spell assignment missing in Web UI character creation
- ❌ MultiLevelGenerator parameter mismatch
- ❌ [Add more as they're discovered]

**Prevention is cheaper than fixes!**
