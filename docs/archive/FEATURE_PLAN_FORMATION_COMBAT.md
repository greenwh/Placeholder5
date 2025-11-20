# Feature Plan: Formation-Based Combat (Priority 1)

## Overview
Implement formation-aware combat targeting based on Gold Box game mechanics, where party positioning affects monster targeting priorities and combat effectiveness.

## Current State
- Party has `formation` attribute (list of 'front'/'back')
- Methods `get_front_line()` and `get_back_line()` exist
- Combat targeting is completely random (`random.choice(targets)`)
- No formation mechanics implemented

## Design Goals (from combat_order_resolution.md)
Keep it simple but not completely random:
1. Monsters should prefer front-line targets (meat shield effect)
2. Spellcasters in back should be harder to target (but not impossible)
3. Wounded/weak targets may draw opportunistic attacks
4. Low AC targets may be prioritized by intelligent enemies

## Implementation Plan

### Phase 1: Monster Targeting AI (2-3 hours)

**File: `aerthos/systems/monster_ai.py` (NEW)**

Create new AI system with targeting priority logic:

```python
class MonsterTargetingAI:
    """Handles monster targeting decisions in combat"""

    def select_target(self, monster: Monster, party: Party,
                      all_targets: List[Character]) -> Character:
        """
        Select best target based on formation, threat, and opportunity

        Priority system:
        1. Front-line targets (70% chance)
        2. Visible back-line targets (20% chance)
        3. Opportunistic targeting - wounded/low AC (10% chance)
        """
```

**Targeting Logic:**
- Roll d100 to determine targeting strategy
- **1-70**: Attack front-line fighter (prefer lowest HP if multiple)
- **71-90**: Attack back-line target if visible/reachable
  - Requires front-line to be defeated OR special ability (flying, reach, etc.)
- **91-100**: Opportunistic - target lowest AC or most wounded

**Intelligence Modifiers:**
- Low INT monsters (animals, oozes): Always attack nearest (front-line bias)
- Average INT: Use standard priority system above
- High INT (humanoids, dragons): Can prioritize spellcasters if detected casting

### Phase 2: Formation Mechanics (1-2 hours)

**File: `aerthos/entities/party.py` (MODIFY)**

Add methods:
```python
def is_front_line_standing(self) -> bool:
    """Check if any front-line members alive"""

def get_available_targets_by_formation(self, attacker_position: str) -> List[Character]:
    """Get targetable characters based on formation and attacker position"""
```

**File: `aerthos/engine/combat.py` (MODIFY)**

Update `resolve_combat_round()` method (lines 368-377):
```python
# OLD: target = random.choice(targets)

# NEW:
if combatant['side'] == 'monster':
    from ..systems.monster_ai import MonsterTargetingAI
    ai = MonsterTargetingAI()

    # Get party formation if available
    party_obj = getattr(game_state, 'party', None)
    if party_obj:
        target = ai.select_target(char, party_obj, targets)
    else:
        # Fallback for solo play
        target = random.choice(targets)
else:
    # Player attacks - keep manual/random for now
    target = random.choice(targets)
```

### Phase 3: Visual Feedback (1 hour)

**File: `aerthos/ui/display.py` (MODIFY)**

Enhance combat narrative to show formation:
```
═══ COMBAT ROUND 2 ═══

FRONT LINE: Thorin (Fighter) [HP: 12/18], Gimli (Cleric) [HP: 8/14]
BACK LINE:  Gandalf (Magic-User) [HP: 6/6], Bilbo (Thief) [HP: 5/8]

Orc targets Thorin (front-line fighter)!
Orc hits Thorin for 5 damage!

Goblin targets Thorin (wounded front-line)!
Goblin misses Thorin!
```

**File: `aerthos/ui/character_sheet.py` (MODIFY)**

Show formation position in party roster display.

### Phase 4: Formation Commands (30 minutes)

**File: `aerthos/engine/parser.py` (MODIFY)**

Add commands:
- `formation` - Show current formation
- `formation <name> front` - Move character to front
- `formation <name> back` - Move character to back
- `formation default` - Auto-assign by class

### Phase 5: Testing (1 hour)

**File: `tests/test_formation_combat.py` (NEW)**

Test cases:
- Front-line targets attacked preferentially
- Back-line protected when front-line alive
- Back-line exposed when front-line defeated
- Opportunistic targeting for wounded characters
- Formation commands work correctly
- Low/High INT monster behavior differs

## Integration Points

**game_state.py modifications:**
- Pass `party` object to combat resolver
- Store AI instance for reuse

**Backward compatibility:**
- If no party exists (solo play), fall back to random targeting
- If formation list empty/invalid, treat all as front-line

## Configuration Constants

Add to `aerthos/constants.py`:
```python
# Formation Combat
FRONT_LINE_TARGET_CHANCE = 70  # % chance to target front-line
BACK_LINE_TARGET_CHANCE = 20   # % chance to target back-line
OPPORTUNISTIC_TARGET_CHANCE = 10  # % chance for opportunistic targeting

# Intelligence thresholds for targeting behavior
MONSTER_INT_LOW = 4   # Animal intelligence
MONSTER_INT_HIGH = 12  # Tactical intelligence
```

## Success Criteria

✅ Monsters preferentially attack front-line characters (70%+ of attacks)
✅ Back-line characters receive significantly fewer attacks when front-line standing
✅ Formation can be viewed and modified via commands
✅ Combat narrative reflects formation-based targeting
✅ All existing tests still pass
✅ New formation combat tests pass (12+ test cases)

## Risks & Mitigations

**Risk**: Front-line characters become "meat grinders" - always targeted, die quickly
**Mitigation**: Opportunistic targeting gives variety; players can move wounded fighters back

**Risk**: Back-line becomes untouchable, breaks balance
**Mitigation**: 20% back-line targeting; special monsters (flying, ranged) bypass formation

**Risk**: Complexity creep - too many rules
**Mitigation**: Keep it simple - 3 targeting modes, clear percentages, no exceptions unless necessary

## Estimated Time: 5-7 hours total

## Files Created/Modified
- **NEW**: `aerthos/systems/monster_ai.py`
- **NEW**: `tests/test_formation_combat.py`
- **MODIFY**: `aerthos/engine/combat.py` (~20 lines changed)
- **MODIFY**: `aerthos/entities/party.py` (~30 lines added)
- **MODIFY**: `aerthos/ui/display.py` (~50 lines added)
- **MODIFY**: `aerthos/ui/character_sheet.py` (~20 lines added)
- **MODIFY**: `aerthos/engine/parser.py` (~10 lines added)
- **MODIFY**: `aerthos/constants.py` (~10 lines added)
