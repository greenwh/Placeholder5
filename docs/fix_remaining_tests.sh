#!/bin/bash

# Fix remaining test issues

echo "Fixing class names (Fighter not fighter)..."
find tests -name "test_*.py" -exec sed -i "s/char_class='fighter'/char_class='Fighter'/g" {} \;
find tests -name "test_*.py" -exec sed -i 's/char_class="fighter"/char_class="Fighter"/g' {} \;
find tests -name "test_*.py" -exec sed -i "s/'fighter'/'Fighter'/g" {} \;
find tests -name "test_*.py" -exec sed -i "s/'cleric'/'Cleric'/g" {} \;
find tests -name "test_*.py" -exec sed -i "s/'magic-user'/'Magic-User'/g" {} \;
find tests -name "test_*.py" -exec sed -i "s/'thief'/'Thief'/g" {} \;

echo "Fixing Dungeon() calls to use load_from_generator()..."
# This requires manual inspection of each test file

echo "Fixing PartyManager constructor - remove character_roster parameter..."
find tests -name "test_*.py" -exec sed -i 's/,\s*character_roster=self\.roster//g' {} \;
find tests -name "test_*.py" -exec sed -i 's/character_roster=self\.roster,\s*//g' {} \;

echo "Fixing SessionManager constructor - remove dependencies..."
find tests -name "test_*.py" -exec sed -i 's/,\s*character_roster=.*$/)/' {} \;

echo "✓ Fixed!"
echo "Note: Dungeon() calls need manual review - should use Dungeon(name, start_room_id, rooms dict)"
