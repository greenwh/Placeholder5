"""
Adventure Seed Generation System

Generates adventure hooks, backstories, and context for dungeons.
Provides the "why" and "what" to turn random dungeons into meaningful scenarios.
"""

import random
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class AdventureContext:
    """Complete adventure context"""
    title: str
    hook: str  # The initial rumor/hook presented to players
    theme: str  # mystery, treasure_hunt, rescue, revenge, etc.
    backstory: str  # Secret history
    primary_antagonist: str  # Main villain/boss
    antagonist_motivation: str  # Why they're here
    factions: List[Dict]  # Different groups in the dungeon
    recommended_level: int
    recommended_party_size: int
    dungeon_type: str  # mine, crypt, ruins, cave, sewer
    special_features: List[str]  # Unique elements
    resolution_paths: List[str]  # Different ways to complete

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "title": self.title,
            "hook": self.hook,
            "theme": self.theme,
            "backstory": self.backstory,
            "primary_antagonist": self.primary_antagonist,
            "antagonist_motivation": self.antagonist_motivation,
            "factions": self.factions,
            "recommended_level": self.recommended_level,
            "recommended_party_size": self.recommended_party_size,
            "dungeon_type": self.dungeon_type,
            "special_features": self.special_features,
            "resolution_paths": self.resolution_paths
        }


