"""
Storage layer for persistent game data

Handles character rosters, parties, scenarios, and game sessions.
"""

from .character_roster import CharacterRoster
from .party_manager import PartyManager
from .scenario_library import ScenarioLibrary
from .session_manager import SessionManager

__all__ = [
    'CharacterRoster',
    'PartyManager',
    'ScenarioLibrary',
    'SessionManager'
]
