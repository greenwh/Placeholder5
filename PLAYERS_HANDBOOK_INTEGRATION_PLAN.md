# Players Handbook Integration Plan - Remaining Tasks

**Status:** Critical Path (Weeks 1-8) Complete ✅
**Last Updated:** 2025-11-18
**Current Branch:** `claude/enhance-handbook-validation-01XEK6GdWbLsu4skKoD2sUjH`

---

## Completed Work Summary

### ✅ Week 1-3: Foundational Character Systems
- Ability score generation and modifiers
- Multi-classing mechanics
- Level progression and XP tables (all 11 classes)
- THAC0 tables by class and level

### ✅ Week 4-5: Racial and Class Abilities
- Complete racial abilities for 7 races (Human, Elf, Dwarf, Halfling, Half-Elf, Half-Orc, Gnome)
- Class special abilities for 11 classes (Fighter, Cleric, Magic-User, Thief, Paladin, Ranger, Druid, Monk, Illusionist, Assassin, Bard)
- Turning undead system (13 undead types, 20 cleric levels)
- Level limits with ability score bonuses
- **Files:** `aerthos/systems/racial_abilities.py`, `aerthos/systems/class_abilities.py`, `aerthos/systems/turning_undead.py`

### ✅ Week 6-7: Spell Expansion (Levels 1-3)
- Expanded from 34 to 143 spells
- Complete spell descriptions for levels 1-3
- Classes covered: Cleric (40 spells), Magic-User (73), Druid (28), Illusionist (17)
- **Files:** `aerthos/data/spells.json` (modified)

### ✅ Week 8: Combat Enhancements
- Comprehensive weapons database (38 weapons)
- Weapon speed factor initiative system
- Multiple attacks per round (1, 1.5, 2, 3, 4 attacks)
- Individual initiative: d6 + weapon speed + DEX modifier
- **Files:** `aerthos/data/weapons.json`, `aerthos/engine/combat.py` (modified)

### ✅ Phase 1.1: Complete Ability Score Modifier Tables (COMPLETED 2025-11-18)
- All six ability score tables implemented (STR, DEX, CON, INT, WIS, CHA)
- Exceptional strength for Fighters (18/01 through 18/00)
- Spell learning mechanics, system shock, resurrection survival
- Complete thief skill modifiers from DEX
- Bonus cleric spells from WIS, spell failure checks
- Max hirelings and loyalty from CHA
- **Files:** `aerthos/data/ability_score_tables.json`, `aerthos/systems/ability_modifiers.py`, `aerthos/entities/character.py` (modified), `tests/test_ability_modifiers.py`

**All Tests Passing:** 128/128 tests ✅ (19 new ability modifier tests)

---

## Remaining Tasks - Organized by Priority

---

## PHASE 1: CORE MECHANICS COMPLETION (High Priority)

These tasks complete the foundational game mechanics from the Players Handbook.

---

### Task 1.1: Complete Ability Score Modifier Tables ✅ COMPLETED

**Status:** ✅ COMPLETED (2025-11-18)
**Actual Effort:** ~6 hours
**Commit:** `bf61b97` - "[Phase 1.1] Complete Ability Score Modifier Tables"
**Files Created:**
- `aerthos/data/ability_score_tables.json` (1833 lines added)
- `aerthos/systems/ability_modifiers.py` (445 lines)
- `tests/test_ability_modifiers.py` (19 tests, all passing)
**Files Modified:**
- `aerthos/entities/character.py` (updated to use ability system)

**Priority:** HIGH
**Estimated Effort:** 4-6 hours
**Dependencies:** None
**Testing Impact:** Medium (affects character creation, combat, skills)

**Reference Documentation:**
- `docs/players_handbook/PH_ability_scores.md` (complete file)

**Objective:**
Implement all six ability score modifier tables with comprehensive lookups for bonuses/penalties.

**Current State:**
- Basic STR and DEX modifiers exist in `aerthos/entities/character.py`
- Incomplete coverage of all ability score effects
- Missing: exceptional strength (18/01-18/00), spell immunity, system shock, resurrection survival, spell failure, max hirelings, loyalty, reaction adjustments

**Implementation Steps:**

1. **Create Data File:** `aerthos/data/ability_score_tables.json`
   - Structure with six ability score sections (STR, DEX, CON, INT, WIS, CHA)
   - Each score (3-25) maps to modifiers

2. **Strength Table (Table I & II from PH_ability_scores.md lines 5-31):**
   ```json
   "strength": {
     "3": {"hit_prob": -3, "damage": -1, "weight_allowance": -350, "open_doors": "1-2", "bend_bars": 1},
     "18": {"hit_prob": 2, "damage": 3, "weight_allowance": 1000, "open_doors": "1-4", "bend_bars": 40},
     "18/01-50": {"hit_prob": 1, "damage": 3, "weight_allowance": 1000, "open_doors": "2(1)", "bend_bars": 40},
     "18/51-75": {"hit_prob": 2, "damage": 3, "weight_allowance": 1250, "open_doors": "3(1)", "bend_bars": 45},
     "18/76-90": {"hit_prob": 2, "damage": 4, "weight_allowance": 1500, "open_doors": "3(2)", "bend_bars": 50},
     "18/91-99": {"hit_prob": 2, "damage": 5, "weight_allowance": 2000, "open_doors": "4(1)", "bend_bars": 60},
     "18/00": {"hit_prob": 3, "damage": 6, "weight_allowance": 2500, "open_doors": "4(2)", "bend_bars": 70}
   }
   ```

