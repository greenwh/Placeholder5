"""
Character sheet display and formatting
"""

from ..entities.player import PlayerCharacter


class CharacterSheet:
    """Formats character information for display"""

    @staticmethod
    def format_character(player: PlayerCharacter) -> str:
        """
        Format complete character sheet

        Args:
            player: Player character

        Returns:
            Formatted character sheet string
        """

        lines = []
        lines.append("═" * 60)
        lines.append(f"CHARACTER: {player.name}")
        lines.append("═" * 60)
        lines.append(f"Race: {player.race}")
        lines.append(f"Class: {player.char_class}")
        lines.append(f"Level: {player.level}")
        lines.append(f"XP: {player.xp} / {player.xp_to_next_level}")
        lines.append("")

        # Ability Scores
        lines.append("ABILITY SCORES:")
        lines.append(f"  STR: {player.strength}" +
                    (f"/{player.strength_percentile}" if player.strength == 18 and player.strength_percentile > 0 else ""))
        lines.append(f"  DEX: {player.dexterity}")
        lines.append(f"  CON: {player.constitution}")
        lines.append(f"  INT: {player.intelligence}")
        lines.append(f"  WIS: {player.wisdom}")
        lines.append(f"  CHA: {player.charisma}")
        lines.append("")

        # Combat Stats
        lines.append("COMBAT STATS:")
        lines.append(f"  HP: {player.hp_current} / {player.hp_max}")
        lines.append(f"  AC: {player.get_effective_ac()} (lower is better)")
        lines.append(f"  THAC0: {player.thac0}")
        lines.append(f"  To-Hit Bonus: {player.get_to_hit_bonus():+d}")
        lines.append(f"  Damage Bonus: {player.get_damage_bonus():+d}")
        lines.append("")

        # Equipment
        lines.append("EQUIPMENT:")
        weapon_name = player.equipment.weapon.name if player.equipment.weapon else "None"
        armor_name = player.equipment.armor.name if player.equipment.armor else "None"
        shield_name = player.equipment.shield.name if player.equipment.shield else "None"
        light_name = player.equipment.light_source.name if player.equipment.light_source else "None"

        lines.append(f"  Weapon: {weapon_name}")
        lines.append(f"  Armor: {armor_name}")
        lines.append(f"  Shield: {shield_name}")
        lines.append(f"  Light: {light_name}")
        lines.append(f"  Gold: {player.gold} gp")
        lines.append("")

        # Spells (if applicable)
        if player.spells_memorized:
            lines.append("SPELLS MEMORIZED:")
            for slot in player.spells_memorized:
                if slot.spell:
                    status = "USED" if slot.is_used else "READY"
                    lines.append(f"  [{status}] {slot.spell.name} (Level {slot.level})")
            lines.append("")

        # Thief Skills (if applicable)
        if player.thief_skills:
            lines.append("THIEF SKILLS:")
            for skill, value in player.thief_skills.items():
                skill_display = skill.replace('_', ' ').title()
                lines.append(f"  {skill_display}: {value}%")
            lines.append("")

        # Conditions
        if player.conditions:
            lines.append("CONDITIONS:")
            lines.append(f"  {', '.join(player.conditions)}")
            lines.append("")

        lines.append("═" * 60)

        return '\n'.join(lines)

    @staticmethod
    def format_quick_status(player: PlayerCharacter) -> str:
        """
        Format quick status line

        Args:
            player: Player character

        Returns:
            Single-line status
        """

        return (f"{player.name} | HP: {player.hp_current}/{player.hp_max} | "
                f"AC: {player.get_effective_ac()} | Gold: {player.gold} gp")

    @staticmethod
    def format_party_roster(party) -> str:
        """
        Format party roster with formation positions

        Args:
            party: Party object

        Returns:
            Formatted party roster string
        """
        from ..entities.party import Party

        if not isinstance(party, Party):
            return "No party data available"

        lines = []
        lines.append("═" * 70)
        lines.append("PARTY ROSTER")
        lines.append("═" * 70)
        lines.append(f"Party Size: {party.size()}/{party.max_size}")
        lines.append(f"Average Level: {party.average_level:.1f}")
        lines.append("")

        # Get formation positions
        front_line = party.get_front_line()
        back_line = party.get_back_line()

        # Display front line
        if front_line:
            lines.append("FRONT LINE:")
            for member in front_line:
                status = "✓" if member.is_alive else "✗"
                hp_pct = int((member.hp_current / member.hp_max) * 100) if member.hp_max > 0 else 0
                hp_bar = CharacterSheet._format_hp_bar(hp_pct)
                lines.append(f"  {status} {member.name} ({member.char_class}-{member.level})")
                lines.append(f"    HP: {member.hp_current}/{member.hp_max} {hp_bar} | AC: {member.ac} | THAC0: {member.thac0}")

        # Display back line
        if back_line:
            lines.append("")
            lines.append("BACK LINE:")
            for member in back_line:
                status = "✓" if member.is_alive else "✗"
                hp_pct = int((member.hp_current / member.hp_max) * 100) if member.hp_max > 0 else 0
                hp_bar = CharacterSheet._format_hp_bar(hp_pct)
                lines.append(f"  {status} {member.name} ({member.char_class}-{member.level})")
                lines.append(f"    HP: {member.hp_current}/{member.hp_max} {hp_bar} | AC: {member.ac} | THAC0: {member.thac0}")

        lines.append("")
        lines.append("═" * 70)

        return '\n'.join(lines)

    @staticmethod
    def _format_hp_bar(percentage: int, width: int = 10) -> str:
        """
        Format HP bar visualization

        Args:
            percentage: HP percentage (0-100)
            width: Bar width in characters

        Returns:
            HP bar string like [████░░░░░░]
        """
        filled = int((percentage / 100) * width)
        empty = width - filled

        return f"[{'█' * filled}{'░' * empty}]"
