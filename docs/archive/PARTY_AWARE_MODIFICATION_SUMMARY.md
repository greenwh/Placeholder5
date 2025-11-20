# Party-Aware Dungeon Modification Summary

## Change Requested
Modify party-aware dungeon generation to allow users to:
1. **Select an already-generated party** from saved parties list, then analyze and tailor
2. **OR answer 4 questions manually** (original plan)

## Implementation Changes

### Original Design
- Single path: Answer 4 questions
- Party auto-detection if party object passed
- Smart defaults for skipped questions

### Modified Design
- **Two-path system:**
  - **Path 1**: Select from saved parties → auto-analyze → show preview → confirm
  - **Path 2**: Answer 4 questions manually (original flow)

## User Flow Comparison

### OLD FLOW (Original Plan)
```
Generate Dungeon → 4 Questions → Config → Generate
```

### NEW FLOW (Modified)
```
Generate Dungeon → Choose Path:

  Path 1: Select Saved Party
    → List Saved Parties
    → Select Party
    → Auto-Analyze Party
    → Show Detailed Analysis
    → Show Dungeon Preview
    → Confirm/Adjust Difficulty
    → Generate

  Path 2: Manual Entry
    → 4 Questions
    → Config
    → Generate
```

## Key Features Added

### Party Selection Mode
1. **List Saved Parties** with summary:
   - Party name
   - Number of characters
   - Average level
   - Member names and classes

2. **Auto-Analysis Display**:
   - Average Party Level (APL)
   - Party composition breakdown
   - Capabilities detected:
     - Has healing (clerics)
     - Can handle traps (thieves)
     - Has AoE spells (magic-users)
   - Total HP pool
   - Magic item assessment (none/low/medium/high)

3. **Dungeon Preview**:
   - Monster pool for party level
   - Boss recommendation
   - Encounter density breakdown
   - Treasure level
   - Lethality factor

4. **Difficulty Adjustment**:
   - Easier: Reduce monster strength
   - Standard: As recommended
   - Harder: Increase monster strength and density

### Manual Entry Mode (Unchanged)
- Original 4-question system
- Smart defaults
- Skip-all option
- Party pre-fill if available

## Technical Implementation

### New Method: `_party_selection_mode()`
```python
def _party_selection_mode(self) -> Dict:
    """Let user select from saved parties"""

    # Get all saved parties from PartyManager
    saved_parties = self.party_manager.list_parties()

    # Display parties with summaries
    # Let user select
    # Load selected party
    # Analyze and return config
```

### New Method: `_analyze_and_confirm()`
```python
def _analyze_and_confirm(self, party: Party) -> Dict:
    """Analyze selected party and show recommendations"""

    # Use PartyAnalyzer to get capabilities
    analysis = analyzer.analyze_party(party)

    # Display detailed analysis
    # Generate dungeon preview using MonsterScaler
    # Get difficulty adjustment from user
    # Return analysis dict for config generation
```

### Modified Method: `conduct_interview()`
```python
def conduct_interview(self, party: Optional[Party] = None,
                      party_manager: Optional[PartyManager] = None) -> Dict:
    """Main entry point - routes to party selection or manual entry"""

    # Show mode selection (1 or 2)
    # Route to appropriate method
    # Return analysis dict
```

## Example Session

