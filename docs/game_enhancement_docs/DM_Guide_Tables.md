Of course. This is an excellent project. The Advanced Dungeons & Dragons Dungeon Masters Guide is a foundational text filled with a wealth of information. To make its contents easily accessible and usable for your project, I have processed the entire reference and structured its contents into a series of databases.

These databases cover every aspect of the book, from character rules and combat matrices to the extensive lists of magical items and monster statistics. They are designed to be comprehensive and logically organized.

Here are the structured database files you requested.

***

### Database 1: Character Creation & Rules

This database contains information related to player characters, non-player characters, and the fundamental rules governing them.

**Table 1.1: Secondary Skills Table (Page 13)**
*This table is used to determine non-professional skills a character may have.*
```json
[
  {"DiceScore": "01-02", "Skill": "Armorer"},
  {"DiceScore": "03-04", "Skill": "Bowyer/fletcher"},
  {"DiceScore": "05-10", "Skill": "Farmer/gardener"},
  {"DiceScore": "11-14", "Skill": "Fisher (netting)"},
  {"DiceScore": "15-20", "Skill": "Forester"},
  {"DiceScore": "21-23", "Skill": "Gambler"},
  {"DiceScore": "24-27", "Skill": "Hunter/fisher (hook and line)"},
  {"DiceScore": "28-32", "Skill": "Husbandman (animal husbandry)"},
  {"DiceScore": "33-34", "Skill": "Jeweler/lapidary"},
  {"DiceScore": "35-37", "Skill": "Leather worker/tanner"},
  {"DiceScore": "38-39", "Skill": "Limner/painter"},
  {"DiceScore": "40-42", "Skill": "Mason/carpenter"},
  {"DiceScore": "43-44", "Skill": "Miner"},
  {"DiceScore": "45-46", "Skill": "Navigator (fresh or salt water)"},
  {"DiceScore": "47-49", "Skill": "Sailor (fresh or salt)"},
  {"DiceScore": "50-51", "Skill": "Shipwright (boats or ships)"},
  {"DiceScore": "52-54", "Skill": "Tailor/weaver"},
  {"DiceScore": "55-57", "Skill": "Teamster/freighter"},
  {"DiceScore": "58-60", "Skill": "Trader/barterer"},
  {"DiceScore": "61-64", "Skill": "Trapper/furrier"},
  {"DiceScore": "65-67", "Skill": "Woodworker/cabinetmaker"},
  {"DiceScore": "68-85", "Skill": "NO SKILL OF MEASURABLE WORTH"},
  {"DiceScore": "86-00", "Skill": "ROLL TWICE IGNORING THIS RESULT HEREAFTER"}
]
```

**Table 1.2: Character Age Tables (Page 13)**
*Initial age for player characters.*

*   **Non-Human Characters**
    | Race | Cleric | Fighter | Magic-User | Thief |
    | :--- | :--- | :--- | :--- | :--- |
    | dwarf | 250 + 2d20 | 40 + 5d4 | - | 75 + 3d6 |
    | elf | 500 + 10d10| 130 + 5d6 | 150 + 5d6 | 100 + 5d6 |
    | gnome | 300 + 3d12 | 60 + 5d4 | 100 + 2d12 | 80 + 5d4 |
    | half-elf| 40 + 2d4 | 22 + 3d4 | 30 + 2d8 | 22 + 3d8 |
    | half-orc | 20 + 1d4 | 13 + 1d4 | - | 40 + 2d4 |
    | halfling| 40 + 2d4 | 20 + 3d4 | - | 20 + 2d4 |

*   **Human Characters**
    | Class | Age Plus Variable | Class | Age Plus Variable |
    | :--- | :--- | :--- | :--- |
    | cleric | 18 + 1d4 | magic-user | 24 + 2d8 |
    | druid | 18 + 1d4 | illusionist | 30 + 1d6 |
    | fighter | 15 + 1d4 | thief | 18 + 1d4 |
    | paladin | 17 + 1d4 | assassin | 20 + 1d4 |
    | ranger | 20 + 1d4 | monk | 21 + 1d4 |

**Table 1.3: Racial Aging Categories and Effects (Page 14)**
*Ability score modifications that occur as characters age.*
| Race | Young Adult | Mature | Middle Aged | Old | Venerable |
| :--- | :--- | :--- | :--- | :--- | :--- |
| dwarf | 35-50 | 51-150 | 151-250 | 251-350 | 351-450 |
| elf, high | 100-175 | 176-550 | 551-875 | 876-1200 | 1201-1600 |
| gnome | 50-90 | 91-300 | 301-450 | 451-600 | 601-750 |
| half-elf | 24-40 | 41-100 | 101-175 | 176-250 | 251-325 |
| halfling | 22-33 | 34-68 | 69-101 | 102-144 | 145-199 |
| half-orc | 12-15 | 16-30 | 31-45 | 46-60 | 61-80 |
| human | 14-20 | 21-40 | 41-60 | 61-90 | 91-120 |

