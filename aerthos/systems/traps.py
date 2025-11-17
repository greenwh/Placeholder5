"""
Trap System

Implements AD&D 1e trap mechanics:
- Trap generation from DMG tables
- Search and detection mechanics
- Disarm mechanics (thief skills)
- Trap effects and damage
"""

import json
import random
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Trap:
    """A trap in the dungeon"""
    trap_type: str
    damage: str
    save_type: str
    description: str
    trigger: str
    detected: bool = False
    disarmed: bool = False
    difficulty: str = "standard"  # simple, standard, complex, magical

    def is_active(self) -> bool:
        """Check if trap is still active"""
        return not self.disarmed

    def is_hidden(self) -> bool:
        """Check if trap is still hidden"""
        return not self.detected


@dataclass
class TrapSearchResult:
    """Result of searching for traps"""
    found: bool
    trap: Optional[Trap] = None
    search_quality: str = "normal"  # normal, thorough, hasty
    time_spent: int = 1  # turns


@dataclass
class TrapDisarmResult:
    """Result of attempting to disarm a trap"""
    success: bool
    trap_triggered: bool = False
    critical_success: bool = False  # Learned something about trap
    damage: int = 0
    message: str = ""


class TrapSystem:
    """
    AD&D 1e Trap Mechanics

    Handles trap generation, detection, and disarming
    """

    def __init__(self, trap_tables_path: Optional[Path] = None):
        """
        Initialize trap system

        Args:
            trap_tables_path: Path to traps.json
        """
        if trap_tables_path is None:
            base_dir = Path(__file__).parent.parent
            trap_tables_path = base_dir / "data" / "dmg_tables" / "traps.json"

        with open(trap_tables_path, 'r') as f:
            self.tables = json.load(f)

    def _roll_dice(self, formula: str) -> int:
        """
        Roll dice from formula

        Args:
            formula: Dice formula like "1-6", "2-12", "3d6"

        Returns:
            Result of roll
        """
        if not formula or formula == "special":
            return 0

        # Handle "1-6" format (range)
        match = re.match(r'(\d+)-(\d+)', formula)
        if match:
            min_val = int(match.group(1))
            max_val = int(match.group(2))
            return random.randint(min_val, max_val)

        # Handle "3d6" format (dice)
        match = re.match(r'(\d+)d(\d+)([+-]\d+)?', formula)
        if match:
            num_dice = int(match.group(1))
            die_size = int(match.group(2))
            modifier = int(match.group(3)) if match.group(3) else 0

            total = sum(random.randint(1, die_size) for _ in range(num_dice))
            return total + modifier

        return 0

    def generate_trap(self, difficulty: str = "standard") -> Trap:
        """
        Generate a random trap from DMG tables

        Args:
            difficulty: Trap difficulty (simple, standard, complex, magical)

        Returns:
            Generated Trap instance
        """
        # Roll on trap table
        roll = random.randint(1, 100)

        trap_table = self.tables["trap_types"]["table"]
        trap_data = None

        for entry in trap_table:
            roll_range = entry["roll"]

            if "-" in roll_range:
                min_r, max_r = map(int, roll_range.split("-"))
                if min_r <= roll <= max_r:
                    trap_data = entry
                    break
            elif roll == int(roll_range):
                trap_data = entry
                break

        if not trap_data:
            trap_data = trap_table[0]  # Fallback

        # Select trigger
        trigger = random.choice(self.tables["trap_triggers"])

        return Trap(
            trap_type=trap_data["trap"],
            damage=trap_data["damage"],
            save_type=trap_data["save"],
            description=trap_data["description"],
            trigger=trigger,
            difficulty=difficulty
        )

    def search_for_traps(
        self,
        searcher_class: str,
        searcher_race: str,
        thief_skill: int = 0,
        search_time: int = 1,
        trap_present: bool = True
    ) -> TrapSearchResult:
        """
        Search for traps in an area

        Args:
            searcher_class: Character class
            searcher_race: Character race
            thief_skill: Find/Remove Traps skill percentage (if thief)
            search_time: Time spent searching (turns)
            trap_present: Whether trap is actually present

        Returns:
            TrapSearchResult
        """
        if not trap_present:
            return TrapSearchResult(found=False, time_spent=search_time)

        found = False

        # Thief using skill
        if searcher_class.lower() == "thief":
            roll = random.randint(1, 100)
            if roll <= thief_skill:
                found = True

        # Dwarf detecting construction traps
        elif searcher_race.lower() == "dwarf":
            roll = random.randint(1, 6)
            if roll <= 2:  # 2 in 6
                found = True

        # General search (1 in 6)
        else:
            roll = random.randint(1, 6)
            if roll == 1:
                found = True

        # Thorough search improves odds
        if search_time >= 2 and not found:
            # Second chance with penalty
            roll = random.randint(1, 6)
            if roll == 1:
                found = True

        if found:
            # Generate the trap that was found
            trap = self.generate_trap()
            trap.detected = True
            return TrapSearchResult(
                found=True,
                trap=trap,
                search_quality="thorough" if search_time >= 2 else "normal",
                time_spent=search_time
            )

        return TrapSearchResult(found=False, time_spent=search_time)

    def disarm_trap(
        self,
        trap: Trap,
        disarmer_class: str,
        thief_skill: int = 0,
        strength: int = 10,
        intelligence: int = 10
    ) -> TrapDisarmResult:
        """
        Attempt to disarm a trap

        Args:
            trap: The trap to disarm
            disarmer_class: Character class
            thief_skill: Remove Traps skill percentage
            strength: STR score (for physical methods)
            intelligence: INT score (for complex traps)

        Returns:
            TrapDisarmResult
        """
        if trap.disarmed:
            return TrapDisarmResult(
                success=True,
                message="Trap is already disarmed."
            )

        if not trap.detected:
            return TrapDisarmResult(
                success=False,
                message="Cannot disarm an undetected trap!"
            )

        # Apply difficulty modifier
        difficulty_mods = {
            "simple": 10,
            "standard": 0,
            "complex": -10,
            "magical": -20
        }

        modifier = difficulty_mods.get(trap.difficulty, 0)

        # Thief using skill
        if disarmer_class.lower() == "thief":
            effective_skill = thief_skill + modifier
            effective_skill = max(1, min(99, effective_skill))  # Clamp 1-99

            roll = random.randint(1, 100)

            if roll <= effective_skill:
                # Success!
                trap.disarmed = True

                # Check for critical success (learn about trap)
                if roll <= 10:
                    return TrapDisarmResult(
                        success=True,
                        critical_success=True,
                        message=f"You skillfully disarm the {trap.trap_type}. "
                                f"You understand how it works now (+5% next time)."
                    )

                return TrapDisarmResult(
                    success=True,
                    message=f"You carefully disarm the {trap.trap_type}."
                )

            else:
                # Failure - check if trap triggers
                # Catastrophic failure on 96-00
                if roll >= 96:
                    damage = self._roll_dice(trap.damage)
                    return TrapDisarmResult(
                        success=False,
                        trap_triggered=True,
                        damage=damage,
                        message=f"You fumble and trigger the {trap.trap_type}!"
                    )

                return TrapDisarmResult(
                    success=False,
                    message=f"You fail to disarm the {trap.trap_type}."
                )

        # Non-thief attempting to disarm (much harder)
        else:
            # Base 10% chance, modified by INT
            int_modifier = (intelligence - 10) // 2  # -5 to +5
            base_chance = 10 + int_modifier + modifier

            roll = random.randint(1, 100)

            if roll <= base_chance:
                trap.disarmed = True
                return TrapDisarmResult(
                    success=True,
                    message=f"Through clever thinking, you manage to disarm the {trap.trap_type}."
                )

            # Higher failure chance for non-thieves
            if roll >= 85:
                damage = self._roll_dice(trap.damage)
                return TrapDisarmResult(
                    success=False,
                    trap_triggered=True,
                    damage=damage,
                    message=f"Your clumsy attempt triggers the {trap.trap_type}!"
                )

            return TrapDisarmResult(
                success=False,
                message=f"You fail to disarm the {trap.trap_type}. Best leave this to an expert."
            )

    def trigger_trap(
        self,
        trap: Trap,
        victim_class: str = "fighter",
        victim_level: int = 1,
        save_bonus: int = 0
    ) -> Dict:
        """
        Trigger a trap and resolve effects

        Args:
            trap: The trap being triggered
            victim_class: Victim's class
            victim_level: Victim's level
            save_bonus: Bonus to saving throw

        Returns:
            Dictionary with trap effects
        """
        if trap.disarmed:
            return {
                "triggered": False,
                "message": "Trap is disarmed and harmless."
            }

        result = {
            "triggered": True,
            "trap_type": trap.trap_type,
            "description": trap.description,
            "damage": 0,
            "save_made": False,
            "effects": []
        }

        # Check for saving throw
        save_made = False
        if trap.save_type != "none":
            # Use appropriate saving throw (simplified)
            save_target = 15 - victim_level + save_bonus

            roll = random.randint(1, 20)
            if roll >= save_target:
                save_made = True
                result["save_made"] = True

        # Calculate damage
        damage = self._roll_dice(trap.damage)

        if save_made and trap.save_type == "breath_weapon":
            # Breath weapon saves halve damage
            damage = damage // 2
            result["effects"].append("Saved for half damage!")

        elif save_made and trap.save_type == "poison":
            # Poison save negates
            damage = 0
            result["effects"].append("Saved vs poison!")

        elif trap.save_type == "poison" and not save_made:
            result["effects"].append("Failed save vs poison - deadly!")

        result["damage"] = damage

        # Special effects for certain traps
        if "gas_blinding" in trap.trap_type:
            result["effects"].append("Blinded (-4 to hit for 2-12 rounds)")

        elif "gas_fear" in trap.trap_type:
            if not save_made:
                result["effects"].append("Overcome by fear - must flee for 2-8 rounds")

        elif "net" in trap.trap_type:
            if not save_made:
                result["effects"].append("Entangled in net - cannot move")

        elif "teleporter" in trap.trap_type:
            result["effects"].append("Teleported to random location!")

        return result

    def describe_trap(self, trap: Trap, detected: bool = False) -> str:
        """
        Generate description of trap

        Args:
            trap: The trap
            detected: Whether trap has been detected

        Returns:
            Description string
        """
        if not detected:
            return "You sense danger here, but cannot locate the source."

        descriptions = {
            "arrow_trap": "A pressure plate connected to a spring-loaded arrow mechanism",
            "pit_spiked_10ft": "A covered pit with sharp spikes at the bottom",
            "gas_poison": "A sealed container of deadly poison gas triggered by opening",
            "scything_blade": "A blade on a pendulum mechanism ready to swing across",
            "ceiling_block": "A heavy stone block suspended above, ready to fall"
        }

        base_desc = descriptions.get(trap.trap_type, trap.description)

        return (
            f"You detect a trap: {base_desc}. "
            f"Trigger: {trap.trigger}. "
            f"Difficulty: {trap.difficulty}."
        )


