import spotipy
from spotipy import SpotifyOAuth
import random
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from pprint import pprint  # noqa
import time
import numpy as np

divider = "|"
start = time.time()


def format_name(name):
    name = name.split(" (")[0]
    name = name.split(" - ")[0]
    name = name.split(" / ")[0]
    while name[-1] == " ":
        name = name[:-1]
    return name


def iterations(length, max_request=50):
    if length % max_request == 0:
        return int((length/50)-1)
    return int(str(length/50).split(".")[0])


def format_data(track):
    raw_name = track["name"]
    if raw_name == "Stop":
        print("Program Force Stopped")
        return "error"
    artists = {artist["name"]: artist["id"] for artist in track["artists"]}
    duration = track["duration_ms"]
    track_id = track["id"]
    explicit = track["explicit"]
    formatted_name = format_name(raw_name)
    release_date = int(dict(track["album"])["release_date"][:4])
    if "dict" not in str(type(track)):
        return "error"
    track_data = "{}|{}|{}|{}|{}|{}|{}\n".format(
        raw_name, artists, duration, track_id, explicit, formatted_name, release_date)
    return track_data


def write_track(track):
    with open(r"C:\\Users\etoom\python files\spotipy\track_data.txt", "a") as data_file:
        data_file.write(track)


def get_all_songs(sp):
    with open(r"C:\\Users\etoom\python files\spotipy\track_data.txt", "w") as data_file:  # noqa
        pass
    raw_data = dict(sp.current_user_saved_tracks(
        limit=50, market="US", offset=0))
    playlist_len = int(raw_data["total"])
    record_data(raw_data)
    for i in range(iterations(playlist_len)):
        offset = i*50+51
        raw_data = dict(sp.current_user_saved_tracks(
            limit=50, market="US", offset=offset))
        if record_data(raw_data) == "error":
            return


def record_data(raw):
    raw = [dict(dict(i)["track"]) for i in raw["items"]]
    for i in raw:
        data = format_data(dict(i))
        if data == "error":
            return "error"
        write_track(data)
    return


def get_genres(sp, divider):
    with open(r"C:\\Users\etoom\python files\spotipy\track_data.txt") as data_file:
        data = data_file.readlines()
    data = [list(eval(track.split(divider)[1]).values()) for track in data]
    artist_ids = []
    for id in data:
        if "list" in str(type(id)):
            for i in id:
                artist_ids.append(i)
        else:
            artist_ids.append(id)
    artist_ids = list(set(artist_ids))
    genres = []
    for i in range(iterations(len(artist_ids))):
        batch_genres = dict(sp.artists(artist_ids[i*50:(i+1)*50]))
        for artist in batch_genres["artists"]:
            genres.extend(artist["genres"])
    genre_dict = str(dict(Counter(genres)))
    with open(r"C:\\Users\etoom\python files\spotipy\genres.txt", "w") as data_file:
        data_file.writelines(genre_dict)


def read_data(divider):
    with open(r"C:\\Users\etoom\python files\spotipy\track_data.txt") as data_file:
        raw_data = data_file.readlines()
    df = pd.DataFrame({
        "raw_name": [],
        "duration": [],
        "artists": [],
        "ID": [],
        "explicit": [],
        "formatted_name": [],
        "release_date": []
    })
    for i in raw_data:
        if i.count(divider) != 6:
            print("Execution Failed")
            print("Change Divider")
            print(f" Divider count: {i.count(divider)}")
            print(i)
            return
        item = i.split(divider)
        raw_name = item[0]
        artists = item[1]
        duration = int(int(item[2])/1000)
        ID = item[3]
        explicit = item[4]
        formatted_name = item[5]
        release_date = int(item[6][:-1])
        df.loc[len(df.index)] = ({
            "raw_name": raw_name,
            "duration": duration,
            "artists": artists,
            "ID": ID,
            "explicit": explicit,
            "formatted_name": formatted_name,
            "release_date": release_date
        })
    # length = len(df)
    # df.drop_duplicates(inplace=True)
    # if length > len(df):
    #     print("There were "+str(length-len(df))+" copies")
    return df


def remaster(sp, data):
    length = len(data)
    with open(r"C:\\Users\etoom\python files\spotipy\track_data.txt") as data_file:
        raw_data = data_file.readlines()

    def release_date(i): return int(dict(i["album"])["release_date"][:4])
    for i in range(len(data)):
        name = data["raw_name"][i].lower()
        artist = list(eval(data["artists"][i]).keys())[0].lower()
        q = f"artist:'{artist}' track:'{name}'"
        results = list(
            dict(sp.search(q=q.encode(), type="track", market="US")["tracks"])["items"])
        if results == []:
            continue
        first_release = release_date(results[0])
        for j in results:
            j = dict(j)
            if release_date(j) < first_release:
                first_release = release_date(j)
        match = int(len(data["raw_name"][i])*.5)
        if data["raw_name"][i][match] != raw_data[i][match] or first_release < 1920:
            print(data["raw_name"][i][match], raw_data[i][match])
            continue
        raw_data[i] = raw_data[i][:-5]+f"{first_release}\n"
        if "str" not in str(type(raw_data[i])):
            print(str(type(raw_data[i]))+" oops")
            print(raw_data[i])
            return
        print(str(round((i/length)*100, 1))+"%")
    with open(r"C:\\Users\etoom\python files\spotipy\track_data.txt", "w") as data_file:
        data_file.writelines(raw_data)


def podcasts(sp):
    podcast_strings=[]
    raw_podcasts = dict(sp.current_user_saved_episodes())["items"]
    name=""
    show=""
    duration=""
    podcast={}
    for i in raw_podcasts:
        podcast = dict(i["episode"])
        name=podcast["name"]
        show=dict(podcast["show"])["name"]
        duration=int(podcast["duration_ms"]/1000)
        podcast_strings.append(f"{show}/{duration}/{name}\n")
    with open(r"C:\\Users\etoom\python files\spotipy\podcast_data.txt", "w") as podcast_file:
        podcast_file.writelines(podcast_strings)


ID = "b95f6a39d55e4ee4bb0a1e7e64ccaf2b"
SECRET = "844a8b6252b84c9f9790206b5eb726b4"
divider = "|"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=ID, client_secret=SECRET,
    redirect_uri="http://www.evantoomey.com/", scope="user-library-read"))


for i in range(10):
    print(" ")

print("Would you like to get accurate release dates for of all your liked songs?(y/n)")
print("It should take 3-5 mins.")
get_dates = str(input()) == "y"
if get_dates:
    remaster(sp, read_data(divider))
get_genres(sp, divider)
podcasts(sp)
get_all_songs(sp)

total_time = round(time.time()-start, 1)
if total_time<=60:
    print("Completed successfully in "+str(int(total_time % 60))+" seconds")
else:
    print("Completed successfully in "+str(int(total_time/60)) +
          " minutes and "+str(int(total_time % 60))+" seconds")