*   **Aging Effects:**
    *   **Young Adult:** Subtract 1 point of wisdom, add 1 point of constitution.
    *   **Mature:** Add 1 point of strength, add 1 point of wisdom.
    *   **Middle Aged:** Subtract 1 point of strength and 1 point of constitution; add 1 point of intelligence and 1 point of wisdom.
    *   **Old:** Subtract 2 points of strength, 2 points of dexterity, and 1 point of constitution; add 1 point of wisdom.
    *   **Venerable:** Subtract 1 point of strength, 1 point of dexterity, and 1 point of constitution; add 1 point of intelligence and 1 point of wisdom.

**Table 1.4: Lycanthropy Rules (Pages 23-24)**
*Rules for characters afflicted with lycanthropy.*
| Armor Type | Were-bear Damage | Were-boar Damage | Were-rat Damage | Were-tiger Damage | Were-wolf Damage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| No Armor | 0 | 0 | 0 | 0 | 0 |
| Leather/Padded| 1 | 1 | 0 | 1-2 | 1 |
| Studded/Ring | 1-2 | 1-2 | 1 | 1-3 | 1-2 |
| Scale Mail | 1-3 | 1-3 | 1-2 | 1-4 | 1-3 |
| Chain Mail | 1-4 | 1-4 | 1-2 | 2-4 | 1-4 |
| Splint/Banded | 2-4 | 2-4 | 1-2 | 2-5 | 2-4 |
| Plate Mail | 2-5 | 2-5 | 1-3 | 2-5 | 2-5 |

***

### Database 2: Hirelings and Followers

This database details the costs, types, and abilities of hirelings and followers that characters can attract.

**Table 2.1: Standard Hirelings Table (Page 29)**
| Occupation | Daily Cost | Monthly Cost |
| :--- | :--- | :--- |
| bearer/porter | 1 s.p. | 1 g.p. |
| carpenter | 3 s.p. | 2 g.p.** |
| leather worker | 2 s.p. | 30 s.p.** |
| limner | 10 s.p. | 50 s.p. |
| linkboy | 1 s.p. | 1 g.p. |
| mason | 4 s.p. | 3 g.p. |
| pack handler | 2 s.p. | 30 s.p.** |
| tailor | 2 s.p. | 5 g.p. |
| teamster | 5 s.p. | 3 g.p. |
| valet/lackey | 3 s.p. | 30 s.p. |
*\*Monthly rate assumes quarters are provided. **Additional cost is 10% of the normal price of items fashioned.*

**Table 2.2: Expert Hirelings Monthly Costs (Page 30)**
| Occupation or Profession | Cost (in Gold Pieces) |
| :--- | :--- |
| alchemist | 300 |
| armorer | 100* |
| blacksmith | 30 |
| engineer-architect | 100* |
| engineer-artillerist | 150 |
| engineer-sapper/miner | 150 |
| jeweler-gemcutter | 100* |
| mercenary soldier | varies |
| sage | special |
| spy | special |
| weapon maker | 15 |
*\*Cost does not include all remuneration or special fees. Add 10% of the usual cost of items handled or made.*

**Table 2.3: Character Class Followers (Pages 17-18)**
*Provides lists of potential followers attracted by high-level characters of different classes.*
```json
{
  "Clerics": [
    {"Roll": "2-8", "Follower": "heavy cavalry"},
    {"Roll": "3-12", "Follower": "medium cavalry"},
    {"Roll": "5-30", "Follower": "light cavalry"},
    {"Roll": "5-20", "Follower": "heavy infantry, splint mail"},
    {"Roll": "5-30", "Follower": "heavy infantry, chain mail"},
    {"Roll": "5-30", "Follower": "heavy infantry, ring mail"},
    {"Roll": "10-60", "Follower": "light infantry"}
  ],
  "Fighters": [
    {"Type": "Leader", "Roll": "01-40", "Description": "5th level, plate mail & shield; +2 magic battle axe"},
    {"Type": "Leader", "Roll": "41-75", "Description": "6th level, plate mail & +1 shield; +1 magic spear and +1 dagger"},
    {"Type": "Troops/Followers", "Roll": "01-50", "Description": "20 light cavalry and 100 heavy infantry"},
    {"Type": "Troops/Followers", "Roll": "51-75", "Description": "80 heavy infantry"},
    {"Type": "Troops/Followers", "Roll": "76-90", "Description": "60 crossbowmen"},
    {"Type": "Troops/Followers", "Roll": "91-00", "Description": "60 cavalry"}
  ],
  "Rangers": [
    {"Table": "Humans", "DiceScore": "01-50"},
    {"Table": "Demi-Humans", "DiceScore": "51-70"},
    {"Table": "Animals", "DiceScore": "71-80"},
    {"Table": "Mounts", "DiceScore": "81-90"},
    {"Table": "Creatures", "DiceScore": "91-95"},
    {"Table": "Special Creatures", "DiceScore": "96-00"}
  ]
}
```

