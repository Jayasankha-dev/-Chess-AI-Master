import os
import eel

try:
    import winsound
except ImportError:
    winsound = None

from backend.chess_core import ChessGame

eel.init("web")
game = ChessGame()
SOUND_DIR = os.path.join(os.path.dirname(__file__), "web", "sounds")


@eel.expose
def play_sound(name):
    """Play a bundled chess sound on Windows, with a system-alias fallback."""
    if winsound is None:
        return "unsupported"

    files = {
        "select": "select.wav",
        "move": "move.wav",
        "capture": "capture.wav",
        "check": "check.wav",
        "illegal": "illegal.wav",
        "gameover": "gameover.wav",
        "draw": "draw.wav",
        "question": "question.wav",
        "victory": "victory.wav",
        "reset": "reset.wav",
        "undo": "undo.wav",
        "redo": "redo.wav",
        "busy": "busy.wav",
    }
    filename = files.get(name, "move.wav")
    path = os.path.join(SOUND_DIR, filename)

    try:
        if os.path.isfile(path):
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return "ok"
    except Exception:
        pass

    # Fallback for systems where a local WAV cannot be played.
    aliases = {
        "select": "SystemDefault",
        "move": "SystemDefault",
        "capture": "SystemExclamation",
        "check": "SystemExclamation",
        "illegal": "SystemHand",
        "gameover": "SystemAsterisk",
        "draw": "SystemAsterisk",
        "question": "SystemQuestion",
        "victory": "SystemAsterisk",
        "reset": "SystemDefault",
        "undo": "SystemDefault",
        "redo": "SystemDefault",
        "busy": "SystemExclamation",
    }
    try:
        winsound.PlaySound(aliases.get(name, "SystemDefault"), winsound.SND_ALIAS | winsound.SND_ASYNC)
        return "fallback"
    except Exception:
        return "error"


@eel.expose
def make_move(uci_move):
    return game.make_player_move(uci_move)


@eel.expose
def get_board_fen():
    return game.board.fen()


@eel.expose
def get_position():
    return game.get_position()


@eel.expose
def reset_game():
    return game.reset_game()


@eel.expose
def undo_move():
    return game.undo_move()


@eel.expose
def redo_move():
    return game.redo_move()


@eel.expose
def get_history():
    return game.get_history()


@eel.expose
def get_legal_moves(square):
    return game.get_legal_moves(square)


@eel.expose
def set_player_color(color):
    return game.set_player_color(color)


@eel.expose
def set_ai_depth(depth):
    return game.set_ai_depth(depth)


@eel.expose
def suggest_move():
    return game.suggest_move()


@eel.expose
def offer_draw():
    return game.request_draw()


@eel.expose
def resign_game():
    return game.resign_game()


@eel.expose
def get_game_status():
    return game.get_game_status()


eel.start("index.html", size=(1250, 900), port=0)
