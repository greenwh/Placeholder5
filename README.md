# Aerthos - AD&D 1e Text Adventure

A faithful recreation of Advanced Dungeons & Dragons 1st Edition as a single-player text adventure game.

## Features

- **Authentic AD&D 1e Mechanics**
  - THAC0 combat system with descending AC
  - Vancian magic with spell memorization
  - 5-category saving throws
  - Thief skills with percentile rolls
  - Resource management (light sources, rations)

- **Four Classic Classes**
  - Fighter - Master of combat
  - Cleric - Divine spellcaster
  - Magic-User - Arcane spellcaster
  - Thief - Cunning rogue with special skills

- **Four Races**
  - Human - Versatile and balanced
  - Elf - Graceful and magical
  - Dwarf - Tough and resilient
  - Halfling - Small and nimble

- **The Abandoned Mine**
  - Hand-crafted 10-room starter dungeon
  - Multiple enemy types (kobolds, goblins, skeletons, giant rats, ogre boss)
  - Traps, puzzles, and treasure
  - Safe rooms for resting

- **Game Systems**
  - Auto-mapping that reveals as you explore
  - Save/load system for checkpoints
  - Time tracking with resource depletion
  - Flexible natural language parser
  - Character death is permanent (restore from saves)

## Installation

Requires Python 3.10 or higher.

```bash
# Clone the repository
git clone <repository-url>
cd Placeholder5

# No additional dependencies needed - uses only Python standard library!
```

## How to Play

```bash
python main.py
```

### Basic Commands

- **Movement**: `go north`, `n`, `south`, `east`, `west`
- **Combat**: `attack orc`, `cast magic missile`
- **Items**: `take sword`, `equip longsword`, `use potion`, `drop torch`
- **Exploration**: `search`, `look`, `map`
- **Character**: `inventory`, `status`, `rest`
- **Game**: `save`, `help`, `quit`

### Tips for Survival

1. **Manage Your Light** - Torches burn out! Carry spares and watch for warnings.
2. **Rest When Safe** - Find safe rooms to restore HP and spells.
3. **Search Carefully** - Thieves can find and disarm traps; others might trigger them!
4. **Know Your Limits** - Combat is lethal. Retreat to safe rooms if wounded.
5. **Save Often** - Character death is permanent. Use save points wisely.

## The AD&D 1e Experience

This game recreates the feel of classic 1st Edition AD&D:

- **Lethal Combat** - Hit points are precious. A few bad rolls can end your adventure.
- **Resource Management** - Track light, food, and spell slots carefully.
- **Old School Challenge** - No hand-holding. Exploration and caution are rewarded.
- **Dice Control Your Fate** - Roll 3d6 in order for abilities. No re-rolls!

## Project Structure

```
aerthos/
├── engine/          # Core game systems (combat, parser, state)
├── entities/        # Character and monster classes
├── systems/         # Magic, skills, saving throws
├── world/           # Dungeon, rooms, encounters, auto-map
├── data/            # JSON data files (classes, monsters, items, spells)
├── ui/              # Display, character creation, save system
└── tests/           # Unit tests

main.py              # Game entry point
```

## Game Design

Aerthos follows these AD&D 1e principles:

- **THAC0**: Roll d20, hit if `roll >= (THAC0 - target AC)`
- **Saving Throws**: Roll d20, succeed if `roll <= save value`
- **Vancian Magic**: Memorize spells, cast once, restore on rest
- **Turn-Based Time**: 1 turn = 10 minutes, important for resource tracking
- **Side Initiative**: Whole party vs. monsters (d6 each side)

## Development Status

**Current Version**: 1.0 (MVP)

This is a pilot implementation with:
- ✅ Complete core systems
- ✅ Character creation
- ✅ Full THAC0 combat
- ✅ Vancian magic (7 spells)
- ✅ Thief skills
- ✅ 10-room starter dungeon
- ✅ Auto-mapping
- ✅ Save/load system

**Future Expansions** (if pilot is successful):
- Additional dungeons
- More monsters and spells
- Party management (multiple PCs)
- Procedural dungeon generator
- More character levels
- Additional classes (Ranger, Paladin, Druid, etc.)

## License

This is a fan project created for educational and entertainment purposes.
Dungeons & Dragons is a trademark of Wizards of the Coast.

## Credits

Designed to capture the spirit of Gary Gygax and Dave Arneson's original Advanced Dungeons & Dragons.

Built with Python 3 and lots of nostalgia for those classic dice-rolling adventures!

---

**May your hits be critical and your saves be high!**