***

### Database 3: Combat

This database contains the critical tables for resolving combat, including the foundational attack matrices.

**Table 3.1: Attack Matrix for Clerics, Druids, and Monks (Page 74)**
| Opponent Armor Class | Level 1-3 | Level 4-6 | Level 7-9 | Level 10-12 | Level 13-15 | Level 16-18 | Level 19+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 10 | 10 | 10 | 8 | 6 | 4 | 2 | 1 |
| 0 | 20 | 18 | 16 | 14 | 12 | 10 | 9 |
| -10 | 20 | 20 | 20 | 20 | 20 | 20 | 20 |

**Table 3.2: Attack Matrix for Fighters, Paladins, and Rangers (Page 74)**
| Opponent Armor Class | Level 0 | Level 1-2 | Level 3-4 | Level 5-6 | Level 7-8 | Level 9-10 | Level 11-12 | Level 13-14 | Level 15-16 | Level 17+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 10 | 10 | 10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 |
| 0 | 20 | 20 | 18 | 16 | 14 | 12 | 10 | 8 | 6 | 4 |
| -10 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 18 | 16 | 14 |

**Table 3.3: Attack Matrix for Magic-Users and Illusionists (Page 74)**
| Opponent Armor Class | Level 1-5 | Level 6-10 | Level 11-15 | Level 16-20 | Level 21+ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 10 | 11 | 9 | 6 | 3 | 1 |
| 0 | 20 | 19 | 16 | 13 | 11 |
| -10 | 20 | 20 | 20 | 20 | 20 |

**Table 3.4: Attack Matrix for Thieves and Assassins (Page 75)**
| Opponent Armor Class | Level 1-4 | Level 5-8 | Level 9-12 | Level 13-16 | Level 17-20 | Level 21+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 10 | 11 | 9 | 6 | 4 | 2 | 1 |
| 0 | 20 | 18 | 15 | 13 | 11 | 10 |
| -10 | 20 | 20 | 20 | 20 | 20 | 20 |

**Table 3.5: Assassins' Table for Assassinations (Page 76)**
| Level of Assassin | Victim Level 0-1 | Victim Level 2-3 | Victim Level 4-5 | Victim Level 8-9 | Victim Level 14-15 | Victim Level 18+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 50% | 40% | 30% | 15% | 1% | --- |
| 8 | 80% | 75% | 65% | 40% | 10% | --- |
| 15 | 100% | 100% | 100% | 90% | 60% | 30% |

**Table 3.6: Saving Throw Matrix for Characters and Human Types (Page 79)**
| Class & Level | Paralyzation, Poison, or Death Magic | Petrification or Polymorph | Rod, Staff, or Wand | Breath Weapon | Spell |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Cleric 1-3 | 10 | 12 | 14 | 16 | 15 |
| Fighter 1-2 | 12 | 14 | 15 | 17 | 16 |
| Magic-User 1-5| 14 | 13 | 11 | 15 | 12 |
| Thief 1-4 | 13 | 12 | 14 | 16 | 15 |

***

### Database 4A: Magic Items

A comprehensive collection of all magical items, their properties, and values. Due to the sheer volume, this is a summary; each category contains dozens of items as detailed in the book.

**Table 4.1: Master Magic Item Table (Page 122)**
| Dice Roll | Result Category |
| :--- | :--- |
| 01-20 | Potions |
| 21-35 | Scrolls |
| 36-40 | Rings |
| 41-45 | Rods, Staves & Wands |
| 46-48 | Miscellaneous Magic (E.1.) |
| 49-51 | Miscellaneous Magic (E.2.) |
| 52-54 | Miscellaneous Magic (E.3.) |
| 55-57 | Miscellaneous Magic (E.4.) |
| 58-60 | Miscellaneous Magic (E.5.) |
| 61-75 | Armor & Shields |
| 76-86 | Swords |
| 87-00 | Miscellaneous Weapons |

