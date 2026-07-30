import requests

# nbMembres, rank, nbGames https://api-ggtech.leagueoflegends.com/api/v2/public/hubs/tft-clubs-fr/teams/whatoubance

def in_wtb_club(riotID):
    url = "https://api-ggtech.leagueoflegends.com/api/v2/public/showcase/tft-clubs-fr/teamMembers?visible=true&perPage=-1&teamSlug=whatoubance"

    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
    else:
        print("Error GGtech API: ", response.text, flush=True)

    data = data["returnData"]["data"]
    for player in data:
            if player.get("gameNicks"):
                if riotID == player["gameNicks"][0]["nick"]:
                    return True
            
    return False

print(in_wtb_club("Toupetit2#WTB"))


