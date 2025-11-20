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
            dungeon: Dungeon or MultiLevelDungeon instance to save
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

        # Check if this is a MultiLevelDungeon
        from aerthos.world.multilevel_dungeon import MultiLevelDungeon
        is_multilevel = isinstance(dungeon, MultiLevelDungeon)

        if is_multilevel:
            # Calculate total rooms across all levels
            num_rooms = sum(len(level.dungeon.rooms) for level in dungeon.levels.values())
            # Multi-level dungeons don't have a single start_room
            start_room = f"level_{dungeon.current_level_number}_start"
        else:
            # Regular dungeon
            num_rooms = len(dungeon.rooms)
            start_room = dungeon.start_room_id

        scenario_data = {
            'id': scenario_id,
            'name': scenario_name,
            'description': description,
            'difficulty': difficulty,
            'created': datetime.now().isoformat(),
            'dungeon_data': dungeon.to_dict(),  # Use to_dict() for full structure
            'num_rooms': num_rooms,
            'start_room': start_room,
            'is_multilevel': is_multilevel
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
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        if data['id'] == scenario_id:
                            return data
                except FileNotFoundError:
                    print(f"Warning: {filepath} not found (may have been deleted)")
                    continue
                except json.JSONDecodeError as e:
                    print(f"Error: {filepath} contains invalid JSON: {e}")
                    continue
                except (PermissionError, OSError) as e:
                    print(f"Error reading {filepath}: {e}")
                    continue

        if scenario_name:
            # Find by name
            for filepath in self.scenarios_dir.glob('*.json'):
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        if data['name'].lower() == scenario_name.lower():
                            return data
                except FileNotFoundError:
                    print(f"Warning: {filepath} not found (may have been deleted)")
                    continue
                except json.JSONDecodeError as e:
                    print(f"Error: {filepath} contains invalid JSON: {e}")
                    continue
                except (PermissionError, OSError) as e:
                    print(f"Error reading {filepath}: {e}")
                    continue

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
        found_path = None
        for filepath in self.scenarios_dir.glob('*.json'):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if data['id'] == scenario_id:
                        # Store path, delete after iteration
                        found_path = filepath
                        break
            except FileNotFoundError:
                print(f"Warning: {filepath} not found (may have been deleted)")
                continue
            except json.JSONDecodeError as e:
                print(f"Error: {filepath} contains invalid JSON: {e}")
                continue
            except (PermissionError, OSError) as e:
                print(f"Error reading {filepath}: {e}")
                continue

        if found_path:
            found_path.unlink()
            return True

        return False

    def create_dungeon_from_scenario(self, scenario_data):
        """
        Recreate a Dungeon or MultiLevelDungeon instance from saved scenario data

        Args:
            scenario_data: Either scenario ID (str) or scenario data dictionary (Dict)

        Returns:
            Dungeon or MultiLevelDungeon instance
        """
        from ..world.dungeon import Dungeon
        from ..world.multilevel_dungeon import MultiLevelDungeon

        # If scenario_data is a string, treat it as ID and load the scenario
        if isinstance(scenario_data, str):
            scenario_id = scenario_data
            scenario_data = self.load_scenario(scenario_id=scenario_id)
            if not scenario_data:
                raise ValueError(f"Scenario {scenario_id} not found")

        dungeon_data = scenario_data['dungeon_data']
        is_multilevel = scenario_data.get('is_multilevel', False)

        # Check if it's a multi-level dungeon
        if is_multilevel or ('levels' in dungeon_data and 'current_level' in dungeon_data):
            # Multi-level dungeon
            dungeon = MultiLevelDungeon.from_dict(dungeon_data)
        else:
            # Regular single-level dungeon
            dungeon = Dungeon.load_from_generator(dungeon_data)

        return dungeon

    def restore_dungeon_from_state(self, dungeon_state: dict):
        """
        Restore a Dungeon or MultiLevelDungeon from saved state

        Args:
            dungeon_state: Serialized dungeon state from session

        Returns:
            Dungeon or MultiLevelDungeon instance
        """
        from ..world.dungeon import Dungeon
        from ..world.multilevel_dungeon import MultiLevelDungeon

        # Detect if it's a multi-level dungeon by checking for 'levels' key
        if 'levels' in dungeon_state and 'current_level' in dungeon_state:
            # Multi-level dungeon - use deserialize() for serialize() format
            return MultiLevelDungeon.deserialize(dungeon_state)
        else:
            # Regular single-level dungeon
            return Dungeon.load_from_generator(dungeon_state)
