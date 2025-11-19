# Feature Plan: Party-Aware Dungeon Generation (Priority 2)

## Overview
Implement simple interview system to gather party information and generate appropriately-scaled dungeons based on actual party composition, level, and equipment.

## Current State
- Preset difficulties (EASY/STANDARD/HARD) use hardcoded party_level 1 or 2
- `DungeonConfig.for_party()` method exists but unused (lines 79-143 in config.py)
- `MonsterScaler` can select appropriate monsters but not invoked
- Dungeons created before party selection

## Design Goals (from scenario_generation_difficulty_determination.md)
Implement SIMPLE interview process with 4 key questions:
1. **Average Party Level (APL)** - Most important factor
2. **Party Size** - Number of characters
3. **Party Composition** - Class mix (fighters/clerics/mages/thieves)
4. **Magical Item Accumulation** - Effective power boost

Accept non-answers and make best guesses. Keep it simple.

## Implementation Plan

### Phase 1: Party Interview System (2-3 hours)

**File: `aerthos/ui/dungeon_interview.py` (NEW)**

Create simple interview with smart defaults:

```python
class DungeonInterview:
    """Simple interview to gather party info for dungeon generation"""

    def conduct_interview(self, party: Optional[Party] = None,
                          party_manager: Optional[PartyManager] = None) -> Dict:
        """
        Ask 4 simple questions, accept non-answers, make educated guesses

        Two modes:
        1. Select from saved parties (if party_manager provided)
        2. Answer 4 questions manually

        If party object provided, pre-fill answers and ask for confirmation only

        Returns:
            Dict with: apl, party_size, composition, magic_level, difficulty_preference
        """
```

**Interview Flow (NEW - Two Paths):**

```
═══════════════════════════════════════════════════════════════
DUNGEON DIFFICULTY SETUP
═══════════════════════════════════════════════════════════════

I need to understand your party to create an appropriate challenge.

Choose your approach:

  1. Select a saved party (I'll analyze and tailor the dungeon)
  2. Answer questions manually (for custom/hypothetical parties)

Choose 1-2: _

[IF OPTION 1 SELECTED:]
═══════════════════════════════════════════════════════════════
SAVED PARTIES
═══════════════════════════════════════════════════════════════

Select a party to adventure with:

  1. The Fellowship (4 characters, Average Level 2)
     - Thorin (Fighter-3), Gandalf (Magic-User-2)
     - Gimli (Cleric-2), Bilbo (Thief-2)

  2. Solo Heroes (1 character, Level 3)
     - Conan (Fighter-3)

  3. The Wizard's Guild (3 characters, Average Level 2)
     - Elminster (Magic-User-3), Mordenkainen (Magic-User-2)
     - Bigby (Magic-User-2)

  4. [Back to manual entry]

Choose 1-4: _

[User selects party #1 - "The Fellowship"]

═══════════════════════════════════════════════════════════════
ANALYZING: The Fellowship
═══════════════════════════════════════════════════════════════

Party Composition Detected:
  • 4 members
  • Average Level: 2.25 → 2
  • 1 Fighter (Thorin-3)
  • 1 Cleric (Gimli-2) - Has healing
  • 1 Magic-User (Gandalf-2) - Has AoE spells
  • 1 Thief (Bilbo-2) - Can handle traps
  • Total HP Pool: 38
  • Magic Items: 2x +1 weapons, 3x healing potions
  • Assessment: Balanced party, medium magic items

Recommended Difficulty: Standard (balanced challenge)

═══════════════════════════════════════════════════════════════
CONFIRMATION
═══════════════════════════════════════════════════════════════

Based on this party, I'll create:
  • Dungeon for Level 2 party (adjusted for 4 members)
  • Monsters: Goblins, Orcs, Skeletons, Hobgoblin boss
  • Encounter density: 60% combat, 20% traps, 20% empty
  • Treasure level: Medium
  • Lethality: Standard (1.0x)

Adjust difficulty?
  1. Easier - Reduce monster strength by one step
  2. As recommended - Standard challenge
  3. Harder - Increase monster strength and density

Choose 1-3 or press Enter for [2-Standard]: _

[User presses Enter or chooses option]

✓ Generating dungeon tailored for The Fellowship...

[IF OPTION 2 SELECTED - Manual Entry:]
═══════════════════════════════════════════════════════════════
DUNGEON DIFFICULTY QUESTIONNAIRE
═══════════════════════════════════════════════════════════════

I'll ask 4 simple questions about your party.
Press Enter to skip any question - I'll make my best guess!

Question 1 of 4
───────────────────────────────────────────────────────────────
What is your party's AVERAGE LEVEL?
(This is the single most important factor for difficulty)

[Detected: 2] Press Enter to accept, or type new value: _

Question 2 of 4
───────────────────────────────────────────────────────────────
How many characters in the party?

[Detected: 3] Press Enter to accept, or type new value: _

Question 3 of 4
───────────────────────────────────────────────────────────────
What is your party composition?

[Detected: 1 Fighter, 1 Magic-User, 1 Thief]

1. Balanced (fighters + magic + healing)
2. Heavy Combat (mostly fighters/warriors)
3. Magic Heavy (multiple spellcasters)
4. Rogue Heavy (thieves/rangers)
5. [Keep detected composition]

Choose 1-5 or press Enter for detected: _

Question 4 of 4
───────────────────────────────────────────────────────────────
What is your magic item level?

1. None/Few - Starting characters, basic equipment
2. Low - A few +1 items, some potions
3. Medium - Several +1/+2 items, scrolls, rings
4. High - Multiple +2/+3 items, powerful artifacts

Choose 1-4 or press Enter for [1-None/Few]: _

Final Question
───────────────────────────────────────────────────────────────
Preferred difficulty?

1. Easy - Fewer encounters, simpler layout
2. Standard - Balanced challenge
3. Hard - More encounters, complex layout, higher lethality

Choose 1-3 or press Enter for [2-Standard]: _
```

