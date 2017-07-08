#!/bin/bash

import datetime
import json
import requests
import time

from m2x.client import M2XClient

import config


def create_or_return_device(client, name):
    devs = client.devices(name=name)
    if len(devs) == 1:
        return devs[0]
    if len(devs) == 0:
        dev = client.create_device(
                name=name,
                description="{} on Twitch".format(name),
                visibility="public"
                )
        return dev
    raise Exception()

def create_or_return_stream(device, name):
    streams = device.streams()
    for stream in streams:
        if stream.name == name:
            return stream
    dev = device.create_stream(name)
    return dev





headers = {"Client-ID": config.client_id}
url = 'https://api.twitch.tv/kraken/games/top?limit=40&on_site=1'
r = requests.get(url, headers=headers)
collection_time = datetime.datetime.now()

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


client = M2XClient(key=config.master_key)


for game in games:
    name = game['name']
    device = create_or_return_device(client, name)
    for stat in ['popularity', 'viewers', 'channels', 'viewer_channel_ratio']:
        stream = create_or_return_stream(device, stat)
        stream.add_value(game[stat], collection_time)
        time.sleep(1)

