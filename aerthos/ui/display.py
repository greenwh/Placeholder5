"""
Display and text formatting utilities
"""

import textwrap
from typing import List


class Display:
    """Handles text output formatting"""

    @staticmethod
    def show_title():
        """Display game title"""
        print("=" * 70)
        print("""
   █████╗ ███████╗██████╗ ████████╗██╗  ██╗ ██████╗ ███████╗
  ██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██║  ██║██╔═══██╗██╔════╝
  ███████║█████╗  ██████╔╝   ██║   ███████║██║   ██║███████╗
  ██╔══██║██╔══╝  ██╔══██╗   ██║   ██╔══██║██║   ██║╚════██║
  ██║  ██║███████╗██║  ██║   ██║   ██║  ██║╚██████╔╝███████║
  ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
""")
        print("      Advanced Dungeons & Dragons 1e Text Adventure")
        print("=" * 70)
        print()

    @staticmethod
    def show_message(message: str, width: int = 70):
        """
        Display a message with word wrapping

        Args:
            message: Message to display
            width: Maximum line width
        """

        # Preserve intentional line breaks
        paragraphs = message.split('\n\n')

        for para in paragraphs:
            if para.strip():
                # Preserve lines that start with special characters or contain ASCII art
                if para.startswith(('═', '─', ' ', '[', '│')) or any(c in para for c in ['│', '─', '↑', '↓', '←', '→']):
                    # This is formatted content (ASCII art, maps, tables) - print as-is
                    print(para)
                else:
                    wrapped = textwrap.fill(para, width=width)
                    print(wrapped)

            print()

    @staticmethod
    def show_room(room_description: str):
        """
        Display room description

        Args:
            room_description: Room text
        """

        print()
        print("─" * 70)
        Display.show_message(room_description)
        print("─" * 70)
        print()

    @staticmethod
    def show_combat_round(messages: List[str]):
        """
        Display combat round results

        Args:
            messages: List of combat messages
        """

        print()
        print("⚔" * 35)
        for msg in messages:
            print(f"  {msg}")
        print("⚔" * 35)
        print()

    @staticmethod
    def show_party_formation(party):
        """
        Display party formation at start of combat

        Args:
            party: Party object with formation data
        """
        from ..entities.party import Party

        if not isinstance(party, Party):
            return

        print()
        print("═" * 70)
        print("COMBAT - PARTY FORMATION")
        print("═" * 70)

        # Get front and back lines
        front_line = party.get_front_line()
        back_line = party.get_back_line()

        # Display front line
        if front_line:
            print("\nFRONT LINE:")
            for member in front_line:
                status = "ALIVE" if member.is_alive else "DEAD"
                hp_str = f"HP: {member.hp_current}/{member.hp_max}"
                ac_str = f"AC: {member.ac}"
                print(f"  • {member.name} ({member.char_class}) [{status}] {hp_str}, {ac_str}")

        # Display back line
        if back_line:
            print("\nBACK LINE:")
            for member in back_line:
                status = "ALIVE" if member.is_alive else "DEAD"
                hp_str = f"HP: {member.hp_current}/{member.hp_max}"
                ac_str = f"AC: {member.ac}"
                print(f"  • {member.name} ({member.char_class}) [{status}] {hp_str}, {ac_str}")

        print("═" * 70)
        print()

    @staticmethod
    def show_death_screen(player_name: str):
        """
        Display death screen

        Args:
            player_name: Name of deceased character
        """

        print()
        print("=" * 70)
        print()
        print(f"              {player_name} HAS FALLEN")
        print()
        print("        Your adventure ends here, brave adventurer.")
        print("        May your next life be more fortunate...")
        print()
        print("=" * 70)
        print()

    @staticmethod
    def show_victory_screen():
        """Display victory screen"""

        print()
        print("=" * 70)
        print()
        print("              ★ ★ ★ VICTORY ★ ★ ★")
        print()
        print("        You have conquered the dungeon!")
        print("        Glory and treasure are yours!")
        print()
        print("=" * 70)
        print()

    @staticmethod
    def prompt_input(prompt: str = "> ") -> str:
        """
        Get user input with prompt

        Args:
            prompt: Input prompt

        Returns:
            User input string
        """

        return input(prompt).strip()

    @staticmethod
    def clear_screen():
        """Clear the screen (optional)"""
        # We'll skip actual clearing for better scrollback
        print("\n" * 2)