class AdventureSeedGenerator:
    """
    Generates adventure seeds and context

    Creates meaningful scenarios with hooks, backstory, and factions
    """

    def __init__(self):
        """Initialize with seed templates"""
        self._init_seed_templates()
        self._init_antagonist_motivations()
        self._init_faction_relationships()

    def _init_seed_templates(self):
        """Initialize adventure seed templates"""
        self.seed_templates = {
            "abandoned_tower": {
                "title_templates": ["The Dark Tower", "The Silent Spire", "The Forgotten Watchtower"],
                "hook": "An old watchtower on the border hills has been dark for years, but locals report strange lights in its windows at night.",
                "theme": "mystery",
                "backstory_templates": [
                    "The tower was built to watch for orc raids, but the guards abandoned it decades ago when something drove them out.",
                    "A reclusive wizard once lived here, conducting forbidden experiments. Now something has awakened.",
                    "This was an ancient shrine before being converted to a watchtower. The original power still lingers."
                ],
                "antagonist_options": ["bandit_leader", "evil_mage", "undead_knight", "corrupted_captain"],
                "dungeon_type": "ruins",
                "recommended_level": "1-2"
            },
            "lost_mine": {
                "title_templates": ["The Lost Mine of Karak", "Deepdelve Mine", "The Abandoned Shaft"],
                "hook": "A profitable mine was suddenly abandoned twenty years ago. The miners fled in terror, and no one has returned since.",
                "theme": "treasure_hunt",
                "backstory_templates": [
                    "The miners dug too deep and broke into ancient tunnels. Something terrible came out.",
                    "A rich vein of gems was cursed by an angry earth spirit.",
                    "The mine accidentally disturbed a goblin warren, and they've claimed it as their own."
                ],
                "antagonist_options": ["goblin_king", "earth_elemental", "corrupted_dwarf_ghost", "orc_warchief"],
                "dungeon_type": "mine",
                "recommended_level": "1-3"
            },
            "haunted_crypt": {
                "title_templates": ["The Crypt of Shadows", "Barrowmoor Cemetery", "The Silent Tombs"],
                "hook": "The old cemetery on the hill has become restless. Townsfolk report seeing lights and hearing chanting at night.",
                "theme": "investigation",
                "backstory_templates": [
                    "A dark cult has taken over the crypts, using them for necromantic rituals.",
                    "An ancient evil sleeps in the deepest tomb, and someone is trying to awaken it.",
                    "The caretaker has been replaced by a doppelganger working for a lich."
                ],
                "antagonist_options": ["necromancer", "lich", "death_cult_leader", "wight_lord"],
                "dungeon_type": "crypt",
                "recommended_level": "2-4"
            },
            "missing_caravan": {
                "title_templates": ["The Lost Caravan", "Road of Bones", "The Merchant's Fate"],
                "hook": "A wealthy merchant caravan is three weeks overdue. The merchant guild offers a reward for information or goods recovered.",
                "theme": "rescue",
                "backstory_templates": [
                    "Bandits ambushed the caravan and dragged the survivors to their hideout.",
                    "The caravan was attacked by monsters who wanted the cargo for their own purposes.",
                    "The guards turned on the merchants, murdered them, and are now hiding with the loot."
                ],
                "antagonist_options": ["bandit_chief", "ogre_tribe", "corrupt_mercenary", "gnoll_pack_leader"],
                "dungeon_type": "cave",
                "recommended_level": "1-2"
            },
            "cursed_village": {
                "title_templates": ["The Cursed Village", "Plague of Shadows", "The Withered Hamlet"],
                "hook": "A nearby village has been struck by a mysterious plague. The sick speak of dark dreams and whisper in unknown tongues.",
                "theme": "investigation",
                "backstory_templates": [
                    "An ancient artifact was unearthed in a farmer's field, releasing a curse.",
                    "A hag has taken residence in the woods and is poisoning the water supply.",
                    "The village elder made a dark pact years ago, and now payment is due."
                ],
                "antagonist_options": ["night_hag", "cursed_artifact", "corrupted_druid", "demon_cultist"],
                "dungeon_type": "ruins",
                "recommended_level": "2-3"
            },
            "stolen_relic": {
                "title_templates": ["The Stolen Relic", "Sacred Theft", "The Missing Icon"],
                "hook": "A sacred relic has been stolen from the temple. The high priest offers a generous reward for its return.",
                "theme": "recovery",
                "backstory_templates": [
                    "A thieves' guild stole it on commission for a dark cult.",
                    "The relic was taken by a possessed acolyte who fled to the old ruins.",
                    "Rival clerics stole it to discredit the temple."
                ],
                "antagonist_options": ["master_thief", "cultist_leader", "corrupted_priest", "demon_in_disguise"],
                "dungeon_type": "ruins",
                "recommended_level": "1-3"
            },
            "dragon_rumors": {
                "title_templates": ["Dragon's Shadow", "The Wyrm's Lair", "Scales and Flame"],
                "hook": "Rumors speak of a dragon that has taken up residence in the old fortress. Livestock has gone missing, and smoke rises from the ruins.",
                "theme": "monster_hunt",
                "backstory_templates": [
                    "A young dragon has claimed the ruins as its first lair.",
                    "It's not actually a dragon, but a powerful drake or wyvern.",
                    "A dragon cultist is impersonating a dragon to scare people away from their real operation."
                ],
                "antagonist_options": ["young_dragon", "wyvern", "dragonscale_sorcerer", "half_dragon_warrior"],
                "dungeon_type": "ruins",
                "recommended_level": "3-5"
            },
            "underground_river": {
                "title_templates": ["The Sunless River", "Caverns of Echo", "The Dark Waters"],
                "hook": "Strange creatures have been seen emerging from caves near the underground river. Fishermen have disappeared.",
                "theme": "exploration",
                "backstory_templates": [
                    "The river connects to a vast underground network controlled by troglodytes.",
                    "Something from the deep places has migrated upriver.",
                    "A tribe of intelligent creatures lives down there and resents surface intrusion."
                ],
                "antagonist_options": ["troglodyte_shaman", "aboleth_spawn", "kuo-toa_priest", "dark_dwarf_warband"],
                "dungeon_type": "cave",
                "recommended_level": "2-4"
            }
        }

    def _init_antagonist_motivations(self):
        """Initialize antagonist motivations"""
        self.motivations = {
            "power": [
                "seeks to complete a ritual that will grant them immense magical power",
                "wants to unlock an ancient artifact's full potential",
                "plans to summon and bind a powerful entity to their will"
            ],
            "revenge": [
                "was wronged by the local lord and seeks vengeance",
                "wants to destroy the town that exiled them",
                "blames the surface world for their misfortunes"
            ],
            "greed": [
                "has discovered a rich vein of treasure and wants it all",
                "is ransoming prisoners for gold",
                "plans to rob a merchant caravan using this as a base"
            ],
            "survival": [
                "just wants a safe place for their tribe to live",
                "is protecting their young and territory",
                "was driven here by something worse"
            ],
            "madness": [
                "has gone insane from isolation and forbidden knowledge",
                "believes they are fulfilling a dark prophecy",
                "serves an entity that drives them toward chaos"
            ],
            "duty": [
                "is following ancient orders from a long-dead master",
                "must guard this place as per an old oath",
                "protects a secret that must never be revealed"
            ]
        }

    def _init_faction_relationships(self):
        """Initialize faction relationship templates"""
        self.faction_templates = [
            {
                "type": "uneasy_alliance",
                "description": "Two groups with different goals are working together out of necessity",
                "example": "Goblins and orcs have allied despite mutual distrust"
            },
            {
                "type": "oppressor_oppressed",
                "description": "A stronger group dominates a weaker one",
                "example": "Ogres have enslaved kobolds to do their bidding"
            },
            {
                "type": "internal_conflict",
                "description": "The group is divided against itself",
                "example": "A power struggle between lieutenants threatens to split the tribe"
            },
            {
                "type": "parasitic",
                "description": "One group secretly feeds on or manipulates the other",
                "example": "A hidden vampire controls the bandits through thralls"
            },
            {
                "type": "ignorant_coexistence",
                "description": "Multiple groups don't know about each other",
                "example": "Bandits in the upper levels don't know about the undead below"
            }
        ]

    def generate_seed_menu(
        self,
        count: int = 3,
        party_level: int = 1
    ) -> List[Dict]:
        """
        Generate a menu of adventure seeds

        Args:
            count: Number of seeds to generate
            party_level: Party level for appropriate challenges

        Returns:
            List of seed dictionaries with hook, title, theme
        """
        # Filter templates by recommended level
        suitable_templates = []
        for seed_id, template in self.seed_templates.items():
            rec_level = template.get("recommended_level", "1-3")
            min_level, max_level = map(int, rec_level.split("-"))

            if min_level <= party_level <= max_level + 1:
                suitable_templates.append((seed_id, template))

        # If not enough suitable, use all
        if len(suitable_templates) < count:
            suitable_templates = list(self.seed_templates.items())

        # Select random seeds
        selected = random.sample(suitable_templates, min(count, len(suitable_templates)))

        menu = []
        for seed_id, template in selected:
            menu.append({
                "id": seed_id,
                "title": random.choice(template["title_templates"]),
                "hook": template["hook"],
                "theme": template["theme"],
                "dungeon_type": template["dungeon_type"]
            })

        return menu

    def generate_full_context(
        self,
        seed_id: str,
        party_level: int = 1,
        party_size: int = 4
    ) -> AdventureContext:
        """
        Generate complete adventure context from seed

        Args:
            seed_id: Seed template ID
            party_level: Party level
            party_size: Number of party members

        Returns:
            Complete AdventureContext
        """
        if seed_id not in self.seed_templates:
            seed_id = random.choice(list(self.seed_templates.keys()))

        template = self.seed_templates[seed_id]

        # Generate basic info
        title = random.choice(template["title_templates"])
        hook = template["hook"]
        theme = template["theme"]
        backstory = random.choice(template["backstory_templates"])
        dungeon_type = template["dungeon_type"]

        # Select antagonist
        antagonist = random.choice(template["antagonist_options"])
        motivation_category = random.choice(list(self.motivations.keys()))
        motivation = random.choice(self.motivations[motivation_category])

        # Generate factions
        factions = self._generate_factions(antagonist, template)

        # Generate special features
        special_features = self._generate_special_features(template, theme)

        # Generate resolution paths
        resolution_paths = self._generate_resolution_paths(theme, antagonist)

        return AdventureContext(
            title=title,
            hook=hook,
            theme=theme,
            backstory=backstory,
            primary_antagonist=antagonist,
            antagonist_motivation=motivation,
            factions=factions,
            recommended_level=party_level,
            recommended_party_size=party_size,
            dungeon_type=dungeon_type,
            special_features=special_features,
            resolution_paths=resolution_paths
        )

    def _generate_factions(self, primary_antagonist: str, template: Dict) -> List[Dict]:
        """Generate faction information"""
        # Primary faction (antagonist's group)
        factions = [
            {
                "name": f"{primary_antagonist.replace('_', ' ').title()}'s Forces",
                "role": "primary",
                "description": "The main antagonist and their direct followers"
            }
        ]

        # Add secondary faction
        relationship = random.choice(self.faction_templates)
        factions.append({
            "name": "Secondary Group",
            "role": "secondary",
            "relationship": relationship["type"],
            "description": relationship["description"]
        })

        # Occasionally add a third wild-card faction
        if random.random() > 0.5:
            factions.append({
                "name": "Wildcard Element",
                "role": "wildcard",
                "description": "An independent force pursuing their own agenda"
            })

        return factions

    def _generate_special_features(self, template: Dict, theme: str) -> List[str]:
        """Generate special features for the adventure"""
        features = []

        feature_pool = [
            "A hidden passage leads to a secret chamber",
            "An ancient magical ward still functions, protecting something",
            "Environmental hazards make exploration dangerous",
            "A neutral NPC can be found who offers information or aid",
            "Clues to a larger mystery are scattered throughout",
            "A time limit adds urgency to the mission",
            "The layout changes or shifts mysteriously",
            "Previous adventurers left behind useful items or warnings"
        ]

        # Select 2-3 features
        num_features = random.randint(2, 3)
        features = random.sample(feature_pool, num_features)

        return features

    def _generate_resolution_paths(self, theme: str, antagonist: str) -> List[str]:
        """Generate different ways the adventure can be resolved"""
        paths = [
            "Combat: Defeat the antagonist and their forces in battle",
        ]

        # Add theme-specific paths
        if theme in ["mystery", "investigation"]:
            paths.append("Investigation: Uncover the truth and expose the conspiracy")

        if theme == "rescue":
            paths.append("Stealth: Sneak past guards and free the prisoners")

        if theme == "recovery":
            paths.append("Theft: Steal back the item without confronting the main force")

        # Universal alternative paths
        paths.append("Negotiation: Parley with the antagonist and reach an accord")
        paths.append("Alliance: Turn one faction against another")

        return paths


