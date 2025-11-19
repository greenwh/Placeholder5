<<<<<<< HEAD
# Players Handbook Integration Plan
**Aerthos AD&D 1e Enhancement Project**

---

## Executive Summary

This document provides a comprehensive plan to integrate all information from the Players Handbook reference materials located in `docs/players_handbook/` into the Aerthos game engine.

**Current Implementation Status:** 70-80% accurate to AD&D 1e rules
**Target Status:** 95%+ accuracy with full PHB integration

**Key Findings:**
- ✅ Core mechanics (THAC0, saves, initiative) are CORRECT
- ✅ Code architecture is solid and maintainable
- ❌ Critical bugs in ability score modifiers
- ❌ Missing racial level limits and special abilities
- ❌ Incomplete spell system (7 of 100+ spells functional)
- ❌ Limited equipment variety (5 weapons vs 30+ in PHB)

---

## Integration Priority Matrix

### CRITICAL (Week 1) - Game-Breaking Issues

| Priority | Issue | Impact | Files Affected |
|----------|-------|--------|----------------|
| **P0** | Exceptional STR damage bonuses incorrect | Fighter damage significantly off | `entities/character.py` |
| **P0** | Racial level limits not enforced | Breaks multiracial balance | `entities/player.py`, `data/races.json` |
| **P0** | Prime requisite XP bonuses missing | Slows progression for optimized characters | `entities/player.py` |

### HIGH (Week 2-3) - Core Features Missing

| Priority | Feature | Impact | Files Affected |
|----------|---------|--------|----------------|
| **P1** | Ability score benefits incomplete | INT/WIS/CHA have minimal effect | `entities/character.py`, `systems/magic.py` |
| **P1** | Racial special abilities not implemented | Races feel generic | `entities/character.py`, `data/races.json` |
| **P1** | WIS bonus spells for clerics | Clerics underpowered at high WIS | `systems/magic.py`, `ui/character_creation.py` |
| **P1** | INT spell learning for magic-users | Magic-users too consistent | `systems/magic.py`, `ui/character_creation.py` |

### MEDIUM (Week 4-6) - Content Expansion

| Priority | Feature | Impact | Files Affected |
|----------|---------|--------|----------------|
| **P2** | Expand weapon list to 30+ types | Limited combat variety | `data/items.json` |
| **P2** | Expand armor list to all PHB types | Limited equipment choices | `data/items.json` |
| **P2** | Implement remaining spell handlers | Only 7 of 22+ spells work | `systems/magic.py`, `data/spells.json` |
| **P2** | Turn undead for clerics | Core class feature missing | `systems/cleric_abilities.py` (new) |
| **P2** | Backstab for thieves | Core class feature missing | `engine/combat.py` |

### LOW (Week 7+) - Polish & Advanced Features

| Priority | Feature | Impact | Files Affected |
|----------|---------|--------|----------------|
| **P3** | Weapon vs armor type modifiers | Adds tactical depth | `engine/combat.py` |
| **P3** | Multiple attacks for high-level fighters | High-level feature | `engine/combat.py` |
| **P3** | Monk martial arts progression | Specialty class feature | `entities/monk.py` (new) |
| **P3** | Multi-class support | Advanced character option | `entities/player.py` |

---

## Phase 1: Critical Fixes (Week 1)

### 1.1 Fix Exceptional Strength Damage Bonuses

**File:** `aerthos/entities/character.py` lines 51-86

**Current (INCORRECT):**
```python
# 18/91-00: +3 to-hit, +5 damage
# 18/51-90: +2 to-hit, +3-4 damage
# 18/01-50: +1 to-hit, +3 damage
```

**Correct (from PH_ability_scores.md):**
```python
# 18/00:    +3 to-hit, +6 damage
# 18/91-99: +2 to-hit, +5 damage
# 18/76-90: +2 to-hit, +4 damage
# 18/51-75: +2 to-hit, +3 damage
# 18/01-50: +1 to-hit, +3 damage
```

**Implementation:**
```python
def _calculate_str_modifiers(self) -> tuple:
    """Calculate STR-based to-hit and damage modifiers per PHB."""
    str_val = self.str
    str_pct = self.str_percentile or 0

    if str_val < 18:
        # Standard strength table
        if str_val >= 18: return (2, 3)
        elif str_val >= 17: return (1, 1)
        elif str_val >= 16: return (0, 1)
        elif str_val >= 15: return (0, 0)
        # ... rest of table
    else:
        # Exceptional strength (fighters only)
        if str_pct == 100:  # 18/00
            return (3, 6)
        elif str_pct >= 91:  # 18/91-99
            return (2, 5)
        elif str_pct >= 76:  # 18/76-90
            return (2, 4)
        elif str_pct >= 51:  # 18/51-75
            return (2, 3)
        else:  # 18/01-50
            return (1, 3)
```

**Testing:**
- Create fighter with 18/00 STR, verify +6 damage
- Create fighter with 18/91 STR, verify +5 damage
- Run `python3 -m unittest tests.test_combat -v`

