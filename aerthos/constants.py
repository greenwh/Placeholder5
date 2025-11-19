"""
Game Constants for AD&D 1e Mechanics

Central location for all magic numbers used throughout the codebase.
This ensures consistency and makes game balance tuning easier.
"""

# ============================================================================
# CORE MECHANICS
# ============================================================================

# Base armor class (unarmored)
BASE_AC = 10

# Maximum d20 roll
D20_MAX = 20

# Critical hit/miss values
CRITICAL_HIT = 20
CRITICAL_MISS = 1

# Initiative die
INITIATIVE_DIE = 6

# ============================================================================
# TIME & TURNS
# ============================================================================

# Minutes per dungeon turn
MINUTES_PER_TURN = 10

# Turns per hour
TURNS_PER_HOUR = 6

# Segments per round (for spell casting)
SEGMENTS_PER_ROUND = 10

# ============================================================================
# COMBAT
# ============================================================================

# Starting THAC0 by class (level 1)
THAC0_FIGHTER_BASE = 20
THAC0_CLERIC_BASE = 20
THAC0_THIEF_BASE = 20
THAC0_MAGIC_USER_BASE = 21

# THAC0 improvement rate (levels per improvement)
THAC0_FIGHTER_RATE = 1  # Improves every level
THAC0_CLERIC_RATE = 2   # Improves every 2 levels
THAC0_THIEF_RATE = 2    # Improves every 2 levels
THAC0_MAGIC_USER_RATE = 3  # Improves every 3 levels

# Size categories for damage
SIZE_SMALL = 'S'
SIZE_MEDIUM = 'M'
SIZE_LARGE = 'L'

# Formation combat targeting (Gold Box style)
FRONT_LINE_TARGET_CHANCE = 70  # % chance to target front-line
BACK_LINE_TARGET_CHANCE = 20   # % chance to target back-line (if reachable)
OPPORTUNISTIC_TARGET_CHANCE = 10  # % chance for opportunistic targeting

# Intelligence thresholds for targeting behavior
MONSTER_INT_LOW = 4   # Animal intelligence - always attack nearest
MONSTER_INT_HIGH = 12  # Tactical intelligence - can prioritize spellcasters

# ============================================================================
# ABILITY SCORES
# ============================================================================

# Ability score range
ABILITY_MIN = 3
ABILITY_MAX = 18

# Exceptional strength (fighters only)
EXCEPTIONAL_STRENGTH_MIN = 1
EXCEPTIONAL_STRENGTH_MAX = 100

# ============================================================================
# ENCUMBRANCE & MOVEMENT
# ============================================================================

# Base movement rate (inches per turn in dungeon)
BASE_MOVEMENT_RATE = 12

# Movement rate adjustments by armor
MOVEMENT_UNARMORED = 12
MOVEMENT_LEATHER = 9
MOVEMENT_CHAIN = 6
MOVEMENT_PLATE = 3

# Encumbrance thresholds (coins)
COINS_PER_POUND = 10
ENCUMBRANCE_LIGHT = 350   # coins
ENCUMBRANCE_MODERATE = 700  # coins
ENCUMBRANCE_HEAVY = 1050  # coins

# ============================================================================
# LIGHT SOURCES
# ============================================================================

# Torch duration (turns)
TORCH_DURATION_TURNS = 6

# Lantern duration (turns)
LANTERN_DURATION_TURNS = 24

# Light radii (feet)
TORCH_RADIUS = 30
LANTERN_RADIUS = 30

# ============================================================================
# MAGIC & SPELLS
# ============================================================================

# Spell component types
COMPONENT_STANDARD = "standard"
COMPONENT_RARE = "rare"

# Magic resistance percentile
MAGIC_RESISTANCE_MIN = 0
MAGIC_RESISTANCE_MAX = 100

# Spell level limits
MIN_SPELL_LEVEL = 1
MAX_SPELL_LEVEL_MAGIC_USER = 9
MAX_SPELL_LEVEL_CLERIC = 7

# ============================================================================
# SAVING THROWS
# ============================================================================

# Save categories (for reference)
SAVE_PARALYZATION = "paralyzation"
SAVE_POISON = "poison"
SAVE_DEATH = "death"
SAVE_ROD_STAFF_WAND = "rod_staff_wand"
SAVE_PETRIFICATION = "petrification"
SAVE_POLYMORPH = "polymorph"
SAVE_BREATH = "breath"
SAVE_SPELL = "spell"

