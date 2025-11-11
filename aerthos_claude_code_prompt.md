# Claude Code Implementation Prompt: Aerthos Text Adventure

## Project Overview

Build **Aerthos**, a single-player text-based adventure game that faithfully emulates Advanced Dungeons & Dragons 1st Edition mechanics. The game features lethal combat, resource management, Vancian magic, and classic dungeon exploration.

**Target:** Python 3.10+, OOP architecture, ~3,000-4,000 LOC  
**Timeline:** 4-6 weeks full implementation, 2-3 weeks for playable MVP

---

## Critical Requirements

### Must-Have Features (MVP)
1. **Character System**: 4 classes (Fighter, Cleric, Magic-User, Thief), 4 races (Human, Elf, Dwarf, Halfling)
2. **THAC0 Combat**: Descending AC, proper hit/damage calculation, side initiative
3. **Vancian Magic**: Spell memorization, daily slots, casting consumes slots until rest
4. **Thief Skills**: Percentage-based skill checks for 8-10 core abilities
5. **Resource Management**: Light sources (torches/lanterns) with burn time, rations consumption
6. **Flexible Parser**: Handle variations like "attack orc", "attack the orc with sword", "carefully search for traps"
7. **Auto-Map**: ASCII map that reveals as player explores
8. **Save/Load**: Checkpoint system with manual save/restore
9. **10-Room Dungeon**: Hand-crafted linear starter dungeon
10. **Dungeon Generator**: Configurable system with "knobs" for room count, layout, difficulty

### Combat Presentation
- Quick resolution with summary narratives (not turn-by-turn detail)
- Example: "You strike the orc for 6 damage. It retaliates, missing you!"
- Monster HP hidden from player (stays mysterious like tabletop)

### Spell Components
- Abstract system: "standard" or "rare" (no granular bat guano tracking)
- Assume PCs have standard components
- Rare components only matter for high-level spells (future expansion)

### Death & Saves
- Character death is permanent within session
- Save/load system allows restoring from checkpoints
- Standard AD&D saving throws (5 categories)

---

## Project Structure

```
aerthos/
├── engine/
│   ├── game_state.py          # Central game state manager
│   ├── parser.py               # Natural language command parser
│   ├── combat.py               # Combat resolution system
│   └── time_tracker.py         # Turn/time management
├── entities/
│   ├── character.py            # Base Character class
│   ├── player.py               # PC subclass with inventory
│   ├── monster.py              # Monster subclass with AI
│   └── party.py                # (Stub for future party management)
├── systems/
│   ├── magic.py                # Vancian magic system
│   ├── skills.py               # Thief skills & ability checks
│   ├── resources.py            # Light, rations, encumbrance
│   └── saving_throws.py        # 5 save categories
├── world/
│   ├── dungeon.py              # Dungeon map & navigation
│   ├── room.py                 # Room class with encounters
│   ├── encounter.py            # Combat/trap/puzzle encounters
│   └── automap.py              # Auto-mapping display
├── data/
│   ├── classes.json            # Class definitions
│   ├── races.json              # Race modifiers
│   ├── monsters.json           # Monster stat blocks
│   ├── items.json              # Items & equipment
│   ├── spells.json             # Spell definitions
│   └── dungeons/
│       └── starter_dungeon.json  # 10-room dungeon data
├── generator/
│   ├── dungeon_generator.py    # Procedural dungeon creation
│   └── config.py               # Generator "knobs" configuration
├── ui/
│   ├── display.py              # Text formatting & output
│   ├── character_sheet.py      # Character display
│   └── save_system.py          # Save/load checkpoints
├── main.py                     # Entry point
└── tests/
    └── (unit tests for core systems)
```

---

## Core Data Structures

### Character Class

```python
class Character:
    """Base class for all entities (PCs and Monsters)"""
    
    # Core Attributes (3-18 range)
    str: int          # Strength
    dex: int          # Dexterity
    con: int          # Constitution
    int: int          # Intelligence (renamed to 'intelligence' to avoid keyword)
    wis: int          # Wisdom
    cha: int          # Charisma
    
    # Combat Stats
    hp_current: int
    hp_max: int
    ac: int           # Descending AC (10 = unarmored, 0 = plate+shield)
    thac0: int        # To Hit AC 0
    level: int
    
    # Identity
    name: str
    race: str
    char_class: str   # 'Fighter', 'Cleric', 'Magic-User', 'Thief'
    
    # State
    is_alive: bool
    conditions: List[str]  # ['poisoned', 'paralyzed', etc.]
    
    # Saving Throws (target numbers, roll d20, must roll <= target)
    save_poison: int
    save_rod_staff_wand: int
    save_petrify_paralyze: int
    save_breath: int
    save_spell: int
```

### PlayerCharacter (extends Character)

```python
class PlayerCharacter(Character):
    inventory: Inventory
    equipment: Equipment  # Worn/wielded items
    spells_known: List[Spell]
    spells_memorized: List[SpellSlot]  # Current daily slots
    
    # Thief Skills (only populated if class == 'Thief')
    thief_skills: Dict[str, int]  # skill_name: percentage (0-100)
    
    # Experience
    xp: int
    xp_to_next_level: int
```

### Monster (extends Character)

```python
class Monster(Character):
    hit_dice: str     # e.g., "2+1" or "4"
    treasure_type: str
    ai_behavior: str  # 'aggressive', 'defensive', 'flee_low_hp'
    special_abilities: List[str]
```

### Spell & SpellSlot