---

### 1.2 Implement Racial Level Limits

**Files:**
- `aerthos/entities/player.py` (add level limit checking)
- `aerthos/data/races.json` (add level_limits field)

**races.json Enhancement:**
```json
{
  "elf": {
    "name": "Elf",
    "ability_modifiers": {"dex": 1, "con": -1},
    "allowed_classes": ["fighter", "magic-user", "thief", "cleric"],
    "level_limits": {
      "fighter": 7,
      "magic-user": 11,
      "thief": null,
      "cleric": 9
    }
  }
}
```

**player.py Enhancement (add to level_up() function):**
```python
def level_up(self):
    """Level up character with racial limit checking."""
    # Check racial level limit
    max_level = self._get_racial_level_limit()
    if max_level and self.level >= max_level:
        return {
            "success": False,
            "message": f"{self.race}s cannot exceed level {max_level} as {self.char_class}s."
        }

    # Proceed with normal level up
    # ... existing code

def _get_racial_level_limit(self) -> int | None:
    """Get maximum level for this race/class combo."""
    race_data = load_json('races.json').get(self.race.lower())
    if not race_data:
        return None

    limits = race_data.get('level_limits', {})
    return limits.get(self.char_class.lower())
```

**Reference:** PH_races.md "Class Availability & Level Limits" table

**Testing:**
- Create elf fighter, gain XP to level 7, verify can level up
- Gain XP to level 8, verify CANNOT level up
- Test for all race/class combinations

---

### 1.3 Add Prime Requisite XP Bonuses

**File:** `aerthos/entities/player.py` lines 371-391 (gain_xp function)

**Current:**
```python
def gain_xp(self, amount: int):
    """Award experience points."""
    self.xp += amount
```

**Enhanced:**
```python
def gain_xp(self, amount: int):
    """Award experience points with prime requisite bonus."""
    # Apply prime requisite bonus (PHB: 10% for 16+)
    bonus_multiplier = 1.0

    if self.char_class == 'fighter' and self.str >= 16:
        bonus_multiplier = 1.10
    elif self.char_class == 'cleric' and self.wis >= 16:
        bonus_multiplier = 1.10
    elif self.char_class == 'magic-user' and self.int >= 16:
        bonus_multiplier = 1.10
    elif self.char_class == 'thief' and self.dex >= 16:
        bonus_multiplier = 1.10

    # TODO: Multi-prime requisite classes (Ranger, Paladin)
    # Ranger: STR/INT/WIS all 16+ = 10% bonus
    # Paladin: STR/WIS 16+ = 10% bonus

    adjusted_amount = int(amount * bonus_multiplier)
    self.xp += adjusted_amount

    return {
        "base_xp": amount,
        "bonus": adjusted_amount - amount,
        "total_xp": self.xp
    }
```

**Reference:** PH_ability_scores.md "XP Bonus" rows

**Testing:**
- Create fighter with STR 16, award 1000 XP, verify gains 1100 XP
- Create fighter with STR 15, award 1000 XP, verify gains 1000 XP

---

## Phase 2: Core Features (Week 2-3)

### 2.1 Complete Ability Score Modifiers

**File:** `aerthos/entities/character.py`

**Intelligence (NEW):**
```python
def get_additional_languages(self) -> int:
    """Number of additional languages known (PHB Table)."""
    int_table = {3:0, 8:0, 9:1, 12:2, 13:3, 14:4, 15:5, 16:6, 17:7, 18:7}
    for threshold, langs in sorted(int_table.items()):
        if self.int <= threshold:
            return langs
    return 7

def get_spell_learning_chance(self) -> int:
    """% chance to learn spell (Magic-Users only)."""
    if self.char_class != 'magic-user':
        return 100

    int_table = {
        3: 0, 8: 0, 9: 35, 10: 40, 11: 45, 12: 50,
        13: 55, 14: 60, 15: 65, 16: 75, 17: 85, 18: 95
    }
    for threshold, chance in sorted(int_table.items()):
        if self.int <= threshold:
            return chance
    return 95
```

**Wisdom (NEW):**
```python
def get_wisdom_spell_bonus(self) -> dict:
    """Bonus spells for clerics (PHB Table)."""
    if self.char_class != 'cleric':
        return {}

    wis_bonuses = {
        13: {1: 1},
        14: {1: 1},
        15: {1: 2},
        16: {1: 2, 2: 1},
        17: {1: 2, 2: 2, 3: 1},
        18: {1: 2, 2: 2, 3: 1, 4: 1}
    }

    for threshold, bonus in sorted(wis_bonuses.items()):
        if self.wis >= threshold:
            continue
        return wis_bonuses.get(self.wis - 1, {})

    return wis_bonuses.get(18, {})

def get_spell_failure_chance(self) -> int:
    """% chance divine spell fails (PHB Table)."""
    if self.char_class not in ['cleric', 'druid']:
        return 0

    wis_failure = {3: 40, 4: 35, 5: 30, 6: 25, 7: 20, 8: 15, 9: 10, 10: 5}
    return wis_failure.get(self.wis, 0)
```

