# Aerthos Technical Specification
## AD&D 1e Text Adventure Engine

**Version:** 1.0  
**Target:** Python 3.10+  
**Architecture:** Object-Oriented, Event-Driven

---

## 1. System Architecture Overview

### 1.1 Core Components

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
│   └── party.py                # (Future: party management)
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
└── ui/
    ├── display.py              # Text formatting & output
    ├── character_sheet.py      # Character display
    └── save_system.py          # Save/load checkpoints
```

### 1.2 Data Flow

```
Player Input → Parser → Game State → System Resolution → Output Display
                           ↓
                    Save/Checkpoint System
```

---

## 2. Core Data Structures

### 2.1 Character Class Hierarchy

```python
class Character:
    """Base class for all entities (PCs and Monsters)"""
    
    # Core Attributes
    str: int          # Strength (3-18, +percentile for 18)
    dex: int          # Dexterity
    con: int          # Constitution
    int: int          # Intelligence
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
    char_class: str   # 'class' is reserved keyword
    
    # State
    is_alive: bool
    conditions: List[str]  # ['poisoned', 'paralyzed', etc.]
    
    # Saving Throws (by category)
    save_poison: int
    save_rod_staff_wand: int
    save_petrify_paralyze: int
    save_breath: int
    save_spell: int


class PlayerCharacter(Character):
    """PC-specific attributes"""
    
    inventory: Inventory
    equipment: Equipment  # Worn/wielded items
    spells_known: List[Spell]
    spells_memorized: List[Spell]  # Current daily slots
    
    # Thief Skills (if applicable)
    thief_skills: Dict[str, int]  # skill_name: percentage
    
    # Experience
    xp: int
    xp_to_next_level: int


class Monster(Character):
    """Monster-specific attributes"""
    
    hit_dice: str     # e.g., "2+1" or "4"
    treasure_type: str
    ai_behavior: str  # 'aggressive', 'defensive', 'flee_low_hp'
    special_abilities: List[str]
```

### 2.2 Inventory & Encumbrance

```python
class Item:
    name: str
    weight: float     # In pounds (AD&D standard)
    item_type: str    # 'weapon', 'armor', 'consumable', 'treasure', etc.
    properties: Dict  # Type-specific data


class Weapon(Item):
    damage_sm: str    # Damage vs Small/Medium (e.g., "1d8")
    damage_l: str     # Damage vs Large (e.g., "1d12")
    speed_factor: int # Initiative modifier


class Inventory:
    items: List[Item]
    max_weight: int   # Based on STR
    
    @property
    def current_weight(self) -> float:
        return sum(item.weight for item in self.items)
    
    @property
    def is_encumbered(self) -> bool:
        return self.current_weight > self.max_weight
```

### 2.3 Spell System

```python
class Spell:
    name: str
    level: int
    school: str       # 'evocation', 'necromancy', etc.
    casting_time: str # "1 segment", "1 round", etc.
    range: str        # "60 feet", "Touch", etc.
    duration: str     # "1 turn/level", "Instantaneous", etc.
    area_of_effect: str
    saving_throw: str # "None", "Negates", "Half", etc.
    components_abstract: str  # "Standard" or "Rare" (no detailed tracking)
    
    def cast(self, caster: PlayerCharacter, targets: List[Character]) -> str:
        """Execute spell effect, return narrative result"""
        pass


class SpellSlot:
    level: int
    spell: Optional[Spell]  # None if empty/used
    is_used: bool
```

---

## 3. Core Systems Implementation

### 3.1 Combat System (THAC0)

```python
class CombatResolver:
    
    def attack_roll(self, attacker: Character, defender: Character, 
                    weapon: Weapon = None) -> Dict:
        """
        Returns: {
            'hit': bool,
            'roll': int,
            'damage': int,
            'narrative': str
        }
        """
        # 1. Roll d20
        roll = random.randint(1, 20)
        
        # 2. Check critical miss/hit
        if roll == 1:
            return self._critical_miss(attacker)
        if roll == 20:
            return self._critical_hit(attacker, defender, weapon)
        
        # 3. THAC0 calculation: Roll >= THAC0 - Target AC
        target_number = attacker.thac0 - defender.ac
        hit = roll >= target_number
        
        # 4. Calculate damage if hit
        damage = 0
        if hit:
            damage = self._roll_damage(weapon, defender.size)
            defender.hp_current -= damage
            
            if defender.hp_current <= 0:
                defender.is_alive = False
        
        # 5. Generate narrative
        narrative = self._generate_combat_text(attacker, defender, hit, damage)
        
        return {
            'hit': hit,
            'roll': roll,
            'damage': damage,
            'narrative': narrative
        }
    
    def _roll_damage(self, weapon: Weapon, target_size: str) -> int:
        """Roll appropriate damage dice based on target size"""
        dice_string = weapon.damage_sm if target_size in ['S', 'M'] else weapon.damage_l
        return self._roll_dice(dice_string)
    
    def _roll_dice(self, dice_string: str) -> int:
        """Parse and roll dice (e.g., '1d8+2', '2d6')"""
        # Implementation: regex parse, roll, sum
        pass
