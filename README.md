<img width="1920" height="1016" alt="Capture" src="https://github.com/user-attachments/assets/b84f042a-90fe-4306-975a-10f1fbfeaa0a" />


````markdown
# ♟️ Chess AI Master

A modern desktop Chess application with an intelligent AI opponent, 
interactive board UI, move history, best-move suggestions, sound effects, 
and a developer-focused interface.

Built with Python and a web-based frontend, 
Chess AI Master is designed to provide a clean and enjoyable chess experience while
remaining lightweight and compatible with older Windows systems.

---

## ✨ Features

### ♟️ Chess Gameplay

- Full chess board interface
- Legal move validation
- Capture highlighting
- Check detection
- Checkmate detection
- Stalemate detection
- Castling
- En passant
- Pawn promotion
- Undo / Redo
- Resign
- New Game / Reset

### 🤖 AI Opponent

- Minimax-based chess AI
- Alpha-Beta pruning
- Configurable AI difficulty
- Search depth control
- AI thinking indicator
- Best Move suggestion system
- AI position evaluation
- Automatic AI move generation

### 🎯 Best Move Suggestions

The player can request an AI recommendation without automatically playing the move.

The application highlights the recommended move on the board so the player can decide whether to follow the suggestion.

### 📜 Move History

Move history is available through a dedicated popup.

- Clean terminal-style move list
- Scrollable history
- Move counter
- White and Black moves
- Does not expand the main page
- Easy to open and close

### 🔊 Chess Sounds

Optional chess sound effects are available for different game events.

Supported events include:

- Normal moves
- Captures
- Check
- Illegal moves
- Undo
- Redo
- Victory
- Draw

Sound effects can be enabled or disabled by the user.

### 🎨 Modern UI

- Clean chess interface
- Responsive board
- Move highlighting
- Hover route indicators
- AI thinking state
- Developer information popup
- Animated RGB developer card
- Dark-themed interface
- Smooth UI interactions

### 👨‍💻 Developer Popup

When the application starts, a small developer information popup introduces the project and its creator.

The popup includes:

- Developer information
- GitHub profile
- Project information
- MIT License information
- Technology overview
- RGB animated visual design

Developer:

**Jayasankha Madhusith**

GitHub:

https://github.com/Jayasankha-dev

---

## 🧠 AI Architecture

The chess AI uses a traditional game-tree search approach.

```text

Current Board Position
        │
        ▼
Generate Legal Moves
        │
        ▼
Evaluate Candidate Moves
        │
        ▼
Minimax Search
        │
        ▼
Alpha-Beta Pruning
        │
        ▼
Position Evaluation
        │
        ▼
Best Move
        │
        ▼
Play Move
````

The AI searches possible future positions and evaluates them to select a strong move.

---

## 🛠️ Technologies

* Python
* JavaScript
* HTML5
* CSS3
* Minimax
* Alpha-Beta Pruning
* PyInstaller
* Local audio assets
* SVG chess-piece assets

---

## 📁 Project Structure

```text
Chess AI Master/
│
├── main.py
│
├── backend/
│   ├── __init__.py
│   ├── chess_core.py
│   ├── ai_engine.py
│   └── evaluation.py
│
├── web/
│   ├── index.html
│   │
│   ├── css/
│   │
│   ├── js/
│   │
│   ├── sounds/
│   │
│   └── svg/
│       └── wikipedia/
│           ├── 1/
│           ├── 2/
│           ├── 3/
│           └── 4/
│
├── LICENSE
└── README.md
```

---

## 🖥️ Windows 7 Support

The project is designed with compatibility with older Windows systems in mind.

For building a standalone Windows executable, the recommended environment is:

* Python 3.8.x
* PyInstaller 5.13.2

Recommended build command:

```bat
pyinstaller --clean --noconfirm --onefile --windowed --name "Chess AI Master" --add-data "web;web" main.py
```

After building:

```text
dist/
└── Chess AI Master.exe
```

The `--onefile` option creates a single executable.

The `--windowed` option prevents a console window from appearing.

The complete `web` directory is packaged into the executable, including:

* HTML
* CSS
* JavaScript
* Sounds
* Chess piece assets

---

## 🚀 Running From Source

Clone the repository:

```bash
git clone https://github.com/Jayasankha-dev/your-repository-name.git
```

Enter the project directory:

```bash
cd your-repository-name
```

Run the application:

```bash
python main.py
```
```bash
pyinstaller --clean --noconfirm --onefile --windowed --icon="icon.ico" --name "Chess AI Master" --add-data "web;web" main.py
```
> Make sure the `web` directory and its required assets remain in the correct project structure.

---

## 🎮 How to Play

1. Start the application.
2. Select your preferred side.
3. Choose the AI difficulty.
4. Make a move on the board.
5. The AI will calculate its response.
6. Use **Best Move** whenever you want an AI recommendation.
7. Open **Move History** to review previous moves.
8. Enable or disable sounds from the settings.
9. Use Undo / Redo when needed.

---

## 💡 Suggested Settings

For a balanced experience:

```text
AI Depth: 3–4
Chess Sounds: ON
Best Move: Use when needed
```

Higher AI depth may provide stronger moves but can require more processing time.

---

## 🔮 Future Improvements

Possible future development ideas include:

* ♟️ Opening book
* 🧠 Stronger evaluation engine
* 📊 Evaluation bar
* ⏱️ Chess clocks
* 🌐 Online multiplayer
* 💾 Save / Load games
* 📄 PGN import and export
* 🏆 ELO-style rating system
* 📈 Game analysis
* 🔥 More advanced AI search
* 🎨 Additional board themes
* 🌍 Multi-language support

---

## 📜 License

This project is released under the **MIT License**.

You are free to:

* Use the software
* Modify the source code
* Distribute the software
* Use it for personal or commercial projects

See the [`LICENSE`](LICENSE) file for the complete license text.

### Third-Party Assets

Some chess piece graphics and other resources may originate from third-party sources.

Please review the relevant asset directories and their associated licensing or attribution requirements before redistributing those assets separately.

---

## 👨‍💻 Developer

### Jayasankha Madhusith

Developer and creator of **Chess AI Master**.

GitHub:

**[https://github.com/Jayasankha-dev](https://github.com/Jayasankha-dev)**

---

## ⭐ Support the Project

If you find this project useful:

* ⭐ Star the repository
* 🍴 Fork the project
* 🐛 Report bugs
* 💡 Suggest improvements
* 🔧 Contribute improvements

Every contribution and suggestion is appreciated.

---

## ❤️ About This Project

Chess AI Master is an ongoing personal development project focused on combining chess logic, artificial intelligence, user interface design, and desktop application development into one practical project.

The project will continue to evolve with stronger AI, improved UI, better performance, and additional chess features.

---

**Built with ♟️ Python, AI, and passion for chess.**

© 2026 Jayasankha Madhusith — Chess AI Master
