"""
Flask web UI for Aerthos - Gold Box style interface

Run with: python3 web_ui/app.py
Then visit: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify, session
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aerthos.world.dungeon import Dungeon
from aerthos.engine.game_state import GameState, GameData
from aerthos.entities.player import PlayerCharacter
from aerthos.entities.party import Party
from aerthos.ui.party_creation import PartyCreator
from aerthos.ui.character_creation import CharacterCreator
from aerthos.generator.dungeon_generator import DungeonGenerator
from aerthos.generator.config import DungeonConfig, STANDARD_DUNGEON
from aerthos.storage.character_roster import CharacterRoster
from aerthos.storage.party_manager import PartyManager
from aerthos.storage.scenario_library import ScenarioLibrary
from aerthos.storage.session_manager import SessionManager

app = Flask(__name__)
app.secret_key = 'aerthos_secret_key_change_in_production'

# Store active game sessions (in production, use proper session management)
active_games = {}


@app.route('/')
def index():
    """Main menu"""
    return render_template('index.html')


@app.route('/modern')
def modern():
    """Modern 2D interface with AD&D styling"""
    return render_template('modern.html')


@app.route('/game')
def game():
    """Game interface"""
    return render_template('game.html')


@app.route('/character_creation')
def character_creation():
    """Character creation interface"""
    return render_template('character_creation.html')


@app.route('/character_roster')
def character_roster():
    """Character roster management"""
    return render_template('character_roster.html')


@app.route('/party_manager')
def party_manager():
    """Party manager"""
    return render_template('party_builder.html')


@app.route('/scenario_library')
def scenario_library():
    """Scenario library"""
    return render_template('scenario_library.html')


@app.route('/session_manager')
def session_manager():
    """Session manager"""
    return render_template('session_manager.html')


@app.route('/api/new_game', methods=['POST'])
def new_game():
    """Start a new game"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')

        # For demo, create a simple party
        # In production, this would go through character creation
        game_data = GameData.load_all()

        # Create demo party
        from aerthos.ui.character_creation import CharacterCreator
        creator = CharacterCreator(game_data)

        # Quick character creation for demo
        player1 = creator.quick_create("Thorin", "Dwarf", "Fighter")
        player2 = creator.quick_create("Elara", "Elf", "Magic-User")
        player3 = creator.quick_create("Cedric", "Human", "Cleric")
        player4 = creator.quick_create("Shadow", "Halfling", "Thief")

        party = Party(members=[player1, player2, player3, player4])

        # Generate dungeon
        generator = DungeonGenerator(game_data)
        config = STANDARD_DUNGEON
        dungeon_data = generator.generate(config)
        dungeon = Dungeon.load_from_generator(dungeon_data)

        # Create game state
        game_state = GameState(party.members[0], dungeon)  # Use first member as main
        game_state.party = party  # Add party to game state
        game_state.load_game_data()

        # Store in session
        active_games[session_id] = game_state

        # Return initial state
        return jsonify({
            'success': True,
            'message': f"Welcome to {dungeon.name}!",
            'state': get_game_state_json(game_state)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/command', methods=['POST'])
def execute_command():
    """Execute a game command"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        command_text = data.get('command', '')
        active_character_index = data.get('active_character', 0)

        game_state = active_games.get(session_id)
        if not game_state:
            return jsonify({'success': False, 'error': 'No active game'})

        # Switch to the active character if party exists
        if hasattr(game_state, 'party') and game_state.party:
            if 0 <= active_character_index < len(game_state.party.members):
                game_state.player = game_state.party.members[active_character_index]

        # Parse and execute command
        from aerthos.engine.parser import CommandParser
        parser = CommandParser()
        command = parser.parse(command_text)

        result = game_state.execute_command(command)

        return jsonify({
            'success': True,
            'message': result.get('message', ''),
            'state': get_game_state_json(game_state),
            'active_character': active_character_index
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/game_state', methods=['POST'])
def get_game_state():
    """Get current game state for an active session"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')

        game_state = active_games.get(session_id)
        if not game_state:
            return jsonify({'success': False, 'error': 'No active game session found'})

        return jsonify({
            'success': True,
            'state': get_game_state_json(game_state)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


def get_game_state_json(game_state):
    """Convert game state to JSON for frontend"""

    party_data = []
    if hasattr(game_state, 'party'):
        for i, member in enumerate(game_state.party.members):
            # Get inventory items
            inventory_items = []
            if hasattr(member, 'inventory') and hasattr(member.inventory, 'items'):
                for item in member.inventory.items:
                    inventory_items.append({
                        'name': item.name,
                        'type': getattr(item, 'item_type', 'unknown'),
                        'weight': getattr(item, 'weight', 0)
                    })

            # Get equipped items
            equipped = {}
            if hasattr(member, 'equipment'):
                if member.equipment.weapon:
                    equipped['weapon'] = member.equipment.weapon.name
                if member.equipment.armor:
                    equipped['armor'] = member.equipment.armor.name
                if member.equipment.shield:
                    equipped['shield'] = member.equipment.shield.name
                if member.equipment.light_source:
                    equipped['light'] = member.equipment.light_source.name

            party_data.append({
                'name': member.name,
                'class': member.char_class,
                'race': member.race,
                'level': member.level,
                'hp': member.hp_current,
                'hp_max': member.hp_max,
                'ac': member.get_effective_ac(),
                'thac0': member.thac0,
                'xp': member.xp,
                'gold': member.gold,
                'is_alive': member.is_alive,
                'weight': member.inventory.current_weight,
                'weight_max': member.inventory.max_weight,
                'formation': game_state.party.formation[i] if i < len(game_state.party.formation) else 'front',
                'inventory': inventory_items,
                'equipped': equipped
            })

    # Get map data
    map_data = build_map_data(game_state)

    return {
        'room': {
            'id': game_state.current_room.id,
            'title': game_state.current_room.title,
            'description': game_state.current_room.description,
            'exits': game_state.current_room.exits,
            'light_level': game_state.current_room.light_level
        },
        'party': party_data,
        'in_combat': game_state.in_combat,
        'time': {
            'turns': game_state.time_tracker.turns_elapsed,
            'hours': game_state.time_tracker.total_hours
        },
        'map': map_data
    }


def build_map_data(game_state):
    """Build map data for 2D visualization with persistent coordinates"""

    # Build a graph of room connections with absolute positions
    # Always start from the dungeon start room for consistency
    explored = {}
    current_id = game_state.current_room.id
    start_room_id = game_state.dungeon.start_room_id

    room_positions = {}
    visited = set()

    def calculate_positions(room_id, x=0, y=0):
        """Recursively calculate room positions based on exits"""
        if room_id in visited or room_id not in game_state.dungeon.rooms:
            return

        visited.add(room_id)
        room = game_state.dungeon.rooms[room_id]

        # Store position for all rooms (explored or not)
        room_positions[room_id] = {'x': x, 'y': y, 'room': room}

        # Calculate neighbor positions based on cardinal directions
        direction_offsets = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0),
            'up': (0, -1),
            'down': (0, 1)
        }

        for direction, next_room_id in room.exits.items():
            if next_room_id not in visited:
                offset = direction_offsets.get(direction, (0, 0))
                calculate_positions(next_room_id, x + offset[0], y + offset[1])

    # Calculate positions starting from START room (for consistency)
    calculate_positions(start_room_id, 0, 0)

    # Collect explored rooms and unexplored adjacent rooms
    for room_id, pos_data in room_positions.items():
        if pos_data['room'].is_explored:
            explored[room_id] = {
                'id': room_id,
                'title': pos_data['room'].title,
                'x': pos_data['x'],
                'y': pos_data['y'],
                'exits': pos_data['room'].exits,
                'is_current': room_id == current_id,
                'is_explored': True
            }

    # Add unexplored but known rooms (exits from explored rooms)
    direction_offsets = {
        'north': (0, -1),
        'south': (0, 1),
        'east': (1, 0),
        'west': (-1, 0),
        'up': (0, -1),
        'down': (0, 1)
    }

    for room_id, room_data in list(explored.items()):
        room = game_state.dungeon.rooms[room_id]
        for direction, next_room_id in room.exits.items():
            # If the connected room exists but is not explored, add it as unknown
            if next_room_id in room_positions and next_room_id not in explored:
                offset = direction_offsets.get(direction, (0, 0))
                explored[next_room_id] = {
                    'id': next_room_id,
                    'title': '???',
                    'x': room_data['x'] + offset[0],
                    'y': room_data['y'] + offset[1],
                    'exits': {},
                    'is_current': False,
                    'is_explored': False
                }

    return {
        'rooms': explored,
        'current_room_id': current_id
    }


# ============================================================================
# Character Roster API Endpoints
# ============================================================================

@app.route('/api/characters', methods=['GET'])
def get_characters():
    """Get all characters from roster"""
    try:
        roster = CharacterRoster()
        characters = roster.list_characters()
        return jsonify({'success': True, 'characters': characters})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/characters', methods=['POST'])
def create_character():
    """Create a new character"""
    try:
        data = request.json

        # Validate input
        name = data.get('name')
        race = data.get('race')
        char_class = data.get('char_class')

        if not name or not race or not char_class:
            return jsonify({'success': False, 'error': 'Name, race, and class are required'})

        # Validate race and class are implemented
        valid_races = ['Human', 'Elf', 'Dwarf', 'Halfling']
        valid_classes = ['Fighter', 'Cleric', 'Magic-User', 'Thief']

        if race not in valid_races:
            return jsonify({'success': False, 'error': f'Race "{race}" not implemented. Available: {", ".join(valid_races)}'})

        if char_class not in valid_classes:
            return jsonify({'success': False, 'error': f'Class "{char_class}" not implemented. Available: {", ".join(valid_classes)}'})

        game_data = GameData.load_all()
        creator = CharacterCreator(game_data)

        # Quick create character
        character = creator.quick_create(name, race, char_class)

        # Save to roster
        roster = CharacterRoster()
        char_id = roster.save_character(character)

        return jsonify({'success': True, 'character_id': char_id})
    except KeyError as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Missing game data for: {str(e)}'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/characters/<char_id>', methods=['GET'])
def get_character(char_id):
    """Get a specific character"""
    try:
        roster = CharacterRoster()
        character = roster.load_character(char_id)

        if not character:
            return jsonify({'success': False, 'error': 'Character not found'})

        # Convert character to dict for JSON
        char_data = {
            'id': char_id,
            'name': character.name,
            'race': character.race,
            'class': character.char_class,
            'level': character.level,
            'xp': character.xp,
            'hp': f"{character.hp_current}/{character.hp_max}",
            'ac': character.get_effective_ac(),
            'thac0': character.thac0,
            'gold': character.gold,
            'weight': character.inventory.current_weight,
            'weight_max': character.inventory.max_weight
        }

        return jsonify({'success': True, 'character': char_data})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/characters/<char_id>', methods=['DELETE'])
def delete_character(char_id):
    """Delete a character"""
    try:
        roster = CharacterRoster()
        success = roster.delete_character(char_id)

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Character not found'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/character/get_races', methods=['POST'])
def get_available_races():
    """Get available races based on ability scores"""
    try:
        data = request.json
        stats = data.get('stats', {})

        game_data = GameData.load_all()
        from aerthos.ui.character_creation import CharacterCreator
        creator = CharacterCreator(game_data)

        races_info = []
        for race_name in ['Human', 'Elf', 'Dwarf', 'Halfling', 'Half-Elf', 'Half-Orc', 'Gnome']:
            if race_name not in game_data.races:
                continue

            race_data = game_data.races[race_name]
            is_available, reason = creator._check_race_requirements(
                race_name,
                stats.get('str', 0),
                stats.get('dex', 0),
                stats.get('con', 0),
                stats.get('int', 0),
                stats.get('wis', 0),
                stats.get('cha', 0)
            )

            mods = race_data.get('ability_modifiers', {})
            mod_str = creator._format_ability_modifiers(mods)

            races_info.append({
                'name': race_name,
                'description': race_data.get('description', ''),
                'modifiers': mod_str,
                'available': is_available,
                'reason': reason
            })

        return jsonify({'success': True, 'races': races_info})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/character/get_classes', methods=['POST'])
