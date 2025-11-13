#!/usr/bin/env python3
"""
Complete test fix script - fixes ALL remaining issues
"""

import re
from pathlib import Path

def fix_dungeon_construction():
    """Fix Dungeon() construction to use proper constructor"""

    # Pattern to find and replace
    old_pattern = r'''dungeon_data = \{[^}]+\}[\s\n]+dungeon = Dungeon\(\)[\s\n]+dungeon\.load_from_dict\(dungeon_data\)'''

    # Read and fix each test file
    for test_file in Path('tests').glob('test_*.py'):
        content = test_file.read_text()

        # Replace the problematic pattern with proper construction
        # This is complex, so we'll do it line by line
        lines = content.split('\n')
        new_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check if this is a Dungeon() call
            if 'dungeon = Dungeon()' in line and i > 0:
                # Find the dungeon_data dict above
                # Look backwards for dungeon_data = {
                data_start = None
                for j in range(i-1, max(0, i-50), -1):
                    if 'dungeon_data = {' in lines[j]:
                        data_start = j
                        break

                if data_start is not None:
                    # Skip the old Dungeon() and load_from_dict lines
                    # Replace with proper construction
                    new_lines.append('        # Create rooms dict from room objects')
                    new_lines.append('        rooms_dict = {}')
                    new_lines.append('        for room_id in dungeon_data["rooms"]:')
                    new_lines.append('            room_info = dungeon_data["rooms"][room_id]')
                    new_lines.append('            if isinstance(room_info, dict) and "id" in room_info:')
                    new_lines.append('                rooms_dict[room_id] = Room(')
                    new_lines.append('                    id=room_info["id"],')
                    new_lines.append('                    title=room_info["title"],')
                    new_lines.append('                    description=room_info["description"],')
                    new_lines.append('                    light_level=room_info.get("light_level", "dark"),')
                    new_lines.append('                    exits=room_info.get("exits", {}),')
                    new_lines.append('                    items=room_info.get("items", []),')
                    new_lines.append('                    is_safe_for_rest=room_info.get("is_safe_for_rest", False)')
                    new_lines.append('                )')
                    new_lines.append('            else:')
                    new_lines.append('                # Already a Room object (from test setup)')
                    new_lines.append('                rooms_dict[room_id] = room_info')
                    new_lines.append('')
                    new_lines.append('        dungeon = Dungeon(')
                    new_lines.append('            name=dungeon_data["name"],')
                    new_lines.append('            start_room_id=dungeon_data["start_room"],')
                    new_lines.append('            rooms=rooms_dict')
                    new_lines.append('        )')

                    # Skip the load_from_dict line if it exists
                    i += 1
                    if i < len(lines) and 'load_from_dict' in lines[i]:
                        i += 1
                    continue

            new_lines.append(line)
            i += 1

        # Write back
        test_file.write_text('\n'.join(new_lines))
        print(f"✓ Fixed Dungeon construction in {test_file.name}")

def fix_dungeon_generator_returns():
    """Fix DungeonGenerator.generate() return type handling"""

    test_file = Path('tests/test_integration.py')
    content = test_file.read_text()

    # The generator returns a dict, need to use Dungeon.load_from_generator()
    content = re.sub(
        r'dungeon = self\.generator\.generate\(config\)',
        r'dungeon_data = self.generator.generate(config)\n        dungeon = Dungeon.load_from_generator(dungeon_data)',
        content
    )

    # Also fix the .rooms access
    content = re.sub(
        r'len\(dungeon_easy\.rooms\)',
        r'len(dungeon_easy.rooms)',
        content
    )

    test_file.write_text(content)
    print(f"✓ Fixed DungeonGenerator returns in {test_file.name}")

def add_missing_import():
    """Add Dungeon import where missing"""
    for test_file in Path('tests').glob('test_*.py'):
        content = test_file.read_text()

        # Check if Dungeon is used but not imported
        if 'Dungeon(' in content or 'Dungeon.load' in content:
            if 'from aerthos.world.dungeon import Dungeon' not in content:
                # Add the import after other aerthos imports
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'from aerthos' in line and 'import' in line:
                        # Insert after this line
                        if 'Dungeon' not in line:
                            lines.insert(i+1, 'from aerthos.world.dungeon import Dungeon')
                            break
                content = '\n'.join(lines)
                test_file.write_text(content)
                print(f"✓ Added Dungeon import to {test_file.name}")

if __name__ == '__main__':
    print("Fixing all remaining test issues...\n")

    add_missing_import()
    fix_dungeon_construction()
    fix_dungeon_generator_returns()

    print("\n✓ All fixes applied!")
    print("\nRun: python3 run_tests.py --no-web")
