import time
import chess
from backend.evaluation import evaluate_board

INF = 10**9

class SearchTimeout(Exception):
    pass


def _check_time(deadline):
    if deadline is not None and time.perf_counter() >= deadline:
        raise SearchTimeout


def minimax(board, depth, alpha, beta, deadline=None):
    _check_time(deadline)
    if depth <= 0 or board.is_game_over(claim_draw=True):
        return evaluate_board(board), None

    maximizing = board.turn == chess.WHITE
    best_move = None
    moves = list(board.legal_moves)
    moves.sort(key=lambda m: (board.is_capture(m), board.gives_check(m)), reverse=True)

    if maximizing:
        best_score = -INF
        for move in moves:
            _check_time(deadline)
            board.push(move)
            try:
                score, _ = minimax(board, depth - 1, alpha, beta, deadline)
            finally:
                board.pop()
            if score > best_score:
                best_score, best_move = score, move
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        return best_score, best_move

    best_score = INF
    for move in moves:
        _check_time(deadline)
        board.push(move)
        try:
            score, _ = minimax(board, depth - 1, alpha, beta, deadline)
        finally:
            board.pop()
        if score < best_score:
            best_score, best_move = score, move
        beta = min(beta, score)
        if alpha >= beta:
            break
    return best_score, best_move


def get_ai_move(board, depth=3, time_limit=None):
    """Iterative-deepening alpha-beta search.

    The requested depth is treated as a maximum, while the time limit prevents
    deep searches from freezing the application. The best fully completed
    iteration is always returned.
    """
    if board.is_game_over(claim_draw=True):
        return None

    depth = max(1, int(depth))
    if time_limit is None:
        time_limit = min(5.0, 0.45 * (2 ** max(0, depth - 2)))

    deadline = time.perf_counter() + max(0.15, float(time_limit))
    best_move = next(iter(board.legal_moves), None)

    for current_depth in range(1, depth + 1):
        try:
            _, move = minimax(board, current_depth, -INF, INF, deadline)
        except SearchTimeout:
            break
        if move is not None:
            best_move = move

    return best_move
