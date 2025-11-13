
# Aerthos Testing Guide

## Overview

This document describes the comprehensive test suite for Aerthos. These tests ensure that both CLI and Web UI work correctly and that changes don't break existing functionality.

## Why These Tests Matter

**The Problem:** When making changes to the Web UI, the CLI gets broken (and vice versa) because they share the same core game systems.

**The Solution:** Comprehensive tests that verify:
1. **Shared core systems** work correctly (both UIs depend on these)
2. **CLI-specific code** works independently
3. **Web UI-specific code** works independently
4. **End-to-end integration** flows work for complete game scenarios

## Test Architecture

### Test Organization

```
tests/
├── test_parser.py        # Command parsing (shared by both UIs)
├── test_combat.py        # Combat mechanics (shared by both UIs)
├── test_game_state.py    # Core game logic (shared by both UIs)
├── test_storage.py       # Persistence systems (shared by both UIs)
├── test_integration.py   # End-to-end game flows
└── test_web_ui.py        # Web UI API endpoints (Flask specific)
```

### Test Categories

**1. Unit Tests (Core Systems)**
- `test_parser.py` - Natural language command parsing
- `test_combat.py` - THAC0 combat resolution and dice rolling
- `test_game_state.py` - Central game state manager
- `test_storage.py` - Character roster, party manager, scenario library, session manager

**2. Integration Tests**
- `test_integration.py` - Complete game flows from start to finish
- Tests exploration, persistence, procedural generation, character creation

**3. Web UI Tests**
- `test_web_ui.py` - Flask routes, JSON responses, session management
- Requires Flask to be installed

## Running Tests

### Quick Start

```bash
# Run all tests
python run_tests.py

# Run with verbose output
python run_tests.py --verbose

# Run specific test categories
python run_tests.py --unit          # Core systems only
python run_tests.py --integration   # Integration tests only
python run_tests.py --web           # Web UI only

# Skip web tests (if Flask not installed)
python run_tests.py --no-web

# List all available tests
python run_tests.py --list
```

### Running Individual Test Files

```bash
# Run specific test file
python -m unittest tests/test_parser.py

# Run specific test class
python -m unittest tests.test_parser.TestCommandParser

# Run specific test method
python -m unittest tests.test_parser.TestCommandParser.test_attack_basic

# Run with verbose output
python -m unittest tests/test_parser.py -v
```

### Requirements

**Minimal (for CLI tests):**
- Python 3.10+
- Standard library only

**For Web UI tests:**
```bash
pip install flask
```

**For all tests:**
```bash
pip install -r requirements.txt  # Includes Flask
```

## Test Coverage

### What's Tested

#### Parser Tests (42 tests)
- ✅ Movement commands (north, south, east, west, n, s, e, w, go [dir])
- ✅ Combat commands (attack, hit, strike, fight)
- ✅ Magic commands (cast [spell], cast [spell] on [target])
- ✅ Item commands (take, get, drop, use, drink, equip, wear)
- ✅ Exploration commands (search, look, examine, open)
- ✅ Character commands (inventory, status, spells, rest)
- ✅ Navigation commands (map, help, save, quit)
- ✅ Edge cases (empty input, extra whitespace, case insensitivity)

#### Combat Tests (18 tests)
- ✅ Dice rolling (d20, multiple dice, modifiers, notation parsing)
- ✅ THAC0 calculations (hit/miss, critical hit/miss, AC variations)
- ✅ Damage resolution
- ✅ Combat integration (full rounds, combat to death)

#### Game State Tests (20+ tests)
- ✅ Initialization with player and dungeon
- ✅ Command execution and routing
- ✅ Movement between rooms
- ✅ Invalid command handling
- ✅ Serialization for saves
- ✅ Complete exploration sequences

#### Storage Tests (20+ tests)
- ✅ Character roster (save, load, list, delete)
- ✅ Party manager (save, load, list, delete)
- ✅ Scenario library (save, load, list, delete)
- ✅ Session manager (create, load, list, delete)
- ✅ Data integrity (stats preserved through save/load)

