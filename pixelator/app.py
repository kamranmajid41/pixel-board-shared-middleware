from flask import Flask, jsonify, render_template, request
import requests
import json 
import sys 
sys.path.append("/Users/macbookpro2015/Desktop/cs340/kmajid2/pixel-board-shared-middleware")
from pixelation import pixelation, save_image

app = Flask(__name__)

settings = {}
board = {}
# host_board = {}

# with app.app_context():
#     r = requests.put('http://127.0.0.1:5000/addPG', json = {"name" : "pixelizer2", "url": "http://127.0.0.1:9000/", "author" : "Kamran Majid", "weight" : 1})

with app.app_context():
    r = requests.put('http://127.0.0.1:5000/register-pg', json = {"name" : "pixelizer2", "author": "Kamran Majid", "secret" : "12TOKEN34"})
    id = r.json()["id"]

with app.app_context():
    r = requests.get('http://127.0.0.1:5000/settings').content
    settings = json.loads(r)

# Update the global "host_board" with the current status of the host board 
# with app.app_context():
#     r = requests.get('http://127.0.0.1:5000/board').content 
#     host_board = json.loads(r)

@app.route('/generator', methods=["GET"])
def generator():
    global board 
    global host_board

     # Call pixelation function only if it hasn't already been called, otherwise just return the global board
    if len(board) == 0: 
        board = pixelation("images/swiper.jpeg", settings["width"], settings["height"], settings["palette"])

    # Serve the pixel generator only the pixels that aren't already in the board, set the ones that are already there to '-1'
    pixels = []
    for i in range(settings["height"]):
        curr = []
        for j in range(settings["width"]):
            if i <= len(board) and j <= len(board[i]):
                if host_board['pixels'][i][j] == board[i][j]:
                    curr.append(-1) 
                else:
                    curr.append(board[i][j])
                    r = requests.put('http://127.0.0.1:5000/update-pixel', json = {"id" : id, "row": i, "column" : j, "color" : board[i][j]})
        
    return jsonify({"pixels" : pixels}), 200