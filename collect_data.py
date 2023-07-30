import time
import threading
import spotipy
from spotipy import SpotifyOAuth
from collections import Counter
from pprint import pprint # noqa
import json
from dotenv import load_dotenv
import os

start = time.time()

load_dotenv()


def iterations(length, max_request=50):
	if length % max_request == 0:
		return int((length/50)-1)
	return int(str(length/50).split(".")[0])

def format_song_name(song_name):
	song_name = song_name.split(" (")[0]
	song_name = song_name.split(" - ")[0]
	song_name = song_name.split(" / ")[0]
	song_name = song_name.split(" Remastered")[0]
	while song_name[-1] in [" ", "/", "\\"]:
		song_name = song_name[:-1]
	return song_name

def format_artist(artist_dict):
	del artist_dict["external_urls"]
	del artist_dict["href"]
	del artist_dict["uri"]
	return artist_dict

def format_track(song):
	if "added_at" in song.keys():
		added = song["added_at"]
		song = dict(song["track"])
	else:
		added = None
	song["added_at"] = added
	song["formatted_name"] = format_song_name(song["name"])
	try:
		del song["album"]["available_markets"]
	except KeyError:
		pass
	del song["album"]["external_urls"]
	del song["album"]["href"]
	del song["album"]["images"]
	del song["album"]["uri"]
	song["album"]["artists"] = [format_artist(i) for i in song["album"]["artists"]]
	song["artists"] = [format_artist(i) for i in song["artists"]]
	try:
		song["available_markets"]
	except KeyError:
		pass
	del song["external_ids"]
	del song["external_urls"]
	del song["href"]
	del song["preview_url"]
	del song["uri"]
	song["artist_num"] = len(song["artists"])
	return song

def format_podcast(podcast):
	if "added_at" in podcast.keys():
		added = podcast["added_at"]
		podcast = dict(podcast["episode"])
	else:
		added = None
	podcast["added_at"] = added
	del podcast["audio_preview_url"]
	del podcast["external_urls"]
	del podcast["href"]
	del podcast["html_description"]
	del podcast["images"]
	del podcast["is_externally_hosted"]
	del podcast["language"]
	del podcast["languages"]
	del podcast["uri"]
	podcast["show"] = format_podcast_show(podcast["show"])
	return podcast

def format_podcast_show(show):
	del show["available_markets"]
	del show["copyrights"]
	del show["external_urls"]
	del show["href"]
	del show["html_description"]
	del show["images"]
	del show["is_externally_hosted"]
	del show["languages"]
	del show["uri"]
	return show

def get_all_songs(spotify_client):
	raw_data = dict(spotify_client.current_user_saved_tracks(
		limit=50, market="US", offset=0))
	playlist_len = int(raw_data["total"])
	data_list = [format_track(i) for i in raw_data["items"]]
	for i in range(iterations(playlist_len)):
		offset = i*50+51
		raw_data = dict(spotify_client.current_user_saved_tracks(
			limit=50, market="US", offset=offset))
		data_list.extend([format_track(i) for i in raw_data["items"]])
	if len(data_list) != playlist_len:
		pprint(len(data_list))
	with open("tracks.json", "w") as data_file:
		json.dump({"data":data_list}, data_file)


def get_genres(spotify_client):
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
	max_podcast_request = True
	podcasts = []
	n = 0
	while max_podcast_request:
		new_podcast_request = dict(sp.current_user_saved_episodes(offset = n))["items"]
		podcasts.extend([format_podcast(i) for i in new_podcast_request])
		if len(new_podcast_request)<20:
			max_podcast_request = False
		n+=20
	with open("podcasts.json", "w") as podcast_file:
		json.dump(podcasts, podcast_file)


client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret,
	redirect_uri="http://www.evantoomey.com/", scope="user-library-read"))


threading.Thread(target=podcasts, args=(spotify_client,)).start()
threading.Thread(target=get_genres, args=(spotify_client,)).start()
get_all_songs(spotify_client)


total_time = round(time.time()-start, 0)
if total_time<=60:
	print("Completed successfully in "+str(int(total_time % 60))+" seconds")
else:
	print("Completed successfully in "+str(int(total_time/60)) +
		" minutes and "+str(int(total_time % 60))+" seconds")