# Convenience functions
def generate_trap(difficulty: str = "standard") -> Trap:
    """Generate a random trap"""
    system = TrapSystem()
    return system.generate_trap(difficulty)


def search_for_trap(
    character_class: str,
    character_race: str,
    thief_skill: int = 0,
    trap_present: bool = True
) -> TrapSearchResult:
    """Search for traps"""
    system = TrapSystem()
    return system.search_for_traps(
        character_class,
        character_race,
        thief_skill,
        search_time=1,
        trap_present=trap_present
    )


if __name__ == "__main__":
    # Test trap system
    print("="*70)
    print("AD&D 1e TRAP SYSTEM TEST")
    print("="*70)

    system = TrapSystem()

    # Test 1: Generate traps
    print("\n1. TRAP GENERATION")
    print("-" * 70)
    for i in range(3):
        trap = system.generate_trap()
        print(f"\nTrap {i+1}: {trap.trap_type}")
        print(f"  Damage: {trap.damage}")
        print(f"  Save: {trap.save_type}")
        print(f"  Trigger: {trap.trigger}")
        print(f"  Description: {trap.description}")

    # Test 2: Search for traps
    print("\n2. SEARCHING FOR TRAPS")
    print("-" * 70)

    # Thief searching
    print("\nThief (50% skill) searching:")
    for i in range(3):
        result = system.search_for_traps(
            searcher_class="thief",
            searcher_race="human",
            thief_skill=50,
            trap_present=True
        )
        if result.found:
            print(f"  Attempt {i+1}: Found trap! ({result.trap.trap_type})")
        else:
            print(f"  Attempt {i+1}: No trap found")

    # Dwarf searching
    print("\nDwarf searching:")
    for i in range(3):
        result = system.search_for_traps(
            searcher_class="fighter",
            searcher_race="dwarf",
            trap_present=True
        )
        if result.found:
            print(f"  Attempt {i+1}: Found trap! ({result.trap.trap_type})")
        else:
            print(f"  Attempt {i+1}: No trap found")

    # Test 3: Disarm trap
    print("\n3. DISARMING TRAPS")
    print("-" * 70)

    trap = system.generate_trap()
    trap.detected = True  # Must detect first

    print(f"\nAttempting to disarm: {trap.trap_type}")
    print(f"Difficulty: {trap.difficulty}")

    # Skilled thief
    print("\nSkilled Thief (70% skill):")
    result = system.disarm_trap(trap, "thief", thief_skill=70)
    print(f"  Success: {result.success}")
    print(f"  Message: {result.message}")
    if result.trap_triggered:
        print(f"  Damage: {result.damage}")

    # Test 4: Trigger trap
    print("\n4. TRIGGERING TRAP")
    print("-" * 70)

    trap = system.generate_trap()
    print(f"\nTriggering: {trap.trap_type}")

    trigger_result = system.trigger_trap(trap, "fighter", victim_level=3)
    print(f"  Triggered: {trigger_result['triggered']}")
    print(f"  Damage: {trigger_result['damage']}")
    print(f"  Save made: {trigger_result['save_made']}")
    if trigger_result['effects']:
        print(f"  Effects: {', '.join(trigger_result['effects'])}")

    print("\n" + "="*70)
    print("Trap system complete!")
    print("="*70)