**Charisma (NEW):**
```python
def get_max_henchmen(self) -> int:
    """Maximum number of henchmen (PHB Table)."""
    cha_table = {3:1, 4:1, 5:2, 6:2, 7:3, 8:3, 9:4, 10:4, 11:4, 12:5,
                 13:5, 14:6, 15:7, 16:8, 17:10, 18:15}
    for threshold, max_h in sorted(cha_table.items()):
        if self.cha <= threshold:
            return max_h
    return 15

def get_loyalty_adjustment(self) -> int:
    """Henchmen loyalty % modifier (PHB Table)."""
    cha_table = {3:-30, 4:-25, 5:-20, 6:-15, 7:-10, 8:-5, 9:0, 10:0, 11:0, 12:0,
                 13:5, 14:10, 15:15, 16:20, 17:25, 18:30}
    for threshold, adj in sorted(cha_table.items()):
        if self.cha <= threshold:
            return adj
    return 30
```

**Reference:** PH_ability_scores.md (all tables)

---

### 2.2 Implement Racial Special Abilities

**File:** `aerthos/entities/character.py`

**Add racial_abilities tracking:**
```python
class Character:
    def __init__(self, ...):
        # ... existing code
        self.racial_abilities = self._load_racial_abilities()

    def _load_racial_abilities(self) -> dict:
        """Load special abilities from race data."""
        race_data = load_json('races.json').get(self.race.lower(), {})
        return race_data.get('special_abilities', {})
```

**races.json Enhancement (Dwarf example):**
```json
{
  "dwarf": {
    "special_abilities": {
      "infravision": 60,
      "saving_throw_bonus": {
        "formula": "1 per 3.5 CON",
        "max": 5,
        "applies_to": ["magic", "poison", "wand", "rod", "staff", "spell"]
      },
      "mining_detection": {
        "grade_slope": 75,
        "new_construction": 75,
        "sliding_walls": 67,
        "traps": 50,
        "depth": 50
      },
      "combat_bonuses": {
        "bonus_vs": ["goblin", "half-orc", "hobgoblin", "orc"],
        "bonus_amount": 1,
        "ac_penalty_vs": ["ogre", "troll", "ogre_mage", "giant", "titan"],
        "ac_penalty_amount": -4
      }
    }
  }
}
```

**Implement saving throw bonus:**
```python
# In aerthos/systems/saving_throws.py
def make_save(character, save_type: str) -> dict:
    """Make a saving throw with racial bonuses."""
    base_value = character.get_save_value(save_type)

    # Apply racial bonuses
    racial_bonus = 0
    if character.race in ['dwarf', 'gnome', 'halfling']:
        # +1 per 3.5 CON vs magic/poison
        if save_type in ['poison', 'wand', 'rod', 'staff', 'spell']:
            racial_bonus = min(5, character.con // 3.5)  # max +5

    adjusted_value = base_value + racial_bonus
    roll = d20()
    success = roll <= adjusted_value

    return {
        "roll": roll,
        "target": adjusted_value,
        "success": success,
        "racial_bonus": racial_bonus
    }
```

**Reference:** PH_races.md (all racial ability sections)

---

### 2.3 Implement Spell Learning (Magic-Users)

**File:** `aerthos/systems/magic.py`

**Add spell learning check:**
```python
def attempt_learn_spell(character: PlayerCharacter, spell_id: str) -> dict:
    """Attempt to learn a spell (Magic-Users only)."""
    if character.char_class != 'magic-user':
        return {"success": False, "message": "Only magic-users learn spells"}

    # Check if already known
    if spell_id in [s['id'] for s in character.spells_known]:
        return {"success": False, "message": "Spell already known"}

    # Get INT-based learning chance
    learn_chance = character.get_spell_learning_chance()
    roll = random.randint(1, 100)

    if roll <= learn_chance:
        spell_data = load_spell_data(spell_id)
        character.spells_known.append(spell_data)
        return {
            "success": True,
            "message": f"Successfully learned {spell_data['name']}!",
            "roll": roll,
            "chance": learn_chance
        }
    else:
        # CRITICAL PHB RULE: Failed spell cannot be learned again this level
        character.failed_spells = character.failed_spells or []
        character.failed_spells.append(spell_id)

        return {
            "success": False,
            "message": f"Failed to comprehend the spell (rolled {roll}, needed {learn_chance}).",
            "roll": roll,
            "chance": learn_chance
        }
```

**Reference:** PH_ability_scores.md Intelligence table

---

### 2.4 Implement Bonus Spells (Clerics)

**File:** `aerthos/ui/character_creation.py`

