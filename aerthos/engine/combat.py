"""
Combat system with THAC0 mechanics and dice rolling
"""

import random
import re
from typing import Dict, Optional, List
from ..entities.character import Character
from ..entities.player import Weapon


class DiceRoller:
    """Handles all dice rolling operations"""

    @staticmethod
    def roll(dice_string: str) -> int:
        """
        Parse and roll dice notation
        Examples: '1d8', '2d6+1', '3d4-2', '1d12', '4+1'

        Args:
            dice_string: Dice notation string

        Returns:
            Total rolled value
        """
        dice_string = dice_string.strip().lower()

        # Handle flat modifiers like "4+1" (hit dice)
        if 'd' not in dice_string:
            # It's just a flat number or number+modifier
            if '+' in dice_string:
                try:
                    parts = dice_string.split('+')
                    if len(parts) == 2:
                        return int(parts[0]) + int(parts[1])
                    else:
                        raise ValueError(f"Invalid dice notation: {dice_string}")
                except (ValueError, IndexError):
                    raise ValueError(f"Invalid dice notation: {dice_string}")
            elif '-' in dice_string:
                try:
                    parts = dice_string.split('-')
                    if len(parts) == 2:
                        return int(parts[0]) - int(parts[1])
                    else:
                        raise ValueError(f"Invalid dice notation: {dice_string}")
                except (ValueError, IndexError):
                    raise ValueError(f"Invalid dice notation: {dice_string}")

            # Just a flat number
            try:
                return int(dice_string)
            except ValueError:
                raise ValueError(f"Invalid dice notation: {dice_string}")

        # Parse dice notation: XdY+Z or XdY-Z or XdY or dY (assumes 1d if no number before d)
        match = re.match(r'(\d*)d(\d+)([+\-]\d+)?', dice_string)

        if not match:
            raise ValueError(f"Invalid dice notation: {dice_string}")

        num_dice = int(match.group(1)) if match.group(1) else 1  # Default to 1 die
        die_size = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0

        # Roll the dice
        total = sum(random.randint(1, die_size) for _ in range(num_dice))
        return total + modifier

    @staticmethod
    def roll_3d6() -> int:
        """Roll 3d6 for ability scores"""
        return sum(random.randint(1, 6) for _ in range(3))

    @staticmethod
    def roll_d20() -> int:
        """Roll a d20"""
        return random.randint(1, 20)

    @staticmethod
    def roll_d100() -> int:
        """Roll d100 (percentile)"""
        return random.randint(1, 100)