def get_available_classes():
    """Get available classes based on race and ability scores"""
    try:
        data = request.json
        stats = data.get('stats', {})
        race = data.get('race', 'Human')

        game_data = GameData.load_all()
        from aerthos.ui.character_creation import CharacterCreator
        creator = CharacterCreator(game_data)

        # Apply racial modifiers to stats
        race_data = game_data.races[race]
        modified_stats = stats.copy()
        for ability, modifier in race_data.get('ability_modifiers', {}).items():
            stat_key = ability[:3]  # str, dex, con, etc.
            if stat_key in modified_stats:
                modified_stats[stat_key] += modifier

        # Apply racial maximums
        maximums = race_data.get('ability_maximums', {})
        for ability, max_val in maximums.items():
            stat_key = ability[:3]
            if stat_key in modified_stats:
                modified_stats[stat_key] = min(modified_stats[stat_key], max_val)

        classes_info = []
        all_classes = ['Fighter', 'Ranger', 'Paladin', 'Cleric', 'Druid', 'Magic-User', 'Illusionist', 'Thief', 'Assassin', 'Monk', 'Bard']

        for class_name in all_classes:
            if class_name not in game_data.classes:
                continue

            is_available, reason = creator._check_class_requirements(
                class_name,
                race,
                modified_stats.get('str', 0),
                modified_stats.get('dex', 0),
                modified_stats.get('con', 0),
                modified_stats.get('int', 0),
                modified_stats.get('wis', 0),
                modified_stats.get('cha', 0)
            )

            class_data = game_data.classes[class_name]
            classes_info.append({
                'name': class_name,
                'description': class_data.get('description', ''),
                'available': is_available,
                'reason': reason
            })

        return jsonify({
            'success': True,
            'classes': classes_info,
            'stats_after_race': modified_stats
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/character/create', methods=['POST'])
def create_character_full():
    """Create a character with full stat rolling"""
    try:
        data = request.json
        name = data.get('name', 'Adventurer')
        race = data.get('race', 'Human')
        char_class = data.get('char_class', 'Fighter')
        base_stats = data.get('stats', {})

        game_data = GameData.load_all()
        from aerthos.ui.character_creation import CharacterCreator
        from aerthos.engine.combat import DiceRoller
        creator = CharacterCreator(game_data)

        # Get base stats
        strength = base_stats.get('str', 10)
        dexterity = base_stats.get('dex', 10)
        constitution = base_stats.get('con', 10)
        intelligence = base_stats.get('int', 10)
        wisdom = base_stats.get('wis', 10)
        charisma = base_stats.get('cha', 10)

        # Apply racial modifiers
        race_data = game_data.races[race]
        for ability, modifier in race_data.get('ability_modifiers', {}).items():
            if ability == 'strength':
                strength += modifier
            elif ability == 'dexterity':
                dexterity += modifier
            elif ability == 'constitution':
                constitution += modifier
            elif ability == 'intelligence':
                intelligence += modifier
            elif ability == 'wisdom':
                wisdom += modifier
            elif ability == 'charisma':
                charisma += modifier

        # Apply racial maximums
        maximums = race_data.get('ability_maximums', {})
        if 'strength' in maximums:
            strength = min(strength, maximums['strength'])
        if 'dexterity' in maximums:
            dexterity = min(dexterity, maximums['dexterity'])
        if 'constitution' in maximums:
            constitution = min(constitution, maximums['constitution'])
        if 'intelligence' in maximums:
            intelligence = min(intelligence, maximums['intelligence'])
        if 'wisdom' in maximums:
            wisdom = min(wisdom, maximums['wisdom'])
        if 'charisma' in maximums:
            charisma = min(charisma, maximums['charisma'])

        # Handle exceptional strength for Fighters
        strength_percentile = 0
        if char_class == 'Fighter' and strength == 18:
            import random
            strength_percentile = random.randint(1, 100)

        # Roll HP
        class_data = game_data.classes[char_class]
        hit_die = class_data['hit_die']
        hp = max(1, DiceRoller.roll(hit_die))

        # Apply CON bonus
        con_bonus = creator._get_con_bonus(constitution)
        hp = max(1, hp + con_bonus)

        # Get class-specific data
        saves = class_data['saves']
        thac0 = class_data['thac0_base']

        # Get XP needed for level 2
        from aerthos.entities.player import XP_TABLES
        xp_to_level_2 = XP_TABLES.get(char_class, [0, 2000])[1]

        # Create character
        player = PlayerCharacter(
            name=name,
            race=race,
            char_class=char_class,
            level=1,
            strength=strength,
            dexterity=dexterity,
            constitution=constitution,
            intelligence=intelligence,
            wisdom=wisdom,
            charisma=charisma,
            strength_percentile=strength_percentile,
            hp_current=hp,
            hp_max=hp,
            ac=10,
            thac0=thac0,
            save_poison=saves['poison'],
            save_rod_staff_wand=saves['rod_staff_wand'],
            save_petrify_paralyze=saves['petrify_paralyze'],
            save_breath=saves['breath'],
            save_spell=saves['spell'],
            xp=0,
            xp_to_next_level=xp_to_level_2
        )

        # Add starting equipment
        creator._add_starting_equipment(player, char_class)

        # Add skills for skill-based classes
        if char_class in ['Thief', 'Assassin', 'Bard']:
            player.thief_skills = class_data.get('skills', {}).copy()

        # Add spell slots if spellcaster
        if char_class in ['Magic-User', 'Illusionist', 'Cleric', 'Druid', 'Ranger', 'Paladin', 'Bard']:
            spell_slots_key = 'spell_slots_level_1'
            if spell_slots_key in class_data:
                num_slots = class_data[spell_slots_key][0]
                if num_slots > 0:
                    for _ in range(num_slots):
                        player.add_spell_slot(1)

        # Save character
        roster = CharacterRoster()
        char_id = roster.save_character(player)

        return jsonify({'success': True, 'character_id': char_id, 'name': name})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# Party Manager API Endpoints
# ============================================================================

@app.route('/api/parties', methods=['GET'])
def get_parties():
    """Get all parties"""
    try:
        party_mgr = PartyManager()
        parties = party_mgr.list_parties()
        return jsonify({'success': True, 'parties': parties})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/parties', methods=['POST'])
def create_party():
    """Create a new party"""
    try:
        data = request.json
        party_mgr = PartyManager()

        character_ids = data.get('character_ids', [])

        # Create default formation if not provided (2 rows)
        formation = data.get('formation')
        if not formation:
            # Default: put half in front row, half in back row
            mid = len(character_ids) // 2
            formation = ['front'] * mid + ['back'] * (len(character_ids) - mid)

        party_id = party_mgr.save_party(
            data.get('name'),
            character_ids,
            formation
        )

        return jsonify({'success': True, 'party_id': party_id})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/parties/<party_id>', methods=['DELETE'])
def delete_party(party_id):
    """Delete a party"""
    try:
        party_mgr = PartyManager()
        success = party_mgr.delete_party(party_id)

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Party not found'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# Scenario Library API Endpoints
# ============================================================================

@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    """Get all scenarios"""
    try:
        library = ScenarioLibrary()
        scenarios = library.list_scenarios()
        return jsonify({'success': True, 'scenarios': scenarios})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/scenarios', methods=['POST'])
def create_scenario():
    """Generate and save a new scenario"""
    try:
        data = request.json
        game_data = GameData.load_all()
        generator = DungeonGenerator(game_data)

        # Get parameters from request (with defaults)
        difficulty = data.get('difficulty', 'medium')
        layout_type = data.get('layout_type', 'branching')
        num_rooms = data.get('num_rooms', 12)
        combat_frequency = data.get('combat_frequency', 0.6)
        trap_frequency = data.get('trap_frequency', 0.2)
        dungeon_theme = data.get('dungeon_theme', 'mine')
        seed = data.get('seed', None)

        # Check if party information is provided
        party_id = data.get('party_id')
        party_level = data.get('party_level')
        party_size = data.get('party_size', 4)

        # If party_id is provided, load party and calculate level
        if party_id:
            try:
                party_mgr = PartyManager()
                party_data = party_mgr.load_party(party_id=party_id)
                if party_data:
                    # Get party object
                    party = party_data['party']
                    # Calculate average level from party members
                    from aerthos.generator.monster_scaling import MonsterScaler
                    scaler = MonsterScaler()
                    members_data = [{'level': m.level} for m in party.members]
                    party_level = scaler.calculate_party_level(members_data)
                    party_size = len(party.members)
            except Exception as e:
                print(f"Warning: Could not load party {party_id}: {e}")

        # If we have party level, use party-based scaling
        if party_level is not None:
            config = DungeonConfig.for_party(
                party_level=party_level,
                party_size=party_size,
                difficulty=difficulty if difficulty in ['easy', 'standard', 'hard'] else 'standard',
                num_rooms=num_rooms,
                layout_type=layout_type,
                dungeon_theme=dungeon_theme,
                seed=seed,
                combat_frequency=combat_frequency,
                trap_frequency=trap_frequency
            )
        else:
            # Fallback to old manual config
            # Determine party level and treasure based on difficulty
            if difficulty == 'easy':
                party_level = 1
                treasure_level = 'low'
                magic_item_chance = 0.05
            elif difficulty == 'hard':
                party_level = 3
                treasure_level = 'high'
                magic_item_chance = 0.2
            else:  # medium
                party_level = 2
                treasure_level = 'medium'
                magic_item_chance = 0.1

            # Create config with custom parameters
            config = DungeonConfig(
                num_rooms=num_rooms,
                layout_type=layout_type,
                combat_frequency=combat_frequency,
                trap_frequency=trap_frequency,
                party_level=party_level,
                treasure_level=treasure_level,
                magic_item_chance=magic_item_chance,
                dungeon_theme=dungeon_theme,
                seed=seed
            )

        # Generate dungeon (returns dict)
        dungeon_data = generator.generate(config)

        # Create Dungeon object to get metadata
        dungeon = Dungeon.load_from_generator(dungeon_data)

        # Save scenario with the generated data
        library = ScenarioLibrary()
        scenario_id = library.save_scenario_from_data(
            data.get('name'),
            data.get('description', ''),
            dungeon_data,
            dungeon.name,
            difficulty
        )

        return jsonify({'success': True, 'scenario_id': scenario_id})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/scenarios/<scenario_id>', methods=['DELETE'])
def delete_scenario(scenario_id):
    """Delete a scenario"""
    try:
        library = ScenarioLibrary()
        success = library.delete_scenario(scenario_id)

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Scenario not found'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# Session Manager API Endpoints
# ============================================================================

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get all sessions"""
    try:
        session_mgr = SessionManager()
        sessions = session_mgr.list_sessions()
        return jsonify({'success': True, 'sessions': sessions})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/sessions', methods=['POST'])
def create_session():
    """Create a new session"""
    try:
        data = request.json
        session_mgr = SessionManager()

        session_id = session_mgr.create_session(
            party_id=data.get('party_id'),
            scenario_id=data.get('scenario_id'),
            session_name=data.get('name')
        )

        return jsonify({'success': True, 'session_id': session_id})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a session"""
    try:
        session_mgr = SessionManager()
        success = session_mgr.delete_session(session_id)

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Session not found'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/sessions/<session_id>/load', methods=['POST'])
def load_session(session_id):
    """Load a game session for playing"""
    try:
        session_mgr = SessionManager()
        party_mgr = PartyManager()
        library = ScenarioLibrary()

        # Load session data
        session_data = session_mgr.load_session(session_id)
        if not session_data:
            return jsonify({'success': False, 'error': 'Session not found'})

        # Load party (returns dict with 'party' key containing Party object)
        party_data = party_mgr.load_party(party_id=session_data['party_id'])
        if not party_data:
            return jsonify({'success': False, 'error': 'Party not found'})
        party = party_data['party']

        # Load scenario
        scenario_data = library.load_scenario(session_data['scenario_id'])
        if not scenario_data:
            return jsonify({'success': False, 'error': 'Scenario not found'})

        # Create dungeon from scenario
        dungeon = library.create_dungeon_from_scenario(scenario_data)

        # Create game state
        game_state = GameState(party.members[0], dungeon)
        game_state.party = party
        game_state.load_game_data()

        # Restore session state if it exists
        if session_data.get('current_room_id'):
            game_state.current_room = dungeon.rooms.get(session_data['current_room_id'])

        # Store in active games
        web_session_id = 'session_' + session_id
        active_games[web_session_id] = game_state

        # Update session last played time (save_session_state expects game_state object)
        session_mgr.save_session_state(session_id, game_state)

        return jsonify({
            'success': True,
            'message': f"Resuming {session_data['name']}...",
            'state': get_game_state_json(game_state),
            'web_session_id': web_session_id
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# Modern UI API Endpoint Aliases
# ============================================================================

@app.route('/api/character/list', methods=['GET'])
def list_characters_modern():
    """Alias for /api/characters - used by modern UI"""
    return get_characters()


@app.route('/api/party/list', methods=['GET'])
def list_parties_modern():
    """Alias for /api/parties - used by modern UI"""
    return get_parties()


@app.route('/api/scenario/list', methods=['GET'])
def list_scenarios_modern():
    """Alias for /api/scenarios - used by modern UI"""
    return get_scenarios()


@app.route('/api/session/list', methods=['GET'])
def list_sessions_modern():
    """Alias for /api/sessions - used by modern UI"""
    return get_sessions()


@app.route('/api/party/create', methods=['POST'])
def create_party_modern():
    """Alias for /api/parties POST - used by modern UI"""
    return create_party()


@app.route('/api/scenario/create', methods=['POST'])
def create_scenario_modern():
    """Alias for /api/scenarios POST - used by modern UI"""
    return create_scenario()


@app.route('/api/session/create', methods=['POST'])
def create_session_modern():
    """Alias for /api/sessions POST - used by modern UI"""
    return create_session()


@app.route('/api/character/delete/<char_id>', methods=['POST'])
def delete_character_modern(char_id):
    """Alias for /api/characters/<char_id> DELETE - used by modern UI"""
    return delete_character(char_id)


@app.route('/api/session/<session_id>', methods=['GET'])
def get_session_state(session_id):
    """Get session state for gameplay - used by modern UI"""
    try:
        session_mgr = SessionManager()
        party_mgr = PartyManager()
        library = ScenarioLibrary()

        # Load session data
        session_data = session_mgr.load_session(session_id)
        if not session_data:
            return jsonify({'success': False, 'error': 'Session not found'})

        # Load party
        party_data = party_mgr.load_party(party_id=session_data['party_id'])
        if not party_data:
            return jsonify({'success': False, 'error': 'Party not found'})

        # Load scenario
        scenario_data = library.load_scenario(session_data['scenario_id'])
        if not scenario_data:
            return jsonify({'success': False, 'error': 'Scenario not found'})

        # Get party object
        party = party_data['party']

        # Convert party members to dict format
        members = []
        for member in party.members:
            members.append({
                'id': getattr(member, 'id', member.name),
                'name': member.name,
                'char_class': member.char_class,
                'level': member.level,
                'hp_current': member.hp_current,
                'hp_max': member.hp_max,
                'ac': member.ac,
                'thac0': member.thac0
            })

        # Create dungeon from scenario
        dungeon = library.create_dungeon_from_scenario(scenario_data)

        # Get current room ID
        current_room_id = session_data.get('current_room', 'room_001')
        current_room = dungeon.rooms.get(current_room_id)

        # Build room dict
        room_dict = {
            'id': current_room_id,
            'title': current_room.title,
            'description': current_room.description,
            'exits': current_room.exits,
            'light_level': current_room.light_level,
            'safe_rest': getattr(current_room, 'is_safe_for_rest', False)
        }

        # Build dungeon dict for map renderer
        dungeon_dict = {
            'name': dungeon.name,
            'start_room': 'room_001',
            'rooms': {}
        }

        for room_id, room in dungeon.rooms.items():
            dungeon_dict['rooms'][room_id] = {
                'id': room_id,
                'title': room.title,
                'description': room.description,
                'exits': room.exits,
                'light_level': room.light_level
            }

        return jsonify({
            'success': True,
            'session': {
                'id': session_id,
                'name': session_data.get('name', 'Adventure'),
                'party': {
                    'name': party_data.get('name', 'Adventurers'),
                    'members': members
                },
                'scenario_name': scenario_data.get('name', 'Dungeon'),
                'current_room_id': current_room_id,
                'current_room': room_dict,
                'dungeon': dungeon_dict,
                'explored_rooms': session_data.get('explored_rooms', [current_room_id])
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/session/<session_id>/move', methods=['POST'])
def move_in_dungeon(session_id):
    """Move to a new room in the dungeon - used by modern UI"""
    try:
        data = request.json
        direction = data.get('direction')

        session_mgr = SessionManager()
        library = ScenarioLibrary()

        # Load session
        session_data = session_mgr.load_session(session_id)
        if not session_data:
            return jsonify({'success': False, 'error': 'Session not found'})

        # Load scenario
        scenario_data = library.load_scenario(session_data['scenario_id'])
        dungeon = library.create_dungeon_from_scenario(scenario_data)

        # Get current and target rooms
        current_room_id = session_data.get('current_room', 'room_001')
        current_room = dungeon.rooms.get(current_room_id)

        if direction not in current_room.exits:
            return jsonify({'success': False, 'error': 'No exit in that direction'})

        target_room_id = current_room.exits[direction]
        target_room = dungeon.rooms.get(target_room_id)

        # Update session data
        session_data['current_room'] = target_room_id
        explored = session_data.get('explored_rooms', [current_room_id])
        if target_room_id not in explored:
            explored.append(target_room_id)
        session_data['explored_rooms'] = explored

        # Save updated session data back to file
        from pathlib import Path
        sessions_dir = Path.home() / '.aerthos' / 'sessions'
        filepath = sessions_dir / f"session_{session_id}.json"
        with open(filepath, 'w') as f:
            import json
            json.dump(session_data, f, indent=2)

        # Check for encounters from dungeon data
        encounter = None
        dungeon_data = scenario_data.get('dungeon_data', {})
        rooms_data = dungeon_data.get('rooms', {})
        target_room_data = rooms_data.get(target_room_id, {})

        encounters = target_room_data.get('encounters', [])
        if encounters and len(encounters) > 0:
            # Check if encounter hasn't been completed
            completed_encounters = session_data.get('completed_encounters', [])
            encounter_id = f"{target_room_id}_encounter_0"
            if encounter_id not in completed_encounters:
                encounter = encounters[0]
                encounter['encounter_id'] = encounter_id

        return jsonify({
            'success': True,
            'room_id': target_room_id,
            'room': {
                'id': target_room_id,
                'title': target_room.title,
                'description': target_room.description,
                'exits': target_room.exits,
                'light_level': target_room.light_level,
                'items': target_room_data.get('items', [])
            },
            'encounter': encounter
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/session/<session_id>/search', methods=['POST'])
def search_room(session_id):
    """Search current room for items and traps"""
    try:
        session_mgr = SessionManager()
        library = ScenarioLibrary()

        # Load session
        session_data = session_mgr.load_session(session_id)
        if not session_data:
            return jsonify({'success': False, 'error': 'Session not found'})

        # Load scenario
        scenario_data = library.load_scenario(session_data['scenario_id'])
        dungeon_data = scenario_data.get('dungeon_data', {})
        rooms_data = dungeon_data.get('rooms', {})

        current_room_id = session_data.get('current_room', 'room_001')
        room_data = rooms_data.get(current_room_id, {})

        # Get items in room
        items = room_data.get('items', [])
        searched_rooms = session_data.get('searched_rooms', [])

        message = ""
        found_items = []

        if current_room_id not in searched_rooms:
            # First time searching this room
            if items:
                found_items = items
                message = f"You search carefully and find: {', '.join(items)}"
            else:
                message = "You search the room thoroughly but find nothing of interest."

            searched_rooms.append(current_room_id)
            session_data['searched_rooms'] = searched_rooms

            # Save session
            from pathlib import Path
            sessions_dir = Path.home() / '.aerthos' / 'sessions'
            filepath = sessions_dir / f"session_{session_id}.json"
            with open(filepath, 'w') as f:
                import json
                json.dump(session_data, f, indent=2)
        else:
            message = "You've already searched this room thoroughly."

        return jsonify({
            'success': True,
            'message': message,
            'items': found_items
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/session/<session_id>/rest', methods=['POST'])
def rest_party(session_id):
    """Rest to recover HP and spells"""
    try:
        session_mgr = SessionManager()
        library = ScenarioLibrary()

        # Load session
        session_data = session_mgr.load_session(session_id)
        if not session_data:
            return jsonify({'success': False, 'error': 'Session not found'})

        # Load scenario
        scenario_data = library.load_scenario(session_data['scenario_id'])
        dungeon_data = scenario_data.get('dungeon_data', {})
        rooms_data = dungeon_data.get('rooms', {})

        current_room_id = session_data.get('current_room', 'room_001')
        room_data = rooms_data.get(current_room_id, {})

        # Check if room is safe
        is_safe = room_data.get('safe_rest', False)

        if not is_safe:
            # Random chance of being interrupted
            import random
            if random.random() < 0.3:  # 30% chance of encounter
                return jsonify({
                    'success': False,
                    'error': 'You were attacked while resting!',
                    'interrupted': True
                })

        # Restore party HP (simplified - restore 50% HP)
        message = "Your party rests. "
        if is_safe:
            message += "This seems like a safe place. You recover fully."
            hp_restored = "full"
        else:
            message += "You rest fitfully, recovering some strength."
            hp_restored = "half"

        return jsonify({
            'success': True,
            'message': message,
            'hp_restored': hp_restored
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/session/<session_id>/save', methods=['POST'])
def save_session_state(session_id):
    """Save current session state"""
    try:
        # Session is auto-saved on each action, so just confirm
        session_mgr = SessionManager()
        session_data = session_mgr.load_session(session_id)

        if not session_data:
            return jsonify({'success': False, 'error': 'Session not found'})

        # Update last saved timestamp
        from datetime import datetime
        session_data['last_saved'] = datetime.now().isoformat()

        from pathlib import Path
        sessions_dir = Path.home() / '.aerthos' / 'sessions'
        filepath = sessions_dir / f"session_{session_id}.json"
        with open(filepath, 'w') as f:
            import json
            json.dump(session_data, f, indent=2)

        return jsonify({'success': True, 'message': 'Game saved successfully'})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/session/<session_id>/party', methods=['GET'])
def get_party_details(session_id):
    """Get detailed party information including inventory and spells"""
    try:
        session_mgr = SessionManager()
        party_mgr = PartyManager()
        roster = CharacterRoster()

        # Load session data
        session_data = session_mgr.load_session(session_id)
        if not session_data:
            return jsonify({'success': False, 'error': 'Session not found'})

        # Load party
        party_data = party_mgr.load_party(party_id=session_data['party_id'])
        if not party_data:
            return jsonify({'success': False, 'error': 'Party not found'})

        party = party_data['party']

        # Get detailed character information
        members_detailed = []
        for member in party.members:
            # Try to load from roster to get full details
            char_id = getattr(member, 'id', None)

            member_dict = {
                'id': char_id or member.name,
                'name': member.name,
                'race': getattr(member, 'race', 'Human'),
                'char_class': member.char_class,
                'level': member.level,
                'xp': getattr(member, 'xp', 0),
                'hp_current': member.hp_current,
                'hp_max': member.hp_max,
                'ac': member.ac,
                'thac0': member.thac0,
                'strength': getattr(member, 'strength', 10),
                'dexterity': getattr(member, 'dexterity', 10),
                'constitution': getattr(member, 'constitution', 10),
                'intelligence': getattr(member, 'intelligence', 10),
                'wisdom': getattr(member, 'wisdom', 10),
                'charisma': getattr(member, 'charisma', 10),
                'gold': getattr(member, 'gold', 0),
                'inventory': [],
                'spells': []
            }

            # Get inventory
            if hasattr(member, 'inventory'):
                if hasattr(member.inventory, 'items'):
                    for item in member.inventory.items:
                        if isinstance(item, str):
                            member_dict['inventory'].append({'name': item, 'type': 'item'})
                        elif hasattr(item, 'name'):
                            member_dict['inventory'].append({
                                'name': item.name,
                                'type': getattr(item, 'item_type', 'item'),
                                'weight': getattr(item, 'weight', 0)
                            })
                        elif isinstance(item, dict):
                            member_dict['inventory'].append(item)

            # Get spells if character is a spellcaster
            if hasattr(member, 'spells') and member.spells:
                member_dict['spells'] = member.spells if isinstance(member.spells, list) else []

            members_detailed.append(member_dict)

        return jsonify({
            'success': True,
            'party': {
                'name': party_data.get('name', 'Adventurers'),
                'members': members_detailed
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    print("=" * 70)
    print("AERTHOS - Web Interface")
    print("=" * 70)
    print()
    print("Starting Flask server...")
    print("Visit: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()

    app.run(debug=True, host='0.0.0.0', port=5000)
