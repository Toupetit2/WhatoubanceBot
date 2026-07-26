import dotenv
import os
from flask import Flask, request, render_template_string
import requests
from discordAPI import DiscordAPI
import json
import asyncio

dotenv.load_dotenv()
dotenv_file = dotenv.find_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "https://bot.whatoubance.fr/oauth/twitch/callback"


class PendingLinks:
    def __init__(self):
        self.links = {}

    def set(self, state, display_name):
        self.links[state] = display_name

    def get(self, state):
        return self.links.get(state)

    def pop(self, state):
        return self.links.pop(state, None)


def is_wtb(display_name):
    return display_name.lower().startswith("wtb")


def load_data():
    if not os.path.exists("data.json"):
        return {}

    with open("data.json", "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


class TwitchLinker:
    def __init__(self, bot):
        self.pending_links = PendingLinks()
        self.bot = bot
        self.discordAPI = DiscordAPI()

    def get_auth_url(self, state):
        auth_url = (
            f"https://id.twitch.tv/oauth2/authorize"
            f"?client_id={CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}"
            f"&response_type=code"
            "&scope=user:read:email"
            f"&state={state}"
            "&force_verify=true"
        )
        return auth_url

    def handle_callback(self, code, state):
        token_res = requests.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI
            }
        ).json()

        if "access_token" not in token_res:
            return "<h1>❌ Erreur lors de la liaison Twitch</h1><p>Impossible d'obtenir le token d'accès.</p>"
        access_token = token_res["access_token"]

        user_res = requests.get(
            "https://api.twitch.tv/helix/users",
            headers={
                "Client-ID": CLIENT_ID,
                "Authorization": f"Bearer {access_token}"
            }
        ).json()

        user = user_res["data"][0]

        data = load_data()

        if is_wtb(user["display_name"]):
            coro = self.discordAPI.give_role(self.bot, int(data["guild_id"]), int(state), data["wtb_twitch_role_id"])
            future = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
        
            try:
                future.result(timeout=10)  # attend le résultat (ou lève l'exception)
            except Exception as e:
                print(f"Erreur give_role: {e}", flush=True)

        return """
        <h1>✅ Compte Twitch lié avec succès !</h1>
        <p>Tu peux retourner sur Discord.</p>
        """

    def get_pending_link(self, state):
        return self.pending_links.get(state)


class TwitchLinkerApp:
    def __init__(self, twitch_linker):
        self.twitch_linker = twitch_linker
        self.app = Flask(__name__)
        self._register_routes()

    def _register_routes(self):
        @self.app.route("/callback")
        def callback():
            code = request.args.get("code")
            state = request.args.get("state")
            return self.twitch_linker.handle_callback(code, state)

        @self.app.route("/riot-link", methods=["GET", "POST"])
        def riot_link():
            discord_id = request.args.get("discord_id") or request.form.get("discord_id")

            if not discord_id:
                return "discord_id manquant"

            if request.method == "POST":
                game_name = request.form.get("game_name", "").strip()
                tag_line = request.form.get("tag_line", "").strip()
                tft_rank = request.form.get("tft_rank", "").strip().upper()

                if not game_name or not tag_line:
                    return "Game Name ou Tag Line manquant"

                riot_id = f"{game_name}#{tag_line}"
                puuid = f"fake_{discord_id}"

                data = load_data()
                data["riot_links"] = data.get("riot_links", {})
                data["riot_links"][str(discord_id)] = {
                    "riot_id": riot_id,
                    "puuid": puuid,
                    "tft_rank": tft_rank
                }
                save_data(data)

                return f"""
                <h1>✅ Compte Riot lié avec succès !</h1>
                <p>Discord ID : {discord_id}</p>
                <p>Riot ID : {riot_id}</p>
                <p>Rang TFT : {tft_rank}</p>
                <p>Tu peux retourner sur Discord.</p>
                """

            return render_template_string("""
                <h1>Connecter Riot</h1>
                <form method="POST">
                    <input type="hidden" name="discord_id" value="{{ discord_id }}">

                    <p>Game Name :</p>
                    <input type="text" name="game_name" required>

                    <p>Tag Line :</p>
                    <input type="text" name="tag_line" required>

                    <p>Rang TFT :</p>
                    <select name="tft_rank">
                        <option>IRON</option>
                        <option>BRONZE</option>
                        <option>SILVER</option>
                        <option>GOLD</option>
                        <option>PLATINUM</option>
                        <option>EMERALD</option>
                        <option>DIAMOND</option>
                        <option>MASTER</option>
                        <option>GRANDMASTER</option>
                        <option>CHALLENGER</option>
                    </select>

                    <br><br>
                    <button type="submit">Valider</button>
                </form>
            """, discord_id=discord_id)

    def run(self, port=3000):
        self.app.run(port=port)