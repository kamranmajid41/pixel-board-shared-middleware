from os import environ
from urllib.parse import urljoin

from dotenv import load_dotenv
from flask import Flask, request, jsonify, make_response
from pixel_cache import PixelCache
from random import random
import requests

# Load the environment variables
load_dotenv()
SERVER_URL = environ['SERVER_URL']
MINION_NAME = environ['MINION_NAME']
AUTHOR = environ['AUTHOR']
SECRET = environ['SECRET']

# Register the PG with the middleware
r = requests.put(urljoin(SERVER_URL, '/register-pg'), json={
    "name": MINION_NAME,
    "author": AUTHOR,
    "secret": SECRET
})
id = r.json()["id"]

# Create an in-memory cache to store the pixels state
pixels_cache = PixelCache(SERVER_URL, id)

# Get app context
app = Flask(__name__)


@app.route('/update-pixel', methods=['PUT'])
def POST_send_pixel():
    update = requests.put(urljoin(SERVER_URL, '/update-pixel'), json={
        "id": id,
        "row": request.json['row'],
        "col": request.json['col'],
        "color": request.json['color']
    })

    return jsonify({'rate': update.json()['rate']})


@app.route('/settings', methods=['GET'])
def GET_settings():
    r = requests.get(urljoin(SERVER_URL, '/settings'))
    return jsonify(r.json())


@app.route('/pixels', methods=['GET'])
def GET_id():
    pixels_cache.update()

    # If the ETag for the pixels cache is the same as the one sent, we can send a 304 Not Modified back
    if request.if_none_match.contains(pixels_cache.etag):
        return '', 304

    # Send Response
    resp = make_response(jsonify({'pixels': pixels_cache.pixels}))
    resp.headers['ETag'] = pixels_cache.etag
    return resp
