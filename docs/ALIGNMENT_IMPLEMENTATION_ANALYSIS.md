# Alignment Implementation Analysis

**Date:** 2025-01-22
**Status:** Pre-Implementation Analysis
**Priority:** MEDIUM - Not critical for MVP, but easier to add now than later

---

## Executive Summary

Alignment is **not currently implemented** in Aerthos, but several game systems reference it:
- **4 spells** explicitly mention alignment (Detect Evil, Protection from Evil, etc.)
- **Paladin class** has "detect_evil" special ability
- **Class restrictions** exist in AD&D 1e (e.g., Paladins must be Lawful Good)

**Recommendation:** Implement alignment **NOW** while the codebase is still manageable. The longer we wait, the more systems will need retrofitting.

---

## Current State Analysis

### ✅ What Works Without Alignment
- Character creation (races, classes, abilities)
- Combat system (THAC0, saves, damage)
- Magic system (spell slots, memorization, casting)
- Inventory and equipment
- Dungeon exploration
- Party management
- Save/load system
- All 374 tests pass

### ❌ What's Missing/Broken Without Alignment

#### **1. Class Restrictions (AD&D 1e PHB, p. 20-34)**
Currently **not enforced**:

| Class | Required Alignment | Currently Enforced? |
|-------|-------------------|---------------------|
| **Paladin** | Lawful Good only | ❌ No |
| **Ranger** | Any Good (LG, NG, CG) | ❌ No |
| **Druid** | True Neutral only | ❌ No |
| **Monk** | Lawful only (LG, LN, LE) | ❌ No (class not implemented) |
| **Assassin** | Any Evil | ❌ No (class not implemented) |
| Fighter, Cleric, Magic-User, Thief, Illusionist, Bard | Any | N/A |

**Impact:** Players can currently create Chaotic Evil Paladins or Lawful Good Assassins, violating AD&D rules.

#### **2. Spell Functionality**

**Implemented spells that reference alignment:**

| Spell | Level | Current Status | Issue |
|-------|-------|---------------|-------|
| **Detect Evil** | Cleric 1 | Implemented | No alignment to detect |
| **Protection from Evil** | Cleric 1 | Implemented | No evil creatures to protect from |
| **Protection from Evil 10' Radius** | Cleric/MU 3 | Implemented | Same as above |
| **Holy/Unholy Word** | Cleric 7 | Implemented | Supposed to affect creatures by alignment |

**Impact:** These spells are non-functional or misleading without alignment data.

#### **3. Paladin Special Abilities**

From `classes.json` line 66:
```json
"special_abilities": ["detect_evil", "lay_on_hands", "turn_undead", "disease_immunity", "cleric_spells_at_9"]
```

**Detect Evil** is listed but has no data to work with.

#### **4. Monster Alignment**

Many monsters have alignment in AD&D:
- **Dragons:** Chromatic (evil), Metallic (good)
- **Demons/Devils:** Always evil
- **Undead:** Usually evil or neutral
- **Animals:** True neutral

**Current state:** `monsters.json` has no alignment field.

---

## AD&D 1e Alignment System

### The 9 Alignments (PHB p. 33)

```
LAWFUL          NEUTRAL         CHAOTIC
  |               |               |
Good     → Lawful Good    Neutral Good    Chaotic Good
Neutral  → Lawful Neutral True Neutral    Chaotic Neutral
Evil     → Lawful Evil    Neutral Evil    Chaotic Evil
```

### Alignment Axes

1. **Law vs Chaos** (order vs freedom)
   - **Lawful:** Believes in order, organization, hierarchy
   - **Neutral:** Balanced or indifferent
   - **Chaotic:** Values freedom, individualism

2. **Good vs Evil** (altruism vs selfishness)
   - **Good:** Concerned with others' well-being
   - **Neutral:** Self-interested or balanced
   - **Evil:** Willing to harm others for personal gain

### Special Cases

- **True Neutral:** Balance between all extremes (required for Druids)
- **Any Good:** LG, NG, or CG (Rangers)
- **Any Lawful:** LG, LN, or LE (Monks)
- **Any Evil:** LE, NE, or CE (Assassins)

