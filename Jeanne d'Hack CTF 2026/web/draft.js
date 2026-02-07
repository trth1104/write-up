

let ws;
let currentSequence = [];
let playerSequence = [];
let isPlaying = false;
let gameStarted = false;
// Buffering / inter-round control
let pendingSequence = null;
let delayBeforeNext = false;
let playTimer = null;

// Read 'player_name' cookie on load and update the title if present.
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}


try {
    const cookieName = getCookie('player_name');
    if (cookieName) {
        const titleEl = document.getElementById('name-title');
        if (titleEl) titleEl.textContent = `${cookieName}'s Ocarina`;
    }
} catch (e) {
    console.warn('Could not read player_name cookie', e);
}

const NOTES = ['A','B','D','E','F'];


// --- Helpers: DOM, popups, errors, network, audio ---
const $id = (id) => document.getElementById(id);

function showPopup(popup) {
    if (!popup) return;
    popup.classList.remove('hidden');
    popup.setAttribute('aria-hidden', 'false');
    // focus first focusable element inside
    const focusable = popup.querySelector('input, button, [tabindex]:not([tabindex="-1"])');
    if (focusable) focusable.focus();
}

function hidePopup(popup) {
    if (!popup) return;
    popup.classList.add('hidden');
    popup.setAttribute('aria-hidden', 'true');
}

function showInlineError(containerId, message) {
    const el = $id(containerId);
    if (!el) return;
    el.textContent = message;
    el.classList.add('visible');
}

function clearInlineError(containerId) {
    const el = $id(containerId);
    if (!el) return;
    el.textContent = '';
    el.classList.remove('visible');
}

async function postJson(url, data, opts = {}) {
    const res = await fetch(url, Object.assign({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }, opts));
    let json = null;
    try { json = await res.json(); } catch(e) { /* ignore */ }
    if (!res.ok) {
        const err = new Error((json && json.message) || `Request failed (${res.status})`);
        err.status = res.status;
        err.body = json;
        throw err;
    }
    return json;
}


// Cache frequently used DOM elements to avoid repeated queries
const els = {
    startButton: $id('start-button'),
    startScreen: $id('start-screen'),
    gameScreen: $id('game-screen'),
    hintButton: $id('hint-button'),
    hintPopup: $id('hint-popup'),
    hintClose: $id('hint-close'),
    settingsButton: $id('settings-button'),
    settingsPopup: $id('settings-popup'),
    settingsSave: $id('settings-save'),
    settingsCancel: $id('settings-cancel'),
    playerNameInput: $id('player-name-input'),
    gameOverPopup: $id('game-over-popup'),
    popupMessage: $id('popup-message'),
    nameTitle: $id('name-title')
};

// Enable start button when Preload signals readiness
if (window.Preload) {
    Preload.onReady(() => {
        if (els.startButton) {
            els.startButton.disabled = false;
            els.startButton.textContent = 'Start';
        }
    });
} else {
    // fallback: enable shortly after load
    setTimeout(() => {
        if (els.startButton) {
            els.startButton.disabled = false;
            els.startButton.textContent = 'Start';
        }
    }, 1000);
}

// Initialize start button (disabled until resources load)
if (els.startButton) {
    els.startButton.disabled = true;
    els.startButton.textContent = 'Loading...';
}

// Wire up the Start button to launch the game when clicked
if (els.startButton) {
    els.startButton.addEventListener('click', () => {
        // Prevent double-starts
        if (gameStarted) return;
        gameStarted = true;

        // Hide start screen, show game screen
        if (els.startScreen) els.startScreen.style.display = 'none';
        if (els.gameScreen) els.gameScreen.style.display = 'block';
        
        // Hide hint and settings buttons during gameplay
        if (els.hintButton) els.hintButton.style.display = 'none';
        if (els.settingsButton) els.settingsButton.style.display = 'none';

        // Disable start button once clicked
        els.startButton.disabled = true;

        // Kick off WebSocket connection and game loop
        try { connect(); } catch (e) { console.error('Failed to start game', e); }
    });
}

// Start preloading of note sounds (fonts/image/hint started by preload.js)
if (window.Preload) {
    Preload.preloadNotes(NOTES);
}


function connect() {
    ws = new WebSocket(`ws://${window.location.host}/ws`);
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        if (data.type === "sequence") {
            // Buffer or play the incoming sequence. Server sends next sequence immediately;
            // the client applies a 500ms inter-round delay before playing the next sequence.
            const incoming = { seq: data.data, round: data.round };
            if (delayBeforeNext) {
                // Store the sequence to play after the delay
                pendingSequence = incoming;
            } else {
                processSequence(incoming);
            }
        } else if (data.type === "timeout") {
            disableButtons();
            gameStarted = false;
            ws.close();
            showGameOverPopup("Time's up!");
        } else if (data.type === "gameover") {
            disableButtons();
            gameStarted = false;
            ws.close();
            showGameOverPopup("Wrong lullaby!");
        } else if (data.type === "result") {
            const result = data.data;
            // Verification is immediate; start the 500ms inter-round delay before playing next
            if (result.correct) {
                // start the small delay before playing any incoming sequence
                delayBeforeNext = true;
                if (playTimer) clearTimeout(playTimer);
                playTimer = setTimeout(() => {
                    delayBeforeNext = false;
                    if (pendingSequence) {
                        const p = pendingSequence;
                        pendingSequence = null;
                        processSequence(p);
                    }
                }, 1500);
            }
        }
    };

    ws.onclose = function() {
        if (gameStarted) {
            disableButtons();
            gameStarted = false;
            showGameOverPopup("Connection lost! Game Over.");
        }
    };
}

function disableButtons() {
    document.querySelectorAll('.note').forEach(b => {
        b.disabled = true;
        b.classList.remove('playing');
    });
}

