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
