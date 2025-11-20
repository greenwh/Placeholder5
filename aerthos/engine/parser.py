"""
Natural language command parser with flexible input handling
"""

from typing import Optional, List
from dataclasses import dataclass


@dataclass
class Command:
    """Parsed command structure"""
    action: str
    target: Optional[str] = None
    modifier: Optional[str] = None
    instrument: Optional[str] = None


class CommandParser:
    """
    Flexible parser supporting natural language variations

    Examples:
    - "attack orc" -> Command('attack', 'orc')
    - "attack the orc with sword" -> Command('attack', 'orc', instrument='sword')
    - "carefully search for traps" -> Command('search', 'traps', 'carefully')
    - "go north" -> Command('move', 'north')
    - "cast sleep on kobolds" -> Command('cast', 'sleep', target2='kobolds')
    """

    # Verb synonyms mapped to normalized actions
    VERBS = {
        'attack': ['attack', 'hit', 'strike', 'fight', 'kill', 'slay'],
        'move': ['go', 'move', 'walk', 'travel', 'head', 'n', 'north', 's', 'south',
                 'e', 'east', 'w', 'west', 'u', 'up', 'd', 'down'],
        'take': ['take', 'get', 'grab', 'pick', 'pickup', 'loot'],
        'drop': ['drop', 'discard'],
        'use': ['use', 'drink', 'eat', 'read', 'apply', 'consume'],
        'equip': ['equip', 'wear', 'wield', 'don'],
        'cast': ['cast'],
        'search': ['search'],
        'look': ['look', 'examine', 'inspect', 'check'],
        'open': ['open', 'unlock', 'pick'],
        'rest': ['rest', 'sleep', 'camp'],
        'inventory': ['inventory', 'inv', 'i', 'items'],
        'status': ['status', 'stats', 'character', 'sheet', 'char'],
        'spells': ['spells', 'spell', 'spellbook'],
        'memorize': ['memorize', 'prepare', 'pray'],
        'map': ['map', 'm', 'automap'],
        'directions': ['directions', 'dirs', 'exits'],
        'formation': ['formation', 'form', 'lineup', 'position'],
        'stairs_up': ['ascend', 'climb'],
        'stairs_down': ['descend'],
        'save': ['save'],
        'load': ['load'],
        'help': ['help', '?', 'commands'],
        'quit': ['quit', 'exit', 'q']
    }

    # Words to ignore
    STOPWORDS = ['the', 'a', 'an', 'at', 'to', 'for', 'on', 'from', 'in']

    # Direction mappings
    DIRECTION_MAP = {
        'n': 'north', 'north': 'north',
        's': 'south', 'south': 'south',
        'e': 'east', 'east': 'east',
        'w': 'west', 'west': 'west',
        'u': 'up', 'up': 'up',
        'd': 'down', 'down': 'down'
    }

    def parse(self, input_text: str) -> Command:
        """
        Parse user input into a Command

        Args:
            input_text: Raw user input

        Returns:
            Command object with normalized action and parameters
        """

        if not input_text or not input_text.strip():
            return Command('invalid')

        # Tokenize
        tokens = self._tokenize(input_text.lower())

        if not tokens:
            return Command('invalid')

        # Extract verb (action)
        action = self._extract_verb(tokens)

        if action == 'invalid':
            return Command('invalid')

        # Handle movement specially
        if action == 'move':
            direction = self._extract_direction(tokens)
            return Command('move', target=direction)

        # Handle inventory/status/map/directions/spells/look/stairs commands (no target needed)
        if action in ['inventory', 'status', 'map', 'directions', 'spells', 'look', 'stairs_up', 'stairs_down', 'help', 'save', 'load', 'quit']:
            return Command(action)

        # Extract target
        target = self._extract_target(tokens, action)

        # Extract modifier (adverbs)
        modifier = self._extract_modifier(tokens)

        # Extract instrument (after "with")
        instrument = self._extract_instrument(tokens)

        return Command(action, target, modifier, instrument)

    def _tokenize(self, text: str) -> List[str]:
        """
        Split text into tokens and remove stopwords

        Args:
            text: Input text (lowercased)

        Returns:
            List of tokens
        """

        words = text.split()
        # Remove stopwords but keep "with" for instrument parsing and "on"/"at"/"to" for spell targeting
        keep_words = {'with', 'on', 'at', 'to'}
        return [w for w in words if w not in self.STOPWORDS or w in keep_words]

    def _extract_verb(self, tokens: List[str]) -> str:
        """
        Find and normalize the verb

        Args:
            tokens: List of tokens

        Returns:
            Normalized action verb or 'invalid'
        """

        for token in tokens:
            for normalized_verb, synonyms in self.VERBS.items():
                if token in synonyms:
                    return normalized_verb

        return 'invalid'

    def _extract_direction(self, tokens: List[str]) -> Optional[str]:
        """
        Extract movement direction

        Args:
            tokens: List of tokens

        Returns:
            Normalized direction or None
        """

        for token in tokens:
            if token in self.DIRECTION_MAP:
                return self.DIRECTION_MAP[token]

        return None

    def _extract_target(self, tokens: List[str], action: str) -> Optional[str]:
        """
        Extract the target noun

        Args:
            tokens: List of tokens
            action: The normalized action

        Returns:
            Target string or None
        """

        # Special case: cast spell "on" target
        if action == 'cast':
            # Return ALL tokens after 'cast' so _handle_cast can parse spell name and target
            # e.g., "cast c on Shadow" → return "c on Shadow"
            try:
                cast_idx = -1
                for i, token in enumerate(tokens):
                    if token in self.VERBS['cast']:
                        cast_idx = i
                        break

                if cast_idx >= 0 and cast_idx + 1 < len(tokens):
                    # Return everything after 'cast' as a single string
                    remaining_tokens = tokens[cast_idx + 1:]
                    return ' '.join(remaining_tokens)
            except (ValueError, IndexError):
                pass

        # Get all verb words for filtering
        verb_words = [syn for syns in self.VERBS.values() for syn in syns]
        modifiers = ['carefully', 'quietly', 'quickly', 'slowly', 'stealthily']

        # Find first noun (not verb, not modifier, not 'with')
        for token in tokens:
            if (token not in verb_words and
                token not in modifiers and
                token != 'with' and
                token not in self.DIRECTION_MAP):
                return token

        return None

    def _extract_modifier(self, tokens: List[str]) -> Optional[str]:
        """
        Extract adverb modifiers

        Args:
            tokens: List of tokens

        Returns:
            Modifier string or None
        """

        modifiers = ['carefully', 'quietly', 'quickly', 'slowly', 'stealthily', 'cautiously']

        for token in tokens:
            if token in modifiers:
                return token

        return None

    def _extract_instrument(self, tokens: List[str]) -> Optional[str]:
        """
        Extract instrument (tool/weapon) after 'with'

        Args:
            tokens: List of tokens

        Returns:
            Instrument name or None
        """

        try:
            with_idx = tokens.index('with')
            if with_idx + 1 < len(tokens):
                return tokens[with_idx + 1]
        except ValueError:
            pass

        return None

    def get_help_text(self) -> str:
        """Get help text showing available commands"""

        return """
═══════════════════════════════════════════════════════════════
AERTHOS - COMMAND REFERENCE
═══════════════════════════════════════════════════════════════

MOVEMENT:
  go <direction>    - Move in a direction (north, south, east, west, up, down)
  n, s, e, w        - Short forms for directions
  directions / dirs - Show available exits from current room

COMBAT:
  attack <target>   - Attack an enemy
  cast <spell>      - Cast a memorized spell

INTERACTION:
  take <item>       - Pick up an item
  drop <item>       - Drop an item
  use <item>        - Use/consume an item (potions, scrolls)
  equip <item>      - Equip a weapon, armor, or light a torch/lantern
  search            - Search for traps or hidden items
  open <target>     - Open/unlock a chest or door (thieves can pick locks)

INFORMATION:
  inventory / i     - Show your inventory
  status            - Show character status
  map / m           - Show auto-map
  look / examine    - Look around current room

MAGIC (Spellcasters):
  spells            - Show known spells and memorized spells
  memorize <spell>  - Memorize a spell into an empty slot
  cast <spell>      - Cast a memorized spell

GAME MANAGEMENT:
  rest              - Rest for 8 hours (restore HP and spells)
  save              - Save your game
  load              - Load a saved game
  help / ?          - Show this help
  quit              - Exit the game

EXAMPLES:
  attack orc
  go north
  take sword
  equip longsword
  equip torch        (to light a torch when in darkness)
  cast magic missile
  search carefully

═══════════════════════════════════════════════════════════════
"""
