import time
start = time.time()
import threading
import spotipy
from spotipy import SpotifyOAuth
from collections import Counter
from pprint import pprint # noqa
import json


def format_song_name(song_name):
	song_name = song_name.split(" (")[0]
	song_name = song_name.split(" - ")[0]
	song_name = song_name.split(" / ")[0]
	song_name = song_name.split(" Remastered")[0]
	while song_name[-1] in [" ", "/", "\\"]:
		song_name = song_name[:-1]
	return song_name


def iterations(length, max_request=50):
	if length % max_request == 0:
		return int((length/50)-1)
	return int(str(length/50).split(".")[0])

def format_data(song_list):
	song_list = dict(song_list)["items"]
	for i in range(len(song_list)):
		added = song_list[i]["added_at"]
		song_list[i] = dict(song_list[i]["track"])
		song_list[i]["added_at"] = added
		song_list[i]["formatted_name"] = format_song_name(song_list[i]["name"])
	return song_list


def get_all_songs(spotify_client):
	with open("tracks.json") as data_file:
		data_file.write("")
	raw_data = dict(spotify_client.current_user_saved_tracks(
		limit=50, market="US", offset=0))
	playlist_len = int(raw_data["total"])
	data_list = format_data(raw_data)
	for i in range(iterations(playlist_len)):
		offset = i*50+51
		raw_data = dict(spotify_client.current_user_saved_tracks(
			limit=50, market="US", offset=offset))
		data_list.extend(format_data(raw_data))
	with open("tracks.json", "a") as data_file:
		json.dump({"data":data_list}, data_file)

def check_for_new_songs(spotify_client):
	with open("tracks.json") as data_file:
		data = dict(json.load(data_file))["data"]
	saved_song_ids = []
	for song in data:
		saved_song_ids.append(song["id"])
	saved_song_ids = list(set(saved_song_ids))


def get_genres(spotify_client):
	with open("genres.json", "w") as data_file:
		data_file.write("")
	with open("tracks.json") as data_file:
		data = dict(json.load(data_file))["data"]
	genre_list = []
	artist_ids = []
	for song in data:
		for artist in song["artists"]:
			artist_ids.append(artist["id"])
	artist_ids = list(set(artist_ids))
	for i in range(iterations(len(artist_ids))):
		batch_genres = dict(spotify_client.artists(artist_ids[i*50:(i+1)*50]))
		for artist in batch_genres["artists"]:
			genre_list.extend(artist["genres"])
	genre_dict = dict(Counter(genre_list))
	with open("genres.json", "w") as data_file:
		json.dump(genre_dict, data_file)


def podcasts(sp):
	with open("podcasts.json", "w") as data_file:
		data_file.write("")
	max_podcast_request = True
	podcasts = []
	n = 0
	while max_podcast_request:
		new_podcast_request = dict(sp.current_user_saved_episodes(offset = n))["items"]
		podcasts.extend(new_podcast_request)
		if len(new_podcast_request)<20:
			max_podcast_request = False
		n+=20
	with open("podcasts.json", "w") as podcast_file:
		json.dump(podcasts, podcast_file)


ID = "b95f6a39d55e4ee4bb0a1e7e64ccaf2b"
SECRET = "c14a3bf94565468fa97c2ebd76c73757"

spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=ID, client_secret=SECRET,
	redirect_uri="http://www.evantoomey.com/", scope="user-library-read"))


# threading.Thread(target=podcasts, args=(spotify_client,)).start()
get_all_songs(spotify_client)
# get_genres(spotify_client)


total_time = round(time.time()-start, 0)
if total_time<=60:
	print("Completed successfully in "+str(int(total_time % 60))+" seconds")
else:
	print("Completed successfully in "+str(int(total_time/60)) +
		" minutes and "+str(int(total_time % 60))+" seconds")
