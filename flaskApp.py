import os
import json
import requests
import base64
import asyncio
from riot_link_handle_callback import handle_callback as riot_handle_callback
from flask import Flask, request, render_template_string
from tftAPI import get_tft_rank


class FlaskApp:
    def __init__(self, twitch_linker):
        self.app = Flask(__name__)

        self.DATA_FILE = "data.json"
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        self.REDIRECT_URI =  os.getenv("REDIRECT_URI")
        self.RSO_CLIENT_ID = os.getenv("RSO_CLIENT_ID")
        self.RSO_CLIENT_SECRET = os.getenv("RSO_CLIENT_SECRET")

        self.twitch_linker = twitch_linker
        self.discordAPI = twitch_linker.discordAPI

        self.bot = twitch_linker.bot 

        self.register_routes()

    # =========================
    # DATA
    # =========================

    def load_data(self):
        if not os.path.exists(self.DATA_FILE):
            return {}

        with open(self.DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}

    def save_data(self, data):
        with open(self.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # =========================
    # ROUTES
    # =========================

    def register_routes(self):

        # -------- RIOT LINK --------
        @self.app.route("/oauth/callback")
        def riot_link():
            print("=== RIOT CALLBACK RECEIVED ===", flush=True)

            code = request.args.get("code")
            state = request.args.get("state") #discord_id

            if not code:
                return "Erreur : code manquant", 400
            
            return riot_handle_callback(self.discordAPI, self.bot, code, state)

        # -------- TWITCH CALLBACK --------
        @self.app.route("/oauth/twitch/callback")
        def twitch_callback():
            code = request.args.get("code")
            state = request.args.get("state")

            return self.twitch_linker.handle_callback(code, state)

    # =========================
    # RUN
    # =========================

    def run(self):
        self.app.run(use_reloader=False, port=3000)