**Enhance spell slot calculation:**
```python
def get_spell_slots(character: PlayerCharacter, spell_level: int) -> int:
    """Get spell slots for a given level, including WIS bonuses."""
    class_data = load_json('classes.json')[character.char_class]
    base_slots = class_data['spell_slots'][character.level - 1][spell_level - 1]

    # Add WIS bonus spells for clerics/druids
    if character.char_class in ['cleric', 'druid']:
        bonus_spells = character.get_wisdom_spell_bonus()
        base_slots += bonus_spells.get(spell_level, 0)

    return base_slots
```

**Reference:** PH_ability_scores.md Wisdom table

---

## Phase 3: Content Expansion (Week 4-6)

### 3.1 Expand Weapon List

**File:** `aerthos/data/items.json`

**Add weapons from PH_weapons_tables_and_costs.md:**

Priority weapons to add:
```json
{
  "battleaxe": {
    "name": "Battle Axe",
    "type": "weapon",
    "damage_sm": "1d8",
    "damage_l": "1d8",
    "weight": 7.5,
    "cost": 7,
    "speed_factor": 7,
    "weapon_type": "axe"
  },
  "spear": {
    "name": "Spear",
    "type": "weapon",
    "damage_sm": "1d6",
    "damage_l": "1d8",
    "weight": 5,
    "cost": 0.3,
    "speed_factor": 6,
    "weapon_type": "polearm",
    "special": "set_vs_charge_double_damage"
  },
  "flail": {
    "name": "Flail",
    "type": "weapon",
    "damage_sm": "2d4",
    "damage_l": "2d4+1",
    "weight": 7.5,
    "cost": 8,
    "speed_factor": 7,
    "weapon_type": "flail"
  },
  "two_handed_sword": {
    "name": "Two-Handed Sword",
    "type": "weapon",
    "damage_sm": "1d10",
    "damage_l": "3d6",
    "weight": 25,
    "cost": 30,
    "speed_factor": 10,
    "weapon_type": "sword",
    "hands": 2
  },
  "longbow": {
    "name": "Long Bow",
    "type": "weapon",
    "damage_sm": "1d6",
    "damage_l": "1d6",
    "weight": 3,
    "cost": 60,
    "speed_factor": 8,
    "weapon_type": "bow",
    "hands": 2,
    "range": {"short": 70, "medium": 140, "long": 210},
    "rate_of_fire": 2,
    "ammo": "arrow"
  }
}
```

**Full list (30+ weapons):** See PH_weapons_tables_and_costs.md

---

### 3.2 Expand Armor List

**File:** `aerthos/data/items.json`

**Add armor from PH_armor_class_weight_cost_descriptions.md:**

```json
{
  "padded_armor": {
    "name": "Padded Armor",
    "type": "armor",
    "ac_bonus": 2,
    "weight": 1,
    "cost": 4,
    "armor_type": "light"
  },
  "studded_leather": {
    "name": "Studded Leather",
    "type": "armor",
    "ac_bonus": 3,
    "weight": 2,
    "cost": 15,
    "armor_type": "light"
  },
  "ring_mail": {
    "name": "Ring Mail",
    "type": "armor",
    "ac_bonus": 3,
    "weight": 3.5,
    "cost": 30,
    "armor_type": "medium"
  },
  "scale_mail": {
    "name": "Scale Mail",
    "type": "armor",
    "ac_bonus": 4,
    "weight": 4.5,
    "cost": 45,
    "armor_type": "medium"
  },
  "splint_mail": {
    "name": "Splint Mail",
    "type": "armor",
    "ac_bonus": 6,
    "weight": 4,
    "cost": 80,
    "armor_type": "heavy"
  },
  "banded_mail": {
    "name": "Banded Mail",
    "type": "armor",
    "ac_bonus": 6,
    "weight": 3.5,
    "cost": 90,
    "armor_type": "heavy"
  }
}
```

---

### 3.3 Implement Spell Handlers

**File:** `aerthos/systems/magic.py`

**Current status:** 7 spells have handlers, 15+ spells defined but not implemented

**Priority spell handlers to add:**

**Level 1:**
```python
def cast_bless(caster, target_party):
    """Bless: +1 to-hit, +1 morale for 6 turns."""
    duration = 6  # turns
    for member in target_party:
        member.add_condition({
            "type": "bless",
            "to_hit_bonus": 1,
            "morale_bonus": 1,
            "duration": duration
        })
    return f"{caster.name} blesses the party! (+1 to-hit for {duration} turns)"

def cast_shield(caster):
    """Shield: AC 2 vs missiles, AC 4 vs melee, immunity to magic missile."""
    caster.add_condition({
        "type": "shield",
        "ac_bonus_missile": 8,  # Brings to AC 2
        "ac_bonus_melee": 6,    # Brings to AC 4
        "magic_missile_immunity": True,
        "duration": 5  # turns/level
    })
    return f"{caster.name} conjures a magical shield!"
```

**Level 2:**
```python
def cast_hold_person(caster, targets: list):
    """Hold Person: Paralysis on 1-4 targets."""
    for target in targets:
        save_result = make_save(target, 'spell')
        if not save_result['success']:
            target.add_condition({
                "type": "paralyzed",
                "duration": 9  # turns
            })
    return f"{caster.name} attempts to hold {len(targets)} creatures!"
```

