import os
import dotenv
import discord
from twitchAPI import TwitchAPI
from discordAPI import DiscordAPI
import json
import utils.jsonStorage

class TwitchBot:
    def __init__(self):
        dotenv.load_dotenv(override=True)
        dotenv_file = dotenv.find_dotenv()

        self.twitchAPI = TwitchAPI()
        self.discordAPI = DiscordAPI()

        self.data = None

    def init_status_streams(self):
        self.data = utils.jsonStorage.load_data()
        if "streamers" not in self.data:
            self.data["streamers"] = {}
        if "streamers_embed_channel" not in self.data:
            self.data["streamers_embed_channel"] = {}
        if "streamers_embed_message" not in self.data:
            self.data["streamers_embed_message"] = {}
        for streamer in self.data["streamers"]:
            self.data["streamers"][streamer] = False
        utils.jsonStorage.save_data(self.data)

    def create_stream_embed(self, username):
        stream = self.twitchAPI.get_stream(username)
        profile_picture_url = self.twitchAPI.get_profile_picture(username)
        if stream is not None:
            image_url = stream["thumbnail_url"]
            image_url = image_url.replace("{width}", "640").replace("{height}", "360")

            embed = discord.Embed(title=stream["title"],
                    url=f"https://twitch.tv/{stream['user_login']}",
                    description=f"🎮{stream['game_name']}",
                    color=0x9146FF)
                
            embed.set_author(name=stream['user_name'], icon_url=profile_picture_url)
            embed.set_image(url=image_url)
            embed.set_footer(text="🔴 Live sur Twitch")
        return embed

    def add_stream(self, username, channel_id, message=""):
        self.data = utils.jsonStorage.load_data()
        stream_added = False
        if len(self.data["streamers"]) == 0:
            self.data["streamers"][username] = False
            self.data["streamers_embed_message"][username] = message
            self.data["streamers_embed_channel"][username] = channel_id
            stream_added = True
        elif username not in self.data["streamers"]:
            self.data["streamers"][username] = False
            self.data["streamers_embed_message"][username] = message
            self.data["streamers_embed_channel"][username] = channel_id
            stream_added = True

        utils.jsonStorage.save_data(self.data)
        
        return stream_added
    
    def get_stream_announce_channel(self, username):
        self.data = utils.jsonStorage.load_data()
        if username in self.data["streamers_embed_channel"]:
            return self.data["streamers_embed_channel"][username]
        return None

    def get_stream_embed_message(self, username):
        self.data = utils.jsonStorage.load_data()
        if username in self.data["streamers_embed_message"]:
            return self.data["streamers_embed_message"][username]
        return ""

    def remove_stream(self, username):
        self.data = utils.jsonStorage.load_data()
        stream_removed = False
        if username in self.data["streamers"]:
            del self.data["streamers"][username]
            del self.data["streamers_embed_channel"][username]
            del self.data["streamers_embed_message"][username]
            stream_removed = True

        utils.jsonStorage.save_data(self.data)
        
        return stream_removed

    def get_live_streams(self):
        live_streams = []
        for streamer in self.data["streamers"]:
            if self.twitchAPI.is_live(streamer):
                live_streams.append(streamer)
        return live_streams


    def check_streams_pings(self, bot):
        self.data = utils.jsonStorage.load_data()
        live_streams = self.get_live_streams()
        for streamer in self.data["streamers"]:
            if streamer in live_streams and not self.data["streamers"][streamer]:
                embed = self.create_stream_embed(streamer)
                bot.loop.create_task(self.discordAPI.send_message(bot, self.data["streamers_embed_channel"][streamer], self.data["streamers_embed_message"][streamer],embed=embed))
                self.data["streamers"][streamer] = True
            elif streamer not in live_streams and self.data["streamers"][streamer]:
                self.data["streamers"][streamer] = False
            
        utils.jsonStorage.save_data(self.data)
