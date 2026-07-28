import discord
import json
import os

def give_coins(amount: int, member: discord.Member):
    
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    data[str(member.id)]["monnaie"] += amount

    with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)



