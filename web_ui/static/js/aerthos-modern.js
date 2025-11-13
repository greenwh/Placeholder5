/**
 * Aerthos Modern UI - Main Application Logic
 */

// Global state
const AppState = {
    currentTab: 'characters',
    selectedCharacter: null,
    selectedParty: null,
    selectedScenario: null,
    activeSession: null,
    characters: [],
    parties: [],
    scenarios: [],
    sessions: []
};

// Initialize app on load
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    loadInitialData();
});

// ========== TAB MANAGEMENT ==========

function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}`).classList.add('active');

    AppState.currentTab = tabName;

    // Load data for tab if needed
    if (tabName === 'characters') loadCharacters();
    if (tabName === 'party') loadParties();
    if (tabName === 'dungeon') loadScenarios();
    if (tabName === 'session') loadSessions();
}

// ========== DATA LOADING ==========

async function loadInitialData() {
    await loadCharacters();
}

async function loadCharacters() {
    try {
        const response = await fetch('/api/character/list');
        const data = await response.json();
        AppState.characters = data.characters || [];
        renderCharacterList();
    } catch (error) {
        console.error('Error loading characters:', error);
    }
}

async function loadParties() {
    try {
        const response = await fetch('/api/party/list');
        const data = await response.json();
        AppState.parties = data.parties || [];
        renderPartyList();
    } catch (error) {
        console.error('Error loading parties:', error);
    }
}

async function loadScenarios() {
    try {
        const response = await fetch('/api/scenario/list');
        const data = await response.json();
        AppState.scenarios = data.scenarios || [];
        renderScenarioList();
    } catch (error) {
        console.error('Error loading scenarios:', error);
    }
}

async function loadSessions() {
    try {
        const response = await fetch('/api/session/list');
        const data = await response.json();
        AppState.sessions = data.sessions || [];
        renderSessionList();
    } catch (error) {
        console.error('Error loading sessions:', error);
    }
}

// ========== CHARACTER MANAGEMENT ==========

function renderCharacterList() {
    const listEl = document.getElementById('character-list');

    if (AppState.characters.length === 0) {
        listEl.innerHTML = `
            <div class="text-center" style="padding: 40px;">
                <p style="color: var(--text-secondary);">No characters yet. Create your first character!</p>
            </div>
        `;
        return;
    }

    listEl.innerHTML = AppState.characters.map(char => `
        <div class="character-card" onclick="selectCharacter('${char.id}')">
            <div class="character-header">
                <span class="character-name">${char.name}</span>
                <span class="character-level">Lvl ${char.level}</span>
            </div>
            <div class="character-class">${char.race} ${char.char_class}</div>
            <div class="character-stats">
                <div class="stat-bar">
                    <div class="stat-label">HP</div>
                    <div class="stat-bar-bg">
                        <div class="stat-bar-fill hp ${getHPClass(char.hp_current, char.hp_max)}"
                             style="width: ${(char.hp_current / char.hp_max) * 100}%">
                            ${char.hp_current}/${char.hp_max}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function getHPClass(current, max) {
    const percent = (current / max) * 100;
    if (percent <= 25) return 'low';
    if (percent <= 50) return 'medium';
    return '';
}

function selectCharacter(charId) {
    AppState.selectedCharacter = AppState.characters.find(c => c.id === charId);
    if (AppState.selectedCharacter) {
        renderCharacterDetails(AppState.selectedCharacter);
    }
}