---

## Implementation Impact Analysis

### 🟢 LOW IMPACT (Easy to Add)

#### **1. Data Model Changes**

**Character class** (`aerthos/entities/character.py`):
```python
@dataclass
class Character:
    # ... existing fields ...
    alignment: str = "True Neutral"  # Add this field
```

**Valid values:**
```python
ALIGNMENTS = [
    "Lawful Good", "Neutral Good", "Chaotic Good",
    "Lawful Neutral", "True Neutral", "Chaotic Neutral",
    "Lawful Evil", "Neutral Evil", "Chaotic Evil"
]
```

**Impact:** Single field addition, no dependencies.

---

#### **2. Save System Compatibility**

**CharacterRoster** (`aerthos/storage/character_roster.py`):
- Add `'alignment': character.alignment` to save dict (line ~73)
- Add default in load: `alignment=data.get('alignment', 'True Neutral')` (line ~120)

**Backward compatibility:** Use `.get('alignment', 'True Neutral')` for old saves.

**Impact:** 2 lines of code, fully backward compatible.

---

#### **3. Monster Data**

Add alignment to `monsters.json`:
```json
{
  "goblin": {
    "name": "Goblin",
    "alignment": "Lawful Evil",
    ...
  }
}
```

**Impact:** Bulk data entry (~100 monsters), no code changes needed.

---

### 🟡 MEDIUM IMPACT (Moderate Effort)

#### **4. Character Creation**

**CLI** (`main.py`):
- Add alignment selection prompt after class choice
- Validate alignment against class requirements
- Display allowed alignments for selected class

**Web UI** (`web_ui/templates/character_creation.html`):
- Add alignment dropdown/radio buttons
- JavaScript to filter alignments by class
- Preview shows alignment restrictions

**Impact:** ~100 lines of UI code, ~50 lines of validation logic.

---

#### **5. Class Restrictions**

Add to `classes.json`:
```json
{
  "Paladin": {
    ...
    "alignment_requirement": "Lawful Good",
    "alignment_restriction": "exact"
  },
  "Ranger": {
    ...
    "alignment_requirement": "Good",
    "alignment_restriction": "any"  // Any Good (LG, NG, CG)
  },
  "Druid": {
    ...
    "alignment_requirement": "True Neutral",
    "alignment_restriction": "exact"
  }
}
```

**Validation function** (`aerthos/ui/character_creation.py`):
```python
def validate_class_alignment(char_class: str, alignment: str, game_data) -> bool:
    """Check if alignment is allowed for class"""
    class_data = game_data.classes[char_class]

    # No restriction
    if 'alignment_requirement' not in class_data:
        return True

    requirement = class_data['alignment_requirement']
    restriction = class_data.get('alignment_restriction', 'exact')

    if restriction == 'exact':
        return alignment == requirement
    elif restriction == 'any':
        # "Good" means any Good alignment
        return requirement in alignment

    return True
```

**Impact:** ~30 lines of validation code, JSON updates.

---

#### **6. Display in UI**

**CLI Character Sheet:**
```
Name: Thorin
Race: Dwarf
Class: Fighter
Alignment: Lawful Good    ← Add this line
Level: 3
```

**Web UI Character Roster:**
```javascript
// character_roster.html
<div class="char-info">${char.race} ${char.char_class} (${char.alignment})</div>
```

**Web UI Game Display:**
```javascript
// game.html - Active Character Panel
Alignment: ${char.alignment}
```

**Impact:** ~20 lines across 5 files.

---

### 🔴 HIGH IMPACT (Complex Systems)

#### **7. Spell Functionality**

**Detect Evil** (Cleric 1):
```python
def cast_detect_evil(caster, game_state):
    """Detect evil creatures in range"""
    evil_creatures = []

    # Check monsters in current room
    for monster in game_state.active_monsters:
        if 'Evil' in monster.alignment:
            evil_creatures.append(monster.name)

    if evil_creatures:
        return f"You sense evil from: {', '.join(evil_creatures)}"
    else:
        return "You detect no evil presence."
```