```python
class Spell:
    name: str
    level: int        # 1-9
    school: str
    casting_time: str
    range: str
    duration: str
    area_of_effect: str
    saving_throw: str  # "None", "Negates", "Half"
    components: str    # "standard" or "rare"
    description: str
    
    def cast(self, caster: PlayerCharacter, targets: List[Character]) -> str:
        """Execute spell effect, return narrative result"""
        pass

class SpellSlot:
    level: int
    spell: Optional[Spell]  # None if empty/used
    is_used: bool
```

### Room

```python
class Room:
    id: str
    title: str
    description: str
    exits: Dict[str, str]  # direction: room_id {'north': 'room_002'}
    encounters: List[Encounter]
    items: List[Item]
    is_explored: bool = False
    is_safe_for_rest: bool = False
    light_level: str  # 'bright', 'dim', 'dark'
    
    def on_enter(self, player: PlayerCharacter) -> str:
        """Called when player enters room"""
        self.is_explored = True
        return self.description
```

### DungeonConfig (Generator Knobs)

```python
@dataclass
class DungeonConfig:
    # Size parameters
    num_rooms: int = 10
    num_levels: int = 1
    
    # Layout
    layout_type: str = 'linear'  # 'linear', 'branching', 'network'
    dead_ends: int = 2
    
    # Encounter density (0.0 to 1.0)
    combat_frequency: float = 0.6
    trap_frequency: float = 0.3
    treasure_frequency: float = 0.4
    
    # Difficulty
    party_level: int = 1
    lethality_factor: float = 1.0  # Multiplier for encounter difficulty
    
    # Monster selection
    monster_pool: List[str] = ['kobold', 'goblin', 'orc', 'skeleton', 'giant_rat']
    
    # Rewards
    treasure_level: str = 'low'  # 'low', 'medium', 'high'
    magic_item_chance: float = 0.1
```

---

## Critical System Implementations

### 1. THAC0 Combat System

**Formula:** Roll d20, hit if `roll >= (attacker.thac0 - defender.ac)`

```python
class CombatResolver:
    
    def attack_roll(self, attacker: Character, defender: Character, 
                    weapon: Weapon = None) -> Dict:
        """
        Returns: {
            'hit': bool,
            'roll': int,
            'damage': int,
            'narrative': str,
            'defender_died': bool
        }
        """
        # 1. Roll d20
        roll = random.randint(1, 20)
        
        # 2. Critical miss/hit
        if roll == 1:
            return {
                'hit': False,
                'roll': 1,
                'damage': 0,
                'narrative': f"{attacker.name} fumbles the attack!",
                'defender_died': False
            }
        
        if roll == 20:
            damage = self._roll_damage(weapon, defender) * 2  # Double damage
            defender.hp_current -= damage
            died = defender.hp_current <= 0
            if died:
                defender.is_alive = False
            
            return {
                'hit': True,
                'roll': 20,
                'damage': damage,
                'narrative': f"{attacker.name} scores a CRITICAL HIT on {defender.name} for {damage} damage!",
                'defender_died': died
            }
        
        # 3. Normal THAC0 calculation
        target_number = attacker.thac0 - defender.ac
        hit = roll >= target_number
        
        damage = 0
        if hit:
            damage = self._roll_damage(weapon, defender)
            defender.hp_current -= damage
            died = defender.hp_current <= 0
            if died:
                defender.is_alive = False
        
        # 4. Generate narrative
        if hit:
            narrative = f"{attacker.name} hits {defender.name} for {damage} damage!"
            if died:
                narrative += f" {defender.name} falls dead!"
        else:
            narrative = f"{attacker.name} misses {defender.name}."
        
        return {
            'hit': hit,
            'roll': roll,
            'damage': damage,
            'narrative': narrative,
            'defender_died': died if hit else False
        }
    
    def _roll_damage(self, weapon: Weapon, defender: Character) -> int:
        """Roll damage based on weapon and defender size"""
        dice_str = weapon.damage_sm if defender.size in ['S', 'M'] else weapon.damage_l
        return self._parse_and_roll_dice(dice_str)
    
    def _parse_and_roll_dice(self, dice_string: str) -> int:
        """Parse '1d8', '2d6+1', '1d10' and roll"""
        # Regex: (\d+)d(\d+)([+-]\d+)?
        match = re.match(r'(\d+)d(\d+)([+-]\d+)?', dice_string)
        num_dice = int(match.group(1))
        die_size = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        total = sum(random.randint(1, die_size) for _ in range(num_dice))
        return total + modifier
```

### 2. Command Parser

**Goal:** Handle flexible input variations

