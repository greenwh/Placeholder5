"""
Guild system for class-specific services and quests
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class GuildService:
    """A service offered by a guild"""
    name: str
    price: int
    level_req: int
    description: str
    benefit: str = ""  # Optional benefit identifier


@dataclass
class GuildQuest:
    """A quest offered by a guild"""
    name: str
    reward: int
    level_req: int
    description: str


class Guild:
    """Represents a guild that offers class-specific services"""

    def __init__(self, guild_id: str, data: Dict):
        self.guild_id = guild_id
        self.name = data['name']
        self.guild_type = data['type']
        self.description = data['description']
        self.allowed_classes = data.get('allowed_classes', [])
        self.membership_fee = data.get('membership_fee', 0)
        self.services = [GuildService(**svc) for svc in data.get('services', [])]
        self.quests = [GuildQuest(**quest) for quest in data.get('quests', [])]
        self.members = set()  # Track who has paid membership

    def can_join(self, character) -> bool:
        """Check if a character can join this guild"""
        return character.char_class in self.allowed_classes

    def is_member(self, character_id: str) -> bool:
        """Check if a character is a member"""
        return character_id in self.members

    def join(self, character_id: str) -> bool:
        """Join the guild (requires membership fee)"""
        self.members.add(character_id)
        return True

    def get_service(self, service_name: str) -> Optional[GuildService]:
        """Get a service by name"""
        for service in self.services:
            if service.name == service_name:
                return service
        return None

    def can_use_service(self, service_name: str, character_level: int) -> bool:
        """Check if character can use a service"""
        service = self.get_service(service_name)
        if not service:
            return False
        return character_level >= service.level_req

    def get_available_quests(self, character_level: int) -> List[GuildQuest]:
        """Get quests available for character's level"""
        return [
            quest for quest in self.quests
            if character_level >= quest.level_req
        ]

    def list_services(self) -> List[Dict]:
        """List all services offered"""
        return [
            {
                'name': svc.name,
                'price': svc.price,
                'level_req': svc.level_req,
                'description': svc.description,
                'benefit': svc.benefit
            }
            for svc in self.services
        ]

    def list_quests(self) -> List[Dict]:
        """List all quests offered"""
        return [
            {
                'name': quest.name,
                'reward': quest.reward,
                'level_req': quest.level_req,
                'description': quest.description
            }
            for quest in self.quests
        ]


class GuildManager:
    """Manages all guilds in the game"""

    def __init__(self, guilds_data_path: str = "aerthos/data/guilds.json"):
        with open(guilds_data_path, 'r') as f:
            data = json.load(f)

        self.guilds = {
            guild_id: Guild(guild_id, guild_data)
            for guild_id, guild_data in data.items()
        }

    def get_guild(self, guild_id: str) -> Optional[Guild]:
        """Get a guild by ID"""
        return self.guilds.get(guild_id)

    def get_guilds_for_class(self, char_class: str) -> List[Guild]:
        """Get all guilds that accept a given class"""
        return [
            guild for guild in self.guilds.values()
            if char_class in guild.allowed_classes
        ]

    def list_all_guilds(self) -> List[Dict]:
        """List all available guilds"""
        return [
            {
                'id': guild_id,
                'name': guild.name,
                'type': guild.guild_type,
                'description': guild.description,
                'allowed_classes': guild.allowed_classes,
                'membership_fee': guild.membership_fee
            }
            for guild_id, guild in self.guilds.items()
        ]
