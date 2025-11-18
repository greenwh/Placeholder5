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