```python
class CommandParser:
    
    VERBS = {
        'attack': ['attack', 'hit', 'strike', 'fight', 'kill'],
        'move': ['go', 'move', 'walk', 'travel', 'n', 'north', 's', 'south', 'e', 'east', 'w', 'west'],
        'take': ['take', 'get', 'grab', 'pick', 'pickup'],
        'use': ['use', 'drink', 'eat', 'read', 'apply'],
        'cast': ['cast'],
        'search': ['search', 'look', 'examine', 'inspect'],
        'rest': ['rest', 'sleep', 'camp'],
        'inventory': ['inventory', 'inv', 'i'],
        'status': ['status', 'stats', 'character', 'sheet'],
        'map': ['map', 'm'],
        'save': ['save'],
        'load': ['load'],
        'help': ['help', '?']
    }
    
    STOPWORDS = ['the', 'a', 'an', 'at', 'to', 'for', 'on', 'with']
    
    def parse(self, input_text: str) -> Command:
        """
        Parse input into normalized command
        
        Examples:
        - "attack orc" -> Command('attack', 'orc', None, None)
        - "attack the orc with sword" -> Command('attack', 'orc', None, 'sword')
        - "carefully search for traps" -> Command('search', 'traps', 'carefully', None)
        - "go north" -> Command('move', 'north', None, None)
        - "cast sleep on kobolds" -> Command('cast', 'sleep', 'kobolds', None)
        """
        tokens = self._tokenize(input_text.lower())
        
        if not tokens:
            return Command('invalid', None, None, None)
        
        # Extract verb
        action = self._extract_verb(tokens)
        
        # Extract target (main noun)
        target = self._extract_target(tokens, action)
        
        # Extract modifier (adverbs like 'carefully')
        modifier = self._extract_modifier(tokens)
        
        # Extract instrument (after 'with')
        instrument = self._extract_instrument(tokens)
        
        return Command(action, target, modifier, instrument)
    
    def _tokenize(self, text: str) -> List[str]:
        """Split and remove stopwords"""
        words = text.split()
        return [w for w in words if w not in self.STOPWORDS]
    
    def _extract_verb(self, tokens: List[str]) -> str:
        """Find and normalize the verb"""
        for token in tokens:
            for normalized_verb, synonyms in self.VERBS.items():
                if token in synonyms:
                    return normalized_verb
        return 'invalid'
    
    def _extract_target(self, tokens: List[str], action: str) -> Optional[str]:
        """Extract the target noun"""
        # Special case: movement directions are the target
        if action == 'move':
            directions = ['north', 'south', 'east', 'west', 'n', 's', 'e', 'w', 'up', 'down']
            for token in tokens:
                if token in directions:
                    # Normalize to full direction
                    if token == 'n': return 'north'
                    if token == 's': return 'south'
                    if token == 'e': return 'east'
                    if token == 'w': return 'west'
                    return token
        
        # For cast: next token after 'cast' is spell name
        if action == 'cast':
            try:
                cast_idx = tokens.index('cast')
                if cast_idx + 1 < len(tokens):
                    return tokens[cast_idx + 1]
            except ValueError:
                pass
        
        # General case: find first noun (not verb, not modifier)
        verb_words = [syn for syns in self.VERBS.values() for syn in syns]
        modifiers = ['carefully', 'quietly', 'quickly']
        
        for token in tokens:
            if token not in verb_words and token not in modifiers:
                return token
        
        return None
    
    def _extract_modifier(self, tokens: List[str]) -> Optional[str]:
        """Extract adverb modifiers"""
        modifiers = ['carefully', 'quietly', 'quickly', 'slowly', 'stealthily']
        for token in tokens:
            if token in modifiers:
                return token
        return None
    
    def _extract_instrument(self, tokens: List[str]) -> Optional[str]:
        """Extract instrument after 'with'"""
        try:
            with_idx = tokens.index('with')
            if with_idx + 1 < len(tokens):
                return tokens[with_idx + 1]
        except ValueError:
            pass
        return None

@dataclass
class Command:
    action: str
    target: Optional[str]
    modifier: Optional[str]
    instrument: Optional[str]
```

### 3. Vancian Magic System

```python
class MagicSystem:
    
    def memorize_spell(self, caster: PlayerCharacter, spell: Spell, slot_level: int) -> bool:
        """
        Memorize a spell into an available slot
        Returns True if successful
        """
        # Check if caster knows the spell
        if spell not in caster.spells_known:
            return False
        
        # Find an empty slot of the right level
        for slot in caster.spells_memorized:
            if slot.level == spell.level and slot.spell is None:
                slot.spell = spell
                slot.is_used = False
                return True
        
        return False  # No available slots
    
    def cast_spell(self, caster: PlayerCharacter, spell_name: str, 
                   targets: List[Character]) -> Dict:
        """
        Cast a memorized spell
        Returns: {
            'success': bool,
            'narrative': str,
            'effect_results': Dict  # Spell-specific results
        }
        """
        # Find the spell in memorized slots
        slot = None
        for s in caster.spells_memorized:
            if s.spell and s.spell.name.lower() == spell_name.lower() and not s.is_used:
                slot = s
                break
        
        if not slot:
            return {
                'success': False,
                'narrative': f"You don't have {spell_name} memorized!",
                'effect_results': {}
            }
        
        # Mark slot as used
        slot.is_used = True
        
        # Execute spell effect
        effect_results = self._execute_spell_effect(slot.spell, caster, targets)
        
        return {
            'success': True,
            'narrative': f"You cast {slot.spell.name}! {effect_results['narrative']}",
            'effect_results': effect_results
        }
    
    def rest_restore_spells(self, caster: PlayerCharacter):
        """Restore all spell slots after rest"""
        for slot in caster.spells_memorized:
            slot.is_used = False
    
    def _execute_spell_effect(self, spell: Spell, caster: PlayerCharacter, 
                              targets: List[Character]) -> Dict:
        """
        Execute spell-specific logic
        Return narrative and any mechanical results
        """
        # Dispatch to spell-specific handlers
        handlers = {
            'sleep': self._spell_sleep,
            'magic_missile': self._spell_magic_missile,
            'cure_light_wounds': self._spell_cure_light_wounds,
            # ... add more
        }
        
        handler = handlers.get(spell.name.lower().replace(' ', '_'))
        if handler:
            return handler(spell, caster, targets)
        else:
            return {'narrative': f"{spell.name} effect not implemented."}
    
    def _spell_sleep(self, spell: Spell, caster: PlayerCharacter, 
                     targets: List[Character]) -> Dict:
        """Sleep spell: 2d4 HD of creatures"""
        total_hd = random.randint(2, 8)  # 2d4
        
        # Sort targets by HD (ascending)
        sorted_targets = sorted(targets, key=lambda t: t.level)
        
        affected = []
        hd_count = 0
        
        for target in sorted_targets:
            if hd_count + target.level <= total_hd:
                target.conditions.append('sleeping')
                affected.append(target.name)
                hd_count += target.level
        
        if affected:
            return {
                'narrative': f"The following creatures fall asleep: {', '.join(affected)}",
                'affected': affected
            }
        else:
            return {
                'narrative': "The spell fails to affect any creatures.",
                'affected': []
            }
```

