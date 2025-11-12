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
from aerthos.generator.dungeon_generator import DungeonGenerator
from aerthos.generator.config import DungeonConfig, STANDARD_DUNGEON

app = Flask(__name__)
app.secret_key = 'aerthos_secret_key_change_in_production'

# Store active game sessions (in production, use proper session management)
active_games = {}


@app.route('/')
def index():
    """Main game interface"""
    return render_template('game.html')


@app.route('/api/new_game', methods=['POST'])
def new_game():
    """Start a new game"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')

        # For demo, create a simple party
        # In production, this would go through character creation
        game_data = GameData()
        game_data.load_all()

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

        game_state = active_games.get(session_id)
        if not game_state:
            return jsonify({'success': False, 'error': 'No active game'})

        # Parse and execute command
        from aerthos.engine.parser import CommandParser
        parser = CommandParser()
        command = parser.parse(command_text)

        result = game_state.execute_command(command)

        return jsonify({
            'success': True,
            'message': result.get('message', ''),
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
                'formation': game_state.party.formation[i] if i < len(game_state.party.formation) else 'front'
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
    """Build map data for visualization"""

    explored = []
    for room_id, room in game_state.dungeon.rooms.items():
        if room.is_explored:
            explored.append({
                'id': room_id,
                'title': room.title,
                'exits': room.exits,
                'is_current': room_id == game_state.current_room.id
            })

    return {
        'explored_rooms': explored,
        'current_room_id': game_state.current_room.id
    }


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