# ============================================================================
# REST & RECOVERY
# ============================================================================

# HP recovered per day of rest
HP_RECOVERY_PER_DAY = 1

# Additional HP recovery with bed rest
HP_RECOVERY_BED_REST_BONUS = 1

# Spell restoration (requires 8 hours rest)
SPELL_RESTORATION_HOURS = 8

# ============================================================================
# TREASURE & ECONOMY
# ============================================================================

# Coin types (weight)
COIN_WEIGHT = 0.1  # pounds per coin

# Standard multipliers
SHOP_BUY_MULTIPLIER = 0.5   # Shops buy at 50% value
SHOP_SELL_MULTIPLIER = 1.0  # Shops sell at 100% value
MAGIC_SHOP_PREMIUM = 1.2    # Magic shops charge 20% premium

# ============================================================================
# MONSTER ABILITIES
# ============================================================================

# Special ability usage chance
MONSTER_ABILITY_USE_CHANCE = 0.3  # 30% chance to use special ability

# Regeneration rates
TROLL_REGENERATION_RATE = 3
VAMPIRE_REGENERATION_RATE = 3
STANDARD_REGENERATION_RATE = 1

# Level drain amounts
VAMPIRE_LEVEL_DRAIN = 2
WIGHT_LEVEL_DRAIN = 1
WRAITH_LEVEL_DRAIN = 1
SPECTRE_LEVEL_DRAIN = 2

# ============================================================================
# THIEF SKILLS
# ============================================================================

# Base percentages are in data files, but these are modifiers

# Armor penalties
THIEF_NO_ARMOR_PENALTY = 0
THIEF_LEATHER_PENALTY = -5
THIEF_STUDDED_LEATHER_PENALTY = -10
THIEF_HEAVIER_ARMOR_PENALTY = -20

# ============================================================================
# PARTY & HIRELINGS
# ============================================================================

# Party size limits
MIN_PARTY_SIZE = 1
MAX_PARTY_SIZE = 6

# Hireling limits (by CHA - from ability tables)
# Actual values are in ability score tables

# ============================================================================
# EXPERIENCE & LEVELING
# ============================================================================

# XP award percentages
XP_BONUS_HIGH_PRIME_REQUISITE = 1.10  # 10% bonus
XP_PENALTY_LOW_PRIME_REQUISITE = 0.90  # 10% penalty

# Maximum level (AD&D 1e varies by class)
MAX_LEVEL_FIGHTER = 20
MAX_LEVEL_CLERIC = 20
MAX_LEVEL_THIEF = 20
MAX_LEVEL_MAGIC_USER = 20

# ============================================================================
# DUNGEON GENERATION
# ============================================================================

# Default dungeon sizes
DUNGEON_SIZE_SMALL = 8
DUNGEON_SIZE_MEDIUM = 12
DUNGEON_SIZE_LARGE = 15

# Encounter frequencies
ENCOUNTER_CHANCE_LOW = 0.3
ENCOUNTER_CHANCE_MEDIUM = 0.5
ENCOUNTER_CHANCE_HIGH = 0.7

# ============================================================================
# GAME BALANCE
# ============================================================================

# Wandering monster check frequency (turns)
WANDERING_MONSTER_CHECK_FREQUENCY = 3

# Wandering monster chance
WANDERING_MONSTER_CHANCE = 0.15  # 15% per check

# Rest interruption chance
REST_INTERRUPTION_CHANCE = 0.15  # 15% chance of encounter during rest

# ============================================================================
# FILE PATHS (relative to project root)
# ============================================================================

DATA_DIR = "aerthos/data"
SAVE_DIR = "~/.aerthos/saves"
CHARACTER_DIR = "~/.aerthos/characters"
PARTY_DIR = "~/.aerthos/parties"
SCENARIO_DIR = "~/.aerthos/scenarios"
SESSION_DIR = "~/.aerthos/sessions"

# ============================================================================
# DISPLAY & UI
# ============================================================================

# Line lengths for text wrapping
TEXT_WRAP_WIDTH = 70
SEPARATOR_WIDTH = 70

# Status display
HP_BAR_WIDTH = 20

# ============================================================================
# DEBUGGING & DEVELOPMENT
# ============================================================================

# Enable debug output (should be False in production)
DEBUG_MODE = False

# Verbose logging
VERBOSE_COMBAT = False
VERBOSE_MAGIC = False
VERBOSE_PARSER = False
