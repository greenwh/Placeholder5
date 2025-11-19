"""
Combat system with THAC0 mechanics and dice rolling
"""

import random
import re
from typing import Dict, Optional, List
from ..entities.character import Character
from ..entities.player import Weapon
from ..constants import D20_MAX, CRITICAL_HIT, CRITICAL_MISS, INITIATIVE_DIE
from ..systems.monster_ai import MonsterTargetingAI


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

        # Critical miss
        if roll == CRITICAL_MISS:
            return {
                'hit': False,
                'roll': 1,
                'damage': 0,
                'narrative': f"{attacker.name} fumbles the attack!",
                'defender_died': False,
                'critical': 'miss'
            }

        # Critical hit
        if roll == CRITICAL_HIT:
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

        # Check weapon proficiency and apply non-proficiency penalty
        if hasattr(attacker, 'weapon_proficiencies') and weapon:
            from ..systems.weapon_proficiency import WeaponProficiencySystem
            prof_system = WeaponProficiencySystem()

            if not prof_system.is_proficient(attacker.weapon_proficiencies, weapon.name):
                penalty = prof_system.get_non_proficiency_penalty(attacker.char_class)
                to_hit_bonus += penalty  # Add penalty (it's negative)

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
                            monsters: List[Character],
                            party_obj=None) -> Dict:
        """
        Resolve a full combat round with individual initiative

        Args:
            party: List of party member Characters
            monsters: List of Monster Characters
            party_obj: Optional Party object for formation-aware targeting

        In AD&D 1e, initiative can be:
        - Side-based (d6 per side)
        - Individual (d6 + weapon speed factor + dexterity modifier)
        This implementation uses individual initiative for more tactical depth

        Args:
            party: List of party members (PCs)
            monsters: List of monsters

        Returns:
            Dict with round results
        """

        # Build initiative order for all combatants
        all_combatants = []

        for character in party:
            if character.is_alive and not character.is_incapacitated():
                init_value = self._calculate_initiative(character)
                all_combatants.append({
                    'character': character,
                    'initiative': init_value,
                    'side': 'party',
                    'attacks_remaining': getattr(character, 'attacks_per_round', 1.0)
                })

        for monster in monsters:
            if monster.is_alive:
                init_value = self._calculate_initiative(monster)
                all_combatants.append({
                    'character': monster,
                    'initiative': init_value,
                    'side': 'monster',
                    'attacks_remaining': getattr(monster, 'attacks_per_round', 1.0)
                })

        # Sort by initiative (lower is better in AD&D 1e)
        all_combatants.sort(key=lambda x: x['initiative'])

        results = {
            'actions': [],
            'party_won': False,
            'monsters_won': False
        }

        # Process attacks in initiative order
        # Handle fractional attacks (1.5, 2.0, etc.)
        attack_segments = [1, 2]  # Two attack segments per round

        for segment in attack_segments:
            for combatant in all_combatants:
                char = combatant['character']

                # Skip if dead or incapacitated
                if not char.is_alive or char.is_incapacitated():
                    continue

                # Determine if this character attacks this segment
                attacks_per_round = combatant['attacks_remaining']

                # 1 attack per round = attack on first segment only
                # 1.5 attacks per round = attack both segments alternately (every other round)
                # 2 attacks per round = attack both segments

                should_attack = False
                if attacks_per_round >= 2.0:
                    should_attack = True
                elif attacks_per_round >= 1.5:
                    # 1.5 attacks = 3 attacks per 2 rounds
                    # Implement as: attack first segment always, second segment alternately
                    should_attack = (segment == 1) or (random.random() < 0.5)
                elif segment == 1:
                    # 1 attack per round = first segment only
                    should_attack = True

                if not should_attack:
                    continue

                # Find target
                if combatant['side'] == 'party':
                    targets = [m for m in monsters if m.is_alive]
                else:
                    targets = [p for p in party if p.is_alive and not p.is_incapacitated()]

                if not targets:
                    break

                # Select target using formation-aware AI for monsters
                if combatant['side'] == 'monster' and party_obj is not None:
                    # Use AI targeting for monsters attacking party
                    ai = MonsterTargetingAI()
                    target = ai.select_target(char, party_obj, targets)
                else:
                    # Random targeting for player attacks or solo play
                    target = random.choice(targets)

                # Get weapon
                weapon = None
                if hasattr(char, 'equipment') and hasattr(char.equipment, 'weapon'):
                    weapon = char.equipment.weapon

                # Make attack
                result = self.attack_roll(char, target, weapon)
                results['actions'].append(result['narrative'])

                # Check for combat end
                if all(not m.is_alive for m in monsters):
                    results['party_won'] = True
                    return results

                if all(not p.is_alive for p in party):
                    results['monsters_won'] = True
                    return results

        return results

    def _calculate_initiative(self, character: Character) -> int:
        """
        Calculate individual initiative value

        Initiative = d6 + weapon speed factor + dexterity modifier

        Args:
            character: Character rolling initiative

        Returns:
            Initiative value (lower is better)
        """
        # Base initiative die roll
        base_roll = random.randint(1, INITIATIVE_DIE)

        # Weapon speed factor (higher = slower)
        weapon_speed = 0
        if hasattr(character, 'equipment') and hasattr(character.equipment, 'weapon'):
            weapon = character.equipment.weapon
            if hasattr(weapon, 'speed_factor'):
                weapon_speed = weapon.speed_factor
            else:
                # Default speed factor by weapon type if not specified
                weapon_speed = 5  # Average
        else:
            # Unarmed/natural weapons are fast
            weapon_speed = 2

        # Dexterity modifier (reaction/defense adjustment)
        # In AD&D 1e, high DEX improves initiative
        dex_mod = 0
        if hasattr(character, 'dex'):
            dex = character.dex
            if dex >= 18:
                dex_mod = -2  # Very fast
            elif dex >= 16:
                dex_mod = -1  # Fast
            elif dex <= 5:
                dex_mod = 2   # Very slow
            elif dex <= 8:
                dex_mod = 1   # Slow

        # Total initiative (lower is better)
        return base_roll + weapon_speed + dex_mod

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
