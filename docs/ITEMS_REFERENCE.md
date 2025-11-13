# Aerthos Item Database Reference

## Summary
All 14 items in the database are properly configured and functional.

## Items by Type

### Weapons (5 items)
All weapons work for combat with proper damage dice vs Small/Medium and Large creatures.

| Item | Damage (S/M) | Damage (L) | Weight | Special |
|------|--------------|------------|--------|---------|
| Longsword | 1d8 | 1d12 | 4 lbs | Versatile blade |
| Shortsword | 1d6 | 1d8 | 3 lbs | Light, easy to wield |
| Dagger | 1d4 | 1d3 | 1 lbs | Easily concealed |
| Mace | 1d6 | 1d6 | 8 lbs | Blunt weapon (Clerics) |
| Staff | 1d6 | 1d6 | 4 lbs | Quarterstaff (Magic-Users) |

**Usage**: `equip <weapon>` then `attack <target>`

### Armor (4 items)
All armor provides AC bonuses (descending AC system - lower is better).

| Item | AC Bonus | Weight | Final AC | Cost |
|------|----------|--------|----------|------|
| Leather Armor | 2 | 15 lbs | AC 8 | 5 gp |
| Chain Mail | 5 | 30 lbs | AC 5 | 75 gp |
| Plate Mail | 7 | 45 lbs | AC 3 | 400 gp |
| Shield | 1 | 10 lbs | -1 AC | 10 gp |

**Usage**: `equip <armor>` (automatically applies AC bonus)

### Light Sources (2 items)
Essential for exploring dark dungeon rooms.

| Item | Burn Time | Radius | Weight |
|------|-----------|--------|--------|
| Torch | 6 turns (1 hour) | 30 ft | 1 lbs |
| Lantern | 24 turns (4 hours) | 30 ft | 3 lbs |

**Usage**: `equip torch` or `equip lantern` (lights and equips)
**Warning**: Tracks burn time! You'll get warnings at 3 and 1 turns remaining.

### Consumables (2 items)

**Rations (1 day)**
- Weight: 1 lbs
- Purpose: Required for resting
- Usage: Automatically consumed when you `rest` in a safe area
- Note: Cannot be used directly - only consumed during rest

**Potion of Healing**
- Weight: 0.5 lbs
- Effect: Heals 2d4+2 HP (4-10 HP)
- Usage: `use potion` (consumed on use)
- Valuable treasure item!

### Equipment (1 item)

**Rope (50 ft)**
- Weight: 5 lbs
- Purpose: General adventuring equipment
- Current Status: Collectible item (no specific use yet)
- Future: Could be used for climbing, tying up prisoners, etc.

## Items Found in Dungeon

Located in starter dungeon "The Abandoned Mine":

- **Room 001** (Mine Entrance): torch
- **Room 002** (Guard Post): rope_50ft
- **Room 003** (Collapsed Tunnel): rations
- **Room 004** (Storage Chamber): rations, torch, dagger
- **Room 006** (Goblin Den): longsword, shield
- **Room 008** (Burial Chamber): mace
- **Room 009** (Foreman's Office): lantern
- **Room 010** (Deep Shaft): potion_healing (in treasure)

## Testing Results

✅ All items load correctly from JSON
✅ All weapons have proper damage dice
✅ All armor has AC bonuses
✅ All light sources have burn times
✅ Potion of Healing heals correctly (tested: 2d4+2)
✅ Rations are consumed during rest
✅ All dungeon item references are valid
✅ Flexible item name matching works (e.g., "rope" finds "rope_50ft")

## Item Interaction Commands

- `take <item>` - Pick up item from room
- `drop <item>` - Drop item in current room
- `equip <item>` - Equip weapon, armor, or light source
- `use <item>` - Use consumable (potions, scrolls)
- `inventory` or `i` - View all carried items
- `status` - See equipped items and AC

## Notes for Players

1. **Light Management**: Critical! Always carry spare torches
2. **Rations**: Required for resting - pick them up!
3. **Weight**: Total encumbrance based on STR (affects movement)
4. **Equipment Slots**:
   - One weapon
   - One armor
   - One shield (optional)
   - One light source
5. **Multiple Items**: Can carry multiple of the same type (e.g., 4 torches)

## Developer Notes

All items are working as intended. The system properly:
- Creates correct item class types (Weapon, Armor, LightSource, Item)
- Preserves all properties from JSON
- Handles flexible name matching for player convenience
- Tracks item state (torch burn time, potion consumption)
- Integrates with combat, rest, and exploration systems