**Implementation Details:**

```python
class DungeonInterview:
    def __init__(self, party_manager: Optional[PartyManager] = None):
        self.party_manager = party_manager

    def conduct_interview(self, party: Optional[Party] = None) -> Dict:
        """Main entry point - routes to party selection or manual entry"""

        # Show mode selection
        print("Choose your approach:")
        print("  1. Select a saved party (I'll analyze and tailor)")
        print("  2. Answer questions manually")
        choice = input("Choose 1-2: ").strip()

        if choice == '1' and self.party_manager:
            return self._party_selection_mode()
        else:
            return self._manual_entry_mode(party)

    def _party_selection_mode(self) -> Dict:
        """Let user select from saved parties"""

        # Get all saved parties
        saved_parties = self.party_manager.list_parties()

        if not saved_parties:
            print("No saved parties found. Switching to manual entry.")
            return self._manual_entry_mode(None)

        # Display parties
        print("\nSAVED PARTIES\n")
        for idx, party_info in enumerate(saved_parties, 1):
            party_obj = self.party_manager.load_party(party_info['id'])
            apl = party_obj.average_level
            size = party_obj.size()
            print(f"  {idx}. {party_info['name']} ({size} characters, Avg Level {apl:.0f})")

            # Show first 4 members
            for member in party_obj.members[:4]:
                print(f"     - {member.name} ({member.char_class}-{member.level})")
            if len(party_obj.members) > 4:
                print(f"     ... and {len(party_obj.members) - 4} more")
            print()

        print(f"  {len(saved_parties) + 1}. [Back to manual entry]")

        # Get selection
        while True:
            choice = input(f"Choose 1-{len(saved_parties) + 1}: ").strip()
            try:
                idx = int(choice)
                if 1 <= idx <= len(saved_parties):
                    # Load and analyze party
                    party_id = saved_parties[idx - 1]['id']
                    party_obj = self.party_manager.load_party(party_id)
                    return self._analyze_and_confirm(party_obj)
                elif idx == len(saved_parties) + 1:
                    return self._manual_entry_mode(None)
            except ValueError:
                pass
            print("Invalid choice.")

    def _analyze_and_confirm(self, party: Party) -> Dict:
        """Analyze selected party and show recommendations"""

        from ..systems.party_analyzer import PartyAnalyzer
        analyzer = PartyAnalyzer()

        # Analyze party
        analysis = analyzer.analyze_party(party)

        # Display analysis
        print(f"\n{'═' * 63}")
        print(f"ANALYZING: {party.members[0].name}'s Party")
        print(f"{'═' * 63}\n")

        print("Party Composition Detected:")
        print(f"  • {analysis['party_size']} members")
        print(f"  • Average Level: {analysis['apl']:.2f} → {int(analysis['apl'])}")

        for member in party.members:
            print(f"  • {member.name} ({member.char_class}-{member.level})")

        print(f"  • Total HP Pool: {analysis['hp_pool']}")
        print(f"  • Magic Items: {analysis['magic_level']}")

        if analysis['has_healing']:
            print("  • Has healing capability")
        if analysis['has_thief_skills']:
            print("  • Can handle traps")
        if analysis['has_aoe_magic']:
            print("  • Has area-effect spells")

        # Show recommended dungeon config
        print(f"\n{'═' * 63}")
        print("RECOMMENDED DUNGEON")
        print(f"{'═' * 63}\n")

        config_preview = self._generate_config_preview(analysis)
        for line in config_preview:
            print(f"  • {line}")

        # Difficulty adjustment
        print("\nAdjust difficulty?")
        print("  1. Easier - Reduce monster strength")
        print("  2. As recommended - Standard challenge")
        print("  3. Harder - Increase monster strength")

        adj_choice = input("Choose 1-3 or press Enter for [2-Standard]: ").strip()

        if adj_choice == '1':
            analysis['difficulty_adjustment'] = 'easier'
        elif adj_choice == '3':
            analysis['difficulty_adjustment'] = 'harder'
        else:
            analysis['difficulty_adjustment'] = 'standard'

        return analysis

    def _generate_config_preview(self, analysis: Dict) -> List[str]:
        """Generate preview of dungeon configuration"""

        from ..generator.monster_scaling import MonsterScaler
        scaler = MonsterScaler()

        apl = int(analysis['apl'])
        party_size = analysis['party_size']

        # Get monster pool
        monsters = scaler.get_monster_pool_for_party(apl, party_size)
        boss = scaler.get_boss_for_party(apl, party_size)

        preview = [
            f"Dungeon for Level {apl} party (adjusted for {party_size} members)",
            f"Monsters: {', '.join(monsters[:4])}",
            f"Boss: {boss}",
            f"Encounter density: 60% combat, 20% traps, 20% empty",
            f"Treasure level: {analysis['magic_level']}",
            "Lethality: Standard (1.0x)"
        ]

        return preview

    def _manual_entry_mode(self, party: Optional[Party]) -> Dict:
        """Ask 4 questions manually"""
        # [EXISTING IMPLEMENTATION - 4 questions]
```

