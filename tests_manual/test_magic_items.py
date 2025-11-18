"""
Test magic item generation in treasure system
"""

import sys
from pathlib import Path

# Add aerthos to path
sys.path.insert(0, str(Path(__file__).parent))

from aerthos.systems.treasure import TreasureGenerator

def test_magic_items():
    print("="*70)
    print("MAGIC ITEM GENERATION TEST")
    print("="*70)

    generator = TreasureGenerator()

    # Test 1: Treasure Type A (magic_any_3: 30% chance)
    print("\n1. Testing Treasure Type A (30% chance of 3 magic items)")
    print("-" * 70)
    for i in range(5):
        hoard = generator.generate_lair_treasure("A")
        print(f"\nAttempt {i+1}:")
        print(f"  Magic items: {len(hoard.magic_items)}")
        if hoard.magic_items:
            for item in hoard.magic_items:
                print(f"    - {item}")

    # Test 2: Treasure Type G (magic_any_4_plus_1_scroll: 35% chance)
    print("\n2. Testing Treasure Type G (35% chance of 4 magic + 1 scroll)")
    print("-" * 70)
    for i in range(5):
        hoard = generator.generate_lair_treasure("G")
        print(f"\nAttempt {i+1}:")
        print(f"  Magic items: {len(hoard.magic_items)}")
        if hoard.magic_items:
            for item in hoard.magic_items:
                print(f"    - {item}")

    # Test 3: Treasure Type F (complex: any 3 no swords + potion + scroll: 30%)
    print("\n3. Testing Treasure Type F (complex magic items)")
    print("-" * 70)
    for i in range(5):
        hoard = generator.generate_lair_treasure("F")
        print(f"\nAttempt {i+1}:")
        print(f"  Magic items: {len(hoard.magic_items)}")
        if hoard.magic_items:
            for item in hoard.magic_items:
                print(f"    - {item}")

    # Test 4: Direct magic item generation
    print("\n4. Testing direct magic item generation by category")
    print("-" * 70)

    categories = ["potions", "scrolls", "weapons", "armor", "rings", "misc_magic"]
    for category in categories:
        item = generator._generate_magic_item(category)
        print(f"\n{category.upper()}:")
        print(f"  {item['name']}")
        print(f"  XP: {item['xp_value']}, GP: {item['gp_value']}")

    # Test 5: Generate many hoards to verify percentages work
    print("\n5. Statistical test (100 Type A hoards, expect ~30 with magic)")
    print("-" * 70)
    magic_count = 0
    total_items = 0
    for _ in range(100):
        hoard = generator.generate_lair_treasure("A")
        if hoard.magic_items:
            magic_count += 1
            total_items += len(hoard.magic_items)

    print(f"  Hoards with magic items: {magic_count}/100 ({magic_count}%)")
    print(f"  Expected: ~30%")
    print(f"  Average items when present: {total_items/magic_count if magic_count > 0 else 0:.1f}")
    print(f"  Expected: ~3 items")

    print("\n" + "="*70)
    print("Magic item generation test complete!")
    print("="*70)

if __name__ == "__main__":
    test_magic_items()
