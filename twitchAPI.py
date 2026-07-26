import os
import dotenv
import requests
import time

from utils.jsonStorage import load_data, save_data

dotenv.load_dotenv()
dotenv_file = dotenv.find_dotenv()




class TwitchAPI:

    def __init__(self):
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.CLIENT_SECRET = os.getenv("CLIENT_SECRET")

        self.TOKEN = os.getenv("TOKEN_TWITCH")

        self.data = load_data()
        if "expires_at" in self.data: #TODO: refactor
            self.EXPIRES_AT = self.data["expires_at"]
        else:
            self.EXPIRES_AT = 0

    def __get_token(self):
        # Get a new token for the twitch api
        global TOKEN, EXPIRES_AT

        if not self.CLIENT_ID or not self.CLIENT_SECRET:
            print("ERROR - CLIENT_ID ou CLIENT_SECRET manquant")
            raise ValueError("CLIENT_ID/CLIENT_SECRET manquant(s)")

        params = {
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
            "grant_type": "client_credentials"
        }

        response = requests.post("https://id.twitch.tv/oauth2/token", params=params, timeout=10).json()
        print(response)

        self.TOKEN = response["access_token"]
        self.EXPIRES_AT = time.time() + response["expires_in"]
        try:
            dotenv.set_key(dotenv_file, "TOKEN_TWITCH", self.TOKEN)
        except Exception as e:
            print(f"ERROR - Failed to update .env file: {e}")
        
        self.data["expires_at"] = self.EXPIRES_AT
        save_data(self.data)

    def get_valid_token(self):
        # Return the token for the twitch api, a new one if the old one is not 
        # valid (2 months lifetime)
        if time.time() >= self.EXPIRES_AT:
            self.__get_token()
        return self.TOKEN

    def is_live(self, username: str) -> bool:
        # username -> str, the streamer name on twitch
        # Return if a user if live using the api
        if not username:
            return False

        self.get_valid_token()

        if not self.TOKEN or not self.CLIENT_ID:
            print("ERROR - Twitch API token or client ID is not set.")

        headers = {
                "Client-ID": self.CLIENT_ID,
                "Authorization": f"Bearer {self.TOKEN}"
        }
        params = {"user_login": username}

        
        response = requests.get("https://api.twitch.tv/helix/streams", headers=headers, params=params, timeout=10).json()

        return len(response.get("data", [])) > 0

    def get_stream(self, username):
        # username -> str, the streamer name on twitch
        # Return the stream information of the streamer if on live, else None
        self.get_valid_token()

        headers = {
            "Client-ID": self.CLIENT_ID,
            "Authorization": f"Bearer {self.TOKEN}"
        }
        params = {"user_login": username}

        response = requests.get("https://api.twitch.tv/helix/streams", headers=headers, params=params).json()

        if len(response.get("data", [])) > 0:
            return response["data"][0]
        return None

    def get_profile_picture(self, username):
        # username -> str, the streamer name on twitch
        # Return the profile picture url of the streamer
        self.get_valid_token()

        headers = {
            "Client-ID": self.CLIENT_ID,
            "Authorization": f"Bearer {self.TOKEN}"
        }
        params = {"login": username}

        response = requests.get("https://api.twitch.tv/helix/users", headers=headers, params=params).json()

        if len(response.get("data", [])) > 0:
            return response["data"][0]["profile_image_url"]
        return None
    