#### Integration Tests (10+ tests)
- ✅ Complete exploration sequences (multi-room dungeons)
- ✅ Command parsing to execution flow
- ✅ Invalid command handling
- ✅ Full persistence flow (characters → party → dungeon → session)
- ✅ Procedural dungeon generation
- ✅ Character creation integration

#### Web UI Tests (30+ tests)
- ✅ Flask route existence and responses
- ✅ JSON API format
- ✅ Session management (create, invalid, concurrent)
- ✅ Command execution through API
- ✅ Character/party/scenario/session CRUD endpoints
- ✅ Error handling (invalid JSON, missing fields)

### Total Test Count

**~140+ tests covering:**
- Parser (42 tests)
- Combat (18 tests)
- Game State (20 tests)
- Storage (20 tests)
- Integration (10 tests)
- Web UI (30 tests)

## CI/CD Integration

### Pre-Commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
echo "Running tests before commit..."
python run_tests.py --no-web

if [ $? -ne 0 ]; then
    echo "Tests failed! Commit aborted."
    exit 1
fi

echo "All tests passed!"
exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### GitHub Actions (Example)

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run tests
      run: |
        python run_tests.py --verbose
```

## Test-Driven Development Workflow

### When Making Changes

**1. Before changing code:**
```bash
# Run tests to establish baseline
python run_tests.py
```

**2. Make your changes**

**3. After changing code:**
```bash
# Run tests to verify nothing broke
python run_tests.py

# If tests fail, identify what broke:
python run_tests.py --verbose
```

**4. If you broke something:**
- Read the test failure message
- Fix the issue
- Re-run tests
- Repeat until all pass

### Adding New Features

**1. Write tests first (TDD approach):**
```python
# tests/test_new_feature.py
def test_new_feature():
    """Test the new feature works"""
    result = new_feature()
    assert result == expected
```

**2. Run test (it should fail):**
```bash
python -m unittest tests.test_new_feature
```

**3. Implement feature**

**4. Run test (it should pass):**
```bash
python -m unittest tests.test_new_feature
```

**5. Run full suite:**
```bash
python run_tests.py
```

## Common Test Patterns

### Testing Command Execution

```python
from aerthos.engine.parser import CommandParser
from aerthos.engine.game_state import GameState

parser = CommandParser()
cmd = parser.parse("north")
result = game_state.execute_command(cmd)

assert 'message' in result
assert isinstance(result['message'], str)
```

### Testing Storage Round-Trip

```python
from aerthos.storage.character_roster import CharacterRoster

roster = CharacterRoster(storage_dir=temp_dir)
char_id = roster.save_character(character)
loaded = roster.load_character(char_id)

assert loaded.name == character.name
assert loaded.hp_current == character.hp_current
```

### Testing Web API

```python
response = client.post('/api/command',
                       json={'session_id': session_id,
                              'command': 'look'})

assert response.status_code == 200
data = json.loads(response.data)
assert 'message' in data
```

## Debugging Failed Tests

### Verbose Output

```bash
python run_tests.py --verbose
```

### Run Specific Test

```bash
# Run just the failing test
python -m unittest tests.test_parser.TestCommandParser.test_attack_basic -v
```

### Add Debug Prints

```python
def test_something(self):
    result = function_under_test()
    print(f"DEBUG: Result = {result}")  # Temporary debug
    assert result == expected
```

### Use Python Debugger

```python
import pdb

def test_something(self):
    result = function_under_test()
    pdb.set_trace()  # Debugger will stop here
    assert result == expected
