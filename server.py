import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.escape import json_encode

import requests
import random

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

API_KEY = ''
CHANNEL_INFO_URL_TEMPLATE = 'https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={}&key={}'
PLAYLIST_URL_TEMPLATE = 'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={}&key={}'
YOUTUBE_BASE_URL = 'https://www.youtube.com/watch?'

class RandomHandler(tornado.web.RequestHandler):
    def get(self, channel_id):
        chan_url = CHANNEL_INFO_URL_TEMPLATE.format(channel_id, API_KEY)
        r = requests.get(chan_url)
        json_data = r.json()

        uploads = None
        if json_data.get('items'):
            uploads = json_data['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        if uploads:
            playlist_url = PLAYLIST_URL_TEMPLATE.format(uploads, API_KEY)
            r = requests.get(playlist_url)
            json_data = r.json()

        if json_data.get('items'):
            r_item = random.choice(json_data['items'])
            video_id = r_item['snippet']['resourceId']['videoId']

            thumbnail_url = r_item['snippet']['thumbnails']['high']['url']
            video_url = YOUTUBE_BASE_URL + video_id

            json_dict = {
                'video_url': video_url,
                'thumbnail_url': thumbnail_url
            }

            json_resp = json_encode(json_dict)
            self.set_header('Content-Type', 'application/javascript')
            self.write(json_resp)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r'/api/(\w+)/random', RandomHandler)
        ]
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