**Smart Defaults:**
- **Path 1 (Party Selection)**: Full auto-detection from saved party
- **Path 2 (Manual Entry)**: If party provided, pre-fill; else use defaults
- If partial answers: Use provided + detected + defaults
- Always succeed - never error on bad input

### Phase 2: Party Analysis System (1-2 hours)

**File: `aerthos/systems/party_analyzer.py` (NEW)**

Analyze party capabilities:

```python
class PartyAnalyzer:
    """Analyzes party composition for dungeon scaling"""

    def analyze_party(self, party: Party) -> Dict:
        """
        Analyze party capabilities

        Returns:
            {
                'apl': float,              # Average party level
                'party_size': int,
                'fighters': int,           # Count of melee classes
                'healers': int,            # Count of clerics
                'casters': int,            # Count of magic-users
                'thieves': int,            # Count of rogues
                'hp_pool': int,            # Total party HP
                'has_thief_skills': bool,  # Can handle traps
                'has_healing': bool,       # Can sustain longer
                'has_aoe_magic': bool,     # Can handle swarms
                'magic_level': str,        # 'none', 'low', 'medium', 'high'
                'effective_level': float   # APL + magic boost
            }
        """
```

**Magic Level Detection:**
```python
def assess_magic_items(self, party: Party) -> str:
    """
    Assess party's magical item level

    Logic:
    - Count +1 or better weapons/armor
    - Check for magical accessories (rings, scrolls, etc.)
    - Return 'none', 'low', 'medium', or 'high'
    """
```

### Phase 3: Dynamic Config Generation (1-2 hours)

**File: `aerthos/generator/config.py` (MODIFY)**

Enhance `for_party()` method to use interview results:

```python
@classmethod
def from_interview(cls, interview_results: Dict, **kwargs) -> 'DungeonConfig':
    """
    Create DungeonConfig from interview results

    Uses:
    - MonsterScaler to select appropriate monsters
    - Party composition to adjust encounter types
    - Magic level to adjust treasure and item requirements
    - Effective level for challenge rating

    Args:
        interview_results: Dict from DungeonInterview
        **kwargs: Override any parameters

    Returns:
        DungeonConfig scaled to party
    """
```