```

## Test Maintenance

### When to Update Tests

**Update tests when:**
1. You add a new feature
2. You change behavior of existing feature
3. You fix a bug (add test to prevent regression)
4. You refactor code (tests should still pass!)

**Don't break tests by:**
1. Changing return value formats without updating tests
2. Renaming functions/classes without updating imports
3. Changing command syntax without updating parser tests
4. Modifying JSON structure without updating storage tests

### Keeping Tests Fast

**Current test suite runs in < 10 seconds**

To keep it fast:
- Use mock data (don't generate huge dungeons)
- Use temporary directories (clean up after)
- Skip slow tests in development (mark with `@unittest.skip`)
- Run full suite before commits only

## Known Test Limitations

### What's NOT Tested (Yet)

1. **Combat with actual monsters** - Uses mocks
2. **Spell effects** - Not fully tested
3. **Thief skills** - Basic tests only
4. **Time/light management** - Minimal coverage
5. **Village systems** (shops, inns, guilds) - Not tested
6. **Multi-level dungeons** - Not implemented yet
7. **Automap display** - Visual output not tested
8. **CLI main menu** - Interactive portions not tested

### Web UI Test Limitations

- Tests require Flask installed
- Some tests skip if session creation fails
- Frontend JavaScript not tested (only API)
- No browser automation tests (Selenium/Playwright)

## Troubleshooting

### "No module named 'flask'"

```bash
pip install flask
# or run without web tests:
python run_tests.py --no-web
```

### "No module named 'aerthos'"

Make sure you're in the project root directory:
```bash
cd /path/to/aerthos
python run_tests.py
```

### "FileNotFoundError: aerthos/data/classes.json"

Tests need access to data files. Run from project root:
```bash
cd /path/to/aerthos
python run_tests.py
```

### Tests Pass Locally But Fail in CI

- Check Python version (need 3.10+)
- Check working directory
- Check file paths (use `Path()` not string concatenation)
- Check for hardcoded paths

## Test Output Examples

### Successful Test Run

```
======================================================================
Running Parser Tests
======================================================================
test_attack_basic (tests.test_parser.TestCommandParser) ... ok
test_attack_synonyms (tests.test_parser.TestCommandParser) ... ok
...
✓ PASS

----------------------------------------------------------------------
Ran 42 tests in 0.234s

OK

======================================================================
TEST SUMMARY
======================================================================

Total Tests Run:    140
Passed:            140
Failed:            0
Errors:            0
Skipped:           0

======================================================================
✓ ALL TESTS PASSED
======================================================================
```

### Failed Test Run

```
======================================================================
FAILURE: test_attack_basic (tests.test_parser.TestCommandParser)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "tests/test_parser.py", line 45, in test_attack_basic
    self.assertEqual(cmd.target, "orc")
AssertionError: 'goblin' != 'orc'

======================================================================
TEST SUMMARY
======================================================================

Total Tests Run:    140
Passed:            139
Failed:            1
Errors:            0
Skipped:           0

======================================================================
✗ 1 TESTS FAILED
======================================================================
```

## Best Practices

### DO:
✅ Run tests before committing
✅ Run tests after pulling changes
✅ Add tests for new features
✅ Add tests for bug fixes
✅ Keep tests fast (< 10 seconds total)
✅ Use descriptive test names
✅ Test both success and failure cases
✅ Clean up temporary files (use `tearDown`)

### DON'T:
❌ Commit code that breaks tests
❌ Skip failing tests without investigating
❌ Test implementation details (test behavior)
❌ Make tests depend on each other
❌ Use real file system without cleanup
❌ Hardcode paths or data
❌ Make tests interactive (no `input()`)

## Contributing Tests

When adding new tests:

1. **Choose the right file:**
   - Core system logic → unit test file
   - End-to-end flow → `test_integration.py`
   - Web API → `test_web_ui.py`

2. **Follow naming convention:**
   - `test_[feature]_[scenario]`
   - `test_attack_with_weapon`
   - `test_save_character_preserves_stats`

3. **Write clear docstrings:**
   ```python
   def test_something(self):
       """Test that something does what it should"""
   ```

4. **Use helpers for setup:**
   ```python
   def create_test_character(self, name="Fighter"):
       # Reusable character creation
   ```

5. **Assert meaningful things:**
   ```python
   # Good
   self.assertEqual(result['action'], 'attack')

   # Bad
   self.assertTrue(result)
   ```

## Questions?

**Test failing and don't know why?**
1. Run with `--verbose` to see details
2. Run just that test file
3. Add debug prints
4. Check if data files changed

**Need to add a test?**
1. Find similar existing test
2. Copy and modify
3. Run to verify it works

**Tests too slow?**
1. Profile with `time python run_tests.py`
2. Look for file I/O in hot paths
3. Use mocks for expensive operations

---

**Remember:** Tests are your safety net. When you change the Web UI, these tests ensure the CLI doesn't break. When you change the CLI, these tests ensure the Web UI doesn't break. Run them often!
