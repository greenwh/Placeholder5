# Aerthos Web API - Technical Specification

**Version:** 1.0
**Last Updated:** November 2025
**Base URL:** `http://localhost:5000`

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication & Sessions](#authentication--sessions)
3. [Response Format](#response-format)
4. [Error Handling](#error-handling)
5. [Game Session API](#game-session-api)
6. [Character Roster API](#character-roster-api)
7. [Party Manager API](#party-manager-api)
8. [Scenario Library API](#scenario-library-api)
9. [Session Manager API](#session-manager-api)
10. [Data Models](#data-models)
11. [Frontend Integration](#frontend-integration)
12. [Versioning & Compatibility](#versioning--compatibility)

---

## Overview

The Aerthos Web API provides a RESTful interface to the AD&D 1e game engine. It supports:

- **Stateful game sessions** - Active games stored server-side
- **Persistent data management** - Characters, parties, scenarios, saved sessions
- **Real-time command execution** - Natural language command parsing
- **Context-aware state delivery** - Dynamic action suggestions based on game state

**Architecture:**
- **Backend:** Python Flask (stateful REST API)
- **Storage:** File-based JSON (in `~/.aerthos/`)
- **Game Engine:** Shared core modules (`aerthos/` package)
- **Session Management:** In-memory active games + persistent saves

**Technology Stack:**
- Python 3.10+
- Flask web framework
- JSON data interchange
- No external database required

---

## Authentication & Sessions

**Current Implementation:** No authentication (local development only)

**Session Management:**
- **Server-side sessions:** Active games stored in `active_games` dict keyed by `session_id`
- **Client responsibility:** Frontend must maintain and send `session_id` with each request
- **Session lifecycle:**
  - Created via `/api/new_game` or `/api/sessions/<session_id>/load`
  - Persists in memory until server restart
  - Can be checkpointed to disk via Session Manager

**Security Considerations (Production):**
- Add authentication middleware
- Use secure session tokens
- Implement CORS policies
- Add rate limiting
- Use HTTPS in production

---

## Response Format

All API responses follow this structure:

### Success Response

```json
{
  "success": true,
  "message": "Optional success message",
  "data_field": "Additional response data..."
}
```

### Error Response

```json
{
  "success": false,
  "error": "Human-readable error message"
}
```

**HTTP Status Codes:**
- `200 OK` - Success (even for errors, check `success` field)
- `500 Internal Server Error` - Unhandled exception (rare)

**Note:** Most errors return `200 OK` with `success: false`. Check the `success` field, not HTTP status.

---

## Error Handling

**Error Response Pattern:**

```json
{
  "success": false,
  "error": "Descriptive error message"
}
```

**Common Error Scenarios:**

| Error Message | Cause | Resolution |
|---------------|-------|------------|
| `"No active game"` | Invalid or expired `session_id` | Start new game or load session |
| `"Character not found"` | Invalid `character_id` | Check character exists in roster |
| `"Party not found"` | Invalid `party_id` | Check party exists in manager |
| `"Scenario not found"` | Invalid `scenario_id` | Check scenario exists in library |
| `"Session not found"` | Invalid session in Session Manager | Create new session |
| `"Race/Class not implemented"` | Invalid race/class name | Use valid options from `/api/character/get_races` or `/api/character/get_classes` |

**Server Errors:**
- Stack traces printed to server console (debug mode)
- Generic error message returned to client
- Check server logs for full traceback

---

## Game Session API

### Start New Game

**Endpoint:** `POST /api/new_game`

**Description:** Creates a demo game with 4 pre-generated characters and a standard dungeon.

**Request:**

```json
{
  "session_id": "my_game_session"  // Optional, defaults to "default"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Welcome to The Dark Tunnels!",
  "state": {
    // Full game state (see Data Models section)
  }
}
```

**Demo Party:**
- Thorin (Dwarf Fighter)
- Elara (Elf Magic-User) - includes Level 2 spells for testing
- Cedric (Human Cleric)
- Shadow (Halfling Thief)

**Use Case:** Quick testing and demo games. For persistent play, use Session Manager API.

---

### Execute Command

**Endpoint:** `POST /api/command`

**Description:** Parse and execute a game command (movement, combat, items, etc.)

**Request:**

```json
{
  "session_id": "my_game_session",
  "command": "attack orc with sword",
  "active_character": 0  // Index of active party member (0-based)
}
```

**Response:**

```json
{
  "success": true,
  "message": "Thorin strikes the orc for 8 damage!",
  "state": {
    // Updated game state
  },
  "active_character": 0
}
```

**Supported Commands:**
- **Movement:** `north`, `south`, `east`, `west`, `go [direction]`
- **Combat:** `attack [monster]`, `cast [spell]`, `cast [spell] on [target]`
- **Items:** `take [item]`, `drop [item]`, `equip [item]`, `use [item]`
- **Exploration:** `search`, `look`, `examine`, `open [object]`
- **Character:** `status`, `inventory`, `spells`, `rest`
- **Navigation:** `map`, `help`

**Parser:** Natural language parsing via `aerthos.engine.parser.CommandParser`

---

### Get Game State

**Endpoint:** `POST /api/game_state`

**Description:** Retrieve current state without executing a command.

**Request:**

```json
{
  "session_id": "my_game_session"
}
```

**Response:**

```json
{
  "success": true,
  "state": {
    // Full game state (see Data Models section)
  }
}
```

**Use Case:** Polling for updates, refreshing UI after external events.

---

## Character Roster API

### List Characters

**Endpoint:** `GET /api/characters`

**Description:** Get all characters from persistent roster.

**Response:**

```json
{
  "success": true,
  "characters": [
    {
      "id": "char_12345",
      "name": "Thorin",
      "race": "Dwarf",
      "class": "Fighter",
      "level": 1,
      "hp_current": 10,
      "hp_max": 10,
      "created": "2025-11-23T10:30:00"
    }
  ]
}
```

---

### Create Character (Quick)

**Endpoint:** `POST /api/characters`

**Description:** Quick character creation with default stats.

**Request:**

```json
{
  "name": "Thorin",
  "race": "Dwarf",
  "char_class": "Fighter"
}
```

**Response:**

```json
{
  "success": true,
  "character_id": "char_12345"
}
```

**Valid Options:**
- **Races:** `Human`, `Elf`, `Dwarf`, `Halfling`
- **Classes:** `Fighter`, `Cleric`, `Magic-User`, `Thief`

**Stat Generation:** Random 3d6 per ability (AD&D 1e method)

---

### Create Character (Full)

**Endpoint:** `POST /api/character/create`

**Description:** Create character with custom stats and alignment.

**Request:**

```json
{
  "name": "Elara",
  "race": "Elf",
  "char_class": "Magic-User",
  "alignment": "Chaotic Good",
  "stats": {
    "str": 10,
    "dex": 16,
    "con": 12,
    "int": 18,
    "wis": 14,
    "cha": 13
  }
}
```

**Response:**

```json
{
  "success": true,
  "character_id": "char_67890",
  "name": "Elara"
}
```

**Alignment Validation:** Checks class restrictions (e.g., Paladin must be Lawful Good)

---

### Get Character

**Endpoint:** `GET /api/characters/<char_id>`

**Description:** Retrieve full character details.

**Response:**

```json
{
  "success": true,
  "character": {
    "id": "char_12345",
    "name": "Thorin",
    "race": "Dwarf",
    "char_class": "Fighter",
    "alignment": "Lawful Good",
    "level": 1,
    "xp": 0,
    "hp_current": 10,
    "hp_max": 10,
    "ac": 4,
    "thac0": 20,
    "gold": 100,
    "weight": 45.5,
    "weight_max": 150
  }
}
```

---

### Delete Character

**Endpoint:** `DELETE /api/characters/<char_id>`

**Description:** Permanently delete character from roster.

**Response:**

```json
{
  "success": true
}
```

**Warning:** Deletion is permanent and cannot be undone.

---

### Get Available Races

**Endpoint:** `POST /api/character/get_races`

**Description:** Get races available based on ability scores.

**Request:**

```json
{
  "stats": {
    "str": 16,
    "dex": 14,
    "con": 15,
    "int": 12,
    "wis": 10,
    "cha": 11
  }
}
```

**Response:**

```json
{
  "success": true,
  "races": [
    {
      "name": "Human",
      "description": "Versatile and adaptable...",
      "modifiers": "None",
      "available": true,
      "reason": null
    },
    {
      "name": "Elf",
      "description": "Graceful and magical...",
      "modifiers": "+1 DEX, -1 CON",
      "available": true,
      "reason": null
    },
    {
      "name": "Half-Orc",
      "description": "Strong but brutish...",
      "modifiers": "+1 STR, +1 CON, -2 CHA",
      "available": false,
      "reason": "Requires CHA ≤ 12"
    }
  ]
}
```

**Use Case:** Frontend race selection with validation.

---

### Get Available Classes

**Endpoint:** `POST /api/character/get_classes`

**Description:** Get classes available for race and stats.

**Request:**

```json
{
  "race": "Elf",
  "stats": {
    "str": 12,
    "dex": 16,
    "con": 14,
    "int": 18,
    "wis": 13,
    "cha": 15
  }
}
```

**Response:**

```json
{
  "success": true,
  "classes": [
    {
      "name": "Fighter",
      "description": "Master of weapons...",
      "available": true,
      "reason": null
    },
    {
      "name": "Paladin",
      "description": "Holy warrior...",
      "available": false,
      "reason": "Requires STR ≥ 12, WIS ≥ 13, CHA ≥ 17"
    }
  ],
  "stats_after_race": {
    "str": 12,
    "dex": 17,
    "con": 13,
    "int": 18,
    "wis": 13,
    "cha": 15
  }
}
```

**Note:** `stats_after_race` includes racial modifiers and maximums.

---

### Get Available Alignments

**Endpoint:** `POST /api/character/get_alignments`

**Description:** Get alignments allowed for a class.

**Request:**

```json
{
  "char_class": "Paladin"
}
```

**Response:**

```json
{
  "success": true,
  "allowed_alignments": ["Lawful Good"]
}
```

**Alignment System:** AD&D 1e nine-point alignment (LG, NG, CG, LN, TN, CN, LE, NE, CE)

---

## Party Manager API

### List Parties

**Endpoint:** `GET /api/parties`

**Description:** Get all saved parties.

**Response:**

```json
{
  "success": true,
  "parties": [
    {
      "id": "party_12345",
      "name": "The Brave Adventurers",
      "character_ids": ["char_001", "char_002", "char_003"],
      "formation": ["front", "front", "back"],
      "created": "2025-11-23T10:30:00"
    }
  ]
}
```

---

### Create Party

**Endpoint:** `POST /api/parties`

**Description:** Create a new party from roster characters.

**Request:**

```json
{
  "name": "The Brave Adventurers",
  "character_ids": ["char_001", "char_002", "char_003", "char_004"],
  "formation": ["front", "front", "back", "back"]  // Optional
}
```

**Response:**

```json
{
  "success": true,
  "party_id": "party_12345"
}
```

**Formation:**
- `"front"` - Front rank (melee combat)
- `"back"` - Back rank (ranged/magic)
- **Default:** First half front, second half back
- **Party Size:** 1-6 characters

---

### Delete Party

**Endpoint:** `DELETE /api/parties/<party_id>`

**Description:** Delete a party (does not delete characters).

**Response:**

```json
{
  "success": true
}
```

---

## Scenario Library API

### List Scenarios

**Endpoint:** `GET /api/scenarios`

**Description:** Get all saved scenarios (dungeons).

**Response:**

```json
{
  "success": true,
  "scenarios": [
    {
      "id": "scenario_12345",
      "name": "The Dark Crypt",
      "description": "An ancient burial ground...",
      "difficulty": "medium",
      "num_rooms": 12,
      "created": "2025-11-23T10:30:00"
    }
  ]
}
```

---

### Create Scenario

**Endpoint:** `POST /api/scenarios`

**Description:** Generate and save a new dungeon scenario.

**Request (Preset):**

```json
{
  "dungeon_type": "3",  // "2"=Easy, "3"=Standard, "4"=Hard
  "party_level": 1,
  "name": "The Dark Tunnels",
  "description": "A mine overrun with monsters"
}
```

**Request (Custom):**

```json
{
  "dungeon_type": "5",
  "name": "The Deep Caverns",
  "description": "Multi-level cave system",
  "num_rooms": 15,
  "layout_type": "network",  // "linear", "branching", "network"
  "num_levels": 3,
  "dungeon_theme": "cave",  // "mine", "crypt", "cave", "ruins", "sewer"
  "seed": 42,  // Optional for reproducibility
  "party_aware": {
    "apl": 2,  // Average Party Level
    "party_size": 4,
    "composition": "balanced",  // "balanced", "melee", "magic", "mixed"
    "magic_level": "medium"  // "low", "medium", "high"
  }
}
```

**Response:**

```json
{
  "success": true,
  "scenario_id": "scenario_67890"
}
```

**Dungeon Types:**
- `"1"` - Fixed starter dungeon (cannot save)
- `"2"` - Easy preset (8 rooms, low danger)
- `"3"` - Standard preset (12 rooms, medium danger)
- `"4"` - Hard preset (15 rooms, high danger)
- `"5"` - Custom (configurable rooms, levels, theme)

**Multi-Level Dungeons:**
- Set `num_levels > 1` in custom scenarios
- Uses `MultiLevelGenerator` with stairs between levels
- Each level has `num_rooms` rooms

---

### Delete Scenario

**Endpoint:** `DELETE /api/scenarios/<scenario_id>`

**Description:** Delete a saved scenario.

**Response:**

```json
{
  "success": true
}
```

---

## Session Manager API

### List Sessions

**Endpoint:** `GET /api/sessions`

**Description:** Get all saved game sessions.

**Response:**

```json
{
  "success": true,
  "sessions": [
    {
      "id": "session_12345",
      "name": "Adventure in the Crypt",
      "party_id": "party_001",
      "scenario_id": "scenario_001",
      "current_room_id": "room_003",
      "last_played": "2025-11-23T15:45:00",
      "created": "2025-11-23T10:00:00"
    }
  ]
}
```

---

### Create Session

**Endpoint:** `POST /api/sessions`

**Description:** Create a new game session from party + scenario.

**Request:**

```json
{
  "party_id": "party_12345",
  "scenario_id": "scenario_67890",
  "name": "Epic Quest"
}
```

**Response:**

```json
{
  "success": true,
  "session_id": "session_99999"
}
```

**Use Case:** Persistent game saves with multiple concurrent campaigns.

---

### Create Solo Session

**Endpoint:** `POST /api/sessions/solo`

**Description:** Create a solo character session (auto-creates party).

**Request:**

```json
{
  "character_id": "char_12345",
  "scenario_id": "scenario_67890",
  "name": "Thorin's Solo Quest"  // Optional
}
```

**Response:**

```json
{
  "success": true,
  "session_id": "session_88888"
}
```

**Auto-Party:**
- Creates single-character party named "Solo: [Character Name]"
- Formation set to `["front"]`
- Session name defaults to "[Character Name] - [Scenario Name]"

---

### Load Session

**Endpoint:** `POST /api/sessions/<session_id>/load`

**Description:** Load a session for playing (creates active game).

**Response:**

```json
{
  "success": true,
  "message": "Resuming Epic Quest...",
  "state": {
    // Full game state
  },
  "web_session_id": "session_session_12345"
}
```

**Important:** Use `web_session_id` for subsequent `/api/command` calls, not the original `session_id`.

**State Restoration:**
- Loads party characters
- Loads dungeon from scenario
- Restores current room if saved
- Updates last played timestamp

---

### Delete Session

**Endpoint:** `DELETE /api/sessions/<session_id>`

**Description:** Delete a saved session.

**Response:**

```json
{
  "success": true
}
```

**Note:** Does not delete associated party or scenario.

---

## Data Models

### Game State Object

The `state` object returned by game commands:

```json
{
  "room": {
    "id": "room_001",
    "title": "Entrance Hall",
    "description": "A dusty chamber with stone walls...",
    "exits": {
      "north": "room_002",
      "east": "room_003"
    },
    "light_level": "dim",
    "items": ["Torch", "Rusty Sword"]
  },
  "party": [
    {
      "name": "Thorin",
      "class": "Fighter",
      "race": "Dwarf",
      "level": 1,
      "hp": 10,
      "hp_max": 10,
      "ac": 4,
      "thac0": 20,
      "xp": 0,
      "gold": 100,
      "is_alive": true,
      "weight": 45.5,
      "weight_max": 150,
      "formation": "front",
      "inventory": [
        {
          "name": "Longsword",
          "type": "weapon",
          "weight": 4.0
        }
      ],
      "equipped": {
        "weapon": "Longsword",
        "armor": "Chain Mail",
        "shield": "Large Shield",
        "light": "Torch"
      },
      "spell_slots": [],  // Empty for non-casters
      "spells_known": []
    }
  ],
  "in_combat": false,
  "active_monsters": [
    {
      "name": "Orc",
      "hp": 5,
      "hp_max": 8,
      "status": "wounded"
    }
  ],
  "available_spells": [
    {
      "name": "Magic Missile",
      "level": 1,
      "caster": "Elara"
    }
  ],
  "available_spells_to_memorize": [
    {
      "name": "Sleep",
      "level": 1,
      "school": "enchantment",
      "caster": "Elara"
    }
  ],
  "time": {
    "turns": 12,
    "hours": 2
  },
  "map": {
    "rooms": {
      "room_001": {
        "id": "room_001",
        "title": "Entrance Hall",
        "x": 0,
        "y": 0,
        "exits": {"north": "room_002"},
        "is_current": true,
        "is_explored": true
      },
      "room_002": {
        "id": "room_002",
        "title": "???",
        "x": 0,
        "y": -1,
        "exits": {},
        "is_current": false,
        "is_explored": false
      }
    },
    "current_room_id": "room_001"
  }
}
```

### Spell Slot Object

```json
{
  "level": 1,
  "is_used": false,
  "spell": {
    "name": "Magic Missile",
    "level": 1,
    "school": "evocation",
    "range": "60 feet",
    "description": "Fires 1 missile per 2 caster levels..."
  }
}
```

**Note:** If `spell` is `null`, the slot is empty (available for memorization).

---

## Frontend Integration

### Initialization Flow

```javascript
// 1. Start new game
const response = await fetch('/api/new_game', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({session_id: 'player_123'})
});
const {success, message, state} = await response.json();

// 2. Render initial state
renderRoom(state.room);
renderParty(state.party);
renderMap(state.map);
```

### Command Execution

```javascript
// Send command
const response = await fetch('/api/command', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    session_id: 'player_123',
    command: 'attack orc',
    active_character: 0  // Party member index
  })
});

const {success, message, state, active_character} = await response.json();

if (success) {
  // Update UI
  appendMessage(message);
  updateGameState(state);
} else {
  showError(message);
}
```

### Context-Aware UI

Use `state` fields to populate action buttons:

```javascript
// Items in room → "Take [item]" buttons
state.room.items.forEach(item => {
  addActionButton(`Take ${item}`, `take ${item}`);
});

// Active monsters → "Attack [monster]" buttons
state.active_monsters.forEach(monster => {
  addActionButton(`Attack ${monster.name}`, `attack ${monster.name}`);
});

// Available spells → "Cast [spell]" buttons
state.available_spells.forEach(spell => {
  addActionButton(`Cast ${spell.name}`, `cast ${spell.name}`);
});
```

### Session Persistence

```javascript
// Save session to Session Manager
await fetch('/api/sessions', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    party_id: 'party_12345',
    scenario_id: 'scenario_67890',
    name: 'My Adventure'
  })
});

// Later: Load session
const loadResponse = await fetch('/api/sessions/session_99999/load', {
  method: 'POST'
});
const {web_session_id, state} = await loadResponse.json();

// Use web_session_id for subsequent commands
sessionId = web_session_id;
```

---

## Versioning & Compatibility

### Current Version

**API Version:** 1.0 (November 2025)

### Breaking Change Policy

**⚠️ CRITICAL - Game State JSON Structure:**

The `get_game_state_json()` function in `web_ui/app.py` defines the contract between backend and frontend. Changes to this structure constitute **breaking changes**.

**Safe Changes:**
- ✅ Adding new fields (frontend ignores unknown fields)
- ✅ Adding new optional fields (frontend handles missing data gracefully)
- ✅ Changing field values (as long as type remains same)

**Breaking Changes:**
- ❌ Removing fields (breaks frontends expecting those fields)
- ❌ Renaming fields (breaks frontends referencing old names)
- ❌ Changing field types (e.g., string → array)

**Change Protocol:**
1. Read WARNING comment at top of `get_game_state_json()` (line 215-219)
2. Search `game.html` for all references to `state.fieldname`
3. Update ALL references before deploying
4. Run manual web UI testing (movement, combat, spells)
5. Consider API versioning for major changes

### Backward Compatibility

**Character Saves:**
- Old character saves without `alignment` field default to "True Neutral"
- All 374 tests pass with backward compatibility

**Session Data:**
- Session files include version metadata
- Loader checks version and migrates if needed

### Deprecation Process

When deprecating fields:
1. Add new field alongside old field
2. Mark old field as deprecated in documentation
3. Maintain both for 1+ releases
4. Remove old field with major version bump

---

## Appendix A: Quick Reference

### All Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| **Game Session** |
| POST | `/api/new_game` | Start demo game |
| POST | `/api/command` | Execute command |
| POST | `/api/game_state` | Get current state |
| **Character Roster** |
| GET | `/api/characters` | List characters |
| POST | `/api/characters` | Create character (quick) |
| POST | `/api/character/create` | Create character (full) |
| GET | `/api/characters/<id>` | Get character details |
| DELETE | `/api/characters/<id>` | Delete character |
| POST | `/api/character/get_races` | Get available races |
| POST | `/api/character/get_classes` | Get available classes |
| POST | `/api/character/get_alignments` | Get allowed alignments |
| **Party Manager** |
| GET | `/api/parties` | List parties |
| POST | `/api/parties` | Create party |
| DELETE | `/api/parties/<id>` | Delete party |
| **Scenario Library** |
| GET | `/api/scenarios` | List scenarios |
| POST | `/api/scenarios` | Generate scenario |
| DELETE | `/api/scenarios/<id>` | Delete scenario |
| **Session Manager** |
| GET | `/api/sessions` | List sessions |
| POST | `/api/sessions` | Create session |
| POST | `/api/sessions/solo` | Create solo session |
| POST | `/api/sessions/<id>/load` | Load session for play |
| DELETE | `/api/sessions/<id>` | Delete session |

### Valid Enumerations

**Races:** `Human`, `Elf`, `Dwarf`, `Halfling`

**Classes:** `Fighter`, `Cleric`, `Magic-User`, `Thief`

**Alignments:** `Lawful Good`, `Neutral Good`, `Chaotic Good`, `Lawful Neutral`, `True Neutral`, `Chaotic Neutral`, `Lawful Evil`, `Neutral Evil`, `Chaotic Evil`

**Layout Types:** `linear`, `branching`, `network`

**Dungeon Themes:** `mine`, `crypt`, `cave`, `ruins`, `sewer`

**Compositions:** `balanced`, `melee`, `magic`, `mixed`

**Magic Levels:** `low`, `medium`, `high`

---

## Appendix B: Testing Endpoints

### cURL Examples

**Start New Game:**
```bash
curl -X POST http://localhost:5000/api/new_game \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test_game"}'
```

**Execute Command:**
```bash
curl -X POST http://localhost:5000/api/command \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test_game", "command": "look", "active_character": 0}'
```

**Create Character:**
```bash
curl -X POST http://localhost:5000/api/characters \
  -H "Content-Type: application/json" \
  -d '{"name": "Thorin", "race": "Dwarf", "char_class": "Fighter"}'
```

**List Characters:**
```bash
curl -X GET http://localhost:5000/api/characters
```

### JavaScript Fetch Examples

See **Frontend Integration** section above.

---

## Appendix C: File System Structure

**Persistent Data Locations:**

```
~/.aerthos/
├── characters/
│   └── char_<uuid>.json          # Character roster
├── parties/
│   └── party_<uuid>.json         # Saved parties
├── scenarios/
│   └── scenario_<uuid>.json      # Saved dungeons
├── sessions/
│   └── session_<uuid>.json       # Game sessions
└── saves/
    └── quick_save.json           # Quick save (single slot)
```

**Data Format:** JSON text files (UTF-8)

---

## Support & Contact

**Documentation:**
- Player Guide: `README.md`
- Setup: `SETUP.md`
- Developer Guide: `CLAUDE.md`
- Technical Spec: `aerthos_tech_spec.md`
- Items Reference: `ITEMS_REFERENCE.md`

**Testing:**
```bash
python3 run_tests.py --no-web    # Core tests
python3 run_tests.py --web       # Flask API tests (requires Flask)
```

**Development Server:**
```bash
python web_ui/app.py
# Visit http://localhost:5000
```

---

**Last Updated:** November 23, 2025
**Document Version:** 1.0
**API Version:** 1.0