3. **Intelligence Table (Table I & II from PH_ability_scores.md lines 33-50):**
   - Additional languages (0-7 based on INT)
   - Spell learning chance (35%-95%)
   - Min/max spells per level (4-10 min, 6-All max)
   - Spell immunity at INT 19+ (illusionist spells 1st level)

4. **Wisdom Table (Table I & II from PH_ability_scores.md lines 52-70):**
   - Magic attack adjustment (-4 to +4)
   - Spell bonus (extra cleric spells at WIS 13+)
   - Spell failure chance (20% at WIS 9, 0% at WIS 13+)

5. **Dexterity Table (Table I & II from PH_ability_scores.md lines 72-90):**
   - Reaction/attacking adjustment (-3 to +3)
   - Defensive adjustment (AC) (-4 to +4)
   - Thief skill bonuses (-15% to +15%)

6. **Constitution Table (Table I & II from PH_ability_scores.md lines 92-110):**
   - HP adjustment (-1 to +4 per die)
   - System shock survival (35%-99%)
   - Resurrection survival (40%-100%)
   - Poison save bonus (+0 to +4)
   - Regeneration (at CON 20+, fighters only)

7. **Charisma Table (Table I & II from PH_ability_scores.md lines 112-130):**
   - Max hirelings (0-25)
   - Loyalty base (0-20)
   - Reaction adjustment (-25% to +25%)

8. **Create System Module:** `aerthos/systems/ability_modifiers.py`
   ```python
   class AbilityModifierSystem:
       def __init__(self):
           # Load ability_score_tables.json

       def get_strength_modifiers(self, strength: int, exceptional: int = 0) -> Dict
       def get_intelligence_modifiers(self, intelligence: int) -> Dict
       def get_wisdom_modifiers(self, wisdom: int) -> Dict
       def get_dexterity_modifiers(self, dexterity: int) -> Dict
       def get_constitution_modifiers(self, constitution: int) -> Dict
       def get_charisma_modifiers(self, charisma: int) -> Dict

       def apply_all_modifiers(self, character: Character) -> None
           # Apply all ability score effects to character
   ```

9. **Update Character Class:** `aerthos/entities/character.py`
   - Add methods to query ability modifiers
   - Replace hardcoded modifier lookups with table-based system
   - Add exceptional_strength field for Fighters

10. **Testing:**
    - Create `tests/test_ability_modifiers.py`
    - Test all ability scores (3-25)
    - Test exceptional strength (18/01 through 18/00)
    - Verify modifier calculations match PH tables
    - Test edge cases (minimum/maximum values)

**Success Criteria:**
- ✅ All six ability score tables implemented
- ✅ Exceptional strength working for Fighters
- ✅ All modifiers match Players Handbook exactly
- ✅ Tests passing for all ability score ranges
- ✅ Character creation properly applies all modifiers

**Completion Notes:**
- Implemented comprehensive JSON tables with all modifiers from PH
- Created AbilityModifierSystem with 20+ methods for modifier lookups
- Updated Character class to use lazy-loaded ability system
- Added property accessors (str, dex, con, int, wis, cha) for convenience
- All 19 new tests passing, total test count increased to 128
- Backward compatible with existing code using get_to_hit_bonus(), etc.
- System supports spell learning rolls, system shock checks, door forcing
- Ready for integration with Task 1.3 (spell level restrictions by INT)

---

### Task 1.2: Complete Armor System

**Priority:** HIGH
**Estimated Effort:** 3-4 hours
**Dependencies:** None
**Testing Impact:** High (affects all combat)

**Reference Documentation:**
- `docs/players_handbook/PH_armor_class_weight_cost_descriptions.md` (complete file)

**Objective:**
Create comprehensive armor database with proper AC values, costs, weights, and restrictions.

**Current State:**
- Basic armor handling exists in `aerthos/entities/player.py` (Armor class)
- No comprehensive armor data file
- Missing armor class restrictions by class

**Implementation Steps:**

1. **Create Data File:** `aerthos/data/armor.json`
   - Reference: PH_armor_class_weight_cost_descriptions.md lines 44-77

2. **Armor Structure:**
   ```json
   {
     "leather": {
       "name": "Leather Armor",
       "ac": 8,
       "cost_gp": 5,
       "weight_gp": 50,
       "armor_type": "light",
       "movement_penalty": 0,
       "allowed_classes": ["Fighter", "Ranger", "Paladin", "Cleric", "Druid", "Thief", "Assassin", "Bard", "Monk"]
     },
     "plate_mail": {
       "name": "Plate Mail",
       "ac": 3,
       "cost_gp": 400,
       "weight_gp": 400,
       "armor_type": "heavy",
       "movement_penalty": 3,
       "allowed_classes": ["Fighter", "Ranger", "Paladin", "Cleric"]
     }
   }
   ```

