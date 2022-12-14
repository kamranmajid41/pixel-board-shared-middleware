import requests
from urllib.parse import urljoin


class PixelCache:
    def __init__(self, server_url, id):
        self.SERVER_URL = server_url
        self.id = id

        self.pixels = None
        self.etag = None

    def update(self):
        # Update pixel cache
        r = requests.get(urljoin(self.SERVER_URL, '/pixels'),
                         headers={"If-None-Match": self.etag},
                         json={"id": self.id})
        if r.status_code == 200:
            self.pixels = r.json()["pixels"]
            self.etag = r.headers.get('ETag')