function renderCharacterDetails(char) {
    const detailsEl = document.getElementById('character-details');
    const nameEl = document.getElementById('selected-character-name');
    const contentEl = document.getElementById('character-details-content');

    nameEl.textContent = char.name;
    detailsEl.style.display = 'block';

    contentEl.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
            <div>
                <h3>Attributes</h3>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px;">
                    ${renderStatBlock('STR', char.strength)}
                    ${renderStatBlock('DEX', char.dexterity)}
                    ${renderStatBlock('CON', char.constitution)}
                    ${renderStatBlock('INT', char.intelligence)}
                    ${renderStatBlock('WIS', char.wisdom)}
                    ${renderStatBlock('CHA', char.charisma)}
                </div>
                <h3 style="margin-top: 20px;">Combat</h3>
                <div class="panel" style="padding: 15px; margin-top: 10px;">
                    <p><strong>AC:</strong> ${char.ac}</p>
                    <p><strong>THAC0:</strong> ${char.thac0}</p>
                    <p><strong>XP:</strong> ${char.experience_points || 0}</p>
                </div>
            </div>
            <div>
                <h3>Equipment</h3>
                <div class="panel" style="padding: 15px; margin-top: 10px;">
                    ${char.inventory && char.inventory.length > 0 ?
                        char.inventory.map(item => `<p>• ${item}</p>`).join('') :
                        '<p style="color: var(--text-secondary);">No items</p>'}
                </div>
                ${char.spells && char.spells.length > 0 ? `
                    <h3 style="margin-top: 20px;">Spells</h3>
                    <div class="panel" style="padding: 15px; margin-top: 10px;">
                        ${char.spells.map(spell => `<p>• ${spell}</p>`).join('')}
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

function renderStatBlock(label, value) {
    return `
        <div class="panel" style="padding: 10px; text-align: center;">
            <div style="font-family: 'Cinzel', serif; color: var(--brown-dark); margin-bottom: 5px;">${label}</div>
            <div style="font-size: 1.5rem; font-weight: 700;">${value}</div>
        </div>
    `;
}

function createNewCharacter() {
    window.location.href = '/character_creation';
}

function editCharacter() {
    if (AppState.selectedCharacter) {
        alert('Edit character functionality coming soon!');
    }
}

function deleteCharacter() {
    if (AppState.selectedCharacter && confirm('Delete this character?')) {
        fetch(`/api/character/delete/${AppState.selectedCharacter.id}`, { method: 'POST' })
            .then(() => {
                document.getElementById('character-details').style.display = 'none';
                loadCharacters();
            });
    }
}

// ========== PARTY MANAGEMENT ==========

function renderPartyList() {
    const listEl = document.getElementById('party-list');

    if (AppState.parties.length === 0) {
        listEl.innerHTML = `
            <div class="text-center" style="padding: 40px;">
                <p style="color: var(--text-secondary);">No parties yet. Create your first party!</p>
            </div>
        `;
        return;
    }

    listEl.innerHTML = AppState.parties.map(party => `
        <div class="card" onclick="selectParty('${party.id}')">
            <h3 style="margin-bottom: 10px;">${party.name}</h3>
            <p style="color: var(--text-secondary);">Members: ${party.members.length}</p>
            <div style="margin-top: 10px;">
                ${party.members.slice(0, 4).map(m => `
                    <span style="display: inline-block; background: var(--parchment-dark); padding: 4px 8px;
                                 border-radius: 3px; margin: 2px; font-size: 0.9rem;">
                        ${m.name} (${m.level})
                    </span>
                `).join('')}
            </div>
        </div>
    `).join('');
}

function createNewParty() {
    document.getElementById('party-builder').style.display = 'block';
    loadCharactersForPartyBuilder();
}

function loadCharactersForPartyBuilder() {
    const selectionEl = document.getElementById('party-member-selection');
    selectionEl.innerHTML = AppState.characters.map(char => `
        <label class="card" style="cursor: pointer; padding: 10px;">
            <input type="checkbox" name="party-member" value="${char.id}" style="margin-right: 10px;">
            ${char.name} - Lvl ${char.level} ${char.char_class}
        </label>
    `).join('');
}

function cancelPartyBuilder() {
    document.getElementById('party-builder').style.display = 'none';
}

async function saveParty() {
    const name = document.getElementById('party-name').value;
    const selected = Array.from(document.querySelectorAll('input[name="party-member"]:checked'))
        .map(cb => cb.value);

    if (!name || selected.length === 0) {
        alert('Please enter a party name and select at least one member');
        return;
    }

    try {
        const response = await fetch('/api/party/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, character_ids: selected })
        });

        if (response.ok) {
            cancelPartyBuilder();
            loadParties();
        }
    } catch (error) {
        console.error('Error creating party:', error);
    }
}

// ========== DUNGEON/SCENARIO MANAGEMENT ==========

function renderScenarioList() {
    const listEl = document.getElementById('scenario-list');

    if (AppState.scenarios.length === 0) {
        listEl.innerHTML = `
            <div class="text-center" style="padding: 40px;">
                <p style="color: var(--text-secondary);">No scenarios yet. Generate your first dungeon!</p>
            </div>
        `;
        return;
    }

    listEl.innerHTML = AppState.scenarios.map(scenario => `
        <div class="card" onclick="selectScenario('${scenario.id}')">
            <h3 style="margin-bottom: 5px;">${scenario.name}</h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 10px;">
                ${scenario.description || 'No description'}
            </p>
            <div style="display: flex; gap: 10px;">
                <span class="exit-badge">${scenario.difficulty || 'medium'}</span>
                <span class="exit-badge">${scenario.num_rooms || '?'} rooms</span>
            </div>
        </div>
    `).join('');
}

function generateNewDungeon() {
    document.getElementById('dungeon-generator').style.display = 'block';

    // Load parties for selection
    const partySelect = document.getElementById('dungeon-party');
    partySelect.innerHTML = '<option value="">No party selected</option>' +
        AppState.parties.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
}

function cancelDungeonGenerator() {
    document.getElementById('dungeon-generator').style.display = 'none';
}

async function generateDungeon() {
    const payload = {
        name: document.getElementById('dungeon-name').value,
        description: document.getElementById('dungeon-description').value,
        difficulty: document.getElementById('dungeon-difficulty').value,
        party_id: document.getElementById('dungeon-party').value || null,
        num_rooms: parseInt(document.getElementById('dungeon-rooms').value),
        layout_type: document.getElementById('dungeon-layout').value,
        dungeon_theme: document.getElementById('dungeon-theme').value,
        seed: document.getElementById('dungeon-seed').value ? parseInt(document.getElementById('dungeon-seed').value) : null
    };

    try {
        const response = await fetch('/api/scenario/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (data.success) {
            cancelDungeonGenerator();
            loadScenarios();
            alert('Dungeon generated successfully!');
        }
    } catch (error) {
        console.error('Error generating dungeon:', error);
    }
}

// ========== SESSION MANAGEMENT ==========

function renderSessionList() {
    const listEl = document.getElementById('session-list');

    if (AppState.sessions.length === 0) {
        listEl.innerHTML = `
            <div class="text-center" style="padding: 40px;">
                <p style="color: var(--text-secondary);">No sessions yet. Create your first adventure!</p>
            </div>
        `;
        return;
    }

    listEl.innerHTML = AppState.sessions.map(session => `
        <div class="card" onclick="loadSession('${session.id}')">
            <h3 style="margin-bottom: 5px;">${session.name}</h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem;">
                ${session.party_name} in ${session.scenario_name}
            </p>
            <button class="btn btn-primary btn-small" style="margin-top: 10px;"
                    onclick="event.stopPropagation(); loadSession('${session.id}')">
                Continue Adventure
            </button>
        </div>
    `).join('');
}

function createNewSession() {
    document.getElementById('session-creator').style.display = 'block';

    // Load parties and scenarios
    const partySelect = document.getElementById('session-party');
    partySelect.innerHTML = '<option value="">Choose a party...</option>' +
        AppState.parties.map(p => `<option value="${p.id}">${p.name}</option>`).join('');

    const scenarioSelect = document.getElementById('session-scenario');
    scenarioSelect.innerHTML = '<option value="">Choose a scenario...</option>' +
        AppState.scenarios.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
}

function cancelSessionCreator() {
    document.getElementById('session-creator').style.display = 'none';
}

async function startSession() {
    const name = document.getElementById('session-name').value;
    const partyId = document.getElementById('session-party').value;
    const scenarioId = document.getElementById('session-scenario').value;

    if (!name || !partyId || !scenarioId) {
        alert('Please fill in all fields');
        return;
    }

    try {
        const response = await fetch('/api/session/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                party_id: partyId,
                scenario_id: scenarioId
            })
        });

        const data = await response.json();
        if (data.success) {
            cancelSessionCreator();
            loadSession(data.session_id);
        }
    } catch (error) {
        console.error('Error starting session:', error);
    }
}

async function loadSession(sessionId) {
    try {
        const response = await fetch(`/api/session/${sessionId}`);
        const data = await response.json();

        if (data.session) {
            AppState.activeSession = data.session;
            switchTab('play');
            initializeGameplay();
        }
    } catch (error) {
        console.error('Error loading session:', error);
    }
}

// ========== GAMEPLAY ==========

function initializeGameplay() {
    document.getElementById('no-session-message').style.display = 'none';
    document.getElementById('gameplay-interface').style.display = 'block';

    if (AppState.activeSession) {
        document.getElementById('current-session-name').textContent = AppState.activeSession.name;
        renderPartyStatus();
        renderCurrentRoom();
        renderDungeonMap();
    }
}

function renderPartyStatus() {
    const statusEl = document.getElementById('party-status');
    const party = AppState.activeSession.party;

    statusEl.innerHTML = party.members.map(member => `
        <div class="card" style="padding: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <strong>${member.name}</strong>
                <span style="font-size: 0.9rem;">Lvl ${member.level}</span>
            </div>
            <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 8px;">
                ${member.char_class}
            </div>
            <div class="stat-bar-bg" style="height: 16px;">
                <div class="stat-bar-fill hp ${getHPClass(member.hp_current, member.hp_max)}"
                     style="width: ${(member.hp_current / member.hp_max) * 100}%; font-size: 0.75rem;">
                    ${member.hp_current}/${member.hp_max}
                </div>
            </div>
        </div>
    `).join('');
}

function renderCurrentRoom() {
    const room = AppState.activeSession.current_room;

    document.getElementById('current-room-title').textContent = room.title;
    document.getElementById('current-room-description').textContent = room.description;

    const exitsEl = document.getElementById('current-room-exits');
    exitsEl.innerHTML = Object.keys(room.exits).map(direction => `
        <button class="btn btn-primary" onclick="moveToRoom('${direction}')">
            ${direction.toUpperCase()}
        </button>
    `).join('');
}

function renderDungeonMap() {
    // Initialize map renderer with current dungeon state
    if (window.DungeonMapRenderer) {
        window.dungeonRenderer = new window.DungeonMapRenderer('dungeonMap', AppState.activeSession.dungeon);
        window.dungeonRenderer.render(AppState.activeSession.current_room_id);
    }
}

async function moveToRoom(direction) {
    try {
        const response = await fetch(`/api/session/${AppState.activeSession.id}/move`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ direction })
        });

        const data = await response.json();
        if (data.success) {
            AppState.activeSession.current_room = data.room;
            AppState.activeSession.current_room_id = data.room_id;
            renderCurrentRoom();
            renderDungeonMap();

            // Check for encounters
            if (data.encounter) {
                handleEncounter(data.encounter);
            }
        }
    } catch (error) {
        console.error('Error moving:', error);
    }
}

function handleEncounter(encounter) {
    if (encounter.type === 'combat') {
        document.getElementById('combat-interface').style.display = 'block';
        // Initialize combat UI
    }
}

// Action functions
async function searchRoom() {
    if (!AppState.activeSession) return;

    try {
        const response = await fetch(`/api/session/${AppState.activeSession.id}/search`, {
            method: 'POST'
        });

        const data = await response.json();
        if (data.success) {
            showMessage(data.message, 'info');
            if (data.items && data.items.length > 0) {
                // Items found - could add to party inventory
                showMessage(`Found items: ${data.items.join(', ')}`, 'success');
            }
        } else {
            showMessage(data.error || 'Search failed', 'error');
        }
    } catch (error) {
        console.error('Error searching:', error);
        showMessage('Error searching room', 'error');
    }
}

async function rest() {
    if (!AppState.activeSession) return;

    if (!confirm('Rest your party? This may attract monsters if the room is not safe.')) {
        return;
    }

    try {
        const response = await fetch(`/api/session/${AppState.activeSession.id}/rest`, {
            method: 'POST'
        });

        const data = await response.json();
        if (data.success) {
            showMessage(data.message, 'success');
            // Reload session to get updated HP
            await loadSession(AppState.activeSession.id);
        } else {
            if (data.interrupted) {
                showMessage('Your rest was interrupted by monsters!', 'error');
                // Could trigger combat here
            } else {
                showMessage(data.error || 'Rest failed', 'error');
            }
        }
    } catch (error) {
        console.error('Error resting:', error);
        showMessage('Error resting', 'error');
    }
}

async function viewInventory() {
    if (!AppState.activeSession) return;

    try {
        const response = await fetch(`/api/session/${AppState.activeSession.id}/party`);
        const data = await response.json();

        if (data.success) {
            showInventoryModal(data.party);
        } else {
            showMessage(data.error || 'Failed to load inventory', 'error');
        }
    } catch (error) {
        console.error('Error loading inventory:', error);
        showMessage('Error loading inventory', 'error');
    }
}

async function viewCharacterSheets() {
    if (!AppState.activeSession) return;

    try {
        const response = await fetch(`/api/session/${AppState.activeSession.id}/party`);
        const data = await response.json();

        if (data.success) {
            showCharacterSheetsModal(data.party);
        } else {
            showMessage(data.error || 'Failed to load character sheets', 'error');
        }
    } catch (error) {
        console.error('Error loading character sheets:', error);
        showMessage('Error loading character sheets', 'error');
    }
}

function useItem() {
    showMessage('Click View Inventory to select and use items', 'info');
}

function castSpell() {
    showMessage('Click Character Sheets to view and cast spells', 'info');
}

async function saveGameSession() {
    if (!AppState.activeSession) return;

    try {
        const response = await fetch(`/api/session/${AppState.activeSession.id}/save`, {
            method: 'POST'
        });

        const data = await response.json();
        if (data.success) {
            showMessage(data.message || 'Game saved successfully!', 'success');
        } else {
            showMessage(data.error || 'Save failed', 'error');
        }
    } catch (error) {
        console.error('Error saving:', error);
        showMessage('Error saving game', 'error');
    }
}

// Helper function to show messages to user
function showMessage(message, type = 'info') {
    // Create message element
    const messageEl = document.createElement('div');
    messageEl.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
        color: white;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        font-family: 'Crimson Text', serif;
        max-width: 400px;
        animation: slideIn 0.3s ease;
    `;
    messageEl.textContent = message;

    document.body.appendChild(messageEl);

    // Remove after 3 seconds
    setTimeout(() => {
        messageEl.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => messageEl.remove(), 300);
    }, 3000);
}