# Convenience functions
def generate_adventure_menu(party_level: int = 1, count: int = 3) -> List[Dict]:
    """
    Generate menu of adventure hooks

    Args:
        party_level: Party level
        count: Number of options

    Returns:
        List of adventure hooks
    """
    generator = AdventureSeedGenerator()
    return generator.generate_seed_menu(count, party_level)


def generate_adventure(seed_id: str, party_level: int = 1, party_size: int = 4) -> Dict:
    """
    Generate complete adventure context

    Args:
        seed_id: Seed template ID
        party_level: Party level
        party_size: Party size

    Returns:
        Adventure context dictionary
    """
    generator = AdventureSeedGenerator()
    context = generator.generate_full_context(seed_id, party_level, party_size)
    return context.to_dict()


if __name__ == "__main__":
    # Test adventure seed generation
    print("="*70)
    print("ADVENTURE SEED GENERATION TEST")
    print("="*70)

    generator = AdventureSeedGenerator()

    # Test 1: Generate menu
    print("\n1. ADVENTURE MENU (Level 1 Party)")
    print("-" * 70)
    menu = generator.generate_seed_menu(count=3, party_level=1)

    for i, seed in enumerate(menu, 1):
        print(f"\nOption {i}: {seed['title']}")
        print(f"  Theme: {seed['theme']}")
        print(f"  Hook: {seed['hook']}")

    # Test 2: Generate full context
    print("\n2. FULL ADVENTURE CONTEXT")
    print("-" * 70)
    chosen_seed = menu[0]["id"]
    context = generator.generate_full_context(chosen_seed, party_level=1, party_size=4)

    print(f"\nTitle: {context.title}")
    print(f"Theme: {context.theme}")
    print(f"\nHook:")
    print(f"  {context.hook}")
    print(f"\nBackstory (Secret):")
    print(f"  {context.backstory}")
    print(f"\nPrimary Antagonist: {context.primary_antagonist}")
    print(f"Motivation: {context.antagonist_motivation}")
    print(f"\nFactions:")
    for faction in context.factions:
        print(f"  - {faction['name']}: {faction['description']}")
    print(f"\nSpecial Features:")
    for feature in context.special_features:
        print(f"  - {feature}")
    print(f"\nResolution Paths:")
    for path in context.resolution_paths:
        print(f"  - {path}")

    print("\n" + "="*70)
    print("Adventure seed system complete!")
    print("="*70)