```
═══════════════════════════════════════════════════════════════
DUNGEON DIFFICULTY SETUP
═══════════════════════════════════════════════════════════════

Choose your approach:

  1. Select a saved party (I'll analyze and tailor)
  2. Answer questions manually (for custom parties)

Choose 1-2: 1

═══════════════════════════════════════════════════════════════
SAVED PARTIES
═══════════════════════════════════════════════════════════════

  1. The Fellowship (4 characters, Avg Level 2)
     - Thorin (Fighter-3)
     - Gandalf (Magic-User-2)
     - Gimli (Cleric-2)
     - Bilbo (Thief-2)

  2. Solo Warrior (1 character, Avg Level 3)
     - Conan (Fighter-3)

  3. [Back to manual entry]

Choose 1-3: 1

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
  • Magic Items: Low (2x +1 weapons, 3x potions)

═══════════════════════════════════════════════════════════════
RECOMMENDED DUNGEON
═══════════════════════════════════════════════════════════════

Based on this party, I'll create:
  • Dungeon for Level 2 party (adjusted for 4 members)
  • Monsters: Goblins, Orcs, Skeletons, Hobgoblin boss
  • Encounter density: 60% combat, 20% traps, 20% empty
  • Treasure level: Low
  • Lethality: Standard (1.0x)

Adjust difficulty?
  1. Easier - Reduce monster strength
  2. As recommended - Standard challenge
  3. Harder - Increase monster strength

Choose 1-3 or press Enter for [2-Standard]:

✓ Generating dungeon tailored for The Fellowship...
✓ Generated: The Goblin Warrens (12 rooms)
```

## Benefits

### User Experience
- **Faster setup** for players with saved parties (skip 4 questions)
- **Transparency** - see exactly what analysis detected
- **Control** - can adjust difficulty after seeing preview
- **Flexibility** - still have manual option for hypothetical parties

### Gameplay Quality
- **Better balance** - dungeons truly tailored to actual party
- **Confidence** - player sees preview before committing
- **Appropriate challenge** - difficulty adjustment prevents over/under-tuning

### Development
- **Reusable code** - PartyAnalyzer used in both paths
- **Testable** - clear separation between selection and analysis
- **Extensible** - easy to add more analysis metrics later

## Files Modified

### Primary Changes
- `FEATURE_PLAN_PARTY_AWARE_DUNGEONS.md` - Updated plan with two-path system

### Implementation Will Modify
- `aerthos/ui/dungeon_interview.py` (NEW) - Two-path interview system
- `aerthos/systems/party_analyzer.py` (NEW) - Party analysis (already planned)
- `aerthos/generator/config.py` - `from_interview()` method (already planned)
- `main.py` - Pass `party_manager` to interview (minor change)

## Testing Updates

### Additional Test Cases (5 new)
1. Party selection lists all saved parties correctly
2. Selected party loads and analyzes accurately
3. Analysis detects all capabilities (healing, traps, AoE)
4. Preview shows appropriate monsters for level
5. Difficulty adjustment modifies config correctly

### Total Test Cases
- Original plan: 10 tests
- Modified plan: 15 tests (10 original + 5 new)

## Estimated Time Impact

### Original Estimate
- Phase 1 (Interview System): 2-3 hours

### Modified Estimate
- Phase 1 (Interview System with Party Selection): 3-4 hours
  - +1 hour for party selection UI
  - +30 minutes for analysis display
  - +30 minutes for preview generation

### Total Feature Time
- Original: 6-9 hours
- Modified: 7-10 hours (+1 hour)

## Risk Assessment

### New Risks
1. **PartyManager dependency** - What if no saved parties?
   - Mitigation: Fall back to manual entry automatically

2. **Analysis complexity** - Too much information?
   - Mitigation: Keep display clean, bullet points, clear sections

3. **Preview accuracy** - Wrong monster predictions?
   - Mitigation: Use existing MonsterScaler (battle-tested)

### Risk Level
**Low** - This is primarily UI/UX enhancement, core logic unchanged

## Conclusion

This modification enhances the user experience by:
- Providing a faster path for players with saved parties
- Showing transparent analysis and preview
- Maintaining the original manual entry option
- Adding minimal complexity (+1 hour development)

The two-path system respects both use cases:
- **Path 1**: Quick, automated, transparent (saved parties)
- **Path 2**: Flexible, manual, customizable (hypothetical parties)

**Status**: Plan updated, ready for implementation
**Estimated Additional Time**: +1 hour (3-4 hours instead of 2-3 hours for Phase 1)
**Total Feature Time**: 7-10 hours (was 6-9 hours)