```

### 3.2 Saving Throw System

```python
class SavingThrowResolver:
    
    CATEGORIES = {
        'poison': 'save_poison',
        'rod': 'save_rod_staff_wand',
        'petrify': 'save_petrify_paralyze',
        'breath': 'save_breath',
        'spell': 'save_spell'
    }
    
    def make_save(self, character: Character, category: str, 
                  modifier: int = 0) -> Dict:
        """
        Returns: {
            'success': bool,
            'roll': int,
            'target': int,
            'narrative': str
        }
        """
        # Get target number from character
        save_attr = self.CATEGORIES[category]
        target = getattr(character, save_attr)
        
        # Roll d20 (lower is better in AD&D saves)
        roll = random.randint(1, 20) + modifier
        success = roll <= target
        
        narrative = f"{character.name} rolls {roll} vs {target} ({category}): {'SUCCESS' if success else 'FAILURE'}!"
        
        return {
            'success': success,
            'roll': roll,
            'target': target,
            'narrative': narrative
        }
```

### 3.3 Natural Language Parser

```python
class CommandParser:
    """
    Flexible parser supporting variations:
    - "attack orc"
    - "attack the orc with sword"
    - "carefully search for traps"
    - "cast sleep on kobolds"
    """
    
    VERBS = {
        'attack': ['attack', 'hit', 'strike', 'fight', 'kill'],
        'move': ['go', 'move', 'walk', 'travel', 'north', 'south', 'east', 'west'],
        'take': ['take', 'get', 'grab', 'pick up'],
        'use': ['use', 'drink', 'eat', 'read'],
        'cast': ['cast'],
        'search': ['search', 'look for', 'examine'],
        'rest': ['rest', 'sleep', 'camp'],
        'inventory': ['inventory', 'inv', 'i'],
        'status': ['status', 'stats', 'character'],
        'map': ['map'],
        'save': ['save'],
        'load': ['load']
    }
    
    def parse(self, input_text: str) -> Command:
        """
        Returns Command object with:
        - action: str (normalized verb)
        - target: str (object of action)
        - modifier: str (adverbs like 'carefully')
        - instrument: str (tool/weapon used)
        """
        tokens = self._tokenize(input_text.lower())
        
        # Identify verb
        action = self._extract_verb(tokens)
        
        # Extract target (noun)
        target = self._extract_target(tokens)
        
        # Extract modifiers
        modifier = self._extract_modifier(tokens)
        
        # Extract instrument ("with sword")
        instrument = self._extract_instrument(tokens)
        
        return Command(action, target, modifier, instrument)
    
    def _tokenize(self, text: str) -> List[str]:
        # Remove articles, split on whitespace
        stopwords = ['the', 'a', 'an']
        return [w for w in text.split() if w not in stopwords]
```

---

## 4. Resource Management

### 4.1 Time & Light Tracking

```python
class TimeTracker:
    """Tracks game time in 10-minute turns"""
    
    turns_elapsed: int = 0
    
    # Light sources burn time (in turns)
    LIGHT_DURATION = {
        'torch': 6,      # 1 hour
        'lantern': 24    # 4 hours
    }
    
    def advance_turn(self, game_state: GameState):
        self.turns_elapsed += 1
        
        # Decrease light
        self._consume_light(game_state.player)
        
        # Every 6 turns (1 hour), check hunger/fatigue
        if self.turns_elapsed % 6 == 0:
            self._check_rations(game_state.player)
    
    def _consume_light(self, player: PlayerCharacter):
        # Find active light source in inventory
        light_source = player.equipment.light_source
        
        if light_source:
            light_source.turns_remaining -= 1
            
            if light_source.turns_remaining <= 0:
                # Light goes out!
                player.equipment.light_source = None
                return "Your light source sputters and dies! You are in darkness."
