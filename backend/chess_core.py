import threading
import chess
from backend.ai_engine import get_ai_move
from backend.evaluation import evaluate_board


class ChessGame:
    def __init__(self):
        self.player_color = chess.WHITE
        self.ai_depth = 3
        self.board = chess.Board()
        self.history_states = []
        self.redo_states = []
        self.san_history = []
        self.game_over = False
        self.result = None
        self.ai_thinking = False
        self._generation = 0
        self._lock = threading.RLock()
        self._last_sound = None

    @property
    def ai_color(self):
        return not self.player_color

    def set_player_color(self, color):
        with self._lock:
            self.player_color = chess.WHITE if color == "white" else chess.BLACK
            self._cancel_ai()
            return self.reset_game()

    def set_ai_depth(self, depth):
        with self._lock:
            self.ai_depth = max(1, min(6, int(depth)))
        return "ok"

    def _cancel_ai(self):
        self._generation += 1
        self.ai_thinking = False

    def _set_sound(self, sound):
        self._last_sound = sound

    def _take_sound(self):
        sound = self._last_sound
        self._last_sound = None
        return sound

    def _snapshot(self):
        return {
            "fen": self.board.fen(),
            "san": list(self.san_history),
            "game_over": self.game_over,
            "result": self.result,
        }

    def _restore(self, state):
        self.board = chess.Board(state["fen"])
        self.san_history = list(state["san"])
        self.game_over = state["game_over"]
        self.result = state["result"]

    def reset_game(self):
        with self._lock:
            self._cancel_ai()
            self.board = chess.Board()
            self.history_states.clear()
            self.redo_states.clear()
            self.san_history.clear()
            self.game_over = False
            self.result = None
            self._set_sound("reset")
            if self.board.turn != self.player_color:
                self._start_ai_move()
            return self.get_position()

    def _record_state(self):
        self.history_states.append(self._snapshot())
        self.redo_states.clear()

    def _update_game_status(self):
        if self.board.is_checkmate():
            self.game_over = True
            self.result = "0-1" if self.board.turn == chess.WHITE else "1-0"
        elif self.board.is_stalemate() or self.board.is_insufficient_material():
            self.game_over, self.result = True, "1/2-1/2"
        elif self.board.is_fivefold_repetition() or self.board.is_seventyfive_moves():
            self.game_over, self.result = True, "1/2-1/2"
        else:
            self.game_over = False
            self.result = None

    def _start_ai_move(self):
        if self.game_over or self.board.turn != self.ai_color or self.ai_thinking:
            return

        generation = self._generation
        fen = self.board.fen()
        depth = self.ai_depth
        self.ai_thinking = True

        def worker():
            try:
                search_board = chess.Board(fen)
                move = get_ai_move(search_board, depth)
            except Exception:
                move = None

            with self._lock:
                if generation != self._generation:
                    self.ai_thinking = False
                    return
                if self.game_over or self.board.fen() != fen:
                    self.ai_thinking = False
                    return

                if move is None:
                    self._update_game_status()
                    self.ai_thinking = False
                    if self.game_over:
                        self._set_sound("gameover")
                    return

                is_capture = self.board.is_capture(move)
                san = self.board.san(move)
                self.board.push(move)
                self.san_history.append(san)
                self._update_game_status()
                self.ai_thinking = False

                if self.game_over:
                    self._set_sound("gameover")
                elif self.board.is_check():
                    self._set_sound("check")
                elif is_capture:
                    self._set_sound("capture")
                else:
                    self._set_sound("move")

        threading.Thread(target=worker, daemon=True).start()

    def make_player_move(self, uci_move):
        with self._lock:
            if self.game_over:
                return {"status": "game_over", "result": self.result, "sound": "gameover"}
            if self.ai_thinking:
                return {"status": "error", "message": "AI is thinking...", "sound": "busy"}

            try:
                move = chess.Move.from_uci(uci_move)
            except ValueError:
                self._set_sound("illegal")
                return {"status": "error", "message": "Invalid move format.", "sound": "illegal"}

            if self.board.turn != self.player_color:
                return {"status": "error", "message": "It is the AI's turn.", "sound": "illegal"}
            if move not in self.board.legal_moves:
                self._set_sound("illegal")
                return {"status": "error", "message": "Illegal chess move.", "sound": "illegal"}

            self._record_state()
            is_capture = self.board.is_capture(move)
            san = self.board.san(move)
            self.board.push(move)
            self.san_history.append(san)
            self._update_game_status()

            if self.game_over:
                sound = "gameover"
            elif self.board.is_check():
                sound = "check"
            elif is_capture:
                sound = "capture"
            else:
                sound = "move"
            self._set_sound(sound)

            response = {
                "status": "ok",
                "player_move": uci_move,
                "player_san": san,
                "ai_move": None,
                "ai_thinking": False,
                "is_check": self.board.is_check(),
                "is_game_over": self.game_over,
                "result": self.result,
                "sound": sound,
            }

            if not self.game_over and self.board.turn == self.ai_color:
                self._start_ai_move()
                response["ai_thinking"] = True

            return response

    def get_legal_moves(self, square):
        with self._lock:
            try:
                sq = chess.parse_square(square)
            except ValueError:
                return []
            if self.game_over or self.ai_thinking or self.board.turn != self.player_color:
                return []
            piece = self.board.piece_at(sq)
            if piece is None or piece.color != self.player_color:
                return []
            return [m.uci() for m in self.board.legal_moves if m.from_square == sq]

    def get_history(self):
        with self._lock:
            return list(self.san_history)

    def suggest_move(self):
        """Return a best-move suggestion for the human player without making it."""
        with self._lock:
            if self.game_over:
                return {"status": "error", "message": "The game is over."}
            if self.ai_thinking:
                return {"status": "error", "message": "Wait until the AI finishes thinking."}
            if self.board.turn != self.player_color:
                return {"status": "error", "message": "It is the AI's turn."}

            search_board = self.board.copy(stack=True)
            move = get_ai_move(search_board, min(self.ai_depth, 4), time_limit=1.2)
            if move is None:
                return {"status": "error", "message": "No legal move is available."}

            return {
                "status": "ok",
                "move": move.uci(),
                "san": self.board.san(move),
                "from": chess.square_name(move.from_square),
                "to": chess.square_name(move.to_square),
                "message": f"Suggested move: {self.board.san(move)}",
            }

    def get_game_status(self):
        with self._lock:
            self._update_game_status()
            sound = self._take_sound()
            if self.game_over:
                return {"game_over": True, "result": self.result,
                        "message": self._result_message(), "ai_thinking": False, "sound": sound}
            if self.ai_thinking:
                return {"game_over": False, "result": None,
                        "message": "AI thinking...", "ai_thinking": True, "sound": sound}
            if self.board.is_check():
                return {"game_over": False, "result": None,
                        "message": "Check!", "ai_thinking": False, "sound": sound}
            return {"game_over": False, "result": None,
                    "message": "Your turn.", "ai_thinking": False, "sound": sound}

    def _result_message(self):
        if self.result == "1-0":
            return "White wins by checkmate."
        if self.result == "0-1":
            return "Black wins by checkmate."
        return "Draw."

    def request_draw(self):
        with self._lock:
            if self.game_over:
                return {"status": "game_over", "result": self.result,
                        "message": self._result_message(), "accepted": False}
            if self.ai_thinking:
                return {"status": "error", "message": "AI is still thinking.", "accepted": False,
                        "sound": "question"}

            score = evaluate_board(self.board)
            material = sum((1 if p.color == chess.WHITE else -1) * {
                chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
                chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0
            }[p.piece_type] for p in self.board.piece_map().values())
            moves = len(self.san_history)
            close_position = abs(score) <= 140
            low_material = abs(material) <= 2
            long_game = moves >= 24
            in_check = self.board.is_check()
            accepted = (close_position and not in_check) or low_material or (long_game and abs(score) <= 300)

            if accepted:
                self._cancel_ai()
                self.game_over = True
                self.result = "1/2-1/2"
                self._set_sound("draw")
                return {
                    "status": "ok", "accepted": True, "result": self.result,
                    "message": "AI agrees to a draw.",
                    "reason": "The AI considers the position sufficiently balanced.",
                    "sound": "draw"
                }

            self._set_sound("question")
            return {
                "status": "ok", "accepted": False, "result": None,
                "message": "AI declines the draw.",
                "reason": "The AI believes it still has enough winning chances.",
                "sound": "question"
            }

    def resign_game(self):
        with self._lock:
            if self.game_over:
                return {"status": "game_over", "result": self.result, "message": self._result_message()}
            self._cancel_ai()
            self.game_over = True
            self.result = "0-1" if self.player_color == chess.WHITE else "1-0"
            self._set_sound("victory")
            return {
                "status": "ok",
                "message": "You resigned. AI wins!",
                "result": self.result,
                "sound": "victory",
                "victory": True,
                "reason": "You resigned the game."
            }

    def undo_move(self):
        with self._lock:
            if not self.history_states:
                return "nothing"
            self._cancel_ai()
            self.redo_states.append(self._snapshot())
            self._restore(self.history_states.pop())
            self._set_sound("undo")
            return "ok"

    def redo_move(self):
        with self._lock:
            if not self.redo_states:
                return "nothing"
            self._cancel_ai()
            self.history_states.append(self._snapshot())
            self._restore(self.redo_states.pop())
            self._set_sound("redo")
            return "ok"

    def get_position(self):
        with self._lock:
            self._update_game_status()
            sound = self._take_sound()
            if self.game_over:
                message = self._result_message()
                reason = "Checkmate." if self.board.is_checkmate() else (
                    "The game ended in a draw." if self.result == "1/2-1/2" else "Game ended."
                )
            elif self.ai_thinking:
                message = "AI thinking..."
                reason = ""
            elif self.board.is_check():
                message = "Check! Your turn."
                reason = "Your king is in check."
            else:
                message = "Your turn."
                reason = ""

            return {
                "fen": self.board.fen(),
                "turn": "white" if self.board.turn == chess.WHITE else "black",
                "player_color": "white" if self.player_color == chess.WHITE else "black",
                "game_over": self.game_over,
                "result": self.result,
                "message": message,
                "reason": reason,
                "in_check": self.board.is_check(),
                "history": list(self.san_history),
                "ai_thinking": self.ai_thinking,
                "sound": sound,
            }
