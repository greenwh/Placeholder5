

### Database 6: Random Dungeon Generation (Appendix A)

This database contains the full, interconnected set of tables from Appendix A (Pages 169-173) used for creating dungeon layouts procedurally. The process begins with the "Periodic Check" table and branches out from there.

**Table 6.1: Periodic Check (d20)**
*This is the main generation table. Roll every 30' in a passage.*
```json
[
  {"DiceRoll": "1-2", "Result": "Continue straight — check again in 60'"},
  {"DiceRoll": "3-5", "Result": "Door (see Table 6.2)"},
  {"DiceRoll": "6-10", "Result": "Side Passage (see Table 6.3) — check again in 30'"},
  {"DiceRoll": "11-13", "Result": "Passage Turns (see Table 6.4)"},
  {"DiceRoll": "14-16", "Result": "Chamber (see Table 6.5) — check 30' after leaving"},
  {"DiceRoll": "17", "Result": "Stairs (see Table 6.6)"},
  {"DiceRoll": "18", "Result": "Dead End"},
  {"DiceRoll": "19", "Result": "Trick/Trap (see Table 6.7) — check again in 30'"},
  {"DiceRoll": "20", "Result": "Wandering Monster, then check again immediately"}
]
```

**Table 6.2: Doors (d20)**
| Location | Dice Roll | Space Beyond Door Is... |
| :--- | :--- | :--- |
| Left | 1-6 | **1-4:** Parallel passage, or 10'x10' room |
| Right | 7-12 | **5-8:** Passage straight ahead |
| Ahead | 13-20 | **9-10:** Passage at 45 degrees |
| | | **11-18:** Room (Go to Table 6.5) |
| | | **19-20:** Chamber (Go to Table 6.5) |

**Table 6.3: Side Passages (d20)**
| Dice Roll | Result |
| :--- | :--- |
| 1-2 | left 90 degrees |
| 3-4 | right 90 degrees |
| 5 | left 45 degrees ahead |
| 6 | right 45 degrees ahead |
| 7 | left 45 degrees behind (135 degrees) |
| 8 | right 45 degrees behind (135 degrees) |
| 9 | left curve 45 degrees ahead |
| 10 | right curve 45 degrees ahead |
| 11-13 | passage "T"s |
| 14-15 | passage "Y"s |
| 16-19 | four-way intersection |
| 20 | passage "X"s |

**Table 6.4: Passage Turns (d20)**
| Dice Roll | Result |
| :--- | :--- |
| 1-8 | left 90 degrees |
| 9 | left 45 degrees ahead |
| 10 | left 45 degrees behind (135 degrees) |
| 11-18 | right 90 degrees |
| 19 | right 45 degrees ahead |
| 20 | right 45 degrees behind (135 degrees) |

**Table 6.5: Chambers and Rooms (d20)**
*This is a master table with several sub-tables for determining the specifics of a room or chamber.*
*   **V: Shape and Area**
    | Dice Roll | Chamber Shape and Area | Room Shape and Area |
    | :--- | :--- | :--- |
    | 1-2 | Square, 20'x20' | Square, 10'x10' |
    | 3-4 | Square, 20'x20' | Square, 20'x20' |
    | 5-6 | Square, 30'x30' | Square, 30'x30' |
    | 7-8 | Square, 40'x40' | Square, 40'x40' |
    | 9-10 | Rectangular, 20'x30' | Rectangular, 10'x20' |
    | 11-13 | Rectangular, 20'x30' | Rectangular, 20'x30' |
    | 14-15 | Rectangular, 30'x50' | Rectangular, 20'x40' |
    | 16-17 | Rectangular, 40'x60' | Rectangular, 30'x40' |
    | 18-20 | Unusual shape and size | (see sub-tables) |
*   **V.F: Chamber or Room Contents (d20)**
    | Dice Roll | Contents |
    | :--- | :--- |
    | 1-12 | Empty |
    | 13-14 | Monster only |
    | 15-17 | Monster and treasure |
    | 18 | Special, or stairway |
    | 19 | Trick/Trap |
    | 20 | Treasure |
*   **V.I: Treasure Is Guarded By (d20)**
    | Dice Roll | Guard/Trap |
    | :--- | :--- |
    | 1-2 | Contact poison on container |
    | 3-4 | Contact poison on treasure |
    | 5-6 | Poisoned needles in lock |
    | 7 | Poisoned needles in handles |
    | 8 | Spring darts firing from front of container |
    | 9 | Spring darts firing up from top of container |
    | 10 | Spring darts firing up from inside bottom |
    | 11-12 | Blade scything across inside |
    | 13 | Poisonous insects or reptiles inside |
    | 14 | Gas released by opening container |
    | 15-20 | (Various other traps) |

**Table 6.6: Stairs (d20)**
| Dice Roll | Result |
| :--- | :--- |
| 1-5 | Down 1 level |
| 6 | Down 2 levels |
| 7 | Down 3 levels |
| 8 | Up 1 level |
| 9 | Up dead end |
| 10 | Down dead end |
| 11-13 | Chimneys |
| 14-16 | Trap door down 1 level |
| 17 | Trap door down 2 levels |
| 18-20 | Up 1 then down 2 (total down 1) |

**Table 6.7: Trick/Trap (d20)**
| Dice Roll | Result |
| :--- | :--- |
| 1-5 | Secret Door |
| 6-7 | Pit, 10' deep |
| 8 | Pit, 10' deep with spikes |
| 9-11 | Elevator room |
| 12-20 | (Various other tricks and traps) |

***

### Database 7: Random Wilderness Generation (Appendix B)