**Implement all 22 defined spells in order of level**

**Reference:** PH_spell_descriptions.md

---

### 3.4 Turn Undead (Clerics)

**File:** `aerthos/systems/cleric_abilities.py` (NEW)

**Implementation:**
```python
def turn_undead(cleric: PlayerCharacter, undead_creatures: list) -> dict:
    """
    Attempt to turn undead (PHB Turn Undead Table).

    Returns number turned, destroyed, or failed.
    """
    if cleric.char_class != 'cleric':
        return {"success": False, "message": "Only clerics can turn undead"}

    # PHB Turn Undead Table (simplified for levels 1-3)
    turn_table = {
        # cleric_level: {undead_type: result}
        1: {
            "skeleton": 10,     # 10+ on 2d6 turns
            "zombie": 13,       # 13+ on 2d6 turns
            "ghoul": None,      # Cannot turn
        },
        2: {
            "skeleton": 7,
            "zombie": 10,
            "ghoul": 13,
            "shadow": None,
        },
        3: {
            "skeleton": "D",    # Destroyed automatically
            "zombie": 7,
            "ghoul": 10,
            "shadow": 13,
            "wight": None,
        }
    }

    results = []
    for creature in undead_creatures:
        undead_type = creature.creature_type.lower()
        turn_value = turn_table.get(cleric.level, {}).get(undead_type)

        if turn_value is None:
            results.append({"creature": creature, "result": "no_effect"})
        elif turn_value == "D":
            creature.hp_current = 0
            results.append({"creature": creature, "result": "destroyed"})
        else:
            roll = random.randint(2, 12)  # 2d6
            if roll >= turn_value:
                creature.add_condition({"type": "turned", "duration": 10})
                results.append({"creature": creature, "result": "turned", "roll": roll})
            else:
                results.append({"creature": creature, "result": "failed", "roll": roll})

    return results
```

**Add to parser commands:**
```python
# In aerthos/engine/parser.py
if action == "turn":
    if "undead" in objects or "undead" in text:
        return self.handle_turn_undead()
```

**Reference:** PH_character_classes.md (Cleric section)

---

### 3.5 Backstab (Thieves)

**File:** `aerthos/engine/combat.py`

**Add backstab mechanics:**
```python
def attempt_backstab(attacker: PlayerCharacter, defender) -> dict:
    """
    Backstab attack (Thieves only).

    Requirements:
    - Thief class
    - Defender surprised or unaware
    - Attack from behind

    Damage multiplier:
    - Levels 1-4: x2
    - Levels 5-8: x3
    - Levels 9-12: x4
    - Levels 13+: x5
    """
    if attacker.char_class != 'thief':
        return {"success": False, "message": "Only thieves can backstab"}

    # Determine multiplier
    if attacker.level <= 4:
        multiplier = 2
    elif attacker.level <= 8:
        multiplier = 3
    elif attacker.level <= 12:
        multiplier = 4
    else:
        multiplier = 5

    # Make attack roll with +4 to-hit (surprise bonus)
    attack_result = resolve_attack(attacker, defender, to_hit_bonus=4)

    if attack_result['hit']:
        # Multiply damage
        base_damage = attack_result['damage']
        backstab_damage = base_damage * multiplier

        defender.take_damage(backstab_damage)

        return {
            "success": True,
            "damage": backstab_damage,
            "multiplier": multiplier,
            "message": f"{attacker.name} backstabs for {backstab_damage} damage! (x{multiplier})"
        }
    else:
        return {
            "success": False,
            "message": f"{attacker.name}'s backstab attempt misses!"
        }
```

**Reference:** PH_character_classes.md (Thief section)

---

## Phase 4: Polish & Advanced Features (Week 7+)

### 4.1 Weapon vs Armor Type Modifiers

**File:** `aerthos/engine/combat.py`

**Add weapon vs armor matrix:**
```python
# From PHB weapon vs armor tables
WEAPON_VS_ARMOR = {
    "sword": {
        "plate": -3,
        "chain": 0,
        "leather": +2
    },
    "axe": {
        "plate": -1,
        "chain": +1,
        "leather": +1
    },
    "flail": {
        "plate": +2,
        "chain": +2,
        "leather": 0
    },
    # ... full table from PHB
}

def get_weapon_vs_armor_modifier(weapon_type: str, armor_type: str) -> int:
    """Get to-hit modifier for weapon vs armor type."""
    return WEAPON_VS_ARMOR.get(weapon_type, {}).get(armor_type, 0)
```

**Reference:** PH_combat_procedures.md

---

### 4.2 Multiple Attacks (High-Level Fighters)

**File:** `aerthos/engine/combat.py`