```

### 4.2 Rest & Recovery

```python
class RestSystem:
    
    def attempt_rest(self, player: PlayerCharacter, location: Room) -> Dict:
        """
        Returns: {
            'success': bool,
            'hp_recovered': int,
            'spells_restored': bool,
            'interrupted': bool,
            'narrative': str
        }
        """
        # Check if location is safe
        if not location.is_safe_for_rest:
            return {'success': False, 'narrative': "This area is too dangerous to rest!"}
        
        # Consume rations
        if not self._consume_ration(player):
            return {'success': False, 'narrative': "You have no rations to eat!"}
        
        # Random encounter check
        if random.random() < 0.15:  # 15% chance
            return {'success': False, 'interrupted': True, 
                    'narrative': "Your rest is interrupted by wandering monsters!"}
        
        # Successful rest
        hp_recovered = self._recover_hp(player)
        player.restore_spells()  # Restore all memorized spell slots
        
        return {
            'success': True,
            'hp_recovered': hp_recovered,
            'spells_restored': True,
            'narrative': f"You rest for 8 hours. HP restored: {hp_recovered}. Spells memorized."
        }
```

---

## 5. World & Navigation

### 5.1 Room Structure

```python
class Room:
    id: str
    title: str
    description: str
    exits: Dict[str, str]  # direction: room_id
    encounters: List[Encounter]
    items: List[Item]
    is_explored: bool = False
    is_safe_for_rest: bool = False
    light_level: str  # 'bright', 'dim', 'dark'
    
    def on_enter(self, player: PlayerCharacter) -> str:
        """Called when player enters room"""
        self.is_explored = True
        
        # Check light requirements
        if self.light_level == 'dark' and not player.has_light():
            return self._describe_darkness()
        
        return self.description


class Encounter:
    encounter_type: str  # 'combat', 'trap', 'puzzle', 'treasure'
    is_active: bool
    difficulty: int
    
    # Type-specific data
    monsters: List[Monster]  # If combat
    trap_data: Dict          # If trap
    puzzle_data: Dict        # If puzzle
```

### 5.2 Auto-Map System

```python
class AutoMap:
    """
    Generates ASCII map as player explores
    Example output:
    
        [ ]
         |
    [ ]-[X]-[ ]
         |
        [ ]
    
    X = current position
    [ ] = explored room
    """
    
    explored_rooms: Set[str]
    room_positions: Dict[str, Tuple[int, int]]  # room_id: (x, y)
    
    def generate_map(self, current_room: str, dungeon: Dungeon) -> str:
        # Build 2D grid representation
        grid = self._build_grid(current_room, dungeon)
        return self._render_ascii(grid)
    
    def _build_grid(self, current: str, dungeon: Dungeon) -> List[List[str]]:
        # Recursive traversal of explored rooms
        # Build coordinate system and connections
        pass
```

---

## 6. Game Generator System

### 6.1 Configuration "Knobs"

```python
@dataclass
class DungeonConfig:
    """Generator configuration"""
    
    # Size parameters
    num_rooms: int = 10
    num_levels: int = 1
    
    # Layout
    layout_type: str = 'linear'  # 'linear', 'branching', 'network'
    dead_ends: int = 2           # Number of dead-end branches
    
    # Encounter density
    combat_frequency: float = 0.6  # 60% of rooms have combat
    trap_frequency: float = 0.3
    treasure_frequency: float = 0.4
    
    # Difficulty
    party_level: int = 1
    lethality_factor: float = 1.0  # Multiplier for encounter difficulty
    
    # Monster selection
    monster_pool: List[str] = field(default_factory=lambda: [
        'kobold', 'goblin', 'orc', 'skeleton', 'giant_rat'
    ])
    
    # Rewards
    treasure_level: str = 'low'  # 'low', 'medium', 'high'
    magic_item_chance: float = 0.1


