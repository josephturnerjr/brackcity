from flask import Flask, request, redirect, url_for, render_template
import json
app = Flask(__name__)


@app.route('/')
def main():
    with open('players.json') as f:
        players = json.loads(f.read())["players"]
    with open('games.json') as f:
        games = json.loads(f.read())["games"]
    game_matrix = [[0] * len(players) for player in players]
    for game in games:
        winner = players.index(game[0])
        loser = players.index(game[1])
        game_matrix[winner][loser] += 1
    for i, player in enumerate(players):
        game_matrix[i][i] = ""
    return render_template('index.html', players=players, game_matrix=game_matrix)


@app.route('/add', methods=['POST', 'GET'])
def add_player():
    if request.method == 'POST':
        name = str(request.form['username'])
        with open('players.json', 'r') as f:
            obj = json.loads(f.read())
        if name != "":
            obj["players"].append(name)
        with open('players.json', 'w') as f:
            obj = f.write(json.dumps(obj))
        return redirect(url_for('main'))
    else:
        return """<form action='/add' method='post'>
                  <input type='text' name='username'></input>
                  <input type='submit' value='Add player'></input></form>"""


@app.route('/game', methods=['POST', 'GET'])
def add_game():
    if request.method == 'POST':
        with open('games.json', 'r') as f:
            obj = json.loads(f.read())
        if request.form["winner"] != request.form["loser"]:
            obj["games"].append([request.form["winner"],
                                 request.form["loser"]])
        with open('games.json', 'w') as f:
            obj = f.write(json.dumps(obj))
        return redirect(url_for('main'))
    else:
        with open('players.json', 'r') as f:
            obj = json.loads(f.read())
        players_options = "".join(["<option value='%s'>%s</option>" % (name, name) for name in obj["players"]])
        return """<form action='/game' method='post'>
                  <label>Winner</label>
                  <select name='winner'>%s</select>
                  <label>Loser</label>
                  <select name='loser'>%s</select>
                  <input type='submit' value='Add game'>
                  </form>""" % (players_options, players_options)

if __name__ == "__main__":
    app.run(debug=True, port=3456)
