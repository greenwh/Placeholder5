"""
PlayerCharacter class - extends Character with inventory, spells, and XP
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from .character import Character


@dataclass
class Item:
    """Base item class"""
    name: str
    item_type: str
    weight: float
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

    def __post_init__(self):
        self.item_type = 'weapon'


@dataclass
class Armor(Item):
    """Armor with AC bonus"""
    ac_bonus: int = 0  # How much it improves AC

    def __post_init__(self):
        self.item_type = 'armor'


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
        """Remove and return item by name"""
        for item in self.items:
            if item.name.lower() == item_name.lower():
                self.items.remove(item)
                return item
        return None

    def has_item(self, item_name: str) -> bool:
        """Check if item exists in inventory"""
        return any(item.name.lower() == item_name.lower() for item in self.items)

    def get_item(self, item_name: str) -> Optional[Item]:
        """Get item by name without removing"""
        for item in self.items:
            if item.name.lower() == item_name.lower():
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
        self.shield: Optional[Armor] = None
        self.light_source: Optional[LightSource] = None

    def get_total_ac(self, base_ac: int = 10) -> int:
        """Calculate total AC from equipment"""
        ac = base_ac
        if self.armor:
            ac -= self.armor.ac_bonus
        if self.shield:
            ac -= self.shield.ac_bonus
        return ac


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
        """Check if a spell is memorized and available"""
        for slot in self.spells_memorized:
            if (slot.spell and
                slot.spell.name.lower() == spell_name.lower() and
                not slot.is_used):
                return True
        return False

    def use_spell_slot(self, spell_name: str) -> Optional[Spell]:
        """Use a spell slot, returns the spell if successful"""
        for slot in self.spells_memorized:
            if (slot.spell and
                slot.spell.name.lower() == spell_name.lower() and
                not slot.is_used):
                slot.is_used = True
                return slot.spell
        return None

    def restore_spells(self):
        """Restore all spell slots (after rest)"""
        for slot in self.spells_memorized:
            slot.is_used = False

    def gain_xp(self, amount: int):
        """Gain experience points"""
        self.xp += amount
        # Level up logic would go here

    def can_use_thief_skill(self, skill_name: str) -> bool:
        """Check if character has a thief skill"""
        return skill_name in self.thief_skills

    def get_thief_skill_value(self, skill_name: str) -> int:
        """Get percentage value for thief skill"""
        return self.thief_skills.get(skill_name, 0)
