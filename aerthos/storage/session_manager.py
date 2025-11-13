"""
Session Manager - Active game session management

Manages active game sessions (party + scenario + current progress).
Extends the existing save system with party and scenario tracking.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from .character_roster import CharacterRoster
from .party_manager import PartyManager
from .scenario_library import ScenarioLibrary


class SessionManager:
    """Manages active game sessions"""

    def __init__(self, sessions_dir: str = None, character_roster_dir: str = None,
                 party_manager_dir: str = None, scenario_library_dir: str = None):
        if sessions_dir is None:
            self.sessions_dir = Path.home() / '.aerthos' / 'sessions'
        else:
            self.sessions_dir = Path(sessions_dir)

        # Create directory if it doesn't exist
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # Initialize managers with specified or default directories
        self.character_roster = CharacterRoster(roster_dir=character_roster_dir) if character_roster_dir else CharacterRoster()
        self.party_manager = PartyManager(parties_dir=party_manager_dir, character_roster=self.character_roster) if party_manager_dir else PartyManager()
        self.scenario_library = ScenarioLibrary(scenarios_dir=scenario_library_dir) if scenario_library_dir else ScenarioLibrary()

    def create_session(self, party_id: str, scenario_id: str,
                      session_name: str = None, session_id: str = None) -> str:
        """
        Create a new game session

        Args:
            party_id: ID of party to use
            scenario_id: ID of scenario to play
            session_name: Optional session name
            session_id: Optional ID (generates UUID if not provided)

        Returns:
            Session ID
        """
        if session_id is None:
            session_id = str(uuid.uuid4())[:8]

        # Load party and scenario to verify they exist
        party_data = self.party_manager.load_party(party_id=party_id)
        if not party_data:
            raise ValueError(f"Party {party_id} not found")

        scenario_data = self.scenario_library.load_scenario(scenario_id=scenario_id)
        if not scenario_data:
            raise ValueError(f"Scenario {scenario_id} not found")

        if session_name is None:
            session_name = f"{party_data['name']} - {scenario_data['name']}"

        session_data = {
            'id': session_id,
            'name': session_name,
            'created': datetime.now().isoformat(),
            'last_played': datetime.now().isoformat(),
            'party_id': party_id,
            'scenario_id': scenario_id,
            'turns_elapsed': 0,
            'total_hours': 0,
            'current_room_id': None,
            'is_active': True
        }

        filename = f"session_{session_id}.json"
        filepath = self.sessions_dir / filename

        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2)

        return session_id

    def save_session_state(self, session_id: str, game_state) -> bool:
        """
        Save current game state to a session

        Args:
            session_id: Session ID
            game_state: GameState instance

        Returns:
            True if saved successfully
        """
        filepath = self.sessions_dir / f"session_{session_id}.json"

        if not filepath.exists():
            return False

        with open(filepath, 'r') as f:
            session_data = json.load(f)

        # Update session data with current game state
        session_data['last_played'] = datetime.now().isoformat()
        session_data['turns_elapsed'] = game_state.time_tracker.turns_elapsed
        session_data['total_hours'] = game_state.time_tracker.total_hours
        session_data['current_room_id'] = game_state.current_room.id if game_state.current_room else None

        # Save party state (updated character stats, inventory, etc.)
        if hasattr(game_state, 'party') and game_state.party:
            session_data['party_state'] = self._serialize_party(game_state.party)
        elif hasattr(game_state, 'player'):
            # Single player - save as single member party
            session_data['player_state'] = self._serialize_character(game_state.player)

        # Save dungeon state (room exploration, monster defeats, loot taken)
        if hasattr(game_state, 'dungeon'):
            session_data['dungeon_state'] = game_state.dungeon.serialize()

        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2)

        return True

    def load_session(self, session_id: str) -> Optional[Dict]:
        """
        Load a session

        Args:
            session_id: Session ID to load

        Returns:
            Session data dictionary or None if not found
        """
        filepath = self.sessions_dir / f"session_{session_id}.json"

        if not filepath.exists():
            return None

        with open(filepath, 'r') as f:
            return json.load(f)

    def list_sessions(self) -> List[Dict]:
        """
        List all sessions

        Returns:
            List of session summary dictionaries
        """
        sessions = []

        for filepath in self.sessions_dir.glob('session_*.json'):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)

                    # Get party and scenario names
                    party_data = self.party_manager.load_party(party_id=data['party_id'])
                    scenario_data = self.scenario_library.load_scenario(scenario_id=data['scenario_id'])

                    sessions.append({
                        'id': data['id'],
                        'name': data['name'],
                        'party_name': party_data['name'] if party_data else 'Unknown',
                        'scenario_name': scenario_data['name'] if scenario_data else 'Unknown',
                        'created': data['created'],
                        'last_played': data['last_played'],
                        'turns_elapsed': data.get('turns_elapsed', 0),
                        'is_active': data.get('is_active', True)
                    })
            except Exception as e:
                print(f"Error loading {filepath}: {e}")

        return sorted(sessions, key=lambda s: s['last_played'], reverse=True)

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted, False if not found
        """
        filepath = self.sessions_dir / f"session_{session_id}.json"

        if filepath.exists():
            filepath.unlink()
            return True

        return False

    def _serialize_party(self, party) -> Dict:
        """Serialize party state"""
        members = []
        for member in party.members:
            members.append(self._serialize_character(member))

        return {
            'members': members,
            'formation': party.formation
        }

    def _serialize_character(self, character) -> Dict:
        """Serialize character state (simplified - just current stats)"""
        return {
            'name': character.name,
            'hp_current': character.hp_current,
            'xp': character.xp,
            'level': character.level,
            'gold': character.gold,
            'conditions': list(character.conditions)
        }
