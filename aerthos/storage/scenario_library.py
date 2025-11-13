"""
Scenario Library - Persistent dungeon/scenario storage

Manages saved dungeons and scenarios for replay.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict


class ScenarioLibrary:
    """Manages persistent scenario/dungeon storage"""

    def __init__(self, scenarios_dir: str = None):
        if scenarios_dir is None:
            self.scenarios_dir = Path.home() / '.aerthos' / 'scenarios'
        else:
            self.scenarios_dir = Path(scenarios_dir)

        # Create directory if it doesn't exist
        self.scenarios_dir.mkdir(parents=True, exist_ok=True)

    def save_scenario(self, dungeon, scenario_name: str = None,
                     description: str = "", difficulty: str = "medium",
                     scenario_id: str = None) -> str:
        """
        Save a dungeon/scenario

        Args:
            dungeon: Dungeon instance to save
            scenario_name: Optional name (uses dungeon.name if not provided)
            description: Optional description
            difficulty: Difficulty level (easy, medium, hard)
            scenario_id: Optional ID (generates UUID if not provided)

        Returns:
            Scenario ID
        """
        if scenario_id is None:
            scenario_id = str(uuid.uuid4())[:8]

        if scenario_name is None:
            scenario_name = dungeon.name

        scenario_data = {
            'id': scenario_id,
            'name': scenario_name,
            'description': description,
            'difficulty': difficulty,
            'created': datetime.now().isoformat(),
            'dungeon_data': dungeon.serialize(),
            'num_rooms': len(dungeon.rooms),
            'start_room': dungeon.start_room_id
        }

        filename = f"{scenario_name.lower().replace(' ', '_')}_{scenario_id}.json"
        filepath = self.scenarios_dir / filename

        with open(filepath, 'w') as f:
            json.dump(scenario_data, f, indent=2)

        return scenario_id

    def save_scenario_from_data(self, scenario_name: str, description: str, dungeon_data: dict,
                                 dungeon_name: str, difficulty: str = 'medium', scenario_id: str = None) -> str:
        """
        Save a scenario from dungeon data dict (from generator)

        Args:
            scenario_name: Name for the scenario
            description: Scenario description
            dungeon_data: Dungeon data dict from generator
            dungeon_name: Name of the dungeon
            difficulty: Difficulty level (easy, medium, hard)
            scenario_id: Optional ID (generates UUID if not provided)

        Returns:
            Scenario ID
        """
        if scenario_id is None:
            scenario_id = str(uuid.uuid4())[:8]

        if not scenario_name:
            scenario_name = dungeon_name

        # Count rooms from dungeon_data
        num_rooms = len(dungeon_data.get('rooms', {}))
        start_room = dungeon_data.get('start_room_id', 'room_0')

        scenario_data = {
            'id': scenario_id,
            'name': scenario_name,
            'description': description,
            'difficulty': difficulty,
            'created': datetime.now().isoformat(),
            'dungeon_data': dungeon_data,
            'num_rooms': num_rooms,
            'start_room': start_room
        }

        filename = f"{scenario_name.lower().replace(' ', '_')}_{scenario_id}.json"
        filepath = self.scenarios_dir / filename

        with open(filepath, 'w') as f:
            json.dump(scenario_data, f, indent=2)

        return scenario_id

    def load_scenario(self, scenario_id: str = None, scenario_name: str = None) -> Optional[Dict]:
        """
        Load a scenario

        Args:
            scenario_id: Scenario ID to load
            scenario_name: Or scenario name to load

        Returns:
            Scenario data dictionary or None if not found
        """
        if scenario_id:
            # Find by ID
            for filepath in self.scenarios_dir.glob('*.json'):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if data['id'] == scenario_id:
                        return data

        if scenario_name:
            # Find by name
            for filepath in self.scenarios_dir.glob('*.json'):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if data['name'].lower() == scenario_name.lower():
                        return data

        return None

    def list_scenarios(self) -> List[Dict]:
        """
        List all saved scenarios

        Returns:
            List of scenario summary dictionaries
        """
        scenarios = []

        for filepath in self.scenarios_dir.glob('*.json'):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    scenarios.append({
                        'id': data['id'],
                        'name': data['name'],
                        'description': data.get('description', ''),
                        'difficulty': data.get('difficulty', 'medium'),
                        'num_rooms': data.get('num_rooms', 0),
                        'created': data['created']
                    })
            except Exception as e:
                print(f"Error loading {filepath}: {e}")

        return sorted(scenarios, key=lambda s: s['name'])

    def delete_scenario(self, scenario_id: str) -> bool:
        """
        Delete a scenario

        Args:
            scenario_id: Scenario ID to delete

        Returns:
            True if deleted, False if not found
        """
        for filepath in self.scenarios_dir.glob('*.json'):
            with open(filepath, 'r') as f:
                data = json.load(f)
                if data['id'] == scenario_id:
                    filepath.unlink()
                    return True

        return False

    def create_dungeon_from_scenario(self, scenario_data: Dict):
        """
        Recreate a Dungeon instance from saved scenario data

        Args:
            scenario_data: Scenario data dictionary

        Returns:
            Dungeon instance
        """
        from ..world.dungeon import Dungeon

        dungeon_data = scenario_data['dungeon_data']

        # Use load_from_generator since we saved the generator output
        dungeon = Dungeon.load_from_generator(dungeon_data)

        return dungeon
