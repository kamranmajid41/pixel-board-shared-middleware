from os import environ
from random import randrange, randint
from time import sleep
from urllib.parse import urljoin
import requests
import numpy as np

from dotenv import load_dotenv
from cross_out import CrossOut, color_distance
from PIL import ImageColor
from pixelation import pixelation, save_image
# Load the environment variables
load_dotenv()
MINION_URL = environ['MINION_URL']


class Gru:
    def __init__(self) -> None:
        # Load minions
        self.minions = MINION_URL
        # Load settings from the first minion
        r = requests.get(urljoin(self.minions, '/settings'))
        settings = r.json()
        self.height = settings['height']
        self.width = settings['width']
        self.palette = settings['palette']

        # Create an in-memory cache to store the pixels state
        self.pixels_cache = None
        self.pixels_cache_etag = ''

        # Store the pixel rate
        self.rate = None

        # Current minion counter
        self.cur_minion = 0

        # Find red and black
        self.palette_rgb = [ImageColor.getrgb(x) for x in self.palette]
        self.RED = np.argmin(list(map(lambda x: color_distance(
            x, (255, 0, 0)), self.palette_rgb)))
        self.BLACK = np.argmin(list(map(lambda x: color_distance(
            x, (0, 0, 0)), self.palette_rgb)))

        self.RED_RGB = self.palette_rgb[self.RED]
        self.BLACK_RGB = self.palette_rgb[self.BLACK]

    def update_pixel(self, row, col, color):
        if row >= self.height or col >= self.width \
                or row < 0 or col < 0:
            self.rate = 0
            return

        self.update_pixel_cache()

        # color = self.RED if self.pixels_cache[row][col] != self.RED else self.BLACK

        if self.pixels_cache[row][col] == color:
            self.rate = 0
            return

        update = requests.put(urljoin(self.minions, '/update-pixel'), json={
            "row": int(row),
            "col": int(col),
            "color": int(color)
        })

        self.rate = update.json()['rate']
        # Change active minion
        self.cur_minion = (self.cur_minion + 1) % len(self.minions)

    def update_pixel_cache(self):
        r = requests.get(urljoin(self.minions, '/pixels'),
                         headers={"If-None-Match": self.pixels_cache_etag})
        if r.status_code == 200:
            self.pixels_cache = r.json()["pixels"]
            self.pixels_cache_etag = r.headers.get('ETag')


if __name__ == '__main__':

    gru = Gru()

    # Create pixelated image
    board = pixelation("images/swiper.jpeg", 30, 30, gru.palette)
    save_image(board, len(board[0]), len(board), gru.palette)
    offsetRow = 0
    offsetCol = 0
    
    while True:
        gru.update_pixel_cache()

        # Increase offset by random vals but ensure it's within bounds 
        offsetRow = randint(0, len(board) - 30)
        offsetCol = randint(0, len(board[0]) - 30)

        for i in range(len(board)):
            for j in range(len(board[0])): 
                gru.update_pixel(i + offsetRow, j + offsetCol, board[i][j])
                sleep(gru.rate/1000.0)