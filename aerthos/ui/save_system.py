"""
Save/Load system for game checkpoints
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class SaveSystem:
    """Handles game saving and loading"""

    def __init__(self, save_dir: str = None):
        if save_dir is None:
            self.save_dir = Path.home() / '.aerthos' / 'saves'
        else:
            self.save_dir = Path(save_dir)

        # Create save directory if it doesn't exist
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def save_game(self, game_state, slot: int = 1, description: str = ""):
        """
        Save game to a slot

        Args:
            game_state: GameState instance
            slot: Save slot number (1-3)
            description: Optional description for this save
        """

        save_data = {
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'player': self._serialize_player(game_state.player),
            'current_room_id': game_state.current_room.id,
            'dungeon_name': game_state.dungeon.name,
            'dungeon_state': game_state.dungeon.serialize(),
            'turns_elapsed': game_state.time_tracker.turns_elapsed,
            'total_hours': game_state.time_tracker.total_hours
        }

        filepath = self.save_dir / f'save_{slot}.json'

        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)

    def load_game(self, slot: int = 1) -> Optional[dict]:
        """
        Load game from a slot

        Args:
            slot: Save slot number

        Returns:
            Save data dictionary or None if not found
        """

        filepath = self.save_dir / f'save_{slot}.json'

        if not filepath.exists():
            return None

        with open(filepath, 'r') as f:
            return json.load(f)

    def list_saves(self) -> list:
        """
        List all available saves

        Returns:
            List of save info dictionaries
        """

        saves = []

        for slot in range(1, 4):
            filepath = self.save_dir / f'save_{slot}.json'

            if filepath.exists():
                with open(filepath, 'r') as f:
                    data = json.load(f)

                saves.append({
                    'slot': slot,
                    'character_name': data['player']['name'],
                    'level': data['player']['level'],
                    'class': data['player']['char_class'],
                    'timestamp': data['timestamp'],
                    'description': data.get('description', '')
                })

        return saves

    def _serialize_player(self, player) -> dict:
        """Serialize player character"""

        return {
            'name': player.name,
            'race': player.race,
            'char_class': player.char_class,
            'level': player.level,
            'strength': player.strength,
            'dexterity': player.dexterity,
            'constitution': player.constitution,
            'intelligence': player.intelligence,
            'wisdom': player.wisdom,
            'charisma': player.charisma,
            'strength_percentile': player.strength_percentile,
            'hp_current': player.hp_current,
            'hp_max': player.hp_max,
            'ac': player.ac,
            'thac0': player.thac0,
            'xp': player.xp,
            'xp_to_next_level': player.xp_to_next_level,
            'gold': player.gold,
            'conditions': list(player.conditions),  # Convert set to list for JSON
            'inventory': [item.name for item in player.inventory.items],
            'thief_skills': player.thief_skills,
            # Equipment
            'equipped_weapon': player.equipment.weapon.name if player.equipment.weapon else None,
            'equipped_armor': player.equipment.armor.name if player.equipment.armor else None,
            'equipped_shield': player.equipment.shield.name if player.equipment.shield else None,
            'equipped_light': player.equipment.light_source.name if player.equipment.light_source else None,
            # Spells
            'spells_known': [spell.name for spell in player.spells_known],
            'spells_memorized': [
                {
                    'level': slot.level,
                    'spell': slot.spell.name if slot.spell else None,
                    'is_used': slot.is_used
                }
                for slot in player.spells_memorized
            ]
        }