**Scaling Logic:**

```python
# Base on APL + magic boost
effective_level = apl + magic_boost

# Select monsters appropriate for effective level
scaler = MonsterScaler()
monster_pool = scaler.get_monster_pool_for_party(effective_level, party_size)

# Adjust encounter frequency based on composition
if composition == 'heavy_combat':
    combat_frequency = 0.7  # More fights
    trap_frequency = 0.1    # Fewer traps
elif composition == 'magic_heavy':
    combat_frequency = 0.5  # Fewer fights (conserve spells)
    trap_frequency = 0.2
elif composition == 'rogue_heavy':
    trap_frequency = 0.3    # More traps (they can handle)
    combat_frequency = 0.5

# Adjust based on healers
if has_healing:
    lethality_factor = 1.0  # Standard
else:
    lethality_factor = 0.8  # Easier (no healing)

# Adjust treasure for magic level
if magic_level == 'none':
    # Must provide magic weapons for higher monsters
    guaranteed_items = ['+1 weapon', 'healing potion']
    magic_item_chance = 0.15
elif magic_level == 'high':
    # Can be stingy with loot
    magic_item_chance = 0.05
```

### Phase 4: Integration with Main Menu (1 hour)

**File: `main.py` (MODIFY)**

Update dungeon generation flow:

```python
def start_new_game(game_data: GameData) -> tuple:
    """Start a new game with character creation"""

    # Character creation
    creator = CharacterCreator(game_data)
    player = creator.create_character()

    # [EXISTING CODE - show character sheet]

    # Choose dungeon type
    dungeon_choice = choose_dungeon_type()

    if dungeon_choice != '1':  # Not fixed dungeon
        # NEW: Conduct interview for generated dungeons
        from aerthos.ui.dungeon_interview import DungeonInterview
        from aerthos.storage.party_manager import PartyManager

        # Initialize interview with party manager for saved party option
        party_manager = PartyManager()
        interview = DungeonInterview(party_manager=party_manager)

        # User can select saved party OR answer questions manually
        # Pass solo player for manual mode detection
        party_info = interview.conduct_interview(party=player)

        # Generate config from interview
        config = DungeonConfig.from_interview(party_info)

        # Generate dungeon
        generator = DungeonGenerator(game_data)
        dungeon_data = generator.generate(config)
        dungeon = Dungeon.load_from_generator(dungeon_data)
```

**For Party Sessions:**
```python
def start_party_session(session_id: str):
    """Load party session"""

    # [EXISTING CODE - load party]

    # If new dungeon needed
    dungeon_choice = choose_dungeon_type()

    if dungeon_choice != '1':
        from aerthos.ui.dungeon_interview import DungeonInterview
        from aerthos.storage.party_manager import PartyManager

        # Initialize interview with party manager
        party_manager = PartyManager()
        interview = DungeonInterview(party_manager=party_manager)

        # User can select saved party OR answer questions manually
        # If party already loaded, pass it for pre-fill
        party_info = interview.conduct_interview(party=party)

        config = DungeonConfig.from_interview(party_info)
        # [Continue dungeon generation]
```

**New flow at dungeon generation prompt:**
```
═══════════════════════════════════════════════════════════════
DUNGEON SELECTION
═══════════════════════════════════════════════════════════════

  1. The Abandoned Mine (Fixed - 10 rooms)
  2. Generate Random Dungeon (Party-Aware)
  3. Generate Random Dungeon (Custom Config)

Choose 1-3: 2

[User selects option 2 - Party-Aware]

═══════════════════════════════════════════════════════════════
DUNGEON DIFFICULTY SETUP
═══════════════════════════════════════════════════════════════

Choose your approach:

  1. Select a saved party (I'll analyze and tailor)
  2. Answer questions manually (for custom parties)

Choose 1-2: 1

[Shows saved parties list...]
```

### Phase 5: Monster Requirement Warnings (30 minutes)

**File: `aerthos/systems/party_analyzer.py` (ADD)**

Check party readiness:

