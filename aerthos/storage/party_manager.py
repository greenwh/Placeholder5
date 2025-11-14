"""
Party Manager - Persistent party compositions

Manages saved party configurations (which characters, what formation).
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from .character_roster import CharacterRoster


class PartyManager:
    """Manages persistent party configurations"""

    def __init__(self, parties_dir: str = None, character_roster: 'CharacterRoster' = None):
        if parties_dir is None:
            self.parties_dir = Path.home() / '.aerthos' / 'parties'
        else:
            self.parties_dir = Path(parties_dir)

        # Create directory if it doesn't exist
        self.parties_dir.mkdir(parents=True, exist_ok=True)

        # Use provided roster or create default one
        if character_roster is not None:
            self.character_roster = character_roster
        else:
            self.character_roster = CharacterRoster()

    def save_party(self, party_name: str, character_ids: List[str],
                   formation: List[str], party_id: str = None) -> str:
        """
        Save a party composition

        Args:
            party_name: Name for this party
            character_ids: List of character IDs in the party
            formation: List of formation positions ('front' or 'back')
            party_id: Optional ID (generates UUID if not provided)

        Returns:
            Party ID
        """
        if party_id is None:
            party_id = str(uuid.uuid4())[:8]

        if len(character_ids) != len(formation):
            raise ValueError("Character IDs and formation must be same length")

        if len(character_ids) < 1 or len(character_ids) > 6:
            raise ValueError("Party must have 1-6 members")

        party_data = {
            'id': party_id,
            'name': party_name,
            'created': datetime.now().isoformat(),
            'character_ids': character_ids,
            'formation': formation,
            'size': len(character_ids)
        }

        filename = f"{party_name.lower().replace(' ', '_')}_{party_id}.json"
        filepath = self.parties_dir / filename

        with open(filepath, 'w') as f:
            json.dump(party_data, f, indent=2)

        return party_id

    def load_party(self, party_id: str = None, party_name: str = None):
        """
        Load a party composition and create Party instance with actual characters

        Args:
            party_id: Party ID to load
            party_name: Or party name to load

        Returns:
            Dictionary with 'party' object and metadata, or None if not found
        """
        party_data = None

        if party_id:
            # Find by ID
            for filepath in self.parties_dir.glob('*.json'):
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        if data['id'] == party_id:
                            party_data = data
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

        if not party_data and party_name:
            # Find by name
            for filepath in self.parties_dir.glob('*.json'):
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        if data['name'].lower() == party_name.lower():
                            party_data = data
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

        if not party_data:
            return None

        # Validate loaded data
        character_ids = party_data.get('character_ids', [])
        formation = party_data.get('formation', [])

        if len(character_ids) != len(formation):
            print(f"Warning: Party {party_data.get('name', 'Unknown')} has mismatched formation. Auto-repairing...")
            # Auto-repair formation
            formation = ['front' if i < 2 else 'back' for i in range(len(character_ids))]
            party_data['formation'] = formation

        if not (1 <= len(character_ids) <= 6):
            print(f"Warning: Party {party_data.get('name', 'Unknown')} has invalid size {len(character_ids)}")
            if len(character_ids) > 6:
                print(f"Truncating party to 6 members")
                character_ids = character_ids[:6]
                formation = formation[:6]
            elif len(character_ids) == 0:
                print(f"Error: Party is empty, cannot load")
                return None

        # Load actual characters from roster
        from ..entities.party import Party

        party = Party()
        for char_id in character_ids:
            character = self.character_roster.load_character(character_id=char_id)
            if character:
                party.add_member(character)
            else:
                print(f"Warning: Character {char_id} not found in roster")

        party.formation = formation

        return {
            'party': party,
            'name': party_data['name'],
            'id': party_data['id'],
            'created': party_data['created']
        }

    def list_parties(self) -> List[Dict]:
        """
        List all saved parties

        Returns:
            List of party summary dictionaries
        """
        parties = []

        for filepath in self.parties_dir.glob('*.json'):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)

                    # Get character info
                    members = []
                    for char_id in data['character_ids']:
                        try:
                            char = self.character_roster.load_character(character_id=char_id)
                            if char:
                                members.append({
                                    'name': char.name,
                                    'class': char.char_class,
                                    'level': char.level
                                })
                            else:
                                members.append({
                                    'name': f"Unknown ({char_id[:6]})",
                                    'class': 'Unknown',
                                    'level': 0
                                })
                        except Exception as char_error:
                            print(f"Error loading character {char_id}: {char_error}")
                            members.append({
                                'name': f"Error ({char_id[:6]})",
                                'class': 'Error',
                                'level': 0
                            })

                    parties.append({
                        'id': data['id'],
                        'name': data['name'],
                        'size': data['size'],
                        'members': members,
                        'formation': data.get('formation', ['front'] * data['size']),
                        'created': data['created']
                    })
            except Exception as e:
                print(f"Error loading {filepath}: {e}")

        return sorted(parties, key=lambda p: p['name'])

    def delete_party(self, party_id: str) -> bool:
        """
        Delete a party configuration

        Args:
            party_id: Party ID to delete

        Returns:
            True if deleted, False if not found
        """
        found_path = None
        for filepath in self.parties_dir.glob('*.json'):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if data['id'] == party_id:
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