**Protection from Evil** (Cleric 1):
```python
def cast_protection_from_evil(caster, target):
    """Grant +2 AC and save bonus vs evil creatures"""
    target.conditions.append('protected_from_evil')
    # Combat system checks for this condition
    # and applies bonuses when attacked by evil creatures
```

**Holy Word** (Cleric 7):
```python
def cast_holy_word(caster, game_state):
    """Affects creatures based on alignment difference"""
    effects = []

    for monster in game_state.active_monsters:
        if 'Evil' in monster.alignment:
            # Kill, paralyze, stun, or deafen based on HD
            if monster.hit_dice <= 4:
                effects.append(f"{monster.name} is slain!")
            elif monster.hit_dice <= 8:
                effects.append(f"{monster.name} is paralyzed!")
            # ... etc

    return "\n".join(effects)
```

**Impact:** ~200 lines of spell effect code, combat system modifications.

---

#### **8. Paladin Detect Evil Ability**

**Passive ability** (always active):
```python
# In game_state.py, when entering a room
if player.char_class == 'Paladin':
    evil_present = any('Evil' in m.alignment for m in room.monsters)
    if evil_present:
        messages.append("⚠️ Your holy senses tingle - evil is near!")
```

**Impact:** ~30 lines, integration with room entry logic.

---

#### **9. Alignment-Based Item Restrictions**

Some magic items have alignment requirements:
- **Holy Avenger sword:** Paladins only (Lawful Good)
- **Unholy weapons:** Evil characters only
- **Neutral-aligned staves:** Druids only

```json
{
  "holy_avenger": {
    "name": "Holy Avenger +5",
    "type": "weapon",
    "alignment_requirement": "Lawful Good",
    "class_requirement": "Paladin",
    ...
  }
}
```

**Impact:** Equipment system modifications, ~50 lines.

---

#### **10. Alignment Change**

**Causes:**
- Using cursed items (Helm of Alignment Change)
- Divine intervention (quest completion/failure)
- Player choice (rare, with consequences)

**Consequences:**
- **Paladin/Ranger/Druid:** Lose class abilities if alignment shifts
- **Magic items:** May become unusable
- **Party relations:** NPCs may react differently

**Impact:** Complex state machine, ~100+ lines.

---

## Migration Strategy

### Phase 1: Data Model (Week 1) 🟢
**Effort:** 1-2 hours
**Risk:** Low

1. Add `alignment` field to Character class
2. Update save/load system with backward compatibility
3. Add alignment to monster data (bulk edit)
4. **Test:** All 374 tests still pass

### Phase 2: Character Creation (Week 1) 🟡
**Effort:** 3-4 hours
**Risk:** Low-Medium

1. Add alignment selection to CLI character creation
2. Add alignment selection to Web UI character creation
3. Implement class restriction validation
4. Update character display (roster, sheets)
5. **Test:** Can create characters with alignments, restrictions enforced

### Phase 3: Basic Spell Support (Week 2) 🟡
**Effort:** 4-6 hours
**Risk:** Medium

1. Implement Detect Evil spell
2. Implement Protection from Evil (basic)
3. Add Paladin detect evil passive ability
4. **Test:** Spells work correctly, Paladin senses evil

### Phase 4: Advanced Systems (Optional - Future) 🔴
**Effort:** 8-12 hours
**Risk:** High

1. Full Protection from Evil mechanics (AC/save bonuses)
2. Holy Word spell
3. Alignment-restricted magic items
4. Alignment change mechanics
5. **Test:** Complex interactions work correctly

---

## Recommended Approach

### ✅ DO NOW (Before More Features)

**Priority 1:** Implement Phases 1-2 (Data Model + Character Creation)
- **Why:** Establishes the foundation, minimal effort
- **Benefit:** All new characters have alignment data
- **Risk:** Almost none (backward compatible)

**Priority 2:** Add alignment to existing monsters
- **Why:** One-time data entry, enables future spell work
- **Benefit:** Monster data is complete
- **Risk:** None (just data)

### ⏸️ DO LATER (After MVP)

**Priority 3:** Implement Phase 3 (Basic spell support)
- **Why:** Requires more thought, testing
- **Benefit:** Makes existing spells functional
- **Risk:** Medium (combat system changes)