**Implementation:**
```python
def get_attacks_per_round(character: PlayerCharacter) -> float:
    """
    Get number of attacks per round (PHB).

    Fighters:
    - Levels 1-6: 1/round
    - Levels 7-12: 3/2 rounds (1.5 attacks)
    - Levels 13+: 2/round
    """
    if character.char_class != 'fighter':
        return 1.0

    if character.level >= 13:
        return 2.0
    elif character.level >= 7:
        return 1.5
    else:
        return 1.0
```

**Track fractional attacks:**
```python
class Combat:
    def __init__(self):
        self.attack_carryover = {}  # Track 0.5 attack for next round

    def resolve_round(self, attacker, defender):
        attacks = get_attacks_per_round(attacker)
        full_attacks = int(attacks)
        partial = attacks - full_attacks

        # Carry over 0.5 attack
        carried = self.attack_carryover.get(attacker.name, 0)
        if carried + partial >= 1.0:
            full_attacks += 1
            self.attack_carryover[attacker.name] = (carried + partial) - 1.0
        else:
            self.attack_carryover[attacker.name] = carried + partial

        # Execute attacks
        for i in range(full_attacks):
            resolve_attack(attacker, defender)
```

**Reference:** PH_character_classes.md (Fighter section)

---

### 4.3 Multi-Class Support

**File:** `aerthos/entities/player.py`

**This is complex - requires:**
- XP splitting between classes
- Separate level tracking
- Hit die averaging
- Combined abilities

**Defer to Phase 4+ (advanced feature)**

---

## Testing Strategy

### Test Files to Create/Update

1. **tests/test_ability_scores.py** (NEW)
   - Test all ability score modifiers
   - Test exceptional strength damage
   - Test INT spell learning
   - Test WIS bonus spells

2. **tests/test_racial_abilities.py** (NEW)
   - Test level limits
   - Test saving throw bonuses
   - Test special abilities

3. **tests/test_experience.py** (UPDATE)
   - Test prime requisite bonuses
   - Test level limit enforcement

4. **tests/test_magic.py** (UPDATE)
   - Test spell learning mechanics
   - Test bonus spell slots
   - Test spell failure chance

5. **tests/test_combat.py** (UPDATE)
   - Test backstab damage multipliers
   - Test turn undead
   - Test multiple attacks

### Manual Testing Checklist

**Phase 1:**
- [ ] Create fighter with 18/00 STR, verify +6 damage
- [ ] Create elf fighter, verify cannot exceed level 7
- [ ] Create fighter with STR 16, verify 10% XP bonus

**Phase 2:**
- [ ] Create magic-user with INT 9, verify 35% spell learning
- [ ] Create cleric with WIS 18, verify bonus spells
- [ ] Create dwarf, verify saving throw bonuses vs magic

**Phase 3:**
- [ ] Equip all new weapon types
- [ ] Test turn undead against skeleton
- [ ] Test thief backstab with x2-x5 multipliers

---

## Implementation Schedule

### Week 1: Critical Fixes
- **Day 1-2:** Fix exceptional strength (1.1)
- **Day 3-4:** Implement racial level limits (1.2)
- **Day 5:** Add prime requisite XP bonuses (1.3)
- **Day 6-7:** Testing and bug fixes

### Week 2: Ability Scores
- **Day 1-3:** Complete all ability score modifiers (2.1)
- **Day 4-5:** Implement spell learning and bonus spells (2.3, 2.4)
- **Day 6-7:** Testing

### Week 3: Racial Abilities
- **Day 1-4:** Implement all racial special abilities (2.2)
- **Day 5-7:** Testing and refinement

### Week 4-5: Equipment Expansion
- **Day 1-7:** Add all weapons from PHB (3.1)
- **Day 8-10:** Add all armor from PHB (3.2)

### Week 6: Spell Expansion
- **Day 1-7:** Implement handlers for all defined spells (3.3)

### Week 7: Class Abilities
- **Day 1-3:** Turn undead (3.4)
- **Day 4-7:** Backstab (3.5)

### Week 8+: Advanced Features
- Weapon vs armor modifiers
- Multiple attacks
- Multi-class support

---

## Data File Changes Summary

### races.json
- Add `level_limits` field for each race
- Add `special_abilities` with detailed mechanics
- Keep existing structure intact

### classes.json
- No changes needed (already accurate)

### items.json
- Add 25+ weapons from PHB
- Add 5+ armor types from PHB
- Add `weapon_type` field for weapon vs armor modifiers

### spells.json
- Already has 22 spells defined
- No structural changes needed
- Just implement handlers in magic.py

---

## Code File Changes Summary

### entities/character.py
- Fix exceptional strength damage (lines 68-85)
- Add INT language/spell learning methods
- Add WIS bonus spell/spell failure methods
- Add CHA henchmen/loyalty methods
- Add racial ability loading

### entities/player.py
- Add racial level limit checking (level_up function)
- Add prime requisite XP bonus (gain_xp function)
- No other major changes

### systems/magic.py
- Implement spell learning with INT check
- Implement bonus spell slots from WIS
- Add spell failure chance check
- Implement 15 new spell handlers

