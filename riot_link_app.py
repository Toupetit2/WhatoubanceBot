import json
import os
from flask import Flask, request, render_template_string

app = Flask(__name__)

DATA_FILE = "data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Connexion Riot</title>
</head>
<body>
    <h2>Connecter Riot</h2>

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

    {% if success %}
        <p>✅ Compte lié :</p>
        <p>{{ riot_id }} - {{ rank }}</p>
    {% endif %}
</body>
</html>
"""


@app.route("/auth/riot", methods=["GET", "POST"])
def riot_link():
    discord_id = request.args.get("discord_id") or request.form.get("discord_id")

    if not discord_id:
        return "discord_id manquant"

    if request.method == "POST":
        game_name = request.form.get("game_name")
        tag_line = request.form.get("tag_line")
        rank = request.form.get("tft_rank")

        riot_id = f"{game_name}#{tag_line}"
        puuid = f"fake_{discord_id}"

        data = load_data()

        if "riot_links" not in data:
            data["riot_links"] = {}

        data["riot_links"][discord_id] = {
            "riot_id": riot_id,
            "puuid": puuid,
            "tft_rank": rank
        }

        save_data(data)

        return render_template_string(
            HTML,
            discord_id=discord_id,
            success=True,
            riot_id=riot_id,
            rank=rank
        )

    return render_template_string(
        HTML,
        discord_id=discord_id,
        success=False
    )


if __name__ == "__main__":
    app.run(debug=True)