### 4. Time & Resource Tracking

```python
class TimeTracker:
    """Tracks game time in 10-minute turns"""
    
    def __init__(self):
        self.turns_elapsed = 0
    
    def advance_turn(self, game_state: 'GameState') -> List[str]:
        """
        Advance time by 1 turn (10 minutes)
        Returns list of event messages
        """
        self.turns_elapsed += 1
        messages = []
        
        # Consume light
        light_msg = self._consume_light(game_state.player)
        if light_msg:
            messages.append(light_msg)
        
        # Every 6 turns (1 hour), check hunger
        if self.turns_elapsed % 6 == 0:
            hunger_msg = self._check_hunger(game_state.player)
            if hunger_msg:
                messages.append(hunger_msg)
        
        return messages
    
    def _consume_light(self, player: PlayerCharacter) -> Optional[str]:
        """Decrease active light source duration"""
        light_source = player.equipment.light_source
        
        if light_source:
            light_source.turns_remaining -= 1
            
            if light_source.turns_remaining <= 0:
                player.equipment.light_source = None
                return "⚠️ Your light source sputters and dies! You are in darkness."
            elif light_source.turns_remaining == 1:
                return "⚠️ Your light source is almost exhausted!"
        
        return None
    
    def _check_hunger(self, player: PlayerCharacter) -> Optional[str]:
        """Check if player needs to eat"""
        # Simplified: track last_ate timestamp
        # For now, just a warning
        return "You're getting hungry. Consider eating rations during your next rest."
```

### 5. Auto-Map System

```python
class AutoMap:
    """
    ASCII map generation
    
    Example output:
        [ ]
         |
    [ ]-[X]-[ ]
         |
        [ ]
    
    X = current position
    """
    
    def __init__(self):
        self.explored_rooms = set()
        self.room_positions = {}  # room_id: (x, y)
    
    def generate_map(self, current_room_id: str, dungeon: 'Dungeon') -> str:
        """Generate ASCII map of explored areas"""
        
        if not self.room_positions:
            # Build coordinate system on first call
            self._build_coordinates(dungeon)
        
        # Build 2D grid
        grid = self._build_grid(current_room_id, dungeon)
        
        # Render to ASCII
        return self._render_ascii(grid, current_room_id)
    
    def _build_coordinates(self, dungeon: 'Dungeon'):
        """Recursively assign (x,y) coordinates to rooms"""
        # Start at origin
        start_room = dungeon.rooms[dungeon.start_room_id]
        self._assign_position(start_room, 0, 0, dungeon, set())
    
    def _assign_position(self, room: Room, x: int, y: int, 
                        dungeon: 'Dungeon', visited: set):
        """Recursive coordinate assignment"""
        if room.id in visited:
            return
        
        visited.add(room.id)
        self.room_positions[room.id] = (x, y)
        
        # Assign connected rooms
        direction_offsets = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0)
        }
        
        for direction, next_room_id in room.exits.items():
            if next_room_id in dungeon.rooms:
                dx, dy = direction_offsets.get(direction, (0, 0))
                next_room = dungeon.rooms[next_room_id]
                self._assign_position(next_room, x + dx, y + dy, dungeon, visited)
    
    def _build_grid(self, current_room_id: str, dungeon: 'Dungeon') -> Dict:
        """Build 2D grid of explored rooms"""
        grid = {}
        
        for room_id in self.explored_rooms:
            if room_id in self.room_positions:
                x, y = self.room_positions[room_id]
                grid[(x, y)] = room_id
        
        return grid
    
    def _render_ascii(self, grid: Dict, current_room_id: str) -> str:
        """Render grid to ASCII string"""
        if not grid:
            return "No map data available."
        
        # Find bounds
        xs = [pos[0] for pos in grid.keys()]
        ys = [pos[1] for pos in grid.keys()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        # Build ASCII
        lines = []
        for y in range(min_y, max_y + 1):
            line = ""
            for x in range(min_x, max_x + 1):
                if (x, y) in grid:
                    room_id = grid[(x, y)]
                    if room_id == current_room_id:
                        line += "[X]"
                    else:
                        line += "[ ]"
                else:
                    line += "   "
                
                # Add connector if next room exists
                if x < max_x and (x + 1, y) in grid:
                    line += "-"
                elif x < max_x:
                    line += " "
            
            lines.append(line)
            
            # Add vertical connectors
            if y < max_y:
                connector_line = ""
                for x in range(min_x, max_x + 1):
                    if (x, y) in grid and (x, y + 1) in grid:
                        connector_line += " | "
                    else:
                        connector_line += "   "
                    
                    if x < max_x:
                        connector_line += " "
                
                lines.append(connector_line)
        
        return "\n".join(lines)
```

---

## Data Files (JSON Schemas)

### classes.json