### systems/saving_throws.py
- Add racial bonus calculation
- Add condition/item modifiers

### systems/cleric_abilities.py (NEW)
- Implement turn undead mechanics
- Add to parser integration

### engine/combat.py
- Add backstab mechanics
- Add weapon vs armor modifiers
- Add multiple attack tracking

---

## Migration Path

### For Existing Save Files

**Challenge:** Adding new fields to character data might break existing saves.

**Solution:**
```python
def migrate_character_data(character_dict: dict) -> dict:
    """Migrate old save files to new format."""
    # Add default values for new fields
    if 'racial_abilities' not in character_dict:
        character_dict['racial_abilities'] = {}

    if 'failed_spells' not in character_dict:
        character_dict['failed_spells'] = []

    # Recalculate ability modifiers with new formulas
    # (non-destructive, just updates derived values)

    return character_dict
```

**Call in load functions:**
```python
def load_character(file_path: str) -> PlayerCharacter:
    data = load_json(file_path)
    data = migrate_character_data(data)  # Migrate before loading
    return PlayerCharacter.from_dict(data)
```

---

## Success Metrics

### Quantitative
- ✅ All 11 races with full special abilities
- ✅ All 4 core classes with complete mechanics
- ✅ 30+ weapons implemented
- ✅ 10+ armor types implemented
- ✅ 20+ spells with handlers
- ✅ 95%+ test coverage for new features
- ✅ All integration tests passing

### Qualitative
- ✅ Game feels authentic to AD&D 1e PHB
- ✅ Character creation choices are meaningful
- ✅ Combat has tactical depth
- ✅ Magic system is strategic
- ✅ Racial/class identity is distinctive

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking existing saves | Medium | High | Implement migration system first |
| Test suite failures | High | Medium | Fix tests incrementally per phase |
| Ability score changes affect balance | Low | Medium | Use PHB values exactly |
| Spell implementation bugs | Medium | Low | Test each spell individually |
| Performance degradation | Low | Low | Profile before/after |

---

## Future Enhancements (Beyond PHB Integration)

Once PHB integration is complete, consider:

1. **Dungeon Master's Guide Integration**
   - Magic item creation rules
   - Dungeon design guidelines
   - Advanced combat options

2. **Monster Manual Integration**
   - Expand monster roster
   - Add special abilities
   - Improve AI behavior

3. **Unearthed Arcana Content**
   - Additional classes (Barbarian, Cavalier)
   - Comeliness attribute
   - Weapon specialization

4. **Quality of Life**
   - Character sheet export to PDF
   - Session replay/logging
   - AI-powered DM narration

---

## Conclusion

This integration plan provides a systematic approach to bringing Aerthos to 95%+ AD&D 1e PHB accuracy. The phased approach ensures:

1. **Critical bugs fixed first** (Week 1)
2. **Core features added next** (Week 2-3)
3. **Content expansion** (Week 4-6)
4. **Polish last** (Week 7+)

**Total Estimated Timeline:** 8-10 weeks for full integration

**Current Status:** 70-80% accurate
**Target Status:** 95%+ accurate

The solid code architecture makes this integration straightforward. Most changes are data additions or minor logic updates, not major refactoring.

**Priority: Start with Phase 1 (Week 1) critical fixes immediately.**

---

**Document Version:** 1.0
**Date:** 2025-11-18
**Author:** Aerthos Development Team
**Based on:** Players Handbook docs analysis and comprehensive codebase review
||||||| f063438
=======
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

