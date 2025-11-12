# Aerthos Setup Guide

## Requirements

- Python 3.10 or higher
- No external dependencies for CLI mode
- Flask required for Web UI mode

## Installation

### Option 1: CLI Mode Only (No Installation Needed)
The text-based CLI version uses only Python standard library:

```bash
python3 main.py
```

### Option 2: Web UI Mode (Requires Flask)

Install Flask:

```bash
pip install -r requirements.txt
```

Or install Flask directly:

```bash
pip install Flask
```

Then run the web interface:

```bash
python3 web_ui/app.py
```

Visit: http://localhost:5000

## Quick Start

### CLI Game
```bash
# Start the game
python3 main.py

# Choose option:
# 1. New Game - Create character(s) and choose dungeon
# 2. Load Game - Continue saved game
# 3. Quit

# Dungeon options:
# 1. The Abandoned Mine (fixed, recommended first time)
# 2-4. Generated dungeons (Easy/Standard/Hard)
# 5. Custom generated dungeon
```

### Web UI
```bash
# Make sure Flask is installed
pip install Flask

# Start the web server
python3 web_ui/app.py

# Open browser to http://localhost:5000
# Click "New Game" to start with demo party
```

## Features

### CLI Mode
- Full character creation
- Single character or party (4-6 characters)
- Text-based adventure
- Auto-mapping
- Save/load system

### Web UI Mode
- Gold Box style interface
- Visual party roster with HP bars
- 2D map display
- Real-time updates
- Demo party included

## Troubleshooting

**"ModuleNotFoundError: No module named 'flask'"**
```bash
pip install Flask
```

**"Python not found"**
- Make sure Python 3.10+ is installed
- Try `python` instead of `python3`

**Game won't start**
- Ensure you're in the Placeholder5 directory
- Check Python version: `python3 --version`

## Game Commands

### Movement
- `north`, `south`, `east`, `west` (or `n`, `s`, `e`, `w`)

### Combat
- `attack [monster]`
- `cast [spell]`

### Actions
- `take [item]`
- `equip [item]`
- `search`
- `rest`
- `open [chest]`

### Information
- `status` - Character sheet
- `inventory` (or `i`) - Your items
- `spells` - Available spells
- `map` (or `m`) - Auto-map
- `help` - Command list

## Enjoy!

Explore procedurally generated dungeons, find magic items, build your party, and survive the dangers of Aerthos!
