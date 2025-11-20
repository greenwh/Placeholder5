"""
Procedural Dungeon Generator

Generates complete dungeons based on DungeonConfig parameters.
Supports fixed (seeded) and random generation.
"""

import random
from typing import List, Dict, Set, Tuple, Optional
from .config import DungeonConfig
from ..systems.narrator import DMNarrator, NarrativeContext
from ..systems.environment_filter import EnvironmentMonsterFilter, EnvironmentContext


class DungeonGenerator:
    """
    Procedural dungeon generation

    Uses config parameters to generate room layouts, encounters,
    treasures, and descriptions. Supports seeded generation for
    reproducible dungeons.
    """

    def __init__(self, game_data=None, use_narrator=True):
        """
        Initialize generator

        Args:
            game_data: GameData instance with monsters/items (optional)
            use_narrator: If True, use DMNarrator for atmospheric descriptions
        """
        self.game_data = game_data
        self.rng = random.Random()
        self.use_narrator = use_narrator
        self.narrator = DMNarrator() if use_narrator else None
        self.environment_filter = EnvironmentMonsterFilter()

        # Theme-based description templates
        self.themes = {
            'mine': {
                'titles': [
                    'Abandoned Shaft', 'Mining Tunnel', 'Ore Chamber', 'Cart Storage',
                    'Excavation Site', 'Collapsed Passage', 'Miners\' Rest', 'Tool Room',
                    'Vein Chamber', 'Deep Shaft', 'Crystal Cavern', 'Foreman\'s Office'
                ],
                'descriptions': [
                    'Wooden support beams creak ominously as you enter. Mining tools lie scattered about.',
                    'An old mining cart sits rusted on broken tracks. The air is thick with dust.',
                    'Pickaxes and shovels hang on the walls. A faint draft brings the smell of earth.',
                    'Broken lanterns and rope coils litter the floor. The ceiling drips with moisture.',
                    'Precious ore veins glimmer in the darkness. This was once a rich find.',
                    'The passage ahead has partially collapsed, forcing a narrow squeeze through rubble.'
                ]
            },
            'crypt': {
                'titles': [
                    'Burial Chamber', 'Tomb Entrance', 'Ossuary', 'Catacombs',
                    'Shrine of the Dead', 'Sarcophagus Hall', 'Bone Chapel', 'Crypt Passage',
                    'Memorial Hall', 'Ancient Vault', 'Sepulcher', 'Charnel House'
                ],
                'descriptions': [
                    'Stone coffins line the walls, their lids cracked and askew. The dead do not rest easy here.',
                    'Bones are piled in alcoves, sorted by type in macabre organization.',
                    'Faded frescoes of death and mourning cover the walls. Candles burn with unnatural flames.',
                    'The air is cold and still. You can almost hear whispers of those long departed.',
                    'Elaborate tombs bear the names of forgotten nobility. Dust covers everything.',
                    'Skeletal remains litter the floor. Whatever killed them still lurks nearby.'
                ]
            },
            'cave': {
                'titles': [
                    'Natural Cavern', 'Limestone Grotto', 'Underground Lake', 'Stalactite Chamber',
                    'Crystal Formation', 'Narrow Passage', 'Echo Chamber', 'Bat Roost',
                    'Flowstone Hall', 'Fault Line', 'Cave Pool', 'Fungus Grove'
                ],
                'descriptions': [
                    'Stalactites and stalagmites create a forest of stone. Water drips constantly.',
                    'The cave walls are slick with moisture. Strange fungi glow faintly in the darkness.',
                    'The passage narrows here, forcing you to squeeze through gaps in the rock.',
                    'A underground stream rushes past, its source and destination unknown.',
                    'The cave opens into a vast chamber. Bats screech overhead.',
                    'Crystals embedded in the walls catch what little light you have, sparkling mysteriously.'
                ]
            },
            'ruins': {
                'titles': [
                    'Ruined Hall', 'Collapsed Temple', 'Ancient Library', 'Throne Room',
                    'Armory', 'Fallen Tower', 'Statue Garden', 'Royal Vault',
                    'Forgotten Archive', 'Shattered Dome', 'Courtyard', 'Ceremonial Chamber'
                ],
                'descriptions': [
                    'Crumbling stonework and fallen pillars show the grandeur that once was.',
                    'Faded tapestries hang in tatters. Furniture has rotted to dust.',
                    'Shelves that once held countless books now hold only decay and cobwebs.',
                    'Broken statues watch over the room with vacant eyes. Rubble covers the floor.',
                    'The ceiling has partially collapsed, letting in shafts of dim light from above.',
                    'Intricate mosaics on the floor are barely visible under centuries of grime.'
                ]
            },
            'sewer': {
                'titles': [
                    'Main Sluice', 'Drainage Tunnel', 'Waste Channel', 'Junction Pool',
                    'Overflow Chamber', 'Filter Room', 'Pump Station', 'Cistern',
                    'Grate Chamber', 'Pipe Maze', 'Settling Pool', 'Access Shaft'
                ],
                'descriptions': [
                    'The stench is overwhelming. Dark water flows sluggishly through channels.',
                    'Slime covers every surface. You can hear rats skittering in the darkness.',
                    'Iron pipes run along the walls, some corroded and dripping foul liquid.',
                    'A deep pool of stagnant water blocks part of the passage. Who knows what lurks within?',
                    'The walls are carved with ancient drainage runes. They no longer function.',
                    'A rusted grate bars further passage. Something large has forced it open from the other side.'
                ]
            }
        }

    def generate(self, config: DungeonConfig) -> Dict:
        """
        Generate a complete dungeon from configuration

        Args:
            config: DungeonConfig instance

        Returns:
            Dictionary representing dungeon (compatible with JSON format)
        """
        # Set random seed if provided (for reproducible dungeons)
        if config.seed is not None:
            self.rng.seed(config.seed)
        else:
            self.rng.seed()

        # Generate dungeon name
        dungeon_name = self._generate_name(config)

        # Generate room layout graph
        room_graph = self._generate_room_graph(config)

        # Create room data structures
        rooms = self._create_rooms(room_graph, config)

        # Populate encounters (combat, traps)
        self._populate_encounters(rooms, config)

        # Place treasures and items
        self._place_treasures(rooms, config)

        # Designate safe rest rooms
        self._designate_safe_rooms(rooms, config)

        # Add flavor descriptions
        self._add_descriptions(rooms, config)

        # Add boss encounter if configured
        if config.include_boss:
            self._add_boss_encounter(rooms, config)

        return {
            'name': dungeon_name,
            'start_room': 'room_001',
            'rooms': rooms,
            'generated': True,
            'seed': config.seed,
            'config': {
                'party_level': config.party_level,
                'num_rooms': config.num_rooms,
                'layout_type': config.layout_type
            }
        }

    def _generate_name(self, config: DungeonConfig) -> str:
        """Generate a dungeon name based on theme"""
        theme = config.dungeon_theme

        prefixes = {
            'mine': ['The Abandoned', 'The Lost', 'The Dark', 'The Cursed', 'The Forgotten'],
            'crypt': ['The Ancient', 'The Haunted', 'The Forsaken', 'The Sealed', 'The Defiled'],
            'cave': ['The Deep', 'The Twisting', 'The Echo', 'The Crystal', 'The Hidden'],
            'ruins': ['The Fallen', 'The Shattered', 'The Broken', 'The Sunken', 'The Lost'],
            'sewer': ['The Fetid', 'The Dark', 'The Flooded', 'The Abandoned', 'The Ancient']
        }

        nouns = {
            'mine': ['Mine', 'Shaft', 'Excavation', 'Quarry', 'Pit'],
            'crypt': ['Crypt', 'Tomb', 'Catacomb', 'Sepulcher', 'Mausoleum'],
            'cave': ['Cave', 'Cavern', 'Grotto', 'Den', 'Hollow'],
            'ruins': ['Ruins', 'Temple', 'Fortress', 'Palace', 'Keep'],
            'sewer': ['Sewer', 'Cistern', 'Aqueduct', 'Drains', 'Underworks']
        }

        prefix = self.rng.choice(prefixes.get(theme, prefixes['mine']))
        noun = self.rng.choice(nouns.get(theme, nouns['mine']))

        return f"{prefix} {noun}"

    def _generate_room_graph(self, config: DungeonConfig) -> Dict[str, Set[str]]:
        """
        Generate room connectivity graph

        Returns:
            Dict mapping room IDs to set of connected room IDs
        """
        if config.layout_type == 'linear':
            return self._generate_linear_layout(config.num_rooms)
        elif config.layout_type == 'branching':
            return self._generate_branching_layout(config)
        elif config.layout_type == 'network':
            return self._generate_network_layout(config)
        else:
            return self._generate_linear_layout(config.num_rooms)

    def _generate_linear_layout(self, num_rooms: int) -> Dict[str, Set[str]]:
        """Generate simple linear path of rooms"""
        graph = {}

        for i in range(1, num_rooms + 1):
            room_id = f"room_{i:03d}"
            connections = set()

            # Connect to previous room
            if i > 1:
                connections.add(f"room_{i-1:03d}")

            # Connect to next room
            if i < num_rooms:
                connections.add(f"room_{i+1:03d}")

            graph[room_id] = connections

        return graph

    def _generate_branching_layout(self, config: DungeonConfig) -> Dict[str, Set[str]]:
        """Generate dungeon with branches and dead ends"""
        graph = {}
        num_rooms = config.num_rooms
        dead_ends = min(config.dead_ends, num_rooms // 3)

        # Start with main path (about 60% of rooms)
        main_path_length = max(3, int(num_rooms * 0.6))
        remaining_rooms = num_rooms - main_path_length

        # Build main path
        for i in range(1, main_path_length + 1):
            room_id = f"room_{i:03d}"
            connections = set()

            if i > 1:
                connections.add(f"room_{i-1:03d}")
            if i < main_path_length:
                connections.add(f"room_{i+1:03d}")

            graph[room_id] = connections

        # Add branches from main path
        room_counter = main_path_length + 1
        branch_points = self.rng.sample(range(2, main_path_length), min(dead_ends, main_path_length - 2))

        for branch_point in branch_points:
            if room_counter > num_rooms:
                break

            # Create short branch (1-3 rooms)
            branch_length = min(self.rng.randint(1, 3), num_rooms - room_counter + 1)

            parent_id = f"room_{branch_point:03d}"

            for j in range(branch_length):
                if room_counter > num_rooms:
                    break

                branch_room_id = f"room_{room_counter:03d}"
                room_counter += 1

                if j == 0:
                    # Connect to main path
                    graph[branch_room_id] = {parent_id}
                    graph[parent_id].add(branch_room_id)
                else:
                    # Connect to previous branch room
                    prev_branch_id = f"room_{room_counter-2:03d}"
                    graph[branch_room_id] = {prev_branch_id}
                    graph[prev_branch_id].add(branch_room_id)

        return graph

    def _generate_network_layout(self, config: DungeonConfig) -> Dict[str, Set[str]]:
        """Generate complex network with loops"""
        # Start with branching layout
        graph = self._generate_branching_layout(config)

        # Add loops by connecting distant rooms
        room_ids = list(graph.keys())
        loops_to_add = min(config.loops, len(room_ids) // 4)

        for _ in range(loops_to_add):
            # Pick two rooms that aren't already connected
            attempts = 0
            while attempts < 20:
                room1 = self.rng.choice(room_ids)
                room2 = self.rng.choice(room_ids)

                if room1 != room2 and room2 not in graph[room1]:
                    # Avoid connecting adjacent rooms in sequence
                    num1 = int(room1.split('_')[1])
                    num2 = int(room2.split('_')[1])

                    if abs(num1 - num2) > 2:
                        graph[room1].add(room2)
                        graph[room2].add(room1)
                        break

                attempts += 1

        return graph

    def _create_rooms(self, room_graph: Dict[str, Set[str]], config: DungeonConfig) -> Dict:
        """Create room data structures from graph"""
        rooms = {}
        theme = config.dungeon_theme

        # Initialize all rooms with empty exits
        for room_id in room_graph.keys():
            rooms[room_id] = {
                'id': room_id,
                'title': 'Unexplored Chamber',  # Will be replaced
                'description': '',  # Will be filled in later
                'light_level': 'dark',
                'exits': {},
                'encounters': [],
                'items': [],
                'safe_rest': False
            }

        # Assign bidirectional exits
        self._assign_bidirectional_exits(rooms, room_graph)

        # Add starting items to first room
        if config.starting_items:
            rooms['room_001']['items'] = config.starting_items.copy()
            rooms['room_001']['light_level'] = 'dim'

        return rooms

    def _assign_bidirectional_exits(self, rooms: Dict, room_graph: Dict[str, Set[str]]):
        """
        Assign bidirectional exits ensuring spatial consistency

        If room A has "east -> room B", then room B has "west -> room A"
        """
        # Track which room pairs we've already processed
        processed_pairs = set()

        # Track available directions for each room
        available_dirs = {room_id: ['north', 'south', 'east', 'west']
                         for room_id in room_graph.keys()}

        # Direction opposites
        opposites = {
            'north': 'south',
            'south': 'north',
            'east': 'west',
            'west': 'east'
        }

        # Sort rooms by number for consistent ordering
        sorted_rooms = sorted(room_graph.keys(), key=lambda r: int(r.split('_')[1]))

        for room_id in sorted_rooms:
            room_num = int(room_id.split('_')[1])

            for connected_id in room_graph[room_id]:
                # Create a canonical pair identifier (always smaller room first)
                pair = tuple(sorted([room_id, connected_id],
                                   key=lambda r: int(r.split('_')[1])))

                if pair in processed_pairs:
                    continue

                processed_pairs.add(pair)

                # Determine direction based on room numbering
                conn_num = int(connected_id.split('_')[1])

                # Choose direction for the connection
                direction = None

                if conn_num < room_num:
                    # Connected room has lower number - prefer south or west from current
                    if 'south' in available_dirs[room_id] and 'north' in available_dirs[connected_id]:
                        direction = 'south'
                    elif 'west' in available_dirs[room_id] and 'east' in available_dirs[connected_id]:
                        direction = 'west'
                else:
                    # Connected room has higher number - prefer north or east from current
                    if 'north' in available_dirs[room_id] and 'south' in available_dirs[connected_id]:
                        direction = 'north'
                    elif 'east' in available_dirs[room_id] and 'west' in available_dirs[connected_id]:
                        direction = 'east'

                # If preferred direction not available, use any available pair
                if not direction:
                    for dir1 in available_dirs[room_id]:
                        dir2 = opposites[dir1]
                        if dir2 in available_dirs[connected_id]:
                            direction = dir1
                            break

                if direction:
                    opposite_dir = opposites[direction]

                    # Assign bidirectional exits
                    rooms[room_id]['exits'][direction] = connected_id
                    rooms[connected_id]['exits'][opposite_dir] = room_id

                    # Mark directions as used
                    available_dirs[room_id].remove(direction)
                    available_dirs[connected_id].remove(opposite_dir)

    def _populate_encounters(self, rooms: Dict, config: DungeonConfig):
        """Add encounters (combat, traps) to rooms"""
        # Skip first room (entrance)
        eligible_rooms = [r for r in rooms.keys() if r != 'room_001']

        # Calculate number of each encounter type
        num_combat = int(len(eligible_rooms) * config.combat_frequency)
        num_traps = int(len(eligible_rooms) * config.trap_frequency)

        # Shuffle rooms for random placement
        self.rng.shuffle(eligible_rooms)

        # Place combat encounters
        for i in range(num_combat):
            if i >= len(eligible_rooms):
                break

            room_id = eligible_rooms[i]
            encounter = self._create_combat_encounter(config)
            rooms[room_id]['encounters'].append(encounter)

        # Place traps
        trap_start = num_combat
        for i in range(trap_start, trap_start + num_traps):
            if i >= len(eligible_rooms):
                break

            room_id = eligible_rooms[i]

            # Don't add trap if room already has combat
            if not rooms[room_id]['encounters']:
                encounter = self._create_trap_encounter(config)
                rooms[room_id]['encounters'].append(encounter)

    def _create_combat_encounter(self, config: DungeonConfig) -> Dict:
        """Create a combat encounter appropriate for party level"""
        num_monsters = self.rng.randint(1, 4)

        # Adjust for lethality
        if config.lethality_factor > 1.2:
            num_monsters += 1
        elif config.lethality_factor < 0.8:
            num_monsters = max(1, num_monsters - 1)

        # Filter monster pool by dungeon environment (DMG Appendix C)
        # This prevents inappropriate encounters like sprites or dolphins in dungeons
        context = EnvironmentContext(
            location_type='dungeon',
            dungeon_level=config.party_level  # Use party level as dungeon depth approximation
        )

        # Get environment-appropriate monsters
        filtered_pool = self.environment_filter.get_appropriate_monsters(
            context,
            monster_pool=config.monster_pool
        )

        # Fall back to full pool if filtering removed everything
        if not filtered_pool:
            filtered_pool = config.monster_pool

        # Select monsters from filtered pool
        monsters = [self.rng.choice(filtered_pool) for _ in range(num_monsters)]

        return {
            'type': 'combat',
            'monsters': monsters,
            'trigger': 'on_enter'
        }

    def _create_trap_encounter(self, config: DungeonConfig) -> Dict:
        """Create a trap encounter"""
        trap_types = ['pit', 'dart', 'poison_needle']
        trap_type = self.rng.choice(trap_types)

        damage_dice = {
            'pit': '1d6',
            'dart': '1d4',
            'poison_needle': '1d3'
        }

        difficulty = 10 + (config.party_level * 5) + int(self.rng.gauss(0, 5))
        difficulty = max(10, min(40, difficulty))  # Clamp 10-40

        return {
            'type': 'trap',
            'trap_type': trap_type,
            'damage': damage_dice[trap_type],
            'detect_difficulty': difficulty,
            'trigger': 'on_search'
        }

    def _place_treasures(self, rooms: Dict, config: DungeonConfig):
        """Place treasures and items in rooms"""
        eligible_rooms = [r for r in rooms.keys() if r != 'room_001']
        num_treasure_rooms = int(len(eligible_rooms) * config.treasure_frequency)

        # Select random rooms for treasure
        treasure_rooms = self.rng.sample(eligible_rooms, min(num_treasure_rooms, len(eligible_rooms)))

        for room_id in treasure_rooms:
            items = self._generate_treasure(config)
            rooms[room_id]['items'].extend(items)

        # Add guaranteed items
        if config.guaranteed_items:
            # Spread them across random rooms
            for item in config.guaranteed_items:
                room_id = self.rng.choice(eligible_rooms)
                rooms[room_id]['items'].append(item)

    def _generate_treasure(self, config: DungeonConfig) -> List[str]:
        """Generate treasure items based on level"""
        items = []

        # Basic items (rations, rope, etc.)
        basic_items = ['rations', 'rope_50ft', 'torch']
        if self.rng.random() < 0.3:
            items.append(self.rng.choice(basic_items))

        # Weapons/armor (based on treasure level)
        if self.rng.random() < 0.4:
            if config.treasure_level == 'low':
                items.append(self.rng.choice(['dagger', 'shortsword', 'leather_armor']))
            elif config.treasure_level == 'medium':
                items.append(self.rng.choice(['longsword', 'mace', 'chain_mail', 'shield']))
            else:  # high
                items.append(self.rng.choice(['longsword', 'plate_mail', 'shield']))

        # Magic items (rare)
        if self.rng.random() < config.magic_item_chance:
            magic_items = ['longsword_plus1', 'shortsword_plus1', 'dagger_plus1',
                          'chain_mail_plus1', 'shield_plus1', 'potion_healing']
            items.append(self.rng.choice(magic_items))

        return items

    def _designate_safe_rooms(self, rooms: Dict, config: DungeonConfig):
        """Mark some rooms as safe for resting"""
        eligible_rooms = [r for r in rooms.keys() if not rooms[r]['encounters']]

        if len(eligible_rooms) < config.safe_rooms:
            # Not enough empty rooms, so make some rooms safe after clearing
            eligible_rooms = list(rooms.keys())

        safe_rooms = self.rng.sample(eligible_rooms, min(config.safe_rooms, len(eligible_rooms)))

        for room_id in safe_rooms:
            rooms[room_id]['safe_rest'] = True

    def _add_descriptions(self, rooms: Dict, config: DungeonConfig):
        """Add thematic titles and descriptions to rooms"""
        theme = config.dungeon_theme
        theme_data = self.themes.get(theme, self.themes['mine'])

        titles = theme_data['titles'].copy()
        descriptions = theme_data['descriptions'].copy()

        self.rng.shuffle(titles)
        self.rng.shuffle(descriptions)

        for i, room_id in enumerate(sorted(rooms.keys())):
            # First room gets special treatment
            if room_id == 'room_001':
                rooms[room_id]['title'] = f"{theme.capitalize()} Entrance"

                if self.use_narrator and self.narrator:
                    # Use DMNarrator for atmospheric entrance description
                    context = NarrativeContext(
                        location_type="dungeon",
                        atmosphere=[theme, "dark", "ancient"],
                        light_level="torch"
                    )
                    base_desc = self.narrator.describe_room_entrance(
                        room_type=f"{theme} entrance",
                        size="",
                        primary_features=[self.rng.choice(descriptions)],
                        context=context
                    )
                    rooms[room_id]['description'] = base_desc
                else:
                    # Fall back to original simple description
                    rooms[room_id]['description'] = f"The entrance to a dark {theme}. " + \
                        self.rng.choice(descriptions)
            else:
                rooms[room_id]['title'] = titles[i % len(titles)]

                if self.use_narrator and self.narrator:
                    # Use DMNarrator for atmospheric room descriptions
                    # Determine room size from title
                    title_lower = titles[i % len(titles)].lower()
                    if any(word in title_lower for word in ['vast', 'huge', 'grand']):
                        size = "vast"
                    elif any(word in title_lower for word in ['large', 'great']):
                        size = "large"
                    else:
                        size = ""

                    # Determine atmosphere
                    atmosphere = [theme]
                    if 'abandoned' in title_lower or 'ruined' in title_lower:
                        atmosphere.append('abandoned')
                    if 'dark' in title_lower or 'shadow' in title_lower:
                        atmosphere.append('dark')
                    if 'ancient' in title_lower or 'old' in title_lower:
                        atmosphere.append('ancient')

                    context = NarrativeContext(
                        location_type="dungeon",
                        atmosphere=atmosphere,
                        light_level="torch"
                    )

                    # Extract room type from title
                    room_type = titles[i % len(titles)].lower()

                    rooms[room_id]['description'] = self.narrator.describe_room_entrance(
                        room_type=room_type,
                        size=size,
                        primary_features=[descriptions[i % len(descriptions)]],
                        context=context
                    )
                else:
                    # Fall back to original simple description
                    rooms[room_id]['description'] = descriptions[i % len(descriptions)]

                # Add encounter hints
                if rooms[room_id]['encounters']:
                    encounter = rooms[room_id]['encounters'][0]
                    if encounter['type'] == 'combat':
                        rooms[room_id]['description'] += self._add_monster_hint(encounter['monsters'])

    def _add_monster_hint(self, monsters: List[str]) -> str:
        """Add subtle hint about monsters in description"""
        monster_type = monsters[0]

        hints = {
            'kobold': ' You hear high-pitched chattering echoing from within.',
            'goblin': ' The stench of goblin habitation is unmistakable.',
            'orc': ' Guttural snoring echoes through the chamber.',
            'skeleton': ' The air grows cold, and you sense something unnatural ahead.',
            'giant_rat': ' You hear scratching and squeaking from the darkness.',
            'ogre': ' Heavy footsteps and a foul stench warn of something massive ahead.'
        }

        return hints.get(monster_type, ' Something dangerous lurks within.')

    def _add_boss_encounter(self, rooms: Dict, config: DungeonConfig):
        """Add a boss encounter to the final room"""
        final_room = sorted(rooms.keys())[-1]

        # Select boss monster
        if config.boss_monster:
            boss = config.boss_monster
        else:
            # Auto-select based on party level
            boss_options = {
                1: ['ogre', 'orc'],
                2: ['ogre', 'orc'],
                3: ['ogre']
            }
            boss = self.rng.choice(boss_options.get(config.party_level, ['ogre']))

        # Clear any existing encounters
        rooms[final_room]['encounters'] = [{
            'type': 'combat',
            'monsters': [boss],
            'trigger': 'on_enter',
            'boss': True
        }]

        # Add boss treasure
        treasure_gold = 100 * config.party_level
        treasure_gems = self.rng.randint(1, 5)

        magic_items_in_treasure = ['potion_healing']
        if self.rng.random() < 0.5:
            magic_items_in_treasure.append(self.rng.choice([
                'longsword_plus1', 'longsword_plus2', 'chain_mail_plus1',
                'plate_mail_plus1', 'shield_plus1'
            ]))

        rooms[final_room]['treasure'] = {
            'gold': treasure_gold,
            'gems': treasure_gems,
            'magic_items': magic_items_in_treasure
        }

        # Update description
        rooms[final_room]['description'] = (
            f"The final chamber of the {config.dungeon_theme}. "
            f"A massive {boss.upper()} guards a pile of glittering treasure! "
            "This is the master of this place, and a formidable foe."
        )
        rooms[final_room]['title'] = f"{boss.capitalize()} Lair"