// ========== MODAL DIALOGS ==========

function showInventoryModal(party) {
    const modal = createModal('Party Inventory');

    let content = '<div style="display: grid; gap: 20px;">';

    party.members.forEach(member => {
        content += `
            <div class="card" style="padding: 15px;">
                <h3 style="margin-bottom: 10px; color: var(--primary-color);">${member.name}</h3>
                <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 10px;">
                    ${member.char_class} • Level ${member.level} • ${member.gold} GP
                </div>
                <div style="margin-top: 10px;">
                    <strong>Inventory:</strong>
                    ${member.inventory && member.inventory.length > 0 ? `
                        <ul style="margin-left: 20px; margin-top: 5px;">
                            ${member.inventory.map(item => `
                                <li>${typeof item === 'string' ? item : item.name}
                                    ${item.type ? ` <span style="color: var(--text-secondary); font-size: 0.85rem;">(${item.type})</span>` : ''}
                                </li>
                            `).join('')}
                        </ul>
                    ` : '<div style="color: var(--text-secondary); margin-top: 5px;">No items</div>'}
                </div>
            </div>
        `;
    });

    content += '</div>';

    modal.body.innerHTML = content;
    document.body.appendChild(modal.element);
}

function showCharacterSheetsModal(party) {
    const modal = createModal('Character Sheets');

    let content = '<div style="display: grid; gap: 20px;">';

    party.members.forEach(member => {
        content += `
            <div class="card" style="padding: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                    <div>
                        <h3 style="color: var(--primary-color); margin-bottom: 5px;">${member.name}</h3>
                        <div style="color: var(--text-secondary);">${member.race} ${member.char_class}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.2rem; font-weight: bold;">Level ${member.level}</div>
                        <div style="font-size: 0.85rem; color: var(--text-secondary);">${member.xp} XP</div>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 15px;">
                    <div class="stat-display">
                        <div class="stat-label">HP</div>
                        <div class="stat-value">${member.hp_current}/${member.hp_max}</div>
                    </div>
                    <div class="stat-display">
                        <div class="stat-label">AC</div>
                        <div class="stat-value">${member.ac}</div>
                    </div>
                    <div class="stat-display">
                        <div class="stat-label">THAC0</div>
                        <div class="stat-value">${member.thac0}</div>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin-bottom: 15px;">
                    <div class="stat-display">
                        <div class="stat-label">STR</div>
                        <div class="stat-value">${member.strength}</div>
                    </div>
                    <div class="stat-display">
                        <div class="stat-label">DEX</div>
                        <div class="stat-value">${member.dexterity}</div>
                    </div>
                    <div class="stat-display">
                        <div class="stat-label">CON</div>
                        <div class="stat-value">${member.constitution}</div>
                    </div>
                    <div class="stat-display">
                        <div class="stat-label">INT</div>
                        <div class="stat-value">${member.intelligence}</div>
                    </div>
                    <div class="stat-display">
                        <div class="stat-label">WIS</div>
                        <div class="stat-value">${member.wisdom}</div>
                    </div>
                    <div class="stat-display">
                        <div class="stat-label">CHA</div>
                        <div class="stat-value">${member.charisma}</div>
                    </div>
                </div>

                ${member.spells && member.spells.length > 0 ? `
                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--border-color);">
                        <strong style="color: var(--primary-color);">Spells Known:</strong>
                        <ul style="margin-left: 20px; margin-top: 5px;">
                            ${member.spells.map(spell => `<li>${spell}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    });

    content += '</div>';

    modal.body.innerHTML = content;
    document.body.appendChild(modal.element);
}

function createModal(title) {
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    `;

    const modalBox = document.createElement('div');
    modalBox.style.cssText = `
        background: var(--bg-dark);
        border: 2px solid var(--border-color);
        border-radius: 8px;
        max-width: 800px;
        max-height: 80vh;
        width: 100%;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        display: flex;
        flex-direction: column;
    `;

    const header = document.createElement('div');
    header.style.cssText = `
        padding: 20px;
        border-bottom: 1px solid var(--border-color);
        display: flex;
        justify-content: space-between;
        align-items: center;
    `;
    header.innerHTML = `
        <h2 style="margin: 0; color: var(--primary-color);">${title}</h2>
        <button class="btn btn-small" onclick="this.closest('[style*=\\'position: fixed\\']').remove()">✕ Close</button>
    `;

    const body = document.createElement('div');
    body.style.cssText = `
        padding: 20px;
        overflow-y: auto;
        flex: 1;
    `;

    modalBox.appendChild(header);
    modalBox.appendChild(body);
    overlay.appendChild(modalBox);

    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.remove();
        }
    });

    return {
        element: overlay,
        body: body,
        header: header
    };
}

function endSession() {
    if (confirm('Exit this session?')) {
        AppState.activeSession = null;
        document.getElementById('gameplay-interface').style.display = 'none';
        document.getElementById('no-session-message').style.display = 'block';
        switchTab('session');
    }
}

function selectParty(id) { AppState.selectedParty = id; }
function selectScenario(id) { AppState.selectedScenario = id; }