```json
{
  "Fighter": {
    "hit_die": "d10",
    "thac0_base": 20,
    "thac0_progression": -1,
    "saves": {
      "poison": 14,
      "rod_staff_wand": 16,
      "petrify_paralyze": 15,
      "breath": 17,
      "spell": 17
    },
    "prime_requisite": "STR",
    "weapons": "all",
    "armor": "all"
  },
  "Cleric": {
    "hit_die": "d8",
    "thac0_base": 20,
    "thac0_progression": -0.67,
    "saves": {
      "poison": 10,
      "rod_staff_wand": 14,
      "petrify_paralyze": 13,
      "breath": 16,
      "spell": 15
    },
    "prime_requisite": "WIS",
    "spell_slots": {
      "1": [1, 2, 2, 3, 3, 3, 4, 4, 4]
    },
    "weapons": "blunt_only",
    "armor": "all"
  },
  "Magic-User": {
    "hit_die": "d4",
    "thac0_base": 20,
    "thac0_progression": -0.33,
    "saves": {
      "poison": 14,
      "rod_staff_wand": 11,
      "petrify_paralyze": 13,
      "breath": 15,
      "spell": 12
    },
    "prime_requisite": "INT",
    "spell_slots": {
      "1": [1, 2, 2, 3, 4, 4, 4, 5, 5]
    },
    "weapons": "dagger_staff_only",
    "armor": "none"
  },
  "Thief": {
    "hit_die": "d6",
    "thac0_base": 20,
    "thac0_progression": -0.5,
    "saves": {
      "poison": 13,
      "rod_staff_wand": 14,
      "petrify_paralyze": 12,
      "breath": 16,
      "spell": 15
    },
    "prime_requisite": "DEX",
    "skills": {
      "pick_pockets": 30,
      "open_locks": 25,
      "find_traps": 20,
      "move_silently": 15,
      "hide_in_shadows": 10,
      "hear_noise": 10,
      "climb_walls": 80,
      "read_languages": 0
    },
    "skill_progression_per_level": {
      "pick_pockets": 5,
      "open_locks": 5,
      "find_traps": 5,
      "move_silently": 5,
      "hide_in_shadows": 5,
      "hear_noise": 5,
      "climb_walls": 1,
      "read_languages": 5
    },
    "weapons": "limited",
    "armor": "leather_only"
  }
}
```

### monsters.json

```json
{
  "kobold": {
    "name": "Kobold",
    "hit_dice": "1d4",
    "ac": 7,
    "thac0": 20,
    "damage": "1d4",
    "size": "S",
    "movement": 6,
    "morale": 6,
    "treasure_type": "J",
    "xp_value": 5,
    "special_abilities": [],
    "ai_behavior": "aggressive",
    "description": "A small, dog-like humanoid with scaly skin and a cowardly demeanor."
  },
  "goblin": {
    "name": "Goblin",
    "hit_dice": "1d8",
    "ac": 6,
    "thac0": 20,
    "damage": "1d6",
    "size": "S",
    "movement": 6,
    "morale": 7,
    "treasure_type": "K",
    "xp_value": 10,
    "special_abilities": [],
    "ai_behavior": "aggressive",
    "description": "A grotesque humanoid with yellow skin and malicious eyes."
  },
  "orc": {
    "name": "Orc",
    "hit_dice": "1d8",
    "ac": 6,
    "thac0": 19,
    "damage": "1d8",
    "size": "M",
    "movement": 9,
    "morale": 8,
    "treasure_type": "D",
    "xp_value": 15,
    "special_abilities": [],
    "ai_behavior": "aggressive",
    "description": "A brutish humanoid with greenish skin and tusks."
  },
  "skeleton": {
    "name": "Skeleton",
    "hit_dice": "1d8",
    "ac": 7,
    "thac0": 19,
    "damage": "1d6",
    "size": "M",
    "movement": 12,
    "morale": 12,
    "treasure_type": "None",
    "xp_value": 10,
    "special_abilities": ["immune_to_sleep", "immune_to_charm"],
    "ai_behavior": "aggressive",
    "description": "An animated skeleton, clattering bones held together by dark magic."
  },
  "giant_rat": {
    "name": "Giant Rat",
    "hit_dice": "1d4",
    "ac": 7,
    "thac0": 20,
    "damage": "1d3",
    "size": "S",
    "movement": 12,
    "morale": 5,
    "treasure_type": "C",
    "xp_value": 5,
    "special_abilities": ["disease_bite"],
    "ai_behavior": "flee_low_hp",
    "description": "A rat the size of a small dog, with matted fur and gleaming teeth."
  },
  "ogre": {
    "name": "Ogre",
    "hit_dice": "4+1",
    "ac": 5,
    "thac0": 17,
    "damage": "1d10",
    "size": "L",
    "movement": 9,
    "morale": 10,
    "treasure_type": "C+1000gp",
    "xp_value": 175,
    "special_abilities": [],
    "ai_behavior": "aggressive",
    "description": "A massive, brutish humanoid standing 9 feet tall with enormous strength."
  }
}
```

### spells.json

