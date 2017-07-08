#!/bin/bash

import requests
import json
import datetime

import config

headers = {"Client-ID": config.client_id}
url = 'https://api.twitch.tv/kraken/games/top?limit=40&on_site=1'
r = requests.get(url, headers=headers)

resp = r.json()
games = []
for g in resp['top']:
    game = {}
    game['name'] = g['game']['name']
    game['popularity'] = g['game']['popularity']
    game['viewers'] = g['viewers']
    game['channels'] = g['channels']
    game['viewer_channel_ratio'] = g['viewers'] / g['channels']
    game['datetime'] = datetime.datetime.now().isoformat()
    games.append(game)

#for g in games:
#    for k,v in g.items():
#        print(k, ":", v)

if __name__ == "__main__":
    print(json.dumps(games))