```python
def check_party_readiness(self, party: Party, config: DungeonConfig) -> List[str]:
    """
    Check if party is ready for dungeon difficulty

    Returns:
        List of warning messages (empty if ready)
    """

    warnings = []

    # Check for magic weapons if needed
    if config.requires_magic_weapons():
        if not self.has_magic_weapons(party):
            warnings.append(
                "⚠️  WARNING: This dungeon contains creatures requiring "
                "+1 or better weapons to hit! Your fighters lack magic weapons."
            )

    # Check for healing
    if config.party_level >= 3 and not self.has_healer(party):
        warnings.append(
            "⚠️  WARNING: No healer in party. Consider bringing potions!"
        )

    # Check for trap removal
    if config.trap_frequency > 0.2 and not self.has_thief(party):
        warnings.append(
            "⚠️  WARNING: High trap density but no thief! "
            "Expect to take damage from traps."
        )

    return warnings
```

Show warnings before dungeon entry, allow cancel.

### Phase 6: Testing (1 hour)

**File: `tests/test_party_aware_dungeons.py` (NEW)**

Test cases:

**Party Selection Mode:**
- List saved parties correctly
- Load selected party and analyze
- Analysis detects APL, composition, magic items correctly
- Preview shows appropriate monsters for party level
- Difficulty adjustment modifies config
- "Back to manual" option works

**Manual Entry Mode:**
- Interview with all answers provided
- Interview with no answers (all defaults)
- Interview with partial answers
- Party detection from existing party
- Solo player treated as party of 1

**Config Generation:**
- Config scales correctly for level 1-5 parties
- Magic level affects monster selection
- Composition affects encounter mix
- Difficulty adjustment (easier/standard/harder) works

**Party Analysis:**
- Detects fighters, clerics, mages, thieves correctly
- Calculates APL correctly (2.25 → 2)
- Assesses magic item level (none/low/medium/high)
- Identifies capabilities (healing, traps, AoE spells)

**Integration:**
- Readiness warnings trigger correctly
- Config generates valid dungeons
- Both modes produce same quality dungeons

## Configuration Constants

Add to `aerthos/constants.py`:
```python
# Party Analysis
MAGIC_LEVEL_NONE = 'none'
MAGIC_LEVEL_LOW = 'low'
MAGIC_LEVEL_MEDIUM = 'medium'
MAGIC_LEVEL_HIGH = 'high'

# Magic boost to effective level
MAGIC_BOOST_LOW = 0.5
MAGIC_BOOST_MEDIUM = 1.0
MAGIC_BOOST_HIGH = 1.5

# Composition types
COMPOSITION_BALANCED = 'balanced'
COMPOSITION_HEAVY_COMBAT = 'heavy_combat'
COMPOSITION_MAGIC_HEAVY = 'magic_heavy'
COMPOSITION_ROGUE_HEAVY = 'rogue_heavy'
```

## Success Criteria

✅ **Two-path system works smoothly**
  - Can select from saved parties list
  - Can answer 4 questions manually
  - Both paths lead to appropriate dungeons

✅ **Party selection mode functional**
  - Lists all saved parties with summary
  - Loads and analyzes selected party
  - Shows comprehensive party analysis
  - Displays recommended dungeon config preview
  - Allows difficulty adjustment (easier/standard/harder)

✅ **Manual entry mode functional**
  - Interview asks 4 simple questions with clear defaults
  - Can skip all questions and get reasonable dungeon
  - Party detection pre-fills answers accurately

✅ **Dynamic scaling works**
  - Generated dungeons scale to actual party level (not hardcoded 1-2)
  - Monster pools appropriate for party effective level
  - Composition affects encounter type distribution
  - Magic level affects loot and monster requirements

✅ **Quality assurance**
  - Warnings shown for unprepared parties
  - All existing tests still pass
  - New party-aware tests pass (15+ test cases)
  - Both paths produce balanced, fun dungeons

## Risks & Mitigations

**Risk**: Interview too long/tedious
**Mitigation**: Keep to 4 questions max, smart defaults, skip-all option

**Risk**: Wrong difficulty calculation
**Mitigation**: Use existing MonsterScaler, follow AD&D HD-per-level guidelines

**Risk**: Breaking existing preset dungeons
**Mitigation**: Keep EASY/STANDARD/HARD presets, new system is optional path

## Estimated Time: 6-9 hours total

## Files Created/Modified
- **NEW**: `aerthos/ui/dungeon_interview.py`
- **NEW**: `aerthos/systems/party_analyzer.py`
- **NEW**: `tests/test_party_aware_dungeons.py`
- **MODIFY**: `aerthos/generator/config.py` (~80 lines added)
- **MODIFY**: `main.py` (~60 lines modified)
- **MODIFY**: `aerthos/constants.py` (~20 lines added)