3. **Armor Types to Include (from PH):**
   - No Armor (AC 10)
   - Padded Armor (AC 8, 4 gp, 40 gp weight)
   - Leather Armor (AC 8, 5 gp, 50 gp weight)
   - Studded Leather (AC 7, 15 gp, 150 gp weight)
   - Ring Mail (AC 7, 30 gp, 300 gp weight)
   - Scale Mail (AC 6, 45 gp, 450 gp weight)
   - Chain Mail (AC 5, 75 gp, 750 gp weight)
   - Splinted Mail (AC 4, 80 gp, 800 gp weight)
   - Banded Mail (AC 4, 90 gp, 900 gp weight)
   - Plate Mail (AC 3, 400 gp, 4000 gp weight)

4. **Shields:**
   ```json
   "shield_small_wood": {
     "name": "Small Wooden Shield",
     "ac_bonus": 1,
     "cost_gp": 1,
     "weight_gp": 10,
     "max_attacks_per_round": 1
   },
   "shield_small": {
     "name": "Small Shield",
     "ac_bonus": 1,
     "cost_gp": 10,
     "weight_gp": 100,
     "max_attacks_per_round": 1
   },
   "shield_large": {
     "name": "Large Shield",
     "ac_bonus": 1,
     "cost_gp": 15,
     "weight_gp": 150,
     "max_attacks_per_round": 3
   }
   ```

5. **Class Restrictions (from PH_class_armor_and_weapons_restrictions.md):**
   - Update each armor entry with `allowed_classes` list
   - Enforce restrictions in character creation and equipment

6. **Magic Armor Handling:**
   - Add `magic_bonus` field to Armor dataclass
   - Magic armor negates weight for movement (note in properties)
   - +1 to +5 bonuses reduce AC by that amount

