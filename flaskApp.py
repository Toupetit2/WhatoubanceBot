import os
import json
import requests
import base64
from flask import Flask, request, render_template_string


class FlaskApp:
    def __init__(self, twitch_linker):
        self.app = Flask(__name__)

        self.DATA_FILE = "data.json"
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        self.REDIRECT_URI = "https://bot.whatoubance.fr/oauth/callback"
        self.RSO_CLIENT_ID = os.getenv("RSO_CLIENT_ID")
        self.RSO_CLIENT_SECRET = os.getenv("RSO_CLIENT_SECRET")

        self.twitch_linker = twitch_linker

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
            code = request.args.get("code")
            state = request.args.get("state") #discord_id

            if not code:
                print("ERROR: Missing code in Riot callback")
                return "Erreur : code manquant", 400
            
            basic = base64.b64encode(f"{self.CLIENT_ID}:{self.CLIENT_SECRET}".encode()).decode()

            headers = {
                "Authorization": f"Basic {basic}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.REDIRECT_URI
                }
        
            token_response = requests.post("https://auth.riotgames.com/token", headers=headers, data=data)

            token_data = token_response.json()

            print(f"DEBUG - status: {token_response.status_code}")
            print(f"DEBUG - token_data: {token_data}")


            if "access_token" not in token_data:
                return "Erreur lors de l'authentification Riot.", 400
            
            access_token = token_data["access_token"]

            user_info_response = requests.get(
                "https://auth.riotgames.com/userinfo",
                headers={
                    "Authorization": f"Bearer {access_token}"
                }
            )

            user_info = user_info_response.json()
            print(f"INFO - Riot user info: {user_info}")
            return "✅ Compte Riot lié avec succès ! Tu peux fermer cette page.", 200

        # -------- TWITCH CALLBACK --------
        @self.app.route("/auth/twitch/callback")
        def twitch_callback():
            code = request.args.get("code")
            state = request.args.get("state")

            return self.twitch_linker.handle_callback(code, state)

    # =========================
    # RUN
    # =========================

    def run(self):
        print("🔥 Flask running on http://localhost:3000")
        self.app.run(debug=True,use_reloader=False, port=3000)