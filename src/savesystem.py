"""
Harvest Farm Constructor - Save System
Gerencia salvamento e carregamento do estado do jogo em JSON.
"""
import json
import os
from pathlib import Path

SAVE_DIR = Path(__file__).resolve().parent.parent / "saves"
SAVE_FILE = SAVE_DIR / "savegame.json"

def ensure_save_dir():
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
def save_game(player, world, game_day, game_hour, game_minute, season_idx, weather_name):
    """serializa o estado completo do jogo em json e salva no disco."""
    ensure_save_dir()
    data = {
        "version": 2,
        "player": {      # dados do jogador
            "x": player.x,
            "y": player.y,
            "coins": player.coins,
            "xp": player.xp,
            "level": player.level,
            "growth_boost": player.growth_boost,
            "seed_inventory": player.seed_inventory,
        },
        "world": {       # estado do mapa e das plantas
            "cols": world.cols,
            "rows": world.rows,
            "crop_state": {
                f"{r},{c}": v for (r, c), v in world.crop_state.items()
            },
            "crop_timer": {
                f"{r},{c}": v for (r, c), v in world.crop_timer.items()
            },
            "soil_wetness": {
                f"{r},{c}": v for (r, c), v in world.soil_wetness.items()
            },
        },
        "time": {        # hora, dia, estação e clima
            "day": game_day,
            "hour": game_hour,
            "minute": game_minute,
            "season_idx": season_idx,
            "weather": weather_name,
        }
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)  # salva com indentakão para legibilidade
    return True

def load_game():
    """carrega o estado do jogo do json. retorna dict ou none se não houver save."""
    if not SAVE_FILE.exists():
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("version", 1) < 2:  # save antigo: ignora
            return None
        return data
    except Exception:  # arquivo corrompido: ignora
        return None

def save_exists():
    return SAVE_FILE.exists()

def delete_save():
    if SAVE_FILE.exists():
        SAVE_FILE.unlink()

def apply_save(data, player, world, weather):
    """aplica os dados carregados nos objetos do jogo. retorna (dia, hora, minuto, season_idx)."""
    # dados do jogador
    pd = data["player"]
    player.x = float(pd["x"])
    player.y = float(pd["y"])
    player.coins = pd["coins"]
    player.xp = pd.get("xp", 0)
    player.level = pd.get("level", 1)
    player.growth_boost = pd.get("growth_boost", 0)
    player.seed_inventory = pd["seed_inventory"]

    # dados do mapa e plantas
    wd = data["world"]
    world.cols = wd["cols"]
    world.rows = wd["rows"]
    world.generate()
    world.crop_state = {
        tuple(int(x) for x in k.split(",")): v
        for k, v in wd["crop_state"].items()
    }
    world.crop_timer = {
        tuple(int(x) for x in k.split(",")): v
        for k, v in wd["crop_timer"].items()
    }
    world.soil_wetness = {
        tuple(int(x) for x in k.split(",")): v
        for k, v in wd["soil_wetness"].items()
    }

    # dados de tempo e clima
    td = data["time"]
    weather.weather = td.get("weather", "Ensolarado")

    return td["day"], td["hour"], td["minute"], td.get("season_idx", 0)
