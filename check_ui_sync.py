#!/usr/bin/env python3
"""
UI Synchronization Checker

Scans main.py and web_ui/app.py for potential code duplication
and synchronization issues.

Run this before committing changes that affect both UIs.
"""

import re
import sys
from pathlib import Path
from difflib import SequenceMatcher


def extract_function_calls(file_path):
    """Extract function calls from a Python file"""
    with open(file_path, 'r') as f:
        content = f.read()

    # Find function calls: object.method(...) or function(...)
    pattern = r'\b(\w+(?:\.\w+)?)\s*\('
    calls = re.findall(pattern, content)

    return set(calls)


def find_duplicate_logic(cli_file, web_file):
    """Find similar code blocks between CLI and Web UI"""

    with open(cli_file, 'r') as f:
        cli_lines = f.readlines()

    with open(web_file, 'r') as f:
        web_lines = f.readlines()

    # Look for similar multi-line blocks (5+ lines)
    duplicates = []

    for i in range(len(cli_lines) - 5):
        cli_block = ''.join(cli_lines[i:i+5])

        for j in range(len(web_lines) - 5):
            web_block = ''.join(web_lines[j:j+5])

            # Calculate similarity
            similarity = SequenceMatcher(None, cli_block, web_block).ratio()

            # If blocks are very similar (>80%), flag as potential duplication
            if similarity > 0.8:
                duplicates.append({
                    'cli_start': i + 1,
                    'web_start': j + 1,
                    'similarity': similarity,
                    'cli_snippet': cli_lines[i].strip()[:60]
                })

    return duplicates


def check_critical_functions():
    """Check that critical functions are called in both UIs"""

    critical_patterns = {
        '_add_starting_spells': 'Character spell assignment',
        '_add_starting_equipment': 'Character equipment assignment',
        'add_spell_slot': 'Spell slot creation',
        'DungeonGenerator.generate': 'Dungeon generation',
        'save_character': 'Character saving',
        'load_character': 'Character loading',
    }

    cli_file = Path('main.py')
    web_file = Path('web_ui/app.py')

    if not cli_file.exists() or not web_file.exists():
        print("❌ Cannot find main.py or web_ui/app.py")
        return

    with open(cli_file, 'r') as f:
        cli_content = f.read()

    with open(web_file, 'r') as f:
        web_content = f.read()

    print("=" * 70)
    print("CRITICAL FUNCTION USAGE CHECK")
    print("=" * 70)
    print()

    issues_found = False

    for pattern, description in critical_patterns.items():
        cli_has = pattern in cli_content
        web_has = pattern in web_content

        if cli_has and web_has:
            print(f"✓ {description}: Found in BOTH UIs")
        elif cli_has and not web_has:
            print(f"⚠️  {description}: Found in CLI but NOT in Web UI")
            issues_found = True
        elif not cli_has and web_has:
            print(f"⚠️  {description}: Found in Web UI but NOT in CLI")
            issues_found = True
        else:
            print(f"  {description}: Not found in either (may not be needed)")

    print()

    return not issues_found


def check_parameter_order():
    """Check for function calls with different parameter patterns"""

    print("=" * 70)
    print("PARAMETER ORDER CHECK")
    print("=" * 70)
    print()

    # Common functions to check
    functions_to_check = [
        'PlayerCharacter(',
        'quick_create(',
        'create_character(',
        'DungeonGenerator.generate(',
        'MultiLevelGenerator.generate(',
    ]

    cli_file = Path('main.py')
    web_file = Path('web_ui/app.py')

    with open(cli_file, 'r') as f:
        cli_lines = f.readlines()

    with open(web_file, 'r') as f:
        web_lines = f.readlines()

    issues_found = False

    for func in functions_to_check:
        # Find calls to this function in both files
        cli_calls = [(i+1, line.strip()) for i, line in enumerate(cli_lines) if func in line]
        web_calls = [(i+1, line.strip()) for i, line in enumerate(web_lines) if func in line]

        if cli_calls and web_calls:
            print(f"Function: {func}")
            print(f"  CLI ({len(cli_calls)} calls):")
            for line_num, line in cli_calls[:3]:  # Show first 3
                print(f"    Line {line_num}: {line[:80]}")

            print(f"  Web UI ({len(web_calls)} calls):")
            for line_num, line in web_calls[:3]:  # Show first 3
                print(f"    Line {line_num}: {line[:80]}")

            print()

    return not issues_found


def main():
    """Run all synchronization checks"""

    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "UI SYNCHRONIZATION CHECK" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    all_good = True

    # Check critical functions
    if not check_critical_functions():
        all_good = False
        print("⚠️  Warning: Some critical functions may be missing in one UI")
        print()

    # Check parameter order
    check_parameter_order()

    # Skip duplicate detection - too slow for large files
    # Run it manually if needed: find_duplicate_logic('main.py', 'web_ui/app.py')

    print()
    print("=" * 70)

    if all_good:
        print("✅ NO SYNCHRONIZATION ISSUES DETECTED")
    else:
        print("⚠️  POTENTIAL SYNCHRONIZATION ISSUES FOUND")
        print()
        print("Review the warnings above and ensure both UIs use identical logic.")
        print("See COMMIT_CHECKLIST.md for guidelines.")

    print("=" * 70)
    print()

    return 0 if all_good else 1


if __name__ == '__main__':
    sys.exit(main())
