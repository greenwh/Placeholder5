"""
Alignment System - AD&D 1e Nine-Point Alignment
Handles validation of class alignment restrictions
"""

from typing import List, Dict, Optional


def get_allowed_alignments_for_class(char_class: str, class_data: Dict) -> List[str]:
    """
    Get list of allowed alignments for a given class

    Args:
        char_class: Character class name
        class_data: Class data dictionary from classes.json

    Returns:
        List of allowed alignment strings
    """
    from ..entities.character import ALIGNMENTS

    # If no restriction, all alignments allowed
    if 'alignment_requirement' not in class_data and 'alignment_restriction' not in class_data:
        return ALIGNMENTS.copy()

    # Get restriction type
    restriction = class_data.get('alignment_restriction')
    requirement = class_data.get('alignment_requirement', '')

    # Handle specific restriction types
    if restriction == 'exact':
        # Only one specific alignment (Paladin: LG, Druid: TN)
        return [requirement]

    elif restriction == 'any_axis':
        # Any alignment on one axis (Ranger: any Good, Assassin: any Evil)
        if requirement == 'Good':
            return ["Lawful Good", "Neutral Good", "Chaotic Good"]
        elif requirement == 'Evil':
            return ["Lawful Evil", "Neutral Evil", "Chaotic Evil"]
        elif requirement == 'Lawful':
            return ["Lawful Good", "Lawful Neutral", "Lawful Evil"]
        elif requirement == 'Chaotic':
            return ["Chaotic Good", "Chaotic Neutral", "Chaotic Evil"]
        elif requirement == 'Neutral':
            # This would mean any neutral (LN, TN, CN, NG, NE)
            return ["Lawful Neutral", "True Neutral", "Chaotic Neutral", "Neutral Good", "Neutral Evil"]

    elif restriction == 'not_lawful_good_or_chaotic_good':
        # Thief: can be neutral or evil (excludes LG and CG)
        excluded = ["Lawful Good", "Chaotic Good"]
        return [a for a in ALIGNMENTS if a not in excluded]

    # Default: all alignments
    return ALIGNMENTS.copy()


def validate_class_alignment(char_class: str, alignment: str, class_data: Dict) -> bool:
    """
    Check if an alignment is valid for a given character class

    Args:
        char_class: Character class name (e.g., "Paladin")
        alignment: Alignment to validate (e.g., "Lawful Good")
        class_data: Class data dictionary from classes.json

    Returns:
        True if alignment is allowed, False otherwise

    Examples:
        >>> validate_class_alignment("Paladin", "Lawful Good", paladin_data)
        True
        >>> validate_class_alignment("Paladin", "Chaotic Evil", paladin_data)
        False
        >>> validate_class_alignment("Fighter", "Chaotic Evil", fighter_data)
        True
    """
    allowed = get_allowed_alignments_for_class(char_class, class_data)
    return alignment in allowed


def get_alignment_description(alignment: str) -> str:
    """
    Get a brief description of what an alignment means

    Args:
        alignment: Alignment name

    Returns:
        Brief description string
    """
    descriptions = {
        "Lawful Good": "Believes in order and law, values life and helping others",
        "Neutral Good": "Values life and welfare, balances law and freedom",
        "Chaotic Good": "Values freedom and individualism, seeks to spread good",
        "Lawful Neutral": "Order and regulation above all, neutral on good vs evil",
        "True Neutral": "Balance in all things, nature and status quo",
        "Chaotic Neutral": "Randomness and freedom above all, unconcerned with morality",
        "Lawful Evil": "Uses law and order to impose dominance and control",
        "Neutral Evil": "Pure evil unconcerned with law or chaos",
        "Chaotic Evil": "Freedom to spread chaos, woe, and destruction"
    }

    return descriptions.get(alignment, "Unknown alignment")


def get_alignment_abbrev(alignment: str) -> str:
    """
    Get abbreviated form of alignment

    Args:
        alignment: Full alignment name

    Returns:
        Abbreviated form (e.g., "LG", "TN", "CE")
    """
    from ..entities.character import ALIGNMENT_ABBREV
    return ALIGNMENT_ABBREV.get(alignment, alignment[:2].upper())


def is_alignment_compatible(alignment1: str, alignment2: str, strict: bool = False) -> bool:
    """
    Check if two alignments are compatible for party cohesion

    In AD&D, certain alignments conflict:
    - Good and Evil are opposed
    - Law and Chaos are opposed (less strictly)

    Args:
        alignment1: First alignment
        alignment2: Second alignment
        strict: If True, law/chaos conflicts also matter

    Returns:
        True if alignments can cooperate, False if strongly opposed
    """
    # Same alignment = always compatible
    if alignment1 == alignment2:
        return True

    # Exact opposites on both axes = incompatible
    opposites = [
        ("Lawful Good", "Chaotic Evil"),
        ("Chaotic Good", "Lawful Evil"),
        ("Neutral Good", "Neutral Evil"),
    ]

    for a, b in opposites:
        if (alignment1 == a and alignment2 == b) or (alignment1 == b and alignment2 == a):
            return False

    # Good and Evil are opposed
    if ('Good' in alignment1 and 'Evil' in alignment2) or ('Evil' in alignment1 and 'Good' in alignment2):
        return False

    # In strict mode, Lawful and Chaotic also oppose
    if strict:
        if ('Lawful' in alignment1 and 'Chaotic' in alignment2) or ('Chaotic' in alignment1 and 'Lawful' in alignment2):
            # Unless one is neutral on the good/evil axis
            if 'Neutral' not in alignment1 and 'Neutral' not in alignment2:
                return False

    return True
