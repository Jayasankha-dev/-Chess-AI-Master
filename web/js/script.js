let position = null;
let selectedSquare = null;
let legalMoves = [];
let isBusy = false;
let pendingPromotion = null;
let aiPollTimer = null;
let soundEnabled = true;
let lastMove = null;
let hoverSquare = null;
let suggestedMove = null;
let suggestionBusy = false;

const files = 'abcdefgh';
const folders = {wK:'1',wP:'1',wQ:'1',wR:'1',bK:'2',bP:'2',bQ:'2',bR:'2',bB:'3',bN:'3',wB:'4',wN:'4'};

function pieceUrl(piece) {
    const folder = folders[piece] || '1';
    return `./svg/wikipedia/${folder}/${piece}@3x.png`;
}

function playSound(name) {
    if (!soundEnabled || !name || typeof eel === 'undefined') return;
    try { eel.play_sound(name)(); } catch (e) {}
}

function squareName(file, rank) { return files[file] + (rank + 1); }

function parseFen(fen) {
    const rows = fen.split(' ')[0].split('/');
    const map = {};
    for (let r = 0; r < 8; r++) {
        let f = 0;
        for (const ch of rows[r]) {
            if (/[1-8]/.test(ch)) f += Number(ch);
            else {
                const color = ch === ch.toUpperCase() ? 'w' : 'b';
                map[squareName(f, 7 - r)] = color + ch.toUpperCase();
                f++;
            }
        }
    }
    return map;
}

function boardIndex(square) {
    const f = files.indexOf(square[0]);
    const r = Number(square[1]) - 1;
    const black = position?.player_color === 'black';
    return {col: black ? 7 - f : f, row: black ? r : 7 - r};
}

function buildBoard() {
    const board = document.getElementById('board');
    board.innerHTML = '';
    const pieces = parseFen(position.fen);

    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const black = position.player_color === 'black';
            const file = black ? 7 - col : col;
            const rank = black ? row : 7 - row;
            const sq = squareName(file, rank);
            const el = document.createElement('div');
            el.className = `square ${((file + rank) % 2 === 0) ? 'light' : 'dark'}`;
            el.dataset.square = sq;

            const piece = pieces[sq];
            if (piece) {
                const img = document.createElement('img');
                img.alt = piece;
                img.draggable = false;
                img.src = pieceUrl(piece);
                img.onerror = () => el.classList.add('broken');
                el.appendChild(img);
            }

            if (file === 0) {
                const c = document.createElement('span');
                c.className = 'coord rank';
                c.textContent = rank + 1;
                el.appendChild(c);
            }
            if (rank === 0) {
                const c = document.createElement('span');
                c.className = 'coord file';
                c.textContent = files[file];
                el.appendChild(c);
            }

            el.addEventListener('click', () => clickSquare(sq));
            el.addEventListener('mouseenter', () => {
                hoverSquare = sq;
                renderMarkers();
            });
            el.addEventListener('mouseleave', () => {
                hoverSquare = null;
                renderMarkers();
            });
            board.appendChild(el);
        }
    }

    renderMarkers();
    drawHoverArrow();
}

function renderMarkers() {
    const pieces = position ? parseFen(position.fen) : {};
    document.querySelectorAll('.square').forEach(el => {
        el.classList.remove('selected', 'legal', 'capture', 'last', 'suggested');
        const sq = el.dataset.square;
        if (sq === selectedSquare) el.classList.add('selected');
        if (lastMove && (sq === lastMove.from || sq === lastMove.to)) el.classList.add('last');

        const move = legalMoves.find(x => x.slice(2, 4) === sq);
        if (move) el.classList.add(pieces[sq] ? 'capture' : 'legal');
        if (suggestedMove && (sq === suggestedMove.from || sq === suggestedMove.to)) el.classList.add('suggested');
    });
}

function drawHoverArrow() {
    const svg = document.getElementById('arrow-layer');
    svg.innerHTML = '';

    // The permanent green last-move arrow was intentionally removed.
    // A route arrow appears only while the user is selecting/hovering a legal destination.
    if (!selectedSquare || !hoverSquare) return;
    const route = legalMoves.find(m => m.slice(2, 4) === hoverSquare);
    if (!route) return;

    const a = boardIndex(selectedSquare);
    const b = boardIndex(hoverSquare);
    const wrap = document.getElementById('board-wrap');
    const w = wrap.clientWidth;
    const h = wrap.clientHeight;
    const x1 = (a.col + .5) * w / 8;
    const y1 = (a.row + .5) * h / 8;
    const x2 = (b.col + .5) * w / 8;
    const y2 = (b.row + .5) * h / 8;

    svg.innerHTML = `<defs><marker id="hover-arrow-head" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="hover-arrow-head"/></marker></defs><line class="hover-arrow" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" marker-end="url(#hover-arrow-head)"/>`;
}

