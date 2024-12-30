from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request  # Added Request here
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict
import uuid
from .game import Game

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Store active games
games: Dict[str, Game] = {}

# Store active websocket connections
connections: Dict[str, WebSocket] = {}

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/game/{code}")
async def game_room(request: Request, code: str):
    return templates.TemplateResponse("game.html", {
        "request": request,
        "code": code
    })

@app.websocket("/ws/{game_code}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_code: str, player_id: str):
    await websocket.accept()
    connections[player_id] = websocket
    game = games.get(game_code)

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            print(f"Received action: {action} from player {player_id}")  # Debug log

            if action == "join":
                if game_code not in games:
                    games[game_code] = Game(game_code)
                game = games[game_code]
                game.add_player(player_id, data["name"])
                await broadcast_game_state(game)

            elif action == "start":
                print(f"Starting game {game_code}")  # Debug log
                if game_code in games:
                    game = games[game_code]
                    if game.start_game():
                        print(f"Game {game_code} started successfully")  # Debug log
                        await broadcast_game_state(game)
                    else:
                        print(f"Failed to start game {game_code}")  # Debug log
                else:
                    print(f"Game {game_code} not found")  # Debug log

            elif action == "play":
                if game and game.play_cards(player_id, data["cards"], data["claimRank"]):
                    await broadcast_game_state(game)
                    # Announce the play
                    player_name = next(p.name for p in game.players if p.id == player_id)
                    message = f"{player_name} played {len(data['cards'])} {data['claimRank']}s."
                    await broadcast_message(game, message)

            elif action == "challenge":
                if game:
                    result = game.challenge(player_id)
                    await broadcast_game_state(game)

            elif action == "continue":
                if game and game.continue_play(player_id):
                    await broadcast_game_state(game)

    except WebSocketDisconnect:
        if player_id in connections:
            del connections[player_id]
            if game:
                game.remove_player(player_id)
                await broadcast_game_state(game)

async def broadcast_game_state(game: Game):
    """Broadcast game state to all connected players"""
    if not game:
        return
        
    for player in game.players:
        if player.id in connections:
            try:
                state = game.get_game_state(player.id)
                await connections[player.id].send_json({
                    "type": "gameState",
                    "data": state
                })
            except Exception as e:
                print(f"Failed to send to player {player.id}: {e}")

async def broadcast_message(game: Game, message: str):
    for player in game.players:
        if player.id in connections:
            await connections[player.id].send_json({
                "type": "announcement",
                "message": message
            })