7. **Update Equipment System:** `aerthos/entities/player.py`
   - Modify Equipment class to track helmet
   - Add method: `calculate_ac(base_ac, armor, shield, dex_modifier, magic_items)`
   - Implement shield attack limit (shields don't count vs right flank/rear)

8. **Testing:**
   - Create `tests/test_armor_system.py`
   - Test AC calculations with various armor combinations
   - Test class restrictions (e.g., Magic-User can't wear armor)
   - Test magic armor bonuses
   - Test weight encumbrance effects

**Success Criteria:**
- ✅ Complete armor database (10 armor types, 3+ shield types)
- ✅ AC calculations match Players Handbook
- ✅ Class restrictions enforced
- ✅ Magic armor properly reduces AC and negates weight
- ✅ Tests passing for all armor combinations

---

### Task 1.3: Advanced Spell Levels (4-9)

**Priority:** MEDIUM-HIGH
**Estimated Effort:** 8-12 hours
**Dependencies:** Task 1.1 (Intelligence determines max spell level)
**Testing Impact:** Medium

**Reference Documentation:**
- `docs/players_handbook/PH_spell_descriptions.md` (lines 1-10000+, levels 4-9 sections)
- `docs/players_handbook/PH_spell_tables.md` (spell progression)
- `docs/players_handbook/PH_spells_by_class.md` (class availability)

**Objective:**
Expand spell database from 143 spells (levels 1-3) to complete coverage (levels 4-9 for all caster classes).

**Current State:**
- 143 spells implemented (levels 1-3 only)
- Spell system fully functional
- Parser script exists from Week 6-7

**Implementation Steps:**

1. **Spell Count Estimate (from PH):**
   - Cleric Level 4: ~10 spells
   - Cleric Level 5: ~10 spells
   - Cleric Level 6: ~8 spells
   - Cleric Level 7: ~6 spells
   - Magic-User Level 4: ~12 spells
   - Magic-User Level 5: ~12 spells
   - Magic-User Level 6: ~15 spells
   - Magic-User Level 7: ~12 spells
   - Magic-User Level 8: ~10 spells
   - Magic-User Level 9: ~8 spells
   - Druid Level 4-7: ~30 spells
   - Illusionist Level 4-7: ~25 spells
   - **Total Additional:** ~150-200 spells

2. **Parse Spells from Documentation:**
   - Use similar script to Week 6-7 implementation
   - Read `PH_spell_descriptions.md`
   - Regex pattern: `^\*   \*\*(.+?):\*\*\s+(.+)`
   - Track current class and level from headers

3. **Update:** `aerthos/data/spells.json`
   - Add spell entries for levels 4-9
   - Maintain same structure as levels 1-3
   - Include: name, level, school, casting_time, range, duration, area, saving_throw, components, description, class_availability

4. **High-Level Spell Examples to Include:**
   - Cleric 4: Cure Serious Wounds, Neutralize Poison, Divination, Tongues
   - Cleric 5: Flame Strike, Raise Dead, Commune, Quest
   - Cleric 6: Heal, Blade Barrier, Word of Recall
   - Cleric 7: Regenerate, Restoration, Resurrection
   - Magic-User 4: Dimension Door, Polymorph Self, Wall of Fire, Ice Storm
   - Magic-User 5: Teleport, Cone of Cold, Cloudkill, Feeblemind
   - Magic-User 6: Disintegrate, Globe of Invulnerability, Death Spell
   - Magic-User 7: Limited Wish, Reverse Gravity, Power Word Stun
   - Magic-User 8: Permanency, Polymorph Any Object, Power Word Blind
   - Magic-User 9: Wish, Time Stop, Gate, Meteor Swarm

5. **Intelligence-Based Spell Access:**
   - Reference: PH_ability_scores.md lines 33-50
   - INT 9: Can cast up to 4th level M-U spells
   - INT 11: Can cast up to 5th level M-U spells
   - INT 14: Can cast up to 7th level M-U spells
   - INT 16: Can cast up to 8th level M-U spells
   - INT 18: Can cast up to 9th level M-U spells

6. **Update Spell System:** `aerthos/systems/magic.py`
   - Add validation: check INT before allowing high-level spell memorization
   - Implement spell learning chance (35%-95% based on INT)
   - Implement max spells per level limits

7. **Material Components (Optional Enhancement):**
   - Add `rare_components` field for high-level spells
   - Examples: Wish (fatigue), Resurrection (cost 10,000 gp in materials)

8. **Testing:**
   - Update `tests/test_magic.py`
   - Test spell availability by level
   - Test INT restrictions for spell access
   - Test spell learning mechanics
   - Test memorization and casting of high-level spells

**Success Criteria:**
- ✅ Spell database expanded to 300+ spells (levels 1-9)
- ✅ All major iconic spells included
- ✅ Intelligence restrictions enforced
- ✅ Spell learning mechanics implemented
- ✅ Tests passing for all spell levels

---

### Task 1.4: Equipment & Gear Database

**Priority:** MEDIUM
**Estimated Effort:** 3-4 hours
**Dependencies:** None
**Testing Impact:** Low

**Reference Documentation:**
- `docs/players_handbook/PH_miscellaneous.md` (equipment lists)

**Objective:**
Create comprehensive equipment database for adventuring gear, tools, containers, clothing, food, animals, transport, etc.

**Current State:**
- Basic items exist in `aerthos/data/items.json`
- Missing comprehensive equipment catalog

**Implementation Steps:**

1. **Create/Expand Data File:** `aerthos/data/equipment.json`

2. **Equipment Categories:**

   **A. Adventuring Gear:**
   ```json
   {
     "backpack": {"name": "Backpack", "cost_gp": 2, "weight_gp": 20, "capacity_gp": 400},
     "rope_50ft": {"name": "Rope, 50 feet", "cost_gp": 1, "weight_gp": 50},
     "grappling_hook": {"name": "Grappling Hook", "cost_gp": 1, "weight_gp": 80},
     "crowbar": {"name": "Crowbar", "cost_gp": 1, "weight_gp": 50},
     "hammer": {"name": "Hammer", "cost_gp": 1, "weight_gp": 10},
     "piton": {"name": "Iron Spike/Piton", "cost_gp": 0.01, "weight_gp": 5},
     "torch": {"name": "Torch", "cost_gp": 0.01, "weight_gp": 10, "burn_time_turns": 6},
     "lantern": {"name": "Lantern", "cost_gp": 10, "weight_gp": 30},
     "oil_flask": {"name": "Oil, Flask", "cost_gp": 2, "weight_gp": 10, "burn_time_turns": 24}
   }
   ```

   **B. Containers:**
   - Waterskin (1 gp, 5 gp weight)
   - Sack, small (5 sp, 5 gp weight, capacity 200 gp)
   - Sack, large (2 gp, 10 gp weight, capacity 600 gp)
   - Chest (2 gp, 250 gp weight)
   - Pouch, belt (1 gp, 5 gp weight, capacity 50 gp)

   **C. Food & Provisions:**
   - Rations, standard (per day) (5 sp, 20 gp weight)
   - Rations, iron (per day) (1 gp, 10 gp weight, preserves 3 months)
   - Wine/ale (per quart) (varies)
   - Trail rations (per week) (5 gp, 140 gp weight)

   **D. Clothing:**
   - Clothing, common (varies, 20-50 gp weight)
   - Cloak (5 sp, 10 gp weight)
   - Boots (varies, 20 gp weight)

   **E. Tools:**
   - Thieves' tools (30 gp, 10 gp weight)
   - Healer's kit (varies)
   - Mining pick (3 gp, 100 gp weight)
   - Shovel (2 gp, 80 gp weight)

   **F. Miscellaneous:**
   - Holy symbol (25 gp, 1 gp weight)
   - Holy water, vial (25 gp, 1 gp weight)
   - Mirror, small steel (20 gp, 5 gp weight)
   - Pole, 10 ft (2 sp, 100 gp weight)

3. **Animals & Transport (Optional):**
   - Horse, riding (75 gp)
   - Horse, war (250 gp)
   - Pony (30 gp)
   - Mule (20 gp)
   - Cart (50 gp, 400 gp weight)
   - Wagon (200 gp, 2500 gp weight)

4. **Update Inventory System:**
   - Ensure container capacity tracking
   - Implement weight-in-weight (backpack reduces carried weight)

5. **Testing:**
   - Test equipment loading from JSON
   - Test inventory capacity
   - Test encumbrance with various equipment loadouts

**Success Criteria:**
- ✅ 50+ equipment items catalogued
- ✅ All costs and weights match Players Handbook
- ✅ Container capacity system working
- ✅ Equipment accessible via parser ("get rope", "use torch")

---

## PHASE 2: ADVANCED SYSTEMS (Medium Priority)

These tasks add depth and authenticity but aren't critical for core gameplay.

---

### Task 2.1: Thief Skills Validation

**Priority:** MEDIUM
**Estimated Effort:** 2-3 hours
**Dependencies:** Task 1.1 (DEX modifiers affect thief skills)
**Testing Impact:** Medium

**Reference Documentation:**
- `docs/players_handbook/PH_character_classes.md` (Thief section, skill tables)

**Objective:**
Validate existing thief skills implementation against Players Handbook tables, add missing mechanics.

**Current State:**
- Thief skills exist in `aerthos/systems/skills.py`
- Basic percentile mechanics implemented
- Missing: race modifiers, DEX adjustments, armor penalties

**Implementation Steps:**

1. **Verify Skill Base Values (from PH):**
   - Compare `aerthos/data/level_progression.json` thief_skills section
   - Update to match PH tables exactly (levels 1-23)
   - Skills: Pick Pockets, Open Locks, Find/Remove Traps, Move Silently, Hide in Shadows, Hear Noise, Climb Walls, Read Languages

2. **Racial Adjustments (from PH_character_classes.md):**
   ```json
   "racial_thief_adjustments": {
     "Dwarf": {"find_remove_traps": 10, "open_locks": 5, "climb_walls": -10, "read_languages": -5},
     "Elf": {"pick_pockets": 5, "hear_noise": 5, "hide_in_shadows": 10, "move_silently": 5, "climb_walls": -5},
     "Gnome": {"pick_pockets": 5, "find_remove_traps": 10, "open_locks": 5, "hear_noise": 10, "climb_walls": -15},
     "Half-Elf": {"pick_pockets": 10, "hide_in_shadows": 5, "hear_noise": 5},
     "Halfling": {"pick_pockets": 5, "open_locks": 5, "find_remove_traps": 5, "move_silently": 10, "hide_in_shadows": 15, "hear_noise": 5, "climb_walls": -15}
   }
   ```

3. **Dexterity Adjustments (from PH_ability_scores.md):**
   - DEX 9 or less: -15% to Pick Pockets, Open Locks, Find/Remove Traps
   - DEX 10-11: -10%
   - DEX 12-15: 0%
   - DEX 16: +5%
   - DEX 17: +10%
   - DEX 18+: +15%

4. **Armor Penalties (from PH):**
   - No armor: Full skills
   - Leather/padded: Full skills
   - Studded leather/ring: -10% to thief skills
   - Any heavier armor: Cannot use thief skills

5. **Update Skills System:** `aerthos/systems/skills.py`
   ```python
   def calculate_thief_skill(self, character, skill_name: str) -> int:
       # Base value from level
       base_value = self.get_base_skill(character.char_class, character.level, skill_name)

       # Racial adjustment
       racial_mod = self.get_racial_adjustment(character.race, skill_name)

       # DEX adjustment
       dex_mod = self.get_dex_adjustment(character.dex)

       # Armor penalty
       armor_penalty = self.get_armor_penalty(character.equipment.armor)

       return max(1, min(99, base_value + racial_mod + dex_mod - armor_penalty))
   ```

6. **Testing:**
   - Test all skill calculations with various race/DEX/armor combinations
   - Test skill progression across all levels
   - Test edge cases (skills can't go below 1% or above 99%)

**Success Criteria:**
- ✅ All thief skill base values match PH exactly
- ✅ Racial adjustments applied correctly
- ✅ DEX modifiers working
- ✅ Armor penalties enforced
- ✅ Tests passing for all thief skill mechanics

---

### Task 2.2: Movement & Encumbrance System

**Priority:** MEDIUM
**Estimated Effort:** 3-4 hours
**Dependencies:** Task 1.1 (STR determines weight allowance), Task 1.2 (armor affects movement)
**Testing Impact:** Medium

**Reference Documentation:**
- `docs/players_handbook/PH_ability_scores.md` (STR weight allowance)
- `docs/players_handbook/PH_armor_class_weight_cost_descriptions.md` (armor movement penalties)

**Objective:**
Implement comprehensive movement rate system with encumbrance effects.

**Current State:**
- Basic encumbrance check exists in `aerthos/entities/player.py` (Inventory class)
- No movement rate calculation
- Missing terrain effects, running, charging

**Implementation Steps:**

1. **Base Movement Rates (from PH):**
   ```json
   "base_movement": {
     "Human": 12,
     "Elf": 12,
     "Half-Elf": 12,
     "Dwarf": 6,
     "Gnome": 6,
     "Halfling": 6,
     "Half-Orc": 12
   }
   ```

2. **Encumbrance Categories (from PH):**
   - Unencumbered: 0 to base weight allowance = full movement
   - Lightly encumbered: up to base + 50% = 3/4 movement
   - Heavily encumbered: up to base + 100% = 1/2 movement
   - Severely encumbered: over base + 100% = 1/4 movement (can barely move)

3. **Armor Movement Penalties:**
   - No armor / Leather / Padded: 12" movement
   - Studded / Ring / Scale: 9" movement
   - Chain / Splinted / Banded: 9" movement
   - Plate: 6" movement
   - Magic armor: negates penalty (counts as no armor for movement)

4. **Create Movement System:** `aerthos/systems/movement.py`
   ```python
   class MovementSystem:
       def get_base_movement(self, race: str) -> int
       def get_encumbrance_modifier(self, current_weight: float, max_weight: float) -> float
       def get_armor_penalty(self, armor: Armor) -> int
       def calculate_movement_rate(self, character: Character) -> int
       def can_run(self, character: Character) -> bool
       def can_charge(self, character: Character) -> bool
   ```

5. **Movement Actions:**
   - Walk: base movement per round
   - Run: 3x movement for short bursts (CON rounds)
   - Charge: 2x movement in straight line (attack bonus)

6. **Update Time Tracker:** `aerthos/engine/time_tracker.py`
   - Add movement tracking per turn
   - Calculate exhaustion from running

7. **Testing:**
   - Create `tests/test_movement.py`
   - Test movement with various armor types
   - Test encumbrance effects
   - Test racial movement differences
   - Test running and charging mechanics

**Success Criteria:**
- ✅ Movement rates match PH exactly
- ✅ Encumbrance properly slows characters
- ✅ Armor penalties applied correctly
- ✅ Magic armor negates weight
- ✅ Running/charging mechanics working

---

### Task 2.3: Weapon Proficiencies & Non-Proficiency Penalties

**Priority:** MEDIUM
**Estimated Effort:** 3-4 hours
**Dependencies:** Task 1.2 (armor database), existing weapons.json
**Testing Impact:** Medium

**Reference Documentation:**
- `docs/players_handbook/PH_character_classes.md` (weapon proficiency slots by class)

**Objective:**
Implement weapon proficiency system with non-proficiency to-hit penalties.

**Current State:**
- Weapons database exists (38 weapons)
- No proficiency tracking
- No non-proficiency penalties

**Implementation Steps:**

1. **Proficiency Slots by Class (from PH):**
   ```json
   "weapon_proficiencies": {
     "Fighter": {"initial": 4, "additional_per_3_levels": 1, "non_proficiency_penalty": -2},
     "Paladin": {"initial": 3, "additional_per_3_levels": 1, "non_proficiency_penalty": -2},
     "Ranger": {"initial": 3, "additional_per_3_levels": 1, "non_proficiency_penalty": -2},
     "Cleric": {"initial": 2, "additional_per_4_levels": 1, "non_proficiency_penalty": -3},
     "Druid": {"initial": 2, "additional_per_4_levels": 1, "non_proficiency_penalty": -4},
     "Thief": {"initial": 2, "additional_per_4_levels": 1, "non_proficiency_penalty": -3},
     "Assassin": {"initial": 3, "additional_per_4_levels": 1, "non_proficiency_penalty": -3},
     "Magic-User": {"initial": 1, "additional_per_6_levels": 1, "non_proficiency_penalty": -5},
     "Illusionist": {"initial": 1, "additional_per_6_levels": 1, "non_proficiency_penalty": -5},
     "Monk": {"initial": 1, "additional_per_3_levels": 1, "non_proficiency_penalty": -3}
   }
   ```

2. **Add Proficiency Tracking:** `aerthos/entities/player.py`
   ```python
   @dataclass
   class PlayerCharacter(Character):
       weapon_proficiencies: List[str] = field(default_factory=list)
       available_proficiency_slots: int = 0
   ```

3. **Proficiency Selection:**
   - During character creation, select initial proficiencies
   - Gain additional slots at specified intervals
   - Choose from weapon list or weapon groups

4. **Update Combat System:** `aerthos/engine/combat.py`
   - Check if attacker is proficient with equipped weapon
   - Apply non-proficiency penalty to to-hit roll
   - Display warning when using non-proficient weapon

5. **Weapon Groups (Optional):**
   - Group similar weapons (e.g., "swords" includes long sword, short sword, etc.)
   - Single proficiency covers entire group

6. **Testing:**
   - Create `tests/test_proficiency.py`
   - Test proficiency slot allocation by class
   - Test non-proficiency penalties in combat
   - Test proficiency gain on level up

**Success Criteria:**
- ✅ Proficiency slots by class match PH
- ✅ Non-proficiency penalties applied correctly
- ✅ Proficiency selection during character creation
- ✅ Combat system recognizes proficiency status
- ✅ Tests passing for all classes

---

### Task 2.4: Saving Throw Enhancements

**Priority:** MEDIUM
**Estimated Effort:** 2-3 hours
**Dependencies:** Task 1.1 (WIS gives magic defense bonus)
**Testing Impact:** Medium

**Reference Documentation:**
- `docs/players_handbook/PH_character_classes.md` (saving throw tables)
- `docs/game_enhancement_docs/DM_Guide_Tables.md` (Database 3: Combat, Table 3.6)

**Objective:**
Validate and enhance saving throw system with all modifiers.

**Current State:**
- Basic saving throws exist in `aerthos/systems/saving_throws.py`
- 5 categories implemented
- Missing: racial bonuses, item bonuses, situational modifiers

**Implementation Steps:**

1. **Verify Base Tables:**
   - Compare against PH saving throw tables by class and level
   - Update `aerthos/data/level_progression.json` if needed

2. **Racial Bonuses (from PH):**
   - Dwarf/Gnome/Halfling: +1 per 3.5 CON points vs poison, magic, wands, staves, rods, spells (max +5)
   - Already implemented in racial_abilities.py, ensure integration

3. **Wisdom Bonuses (from Task 1.1):**
   - WIS 15: +1 to mental saves
   - WIS 16: +2 to mental saves
   - WIS 17: +3 to mental saves
   - WIS 18: +4 to mental saves

4. **Magic Item Bonuses:**
   - Rings of Protection: +1 to +5 to all saves
   - Cloaks of Resistance: +1 to +5 to all saves
   - Specific items vs specific save types

5. **Situational Modifiers:**
   - Cover: +2 to saves vs area effects
   - Surprised: -2 to saves
   - Blind/deaf: penalties as appropriate

6. **Update Saving Throw System:** `aerthos/systems/saving_throws.py`
   ```python
   def make_save(self, character: Character, save_type: str,
                 modifier: int = 0, situational: Dict = None) -> bool:
       base_save = self.get_base_save(character.char_class, character.level, save_type)
       racial_bonus = self.get_racial_bonus(character.race, character.con, save_type)
       wis_bonus = self.get_wisdom_bonus(character.wis, save_type)
       magic_bonus = self.get_magic_item_bonuses(character.equipment, save_type)
       situational_mod = self.calculate_situational(situational)

       total_modifier = racial_bonus + wis_bonus + magic_bonus + situational_mod + modifier
       roll = random.randint(1, 20)

       return roll + total_modifier >= base_save
   ```

7. **Testing:**
   - Update `tests/test_saving_throws.py`
   - Test all save modifiers
   - Test edge cases (very high/low saves)

**Success Criteria:**
- ✅ Base saves match PH exactly
- ✅ All modifiers (racial, WIS, magic, situational) working
- ✅ Save rolls properly calculate and display modifiers
- ✅ Tests passing for all save types and modifiers

---

## PHASE 3: OPTIONAL ENHANCEMENTS (Low Priority)

These tasks add polish and completeness but aren't essential for core AD&D 1e experience.

---

### Task 3.1: Age & Aging Effects

**Priority:** LOW
**Estimated Effort:** 2-3 hours
**Dependencies:** Task 1.1 (ability score tables)
**Testing Impact:** Low

**Reference Documentation:**
- `docs/game_enhancement_docs/DM_Guide_Tables.md` (Table 1.2 & 1.3, lines 42-81)

**Objective:**
Implement character aging with ability score modifications over time.

**Implementation Steps:**

1. **Age Categories by Race:**
   ```json
   "aging": {
     "Human": {
       "starting_age": {"Fighter": "15+1d4", "Cleric": "18+1d4", "Magic-User": "24+2d8", "Thief": "18+1d4"},
       "young_adult": [14, 20],
       "mature": [21, 40],
       "middle_aged": [41, 60],
       "old": [61, 90],
       "venerable": [91, 120]
     },
     "Elf": {
       "starting_age": {"Fighter": "130+5d6", "Cleric": "500+10d10", "Magic-User": "150+5d6"},
       "young_adult": [100, 175],
       "mature": [176, 550],
       "middle_aged": [551, 875],
       "old": [876, 1200],
       "venerable": [1201, 1600]
     }
   }
   ```

2. **Aging Effects:**
   - Young Adult: -1 WIS, +1 CON
   - Mature: +1 STR, +1 WIS
   - Middle Aged: -1 STR, -1 CON, +1 INT, +1 WIS
   - Old: -2 STR, -2 DEX, -1 CON, +1 WIS
   - Venerable: -1 STR, -1 DEX, -1 CON, +1 INT, +1 WIS

3. **Magical Aging:**
   - Some spells cause aging (Haste, etc.)
   - Potions of longevity
   - Reverse aging effects

4. **Create Aging System:** `aerthos/systems/aging.py`

**Success Criteria:**
- ✅ Starting ages by race and class
- ✅ Aging category effects implemented
- ✅ Optional: magical aging/restoration

---

### Task 3.2: Hirelings & Followers

**Priority:** LOW
**Estimated Effort:** 4-6 hours
**Dependencies:** Task 1.1 (CHA determines max hirelings and loyalty)
**Testing Impact:** Low

**Reference Documentation:**
- `docs/game_enhancement_docs/DM_Guide_Tables.md` (Database 2, lines 97-162)

**Objective:**
Implement hireling and follower system with loyalty mechanics.

**Implementation Steps:**

1. **Hireling Types:**
   - Men-at-arms (soldiers)
   - Specialists (armorer, blacksmith, etc.)
   - Mercenaries
   - Henchmen (loyal followers)

2. **Loyalty System:**
   - Base loyalty from CHA (0-20)
   - Modified by treatment (pay, danger, magic items given)
   - Morale checks in combat

3. **Max Hirelings (from CHA):**
   - CHA 3: 1 hireling
   - CHA 13: 5 hirelings
   - CHA 18: 15 hirelings

4. **Create Hireling System:** `aerthos/entities/hireling.py`, `aerthos/systems/loyalty.py`

**Success Criteria:**
- ✅ Hireling creation and management
- ✅ Loyalty calculations match PH
- ✅ Morale checks in combat

---

### Task 3.3: Psionic Abilities (Optional)

**Priority:** VERY LOW
**Estimated Effort:** 8-12 hours
**Dependencies:** None (separate subsystem)
**Testing Impact:** Low

**Reference Documentation:**
- Players Handbook Appendix I (Psionics)

**Objective:**
Implement optional psionic powers system.

**Note:** This is a complex optional system. Recommend deferring until after all other tasks complete.

---

## TESTING STRATEGY

### Continuous Testing Requirements

**After Each Task:**
1. Run full test suite: `python3 run_tests.py --no-web`
2. All 109+ tests must pass before committing
3. Add new tests for new features
4. Update existing tests if behavior changes

**Integration Testing:**
- Create end-to-end character from creation through combat
- Test all systems working together
- Verify Players Handbook accuracy

**Performance Testing:**
- Game should remain responsive (<100ms per command)
- Large spell databases should load quickly (<1 second)

---

## DOCUMENTATION REQUIREMENTS

### Per-Task Documentation

**After Each Task, Update:**
1. `CLAUDE.md` - Add new systems to "Core Game Systems" section
2. `README.md` - Update feature list if user-facing
3. Code comments - Ensure all functions have docstrings
4. Commit messages - Clear description of what was implemented

### Final Documentation

**After All Tasks Complete:**
1. Create `PLAYERS_HANDBOOK_COMPLETE.md` - Comprehensive mapping of PH to implementation
2. Update `ITEMS_REFERENCE.md` with all equipment
3. Create spell reference guide
4. Update architecture diagrams

---

## COMMIT & BRANCH STRATEGY

### Git Workflow

**Branch Naming:**
- Continue using: `claude/enhance-handbook-validation-01XEK6GdWbLsu4skKoD2sUjH`
- Or create new feature branches: `claude/feature-name-<session-id>`

**Commit Messages:**
- Format: `[Phase X.Y] Task Name - Brief description`
- Example: `[Phase 1.1] Complete Ability Score Modifier Tables - All six abilities with full PH coverage`

**After Each Task:**
```bash
git add -A
git commit -m "[Phase X.Y] Task Name - Description"
git push -u origin <branch-name>
```

**Testing Before Commit:**
```bash
python3 run_tests.py --no-web
# All tests must pass before committing
```

---

## PRIORITY EXECUTION ORDER

**Recommended Sequence:**

1. **Task 1.1** - Ability Score Tables (foundation for many other systems)
2. **Task 1.2** - Armor System (critical for combat)
3. **Task 2.1** - Thief Skills Validation (depends on Task 1.1)
4. **Task 2.2** - Movement & Encumbrance (depends on Tasks 1.1, 1.2)
5. **Task 1.4** - Equipment Database (independent, can be done anytime)
6. **Task 2.3** - Weapon Proficiencies (depends on weapons.json existing)
7. **Task 2.4** - Saving Throw Enhancements (depends on Task 1.1)
8. **Task 1.3** - Advanced Spell Levels 4-9 (large task, save for last in Phase 1)
9. **Task 3.x** - Optional enhancements as time permits

---

## SUCCESS METRICS

### Phase 1 Complete When:
- ✅ All ability score tables implemented
- ✅ Complete armor system
- ✅ Full spell library (levels 1-9, 300+ spells)
- ✅ Comprehensive equipment database
- ✅ All tests passing (150+ tests expected)

### Phase 2 Complete When:
- ✅ Thief skills fully validated
- ✅ Movement and encumbrance working
- ✅ Weapon proficiencies implemented
- ✅ Saving throws with all modifiers
- ✅ All tests passing

### Phase 3 Complete When:
- ✅ Optional systems implemented as desired
- ✅ Full documentation updated
- ✅ Players Handbook integration 100% complete

---

## ESTIMATED TOTAL EFFORT

**Phase 1:** 18-26 hours
**Phase 2:** 12-16 hours
**Phase 3:** 14-21 hours (optional)

**Total Core (Phases 1-2):** 30-42 hours
**Total Complete (All Phases):** 44-63 hours

---

## NOTES

- This plan assumes familiarity with Python, JSON data structures, and AD&D 1e mechanics
- All references to "Players Handbook" (PH) refer to AD&D 1st Edition Players Handbook
- File paths are relative to `/home/user/aerthos/`
- Test files go in `/home/user/aerthos/tests/`
- Always run tests before committing
- Keep commits atomic (one task per commit)
- Document as you go - don't leave documentation for the end

---

**End of Plan**
