# Liar's Bar Card Game

A multiplayer web-based card game where players bluff and challenge each other in a high-stakes game of deception. Built with FastAPI, WebSockets, and vanilla JavaScript.

## 🎮 Game Rules

- Players take turns playing 1-3 cards face down, claiming them to be a specific rank (K, Q, or A)
- Each round requires a specific card rank to be played
- Players can either challenge the previous play or continue the round
- If challenged:
  - If the player lied, they must play Russian Roulette
  - If the player was honest, the challenger must play Russian Roulette
- Getting shot in Russian Roulette eliminates the player
- Last player standing wins!

## 🚀 Features

- Real-time multiplayer gameplay using WebSockets
- Persistent game sessions
- Player name customization
- Automatic game state synchronization
- Mobile-responsive design
- Session recovery on disconnect

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Vanilla JavaScript
- **WebSockets**: For real-time communication
- **Styling**: CSS3 with custom variables
- **Templates**: Jinja2

## 🎯 How to Play

1. Create a new game or join an existing one using a game code
2. Share the game code with friends
3. First player can start the game once at least 2 players have joined
4. On your turn:
   - Select 1-3 cards to play
   - Claim them as the required rank
   - Other players can choose to challenge or continue
5. Stay alive and catch others in their lies!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Card game inspired by various bluffing games
- Built with love for game development and real-time web applications