function clickSquare(sq) {
    if (isBusy || !position || position.game_over) return;
    const pieces = parseFen(position.fen);

    if (selectedSquare) {
        const move = legalMoves.find(m => m.slice(2, 4) === sq);
        if (move) {
            if (move.length === 5) {
                pendingPromotion = {moves: legalMoves.filter(m => m.startsWith(selectedSquare + sq))};
                document.getElementById('promotion-modal').classList.remove('hidden');
            } else {
                sendMove(move);
            }
            return;
        }
    }

    const piece = pieces[sq];
    const mine = position.player_color === 'white' ? 'w' : 'b';
    if (piece && piece[0] === mine) {
        selectedSquare = sq;
        suggestedMove = null;
        eel.get_legal_moves(sq)(moves => {
            legalMoves = moves || [];
            renderMarkers();
            drawHoverArrow();
            playSound('select');
        });
    } else {
        selectedSquare = null;
        legalMoves = [];
        renderMarkers();
        drawHoverArrow();
    }
}

function sendMove(move) {
    pendingPromotion = null;
    document.getElementById('promotion-modal').classList.add('hidden');
    suggestedMove = null;
    isBusy = true;
    eel.make_move(move)(response => {
        isBusy = false;
        if (response.sound) playSound(response.sound);
        if (response.status === 'ok') {
            lastMove = {from: move.slice(0, 2), to: move.slice(2, 4)};
            selectedSquare = null;
            legalMoves = [];
            refresh();
            if (response.ai_thinking) pollAI();
        } else {
            setStatus(response.message || 'Move rejected.');
            renderMarkers();
        }
    });
}

function pollAI() {
    clearTimeout(aiPollTimer);
    aiPollTimer = setTimeout(() => eel.get_position()(p => {
        position = p;
        buildBoard();
        renderHistory(p.history || []);
        updateStatus();
        if (p.sound) playSound(p.sound);
        if (p.ai_thinking) pollAI();
        else if (p.game_over) showResult(p);
    }), 180);
}

function refresh(cb) {
    eel.get_position()(p => {
        position = p;
        buildBoard();
        renderHistory(p.history || []);
        updateStatus();
        if (p.sound) playSound(p.sound);
        if (p.game_over) showResult(p);
        if (cb) cb(p);
    });
}

function setStatus(text) { document.getElementById('status').textContent = text; }

function updateStatus() {
    if (!position) return;
    setStatus(position.message || 'Your turn.');
    document.getElementById('board-wrap').classList.toggle('ai-busy', !!position.ai_thinking);
}

function renderHistory(history) {
    const moves = history || [];
    const list = document.getElementById('move-list');
    const count = document.getElementById('history-count');

    if (!moves.length) {
        list.innerHTML = '<div class="history-empty">No moves yet. Start the game to build the move history.</div>';
        count.textContent = 'No moves yet.';
        return;
    }

    list.innerHTML = moves.map((move, i) =>
        `<div class="move-row"><span>${i + 1}.</span><span>${escapeHtml(move)}</span></div>`
    ).join('');
    count.textContent = `${moves.length} move${moves.length === 1 ? '' : 's'}`;
}

function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function showResult(p) {
    if (!p.game_over) return;
    const modal = document.getElementById('game-result-modal');
    const title = document.getElementById('result-title');
    const msg = document.getElementById('result-message');
    const why = document.getElementById('result-reason');
    const playerWon = (p.player_color === 'white' && p.result === '1-0') || (p.player_color === 'black' && p.result === '0-1');
    document.getElementById('result-icon').textContent = p.result === '1/2-1/2' ? '🤝' : playerWon ? '🏆' : '♛';
    title.textContent = p.result === '1/2-1/2' ? 'Draw' : playerWon ? 'Victory!' : 'AI Wins';
    title.className = p.result === '1/2-1/2' ? 'draw-title' : playerWon ? 'win-title' : 'loss-title';
    msg.textContent = p.message || '';
    why.textContent = p.reason || '';
    modal.classList.remove('hidden');
}

