from matplotlib import pyplot as plt
from pprint import pprint
import numpy as np
import json
import os
import sys
import time
import random

def read_spotify_data():
	with open("tracks.json") as data_file:
		data = list(json.load(data_file)["data"])
	return data, len(data)

def duration_graph_organization(data, bars_per_graph):
	maxes, durations = [], []
	shortest = {data[0]["duration_ms"]: data[0]["formatted_name"]}
	for i in data:
		duration = i["duration_ms"]
		if len(maxes) < bars_per_graph:
			maxes.append({duration: i["formatted_name"]})
		maxes_min = min([list(i.keys())[0] for i in maxes])
		if duration > maxes_min:
			for j in range(len(maxes)):
				if list(maxes[j].keys())[0] == maxes_min:
					maxes[j] = {duration: i["formatted_name"]}
					break
		if duration < list(shortest.keys())[0]:
			shortest = {duration: i["formatted_name"]}
		durations.append(duration)
	avg_track = round(np.mean(a=durations)/1000)
	maxes.sort(key=lambda x: list(x.keys())[0], reverse=True)
	longest = round(int(list(maxes[0].keys())[0])/1000)
	shortest = round(int(list(shortest.keys())[0])/1000)
	return maxes, avg_track, longest, shortest

def get_artist_info(data):
	artist_dict = {}
	for i in data:
		for artist in i["artists"]:
			if artist["name"] in artist_dict.keys():
				artist_dict[artist["name"]] += 1
			else:
				artist_dict.update({artist["name"]: 1})
	return artist_dict, len(artist_dict)

def find_popular(artist_dict, artists_per_graph):
	values_list = list(artist_dict.values())
	popularity = {}
	most_popular = []
	uses = []
	for i in values_list:
		if i not in popularity.keys():
			popularity.update({i: 1})
		else:
			popularity[i] += 1
	use_nums = sorted(popularity.keys(), reverse=True)
	for key in use_nums:
		for artist in artist_dict:
			if artist_dict[artist] == key:
				most_popular.append(artist)
				uses.append(key)
			if len(most_popular) >= artists_per_graph:
				break
	return most_popular, uses

def get_explicits(data):
	explicits = {"Explicit": 0, "Clean": 0, "Unknown": 0}
	for item in data:
		if str(item["explicit"]) == "True":
			explicits["Explicit"] += 1
		elif str(item["explicit"]) == "False":
			explicits["Clean"] += 1
		else:
			explicits["Unknown"] += 1
	if explicits["Unknown"] == 0:
		del explicits["Unknown"]
	return explicits

def genre_data_organization(genres_per_graph):
	with open("genres.json") as data_file:
		data = json.load(data_file)
	values_list = list(data.values())
	popularity = {}
	most_popular = []
	uses = []
	for i in values_list:
		if i not in popularity.keys():
			popularity.update({i: 1})
		else:
			popularity[i] += 1
	use_nums = sorted(popularity.keys(), reverse=True)
	for key in use_nums:
		for artist in data:
			if data[artist] == key:
				most_popular.append(artist.capitalize())
				uses.append(key)
		if len(most_popular) >= genres_per_graph:
			break
	return most_popular, uses, len(data)

def covers(data):
	names = [i["formatted_name"] for i in data]
	copies = list(set([i for i in names if list(names).count(i) > 1]))
	return len(copies)

def release_date_data(data):
	yrs = [int(i["album"]["release_date"][:4]) for i in data]
	first = min(yrs)
	last = max(yrs)
	def to_decade(i): return int(str(i)[:-1]+"0")
	yrs = sorted(list(map(to_decade, yrs)))
	popularity = {}
	for i in yrs:
		if i not in popularity.keys():
			popularity.update({i: 1})
		else:
			popularity[i] += 1
	popularity = dict(sorted(popularity.items(), key=lambda item: item[0]))
	return list(popularity.keys()), list(popularity.values()), last-first

def auto_pct(pct, allvalues):
	absolute = int(pct / 100.*np.sum(allvalues))
	return "{:.1f}%\n({:d})".format(pct, absolute)

def get_podcast_data():
	with open("podcasts.json") as data_file:
		data = json.load(data_file)
	return data

def get_podcast_duration(data):
	total = 0
	for i in data:
		total += i["duration_ms"]
	return total