class CombatResolver:
    """Handles combat resolution using THAC0 system"""

    def __init__(self):
        self.dice_roller = DiceRoller()

    def attack_roll(self, attacker: Character, defender: Character,
                    weapon: Optional[Weapon] = None) -> Dict:
        """
        Resolve a single attack using THAC0

        Formula: Roll d20, hit if roll >= (THAC0 - target AC)

        Args:
            attacker: The attacking character
            defender: The defending character
            weapon: Optional weapon being used (None = unarmed/default)

        Returns:
            Dict with: hit, roll, damage, narrative, defender_died
        """

        # Roll d20
        roll = self.dice_roller.roll_d20()

        # Critical miss (natural 1)
        if roll == 1:
            return {
                'hit': False,
                'roll': 1,
                'damage': 0,
                'narrative': f"{attacker.name} fumbles the attack!",
                'defender_died': False,
                'critical': 'miss'
            }

        # Critical hit (natural 20)
        if roll == 20:
            damage = self._calculate_damage(attacker, defender, weapon, critical=True)
            died = defender.take_damage(damage)

            narrative = f"{attacker.name} scores a CRITICAL HIT on {defender.name} for {damage} damage!"
            if died:
                narrative += f" {defender.name} falls dead!"

            return {
                'hit': True,
                'roll': 20,
                'damage': damage,
                'narrative': narrative,
                'defender_died': died,
                'critical': 'hit'
            }

        # Normal THAC0 calculation
        # Target number = THAC0 - defender's AC
        # (Lower AC is better, so subtracting a low AC makes target number higher)
        target_number = attacker.thac0 - defender.ac

        # Apply to-hit bonuses (STR modifier + weapon magic bonus)
        to_hit_bonus = attacker.get_to_hit_bonus()

        # Add weapon magic bonus if present
        if weapon and hasattr(weapon, 'magic_bonus'):
            to_hit_bonus += weapon.magic_bonus

        # Handle special weapon to-hit bonuses
        if weapon and hasattr(weapon, 'properties'):
            props = weapon.properties

            # Dragon Slayer - bonus to hit vs dragons
            if props.get('special') == 'dragon_slayer':
                if hasattr(defender, 'name') and 'dragon' in defender.name.lower():
                    to_hit_bonus += props.get('bonus_vs_dragons', 3)

            # Vs Lycanthropes - bonus to hit vs lycanthropes
            elif props.get('special') == 'vs_lycanthropes':
                if hasattr(defender, 'name') and 'were' in defender.name.lower():
                    to_hit_bonus += props.get('bonus_vs_lycanthropes', 2)

        adjusted_roll = roll + to_hit_bonus

        hit = adjusted_roll >= target_number

        if hit:
            damage = self._calculate_damage(attacker, defender, weapon)
            died = defender.take_damage(damage)

            narrative = f"{attacker.name} hits {defender.name} for {damage} damage!"
            if died:
                narrative += f" {defender.name} is slain!"

            return {
                'hit': True,
                'roll': roll,
                'damage': damage,
                'narrative': narrative,
                'defender_died': died,
                'critical': None
            }
        else:
            return {
                'hit': False,
                'roll': roll,
                'damage': 0,
                'narrative': f"{attacker.name} misses {defender.name}.",
                'defender_died': False,
                'critical': None
            }

    def _calculate_damage(self, attacker: Character, defender: Character,
                         weapon: Optional[Weapon] = None,
                         critical: bool = False) -> int:
        """
        Calculate damage for an attack

        Args:
            attacker: The attacking character
            defender: The defending character
            weapon: Weapon used (None = unarmed)
            critical: Whether this is a critical hit (double damage)

        Returns:
            Total damage dealt
        """

        # Determine damage dice
        if weapon:
            # Use appropriate damage dice based on defender size
            if defender.size in ['S', 'M']:
                dice_string = weapon.damage_sm
            else:
                dice_string = weapon.damage_l
        else:
            # Unarmed or natural weapon
            # Check if attacker is a monster with damage property
            if hasattr(attacker, 'damage'):
                dice_string = attacker.damage
            else:
                # Default unarmed damage
                dice_string = "1d2"

        # Roll damage
        base_damage = self.dice_roller.roll(dice_string)

        # Add strength bonus
        damage_bonus = attacker.get_damage_bonus()

        # Add weapon magic bonus to damage
        if weapon and hasattr(weapon, 'magic_bonus'):
            damage_bonus += weapon.magic_bonus

        # Handle special weapon properties
        extra_damage = 0
        if weapon and hasattr(weapon, 'properties'):
            props = weapon.properties

            # Flame Tongue - extra fire damage
            if props.get('special') == 'flame_tongue':
                fire_dice = props.get('fire_damage', '1d4+1')
                extra_damage += self.dice_roller.roll(fire_dice)

            # Frost Brand - extra cold damage
            elif props.get('special') == 'frost_brand':
                cold_dice = props.get('cold_damage', '1d6')
                extra_damage += self.dice_roller.roll(cold_dice)

            # Dragon Slayer - bonus vs dragons
            elif props.get('special') == 'dragon_slayer':
                if hasattr(defender, 'name') and 'dragon' in defender.name.lower():
                    bonus_vs_dragons = props.get('bonus_vs_dragons', 3)
                    damage_bonus += bonus_vs_dragons

            # Vs Lycanthropes - bonus vs lycanthropes
            elif props.get('special') == 'vs_lycanthropes':
                if hasattr(defender, 'name') and 'were' in defender.name.lower():
                    bonus_vs_lycan = props.get('bonus_vs_lycanthropes', 2)
                    damage_bonus += bonus_vs_lycan

        total_damage = base_damage + damage_bonus + extra_damage

        # Critical hit doubles the total
        if critical:
            total_damage *= 2

        # Minimum 1 damage on a hit
        return max(1, total_damage)

    def resolve_combat_round(self, party: List[Character],
                            monsters: List[Character]) -> Dict:
        """
        Resolve a full combat round (side-based initiative)

        In AD&D 1e, initiative is rolled per side, not per character

        Args:
            party: List of party members (PCs)
            monsters: List of monsters

        Returns:
            Dict with round results
        """

        # Roll initiative (d6 for each side, lower goes first)
        party_init = random.randint(1, 6)
        monster_init = random.randint(1, 6)

        results = {
            'party_initiative': party_init,
            'monster_initiative': monster_init,
            'actions': [],
            'party_won': False,
            'monsters_won': False
        }

        # Determine order
        if party_init <= monster_init:
            # Party goes first
            self._process_side_actions(party, monsters, results['actions'])
            if all(not m.is_alive for m in monsters):
                results['party_won'] = True
                return results

            self._process_side_actions(monsters, party, results['actions'])
            if all(not p.is_alive for p in party):
                results['monsters_won'] = True
        else:
            # Monsters go first
            self._process_side_actions(monsters, party, results['actions'])
            if all(not p.is_alive for p in party):
                results['monsters_won'] = True
                return results

            self._process_side_actions(party, monsters, results['actions'])
            if all(not m.is_alive for m in monsters):
                results['party_won'] = True

        return results

    def _process_side_actions(self, attackers: List[Character],
                              defenders: List[Character],
                              action_log: List[str]):
        """
        Process actions for one side in combat

        Args:
            attackers: Characters taking action
            defenders: Characters being targeted
            action_log: List to append action narratives to
        """

        for attacker in attackers:
            # Skip if incapacitated
            if attacker.is_incapacitated():
                continue

            # Find a living target
            living_defenders = [d for d in defenders if d.is_alive]
            if not living_defenders:
                break

            # Pick a random target
            target = random.choice(living_defenders)

            # Get weapon if attacker has equipment
            weapon = None
            if hasattr(attacker, 'equipment') and attacker.equipment.weapon:
                weapon = attacker.equipment.weapon

            # Make attack
            result = self.attack_roll(attacker, target, weapon)
            action_log.append(result['narrative'])