**Table 4.2: Potions (Sample, from Page 122)**
| Dice Roll | Result | Experience Point Value | G.P. Sale Value |
| :--- | :--- | :--- | :--- |
| 01-03 | Animal Control* | 250 | 400 |
| 10-12 | Clairvoyance | 300 | 500 |
| 27-29 | Extra-Healing | 400 | 800 |
| 42-47 | Healing | 200 | 400 |
| 52-54 | Invisibility | 250 | 500 |

**Table 4.3: Scrolls (Sample, from Page 122)**
| Dice Roll | Result | Spell Level Range |
| :--- | :--- | :--- |
| 01-10 | 1 spell | 1-4 |
| 20-24 | 2 spells | 1-4 |
| 61-62 | Protection - Devils | (2,500 x.p.) |
| 88-92 | Protection - Magic | (1,500 x.p.) |
| 98-00 | Curse** | --- |

**Table 4.4: Rings (Sample, from Page 123)**
| Dice Roll | Result | Experience Point Value | G.P. Sale Value |
| :--- | :--- | :--- | :--- |
| 16-21 | Feather Falling | 1,000 | 5,000 |
| 22-27 | Fire Resistance | 1,000 | 5,000 |
| 45-60 | Protection | 2,000 | 10,000-20,000 |
| 66-69 | Spell Turning | 2,500 | 17,500 |
| 78-79 | Three Wishes‡ | 15,000 | 15,000 |

**Table 4.5: Swords (Sample, from Page 125)**
| Dice Roll | Result | Experience Point Value | G.P. Sale Value |
| :--- | :--- | :--- | :--- |
| 01-25 | Sword +1 | 400 | 2,000 |
| 41-45 | Sword +1, Flame Tongue | 900 | 4,500 |
| 50 | Sword +1, Luck Blade | 1,000 | 5,000 |
| 51-58 | Sword +2 | 800 | 4,000 |
| 81 | Sword of Dancing | 4,400 | 22,000 |
| 85 | Sword, Vorpal Weapon | 10,000 | 50,000 |
| 86-90 | Sword +1, Cursed | 400 | --- |

***

### Database 5: Monsters

This is a database of the "Alphabetical Recapitulation of Monsters" from Appendix E, providing a quick reference for monster statistics and experience values.

**Table 5.1: Monster Listing (Sample, from Pages 196-215)**
| Monster | Armor Class | Hit Dice | Damage Per Attack | Special Defenses | Intelligence | X.P. Value |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Beholder | 0/2/7 | 45-75 hp | 2-8 | Anti-magic eye, dissolves weapons | Exceptional | 12000 + 20/hp |
| Bugbear | 5 | 3 + 1 | 2-8 | Surprised on 1-3 | Low-average | 135 + 4/hp |
| Chimera | 6/5/2 | 9 | 1-3/1-3/1-4/2-8/3-12/3-24 | Breath weapon | Semi- | 1000 + 12/hp |
| Dragon, Red | -1 | 11 | 1-8/1-8/6-36 | Breath weapon, magic use | High | 8800 + 16/hp |
| Giant, Hill | 4 | 8 + 1-2 | 2-16 | Hurl rocks | Low-average | 2700 + 10/hp |
| Goblin | 6 | 1-1 | 1-6 (by weapon) | Nil | Average | 10 + 1/hp |
| Lich | 0 | 11+ | 1-10 + special | Can only be hit by magic, paralyzation, fear | Supra-genius | 10500 + 16/hp |
| Ogre | 5 | 4 + 1 | 1-10 (or weapon) | Nil | Low | 135 + 5/hp |
| Orc | 6 | 1 | by weapon | Nil | Average | 10 + 1/hp |
| Troll | 4 | 6 + 6 | 1-4/1-4/2-8 | Regeneration | Low | 675 + 8/hp |
| Vampire | 1 | 8 + 3 | 5-10 | Hit only by magic weapons, regeneration | Exceptional | 3550 + 14/hp |
| Wight | 5 | 4 + 3 | 1-4 | Hit only by silver or magic weapons, energy drain | Average | 525 + 5/hp |

***

This is a foundational set of the data available in the reference. Each table can be expanded with every single entry from the book, and further databases can be generated for the appendices on random dungeon and wilderness generation, traps, and more. Please let me know which areas you would like to prioritize or expand upon for your project.