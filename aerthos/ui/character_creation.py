"""
Character creation system - AD&D 1e style
"""

import random
from typing import Dict, List
from ..entities.player import PlayerCharacter, Weapon, Armor, Item, LightSource, Spell, SpellSlot, XP_TABLES
from ..engine.combat import DiceRoller


class CharacterCreator:
    """Handles character creation flow"""

    def __init__(self, game_data):
        self.game_data = game_data

    def create_character(self) -> PlayerCharacter:
        """
        Full character creation flow

        Returns:
            New PlayerCharacter
        """

        print("═══════════════════════════════════════════════════════════════")
        print("CHARACTER CREATION - AD&D 1st Edition")
        print("═══════════════════════════════════════════════════════════════")
        print()

        # Roll ability scores
        print("Rolling ability scores (3d6 in order)...")
        print()

        strength = DiceRoller.roll_3d6()
        dexterity = DiceRoller.roll_3d6()
        constitution = DiceRoller.roll_3d6()
        intelligence = DiceRoller.roll_3d6()
        wisdom = DiceRoller.roll_3d6()
        charisma = DiceRoller.roll_3d6()

        print(f"STR: {strength}")
        print(f"DEX: {dexterity}")
        print(f"CON: {constitution}")
        print(f"INT: {intelligence}")
        print(f"WIS: {wisdom}")
        print(f"CHA: {charisma}")
        print()

        # Optional rerolls
        while True:
            reroll_choice = input("Reroll these ability scores? (y/n): ").strip().lower()

            if reroll_choice not in ['y', 'yes']:
                break

            # Save current scores
            old_str, old_dex, old_con = strength, dexterity, constitution
            old_int, old_wis, old_cha = intelligence, wisdom, charisma

            # Roll new scores
            new_str = DiceRoller.roll_3d6()
            new_dex = DiceRoller.roll_3d6()
            new_con = DiceRoller.roll_3d6()
            new_int = DiceRoller.roll_3d6()
            new_wis = DiceRoller.roll_3d6()
            new_cha = DiceRoller.roll_3d6()

            print("\n--- NEW ROLLS ---")
            print(f"STR: {new_str}")
            print(f"DEX: {new_dex}")
            print(f"CON: {new_con}")
            print(f"INT: {new_int}")
            print(f"WIS: {new_wis}")
            print(f"CHA: {new_cha}")
            print("\n--- PREVIOUS ROLLS ---")
            print(f"STR: {old_str}")
            print(f"DEX: {old_dex}")
            print(f"CON: {old_con}")
            print(f"INT: {old_int}")
            print(f"WIS: {old_wis}")
            print(f"CHA: {old_cha}")
            print()

            keep_choice = input("Keep NEW rolls? (y/n): ").strip().lower()

            if keep_choice in ['y', 'yes']:
                strength = new_str
                dexterity = new_dex
                constitution = new_con
                intelligence = new_int
                wisdom = new_wis
                charisma = new_cha
                print("✓ Keeping new rolls!\n")
            else:
                print("✓ Keeping previous rolls!\n")

        print("Final ability scores:")
        print(f"STR: {strength}")
        print(f"DEX: {dexterity}")
        print(f"CON: {constitution}")
        print(f"INT: {intelligence}")
        print(f"WIS: {wisdom}")
        print(f"CHA: {charisma}")
        print()

        # Roll exceptional strength if Fighter with 18 STR
        strength_percentile = 0

        # Choose name
        name = input("Enter your character's name: ").strip()
        if not name:
            name = "Adventurer"

        # Choose race
        print("\nAvailable Races:")
        print("1. Human (no modifiers, no restrictions)")
        print("2. Elf (+1 DEX, -1 CON, infravision, cannot be Cleric)")
        print("3. Dwarf (+1 CON, -1 CHA, infravision, cannot be Magic-User)")
        print("4. Halfling (+1 DEX, -1 STR, cannot be Magic-User or Cleric)")

        race_choice = input("\nChoose race (1-4): ").strip()
        race_map = {'1': 'Human', '2': 'Elf', '3': 'Dwarf', '4': 'Halfling'}
        race = race_map.get(race_choice, 'Human')

        # Apply racial modifiers
        if race == 'Elf':
            dexterity += 1
            constitution -= 1
        elif race == 'Dwarf':
            constitution += 1
            charisma -= 1
        elif race == 'Halfling':
            dexterity += 1
            strength -= 1

        # Choose class
        print(f"\nAvailable Classes for {race}:")
        available_classes = self._get_available_classes(race)

        for i, cls in enumerate(available_classes, 1):
            print(f"{i}. {cls}")

        class_choice = input(f"\nChoose class (1-{len(available_classes)}): ").strip()

        try:
            class_idx = int(class_choice) - 1
            if 0 <= class_idx < len(available_classes):
                char_class = available_classes[class_idx]
            else:
                char_class = available_classes[0]
        except ValueError:
            char_class = available_classes[0]

        # Handle exceptional strength for Fighters
        if char_class == 'Fighter' and strength == 18:
            strength_percentile = random.randint(1, 100)
            print(f"\nExceptional Strength! You rolled 18/{strength_percentile:02d}!")

        # Roll HP
        class_data = self.game_data.classes[char_class]
        hit_die = class_data['hit_die']

        hp = max(1, DiceRoller.roll(hit_die))

        # Apply CON bonus
        con_bonus = self._get_con_bonus(constitution)
        hp = max(1, hp + con_bonus)

        print(f"\nStarting HP: {hp}")

        # Get class-specific data
        saves = class_data['saves']
        thac0 = class_data['thac0_base']

        # Get XP needed for level 2
        xp_to_level_2 = XP_TABLES.get(char_class, [0, 2000])[1]

        # Create character
        player = PlayerCharacter(
            name=name,
            race=race,
            char_class=char_class,
            level=1,
            strength=strength,
            dexterity=dexterity,
            constitution=constitution,
            intelligence=intelligence,
            wisdom=wisdom,
            charisma=charisma,
            strength_percentile=strength_percentile,
            hp_current=hp,
            hp_max=hp,
            ac=10,
            thac0=thac0,
            save_poison=saves['poison'],
            save_rod_staff_wand=saves['rod_staff_wand'],
            save_petrify_paralyze=saves['petrify_paralyze'],
            save_breath=saves['breath'],
            save_spell=saves['spell'],
            xp=0,
            xp_to_next_level=xp_to_level_2
        )

        # Add starting equipment
        self._add_starting_equipment(player, char_class)

        # Add thief skills if thief
        if char_class == 'Thief':
            player.thief_skills = class_data['skills'].copy()

        # Add spell slots if spellcaster
        if char_class in ['Magic-User', 'Cleric']:
            num_slots = class_data['spell_slots_level_1'][0]
            for _ in range(num_slots):
                player.add_spell_slot(1)

        print("\n═══════════════════════════════════════════════════════════════")
        print(f"Character created: {name} the {race} {char_class}")
        print("═══════════════════════════════════════════════════════════════")
        print()

        return player

    def _get_available_classes(self, race: str) -> List[str]:
        """Get available classes for a race"""

        all_classes = ['Fighter', 'Cleric', 'Magic-User', 'Thief']

        if race == 'Human':
            return all_classes
        elif race == 'Elf':
            return ['Fighter', 'Magic-User', 'Thief']
        elif race == 'Dwarf':
            return ['Fighter', 'Cleric', 'Thief']
        elif race == 'Halfling':
            return ['Fighter', 'Thief']

        return all_classes

    def _get_con_bonus(self, constitution: int) -> int:
        """Get HP bonus from CON"""

        if constitution >= 17:
            return 3
        elif constitution >= 16:
            return 2
        elif constitution >= 15:
            return 1
        elif constitution <= 6:
            return -1
        elif constitution <= 3:
            return -2
        return 0

    def _add_starting_equipment(self, player: PlayerCharacter, char_class: str):
        """Add starting equipment based on class"""

        # Everyone gets basic supplies (use proper item types!)
        torch1 = LightSource(name="Torch", weight=1, burn_time_turns=6, light_radius=30)
        torch2 = LightSource(name="Torch", weight=1, burn_time_turns=6, light_radius=30)
        ration1 = Item(name="Rations (1 day)", item_type="consumable", weight=1, properties={'healing': '0'})
        ration2 = Item(name="Rations (1 day)", item_type="consumable", weight=1, properties={'healing': '0'})

        player.inventory.add_item(torch1)
        player.inventory.add_item(torch2)
        player.inventory.add_item(ration1)
        player.inventory.add_item(ration2)
        player.gold = 10  # Starting gold

        # Class-specific equipment
        if char_class == 'Fighter':
            longsword = Weapon(name="Longsword", weight=4, damage_sm="1d8", damage_l="1d12", speed_factor=5)
            chain = Armor(name="Chain Mail", weight=30, ac_bonus=5)
            shield = Armor(name="Shield", weight=10, ac_bonus=1)

            player.inventory.add_item(longsword)
            player.inventory.add_item(chain)
            player.inventory.add_item(shield)

            player.equip_weapon(longsword)
            player.equip_armor(chain)
            player.equipment.shield = shield

            player.ac = 5  # Chain mail
            player.ac -= 1  # Shield

        elif char_class == 'Cleric':
            mace = Weapon(name="Mace", weight=8, damage_sm="1d6", damage_l="1d6", speed_factor=7)
            chain = Armor(name="Chain Mail", weight=30, ac_bonus=5)
            shield = Armor(name="Shield", weight=10, ac_bonus=1)

            player.inventory.add_item(mace)
            player.inventory.add_item(chain)
            player.inventory.add_item(shield)

            player.equip_weapon(mace)
            player.equip_armor(chain)
            player.equipment.shield = shield

            player.ac = 5
            player.ac -= 1

        elif char_class == 'Magic-User':
            staff = Weapon(name="Staff", weight=4, damage_sm="1d6", damage_l="1d6", speed_factor=4)
            dagger = Weapon(name="Dagger", weight=1, damage_sm="1d4", damage_l="1d3", speed_factor=2)

            player.inventory.add_item(staff)
            player.inventory.add_item(dagger)

            player.equip_weapon(dagger)

        elif char_class == 'Thief':
            shortsword = Weapon(name="Shortsword", weight=3, damage_sm="1d6", damage_l="1d8", speed_factor=3)
            leather = Armor(name="Leather Armor", weight=15, ac_bonus=2)

            player.inventory.add_item(shortsword)
            player.inventory.add_item(leather)

            player.equip_weapon(shortsword)
            player.equip_armor(leather)

            player.ac = 8  # Leather armor

        # Equip a torch
        torch = LightSource(name="Torch", weight=1, burn_time_turns=6)
        player.equip_light(torch)
