"""
Character creation system - AD&D 1e style
"""

import random
from typing import Dict, List
from ..entities.player import PlayerCharacter, Weapon, Armor, Shield, Item, LightSource, Spell, SpellSlot, XP_TABLES
from ..engine.combat import DiceRoller
from ..systems.armor_system import ArmorSystem


class CharacterCreator:
    """Handles character creation flow"""

    def __init__(self, game_data):
        self.game_data = game_data
        self.armor_system = ArmorSystem()

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

        # Choose race (with stat requirements)
        print("\nAvailable Races:")
        available_races = self._get_available_races(strength, dexterity, constitution, intelligence, wisdom, charisma)

        race_list = []
        race_index = 1
        for race_name in ['Human', 'Elf', 'Dwarf', 'Halfling', 'Half-Elf', 'Half-Orc', 'Gnome']:
            race_data = self.game_data.races.get(race_name, {})
            is_available, reason = self._check_race_requirements(race_name, strength, dexterity, constitution, intelligence, wisdom, charisma)

            if is_available:
                mods = race_data.get('ability_modifiers', {})
                mod_str = self._format_ability_modifiers(mods)
                print(f"{race_index}. {race_name} {mod_str}")
                race_list.append(race_name)
                race_index += 1
            else:
                print(f"   {race_name} - UNAVAILABLE ({reason})")

        race_choice = input(f"\nChoose race (1-{len(race_list)}): ").strip()

        try:
            race_idx = int(race_choice) - 1
            if 0 <= race_idx < len(race_list):
                race = race_list[race_idx]
            else:
                race = race_list[0] if race_list else 'Human'
        except ValueError:
            race = race_list[0] if race_list else 'Human'

        # Apply racial modifiers
        race_data = self.game_data.races[race]
        for ability, modifier in race_data['ability_modifiers'].items():
            if ability == 'strength':
                strength += modifier
            elif ability == 'dexterity':
                dexterity += modifier
            elif ability == 'constitution':
                constitution += modifier
            elif ability == 'intelligence':
                intelligence += modifier
            elif ability == 'wisdom':
                wisdom += modifier
            elif ability == 'charisma':
                charisma += modifier

        # Apply racial maximums
        maximums = race_data.get('ability_maximums', {})
        if 'strength' in maximums:
            strength = min(strength, maximums['strength'])
        if 'dexterity' in maximums:
            dexterity = min(dexterity, maximums['dexterity'])
        if 'constitution' in maximums:
            constitution = min(constitution, maximums['constitution'])
        if 'intelligence' in maximums:
            intelligence = min(intelligence, maximums['intelligence'])
        if 'wisdom' in maximums:
            wisdom = min(wisdom, maximums['wisdom'])
        if 'charisma' in maximums:
            charisma = min(charisma, maximums['charisma'])

        # Choose class (with stat and race requirements)
        print(f"\nAvailable Classes for {race}:")
        available_classes = []
        class_index = 1

        all_classes = ['Fighter', 'Ranger', 'Paladin', 'Cleric', 'Druid', 'Magic-User', 'Illusionist', 'Thief', 'Assassin', 'Monk', 'Bard']

        for class_name in all_classes:
            if class_name not in self.game_data.classes:
                continue

            is_available, reason = self._check_class_requirements(class_name, race, strength, dexterity, constitution, intelligence, wisdom, charisma)

            if is_available:
                class_data = self.game_data.classes[class_name]
                desc = class_data.get('description', '')
                print(f"{class_index}. {class_name} - {desc}")
                available_classes.append(class_name)
                class_index += 1
            else:
                print(f"   {class_name} - UNAVAILABLE ({reason})")

        if not available_classes:
            print("\nNo classes available with these stats and race! Defaulting to Fighter.")
            available_classes = ['Fighter']

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

        # Add skills for skill-based classes
        if char_class in ['Thief', 'Assassin']:
            player.thief_skills = class_data.get('skills', {}).copy()
        elif char_class == 'Bard':
            player.thief_skills = class_data.get('skills', {}).copy()
        elif char_class == 'Monk':
            # Monks have special abilities but no thief skills
            pass

        # Add spell slots if spellcaster
        if char_class in ['Magic-User', 'Illusionist', 'Cleric', 'Druid', 'Ranger', 'Paladin', 'Bard']:
            spell_slots_key = 'spell_slots_level_1'
            if spell_slots_key in class_data:
                num_slots = class_data[spell_slots_key][0]
                if num_slots > 0:
                    for _ in range(num_slots):
                        player.add_spell_slot(1)

                    # Give starting spells
                    self._add_starting_spells(player, char_class)

        print("\n═══════════════════════════════════════════════════════════════")
        print(f"Character created: {name} the {race} {char_class}")
        print("═══════════════════════════════════════════════════════════════")
        print()

        return player

    def _get_available_races(self, str_val, dex_val, con_val, int_val, wis_val, cha_val) -> List[str]:
        """Get list of available races based on ability scores"""
        available = []
        for race_name in ['Human', 'Elf', 'Dwarf', 'Halfling', 'Half-Elf', 'Half-Orc', 'Gnome']:
            is_available, _ = self._check_race_requirements(race_name, str_val, dex_val, con_val, int_val, wis_val, cha_val)
            if is_available:
                available.append(race_name)
        return available

    def _check_race_requirements(self, race_name: str, str_val, dex_val, con_val, int_val, wis_val, cha_val):
        """Check if character meets race requirements. Returns (is_available, reason)"""
        if race_name not in self.game_data.races:
            return False, "Race not found"

        race_data = self.game_data.races[race_name]
        minimums = race_data.get('ability_minimums', {})

        stats = {
            'strength': str_val,
            'dexterity': dex_val,
            'constitution': con_val,
            'intelligence': int_val,
            'wisdom': wis_val,
            'charisma': cha_val
        }

        for ability, min_val in minimums.items():
            if stats.get(ability, 0) < min_val:
                return False, f"Need {ability.upper()} {min_val}+"

        return True, ""

    def _check_class_requirements(self, class_name: str, race: str, str_val, dex_val, con_val, int_val, wis_val, cha_val):
        """Check if character meets class requirements. Returns (is_available, reason)"""
        if class_name not in self.game_data.classes:
            return False, "Class not found"

        # Check race restrictions
        race_data = self.game_data.races.get(race, {})
        restrictions = race_data.get('class_restrictions', [])
        if class_name in restrictions:
            return False, f"{race} cannot be {class_name}"

        # Check ability minimums
        class_data = self.game_data.classes[class_name]
        minimums = class_data.get('ability_minimums', {})

        stats = {
            'strength': str_val,
            'dexterity': dex_val,
            'constitution': con_val,
            'intelligence': int_val,
            'wisdom': wis_val,
            'charisma': cha_val
        }

        for ability, min_val in minimums.items():
            if stats.get(ability, 0) < min_val:
                return False, f"Need {ability.upper()} {min_val}+"

        return True, ""

    def _format_ability_modifiers(self, modifiers: Dict[str, int]) -> str:
        """Format ability modifiers for display"""
        mods = []
        for ability, value in modifiers.items():
            if value > 0:
                mods.append(f"+{value} {ability[:3].upper()}")
            elif value < 0:
                mods.append(f"{value} {ability[:3].upper()}")

        return f"({', '.join(mods)})" if mods else ""

    def _get_available_classes(self, race: str) -> List[str]:
        """Get available classes for a race (legacy method)"""
        race_data = self.game_data.races.get(race, {})
        restrictions = race_data.get('class_restrictions', [])

        all_classes = ['Fighter', 'Ranger', 'Paladin', 'Cleric', 'Druid', 'Magic-User', 'Illusionist', 'Thief', 'Assassin', 'Monk', 'Bard']
        available = [c for c in all_classes if c not in restrictions and c in self.game_data.classes]

        return available if available else ['Fighter']

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
        torch1 = LightSource(name="Torch", weight=0.1, burn_time_turns=6, light_radius=30)  # 1 GP = 0.1 lbs
        torch2 = LightSource(name="Torch", weight=0.1, burn_time_turns=6, light_radius=30)
        ration1 = Item(name="Rations (1 day)", item_type="consumable", weight=0.1, properties={'healing': '0'})
        ration2 = Item(name="Rations (1 day)", item_type="consumable", weight=0.1, properties={'healing': '0'})

        player.inventory.add_item(torch1)
        player.inventory.add_item(torch2)
        player.inventory.add_item(ration1)
        player.inventory.add_item(ration2)
        player.gold = 30  # Starting gold

        # Class-specific equipment
        if char_class in ['Fighter', 'Ranger', 'Paladin']:
            longsword = Weapon(name="Longsword", weight=0.4, damage_sm="1d8", damage_l="1d12", speed_factor=5)  # 4 GP = 0.4 lbs
            chain = self.armor_system.create_armor('chain_mail')
            shield = self.armor_system.create_shield('shield_small')

            player.inventory.add_item(longsword)
            player.inventory.add_item(chain)
            player.inventory.add_item(shield)

            player.equip_weapon(longsword)
            player.equipment.armor = chain
            player.equipment.shield = shield
            # Calculate AC: armor base AC - shield bonus
            player.ac = chain.ac - shield.ac_bonus

        elif char_class in ['Cleric', 'Druid']:
            mace = Weapon(name="Mace", weight=0.8, damage_sm="1d6", damage_l="1d6", speed_factor=7)  # 8 GP = 0.8 lbs
            chain = self.armor_system.create_armor('chain_mail')
            shield = self.armor_system.create_shield('shield_small')

            player.inventory.add_item(mace)
            player.inventory.add_item(chain)
            player.inventory.add_item(shield)

            player.equip_weapon(mace)
            player.equipment.armor = chain
            player.equipment.shield = shield
            # Calculate AC: armor base AC - shield bonus
            player.ac = chain.ac - shield.ac_bonus

        elif char_class in ['Magic-User', 'Illusionist']:
            staff = Weapon(name="Staff", weight=0.4, damage_sm="1d6", damage_l="1d6", speed_factor=4)  # 4 GP = 0.4 lbs
            dagger = Weapon(name="Dagger", weight=0.1, damage_sm="1d4", damage_l="1d3", speed_factor=2)  # 1 GP = 0.1 lbs

            player.inventory.add_item(staff)
            player.inventory.add_item(dagger)

            player.equip_weapon(dagger)

        elif char_class in ['Thief', 'Assassin', 'Bard']:
            shortsword = Weapon(name="Shortsword", weight=0.3, damage_sm="1d6", damage_l="1d8", speed_factor=3)  # 3 GP = 0.3 lbs
            leather = self.armor_system.create_armor('leather')

            player.inventory.add_item(shortsword)
            player.inventory.add_item(leather)

            player.equip_weapon(shortsword)
            player.equipment.armor = leather
            # Calculate AC: armor base AC (no shield)
            player.ac = leather.ac

        elif char_class == 'Monk':
            # Monks use their fists and wear no armor
            staff = Weapon(name="Staff", weight=0.4, damage_sm="1d6", damage_l="1d6", speed_factor=4)  # 4 GP = 0.4 lbs
            player.inventory.add_item(staff)
            player.equip_weapon(staff)

        # Equip a torch
        torch = LightSource(name="Torch", weight=0.1, burn_time_turns=6)  # 1 GP = 0.1 lbs
        player.equip_light(torch)

    def _add_starting_spells(self, player: PlayerCharacter, char_class: str):
        """Add starting spells for spellcasters"""

        if char_class in ['Magic-User', 'Illusionist']:
            # Mages start with 2-4 level 1 spells
            starting_spell_ids = ['magic_missile', 'sleep', 'detect_magic']

            print("\nStarting Spells:")
            for spell_id in starting_spell_ids:
                if spell_id in self.game_data.spells:
                    spell_data = self.game_data.spells[spell_id]
                    # Check class availability
                    if char_class not in spell_data.get('class_availability', []):
                        continue

                    spell = Spell(
                        name=spell_data['name'],
                        level=spell_data['level'],
                        school=spell_data['school'],
                        casting_time=spell_data['casting_time'],
                        range=spell_data['range'],
                        duration=spell_data['duration'],
                        area_of_effect=spell_data['area'],
                        saving_throw=spell_data['saving_throw'],
                        components=spell_data['components'],
                        description=spell_data['description'],
                        class_availability=spell_data['class_availability']
                    )
                    player.spells_known.append(spell)
                    print(f"  - {spell.name}: {spell.description}")

        elif char_class in ['Cleric', 'Druid']:
            # Divine casters know all spells of their class
            print(f"\nAs a {char_class}, you have access to all level 1 {char_class} spells.")
            print("Use 'spells' to see available spells, 'memorize <spell>' to prepare them.")

            for spell_id, spell_data in self.game_data.spells.items():
                if char_class in spell_data.get('class_availability', []) and spell_data['level'] == 1:
                    spell = Spell(
                        name=spell_data['name'],
                        level=spell_data['level'],
                        school=spell_data['school'],
                        casting_time=spell_data['casting_time'],
                        range=spell_data['range'],
                        duration=spell_data['duration'],
                        area_of_effect=spell_data['area'],
                        saving_throw=spell_data['saving_throw'],
                        components=spell_data['components'],
                        description=spell_data['description'],
                        class_availability=spell_data['class_availability']
                    )
                    player.spells_known.append(spell)
                    print(f"  - {spell.name}")

        elif char_class == 'Bard':
            # Bards have limited spells
            print("\nAs a Bard, you know a limited selection of spells.")
            for spell_id in ['charm_person', 'detect_magic']:
                if spell_id in self.game_data.spells:
                    spell_data = self.game_data.spells[spell_id]
                    spell = Spell(
                        name=spell_data['name'],
                        level=spell_data['level'],
                        school=spell_data['school'],
                        casting_time=spell_data['casting_time'],
                        range=spell_data['range'],
                        duration=spell_data['duration'],
                        area_of_effect=spell_data['area'],
                        saving_throw=spell_data['saving_throw'],
                        components=spell_data['components'],
                        description=spell_data['description'],
                        class_availability=spell_data.get('class_availability', [])
                    )
                    player.spells_known.append(spell)
                    print(f"  - {spell.name}")

    def quick_create(self, name: str, race: str, char_class: str) -> PlayerCharacter:
        """
        Quick character creation for demos/testing

        Args:
            name: Character name
            race: Race (Human, Elf, Dwarf, Halfling)
            char_class: Class (Fighter, Cleric, Magic-User, Thief)

        Returns:
            PlayerCharacter with reasonable stats
        """

        # Generate decent stats
        strength = random.randint(13, 16)
        dexterity = random.randint(13, 16)
        constitution = random.randint(13, 16)
        intelligence = random.randint(13, 16)
        wisdom = random.randint(13, 16)
        charisma = random.randint(10, 14)

        # Optimize primary stat for class
        if char_class == 'Fighter':
            strength = 16
        elif char_class == 'Cleric':
            wisdom = 16
        elif char_class == 'Magic-User':
            intelligence = 16
        elif char_class == 'Thief':
            dexterity = 16

        strength_percentile = 0

        # Apply racial modifiers (same as main character creation)
        if race == 'Elf':
            dexterity += 1
            constitution -= 1
        elif race == 'Dwarf':
            constitution += 1
            charisma -= 1
        elif race == 'Halfling':
            dexterity += 1
            strength -= 1

        # Handle exceptional strength for Fighters
        if char_class == 'Fighter' and strength == 18:
            strength_percentile = 50

        # Roll HP
        class_data = self.game_data.classes[char_class]
        hit_die = class_data['hit_die']
        hp = max(1, DiceRoller.roll(hit_die))

        # Apply CON bonus
        con_bonus = self._get_con_bonus(constitution)
        hp = max(1, hp + con_bonus)

        # Get class-specific data
        saves = class_data['saves']
        thac0 = class_data['thac0_base']

        # Get XP needed for level 2
        xp_to_level_2 = XP_TABLES.get(char_class, [0, 2000])[1]

        # Create character (same as main method)
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

        # Add skills for skill-based classes
        if char_class in ['Thief', 'Assassin']:
            player.thief_skills = class_data.get('skills', {}).copy()
        elif char_class == 'Bard':
            player.thief_skills = class_data.get('skills', {}).copy()

        # Add spell slots if spellcaster
        if char_class in ['Magic-User', 'Illusionist', 'Cleric', 'Druid', 'Ranger', 'Paladin', 'Bard']:
            spell_slots_key = 'spell_slots_level_1'
            if spell_slots_key in class_data:
                num_slots = class_data[spell_slots_key][0]
                if num_slots > 0:
                    for _ in range(num_slots):
                        player.add_spell_slot(1)

                    # Add starting spells (silently for quick creation)
                    if char_class in ['Magic-User', 'Illusionist']:
                        for spell_id in ['magic_missile', 'sleep']:
                            if spell_id in self.game_data.spells:
                                spell_data = self.game_data.spells[spell_id]
                                if char_class in spell_data.get('class_availability', []):
                                    spell = Spell(
                                        name=spell_data['name'],
                                        level=spell_data['level'],
                                        school=spell_data['school'],
                                        casting_time=spell_data['casting_time'],
                                        range=spell_data['range'],
                                        duration=spell_data['duration'],
                                        area_of_effect=spell_data['area'],
                                        saving_throw=spell_data['saving_throw'],
                                        components=spell_data['components'],
                                        description=spell_data['description'],
                                        class_availability=spell_data['class_availability']
                                    )
                                    player.spells_known.append(spell)

                    elif char_class in ['Cleric', 'Druid']:
                        for spell_id, spell_data in self.game_data.spells.items():
                            if char_class in spell_data.get('class_availability', []) and spell_data['level'] == 1:
                                spell = Spell(
                                    name=spell_data['name'],
                                    level=spell_data['level'],
                                    school=spell_data['school'],
                                    casting_time=spell_data['casting_time'],
                                    range=spell_data['range'],
                                    duration=spell_data['duration'],
                                    area_of_effect=spell_data['area'],
                                    saving_throw=spell_data['saving_throw'],
                                    components=spell_data['components'],
                                    description=spell_data['description'],
                                    class_availability=spell_data['class_availability']
                                )
                                player.spells_known.append(spell)

        return player