```json
{
  "sleep": {
    "name": "Sleep",
    "level": 1,
    "school": "enchantment",
    "casting_time": "1 segment",
    "range": "30 feet",
    "duration": "5 rounds/level",
    "area": "20-foot radius",
    "saving_throw": "None",
    "components": "standard",
    "description": "Puts 2d4 HD of creatures to sleep. Affects lowest HD creatures first.",
    "class_availability": ["Magic-User"]
  },
  "magic_missile": {
    "name": "Magic Missile",
    "level": 1,
    "school": "evocation",
    "casting_time": "1 segment",
    "range": "60 feet",
    "duration": "Instantaneous",
    "area": "1-5 targets",
    "saving_throw": "None",
    "components": "standard",
    "description": "Fires 1 missile (+1 per 2 levels after 1st). Each missile does 1d4+1 damage.",
    "class_availability": ["Magic-User"]
  },
  "cure_light_wounds": {
    "name": "Cure Light Wounds",
    "level": 1,
    "school": "necromancy",
    "casting_time": "5 segments",
    "range": "Touch",
    "duration": "Permanent",
    "area": "1 creature",
    "saving_throw": "None",
    "components": "standard",
    "description": "Heals 1d8 points of damage.",
    "class_availability": ["Cleric"]
  },
  "protection_from_evil": {
    "name": "Protection from Evil",
    "level": 1,
    "school": "abjuration",
    "casting_time": "1 segment",
    "range": "Touch",
    "duration": "12 rounds",
    "area": "1 creature",
    "saving_throw": "None",
    "components": "standard",
    "description": "Grants +2 to AC and saves against evil creatures. Prevents possession.",
    "class_availability": ["Cleric", "Magic-User"]
  },
  "detect_magic": {
    "name": "Detect Magic",
    "level": 1,
    "school": "divination",
    "casting_time": "1 round",
    "range": "60 feet",
    "duration": "2 rounds/level",
    "area": "10-foot path",
    "saving_throw": "None",
    "components": "standard",
    "description": "Detects magical auras on objects and creatures.",
    "class_availability": ["Magic-User", "Cleric"]
  }
}
```

### items.json

```json
{
  "longsword": {
    "name": "Longsword",
    "type": "weapon",
    "weight": 4,
    "damage_sm": "1d8",
    "damage_l": "1d12",
    "speed_factor": 5,
    "cost_gp": 15,
    "description": "A well-balanced blade of steel."
  },
  "dagger": {
    "name": "Dagger",
    "type": "weapon",
    "weight": 1,
    "damage_sm": "1d4",
    "damage_l": "1d3",
    "speed_factor": 2,
    "cost_gp": 2,
    "description": "A short blade, easily concealed."
  },
  "mace": {
    "name": "Mace",
    "type": "weapon",
    "weight": 8,
    "damage_sm": "1d6",
    "damage_l": "1d6",
    "speed_factor": 7,
    "cost_gp": 8,
    "description": "A heavy bludgeon with a flanged head."
  },
  "torch": {
    "name": "Torch",
    "type": "light_source",
    "weight": 1,
    "burn_time_turns": 6,
    "light_radius": 30,
    "cost_gp": 0.01,
    "description": "A wooden stick wrapped in oil-soaked cloth. Burns for 1 hour."
  },
  "lantern": {
    "name": "Lantern",
    "type": "light_source",
    "weight": 3,
    "burn_time_turns": 24,
    "light_radius": 30,
    "cost_gp": 10,
    "description": "An oil-burning lantern. Burns for 4 hours per flask of oil."
  },
  "rations": {
    "name": "Rations (1 day)",
    "type": "consumable",
    "weight": 1,
    "cost_gp": 0.5,
    "description": "Preserved food for one day."
  },
  "rope_50ft": {
    "name": "Rope (50 ft)",
    "type": "equipment",
    "weight": 5,
    "cost_gp": 1,
    "description": "Hemp rope, 50 feet long."
  },
  "leather_armor": {
    "name": "Leather Armor",
    "type": "armor",
    "weight": 15,
    "ac_bonus": 2,
    "cost_gp": 5,
    "description": "Soft leather armor. AC 8."
  },
  "chain_mail": {
    "name": "Chain Mail",
    "type": "armor",
    "weight": 30,
    "ac_bonus": 5,
    "cost_gp": 75,
    "description": "Interlocking metal rings. AC 5."
  },
  "shield": {
    "name": "Shield",
    "type": "armor",
    "weight": 10,
    "ac_bonus": 1,
    "cost_gp": 10,
    "description": "Wooden shield with metal boss. -1 AC."
  }
}
```

### starter_dungeon.json

