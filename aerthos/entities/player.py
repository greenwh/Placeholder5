"""
PlayerCharacter class - extends Character with inventory, spells, and XP
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from .character import Character

# AD&D 1e Experience Point Tables
XP_TABLES = {
    'Fighter': [0, 2000, 4000, 8000, 16000, 32000, 64000, 125000, 250000, 500000, 750000],
    'Cleric': [0, 1500, 3000, 6000, 13000, 27500, 55000, 110000, 225000, 450000, 675000],
    'Magic-User': [0, 2500, 5000, 10000, 22500, 40000, 60000, 90000, 135000, 250000, 375000],
    'Thief': [0, 1250, 2500, 5000, 10000, 20000, 40000, 70000, 110000, 160000, 220000]
}


@dataclass
class Item:
    """Base item class"""
    name: str
    item_type: str = "generic"  # Default item type
    weight: float = 0.0
    properties: Dict = field(default_factory=dict)
    description: str = ""

    def __str__(self):
        return self.name


@dataclass
class Weapon(Item):
    """Weapon with damage dice"""
    damage_sm: str = "1d4"  # vs Small/Medium
    damage_l: str = "1d4"   # vs Large
    speed_factor: int = 5
    magic_bonus: int = 0    # +1, +2, etc. for magic weapons

    def __post_init__(self):
        self.item_type = 'weapon'


@dataclass
class Armor(Item):
    """Armor with AC rating and properties"""
    ac: int = 10  # Base AC when wearing this armor
    armor_type: str = "light"  # light, heavy, very_heavy
    movement_rate: int = 12  # Movement rate in inches (dungeon)
    magic_bonus: int = 0  # +1, +2, etc. for magic armor (improves AC further)
    allowed_classes: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.item_type = 'armor'

    def get_effective_ac(self) -> int:
        """Get effective AC including magic bonus"""
        return self.ac - self.magic_bonus


@dataclass
class Shield(Item):
    """Shield with AC bonus"""
    ac_bonus: int = 1  # How much it improves AC (usually 1)
    max_attacks_blocked: int = 1  # How many attacks can be blocked per round
    magic_bonus: int = 0  # +1, +2, etc. for magic shields
    allowed_classes: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.item_type = 'shield'

    def get_effective_bonus(self) -> int:
        """Get effective AC bonus including magic"""
        return self.ac_bonus + self.magic_bonus


@dataclass
class LightSource(Item):
    """Light source with burn time"""
    burn_time_turns: int = 6
    turns_remaining: int = 6
    light_radius: int = 30

    def __post_init__(self):
        self.item_type = 'light_source'
        self.turns_remaining = self.burn_time_turns


@dataclass
class Spell:
    """Spell definition"""
    name: str
    level: int
    school: str
    casting_time: str
    range: str
    duration: str
    area_of_effect: str
    saving_throw: str
    components: str
    description: str
    class_availability: List[str] = field(default_factory=list)


@dataclass
class SpellSlot:
    """A memorized spell slot"""
    level: int
    spell: Optional[Spell] = None
    is_used: bool = False


class Inventory:
    """Character inventory with encumbrance"""

    def __init__(self, max_weight: int = 100):
        self.items: List[Item] = []
        self.max_weight = max_weight

    @property
    def current_weight(self) -> float:
        """Total weight carried"""
        return sum(item.weight for item in self.items)

    @property
    def is_encumbered(self) -> bool:
        """Check if over weight limit"""
        return self.current_weight > self.max_weight

    def add_item(self, item: Item) -> bool:
        """Add item to inventory"""
        self.items.append(item)
        return True

    def remove_item(self, item_name: str) -> Optional[Item]:
        """Remove and return item by name (supports partial matching)"""
        search_lower = item_name.lower().replace('_', ' ')

        # First try exact match
        for item in self.items:
            item_name_normalized = item.name.lower().replace('_', ' ')
            if item_name_normalized == search_lower:
                self.items.remove(item)
                return item

        # Then try partial match (search term is in item name)
        for item in self.items:
            item_name_normalized = item.name.lower().replace('_', ' ')
            if search_lower in item_name_normalized:
                self.items.remove(item)
                return item

        return None

    def has_item(self, item_name: str) -> bool:
        """Check if item exists in inventory"""
        return any(item.name.lower() == item_name.lower() for item in self.items)

    def get_item(self, item_name: str) -> Optional[Item]:
        """Get item by name without removing (supports partial matching)"""
        search_lower = item_name.lower().replace('_', ' ')

        # First try exact match
        for item in self.items:
            item_name_normalized = item.name.lower().replace('_', ' ')
            if item_name_normalized == search_lower:
                return item

        # Then try partial match (search term is in item name)
        for item in self.items:
            item_name_normalized = item.name.lower().replace('_', ' ')
            if search_lower in item_name_normalized:
                return item

        return None

    def get_items_by_type(self, item_type: str) -> List[Item]:
        """Get all items of a specific type"""
        return [item for item in self.items if item.item_type == item_type]

    def list_items(self) -> List[str]:
        """Get list of item names"""
        return [item.name for item in self.items]


class Equipment:
    """Equipped items"""

    def __init__(self):
        self.weapon: Optional[Weapon] = None
        self.armor: Optional[Armor] = None
        self.shield: Optional[Shield] = None
        self.light_source: Optional[LightSource] = None
        self.helmet: Optional[Item] = None

    def get_total_ac(self, base_ac: int = 10, dex_modifier: int = 0) -> int:
        """
        Calculate total AC from equipment

        Args:
            base_ac: Character's base AC (10 for unarmored)
            dex_modifier: DEX defensive adjustment (negative improves AC)

        Returns:
            Final AC (lower is better)
        """
        # Start with armor AC if worn, otherwise base AC
        if self.armor:
            ac = self.armor.get_effective_ac()
        else:
            ac = base_ac

        # Add shield bonus (reduces AC, so we subtract)
        if self.shield:
            ac -= self.shield.get_effective_bonus()

        # Apply DEX modifier (negative improves AC)
        ac += dex_modifier

        return ac

    def get_movement_rate(self, base_movement: int = 12, is_magic_armor: bool = False) -> int:
        """
        Get movement rate based on armor

        Args:
            base_movement: Character's base movement rate
            is_magic_armor: Whether the armor is magical (negates weight penalty)

        Returns:
            Movement rate in inches
        """
        if not self.armor or is_magic_armor:
            return base_movement

        return self.armor.movement_rate

    def get_total_weight(self) -> float:
        """Get total weight of equipped items in GP"""
        weight = 0.0
        if self.weapon:
            weight += self.weapon.weight
        if self.armor:
            weight += self.armor.weight
        if self.shield:
            weight += self.shield.weight
        if self.helmet:
            weight += self.helmet.weight
        if self.light_source:
            weight += self.light_source.weight
        return weight


@dataclass
class PlayerCharacter(Character):
    """Player Character with inventory, spells, and progression"""

    # Inventory
    inventory: Inventory = field(default_factory=Inventory)
    equipment: Equipment = field(default_factory=Equipment)
    gold: int = 0

    # Spells (for spellcasters)
    spells_known: List[Spell] = field(default_factory=list)
    spells_memorized: List[SpellSlot] = field(default_factory=list)

    # Thief Skills (if thief class)
    thief_skills: Dict[str, int] = field(default_factory=dict)

    # Experience
    xp: int = 0
    xp_to_next_level: int = 2000

    def __post_init__(self):
        """Initialize inventory with appropriate max weight"""
        # Max weight based on STR (AD&D encumbrance)
        if self.strength >= 18:
            if self.strength_percentile >= 91:
                max_weight = 250
            elif self.strength_percentile >= 51:
                max_weight = 200
            else:
                max_weight = 150
        elif self.strength >= 17:
            max_weight = 140
        elif self.strength >= 16:
            max_weight = 120
        else:
            max_weight = 50 + (self.strength * 5)

        self.inventory = Inventory(max_weight=max_weight)
        self.equipment = Equipment()

    def has_light(self) -> bool:
        """Check if character has an active light source"""
        return (self.equipment.light_source is not None and
                self.equipment.light_source.turns_remaining > 0)

    def get_effective_ac(self) -> int:
        """Calculate effective AC including DEX bonus and equipment"""
        base_ac = self.ac
        equipment_ac = self.equipment.get_total_ac(base_ac)
        dex_bonus = self.get_ac_bonus()
        return equipment_ac + dex_bonus

    def can_use_weapon(self, weapon: Weapon) -> Tuple[bool, str]:
        """
        Check if character's class allows them to use this weapon

        Returns:
            (can_use: bool, message: str)
        """
        weapon_name_lower = weapon.name.lower()

        # AD&D 1e weapon restrictions by class
        if self.char_class == 'Fighter':
            return (True, "")  # Fighters can use all weapons

        elif self.char_class == 'Cleric':
            # Clerics can only use bludgeoning weapons (no bladed)
            allowed = ['mace', 'flail', 'hammer', 'staff', 'club', 'sling']
            if any(w in weapon_name_lower for w in allowed):
                return (True, "")
            return (False, f"Clerics cannot use bladed weapons like {weapon.name}! Religious restrictions forbid shedding blood.")

        elif self.char_class == 'Magic-User':
            # Magic-Users very limited - dagger, staff, dart, sling
            allowed = ['dagger', 'staff', 'dart', 'sling']
            if any(w in weapon_name_lower for w in allowed):
                return (True, "")
            return (False, f"Magic-Users cannot use {weapon.name}! They lack martial training and can only use daggers, staves, darts, and slings.")

        elif self.char_class == 'Thief':
            # Thieves limited selection - no two-handed weapons or heavy weapons
            # Can use: dagger, shortsword, club, hand axe, short bow, light crossbow
            allowed = ['dagger', 'shortsword', 'short sword', 'club', 'hand axe', 'short bow', 'crossbow']
            disallowed = ['longsword', 'long sword', 'greatsword', 'great sword', 'battle axe',
                         'two-handed', 'polearm', 'pike', 'halberd']

            if any(w in weapon_name_lower for w in disallowed):
                return (False, f"Thieves cannot use heavy weapons like {weapon.name}! Too cumbersome for their fighting style.")
            if any(w in weapon_name_lower for w in allowed):
                return (True, "")

            # Default for thieves - be permissive for light weapons
            return (True, "")

        # Unknown class - allow by default
        return (True, "")

    def equip_weapon(self, weapon: Weapon):
        """Equip a weapon"""
        self.equipment.weapon = weapon

    def equip_armor(self, armor: Armor):
        """Equip armor or shield"""
        if armor.name.lower().find('shield') != -1:
            self.equipment.shield = armor
        else:
            self.equipment.armor = armor

    def equip_light(self, light: LightSource):
        """Equip a light source"""
        self.equipment.light_source = light

    def consume_ration(self) -> bool:
        """Consume one ration from inventory"""
        ration = self.inventory.get_item("Rations (1 day)")
        if ration:
            self.inventory.remove_item("Rations (1 day)")
            return True
        return False

    def add_spell_slot(self, level: int):
        """Add an empty spell slot"""
        self.spells_memorized.append(SpellSlot(level=level))

    def memorize_spell(self, spell: Spell) -> bool:
        """Memorize a spell into an available slot"""
        if spell not in self.spells_known:
            return False

        # Find empty slot of correct level
        for slot in self.spells_memorized:
            if slot.level == spell.level and slot.spell is None:
                slot.spell = spell
                slot.is_used = False
                return True
        return False

    def has_spell_memorized(self, spell_name: str) -> bool:
        """Check if a spell is memorized and available (supports partial matching)"""
        search_lower = spell_name.lower()

        # First try exact match
        for slot in self.spells_memorized:
            if (slot.spell and
                slot.spell.name.lower() == search_lower and
                not slot.is_used):
                return True

        # Then try partial match (search term is in spell name)
        for slot in self.spells_memorized:
            if (slot.spell and
                search_lower in slot.spell.name.lower() and
                not slot.is_used):
                return True

        return False

    def use_spell_slot(self, spell_name: str) -> Optional[Spell]:
        """Use a spell slot, returns the spell if successful (supports partial matching)"""
        search_lower = spell_name.lower()

        # First try exact match
        for slot in self.spells_memorized:
            if (slot.spell and
                slot.spell.name.lower() == search_lower and
                not slot.is_used):
                slot.is_used = True
                return slot.spell

        # Then try partial match (search term is in spell name)
        for slot in self.spells_memorized:
            if (slot.spell and
                search_lower in slot.spell.name.lower() and
                not slot.is_used):
                slot.is_used = True
                return slot.spell

        return None

    def restore_spells(self):
        """Restore all spell slots (after rest)"""
        for slot in self.spells_memorized:
            slot.is_used = False

    def gain_xp(self, amount: int) -> Optional[str]:
        """
        Gain experience points and check for level up

        Returns:
            Level up message if leveled up, None otherwise
        """
        self.xp += amount

        # Check if we can level up
        if self.char_class in XP_TABLES:
            xp_table = XP_TABLES[self.char_class]

            # Find next level in table
            if self.level < len(xp_table) - 1:
                xp_needed = xp_table[self.level]

                if self.xp >= xp_needed:
                    return self._level_up()

        return None

    def _level_up(self) -> str:
        """
        Level up the character

        Returns:
            Level up message
        """
        from ..engine.combat import DiceRoller

        old_level = self.level
        self.level += 1

        messages = []
        messages.append(f"\n✨ LEVEL UP! You are now level {self.level}! ✨")

        # Roll HP increase based on class hit die
        hit_dice_map = {
            'Fighter': 'd10',
            'Cleric': 'd8',
            'Magic-User': 'd4',
            'Thief': 'd6'
        }

        hit_die = hit_dice_map.get(self.char_class, 'd6')
        hp_gain = DiceRoller.roll(hit_die)

        # Add CON bonus
        con_bonus = self.get_hp_bonus_per_level()
        if con_bonus > 0:
            hp_gain += con_bonus
        elif con_bonus < 0:
            hp_gain = max(1, hp_gain + con_bonus)  # Minimum 1 HP per level

        self.hp_max += hp_gain
        self.hp_current += hp_gain
        messages.append(f"   HP: +{hp_gain} (now {self.hp_max})")

        # Improve THAC0
        thac0_progression = {
            'Fighter': -1,      # Every level
            'Cleric': -0.67,    # Every 1.5 levels (2 per 3 levels)
            'Magic-User': -0.33, # Every 3 levels
            'Thief': -0.5       # Every 2 levels
        }

        progression = thac0_progression.get(self.char_class, -0.5)

        # Calculate how many THAC0 points to improve
        # We track cumulative progression
        if not hasattr(self, '_thac0_progress'):
            self._thac0_progress = 0.0

        self._thac0_progress += abs(progression)

        if self._thac0_progress >= 1.0:
            thac0_improvement = int(self._thac0_progress)
            self.thac0 -= thac0_improvement
            self._thac0_progress -= thac0_improvement
            messages.append(f"   THAC0: improved to {self.thac0}")

        # Improve thief skills
        if self.char_class == 'Thief':
            skill_gains = {
                'pick_pockets': 5,
                'open_locks': 5,
                'find_traps': 5,
                'move_silently': 5,
                'hide_in_shadows': 5,
                'hear_noise': 5,
                'climb_walls': 1,
                'read_languages': 5
            }

            messages.append("   Thief Skills Improved:")
            for skill, gain in skill_gains.items():
                if skill in self.thief_skills:
                    self.thief_skills[skill] += gain
                    messages.append(f"      {skill.replace('_', ' ').title()}: +{gain}% (now {self.thief_skills[skill]}%)")

        # Update XP needed for next level
        if self.char_class in XP_TABLES:
            xp_table = XP_TABLES[self.char_class]
            if self.level < len(xp_table) - 1:
                self.xp_to_next_level = xp_table[self.level]
            else:
                self.xp_to_next_level = 999999999  # Max level reached

        return '\n'.join(messages)

    def can_use_thief_skill(self, skill_name: str) -> bool:
        """Check if character has a thief skill"""
        # Support both find_traps and find_remove_traps
        if skill_name == 'find_traps':
            skill_name = 'find_remove_traps'
        return skill_name in self.thief_skills

    def get_thief_skill_value(self, skill_name: str) -> int:
        """
        Get percentage value for thief skill
        Note: This returns base value only. For full calculation with
        racial/DEX/armor modifiers, use SkillResolver.calculate_thief_skill()
        """
        # Support both find_traps and find_remove_traps
        if skill_name == 'find_traps':
            skill_name = 'find_remove_traps'
        return self.thief_skills.get(skill_name, 0)
