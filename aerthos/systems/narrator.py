"""
DM Narrative Layer

Provides atmospheric, engaging narration for all game events.
Transforms mechanical descriptions into DM-style storytelling.
"""

import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class NarrativeContext:
    """Context for narrative generation"""
    location_type: str = "dungeon"  # dungeon, wilderness, village, etc.
    atmosphere: List[str] = None  # dark, damp, ancient, dangerous, etc.
    time_of_day: str = "day"
    light_level: str = "torch"  # torch, dim, dark, bright
    recent_events: List[str] = None  # combat, trap, treasure, etc.
    party_condition: str = "healthy"  # healthy, wounded, exhausted

    def __post_init__(self):
        if self.atmosphere is None:
            self.atmosphere = []
        if self.recent_events is None:
            self.recent_events = []


class DMNarrator:
    """
    DM-style narrative generator

    Provides atmospheric descriptions for rooms, encounters,
    combat, and other game events using templates and context.
    """

    def __init__(self):
        """Initialize narrator with template libraries"""
        self._init_room_templates()
        self._init_combat_templates()
        self._init_sensory_details()
        self._init_atmospheric_modifiers()
        self._init_encounter_intros()

    def _init_room_templates(self):
        """Initialize room description templates"""
        self.room_entrance_templates = [
            "You {verb} into {article} {room_type}. {primary_feature} {secondary_feature}",
            "{article_cap} {room_type} {opens} before you. {atmosphere} {sensory}",
            "Pushing through the {door_type}, you find yourself in {article} {room_type}. {primary_feature}",
            "The passage {leads} into {article} {room_type}. {atmosphere} {primary_feature}",
        ]

        self.room_verbs = ["step cautiously", "enter", "emerge", "venture", "move carefully"]
        self.room_opens_verbs = ["opens", "extends", "stretches", "looms", "yawns"]
        self.room_leads_verbs = ["opens", "leads", "expands", "widens", "continues"]

    def _init_combat_templates(self):
        """Initialize combat narration templates"""
        self.attack_hit_verbs = {
            "sword": ["slashes", "cleaves", "cuts", "strikes", "hacks"],
            "axe": ["chops", "hews", "hacks", "splits", "smashes"],
            "mace": ["smashes", "crushes", "pounds", "batters", "strikes"],
            "dagger": ["stabs", "pierces", "jabs", "strikes"],
            "claw": ["rakes", "tears", "slashes", "rends"],
            "bite": ["bites", "chomps", "tears into", "sinks teeth into"],
            "default": ["hits", "strikes", "attacks"],
        }

        self.attack_miss_phrases = [
            "{attacker} swings wide, missing {defender}",
            "{attacker}'s attack is deflected by {defender}'s armor",
            "{defender} dodges aside as {attacker} attacks",
            "{attacker} fails to connect",
            "{attacker}'s strike goes wide",
            "{defender} parries {attacker}'s blow",
        ]

        self.critical_hit_phrases = [
            "{attacker} lands a devastating blow",
            "{attacker} finds a weak spot",
            "{attacker} strikes with deadly precision",
            "A perfect strike from {attacker}",
            "{attacker} delivers a crushing blow",
        ]

        self.critical_miss_phrases = [
            "{attacker} stumbles badly",
            "{attacker} loses their footing",
            "{attacker} fumbles their attack spectacularly",
            "{attacker}'s weapon nearly flies from their grasp",
        ]

    def _init_sensory_details(self):
        """Initialize sensory detail libraries"""
        self.smells = {
            "dungeon": ["musty air", "decay", "dampness", "ancient dust", "mold"],
            "mine": ["earth and stone", "mineral deposits", "stale air", "rust"],
            "crypt": ["death and decay", "incense and rot", "dry bones", "ancient perfumes"],
            "cave": ["damp stone", "bat guano", "mineral water", "earth"],
            "sewer": ["waste and filth", "stagnant water", "rot", "sewage"],
        }

        self.sounds = {
            "empty": ["echoes of dripping water", "your own breathing", "distant groans", "an ominous silence"],
            "inhabited": ["faint scratching", "distant voices", "movement ahead", "something stirring"],
            "combat": ["clanging metal", "shouts and cries", "the thud of impacts"],
            "peaceful": ["gentle echoes", "the sound of running water", "a light breeze"],
        }

        self.temperatures = [
            "uncomfortably cold",
            "pleasantly cool",
            "dank and clammy",
            "unnaturally warm",
            "frigid",
            "oppressively hot",
        ]

    def _init_atmospheric_modifiers(self):
        """Initialize atmospheric description modifiers"""
        self.atmosphere_templates = {
            "dark": [
                "darkness presses in around your torchlight",
                "shadows dance at the edge of your vision",
                "the darkness here seems almost alive",
                "your light barely pierces the gloom",
            ],
            "damp": [
                "moisture drips from the walls",
                "the air is thick with humidity",
                "water seeps from cracks in the stone",
                "everything is slick with dampness",
            ],
            "ancient": [
                "centuries of dust coat every surface",
                "time has not been kind to this place",
                "the weight of ages is palpable here",
                "ancient stonework crumbles at the edges",
            ],
            "dangerous": [
                "something feels wrong here",
                "your instincts scream danger",
                "the hair on your neck stands on end",
                "an oppressive sense of menace fills the air",
            ],
            "abandoned": [
                "this place has been empty for years",
                "signs of long-abandoned habitation remain",
                "whoever lived here left in haste",
                "decay and neglect are everywhere",
            ],
            "magical": [
                "the air crackles with arcane energy",
                "strange symbols glow faintly on the walls",
                "you sense powerful magic at work here",
                "reality seems thin in this place",
            ],
        }

    def _init_encounter_intros(self):
        """Initialize encounter introduction templates"""
        self.encounter_surprise_party = [
            "You walk right into {count} {monster}! They have the drop on you!",
            "Before you can react, {count} {monster} are upon you!",
            "You're caught off-guard as {count} {monster} attack!",
        ]

        self.encounter_surprise_monsters = [
            "You spot {count} {monster} ahead, unaware of your presence.",
            "Ahead, {count} {monster} haven't noticed you yet.",
            "You see {count} {monster} before they see you.",
        ]

        self.encounter_mutual = [
            "As you enter, {count} {monster} turn to face you, weapons drawn!",
            "{count} {monster} spot you at the same moment you see them!",
            "You and {count} {monster} notice each other simultaneously!",
        ]

        self.encounter_lair_descriptions = [
            "This appears to be their lair - {signs}.",
            "Signs of habitation are everywhere - {signs}.",
            "They've made this place their home - you see {signs}.",
        ]

        self.lair_signs = [
            "bones and refuse litter the floor",
            "crude bedding and supplies are piled in corners",
            "the stench of their presence is overwhelming",
            "primitive drawings cover the walls",
            "a small fire pit smolders in the center",
        ]

    def describe_room_entrance(
        self,
        room_type: str,
        size: str,
        primary_features: List[str],
        context: NarrativeContext
    ) -> str:
        """
        Generate atmospheric room entrance description

        Args:
            room_type: Type of room (chamber, passage, hall, etc.)
            size: Size description (small, large, vast, etc.)
            primary_features: List of notable features
            context: Narrative context

        Returns:
            Formatted description string
        """
        template = random.choice(self.room_entrance_templates)

        # Determine article
        article = "an" if room_type[0].lower() in "aeiou" else "a"
        article_cap = article.capitalize()

        # Pick verb
        verb = random.choice(self.room_verbs)
        opens = random.choice(self.room_opens_verbs)
        leads = random.choice(self.room_leads_verbs)

        # Add size if significant
        if size in ["large", "huge", "vast"]:
            room_type = f"{size} {room_type}"

        # Primary feature
        if primary_features:
            primary_feature = random.choice(primary_features)
        else:
            primary_feature = "The room appears empty at first glance."

        # Secondary feature (sensory)
        sensory = self._get_sensory_detail(context)

        # Atmospheric detail
        atmosphere = self._get_atmospheric_detail(context)

        # Door type
        door_type = random.choice(["door", "doorway", "entrance", "portal"])

        # Format description
        description = template.format(
            verb=verb,
            article=article,
            article_cap=article_cap,
            room_type=room_type,
            primary_feature=primary_feature,
            secondary_feature="",
            opens=opens,
            leads=leads,
            atmosphere=atmosphere,
            sensory=sensory,
            door_type=door_type
        )

        return description

    def describe_combat_round(
        self,
        attacker_name: str,
        defender_name: str,
        weapon_type: str,
        hit: bool,
        damage: int,
        is_critical: bool = False,
        is_fumble: bool = False
    ) -> str:
        """
        Generate narrative combat description

        Args:
            attacker_name: Name of attacker
            defender_name: Name of defender
            weapon_type: Type of weapon (sword, claw, etc.)
            hit: Whether attack hit
            damage: Damage dealt (if hit)
            is_critical: If True, this was a critical hit
            is_fumble: If True, this was a critical miss

        Returns:
            Combat narration string
        """
        if is_fumble:
            template = random.choice(self.critical_miss_phrases)
            return template.format(attacker=attacker_name) + "!"

        if not hit:
            template = random.choice(self.attack_miss_phrases)
            return template.format(attacker=attacker_name, defender=defender_name) + "."

        # Hit!
        verbs = self.attack_hit_verbs.get(weapon_type.lower(), self.attack_hit_verbs["default"])
        verb = random.choice(verbs)

        if is_critical:
            intro = random.choice(self.critical_hit_phrases)
            return f"{intro.format(attacker=attacker_name)} - {attacker_name} {verb} {defender_name} for {damage} damage!"

        return f"{attacker_name} {verb} {defender_name} for {damage} damage!"

    def describe_encounter_start(
        self,
        monster_name: str,
        count: int,
        surprise_party: bool = False,
        surprise_monsters: bool = False,
        is_lair: bool = False
    ) -> str:
        """
        Generate encounter introduction

        Args:
            monster_name: Name of monster type
            count: Number of monsters
            surprise_party: True if party is surprised
            surprise_monsters: True if monsters are surprised
            is_lair: True if this is the monster's lair

        Returns:
            Encounter introduction narrative
        """
        # Pluralize monster name if needed
        if count > 1:
            # Simple pluralization
            if monster_name.endswith('s'):
                monster_plural = monster_name + "es"
            else:
                monster_plural = monster_name + "s"
        else:
            monster_plural = monster_name
            count_str = "a" if monster_name[0].lower() not in "aeiou" else "an"
            monster_plural = f"{count_str} {monster_plural}"
            count = ""  # Don't show "1"

        # Format count
        if isinstance(count, int) and count > 0:
            count_str = str(count)
        else:
            count_str = count  # Already formatted

        # Select template based on surprise
        if surprise_party:
            template = random.choice(self.encounter_surprise_party)
        elif surprise_monsters:
            template = random.choice(self.encounter_surprise_monsters)
        else:
            template = random.choice(self.encounter_mutual)

        description = template.format(count=count_str, monster=monster_plural)

        # Add lair description if applicable
        if is_lair:
            lair_template = random.choice(self.encounter_lair_descriptions)
            signs = random.choice(self.lair_signs)
            description += " " + lair_template.format(signs=signs)

        return description

    def describe_treasure_found(
        self,
        coins: Dict[str, int],
        gems: List[Dict],
        jewelry: List[Dict],
        magic_items: List[str]
    ) -> str:
        """
        Generate treasure discovery narrative

        Args:
            coins: Dict of coin types and amounts
            gems: List of gem dicts
            jewelry: List of jewelry dicts
            magic_items: List of magic item names

        Returns:
            Treasure description
        """
        descriptions = []

        # Coins
        coin_phrases = []
        if coins.get("platinum", 0) > 0:
            coin_phrases.append(f"{coins['platinum']} platinum pieces")
        if coins.get("gold", 0) > 0:
            coin_phrases.append(f"{coins['gold']} gold pieces")
        if coins.get("electrum", 0) > 0:
            coin_phrases.append(f"{coins['electrum']} electrum pieces")
        if coins.get("silver", 0) > 0:
            coin_phrases.append(f"{coins['silver']} silver pieces")
        if coins.get("copper", 0) > 0:
            coin_phrases.append(f"{coins['copper']} copper pieces")

        if coin_phrases:
            if len(coin_phrases) == 1:
                descriptions.append(f"You find {coin_phrases[0]}.")
            else:
                descriptions.append(f"You find {', '.join(coin_phrases[:-1])}, and {coin_phrases[-1]}.")

        # Gems
        if gems:
            total_value = sum(g["value"] for g in gems)
            if len(gems) == 1:
                descriptions.append(f"Among the treasure is {gems[0]['description']}.")
            else:
                descriptions.append(f"You discover {len(gems)} gems worth a total of {total_value}gp.")

        # Jewelry
        if jewelry:
            total_value = sum(j["value"] for j in jewelry)
            if len(jewelry) == 1:
                descriptions.append(f"You find {jewelry[0]['description']}.")
            else:
                descriptions.append(f"There are {len(jewelry)} pieces of jewelry worth {total_value}gp in total.")

        # Magic items
        if magic_items:
            descriptions.append(f"Something magical catches your eye - {', '.join(magic_items)}!")

        if not descriptions:
            return "You search thoroughly but find nothing of value."

        return " ".join(descriptions)

    def _get_sensory_detail(self, context: NarrativeContext) -> str:
        """Get appropriate sensory detail for context"""
        details = []

        # Smell
        if context.location_type in self.smells:
            smell_options = self.smells[context.location_type]
            smell = random.choice(smell_options)
            details.append(f"You catch the scent of {smell}.")

        # Sound
        if "combat" in context.recent_events:
            sound_type = "combat"
        elif len(context.recent_events) > 0:
            sound_type = "inhabited"
        else:
            sound_type = random.choice(["empty", "empty", "inhabited"])  # Bias toward empty

        sound = random.choice(self.sounds[sound_type])
        details.append(f"You hear {sound}.")

        return " ".join(details) if details else ""

    def _get_atmospheric_detail(self, context: NarrativeContext) -> str:
        """Get atmospheric description based on context"""
        if not context.atmosphere:
            return ""

        # Pick one atmosphere element
        atmosphere_type = random.choice(context.atmosphere)

        if atmosphere_type in self.atmosphere_templates:
            templates = self.atmosphere_templates[atmosphere_type]
            return random.choice(templates).capitalize() + "."

        return ""

    def describe_death(self, character_name: str, killer_name: Optional[str] = None) -> str:
        """Generate death narrative"""
        if killer_name:
            return f"{character_name} falls to {killer_name}'s final blow. Their adventure ends here."
        else:
            return f"{character_name} has fallen. Their adventure ends here."

    def describe_monster_death(self, monster_name: str) -> str:
        """Generate monster death narrative"""
        templates = [
            "The {monster} falls dead!",
            "{monster} collapses with a final shriek!",
            "The {monster} crumples to the ground, defeated!",
            "{monster} breathes its last!",
        ]
        template = random.choice(templates)
        return template.format(monster=monster_name)

    def describe_level_up(self, character_name: str, new_level: int) -> str:
        """Generate level advancement narrative"""
        return (
            f"{character_name} has gained enough experience to advance to level {new_level}! "
            f"Through trials and tribulations, they have grown stronger and more capable."
        )

    def get_foreshadowing(self, upcoming_encounter_type: str) -> Optional[str]:
        """Generate subtle foreshadowing hints"""
        foreshadowing = {
            "combat": [
                "You notice fresh claw marks on the walls.",
                "The remains of a previous victim lie in the corner.",
                "You hear movement somewhere ahead.",
                "Crude weapons and armor litter the floor - recent activity.",
            ],
            "trap": [
                "The floor ahead looks suspiciously clean.",
                "You notice faint seams in the stonework.",
                "Something about this passage doesn't seem right.",
                "Your instincts warn you to step carefully.",
            ],
            "treasure": [
                "You catch a metallic glint in the distance.",
                "Something valuable might be hidden here.",
                "This looks like a good place for a cache.",
            ],
            "boss": [
                "The air grows thick with menace.",
                "An overwhelming sense of power radiates from ahead.",
                "This must be the lair of something powerful.",
                "You steel yourself for what lies ahead.",
            ],
        }

        if upcoming_encounter_type in foreshadowing:
            return random.choice(foreshadowing[upcoming_encounter_type])

        return None


# Singleton instance
_narrator_instance = None


def get_narrator() -> DMNarrator:
    """Get or create singleton narrator instance"""
    global _narrator_instance
    if _narrator_instance is None:
        _narrator_instance = DMNarrator()
    return _narrator_instance
