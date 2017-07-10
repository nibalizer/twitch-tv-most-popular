#!/bin/bash

import datetime
import json
import requests
import time

from m2x.client import M2XClient

import config


def get_total_devices(client):
    # client.devices() only returns the first page
    # this is pulled from examples/iterate_over_devices.py in m2x-python
    side_effect = client.devices()
    total_devices = client.last_response.json['total']
    if total_devices < config.max_devices:
        return False
    else:
        return True


def get_device(client, name):
    devs = client.devices(name=name)
    if len(devs) == 1:
        return devs[0]
    if len(devs) == 0:
        return None
    if len(devs) > 1:
        # This happens sometimes!?
        # (Pdb) ds = client.devices(name="ARK")
        # (Pdb) ds
        # [<m2x.v2.devices.Device object at 0x7fee4086c6a0>, <m2x.v2.devices.Device object at 0x7fee4086cba8>]
        # (Pdb) ds[0].name
        # 'Darkest Dungeon'
        # (Pdb) ds[1].name
        # 'Dark Souls II: Scholar of the First Sin'
        # (Pdb) ds[1]
        # <m2x.v2.devices.Device object at 0x7fee4086cba8>
        # Workaround: get the first one, accept potential errors this causes
        return devs[0]


def create_device(client, name):
    dev = client.create_device(
            name=name,
            description="{} on Twitch".format(name),
            visibility="public"
            )
    return dev


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
    at_max_devices = get_total_devices(client)
    name = game['name']
    print("Processing {0}".format(name))
    device = get_device(client, name)
    if device is None and at_max_devices == False:
        device = create_device(client, name)
        for stat in ['popularity', 'viewers', 'channels', 'viewer_channel_ratio']:
            stream = create_or_return_stream(device, stat)
            stream.add_value(game[stat], collection_time)
            time.sleep(config.delay)