function enableButtons() {
    document.querySelectorAll('.note').forEach(b => {
        b.disabled = false;
        b.classList.remove('playing');
    });
}

// Process an incoming sequence: set state, play it, then enable player input
function processSequence(incoming) {
    if (!incoming) return;
    currentSequence = incoming.seq;
    updateRoundDisplay(incoming.round);
    // Reset state and disable input while sequence plays
    playerSequence = [];
    isPlaying = false;
    disableButtons();
    // Play the sequence and then enable input for player
    playSequence(currentSequence).then(() => {
        enableButtons();
        isPlaying = true;
        playerSequence = [];
    });
}

function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

async function playSequence(seq) {
    // Play each note with a pause between them. Adjusted for better timing
    const noteDuration = 800; // ms per note (reduced from 1000)
    const gap = 200; // ms gap between notes (reduced from 250)

    for (const n of seq) {
        // Play sound if available
        const btn = document.querySelector(`.note[data-note="${n}"]`);
        if (btn) btn.classList.add('playing');
        const a = (window.Preload && Preload.audioMap && Preload.audioMap[n]) ? Preload.audioMap[n] : null;
        if (a) {
            try { a.currentTime = 0; } catch(e){}
            await a.play().catch(err => console.warn('Playback blocked for sequence play', n, err));
        }
        // Wait noteDuration, then remove visual and wait gap
        await sleep(noteDuration);
        if (btn) btn.classList.remove('playing');
        await sleep(gap);
    }
}

function updateRoundDisplay(round) {
    const display = document.getElementById("round-display");
    if (display) display.textContent = `Round ${round} / 99`;
}

function showGameOverPopup(message) {
    if (els.popupMessage) els.popupMessage.textContent = message;
    showPopup(els.gameOverPopup || $id('game-over-popup'));
    
    // Show hint and settings buttons again when game is over
    if (els.hintButton) els.hintButton.style.display = '';
    if (els.settingsButton) els.settingsButton.style.display = '';
}

function playNote(note) {
    // Play audio on every click
    const pa = (window.Preload && Preload.audioMap && Preload.audioMap[note]) ? Preload.audioMap[note] : null;
    if (pa) {
        try { pa.currentTime = 0; } catch(e){}
        pa.play().catch(err => console.warn('Playback failed for', note, err));
    }

    // Only record note in sequence if currently expecting player input
    if (!isPlaying) return;

    playerSequence.push(note);

    if (playerSequence.length === currentSequence.length) {
        // Send sequence to server for verification
        ws.send(JSON.stringify({ type: "verify", sequence: playerSequence }));
        isPlaying = false;
    }
}

// Add click handlers to note buttons
document.querySelectorAll(".note").forEach(button => {
    button.addEventListener("click", () => playNote(button.dataset.note));
});

// Hint & Settings handling using cached els and helpers
if (els.hintButton && els.hintPopup) {
    els.hintButton.addEventListener('click', () => {
        const msgEl = $id('hint-message');
        if (msgEl) msgEl.innerHTML = 'Five seconds seems too short for the 99th lullaby, huh ?<br>Well deal with it ;)';
        showPopup(els.hintPopup);
        if (window.Preload && Preload.hintAudio) {
            try { Preload.hintAudio.currentTime = 0 } catch (e) {}
            Preload.hintAudio.play().catch(err => console.warn('Hint audio playback failed', err));
        } else if (window.Preload && Preload.loadAudio) {
            Preload.loadAudio('/static/sounds/hint.wav').then(a => { Preload.hintAudio = a; a.play().catch(()=>{}); }).catch(()=>{});
        } else {
            // last-resort fallback
            const fb = new Audio('/static/sounds/hint.wav'); fb.play().catch(()=>{});
        }
    });
}

if (els.hintClose && els.hintPopup) els.hintClose.addEventListener('click', () => hidePopup(els.hintPopup));
if (els.hintPopup) els.hintPopup.addEventListener('click', (e) => { if (e.target === els.hintPopup) hidePopup(els.hintPopup); });

function getCurrentPlayerNameFromTitle() {
    const t = els.nameTitle || $id('name-title');
    if (!t) return 'Jeanne';
    const txt = t.textContent || '';
    const match = txt.match(/^(.+?)'s\s+Ocarina/);
    return match ? match[1] : 'Jeanne';
}

if (els.settingsButton && els.settingsPopup) {
    els.settingsButton.addEventListener('click', () => {
        try { if (els.playerNameInput) els.playerNameInput.value = getCurrentPlayerNameFromTitle(); } catch(e){}
        showPopup(els.settingsPopup);
        clearInlineError('settings-error');
        if (els.playerNameInput) els.playerNameInput.focus();
    });
}

if (els.settingsCancel && els.settingsPopup) els.settingsCancel.addEventListener('click', () => hidePopup(els.settingsPopup));

if (els.settingsSave && els.playerNameInput) {
    els.settingsSave.addEventListener('click', async () => {
        let name = (els.playerNameInput.value || '').trim();
        if (!name) name = 'Jeanne';
        try {
            const data = await postJson('/set-name', { name });
            const newName = data.name || name;
            if (els.nameTitle) els.nameTitle.textContent = `${newName}'s Ocarina`;
            hidePopup(els.settingsPopup);
        } catch (err) {
            const msg = (err && err.body && err.body.message) || err.message || 'Failed to set name on server';
            showInlineError('settings-error', msg);
            return;
        }
    });
    els.playerNameInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); els.settingsSave.click(); } });
}

if (els.settingsPopup) els.settingsPopup.addEventListener('click', (e) => { if (e.target === els.settingsPopup) hidePopup(els.settingsPopup); });