```json
{
  "name": "The Abandoned Mine",
  "start_room": "room_001",
  "rooms": {
    "room_001": {
      "id": "room_001",
      "title": "Mine Entrance",
      "description": "The entrance to an abandoned mine. Broken timbers frame the opening. A musty smell wafts from within. Two passages lead deeper: one north, one east.",
      "light_level": "dim",
      "exits": {
        "north": "room_002",
        "east": "room_003"
      },
      "encounters": [],
      "items": ["torch"],
      "safe_rest": false
    },
    "room_002": {
      "id": "room_002",
      "title": "Guard Post",
      "description": "A small chamber with arrow slits in the walls. Old weapon racks line the walls, now empty. Kobolds have made this their guard post.",
      "light_level": "dark",
      "exits": {
        "south": "room_001",
        "north": "room_004"
      },
      "encounters": [
        {
          "type": "combat",
          "monsters": ["kobold", "kobold", "kobold"],
          "trigger": "on_enter"
        }
      ],
      "items": ["rope_50ft"],
      "safe_rest": false
    },
    "room_003": {
      "id": "room_003",
      "title": "Collapsed Tunnel",
      "description": "Rubble blocks the eastern passage. Giant rats nest in the debris. The only exit is back west.",
      "light_level": "dark",
      "exits": {
        "west": "room_001"
      },
      "encounters": [
        {
          "type": "combat",
          "monsters": ["giant_rat", "giant_rat"],
          "trigger": "on_enter"
        }
      ],
      "items": ["rations"],
      "safe_rest": false
    },
    "room_004": {
      "id": "room_004",
      "title": "Storage Chamber",
      "description": "Old crates and barrels line the walls. Most are empty, but some contain supplies. A passage continues north.",
      "light_level": "dark",
      "exits": {
        "south": "room_002",
        "north": "room_005"
      },
      "encounters": [
        {
          "type": "trap",
          "trap_type": "pit",
          "damage": "1d6",
          "detect_difficulty": 20,
          "trigger": "on_search"
        }
      ],
      "items": ["rations", "torch", "dagger"],
      "safe_rest": true
    },
    "room_005": {
      "id": "room_005",
      "title": "Crossroads",
      "description": "Three passages meet here. The walls are covered in crude goblin graffiti. You hear sounds from the east.",
      "light_level": "dark",
      "exits": {
        "south": "room_004",
        "east": "room_006",
        "north": "room_007"
      },
      "encounters": [],
      "items": [],
      "safe_rest": false
    },
    "room_006": {
      "id": "room_006",
      "title": "Goblin Den",
      "description": "A reeking chamber filled with filth and bones. Four goblins guard this area, alert to intruders.",
      "light_level": "dim",
      "exits": {
        "west": "room_005"
      },
      "encounters": [
        {
          "type": "combat",
          "monsters": ["goblin", "goblin", "goblin", "goblin"],
          "trigger": "on_enter"
        }
      ],
      "items": ["longsword", "shield"],
      "safe_rest": false
    },
    "room_007": {
      "id": "room_007",
      "title": "Old Shrine",
      "description": "A forgotten shrine to some mining deity. The altar is cracked but still intact. The air feels strangely peaceful here.",
      "light_level": "dark",
      "exits": {
        "south": "room_005",
        "north": "room_008"
      },
      "encounters": [],
      "items": [],
      "safe_rest": true
    },
    "room_008": {
      "id": "room_008",
      "title": "Burial Chamber",
      "description": "Ancient miners were laid to rest here. Now their bones have risen as skeletons, guarding their eternal rest.",
      "light_level": "dark",
      "exits": {
        "south": "room_007",
        "east": "room_009"
      },
      "encounters": [
        {
          "type": "combat",
          "monsters": ["skeleton", "skeleton"],
          "trigger": "on_enter"
        }
      ],
      "items": ["mace"],
      "safe_rest": false
    },
    "room_009": {
      "id": "room_009",
      "title": "Mine Foreman's Office",
      "description": "A small office with a desk and chairs. Papers are scattered about, illegible after years of decay. A locked chest sits in the corner.",
      "light_level": "dark",
      "exits": {
        "west": "room_008",
        "north": "room_010"
      },
      "encounters": [
        {
          "type": "puzzle",
          "puzzle_type": "locked_chest",
          "difficulty": 30,
          "reward": "treasure_chest_1"
        }
      ],
      "items": ["lantern"],
      "safe_rest": true
    },
    "room_010": {
      "id": "room_010",
      "title": "The Deep Shaft",
      "description": "A massive vertical shaft plunges into darkness. At the edge, an enormous orc guards a pile of treasure. This is the master of the mine.",
      "light_level": "dim",
      "exits": {
        "south": "room_009"
      },
      "encounters": [
        {
          "type": "combat",
          "monsters": ["ogre"],
          "trigger": "on_enter",
          "boss": true
        }
      ],
      "items": [],
      "safe_rest": false,
      "treasure": {
        "gold": 250,
        "gems": 3,
        "magic_items": ["potion_healing"]
      }
    }
  }
}
```

---

## Implementation Phases

### Phase 1: Core Engine (Priority: CRITICAL)
**Goal:** Get basic game loop working
**Time:** Week 1

**Tasks:**
1. Implement `Character`, `PlayerCharacter`, `Monster` classes
2. Implement `CombatResolver` with THAC0 calculations
3. Implement `SavingThrowResolver`
4. Implement basic `CommandParser` (5-10 core verbs)
5. Implement `Room` and `Dungeon` navigation
6. Create simple game loop: `main.py` that processes commands

**Testing:**
- Create a test character and monster manually
- Run 10 combat rounds, verify THAC0 math
- Test parser with 20+ input variations
- Navigate between 3 rooms manually

**Deliverable:** Can create a character, move between rooms, attack monsters

---

### Phase 2: Systems Integration (Priority: HIGH)
**Goal:** Add magic, skills, resources
**Time:** Week 2

**Tasks:**
1. Implement `MagicSystem` with Vancian mechanics
2. Implement spell effects for 5 core spells (sleep, magic missile, cure light wounds, etc.)
3. Implement thief skills (percentage checks)
4. Implement `Inventory` and encumbrance tracking
5. Implement `TimeTracker` with light/ration consumption
6. Implement rest system with spell restoration

**Testing:**
- Cast all 5 spells in different scenarios
- Test thief skill checks (should succeed ~expected percentage)
- Carry heavy items, verify encumbrance penalties
- Advance 100 turns, verify light extinguishes
- Rest and verify HP/spell restoration

**Deliverable:** Full character capabilities working

---

### Phase 3: Content Loading (Priority: HIGH)
**Goal:** Load game data from JSON files
**Time:** Week 3

**Tasks:**
1. Create JSON loader for classes, races, monsters, items, spells
2. Implement character creation flow (roll 3d6 in order, choose class/race)
3. Load `starter_dungeon.json`
4. Implement encounter resolution (combat, traps, puzzles)
5. Implement loot/treasure pickup
6. Implement `AutoMap` system