### ✅ Phase 1.2: Complete Armor System (COMPLETED 2025-11-18)
- Comprehensive armor database (9 armor types, 4 shields, 2 helmets)
- Class armor/shield restrictions for all 11 classes
- AC calculations with armor, shields, DEX modifiers
- Movement rates by armor type (light 12", heavy 9", very_heavy 6")
- Magic armor bonuses (AC reduction, weight negation)
- Shield attack blocking limits (small=1, medium=2, large=3)
- **Files:** `aerthos/data/armor.json`, `aerthos/systems/armor_system.py`, `aerthos/entities/player.py` (modified), `tests/test_armor_system.py`

### ✅ Phase 1.3: Expand Spell Database to Levels 4-9 (COMPLETED 2025-11-18)
- Expanded spell database from 143 to 332 spells (+189 new spells)
- Complete spell coverage: Cleric (1-7), Druid (1-7), Magic-User (1-9), Illusionist (1-7)
- All iconic high-level spells: Wish, Time Stop, Resurrection, Gate, Meteor Swarm, etc.
- Automated parser for extracting spells from PH documentation
- Proper class assignments for all divine and arcane casters
- **Files:** `aerthos/data/spells.json` (modified, +2841 lines)

### ✅ Phase 1.4: Complete Equipment & Gear Database (COMPLETED 2025-11-18)
- Comprehensive equipment database with 65 items (exceeds 50+ requirement)
- All standard adventuring gear: ropes, tools, light sources, containers, food
- Container capacity tracking for weight-in-weight calculations
- Animals and transport with movement/carrying capacity
- Special items: thieves' tools, holy water, wolfsbane, garlic
- **Files:** `aerthos/data/equipment.json` (created, 485 lines)

**All Tests Passing:** 154/154 tests ✅ (109 original + 19 ability modifiers + 26 armor system)

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

### Task 1.2: Complete Armor System ✅ COMPLETED

**Status:** ✅ COMPLETED (2025-11-18)
**Actual Effort:** ~4 hours
**Commit:** `572fa9c` - "Implement Task 1.2: Complete Armor System with Class Restrictions"
**Files Created:**
- `aerthos/data/armor.json` (213 lines added)
- `aerthos/systems/armor_system.py` (289 lines)
- `tests/test_armor_system.py` (26 tests, all passing)
**Files Modified:**
- `aerthos/entities/player.py` (added Shield dataclass, updated Armor and Equipment classes)
- `aerthos/ui/character_creation.py` (updated to use ArmorSystem)
- `run_tests.py` (added new test files to test suite)

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

**Completion Notes:**
- Created comprehensive armor.json with 9 armor types, 4 shields, 2 helmets, and all 11 class restrictions
- Modified Armor dataclass to include AC, armor_type, movement_rate (light 12", heavy 9", very_heavy 6")
- Created separate Shield dataclass with ac_bonus and max_attacks_blocked
- Updated Equipment class with improved get_total_ac(), get_movement_rate(), get_total_weight()
- Created ArmorSystem for armor creation, restriction validation, best armor lookups
- Updated character_creation.py to use ArmorSystem instead of direct Armor instantiation
- All 26 armor tests passing, total test count increased to 154
- Magic armor bonus system implemented (reduces AC, negates weight penalty)
- Shield attack blocking limits implemented (small=1, medium=2, large=3)
- Ready for integration with combat system to enforce movement rates by armor type

---

### Task 1.3: Advanced Spell Levels (4-9) ✅ COMPLETED

**Status:** ✅ COMPLETED (2025-11-18)
**Actual Effort:** ~3 hours
**Commit:** `4d43f5a` - "Implement Task 1.3: Expand Spell Database to Levels 4-9"
**Files Modified:**
- `aerthos/data/spells.json` (+2841 lines, 143→332 spells)

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

**Completion Notes:**
- Expanded spell database from 143 to 332 spells (+189 new spells, 132% increase)
- Created automated parser to extract spells from PH_spell_descriptions.md
- Added Cleric spells levels 4-7: 38 new spells (76 total, covers all divine magic)
- Added Druid spells levels 4-7: 38 new spells (66 total, complete druidic spell list)
- Added Magic-User spells levels 4-9: 97 new spells (175 total, full arcane progression)
- Added Illusionist spells levels 4-7: 16 new spells (33 total, complete illusion school)
- Fixed class assignment issues (Druid spells were initially marked as Cleric, Illusionist as Magic-User)
- All iconic high-level spells included: Wish, Time Stop, Resurrection, Gate, Meteor Swarm, etc.
- All 154 tests passing (no regressions from spell expansion)
- Intelligence max spell level restrictions already implemented in Task 1.1 (AbilityModifierSystem.can_learn_spell_level)
- Spell learning mechanics already implemented in Task 1.1 (attempt_spell_learning with INT-based success chance)
- Ready for high-level character play (levels 7-20 with full spell progression)

---

### Task 1.4: Equipment & Gear Database ✅ COMPLETED

**Status:** ✅ COMPLETED (2025-11-18)
**Actual Effort:** ~1 hour
**Commit:** `b229d60` - "Implement Task 1.4: Complete Equipment & Gear Database"
**Files Created:**
- `aerthos/data/equipment.json` (485 lines, 65 equipment items)

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

**Completion Notes:**
- Created equipment.json with 65 items (exceeds 50+ requirement by 30%)
- Comprehensive coverage of all standard AD&D 1e equipment categories
- Equipment categories: 24 general equipment, 9 containers, 9 consumables, 6 tools, 5 clothing, 4 light sources, 4 animals, 2 transport, 2 religious
- Container capacity tracking implemented (backpack 400 gp, large sack 600 gp, chest 1000 gp, etc.)
- All costs and weights sourced from AD&D 1e Players Handbook standards
- Light sources include burn_time_turns for gameplay mechanics (torch 6 turns, lantern 24 turns)
- Animals and transport include movement_rate and carrying_capacity_gp fields
- Special items included: thieves' tools (30 gp), healer's kit (25 gp), holy water (25 gp), wolfsbane, garlic
- Supports weight-in-weight calculations via capacity_gp fields in containers
- All 154 tests passing (no regressions)
- Ready for integration with inventory system and parser for "get", "use", "equip" commands

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
>>>>>>> claude/enhance-handbook-validation-01XEK6GdWbLsu4skKoD2sUjH