function resetGame() {
    eel.reset_game()(() => {
        lastMove = null;
        selectedSquare = null;
        legalMoves = [];
        suggestedMove = null;
        document.getElementById('game-result-modal').classList.add('hidden');
        document.getElementById('suggestion-box').classList.add('hidden');
        refresh();
    });
}

function undoMove() {
    eel.undo_move()(r => {
        if (r === 'ok') {
            lastMove = null;
            suggestedMove = null;
            refresh();
        } else setStatus('Nothing to undo.');
    });
}

function redoMove() {
    eel.redo_move()(r => {
        if (r === 'ok') {
            lastMove = null;
            suggestedMove = null;
            refresh();
        } else setStatus('Nothing to redo.');
    });
}

function offerDraw() {
    eel.offer_draw()(r => {
        if (r.sound) playSound(r.sound);
        setStatus(r.message || '');
        if (r.accepted) refresh();
    });
}

function resignGame() {
    eel.resign_game()(r => {
        if (r.sound) playSound(r.sound);
        refresh();
    });
}

function requestSuggestion() {
    if (suggestionBusy || !position || position.game_over || position.ai_thinking) return;
    suggestionBusy = true;
    const box = document.getElementById('suggestion-box');
    const text = document.getElementById('suggestion-text');
    box.classList.remove('hidden');
    text.textContent = 'Analyzing the position...';

    eel.suggest_move()(result => {
        suggestionBusy = false;
        if (result.status !== 'ok') {
            suggestedMove = null;
            text.textContent = result.message || 'No suggestion available.';
            renderMarkers();
            return;
        }
        suggestedMove = {from: result.from, to: result.to};
        text.innerHTML = `<strong>${escapeHtml(result.san)}</strong> — ${escapeHtml(result.from)} → ${escapeHtml(result.to)}`;
        renderMarkers();
    });
}

window.addEventListener('resize', drawHoverArrow);

window.addEventListener('load', () => {
    document.getElementById('sound-enabled').addEventListener('change', e => {
        soundEnabled = e.target.checked;
        if (soundEnabled) playSound('select');
    });
    document.getElementById('reset-btn').onclick = resetGame;
    document.getElementById('undo-btn').onclick = undoMove;
    document.getElementById('redo-btn').onclick = redoMove;
    document.getElementById('draw-btn').onclick = offerDraw;
    document.getElementById('resign-btn').onclick = resignGame;
    document.getElementById('suggest-btn').onclick = requestSuggestion;
    document.getElementById('result-new-game').onclick = resetGame;

    const aboutModal = document.getElementById('about-modal');
    const closeAbout = () => aboutModal.classList.add('hidden');
    document.getElementById('about-close').onclick = closeAbout;
    document.getElementById('about-ok').onclick = closeAbout;
    aboutModal.addEventListener('click', e => {
        if (e.target === aboutModal) closeAbout();
    });

    const historyModal = document.getElementById('history-modal');
    document.getElementById('history-btn').onclick = () => {
        renderHistory(position?.history || []);
        historyModal.classList.remove('hidden');
    };
    document.getElementById('history-close').onclick = () => historyModal.classList.add('hidden');
    historyModal.addEventListener('click', e => {
        if (e.target === historyModal) historyModal.classList.add('hidden');
    });
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
            historyModal.classList.add('hidden');
            aboutModal.classList.add('hidden');
        }
    });

    document.getElementById('player-color').onchange = e => eel.set_player_color(e.target.value)(p => {
        position = p;
        lastMove = null;
        suggestedMove = null;
        selectedSquare = null;
        legalMoves = [];
        buildBoard();
        renderHistory(p.history || []);
        updateStatus();
        if (p.sound) playSound(p.sound);
        if (p.ai_thinking) pollAI();
    });

    document.getElementById('ai-depth').oninput = e => {
        document.getElementById('depth-label').textContent = e.target.value;
        eel.set_ai_depth(Number(e.target.value));
    };

    document.querySelectorAll('#promotion-buttons button').forEach(button => {
        button.onclick = () => {
            if (pendingPromotion) {
                const move = pendingPromotion.moves.find(x => x.endsWith(button.dataset.piece));
                if (move) sendMove(move);
            }
        };
    });

    refresh();
});
