# Campaign System Implementation Plan - Aerthos

**Last Updated:** 2025-11-20
**Status:** Planning Complete - Ready for Implementation
**Estimated Total Time:** 10-15 weeks (part-time development)

---

## 📊 PROGRESS TRACKER

**Current Phase:** Not Started
**Overall Progress:** 0% (0/7 phases complete)

### Quick Status Overview

| Phase | Name | Status | Progress | Estimated Time |
|-------|------|--------|----------|----------------|
| 1 | Foundation | ⬜ Not Started | 0% | 2-3 weeks |
| 2 | Travel System | ⬜ Not Started | 0% | 2-3 weeks |
| 3 | Location Integration | ⬜ Not Started | 0% | 2 weeks |
| 4 | Faction & Reputation | ⬜ Not Started | 0% | 1-2 weeks |
| 5 | Weather & Environment | ⬜ Not Started | 0% | 1-2 weeks |
| 6 | Web UI Support | ⬜ Not Started | 0% | 1-2 weeks |
| 7 | Content Expansion | ⬜ Not Started | 0% | Ongoing |

### Current Work Session Notes

```
Date: ___________
Phase: ___________
Working On: ___________
Next Steps: ___________
Blockers: ___________
```

---

## 📋 TABLE OF CONTENTS

1. [Project Overview](#project-overview)
2. [Current State Assessment](#current-state-assessment)
3. [Architecture Design](#architecture-design)
4. [Implementation Phases](#implementation-phases)
   - [Phase 1: Foundation](#phase-1-foundation)
   - [Phase 2: Travel System](#phase-2-travel-system)
   - [Phase 3: Location Integration](#phase-3-location-integration)
   - [Phase 4: Faction & Reputation](#phase-4-faction--reputation)
   - [Phase 5: Weather & Environment](#phase-5-weather--environment)
   - [Phase 6: Web UI Support](#phase-6-web-ui-support)
   - [Phase 7: Content Expansion](#phase-7-content-expansion)
5. [Data Schemas](#data-schemas)
6. [Code Examples](#code-examples)
7. [Testing Strategy](#testing-strategy)
8. [Risk Mitigation](#risk-mitigation)
9. [Quick Reference](#quick-reference)

---

## 🎯 PROJECT OVERVIEW

### Goal
Implement a modular campaign system that extends Aerthos beyond dungeon delving to support overworld travel, multiple settlements, wilderness encounters, and campaign progression.

### Key Requirements
- ✅ Modular campaigns (data-driven, not hardcoded)
- ✅ Support future campaign imports
- ✅ Aerthos world as first campaign
- ✅ Hex-based overworld travel (1 hex = 24 miles per DMG)
- ✅ Multiple settlements (Oakhaven, Eldoria, villages)
- ✅ Wilderness encounters between locations
- ✅ Faction/reputation system
- ✅ Integration with existing village/shop/inn systems
- ✅ Non-breaking implementation (existing dungeon-only games still work)

### Design Principles
1. **Campaigns are optional** - GameState works with or without a campaign
2. **Data-driven** - All campaign content in JSON files
3. **Backwards compatible** - Existing functionality untouched
4. **DMG authentic** - Follow AD&D 1e DMG standards for travel, encounters, economics
5. **Modular** - Easy to add new campaigns later

---

## 🔍 CURRENT STATE ASSESSMENT

### ✅ What We Have (Ready to Use)

**Core Engine - 100% Complete**
- ✅ THAC0 combat system
- ✅ Vancian magic (spell slots, memorization, rest)
- ✅ 5-category saving throws
- ✅ Thief skills (percentile-based)
- ✅ Resource management (light, rations, encumbrance)
- ✅ Time tracking (turns, hours, days)
- ✅ Natural language parser
- ✅ Auto-mapping (ASCII maps)
- ✅ Character creation (4 classes, 4 races)
- ✅ 374/374 tests passing

**Dungeon Systems - 100% Complete**
- ✅ Single-level dungeons (hand-crafted)
- ✅ Multi-level dungeons with stairs
- ✅ Procedural generation (DungeonGenerator, MultiLevelGenerator)
- ✅ Monster scaling by difficulty
- ✅ Environment-based monster filtering (dungeon/wilderness/underwater)
- ✅ Trap generation and detection
- ✅ Treasure generation
- ✅ Room encounters (combat, traps, puzzles, treasure)

**Village System - Exists But Not Connected to Overworld**
- ✅ Village class with shops, inns, guilds (`aerthos/world/village.py`)
- ✅ Shop system with equipment purchases (`aerthos/world/shop.py`)
- ✅ Inn system with rest and rumors (`aerthos/world/inn.py`)
- ✅ Guild system with class-specific services (`aerthos/world/guild.py`)
- ⚠️ Villages are standalone - no overworld connection yet
- ⚠️ No travel between villages/dungeons yet

**Persistence - 5 Layers Complete**
- ✅ Quick save/load (temporary session)
- ✅ Character roster (persistent database)
- ✅ Party manager (persistent parties)
- ✅ Scenario library (saved dungeons)
- ✅ Session manager (full game state snapshots)
- ⚠️ No campaign state persistence yet

**Web UI - Functional**
- ✅ Flask REST API
- ✅ Gold Box style interface
- ✅ Visual party roster with HP bars
- ✅ 2D map display
- ✅ Keyboard shortcuts
- ✅ Context-aware action buttons
- ⚠️ No overworld map visualization yet

### ❌ What's Missing (To Be Implemented)

**Overworld Travel System**
- ❌ Hex-based world map representation
- ❌ Travel mechanics (time costs, encounter checks)
- ❌ Wilderness encounters (terrain-specific)
- ❌ Movement between locations
- ❌ Overworld auto-mapping

**Campaign Structure**
- ❌ Campaign class and loader
- ❌ Campaign metadata (name, description, starting location)
- ❌ Campaign state persistence (progress, reputation, calendar)
- ❌ Multiple settlements on map
- ❌ Location interconnection

**Faction & Reputation**
- ❌ Faction definitions
- ❌ Reputation tracking (0-100 scale per faction)
- ❌ Reputation effects on prices, rumors, quests
- ❌ Faction-specific consequences

**Environmental Systems**
- ❌ Weather generation (region-specific)
- ❌ Seasonal effects
- ❌ Travel hazards (storms, heat, cold)

**Campaign Integration**
- ❌ Parser commands for travel (travel, map, where, etc.)
- ❌ GameState campaign awareness
- ❌ Seamless transitions (overworld → village → dungeon)

---

## 🏗️ ARCHITECTURE DESIGN

### Directory Structure (New Files)

```
aerthos/
├── campaigns/                    # NEW: Campaign system modules
│   ├── __init__.py
│   ├── campaign.py              # Base Campaign class
│   ├── campaign_loader.py       # Campaign loading/validation
│   └── overworld.py             # Overworld map and travel
│
├── world/
│   ├── hex_map.py               # NEW: Hex grid representation
│   ├── travel_system.py         # NEW: Travel mechanics
│   ├── weather.py               # NEW: Weather generation
│   ├── wilderness_encounters.py # NEW: Encounter generation
│   ├── location.py              # NEW: Generic location class
│   ├── village.py               # EXISTS: Extend with hex coordinates
│   ├── dungeon.py               # EXISTS: Extend with hex coordinates
│   └── multilevel_dungeon.py    # EXISTS: Extend with hex coordinates
│
├── data/
│   └── campaigns/               # NEW: Campaign data files
│       └── aerthos_campaign/
│           ├── campaign.json          # Campaign metadata
│           ├── world_map.json         # 30x40 hex map
│           ├── locations.json         # Settlements, dungeons, POIs
│           ├── factions.json          # Political entities
│           └── encounters.json        # Wilderness encounter tables
│
└── tests/
    ├── test_hex_map.py          # NEW: Hex coordinate tests
    ├── test_travel_system.py    # NEW: Travel mechanic tests
    ├── test_campaign.py         # NEW: Campaign loading tests
    └── test_campaign_integration.py  # NEW: End-to-end campaign tests
```

### Key Classes (New)

**Campaign** (`campaigns/campaign.py`)
- Represents a complete campaign module
- Loads world map, locations, factions, encounters
- Tracks campaign progress (reputation, discovered locations, calendar)
- Provides campaign-level save/load

**HexMap** (`world/hex_map.py`)
- Hex grid representation (offset coordinates)
- Hex terrain types (plains, forest, mountains, etc.)
- Neighbor calculation (6 adjacent hexes)
- Path finding (optional, for "auto-travel")

**TravelSystem** (`world/travel_system.py`)
- Travel time calculations by terrain and pace
- Encounter checks (twice per day per DMG)
- Resource consumption during travel
- Arrival at destinations

**Location** (`world/location.py`)
- Base class for all map locations
- Types: settlement, dungeon, poi, landmark
- Hex coordinates
- Discovery state (undiscovered/discovered/visited)

**WildernessEncounterSystem** (`world/wilderness_encounters.py`)
- Generates encounters from tables by terrain
- Scales encounters to party level
- Uses existing Monster and Encounter classes

### Modified Classes

**GameState** (`engine/game_state.py`)
- Add `campaign: Optional[Campaign]` field
- Add `current_hex: Optional[Tuple[int, int]]` field
- Add `location_type: str` field ("overworld"/"village"/"dungeon")
- Add campaign state to serialize()/deserialize()

**Parser** (`engine/parser.py`)
- Add travel commands: "travel [direction]", "travel [distance]"
- Add info commands: "map", "where", "weather"
- Add location commands: "visit [location]", "enter [location]"

**Village** (`world/village.py`)
- Add `hex_coordinates: Optional[Tuple[int, int]]` field
- Extend serialize() to include coordinates

**Dungeon/MultiLevelDungeon** (`world/dungeon.py`, `world/multilevel_dungeon.py`)
- Add `hex_coordinates: Optional[Tuple[int, int]]` field
- Extend serialize() to include coordinates

### Data Flow

```
Campaign Load:
Campaign.json → Campaign class → Loads HexMap, Locations, Factions, Encounters
                                         ↓
                                    GameState.campaign = Campaign
                                         ↓
                                    GameState.current_hex = start_hex
                                         ↓
                                    GameState.location_type = "overworld"

Overworld Travel:
Player command "travel north" → Parser → TravelSystem.travel()
                                              ↓
                                    Calculate time, check encounters
                                              ↓
                                    Update current_hex, time, resources
                                              ↓
                                    Check if arrived at location
                                              ↓
                                    "You arrive at Oakhaven" or "Wilderness encounter!"

Location Entry:
Player command "enter oakhaven" → Parser → Campaign.get_location("oakhaven")
                                              ↓
                                    Load Village from locations.json
                                              ↓
                                    GameState.location_type = "village"
                                              ↓
                                    GameState.current_village = Village
                                              ↓
                                    "You enter Oakhaven. What do you do?"

Dungeon Entry (from overworld):
Player command "enter kaldor" → Parser → Campaign.get_location("kaldor")
                                              ↓
                                    Load Dungeon from scenarios
                                              ↓
                                    GameState.location_type = "dungeon"
                                              ↓
                                    GameState.current_dungeon = Dungeon
                                              ↓
                                    Start dungeon gameplay

Exit to Overworld:
Player command "leave" (from village/dungeon) → Parser → GameState.location_type = "overworld"
                                                               ↓
                                                    GameState.current_hex = location.hex_coordinates
                                                               ↓
                                                    "You return to the wilderness"
```

---

## 🚀 IMPLEMENTATION PHASES

---

## PHASE 1: FOUNDATION (2-3 weeks)

**Goal:** Create campaign architecture and hex map system

### ✅ Phase 1 Checklist

**Week 1: Campaign Architecture**
- [ ] Create `campaigns/` directory and __init__.py
- [ ] Implement `Campaign` class (campaigns/campaign.py)
- [ ] Implement `CampaignLoader` class (campaigns/campaign_loader.py)
- [ ] Create `data/campaigns/aerthos_campaign/` directory
- [ ] Write campaign.json schema and example
- [ ] Write unit tests for Campaign class
- [ ] Run tests: `python3 run_tests.py --no-web`

**Week 2: Hex Map System**
- [ ] Implement `HexMap` class (world/hex_map.py)
- [ ] Implement offset coordinate system
- [ ] Implement neighbor calculation (6 adjacent hexes)
- [ ] Implement terrain types (plains, forest, mountains, etc.)
- [ ] Write world_map.json schema and example (30x40 Aerthos map)
- [ ] Write unit tests for HexMap class
- [ ] Run tests: `python3 run_tests.py --no-web`

**Week 3: Integration**
- [ ] Add `campaign: Optional[Campaign]` to GameState
- [ ] Add `current_hex: Optional[Tuple[int, int]]` to GameState
- [ ] Add campaign serialization to GameState.serialize()
- [ ] Add campaign deserialization to GameState.deserialize()
- [ ] Test campaign loading in main.py
- [ ] Run full test suite: `python3 run_tests.py --no-web`
- [ ] Verify all 374 existing tests still pass (regression check)

### 📝 Phase 1 Deliverables

1. **campaigns/campaign.py** - Campaign class implementation
2. **campaigns/campaign_loader.py** - Campaign loading/validation
3. **world/hex_map.py** - Hex grid representation
4. **data/campaigns/aerthos_campaign/campaign.json** - Campaign metadata
5. **data/campaigns/aerthos_campaign/world_map.json** - 30x40 hex map
6. **tests/test_campaign.py** - Unit tests for Campaign
7. **tests/test_hex_map.py** - Unit tests for HexMap

### 🧪 Phase 1 Testing

```bash
# Unit tests
python3 -m unittest tests.test_campaign -v
python3 -m unittest tests.test_hex_map -v

# Regression tests (ensure existing functionality untouched)
python3 run_tests.py --no-web

# Manual test: Load campaign
python3 main.py
# Choose option to load campaign (will be added to menu)
# Verify campaign loads without errors
```

### 📖 Phase 1 Code Examples

See [Code Examples - Phase 1](#code-examples---phase-1) section below for full implementations.

---

## PHASE 2: TRAVEL SYSTEM (2-3 weeks)

**Goal:** Implement overworld travel mechanics and wilderness encounters

### ✅ Phase 2 Checklist

**Week 1: Travel Mechanics**
- [ ] Implement `TravelSystem` class (world/travel_system.py)
- [ ] Implement travel time calculations (by terrain and pace)
- [ ] Implement encounter checks (2 per day per DMG)
- [ ] Implement resource consumption (rations, light)
- [ ] Add travel commands to Parser ("travel north", "travel 3 hexes north")
- [ ] Write unit tests for TravelSystem
- [ ] Run tests: `python3 run_tests.py --no-web`

**Week 2: Wilderness Encounters**
- [ ] Implement `WildernessEncounterSystem` class (world/wilderness_encounters.py)
- [ ] Implement encounter table loading from JSON
- [ ] Implement terrain-specific encounter generation
- [ ] Implement party-level scaling
- [ ] Write encounters.json schema and Aerthos encounter tables
- [ ] Write unit tests for WildernessEncounterSystem
- [ ] Run tests: `python3 run_tests.py --no-web`

**Week 3: Integration**
- [ ] Add `location_type` field to GameState ("overworld"/"village"/"dungeon")
- [ ] Integrate TravelSystem with GameState
- [ ] Integrate WildernessEncounterSystem with TravelSystem
- [ ] Add travel UI display (distance traveled, time passed, encounters)
- [ ] Test overworld travel loop (move, encounter, move, encounter)
- [ ] Run full test suite: `python3 run_tests.py --no-web`
- [ ] Verify all existing tests still pass

### 📝 Phase 2 Deliverables

1. **world/travel_system.py** - Travel mechanics implementation
2. **world/wilderness_encounters.py** - Encounter generation
3. **data/campaigns/aerthos_campaign/encounters.json** - Encounter tables
4. **tests/test_travel_system.py** - Unit tests for TravelSystem
5. **tests/test_wilderness_encounters.py** - Unit tests for WildernessEncounterSystem

### 🧪 Phase 2 Testing

```bash
# Unit tests
python3 -m unittest tests.test_travel_system -v
python3 -m unittest tests.test_wilderness_encounters -v

# Regression tests
python3 run_tests.py --no-web

# Manual test: Travel and encounters
python3 main.py
# Start campaign
# Use "travel north" command
# Verify time passes, resources consumed
# Verify wilderness encounters trigger
# Verify combat works in wilderness
```

### 📖 Phase 2 Code Examples

See [Code Examples - Phase 2](#code-examples---phase-2) section below for full implementations.

---

## PHASE 3: LOCATION INTEGRATION (2 weeks)

**Goal:** Connect villages, dungeons, and POIs to overworld map

### ✅ Phase 3 Checklist

**Week 1: Location System**
- [ ] Implement `Location` base class (world/location.py)
- [ ] Add `hex_coordinates` field to Village class
- [ ] Add `hex_coordinates` field to Dungeon class
- [ ] Add `hex_coordinates` field to MultiLevelDungeon class
- [ ] Implement location discovery system
- [ ] Write locations.json schema and Aerthos locations
- [ ] Write unit tests for Location class
- [ ] Run tests: `python3 run_tests.py --no-web`

**Week 2: Transitions**
- [ ] Add location entry/exit commands to Parser ("enter oakhaven", "leave")
- [ ] Implement GameState location transitions (overworld ↔ village ↔ dungeon)
- [ ] Add location-aware command filtering (travel only in overworld, shop only in village)
- [ ] Add "where" command (shows current location)
- [ ] Test seamless transitions (overworld → village → overworld → dungeon → overworld)
- [ ] Run full test suite: `python3 run_tests.py --no-web`
- [ ] Write integration tests: `tests/test_campaign_integration.py`

### 📝 Phase 3 Deliverables

1. **world/location.py** - Location base class
2. **data/campaigns/aerthos_campaign/locations.json** - Oakhaven, Eldoria, dungeons, POIs
3. **tests/test_location.py** - Unit tests for Location
4. **tests/test_campaign_integration.py** - Integration tests for transitions

### 🧪 Phase 3 Testing

```bash
# Unit tests
python3 -m unittest tests.test_location -v

# Integration tests
python3 -m unittest tests.test_campaign_integration -v

# Regression tests
python3 run_tests.py --no-web

# Manual test: Location transitions
python3 main.py
# Start campaign at Oakhaven
# Use "leave" to go to overworld
# Use "travel north" to move on map
# Use "enter eldoria" to enter city
# Use "shop" to buy items
# Use "leave" to return to overworld
# Verify seamless transitions, no errors
```

### 📖 Phase 3 Code Examples

See [Code Examples - Phase 3](#code-examples---phase-3) section below for full implementations.

---

## PHASE 4: FACTION & REPUTATION (1-2 weeks)

**Goal:** Implement faction system with reputation tracking

### ✅ Phase 4 Checklist

**Week 1: Faction System**
- [ ] Implement `Faction` class (campaigns/faction.py)
- [ ] Implement reputation tracking (0-100 scale per faction)
- [ ] Add reputation effects on shop prices
- [ ] Add reputation effects on inn rumors
- [ ] Write factions.json schema and Aerthos factions
- [ ] Write unit tests for Faction class
- [ ] Run tests: `python3 run_tests.py --no-web`

**Week 2: Integration & Consequences**
- [ ] Add faction reputation to Campaign class
- [ ] Add reputation change events (quest completion, crimes, donations)
- [ ] Add faction-specific dialogue variations
- [ ] Add "reputation" command (shows standing with all factions)
- [ ] Test reputation effects (price changes, rumors, access)
- [ ] Run full test suite: `python3 run_tests.py --no-web`

### 📝 Phase 4 Deliverables

1. **campaigns/faction.py** - Faction class
2. **data/campaigns/aerthos_campaign/factions.json** - Faction definitions
3. **tests/test_faction.py** - Unit tests for Faction

### 🧪 Phase 4 Testing

```bash
# Unit tests
python3 -m unittest tests.test_faction -v

# Regression tests
python3 run_tests.py --no-web

# Manual test: Reputation effects
python3 main.py
# Start campaign
# Check initial reputation: "reputation"
# Complete a quest or donate to temple
# Check reputation again
# Visit shop, verify prices changed
# Visit inn, verify new rumors available
```

---

## PHASE 5: WEATHER & ENVIRONMENT (1-2 weeks)

**Goal:** Add weather generation and environmental effects

### ✅ Phase 5 Checklist

**Week 1: Weather System**
- [ ] Implement `Weather` class (world/weather.py)
- [ ] Implement weather generation by region (Aerthos regions)
- [ ] Implement seasonal effects (spring/summer/fall/winter)
- [ ] Implement weather effects on travel (slow in rain, blocked in blizzard)
- [ ] Add "weather" command (shows current weather)
- [ ] Write unit tests for Weather class
- [ ] Run tests: `python3 run_tests.py --no-web`

**Week 2: Environmental Hazards**
- [ ] Implement travel hazards (storms, heat, cold)
- [ ] Implement saving throws vs environmental damage
- [ ] Add weather descriptions to room/travel text
- [ ] Test weather effects on gameplay
- [ ] Run full test suite: `python3 run_tests.py --no-web`

### 📝 Phase 5 Deliverables

1. **world/weather.py** - Weather system
2. **tests/test_weather.py** - Unit tests for Weather

### 🧪 Phase 5 Testing

```bash
# Unit tests
python3 -m unittest tests.test_weather -v

# Regression tests
python3 run_tests.py --no-web

# Manual test: Weather effects
python3 main.py
# Start campaign
# Check weather: "weather"
# Travel during storm, verify slower movement
# Travel in extreme weather, verify saving throws
```

---

## PHASE 6: WEB UI SUPPORT (1-2 weeks)

**Goal:** Add overworld visualization to web UI

### ✅ Phase 6 Checklist

**Week 1: API Enhancements**
- [ ] Add `/api/campaign/map` endpoint (returns hex map data)
- [ ] Add `/api/campaign/locations` endpoint (returns location list)
- [ ] Add `/api/campaign/travel` endpoint (processes travel commands)
- [ ] Update `/api/state` to include campaign data
- [ ] Test API endpoints manually (curl or browser)

**Week 2: Frontend UI**
- [ ] Add overworld map visualization (SVG hex grid)
- [ ] Add location markers on map (settlements, dungeons)
- [ ] Add player position marker
- [ ] Add travel UI (click hexes to travel or use travel buttons)
- [ ] Add faction reputation display
- [ ] Add weather display
- [ ] Test web UI manually (play full campaign loop)

### 📝 Phase 6 Deliverables

1. **web_ui/app.py** - API endpoint updates
2. **web_ui/templates/campaign_map.html** - Overworld map UI
3. **web_ui/static/campaign.js** - Campaign JavaScript
4. **web_ui/static/campaign.css** - Campaign styling

### 🧪 Phase 6 Testing

```bash
# Start web UI
python web_ui/app.py

# Open browser: http://localhost:5000

# Manual test checklist:
# [ ] Campaign map displays correctly
# [ ] Locations visible on map
# [ ] Player position marker shows
# [ ] Click hex to travel works
# [ ] Location entry/exit works
# [ ] Reputation display works
# [ ] Weather display works
# [ ] All existing web UI features still work
```

---

## PHASE 7: CONTENT EXPANSION (Ongoing)

**Goal:** Fill out Aerthos world with complete content

### ✅ Phase 7 Checklist

**Locations (Settlements)**
- [ ] Oakhaven - Complete JSON (shops, inns, guilds, NPCs)
- [ ] Eldoria - Complete JSON (shops, inns, guilds, NPCs)
- [ ] Ironfast - Dwarf settlement
- [ ] Silvan village - Elf settlement
- [ ] Grey Warden outpost
- [ ] Ruined settlements (exploration/looting)

**Locations (Dungeons)**
- [ ] Ruined Keep of Kaldor (starter dungeon, already exists)
- [ ] Kobold Warrens (multi-level)
- [ ] Orc Fortress (Scarred Wastes)
- [ ] Lizardfolk Temple (Whispering Marshes)
- [ ] Sahuagin Caves (Sunken Coast)
- [ ] Ancient Ruins (Verdant Heartlands)
- [ ] Cult of Serpent Eye hideout

**Locations (Points of Interest)**
- [ ] Shrines and temples
- [ ] Landmarks (statues, monuments)
- [ ] Ruins (exploration, lore)
- [ ] Natural wonders (waterfalls, hot springs)

**Factions (Complete Descriptions)**
- [ ] Free Cities (Eldoria, Oakhaven)
- [ ] Silvan Concordance (elves)
- [ ] Ironfast Dwarves
- [ ] Cult of the Serpent Eye
- [ ] Grey Wardens
- [ ] Orc tribes (Scarred Wastes)
- [ ] Lizardfolk tribes (Whispering Marshes)

**Encounters (Complete Tables)**
- [ ] Verdant Heartlands encounter table
- [ ] Whispering Marshes encounter table
- [ ] Shattered Peaks encounter table
- [ ] Scarred Wastes encounter table
- [ ] Sunken Coast encounter table

**Quests (Future Expansion)**
- [ ] Main questline (Cult of Serpent Eye threat)
- [ ] Side quests (faction-specific)
- [ ] Random quests (from inn rumors)

### 📝 Phase 7 Ongoing Tasks

This phase doesn't have a fixed end date. Content can be added incrementally over time. Priority:

1. **High Priority**: Oakhaven and Eldoria (starting areas)
2. **Medium Priority**: Starter dungeons (Kaldor, Kobold Warrens)
3. **Low Priority**: Distant locations, advanced dungeons

---

## 📊 DATA SCHEMAS

### campaign.json

```json
{
  "id": "aerthos",
  "name": "Aerthos: The Sundered Realm",
  "description": "A world scarred by ancient wars, where the Cult of the Serpent Eye rises.",
  "version": "1.0.0",
  "author": "Aerthos Campaign Team",

  "starting_location": {
    "type": "settlement",
    "id": "oakhaven",
    "hex": [15, 20]
  },

  "world_map_file": "world_map.json",
  "locations_file": "locations.json",
  "factions_file": "factions.json",
  "encounters_file": "encounters.json",

  "calendar": {
    "year": 1473,
    "month": 3,
    "day": 15,
    "season": "spring"
  },

  "regions": [
    {
      "id": "verdant_heartlands",
      "name": "Verdant Heartlands",
      "description": "Civilized plains and forests with farms and villages.",
      "climate": "temperate",
      "dominant_terrain": "plains"
    },
    {
      "id": "whispering_marshes",
      "name": "Whispering Marshes",
      "description": "Fog-shrouded wetlands, disease and lizardfolk.",
      "climate": "tropical",
      "dominant_terrain": "marsh"
    },
    {
      "id": "shattered_peaks",
      "name": "Shattered Peaks",
      "description": "Storm-wracked mountains, nearly impassable.",
      "climate": "alpine",
      "dominant_terrain": "mountains"
    },
    {
      "id": "scarred_wastes",
      "name": "Scarred Wastes",
      "description": "Volcanic ashlands, orc tribes, blighted terrain.",
      "climate": "arid",
      "dominant_terrain": "volcanic"
    },
    {
      "id": "sunken_coast",
      "name": "Sunken Coast",
      "description": "Treacherous archipelago, sahuagin raids.",
      "climate": "coastal",
      "dominant_terrain": "coast"
    }
  ],

  "campaign_flags": {
    "cult_discovered": false,
    "kaldor_cleared": false,
    "eldoria_unlocked": false
  }
}
```

### world_map.json

```json
{
  "width": 30,
  "height": 40,
  "hex_size": 24,
  "coordinate_system": "offset",

  "hexes": [
    {
      "q": 15,
      "r": 20,
      "terrain": "plains",
      "region": "verdant_heartlands",
      "features": ["settlement:oakhaven"],
      "travel_cost": 1.0,
      "description": "Rolling plains with a fortified border town."
    },
    {
      "q": 16,
      "r": 20,
      "terrain": "forest",
      "region": "verdant_heartlands",
      "features": [],
      "travel_cost": 1.5,
      "description": "Dense oak forest, well-traveled roads."
    },
    {
      "q": 14,
      "r": 21,
      "terrain": "hills",
      "region": "verdant_heartlands",
      "features": ["dungeon:kaldor"],
      "travel_cost": 2.0,
      "description": "Rocky hills with ruins of an ancient keep."
    }
  ]
}
```

**Note:** Full 30x40 map (1200 hexes) will be generated from Aerthos hex map document.

### locations.json

```json
{
  "locations": [
    {
      "id": "oakhaven",
      "type": "settlement",
      "name": "Oakhaven",
      "hex": [15, 20],
      "region": "verdant_heartlands",
      "description": "A rough, fortified border town where adventurers gather.",
      "population": 800,
      "government": "Syndic governance",
      "discovery_state": "discovered",

      "village_data": {
        "shops": ["silas_shop", "blacksmith", "general_store"],
        "inns": ["dirty_mug"],
        "guilds": ["fighters_guild", "thieves_guild"],
        "temple": "temple_of_light"
      },

      "faction_affiliations": {
        "free_cities": 100,
        "grey_wardens": 70
      },

      "rumors": [
        "Goblins have taken over the Ruined Keep of Kaldor to the west.",
        "The road to Eldoria has been safer lately, fewer bandits.",
        "Strange cultists have been seen in the Whispering Marshes."
      ]
    },

    {
      "id": "eldoria",
      "type": "settlement",
      "name": "Eldoria",
      "hex": [25, 18],
      "region": "verdant_heartlands",
      "description": "The Free City, a wealthy trade hub ruled by merchant syndicates.",
      "population": 12000,
      "government": "Syndicracy (geriatocracy)",
      "discovery_state": "undiscovered",

      "village_data": {
        "shops": ["cloth_syndic_shop", "grain_syndic_shop", "iron_syndic_shop"],
        "inns": ["golden_lion", "river_view"],
        "guilds": ["mages_guild", "merchants_guild", "artisans_guild"],
        "temple": "grand_cathedral"
      },

      "faction_affiliations": {
        "free_cities": 100,
        "silvan_concordance": 50
      },

      "unlock_condition": {
        "type": "reputation",
        "faction": "free_cities",
        "min_reputation": 30
      }
    },

    {
      "id": "kaldor",
      "type": "dungeon",
      "name": "Ruined Keep of Kaldor",
      "hex": [14, 21],
      "region": "verdant_heartlands",
      "description": "An ancient keep overrun by goblins and worse things.",
      "discovery_state": "discovered",

      "dungeon_data": {
        "scenario_file": "starter_dungeon.json",
        "recommended_level": 1,
        "size": "small",
        "type": "ruins"
      },

      "entrance_description": "The keep's gate hangs open, revealing darkness within."
    },

    {
      "id": "ancient_shrine",
      "type": "poi",
      "name": "Shrine of the Old Gods",
      "hex": [18, 22],
      "region": "verdant_heartlands",
      "description": "A weathered stone shrine in a forest clearing.",
      "discovery_state": "undiscovered",

      "poi_data": {
        "type": "shrine",
        "deity": "old_gods",
        "effect": "restore_hp_and_spells",
        "use_limit": "once_per_day"
      }
    }
  ]
}
```

### factions.json

```json
{
  "factions": [
    {
      "id": "free_cities",
      "name": "Free Cities",
      "description": "Merchant-ruled city-states that value trade and profit.",
      "alignment": "LN",
      "headquarters": "eldoria",
      "leader": "The Three Syndics (Cloth, Grain, Iron)",

      "reputation_tiers": [
        {"min": 0, "max": 20, "title": "Outsider", "effect": "Normal prices, basic access"},
        {"min": 21, "max": 40, "title": "Known Traveler", "effect": "5% discount, travel permits"},
        {"min": 41, "max": 60, "title": "Friend of the Cities", "effect": "10% discount, Eldoria access"},
        {"min": 61, "max": 80, "title": "Honored Ally", "effect": "15% discount, faction quests"},
        {"min": 81, "max": 100, "title": "Champion of Commerce", "effect": "20% discount, VIP access"}
      ],

      "relations": {
        "silvan_concordance": 50,
        "ironfast_dwarves": 70,
        "grey_wardens": 60,
        "cult_of_serpent_eye": 0,
        "orc_tribes": 10
      }
    },

    {
      "id": "cult_of_serpent_eye",
      "name": "Cult of the Serpent Eye",
      "description": "A chaotic evil cult seeking to awaken an ancient serpent god.",
      "alignment": "CE",
      "headquarters": "hidden_temple",
      "leader": "The Scaled Prophet",

      "reputation_tiers": [
        {"min": 0, "max": 20, "title": "Enemy", "effect": "Attacked on sight"},
        {"min": 21, "max": 100, "title": "Hostile", "effect": "Not implemented (players should not ally with CE cult)"}
      ],

      "relations": {
        "free_cities": 0,
        "silvan_concordance": 0,
        "ironfast_dwarves": 0,
        "grey_wardens": 0,
        "orc_tribes": 30,
        "lizardfolk_tribes": 50
      }
    }
  ]
}
```

### encounters.json

```json
{
  "encounter_tables": [
    {
      "region": "verdant_heartlands",
      "terrain": "plains",
      "encounters": [
        {"roll": [1, 10], "type": "monster", "id": "bandit_group", "count": "1d6"},
        {"roll": [11, 20], "type": "monster", "id": "wolf_pack", "count": "2d4"},
        {"roll": [21, 30], "type": "monster", "id": "goblin_patrol", "count": "1d8"},
        {"roll": [31, 50], "type": "npc", "id": "traveling_merchant", "count": 1},
        {"roll": [51, 70], "type": "npc", "id": "farmer_refugees", "count": "1d4"},
        {"roll": [71, 85], "type": "none", "description": "Peaceful travel, no encounter"},
        {"roll": [86, 95], "type": "event", "id": "abandoned_camp"},
        {"roll": [96, 100], "type": "treasure", "id": "hidden_cache"}
      ]
    },

    {
      "region": "whispering_marshes",
      "terrain": "marsh",
      "encounters": [
        {"roll": [1, 20], "type": "monster", "id": "lizardfolk_warriors", "count": "2d4"},
        {"roll": [21, 35], "type": "monster", "id": "giant_crocodile", "count": 1},
        {"roll": [36, 50], "type": "monster", "id": "stirge_swarm", "count": "3d6"},
        {"roll": [51, 65], "type": "hazard", "id": "quicksand"},
        {"roll": [66, 80], "type": "hazard", "id": "disease_cloud"},
        {"roll": [81, 90], "type": "none", "description": "Misty travel, no encounter"},
        {"roll": [91, 95], "type": "event", "id": "lizardfolk_totem"},
        {"roll": [96, 100], "type": "treasure", "id": "sunken_chest"}
      ]
    },

    {
      "region": "scarred_wastes",
      "terrain": "volcanic",
      "encounters": [
        {"roll": [1, 30], "type": "monster", "id": "orc_warband", "count": "2d6"},
        {"roll": [31, 50], "type": "monster", "id": "fire_beetle_swarm", "count": "3d4"},
        {"roll": [51, 65], "type": "monster", "id": "ash_zombie", "count": "1d8"},
        {"roll": [66, 80], "type": "hazard", "id": "lava_flow"},
        {"roll": [81, 90], "type": "hazard", "id": "toxic_fumes"},
        {"roll": [91, 95], "type": "event", "id": "orc_battle_aftermath"},
        {"roll": [96, 100], "type": "treasure", "id": "volcanic_gems"}
      ]
    }
  ],

  "encounter_frequency": {
    "per_day_checks": 2,
    "check_times": ["morning", "evening"],
    "base_chance": 0.33
  }
}
```

---

## 💻 CODE EXAMPLES

### Code Examples - Phase 1

#### campaigns/campaign.py

```python
"""
Campaign Module - Represents a complete campaign
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import json
from pathlib import Path


@dataclass
class CampaignMetadata:
    """Campaign metadata"""
    id: str
    name: str
    description: str
    version: str
    author: str
    starting_location_type: str
    starting_location_id: str
    starting_hex: Tuple[int, int]


class Campaign:
    """
    Represents a complete campaign module

    Campaigns are data-driven modules loaded from JSON files.
    They contain:
    - World map (hex grid)
    - Locations (settlements, dungeons, POIs)
    - Factions (political entities)
    - Encounters (wilderness tables)
    - Campaign state (progress, reputation, calendar)
    """

    def __init__(self, campaign_dir: Path):
        """
        Initialize campaign from directory

        Args:
            campaign_dir: Path to campaign directory (e.g., data/campaigns/aerthos_campaign/)
        """
        self.campaign_dir = campaign_dir
        self.metadata: Optional[CampaignMetadata] = None
        self.world_map = None  # HexMap instance (Phase 1)
        self.locations: Dict[str, dict] = {}  # Location data (Phase 3)
        self.factions: Dict[str, dict] = {}  # Faction data (Phase 4)
        self.encounter_tables: Dict[str, dict] = {}  # Encounter data (Phase 2)

        # Campaign state (mutable during gameplay)
        self.current_date: Dict[str, int] = {}  # {year, month, day, season}
        self.faction_reputation: Dict[str, int] = {}  # faction_id -> reputation (0-100)
        self.discovered_locations: List[str] = []  # location_ids
        self.campaign_flags: Dict[str, bool] = {}  # story flags

        # Load campaign data
        self._load_campaign()

    def _load_campaign(self):
        """Load campaign data from JSON files"""
        # Load campaign.json (metadata)
        campaign_file = self.campaign_dir / "campaign.json"
        with open(campaign_file, 'r') as f:
            data = json.load(f)

        self.metadata = CampaignMetadata(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            version=data['version'],
            author=data['author'],
            starting_location_type=data['starting_location']['type'],
            starting_location_id=data['starting_location']['id'],
            starting_hex=tuple(data['starting_location']['hex'])
        )

        # Initialize campaign state
        self.current_date = data['calendar'].copy()
        self.campaign_flags = data['campaign_flags'].copy()

        # Load world map (Phase 1)
        world_map_file = self.campaign_dir / data['world_map_file']
        from aerthos.world.hex_map import HexMap
        self.world_map = HexMap.load_from_file(world_map_file)

        # Load locations (Phase 3 - stub for now)
        locations_file = self.campaign_dir / data['locations_file']
        if locations_file.exists():
            with open(locations_file, 'r') as f:
                locations_data = json.load(f)
                for loc in locations_data['locations']:
                    self.locations[loc['id']] = loc

        # Load factions (Phase 4 - stub for now)
        factions_file = self.campaign_dir / data['factions_file']
        if factions_file.exists():
            with open(factions_file, 'r') as f:
                factions_data = json.load(f)
                for faction in factions_data['factions']:
                    self.factions[faction['id']] = faction
                    self.faction_reputation[faction['id']] = 50  # Neutral start

        # Load encounters (Phase 2 - stub for now)
        encounters_file = self.campaign_dir / data['encounters_file']
        if encounters_file.exists():
            with open(encounters_file, 'r') as f:
                encounters_data = json.load(f)
                for table in encounters_data['encounter_tables']:
                    key = f"{table['region']}_{table['terrain']}"
                    self.encounter_tables[key] = table

    def get_location(self, location_id: str) -> Optional[dict]:
        """Get location data by ID"""
        return self.locations.get(location_id)

    def get_locations_at_hex(self, hex_coords: Tuple[int, int]) -> List[dict]:
        """Get all locations at a hex coordinate"""
        return [
            loc for loc in self.locations.values()
            if tuple(loc['hex']) == hex_coords
        ]

    def get_faction(self, faction_id: str) -> Optional[dict]:
        """Get faction data by ID"""
        return self.factions.get(faction_id)

    def get_reputation(self, faction_id: str) -> int:
        """Get current reputation with faction (0-100)"""
        return self.faction_reputation.get(faction_id, 50)

    def modify_reputation(self, faction_id: str, delta: int):
        """
        Modify reputation with faction

        Args:
            faction_id: Faction ID
            delta: Change in reputation (+/-)
        """
        if faction_id not in self.faction_reputation:
            self.faction_reputation[faction_id] = 50

        new_rep = self.faction_reputation[faction_id] + delta
        self.faction_reputation[faction_id] = max(0, min(100, new_rep))

    def discover_location(self, location_id: str):
        """Mark location as discovered"""
        if location_id not in self.discovered_locations:
            self.discovered_locations.append(location_id)

    def is_location_discovered(self, location_id: str) -> bool:
        """Check if location has been discovered"""
        return location_id in self.discovered_locations

    def set_flag(self, flag_name: str, value: bool):
        """Set campaign flag"""
        self.campaign_flags[flag_name] = value

    def get_flag(self, flag_name: str) -> bool:
        """Get campaign flag value"""
        return self.campaign_flags.get(flag_name, False)

    def advance_time(self, hours: int):
        """
        Advance campaign time

        Args:
            hours: Hours to advance
        """
        # Simple time advancement (can be enhanced with calendar logic)
        days = hours // 24
        if days > 0:
            self.current_date['day'] += days
            # Handle month/year rollover (simplified)
            while self.current_date['day'] > 30:
                self.current_date['day'] -= 30
                self.current_date['month'] += 1
                if self.current_date['month'] > 12:
                    self.current_date['month'] = 1
                    self.current_date['year'] += 1

    def serialize(self) -> Dict:
        """
        Serialize campaign state for saving

        Returns:
            Dictionary with campaign state
        """
        return {
            'campaign_id': self.metadata.id,
            'campaign_dir': str(self.campaign_dir),
            'current_date': self.current_date.copy(),
            'faction_reputation': self.faction_reputation.copy(),
            'discovered_locations': self.discovered_locations.copy(),
            'campaign_flags': self.campaign_flags.copy()
        }

    @classmethod
    def deserialize(cls, data: Dict) -> 'Campaign':
        """
        Deserialize campaign from saved state

        Args:
            data: Dictionary from serialize()

        Returns:
            Campaign instance
        """
        campaign_dir = Path(data['campaign_dir'])
        campaign = cls(campaign_dir)

        # Restore mutable state
        campaign.current_date = data['current_date']
        campaign.faction_reputation = data['faction_reputation']
        campaign.discovered_locations = data['discovered_locations']
        campaign.campaign_flags = data['campaign_flags']

        return campaign
```

#### world/hex_map.py

```python
"""
Hex Map Module - Hex grid representation for overworld travel
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class Hex:
    """A single hex on the map"""
    q: int  # Column (offset coordinate)
    r: int  # Row (offset coordinate)
    terrain: str  # plains, forest, mountains, etc.
    region: str  # verdant_heartlands, whispering_marshes, etc.
    features: List[str]  # ["settlement:oakhaven", "dungeon:kaldor"]
    travel_cost: float  # Movement cost multiplier (1.0 = normal, 2.0 = slow)
    description: str  # Flavor text

    def __post_init__(self):
        if self.features is None:
            self.features = []

    def has_feature(self, feature_type: str) -> bool:
        """Check if hex has a feature type (e.g., 'settlement', 'dungeon')"""
        return any(f.startswith(feature_type) for f in self.features)

    def get_feature_id(self, feature_type: str) -> Optional[str]:
        """Get feature ID for a type (e.g., 'oakhaven' from 'settlement:oakhaven')"""
        for feature in self.features:
            if feature.startswith(f"{feature_type}:"):
                return feature.split(':')[1]
        return None


class HexMap:
    """
    Hex-based world map using offset coordinates

    Coordinate System:
    - q = column (x-axis)
    - r = row (y-axis)
    - Offset coordinates (odd-r layout)
    - 1 hex = 24 miles (AD&D 1e DMG standard)
    """

    def __init__(self, width: int, height: int, hex_size: int = 24):
        """
        Initialize hex map

        Args:
            width: Map width in hexes
            height: Map height in hexes
            hex_size: Miles per hex (default 24)
        """
        self.width = width
        self.height = height
        self.hex_size = hex_size
        self.hexes: Dict[Tuple[int, int], Hex] = {}

    def add_hex(self, hex_obj: Hex):
        """Add a hex to the map"""
        self.hexes[(hex_obj.q, hex_obj.r)] = hex_obj

    def get_hex(self, q: int, r: int) -> Optional[Hex]:
        """Get hex at coordinates"""
        return self.hexes.get((q, r))

    def get_neighbors(self, q: int, r: int) -> List[Tuple[int, int]]:
        """
        Get 6 neighboring hex coordinates (offset coordinate system)

        Offset coordinates (odd-r layout):
        - Even rows: NW, NE, E, SE, SW, W
        - Odd rows: NW, NE, E, SE, SW, W (offsets differ)

        Returns:
            List of (q, r) tuples for valid neighbors
        """
        neighbors = []

        if r % 2 == 0:  # Even row
            offsets = [
                (-1, -1),  # NW
                (0, -1),   # NE
                (1, 0),    # E
                (0, 1),    # SE
                (-1, 1),   # SW
                (-1, 0)    # W
            ]
        else:  # Odd row
            offsets = [
                (0, -1),   # NW
                (1, -1),   # NE
                (1, 0),    # E
                (1, 1),    # SE
                (0, 1),    # SW
                (-1, 0)    # W
            ]

        for dq, dr in offsets:
            nq, nr = q + dq, r + dr
            if 0 <= nq < self.width and 0 <= nr < self.height:
                neighbors.append((nq, nr))

        return neighbors

    def get_direction_to_neighbor(self, from_q: int, from_r: int, to_q: int, to_r: int) -> Optional[str]:
        """
        Get direction name for movement between adjacent hexes

        Returns:
            Direction string: 'north', 'northeast', 'southeast', 'south', 'southwest', 'northwest'
            None if hexes are not adjacent
        """
        neighbors = self.get_neighbors(from_q, from_r)
        if (to_q, to_r) not in neighbors:
            return None

        dq = to_q - from_q
        dr = to_r - from_r

        # Direction mapping (works for both even and odd rows)
        if dr == -1:
            if dq == 0:
                return 'northeast' if from_r % 2 == 1 else 'northwest'
            elif dq == 1:
                return 'northeast'
            elif dq == -1:
                return 'northwest'
        elif dr == 0:
            if dq == 1:
                return 'east'
            elif dq == -1:
                return 'west'
        elif dr == 1:
            if dq == 0:
                return 'southeast' if from_r % 2 == 1 else 'southwest'
            elif dq == 1:
                return 'southeast'
            elif dq == -1:
                return 'southwest'

        return None

    def get_hex_in_direction(self, q: int, r: int, direction: str) -> Optional[Tuple[int, int]]:
        """
        Get hex coordinates in a direction

        Args:
            q, r: Starting coordinates
            direction: 'north', 'south', 'east', 'west', 'northeast', 'northwest', 'southeast', 'southwest'

        Returns:
            (q, r) tuple or None if invalid
        """
        neighbors = self.get_neighbors(q, r)
        for nq, nr in neighbors:
            if self.get_direction_to_neighbor(q, r, nq, nr) == direction:
                return (nq, nr)
        return None

    def get_distance(self, q1: int, r1: int, q2: int, r2: int) -> int:
        """
        Get distance in hexes between two coordinates (Manhattan distance approximation)

        Returns:
            Number of hexes
        """
        # Convert offset to cube coordinates for distance calculation
        x1, y1, z1 = self._offset_to_cube(q1, r1)
        x2, y2, z2 = self._offset_to_cube(q2, r2)

        return (abs(x1 - x2) + abs(y1 - y2) + abs(z1 - z2)) // 2

    def _offset_to_cube(self, q: int, r: int) -> Tuple[int, int, int]:
        """Convert offset coordinates to cube coordinates"""
        x = q - (r - (r & 1)) // 2
        z = r
        y = -x - z
        return (x, y, z)

    def get_terrain_at(self, q: int, r: int) -> Optional[str]:
        """Get terrain type at coordinates"""
        hex_obj = self.get_hex(q, r)
        return hex_obj.terrain if hex_obj else None

    def get_region_at(self, q: int, r: int) -> Optional[str]:
        """Get region at coordinates"""
        hex_obj = self.get_hex(q, r)
        return hex_obj.region if hex_obj else None

    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            'width': self.width,
            'height': self.height,
            'hex_size': self.hex_size,
            'hexes': [
                {
                    'q': hex_obj.q,
                    'r': hex_obj.r,
                    'terrain': hex_obj.terrain,
                    'region': hex_obj.region,
                    'features': hex_obj.features,
                    'travel_cost': hex_obj.travel_cost,
                    'description': hex_obj.description
                }
                for hex_obj in self.hexes.values()
            ]
        }

    @classmethod
    def load_from_file(cls, file_path: Path) -> 'HexMap':
        """Load hex map from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)

        hex_map = cls(data['width'], data['height'], data['hex_size'])

        for hex_data in data['hexes']:
            hex_obj = Hex(
                q=hex_data['q'],
                r=hex_data['r'],
                terrain=hex_data['terrain'],
                region=hex_data['region'],
                features=hex_data.get('features', []),
                travel_cost=hex_data['travel_cost'],
                description=hex_data['description']
            )
            hex_map.add_hex(hex_obj)

        return hex_map
```

#### tests/test_hex_map.py

```python
"""
Unit tests for HexMap
"""

import unittest
from aerthos.world.hex_map import HexMap, Hex


class TestHexMap(unittest.TestCase):
    """Test hex map functionality"""

    def setUp(self):
        """Create test hex map"""
        self.map = HexMap(width=10, height=10, hex_size=24)

        # Add some test hexes
        self.map.add_hex(Hex(5, 5, 'plains', 'test_region', [], 1.0, 'Test plains'))
        self.map.add_hex(Hex(6, 5, 'forest', 'test_region', [], 1.5, 'Test forest'))
        self.map.add_hex(Hex(5, 6, 'mountains', 'test_region', [], 2.0, 'Test mountains'))

    def test_get_hex(self):
        """Test hex retrieval"""
        hex_obj = self.map.get_hex(5, 5)
        self.assertIsNotNone(hex_obj)
        self.assertEqual(hex_obj.terrain, 'plains')
        self.assertEqual(hex_obj.region, 'test_region')

    def test_get_neighbors(self):
        """Test neighbor calculation"""
        neighbors = self.map.get_neighbors(5, 5)
        self.assertEqual(len(neighbors), 6)  # 6 neighbors for non-edge hex

        # Edge hex should have fewer neighbors
        edge_neighbors = self.map.get_neighbors(0, 0)
        self.assertLess(len(edge_neighbors), 6)

    def test_get_direction_to_neighbor(self):
        """Test direction calculation"""
        direction = self.map.get_direction_to_neighbor(5, 5, 6, 5)
        self.assertIn(direction, ['east', 'northeast', 'southeast'])

    def test_get_hex_in_direction(self):
        """Test hex lookup by direction"""
        # This will depend on the row parity
        result = self.map.get_hex_in_direction(5, 5, 'east')
        self.assertIsNotNone(result)

    def test_distance(self):
        """Test distance calculation"""
        distance = self.map.get_distance(5, 5, 7, 7)
        self.assertGreater(distance, 0)

        # Same hex
        distance_same = self.map.get_distance(5, 5, 5, 5)
        self.assertEqual(distance_same, 0)

    def test_terrain_at(self):
        """Test terrain retrieval"""
        terrain = self.map.get_terrain_at(5, 5)
        self.assertEqual(terrain, 'plains')

        terrain_forest = self.map.get_terrain_at(6, 5)
        self.assertEqual(terrain_forest, 'forest')

    def test_region_at(self):
        """Test region retrieval"""
        region = self.map.get_region_at(5, 5)
        self.assertEqual(region, 'test_region')

    def test_serialization(self):
        """Test map serialization"""
        data = self.map.to_dict()
        self.assertEqual(data['width'], 10)
        self.assertEqual(data['height'], 10)
        self.assertEqual(data['hex_size'], 24)
        self.assertGreater(len(data['hexes']), 0)


if __name__ == '__main__':
    unittest.main()
```

---

### Code Examples - Phase 2

#### world/travel_system.py

```python
"""
Travel System - Overworld movement and encounters
"""

from typing import Dict, List, Optional, Tuple
import random
from dataclasses import dataclass


@dataclass
class TravelResult:
    """Result of a travel action"""
    success: bool
    hexes_moved: int
    time_spent_hours: int
    resources_consumed: Dict[str, int]  # {'rations': 1, 'light': 0}
    encounter: Optional[dict]  # Encounter data if one occurred
    arrived_at_location: Optional[str]  # Location ID if arrived
    message: str  # Narrative description


class TravelSystem:
    """
    Manages overworld travel mechanics

    Based on AD&D 1e DMG travel rules:
    - Base movement: 30 miles per day (1.25 hexes at 24 miles/hex)
    - Terrain affects speed (plains fast, mountains slow)
    - Encounter checks twice per day
    - Rations consumed once per day
    """

    def __init__(self, campaign, game_state):
        """
        Initialize travel system

        Args:
            campaign: Campaign instance
            game_state: GameState instance
        """
        self.campaign = campaign
        self.game_state = game_state
        self.hex_map = campaign.world_map

        # Travel paces (miles per day)
        self.PACE_SLOW = 18  # Cautious, lower encounter chance
        self.PACE_NORMAL = 24  # Standard, 1 hex per day
        self.PACE_FAST = 30  # Rushing, higher encounter chance

        self.current_pace = self.PACE_NORMAL

    def set_pace(self, pace: str):
        """
        Set travel pace

        Args:
            pace: 'slow', 'normal', or 'fast'
        """
        if pace == 'slow':
            self.current_pace = self.PACE_SLOW
        elif pace == 'normal':
            self.current_pace = self.PACE_NORMAL
        elif pace == 'fast':
            self.current_pace = self.PACE_FAST

    def travel(self, direction: str, distance: int = 1) -> TravelResult:
        """
        Travel in a direction for a distance

        Args:
            direction: 'north', 'south', 'east', 'west', etc.
            distance: Number of hexes to attempt to travel

        Returns:
            TravelResult with outcome
        """
        if not self.game_state.campaign:
            return TravelResult(
                success=False,
                hexes_moved=0,
                time_spent_hours=0,
                resources_consumed={},
                encounter=None,
                arrived_at_location=None,
                message="No active campaign for overworld travel."
            )

        # Get current hex
        current_hex = self.game_state.current_hex
        if not current_hex:
            return TravelResult(
                success=False,
                hexes_moved=0,
                time_spent_hours=0,
                resources_consumed={},
                encounter=None,
                arrived_at_location=None,
                message="Current hex not set."
            )

        q, r = current_hex
        hexes_moved = 0
        total_time = 0
        total_rations = 0
        encounter_occurred = None
        arrived_location = None

        # Move hex by hex
        for i in range(distance):
            # Get next hex in direction
            next_coords = self.hex_map.get_hex_in_direction(q, r, direction)
            if not next_coords:
                break  # Can't go further

            nq, nr = next_coords
            next_hex = self.hex_map.get_hex(nq, nr)
            if not next_hex:
                break  # Invalid hex

            # Calculate travel time based on terrain
            travel_hours = self._calculate_travel_time(next_hex)

            # Check for encounter
            encounter = self._check_encounter(next_hex, travel_hours)
            if encounter:
                encounter_occurred = encounter
                # Encounter interrupts travel
                self.game_state.current_hex = (nq, nr)
                hexes_moved += 1
                total_time += travel_hours
                break

            # Move to next hex
            q, r = nq, nr
            hexes_moved += 1
            total_time += travel_hours

            # Check if arrived at location
            if next_hex.features:
                for feature in next_hex.features:
                    if ':' in feature:
                        feature_type, feature_id = feature.split(':', 1)
                        if feature_type in ['settlement', 'dungeon', 'poi']:
                            arrived_location = feature_id
                            break

        # Update game state
        self.game_state.current_hex = (q, r)

        # Consume resources
        days = total_time // 24
        if days > 0:
            total_rations = days
            # TODO: Actually consume rations from party inventory

        # Advance time
        self.campaign.advance_time(total_time)

        # Build message
        if encounter_occurred:
            message = f"You travel {hexes_moved} hex(es) {direction} before encountering something!"
        elif arrived_location:
            message = f"You travel {hexes_moved} hex(es) {direction} and arrive at {arrived_location}."
        else:
            message = f"You travel {hexes_moved} hex(es) {direction}. ({total_time} hours)"

        return TravelResult(
            success=True,
            hexes_moved=hexes_moved,
            time_spent_hours=total_time,
            resources_consumed={'rations': total_rations},
            encounter=encounter_occurred,
            arrived_at_location=arrived_location,
            message=message
        )

    def _calculate_travel_time(self, hex_obj) -> int:
        """
        Calculate travel time through a hex

        Args:
            hex_obj: Hex instance

        Returns:
            Hours to traverse hex
        """
        # Base time: 24 miles at current pace
        base_hours = 24 / (self.current_pace / 24)

        # Apply terrain multiplier
        terrain_hours = base_hours * hex_obj.travel_cost

        return int(terrain_hours)

    def _check_encounter(self, hex_obj, travel_hours: int) -> Optional[dict]:
        """
        Check for random encounter

        Args:
            hex_obj: Hex being traveled through
            travel_hours: Hours of travel

        Returns:
            Encounter dict or None
        """
        # Base encounter chance: 33% per check (DMG standard)
        base_chance = 0.33

        # Modify by pace
        if self.current_pace == self.PACE_SLOW:
            base_chance *= 0.66  # Cautious reduces encounters
        elif self.current_pace == self.PACE_FAST:
            base_chance *= 1.5  # Rushing increases encounters

        # 2 checks per day (morning and evening)
        checks = max(1, travel_hours // 12)

        for _ in range(checks):
            if random.random() < base_chance:
                # Encounter!
                from aerthos.world.wilderness_encounters import WildernessEncounterSystem
                encounter_system = WildernessEncounterSystem(self.campaign)
                return encounter_system.generate_encounter(
                    hex_obj.region,
                    hex_obj.terrain,
                    self.game_state.party
                )

        return None
```

#### world/wilderness_encounters.py

```python
"""
Wilderness Encounter System - Generate random encounters
"""

from typing import Dict, List, Optional
import random
import json


class WildernessEncounterSystem:
    """
    Generates wilderness encounters from tables

    Based on AD&D 1e DMG Appendix C encounter tables
    """

    def __init__(self, campaign):
        """
        Initialize encounter system

        Args:
            campaign: Campaign instance with encounter tables
        """
        self.campaign = campaign
        self.encounter_tables = campaign.encounter_tables

    def generate_encounter(
        self,
        region: str,
        terrain: str,
        party: List
    ) -> Optional[Dict]:
        """
        Generate a wilderness encounter

        Args:
            region: Region ID (e.g., 'verdant_heartlands')
            terrain: Terrain type (e.g., 'plains', 'forest')
            party: Party list for level scaling

        Returns:
            Encounter dict or None
        """
        # Get encounter table
        table_key = f"{region}_{terrain}"
        table = self.encounter_tables.get(table_key)

        if not table:
            return None  # No table for this region/terrain

        # Roll on table
        roll = random.randint(1, 100)

        for entry in table['encounters']:
            min_roll, max_roll = entry['roll']
            if min_roll <= roll <= max_roll:
                return self._build_encounter(entry, party)

        return None  # No encounter

    def _build_encounter(self, entry: Dict, party: List) -> Dict:
        """
        Build encounter from table entry

        Args:
            entry: Encounter table entry
            party: Party for scaling

        Returns:
            Encounter dict
        """
        encounter_type = entry['type']

        if encounter_type == 'monster':
            return self._build_monster_encounter(entry, party)
        elif encounter_type == 'npc':
            return self._build_npc_encounter(entry)
        elif encounter_type == 'hazard':
            return self._build_hazard_encounter(entry)
        elif encounter_type == 'event':
            return self._build_event_encounter(entry)
        elif encounter_type == 'treasure':
            return self._build_treasure_encounter(entry)
        elif encounter_type == 'none':
            return None

        return None

    def _build_monster_encounter(self, entry: Dict, party: List) -> Dict:
        """Build combat encounter"""
        monster_id = entry['id']
        count_str = entry['count']

        # Roll count (e.g., "1d6" or "2d4")
        if 'd' in count_str:
            num_dice, die_size = count_str.split('d')
            count = sum(random.randint(1, int(die_size)) for _ in range(int(num_dice)))
        else:
            count = int(count_str)

        # Load monster data
        from aerthos.entities.monster import Monster
        from aerthos.data_loader import load_monster_data

        monster_data = load_monster_data()
        if monster_id not in monster_data:
            return None

        # Create monster instances
        monsters = []
        for i in range(count):
            monster = Monster.from_data(monster_data[monster_id])
            monsters.append(monster)

        return {
            'type': 'combat',
            'monsters': monsters,
            'description': f"You encounter {count} {monster_id}(s)!"
        }

    def _build_npc_encounter(self, entry: Dict) -> Dict:
        """Build NPC encounter"""
        npc_id = entry['id']
        count = entry['count']

        return {
            'type': 'npc',
            'npc_id': npc_id,
            'count': count,
            'description': f"You encounter {count} {npc_id.replace('_', ' ')}."
        }

    def _build_hazard_encounter(self, entry: Dict) -> Dict:
        """Build hazard encounter"""
        hazard_id = entry['id']

        return {
            'type': 'hazard',
            'hazard_id': hazard_id,
            'description': f"You encounter a hazard: {hazard_id.replace('_', ' ')}!"
        }

    def _build_event_encounter(self, entry: Dict) -> Dict:
        """Build event encounter"""
        event_id = entry['id']

        return {
            'type': 'event',
            'event_id': event_id,
            'description': f"You discover something: {event_id.replace('_', ' ')}."
        }

    def _build_treasure_encounter(self, entry: Dict) -> Dict:
        """Build treasure encounter"""
        treasure_id = entry['id']

        return {
            'type': 'treasure',
            'treasure_id': treasure_id,
            'description': f"You find treasure: {treasure_id.replace('_', ' ')}!"
        }
```

---

### Code Examples - Phase 3

#### world/location.py

```python
"""
Location Module - Base class for all map locations
"""

from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class Location:
    """
    Base class for all map locations

    Locations are points of interest on the overworld map:
    - Settlements (villages, cities)
    - Dungeons (ruins, lairs)
    - POIs (shrines, landmarks)
    """
    id: str
    type: str  # 'settlement', 'dungeon', 'poi', 'landmark'
    name: str
    hex_coordinates: Tuple[int, int]
    region: str
    description: str
    discovery_state: str = 'undiscovered'  # 'undiscovered', 'discovered', 'visited'

    def is_discovered(self) -> bool:
        """Check if location has been discovered"""
        return self.discovery_state in ['discovered', 'visited']

    def is_visited(self) -> bool:
        """Check if location has been visited"""
        return self.discovery_state == 'visited'

    def discover(self):
        """Mark location as discovered"""
        if self.discovery_state == 'undiscovered':
            self.discovery_state = 'discovered'

    def visit(self):
        """Mark location as visited"""
        self.discovery_state = 'visited'

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            'id': self.id,
            'type': self.type,
            'name': self.name,
            'hex': list(self.hex_coordinates),
            'region': self.region,
            'description': self.description,
            'discovery_state': self.discovery_state
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Location':
        """Deserialize from dictionary"""
        return cls(
            id=data['id'],
            type=data['type'],
            name=data['name'],
            hex_coordinates=tuple(data['hex']),
            region=data['region'],
            description=data['description'],
            discovery_state=data.get('discovery_state', 'undiscovered')
        )
```

---

## 🧪 TESTING STRATEGY

### Regression Testing (Every Phase)

```bash
# ALWAYS run before and after changes
python3 run_tests.py --no-web

# Expected: All 374 existing tests pass
# If tests fail: Fix code or update tests
```

### Unit Testing (Each New Module)

**Phase 1 Tests:**
```bash
python3 -m unittest tests.test_campaign -v
python3 -m unittest tests.test_hex_map -v
```

**Phase 2 Tests:**
```bash
python3 -m unittest tests.test_travel_system -v
python3 -m unittest tests.test_wilderness_encounters -v
```

**Phase 3 Tests:**
```bash
python3 -m unittest tests.test_location -v
python3 -m unittest tests.test_campaign_integration -v
```

### Manual Testing Checklist

**After Phase 1:**
- [ ] Load campaign from main menu
- [ ] Verify campaign metadata displays
- [ ] Check hex map loaded correctly
- [ ] Verify no errors on campaign load

**After Phase 2:**
- [ ] Use "travel north" command
- [ ] Verify time advances
- [ ] Verify resources consumed
- [ ] Encounter wilderness combat
- [ ] Verify combat works in wilderness

**After Phase 3:**
- [ ] Travel to settlement hex
- [ ] Use "enter oakhaven" command
- [ ] Use "shop" command in village
- [ ] Use "leave" to return to overworld
- [ ] Travel to dungeon hex
- [ ] Use "enter kaldor" command
- [ ] Play through dungeon
- [ ] Use "leave" to return to overworld

**After Phase 4:**
- [ ] Check reputation: "reputation"
- [ ] Complete quest or donate
- [ ] Check reputation changed
- [ ] Verify shop prices affected
- [ ] Verify inn rumors affected

**After Phase 5:**
- [ ] Check weather: "weather"
- [ ] Travel in storm
- [ ] Verify slower movement
- [ ] Verify saving throws vs environment

**After Phase 6:**
- [ ] Open web UI: http://localhost:5000
- [ ] Load campaign
- [ ] Verify map displays
- [ ] Verify locations visible
- [ ] Click hex to travel
- [ ] Enter location from web UI
- [ ] Verify all existing web features work

---

## ⚠️ RISK MITIGATION

### Technical Risks

**Risk: Breaking existing functionality**
- Mitigation: Run regression tests after every change
- Test both CLI and web UI manually after major changes

**Risk: Complex hex coordinate math errors**
- Mitigation: Write comprehensive unit tests for HexMap
- Test with multiple hex sizes and map shapes

**Risk: Performance issues with large maps**
- Mitigation: Start with 30x40 map, optimize if needed
- Consider lazy loading for very large maps

### Design Risks

**Risk: Campaign system too rigid for future campaigns**
- Mitigation: Keep Campaign class abstract, data-driven
- Test with second campaign (future) to validate modularity

**Risk: Save/load compatibility breaks**
- Mitigation: Version campaign save format
- Test deserialization with old saves

### Content Risks

**Risk: Incomplete Aerthos content at launch**
- Mitigation: Phase 7 is ongoing, prioritize starter areas
- Release with Oakhaven + Kaldor, expand later

**Risk: Unbalanced wilderness encounters**
- Mitigation: Playtest extensively, adjust tables as needed
- Start with conservative encounter chances

---

## 📚 QUICK REFERENCE

### Commands to Remember

```bash
# Run tests (always before/after changes)
python3 run_tests.py --no-web

# Run specific test
python3 -m unittest tests.test_hex_map -v

# Start CLI game
python main.py

# Start web UI
python web_ui/app.py
```

### File Locations

```
Campaign data:    data/campaigns/aerthos_campaign/
Campaign code:    aerthos/campaigns/
World systems:    aerthos/world/
Tests:            tests/
Docs:             docs/
```

### Key Files to Modify

**Phase 1:**
- `aerthos/engine/game_state.py` - Add campaign field
- `main.py` - Add campaign loading to menu

**Phase 2:**
- `aerthos/engine/parser.py` - Add travel commands

**Phase 3:**
- `aerthos/engine/parser.py` - Add location commands
- `aerthos/world/village.py` - Add hex coordinates
- `aerthos/world/dungeon.py` - Add hex coordinates

### Progress Tracking Template

```
Session Date: ___________
Phase: ___________
Tasks Completed:
- [ ] _____________________
- [ ] _____________________

Next Session Goals:
- [ ] _____________________
- [ ] _____________________

Blockers/Questions:
_____________________
```

---

## 🎉 READY TO BEGIN!

This plan is designed for part-time development. Take it one phase at a time, test frequently, and don't rush. The modular design means each phase is independent and can be completed in 1-3 weeks.

**Remember:**
1. ✅ Run tests before and after every change
2. ✅ Update progress tracker as you go
3. ✅ Keep sessions small and focused
4. ✅ Ask questions if anything is unclear

**Good luck, adventurer! The world of Aerthos awaits.**

---

*Last Updated: 2025-11-20*
*Status: Ready for Phase 1 Implementation*