**Testing:**
- Create 10 characters with different class/race combos
- Walk through entire 10-room dungeon
- Trigger all encounters
- Verify map updates correctly
- Pick up all items

**Deliverable:** Complete playable dungeon

---

### Phase 4: Polish & UI (Priority: MEDIUM)
**Goal:** Make it feel good to play
**Time:** Week 4

**Tasks:**
1. Enhance parser with synonym support and better error messages
2. Create `CharacterSheet` display (formatted stat block)
3. Implement `SaveSystem` (JSON serialization)
4. Add combat narratives (flavor text for hits/misses/crits)
5. Add room flavor text variations
6. Implement death screen and restart flow

**Testing:**
- Save in 3 different rooms, reload, verify state
- Parse 50+ command variations
- Play through dungeon, rate "feel"
- Test death and restart

**Deliverable:** Polished, saveable game

---

### Phase 5: Generator System (Priority: LOW - Future)
**Goal:** Procedural dungeon creation
**Time:** Week 5

**Tasks:**
1. Implement `DungeonConfig` dataclass
2. Implement `DungeonGenerator` core logic
3. Implement layout algorithms (linear, branching, network)
4. Implement encounter placement with difficulty scaling
5. Implement treasure generation
6. Create generator CLI/config file interface

**Testing:**
- Generate 10 dungeons with different configs
- Verify solvability (can reach end)
- Verify difficulty matches config
- Play 3 generated dungeons start to finish

**Deliverable:** Configurable dungeon generator

---

## Critical Edge Cases & Requirements

### Combat
- **Zero HP:** Character dies immediately, no death saves
- **Critical hit (nat 20):** Always hits, double damage
- **Critical miss (nat 1):** Always misses, no special fumble effects (keep it simple)
- **Monster death:** Remove from encounter, drop loot/XP

### Darkness
- **No light in dark room:** Heavy penalties:
  - -4 to attack rolls
  - Cannot search for traps
  - Cannot read maps/scrolls
  - Movement slowed

### Encumbrance
- **Over max weight:** 
  - Movement reduced by half
  - -2 to DEX-based checks
  - Cannot run/flee

### Spell Casting
- **No memorized spell:** Cannot cast, clear error message
- **After cast:** Slot is consumed until rest
- **Rest required:** 8 hours in safe location

### Thief Skills
- **Failure is visible:** Always tell player the roll and result
- **Find traps:** Must explicitly search to trigger check
- **Critical fail (01-05):** Trap triggers automatically

### Saving Throws
- **Roll d20, must roll ≤ target:** Lower target is better
- **Natural 1:** Always succeeds
- **Natural 20:** Always fails

### Parser Error Handling
- **Unknown verb:** "I don't understand that command. Type 'help' for options."
- **Ambiguous target:** "Which [object]? Please be more specific."
- **Invalid direction:** "You can't go that way."

### Save System
- **Save location:** `~/.aerthos/saves/`
- **Auto-create directory:** If doesn't exist
- **Save slots:** Support 3 numbered slots
- **Save data:** Complete game state (player, dungeon, time)

---

## Performance Considerations

### JSON Loading
- Load all JSON files at startup (classes, races, monsters, items, spells)
- Cache in memory for game session
- Only dungeon needs to be mutable

### Combat Speed
- Pre-calculate THAC0 on character creation/level-up
- Cache monster stats on encounter load
- Avoid re-parsing dice strings (cache parsed dice objects)

### Parser Optimization
- Build verb dictionary once at startup
- Use fast string matching (no regex unless necessary)
- Limit token list size (max 20 words)

---

## Entry Point (main.py)

```python
#!/usr/bin/env python3
"""
Aerthos - AD&D 1e Text Adventure
Entry point for the game
"""

from engine.game_state import GameState
from engine.parser import CommandParser
from ui.display import Display
from ui.character_sheet import CharacterSheet
from world.dungeon import Dungeon
import json

def load_game_data():
    """Load all JSON data files"""
    data = {}
    data['classes'] = json.load(open('data/classes.json'))
    data['races'] = json.load(open('data/races.json'))
    data['monsters'] = json.load(open('data/monsters.json'))
    data['items'] = json.load(open('data/items.json'))
    data['spells'] = json.load(open('data/spells.json'))
    return data

def main():
    print("=" * 60)
    print("AERTHOS - Advanced Dungeons & Dragons Text Adventure")
    print("=" * 60)
    print()
    
    # Load game data
    game_data = load_game_data()
    
    # Character creation
    print("Character Creation")
    print("-" * 60)
    player = create_character(game_data)
    
    # Load dungeon
    dungeon = Dungeon.load_from_file('data/dungeons/starter_dungeon.json')
    
    # Initialize game state
    game_state = GameState(player, dungeon)
    parser = CommandParser()
    display = Display()
    
    # Main game loop
    print("\n" + "=" * 60)
    print("BEGIN ADVENTURE")
    print("=" * 60)
    print()
    
    display.show_room(game_state.current_room)
    
    while game_state.is_active:
        # Get player input
        user_input = input("\n> ").strip()
        
        if not user_input:
            continue
        
        # Parse command
        command = parser.parse(user_input)
        
        # Execute command
        result = game_state.execute_command(command)
        
        # Display result
        display.show_result(result)
        
        # Check win/loss conditions
        if game_state.player.is_alive == False:
            display.show_death_screen()
            break
        
        if game_state.is_dungeon_complete():
            display.show_victory_screen()
            break
    
    print("\nThanks for playing Aerthos!