**Priority 4:** Implement Phase 4 (Advanced systems)
- **Why:** Complex, low ROI for MVP
- **Benefit:** Full AD&D authenticity
- **Risk:** High (many edge cases)

---

## Breaking Changes & Risks

### ⚠️ Potential Issues

1. **Old Save Files:** Characters without alignment field
   - **Solution:** Default to "True Neutral" on load

2. **Monster Data Migration:** 100+ monster entries to update
   - **Solution:** Bulk edit with script or AI assist

3. **Test Suite:** May need alignment fixtures
   - **Solution:** Add default alignment to test character creation

4. **CLI/Web UI Sync:** Both UIs must handle alignment consistently
   - **Solution:** Use shared validation function

### ✅ Non-Breaking

- Adding `alignment` field is **additive** (doesn't break existing code)
- Save system handles missing fields gracefully
- Tests don't currently check alignment, so won't fail

---

## Cost-Benefit Analysis

### **Cost of Adding Now**
- 6-10 hours of development (Phases 1-2)
- 50-100 lines of new code
- Bulk data entry for monsters
- Testing and validation

### **Cost of Adding Later**
- All of the above, PLUS:
- Retrofitting existing save files (migration scripts)
- Updating all character creation workflows
- Rewriting tests that assume no alignment
- Fixing bugs from alignment-dependent spells
- User confusion (why don't spells work?)

### **Benefit of Adding Now**
- ✅ Authentic AD&D 1e experience
- ✅ Class restrictions enforced
- ✅ Foundation for spell/ability systems
- ✅ Future-proof (no migration pain)
- ✅ Better UX (players understand their character)

---

## Implementation Checklist

### Phase 1: Data Model ✅ RECOMMENDED NOW
- [ ] Add `alignment: str` field to `Character` dataclass
- [ ] Add `ALIGNMENTS` constant with 9 valid values
- [ ] Update `CharacterRoster.save_character()` to include alignment
- [ ] Update `CharacterRoster.load_character()` with default fallback
- [ ] Add alignment to `monsters.json` (bulk edit ~100 entries)
- [ ] Add alignment to `Monster` class
- [ ] Update API endpoints (`/api/characters`) to return alignment
- [ ] Run full test suite (should still pass)

### Phase 2: Character Creation ✅ RECOMMENDED NOW
- [ ] Add `alignment_requirement` to `classes.json` (Paladin, Ranger, Druid)
- [ ] Create `validate_class_alignment()` function
- [ ] **CLI:** Add alignment selection prompt in `main.py`
- [ ] **CLI:** Show allowed alignments for selected class
- [ ] **Web UI:** Add alignment dropdown to character creation
- [ ] **Web UI:** JavaScript to filter alignments by class
- [ ] Update character display (roster, sheet, game UI)
- [ ] Test character creation enforces restrictions
- [ ] Test character display shows alignment

### Phase 3: Basic Spells ⏸️ DEFER TO LATER
- [ ] Implement `Detect Evil` spell effect
- [ ] Implement `Protection from Evil` basic version
- [ ] Add Paladin passive detect evil
- [ ] Test spells work correctly
- [ ] Update spell descriptions to explain mechanics

### Phase 4: Advanced Systems ⏸️ DEFER TO LATER
- [ ] Full Protection from Evil (AC/save bonuses in combat)
- [ ] Holy Word spell implementation
- [ ] Alignment-restricted magic items
- [ ] Alignment change mechanics
- [ ] Comprehensive integration tests

---

## Conclusion

**Alignment should be implemented NOW (Phases 1-2) for these reasons:**

1. **Low effort:** 6-10 hours of work
2. **High value:** Authentic AD&D, foundation for future features
3. **Low risk:** Backward compatible, additive changes
4. **Future-proof:** Much harder to add later after more systems depend on it
5. **User experience:** Players expect alignment in D&D

**The window is closing.** Once we add more classes, spells, and features, retrofitting alignment becomes exponentially harder.

---

**Recommendation:** Implement Phases 1-2 this week while the codebase is still manageable.
