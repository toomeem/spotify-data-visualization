from textwrap import wrap
from spotipy import SpotifyOAuth
import pandas as pd
from matplotlib import pyplot as plt
from collections import Counter
from pprint import pprint  # noqa
import time
import numpy as np

divider = "|"


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
        duration = int(round(int(item[2])/1000, 0))
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
    length = len(df)
    duplicate_indexes = df.loc[df.duplicated(), :]
    df.drop_duplicates(inplace=True)
    if length > len(df):
        print("There were "+str(length-len(df))+" copies")
        pprint(duplicate_indexes)
    return df


def duration_graph_organization(df, bars_per_graph):
    df.sort_values(by=["duration"], ascending=True, inplace=True)
    avg_track = int((round(df["duration"].sum()/len(df["duration"]), 1))/60)
    names = []
    durations = []
    names.append("Average")
    durations.append(avg_track)
    for i in df.tail(bars_per_graph)["duration"]:
        durations.append(i/60)
    for i in df.tail(bars_per_graph)["formatted_name"]:
        names.append(i)
    return names, durations, len(df), max(df["duration"]), min(df["duration"])


def get_artist_info(df):
    artist_dict = {}
    for i in df["artists"]:
        i = eval(i)
        for artist in i:
            if artist in artist_dict.keys():
                artist_dict[artist] += 1
            else:
                artist_dict.update({artist: 1})
    artist_dict = dict(sorted(artist_dict.items(), key=lambda item: item[1], reverse=True))
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
    # top = sorted(artist_dict, key=artist_dict.get, reverse=True)[:30]
    # for i in top:
    #     print(f"{i}:{artist_dict[i]}")
    for key in use_nums:
        for artist in artist_dict:
            if artist_dict[artist] == key:
                most_popular.append(artist)
                uses.append(key)
        if len(most_popular) >= artists_per_graph:
            break
    """       show average
    # most_popular.append("Average")
    # artist_use_sum = 0
    # for key, val in popularity.items():
    # 	artist_use_sum+=key*val
    # uses.append(artist_use_sum/len(artist_dict))
    """
    return most_popular, uses


def get_explicits(data):
    explicits = {"Explicit": 0, "Clean": 0, "Unknown": 0}
    for item in data["explicit"]:
        if item == "True":
            explicits["Explicit"] += 1
        if item == "False":
            explicits["Clean"] += 1
        else:
            explicits["Unknown"] += 1
    return dict(sorted(explicits.items(), key=lambda item: item[1], reverse=True))


def get_genres():
    with open(r"C:\\Users\etoom\python files\spotipy\genres.txt") as data_file:
        data = eval(data_file.read())
    return data


def genre_data_organization(genres_per_graph):
    data = get_genres()
    # pprint(sorted(data.items(),key=lambda item: item[1], reverse=True))
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
    names = data["formatted_name"]
    copies = list(set([i for i in names if list(names).count(i) > 1]))
    return len(copies)


def release_date_data(data):
    yrs = data["release_date"]
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
    data = []
    with open(r"C:\\Users\etoom\python files\spotipy\podcast_data.txt") as data_file:
        raw_data = data_file.readlines()
    for i in raw_data:
        i = i.split("/")
        data.append({
            "name": i[2][:-1],
            "duration": int(i[1]),
            "show": i[0]
        })
    return data


def get_podcast_duration(data):
    total = 0
    for i in data:
        total += i["duration"]
    return total


def get_show_frequency(data):
    shows = []
    show_dict = {}
    for i in data:
        shows.append(i["show"])
    for i in shows:
        show_dict.update({i: shows.count(i)})
    return dict(sorted(show_dict.items(), key=lambda item: item[1], reverse=True))


def get_show_durations(data):
    show_dict = {}
    for i in data:
        show = i["show"]
        duration = int(i["duration"]/60)
        if show in show_dict.keys():
            show_dict[show] = show_dict[show] + duration
        else:
            show_dict.update({show: duration})
    return dict(sorted(show_dict.items(), key=lambda item: item[1], reverse=True))


data = read_data(divider)
fig = plt.figure()

artist_dict, artist_num = get_artist_info(data)
popular_artists, artist_uses = find_popular(artist_dict, 20)
duration_names, durations, track_num, longest, shortest = duration_graph_organization(data, 20)
all_durations = data["duration"]
hours = float(round((all_durations.sum()/60)/60, 1))
avg_track = int(round(all_durations.sum()/len(all_durations), 1))
explicits = get_explicits(data)
popular_genres, genres_uses, genre_num = genre_data_organization(20)
cover_num = covers(data)
release_decades, release_nums, release_range = release_date_data(data)
podcast_data = get_podcast_data()
podcast_hours = get_podcast_duration(podcast_data)
podcast_hours = float(round((podcast_hours/60)/60, 1))
shows = get_show_frequency(podcast_data)
show_duration_dict = get_show_durations(podcast_data)

for i in range(10):
    print("")
print(f"Your playlist is {track_num} songs long and it is {hours} hours long.")
print(f"It spans {release_range} years of music.")
print(
    f"Your playlist consisted of {artist_num} artists that represented {genre_num} different genres.")
print("The songs were an average of "+str(avg_track//60) +
      " minutes and "+str(avg_track % 60)+" seconds long.")
print("The longest song was "+str(longest//60) +
      " minutes and "+str(longest % 60)+" seconds long.")
print("The shortest song was "+str(shortest//60) +
      " minute and "+str(shortest % 60)+" seconds long.")
print(f"There were around {cover_num} cover songs.")
print("")
print(f"You have {len(podcast_data)} podcast episodes saved that are in total {podcast_hours} hours long.")
print(f"Those episodes are from {len(shows.keys())} different shows.")

for i in range(2):
    print("")

show = True
if True:
    plt.yticks(fontsize=8)
    plt.title("Most Liked Songs")
    plt.xlabel("Number of Songs in Playlist")
    plt.barh(popular_artists[::-1], artist_uses[::-1])
elif True:
    plt.yticks(fontsize=8)
    plt.title("Longest Songs")
    plt.xlabel("Song Duration (minutes)")
    plt.barh(duration_names, durations)
elif True:
    plt.yticks(fontsize=8)
    plt.title("Most Popular Genres")
    plt.xlabel("Number of Liked Genres")
    plt.barh(popular_genres[::-1], genres_uses[::-1])
elif True:
    plt.title("Number of Explicit Songs(Aproximate)", pad=40)
    plt.pie(x=explicits.values(), labels=explicits.keys(), radius=1.3,
        autopct=lambda pct: auto_pct(pct, list(explicits.values())),)
elif True:
    plt.title("Number of Covers(Aproximate)")
    plt.pie(x=[len(data)-cover_num, cover_num], labels=["Originals", "Covers"], pctdistance=.85,
        autopct=lambda pct: auto_pct(pct, [len(data)-cover_num, cover_num]))
elif True:
    plt.title("Songs from Each Decade", pad=40, fontdict={'fontsize': 20})
    plt.pie(x=release_nums, labels=release_decades, autopct=lambda pct: auto_pct(pct, release_nums),
        pctdistance=.85, labeldistance=1.05)
elif True:
    plt.title(f"Number of Episodes (total {sum(shows.values())})")
    plt.pie(x=shows.values(), labels=shows.keys(),
        autopct=lambda pct: auto_pct(pct, list(shows.values())))
elif True:
    plt.title("Runtime (minutes)")
    plt.pie(x=show_duration_dict.values(), labels=show_duration_dict.keys(),
        autopct=lambda pct: auto_pct(pct, list(show_duration_dict.values())))
else:
    show = False
if show:
    plt.show()