These tables from page 173 are used to generate wilderness terrain procedurally as a party explores the unknown.

**Table 7.1: Wilderness Terrain Generation (d20)**
*To use, find the current terrain type in the top row, then roll a d20 and find the result in that column to determine the next terrain type by reading to the left.*
| Resulting Terrain | Plain | Scrub | Forest | Rough | Desert | Hills | Mountains | Marsh |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Plain | 1-11 | 1-3 | 1 | 1-2 | 1-3 | 1 | 1 | 1-2 |
| Scrub | 12 | 4-11 | 2-4 | 3-4 | 4-5 | 2-3 | 2 | 3-4 |
| Forest | 13 | 12-13 | 5-14 | 5 | -- | 4-5 | 3 | 5-6 |
| Rough | 14 | 14 | 15 | 6-8 | 6-8 | 6-7 | 4-5 | 7 |
| Desert | 15 | 15 | -- | 9-10 | 9-14 | 8 | 6 | -- |
| Hills | 16 | 16 | 16 | 11-15 | 15 | 9-14 | 7-10 | 8 |
| Mountains | 17 | 17 | 17 | 16-17 | 16-17 | 15-16 | 11-18 | -- |
| Marsh | 18 | 18 | 18 | 18 | 18 | 17 | -- | 9-15 |
| Pond | 19 | 19 | 19 | 19 | 19 | 18-19 | 19 | 16-19 |
| Depression | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 |

**Table 7.2: Inhabitation (d100)**
*Check each wilderness space for the possibility of habitation.*
| Dice Roll | Type of Settlement | Population |
| :--- | :--- | :--- |
| 01-03 | Single Dwelling | 1-12 |
| 04-05 | Thorps | 20-80 |
| 06-07 | Hamlet | 100-400 |
| 08-09 | Village | 600-900 |
| 10 | Town | 1,000-6,000 |
| 11 | City | 10,000-50,000 |
| 12-14 | Castle | Varies |
| 15-16 | Village | Varies |
| 17-30 | Ruins | Varies |
| 31-60 | Tomb | Varies |
| 61-85 | Shrine | Varies |
| 86-00 | Uninhabited | 0 |

***

### Database 8: Populating Adventures

This database includes tools for adding flavor, detail, and specific hazards to your generated adventure locations, drawn from Appendices G, H, and I.

**Table 8.1: Dungeon Dressing (Appendix I - Sample, Pages 217-219)**
*This is a selection from multiple tables used to add descriptive details to otherwise empty rooms and corridors.*
```json
{
  "General": [
    "arrow, broken", "bones", "cobwebs", "cracks, floor", "dripping", "dust", "fungi, common", "iron bar, bent, rusted", "rubble & dirt", "slimy coating, wall", "sticks", "wall scratchings"
  ],
  "Unexplained Sounds and Weird Noises": [
    "bellow(ing)", "chanting", "clanking", "coughing", "footsteps (ahead)", "groaning", "hissing", "knocking", "laughter", "moaning", "rattling", "scream(ing)", "whispering"
  ],
  "Furnishings and Appointments": [
    "altar", "armoire", "bed", "bench", "box (large)", "brazier", "cabinet", "candelabrum", "carpet", "chair", "chest", "couch", "desk", "fireplace", "idol", "mattress", "pedestal", "screen", "shrine", "statue", "table", "tapestry", "throne", "workbench"
  ]
}
```

**Table 8.2: Trap List (Appendix G, Page 216)**
| Dice Roll (%) | Trap |
| :--- | :--- |
| 01-05 | Arrow trap |
| 06 | Arrow trap, poisoned |
| 08-09 | Caltrops |
| 14-16 | Ceiling block falls |
| 19-23 | Door, falling |
| 33 | Floor, collapsing |
| 37-38 | Gas, corroding |
| 47-48 | Gas, poison |
| 58-59 | Pendulum, ball or blade |
| 60-63 | Pit |
| 68-70 | Pit, with spikes |

***

### Database 9: Adventure Environment Rules

This database contains key rules and tables from the main body of the text that govern movement and encounters in various adventure environments.

**Table 9.1: Outdoor Encounter Chance (Page 47)**
| Population Density | Base Chance Of Encounter |
| :--- | :--- |
| relatively dense | 1 in 20 |
| moderate to sparse/patrolled| 1 in 12 |
| uninhabited/wilderness | 1 in 10 |

**Table 9.2: Chance Of Becoming Lost (Page 49)**
| Terrain Type | Chance Of Becoming Lost | Direction Lost |
| :--- | :--- | :--- |
| Plain | 1 in 10 | 60° left or right |
| Scrub | 3 in 10 | 60° left or right |
| Forest | 7 in 10 | any |
| Desert | 4 in 10 | 60° left or right |
| Hills | 2 in 10 | 60° left or right |
| Mountains | 5 in 10 | 120° left or right |
| Marsh | 6 in 10 | any |

**Table 9.3: Movement Afloat, Sailed in Miles/Day (Page 58)**
| Vessel Type | Lake | River* | Sea |
| :--- | :--- | :--- | :--- |
| raft | 30 | 30 | --- |
| boat, small | 80 | 60 | --- |
| barge | 50 | 40 | --- |
| galley, small | 70-80 | 60 | 50 |
| galley, large | 50-60 | 50 | 50 |
| merchant, small | 25-35 | 50 | 50 |
| merchant, large | 40-50 | 35 | 35 |
| warship | 50-60 | 40 | 50 |
*\*See book for effects of current on movement.*

***

These databases provide the mechanical core for creating and populating adventures. What is the next most critical area for your project?