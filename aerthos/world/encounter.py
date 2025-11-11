"""
Encounter system - handles combat encounters, traps, and puzzles
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Encounter:
    """Base encounter class"""

    encounter_id: str
    encounter_type: str  # 'combat', 'trap', 'puzzle', 'treasure'
    is_active: bool = True
    trigger: str = 'on_enter'  # 'on_enter', 'on_search', 'manual'


@dataclass
class CombatEncounter(Encounter):
    """Combat encounter with monsters"""

    monster_ids: List[str] = field(default_factory=list)
    is_boss: bool = False

    def __post_init__(self):
        self.encounter_type = 'combat'


@dataclass
class TrapEncounter(Encounter):
    """Trap encounter"""

    trap_type: str = 'pit'  # 'pit', 'poison_needle', 'arrow', etc.
    damage: str = '1d6'
    detect_difficulty: int = 20  # Thief skill % penalty
    disarm_difficulty: int = 0   # Additional penalty to disarm

    def __post_init__(self):
        self.encounter_type = 'trap'


@dataclass
class PuzzleEncounter(Encounter):
    """Puzzle or locked container"""

    puzzle_type: str = 'locked_chest'
    difficulty: int = 30  # Base difficulty
    reward: Optional[str] = None  # Treasure or item ID

    def __post_init__(self):
        self.encounter_type = 'puzzle'


@dataclass
class TreasureEncounter(Encounter):
    """Simple treasure (not guarded)"""

    gold: int = 0
    gems: int = 0
    magic_items: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.encounter_type = 'treasure'


class EncounterManager:
    """Manages encounter resolution"""

    def __init__(self):
        self.active_encounters: Dict[str, Encounter] = {}

    def load_room_encounters(self, room_data: Dict) -> List[Encounter]:
        """
        Load encounters from room JSON data

        Args:
            room_data: Room dictionary from JSON

        Returns:
            List of Encounter objects
        """

        encounters = []

        if 'encounters' not in room_data:
            return encounters

        for i, enc_data in enumerate(room_data['encounters']):
            encounter_id = f"{room_data['id']}_encounter_{i}"
            enc_type = enc_data.get('type', 'combat')

            if enc_type == 'combat':
                encounter = CombatEncounter(
                    encounter_id=encounter_id,
                    encounter_type='combat',  # Required by parent class
                    monster_ids=enc_data.get('monsters', []),
                    is_boss=enc_data.get('boss', False),
                    trigger=enc_data.get('trigger', 'on_enter')
                )
            elif enc_type == 'trap':
                encounter = TrapEncounter(
                    encounter_id=encounter_id,
                    encounter_type='trap',  # Required by parent class
                    trap_type=enc_data.get('trap_type', 'pit'),
                    damage=enc_data.get('damage', '1d6'),
                    detect_difficulty=enc_data.get('detect_difficulty', 20),
                    trigger=enc_data.get('trigger', 'on_search')
                )
            elif enc_type == 'puzzle':
                encounter = PuzzleEncounter(
                    encounter_id=encounter_id,
                    encounter_type='puzzle',  # Required by parent class
                    puzzle_type=enc_data.get('puzzle_type', 'locked_chest'),
                    difficulty=enc_data.get('difficulty', 30),
                    reward=enc_data.get('reward'),
                    trigger=enc_data.get('trigger', 'manual')
                )
            else:
                continue

            encounters.append(encounter)

        return encounters

    def get_triggered_encounters(self, encounters: List[Encounter],
                                trigger_type: str) -> List[Encounter]:
        """
        Get encounters that should trigger

        Args:
            encounters: List of possible encounters
            trigger_type: Type of trigger ('on_enter', 'on_search', etc.)

        Returns:
            List of triggered encounters
        """

        return [enc for enc in encounters
                if enc.is_active and enc.trigger == trigger_type]
