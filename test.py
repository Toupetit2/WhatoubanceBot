import requests

# nbMembres, rank, nbGames https://api-ggtech.leagueoflegends.com/api/v2/public/hubs/tft-clubs-fr/teams/whatoubance

url = "https://api-ggtech.leagueoflegends.com/api/v2/public/showcase/tft-clubs-fr/teamMembers?visible=true&perPage=15&teamSlug=whatoubance&rol=staff&page=1"

response = requests.get(url)

print("Status code :", response.status_code)

if response.status_code == 200:
    data = response.json()
    print("Résultat JSON :")
    print(data)
else:
    print("Erreur :", response.text)