def get_show_frequency(data):
	shows = []
	show_dict = {}
	for i in data:
		shows.append(i["show"]["name"])
	for i in shows:
		show_dict.update({i: shows.count(i)})
	return show_dict

def get_show_durations(data):
	show_dict = {}
	for i in data:
		show_name = i["show"]["name"]
		duration = int(i["duration_ms"]/(60*1000))
		if show_name in show_dict.keys():
			show_dict[show_name] = show_dict[show_name] + duration
		else:
			show_dict.update({show_name: duration})
	return show_dict


data, track_num = read_spotify_data()
artist_dict, artist_num = get_artist_info(data)
popular_artists, artist_uses = find_popular(artist_dict, 20)
durations, avg_track_len, longest, shortest = duration_graph_organization(data, 20)
duration_names = [list(i.values())[0] for i in durations][::-1]
duration_values = [list(i.keys())[0] for i in durations][::-1]
all_durations = sum([i["duration_ms"] for i in data])
hours = float(round((all_durations/(60*1000))/60, 1))
explicits = get_explicits(data)
popular_genres, genres_uses, genre_num = genre_data_organization(20)
cover_num = covers(data)
release_decades, release_nums, release_range = release_date_data(data)
podcast_data = get_podcast_data()
podcast_hours = get_podcast_duration(podcast_data)
podcast_hours = float(round((podcast_hours/(60*1000))/60, 1))
shows = get_show_frequency(podcast_data)
show_duration_dict = get_show_durations(podcast_data)

for i in range(10):
		print("")
print(f"Your playlist is {track_num} songs long and it is {hours} hours long.")
print(f"It spans {release_range} years of music.")
print(
		f"Your playlist consisted of {artist_num} artists that represented {genre_num} different genres.")
print("The songs were an average of "+str(int(avg_track_len//60)) +
      " minutes and "+str(int(avg_track_len % 60))+" seconds long.")
print("The longest song was "+str(longest//60) +
			" minutes and "+str(longest % 60)+" seconds long.")
print("The shortest song was "+str(shortest//60) +
			" minute and "+str(shortest % 60)+" seconds long.")
print(f"There were around {cover_num} cover songs.")
print("")
print(f"You have {len(podcast_data)} podcast episodes saved that are in total {podcast_hours} hours long.")
print(f"Those episodes are from {len(shows.keys())} different shows.")

print("")

show_graph = True
if True:
	plt.yticks(fontsize=8)
	plt.title("Most Liked Songs")
	plt.xlabel("Number of Liked Songs")
	plt.barh(popular_artists[::-1], artist_uses[::-1])
elif True:
	plt.yticks(fontsize=8)
	plt.title("Longest Songs")
	plt.xlabel("Song Duration (minutes)")
	plt.barh(duration_names, duration_values)
elif True:
	plt.yticks(fontsize=8)
	plt.title("Most Popular Genres")
	plt.xlabel("Number of Liked Genres")
	plt.barh(popular_genres[::-1], genres_uses[::-1])
elif True:
	plt.title("Number of Explicit Songs(Aproximate)", pad=40)
	plt.pie(x=explicits.values(), labels=list(explicits.keys()), radius=1.3,
			autopct=lambda pct: auto_pct(pct, list(explicits.values())),)
elif True:
	plt.title("Number of Covers(Aproximate)")
	plt.pie(x=[len(data)-cover_num, cover_num], labels=["Original Songs", "Covers"], pctdistance=.85,
			autopct=lambda pct: auto_pct(pct, [len(data)-cover_num, cover_num]))
elif True:
	plt.title("Songs from Each Decade", pad=40, fontdict={'fontsize': 20})
	plt.pie(x=release_nums, labels=release_decades, autopct=lambda pct: auto_pct(pct, release_nums),
			pctdistance=.85, labeldistance=1.05)
elif True:
	plt.title(f"Number of Episodes (total {sum(shows.values())})")
	plt.pie(x=shows.values(), labels=list(shows.keys()),
			autopct=lambda pct: auto_pct(pct, list(shows.values())))
elif True:
	plt.title("Runtime (minutes)")
	plt.pie(x=show_duration_dict.values(), labels=list(show_duration_dict.keys()),
			autopct=lambda pct: auto_pct(pct, list(show_duration_dict.values())))
else:
	show_graph = False
if show_graph:
	plt.show()