class DungeonGenerator:
    
    def generate(self, config: DungeonConfig) -> Dungeon:
        """Generate complete dungeon from config"""
        
        # 1. Generate room graph
        rooms = self._generate_rooms(config)
        
        # 2. Populate encounters
        self._populate_encounters(rooms, config)
        
        # 3. Place treasures
        self._place_treasures(rooms, config)
        
        # 4. Add flavor descriptions
        self._add_descriptions(rooms)
        
        return Dungeon(rooms, config)
    
    def _generate_rooms(self, config: DungeonConfig) -> List[Room]:
        if config.layout_type == 'linear':
            return self._generate_linear_path(config.num_rooms)
        elif config.layout_type == 'branching':
            return self._generate_branching_dungeon(config)
        # ... etc
```

---

## 7. Save System

### 7.1 Checkpoint Structure

```python
@dataclass
class SaveData:
    """Complete game state snapshot"""
    
    timestamp: datetime
    player: PlayerCharacter
    current_room_id: str
    dungeon_state: Dict  # Room exploration, loot taken, monsters killed
    time_tracker: TimeTracker
    
    def to_json(self) -> str:
        """Serialize to JSON"""
        pass
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SaveData':
        """Deserialize from JSON"""
        pass


class SaveSystem:
    
    SAVE_DIR = Path.home() / '.aerthos' / 'saves'
    
    def save_game(self, game_state: GameState, slot: int = 1):
        save_data = SaveData(
            timestamp=datetime.now(),
            player=game_state.player,
            current_room_id=game_state.current_room.id,
            dungeon_state=game_state.dungeon.serialize(),
            time_tracker=game_state.time_tracker
        )
        
        filepath = self.SAVE_DIR / f'save_{slot}.json'
        filepath.write_text(save_data.to_json())
    
    def load_game(self, slot: int = 1) -> GameState:
        filepath = self.SAVE_DIR / f'save_{slot}.json'
        save_data = SaveData.from_json(filepath.read_text())
        
        return GameState.from_save_data(save_data)
```

---

## 8. Implementation Phases

### Phase 1: Core Engine (Week 1)
- [ ] Character class hierarchy
- [ ] Basic THAC0 combat
- [ ] Saving throws
- [ ] Command parser (basic verbs)
- [ ] Room navigation

### Phase 2: Systems (Week 2)
- [ ] Vancian magic system
- [ ] Thief skills
- [ ] Inventory & encumbrance
- [ ] Time tracking & light
- [ ] Rest system

### Phase 3: Content (Week 3)
- [ ] Monster definitions (10-15 types)
- [ ] Item database
- [ ] Spell database
- [ ] 10-room starter dungeon (hand-crafted)
- [ ] Encounter logic

### Phase 4: Polish (Week 4)
- [ ] Auto-map display
- [ ] Save/load system
- [ ] Enhanced parser (flexible inputs)
- [ ] Combat narratives
- [ ] Character creation flow

### Phase 5: Generator (Week 5)
- [ ] Dungeon generator core
- [ ] Configuration system
- [ ] Random encounter placement
- [ ] Treasure generation
- [ ] Testing & balance

---

## 9. Data Schema Examples

### 9.1 Monster Definition (JSON)

```json
{
  "orc": {
    "name": "Orc",
    "hit_dice": "1",
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
  }
}
```

### 9.2 Spell Definition (JSON)

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
    "effect": "Puts 2d4 HD of creatures to sleep (lowest HD first)",
    "implementation": "sleep_spell_handler"
  }
}
```

### 9.3 Room Definition (JSON)

```json
{
  "room_001": {
    "title": "Torch-lit Entry Hall",
    "description": "Stone walls glisten with moisture. Two torches flicker in rusted sconces. A musty smell fills the air.",
    "light_level": "dim",
    "exits": {
      "north": "room_002",
      "east": "room_003"
    },
    "encounters": [
      {
        "type": "combat",
        "monsters": ["kobold", "kobold", "kobold"],
        "trigger": "on_enter"
      }
    ],
    "items": ["torch", "rope_50ft"],
    "safe_rest": false
  }
}
```

---

## 10. Next Steps

This specification provides the foundation for implementation. The next document will be the **Claude Code Handoff Prompt** with:

1. Prioritized implementation order
2. Testing requirements for each phase
3. Example code snippets for critical systems
4. Edge cases and error handling requirements
5. Performance considerations

**Total Estimated LOC:** ~3,000-4,000 lines of Python
**Development Time:** 4-6 weeks for full implementation
**Core Playable MVP:** 2-3 weeks