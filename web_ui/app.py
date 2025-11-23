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
    """
    Convert game state to JSON for frontend

    ⚠️ WARNING - WEB UI DEPENDENCY:
    The web UI (game.html) depends on this JSON structure.
    When adding fields: Safe - web UI will ignore unknown fields
    When removing/renaming fields: DANGEROUS - will break web UI!
    If you change this, update game.html JavaScript accordingly.
    """

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

            # PRIORITY 5: Get spell slots for spellcasters
            spell_slots = []
            if hasattr(member, 'spells_memorized'):
                for slot in member.spells_memorized:
                    spell_slot_data = {
                        'level': slot.level,
                        'is_used': slot.is_used,
                        'spell': None
                    }
                    if slot.spell:
                        spell_slot_data['spell'] = {
                            'name': slot.spell.name,
                            'level': slot.spell.level,
                            'school': getattr(slot.spell, 'school', 'unknown'),
                            'range': getattr(slot.spell, 'range', 'self'),
                            'description': getattr(slot.spell, 'description', '')
                        }
                    spell_slots.append(spell_slot_data)

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
                'equipped': equipped,
                'spell_slots': spell_slots  # NEW: For spell quick-cast bar
            })

    # Get map data
    map_data = build_map_data(game_state)

    # PRIORITY 1: Context-aware action bar data
    # Get items in current room (for "take" actions)
    room_items = []
    if hasattr(game_state.current_room, 'items'):
        room_items = game_state.current_room.items

    # Get active monsters (for "attack" actions)
    active_monsters = []
    if game_state.in_combat and hasattr(game_state, 'active_monsters'):
        for monster in game_state.active_monsters:
            if monster.is_alive:
                active_monsters.append({
                    'name': monster.name,
                    'hp': monster.hp_current,
                    'hp_max': monster.hp_max,
                    'status': 'wounded' if monster.hp_current < monster.hp_max * 0.5 else 'healthy'
                })

    # Get available spells for active character (for "cast" actions)
    available_spells = []
    if hasattr(game_state, 'party') and len(game_state.party.members) > 0:
        # Use first living member as "active" for spell suggestions
        # (In real gameplay, frontend tracks which character is active)
        for member in game_state.party.members:
            if member.is_alive and hasattr(member, 'spells_memorized'):
                for slot in member.spells_memorized:
                    if slot.spell and not slot.is_used:
                        available_spells.append({
                            'name': slot.spell.name,
                            'level': slot.spell.level,
                            'caster': member.name
                        })
                break  # Only get spells from first living caster

    return {
        'room': {
            'id': game_state.current_room.id,
            'title': game_state.current_room.title,
            'description': game_state.current_room.description,
            'exits': game_state.current_room.exits,
            'light_level': game_state.current_room.light_level,
            'items': room_items  # NEW: Items in room for context-aware actions
        },
        'party': party_data,
        'in_combat': game_state.in_combat,
        'active_monsters': active_monsters,  # NEW: Monsters for context-aware actions
        'available_spells': available_spells,  # NEW: Spells for context-aware actions
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
    for room_id, room_data in list(explored.items()):
        room = game_state.dungeon.rooms[room_id]
        for direction, next_room_id in room.exits.items():
            # If the connected room exists but is not explored, add it as unknown
            if next_room_id in room_positions and next_room_id not in explored:
                pos_data = room_positions[next_room_id]
                explored[next_room_id] = {
                    'id': next_room_id,
                    'title': '???',  # Hide title until explored
                    'x': pos_data['x'],  # Use pre-calculated position
                    'y': pos_data['y'],  # Use pre-calculated position
                    'exits': {},  # Don't reveal exits until explored
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
            'char_class': character.char_class,
            'alignment': character.alignment,
            'level': character.level,
            'xp': character.xp,
            'hp_current': character.hp_current,
            'hp_max': character.hp_max,
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


@app.route('/api/character/get_alignments', methods=['POST'])
def get_available_alignments():
    """Get available alignments for a class"""
    try:
        data = request.json
        char_class = data.get('char_class')

        if not char_class:
            return jsonify({'success': False, 'error': 'Class required'})

        # Load class data
        game_data = load_game_data()
        class_data = game_data.classes.get(char_class)

        if not class_data:
            return jsonify({'success': False, 'error': 'Invalid class'})

        # Get allowed alignments
        from aerthos.systems.alignment import get_allowed_alignments_for_class
        allowed_alignments = get_allowed_alignments_for_class(char_class, class_data)

        return jsonify({
            'success': True,
            'allowed_alignments': allowed_alignments
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
        alignment = data.get('alignment', 'True Neutral')
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

        # Validate alignment for class
        class_data = game_data.classes[char_class]
        from aerthos.systems.alignment import validate_class_alignment
        if not validate_class_alignment(char_class, alignment, class_data):
            return jsonify({
                'success': False,
                'error': f'{alignment} is not a valid alignment for {char_class}'
            })

        # Roll HP
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
            alignment=alignment,
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
    """
    Generate and save a new scenario

    Expected JSON parameters:
    - dungeon_type: '1' (fixed - not saveable), '2' (easy), '3' (standard), '4' (hard), '5' (custom)
    - party_level: Required for types 2-4 (default 1)
    - name: Scenario name
    - description: Scenario description

    For custom (type 5):
    - num_rooms: Rooms per level (5-30, default 12)
    - layout_type: 'linear', 'branching', 'network' (default 'branching')
    - num_levels: Number of levels (1-5, default 1)
    - dungeon_theme: 'mine', 'crypt', 'cave', 'ruins', 'sewer' (default 'mine')
    - seed: Optional seed for reproducibility
    - party_aware: Interview results dict with apl, party_size, composition, magic_level
    """
    try:
        data = request.json
        game_data = GameData.load_all()

        dungeon_type = data.get('dungeon_type', '3')  # Default to standard

        # Type 1 (fixed) cannot be saved
        if dungeon_type == '1':
            return jsonify({'success': False, 'error': 'Cannot save fixed starter dungeon'})

        generator = DungeonGenerator(game_data)
        config = None
        dungeon = None
        difficulty = 'medium'

        # Types 2-4: Preset dungeons (Easy/Standard/Hard)
        if dungeon_type in ['2', '3', '4']:
            from aerthos.generator.config import EASY_DUNGEON, STANDARD_DUNGEON, HARD_DUNGEON

            party_level = data.get('party_level', 1)

            if dungeon_type == '2':
                config = EASY_DUNGEON
                difficulty = 'easy'
            elif dungeon_type == '3':
                config = STANDARD_DUNGEON
                difficulty = 'medium'
            else:  # '4'
                config = HARD_DUNGEON
                difficulty = 'hard'

            # Update config with party level
            config.party_level = party_level

            # Generate single-level dungeon
            dungeon_data = generator.generate(config)
            dungeon = Dungeon.load_from_generator(dungeon_data)

        # Type 5: Custom (includes multi-level and party-aware)
        elif dungeon_type == '5':
            # Get custom parameters
            num_rooms = data.get('num_rooms', 12)
            layout_type = data.get('layout_type', 'branching')
            num_levels = data.get('num_levels', 1)
            dungeon_theme = data.get('dungeon_theme', 'mine')
            seed = data.get('seed', None)

            # Party-aware interview results
            party_aware = data.get('party_aware', {})
            apl = party_aware.get('apl', 1)
            party_size = party_aware.get('party_size', 4)
            composition = party_aware.get('composition', 'balanced')
            magic_level = party_aware.get('magic_level', 'low')

            # Create config from interview results
            interview_results = {
                'apl': apl,
                'party_size': party_size,
                'composition': composition,
                'magic_level': magic_level
            }
            config = DungeonConfig.from_interview(interview_results)

            # Apply custom settings
            config.seed = seed
            config.num_rooms = num_rooms
            config.layout_type = layout_type
            config.dungeon_theme = dungeon_theme

            # Generate dungeon name
            if num_levels > 1:
                dungeon_name = f"The {dungeon_theme.capitalize()} Depths"
            else:
                dungeon_name = f"The Abandoned {dungeon_theme.capitalize()}"

            # Multi-level or single-level?
            if num_levels > 1:
                from aerthos.generator.multilevel_generator import MultiLevelGenerator

                ml_generator = MultiLevelGenerator()
                dungeon = ml_generator.generate(
                    num_levels=num_levels,
                    rooms_per_level=config.num_rooms,
                    dungeon_name=dungeon_name
                )
                difficulty = 'multilevel_custom'
            else:
                dungeon_data = generator.generate(config)
                dungeon = Dungeon.load_from_generator(dungeon_data)
                difficulty = 'custom'

        # Save scenario
        library = ScenarioLibrary()
        scenario_name = data.get('name', dungeon.name)
        description = data.get('description', '')

        scenario_id = library.save_scenario(dungeon, scenario_name, description, difficulty)

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


@app.route('/api/sessions/solo', methods=['POST'])
def create_solo_session():
    """Create a solo character session (auto-creates party)"""
    try:
        data = request.json
        session_mgr = SessionManager()
        roster = CharacterRoster()

        character_id = data.get('character_id')
        scenario_id = data.get('scenario_id')
        session_name = data.get('name')

        if not character_id:
            return jsonify({'success': False, 'error': 'Character ID required'})
        if not scenario_id:
            return jsonify({'success': False, 'error': 'Scenario ID required'})

        # Load character to get name
        character = roster.load_character(character_id=character_id)
        if not character:
            return jsonify({'success': False, 'error': 'Character not found'})

        # Create a solo party automatically
        solo_party_name = f"Solo: {character.name}"
        party_id = session_mgr.party_manager.save_party(
            solo_party_name,
            [character_id],
            ['front']
        )

        # Generate session name if not provided
        if not session_name:
            scenario_data = session_mgr.scenario_library.load_scenario(scenario_id)
            scenario_name = scenario_data['name'] if scenario_data else 'Unknown'
            session_name = f"{character.name} - {scenario_name}"

        # Create session
        session_id = session_mgr.create_session(
            party_id=party_id,
            scenario_id=scenario_id,
            session_name=session_name
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
