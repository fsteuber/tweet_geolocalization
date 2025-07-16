import bz2
import json
from os import listdir
from os.path import isfile, join
import io
from multiprocessing import Process, Queue
from datetime import datetime
import traceback

path = "/mnt/erebor1/Daten/Tweetlocator/"


def run(q_batches, q_results):
    global path
    batch = []
    batch_coordinate = []
    file = q_batches.get()
    file_size = 5 * 10 ** 5
    unique_places = {}
    
    try:
        while file is not None:
            with bz2.open(file, "rb") as content:
                for line in content:
                    tweet = json.loads(line)

                    place = tweet.get("place")
                    if place is not None:
                        pid = place.get("id")
                        if pid not in unique_places:
                            unique_places[pid] = [1, place]
                        else:
                            unique_places[pid][0] += 1

                    batch.append(tweet)
                    geo = tweet.get("geo")

                    if geo is not None:
                        batch_coordinate.append(tweet)

                    if len(batch) == file_size:
                        # format: place_YY-MM-DD_HH:MM:SS.json.bz2
                        file_name = datetime.strptime(batch[0].get("created_at"), "%a %b %d %H:%M:%S %z %Y").strftime(
                            "place_%Y-%m-%d_%H:%M:%S.json.bz2")
                        with bz2.open(path + file_name, "wb") as out:
                            out.write("\n".join([json.dumps(x) for x in batch]).encode())
                        batch = []

                    if len(batch_coordinate) == file_size:
                        # format: geo_YY-MM-DD_HH:MM:SS.json.bz2
                        file_name = datetime.strptime(batch_coordinate[0].get("created_at"), "%a %b %d %H:%M:%S %z %Y").strftime(
                            "geo_%Y-%m-%d_%H:%M:%S.json.bz2")
                        with bz2.open(path + file_name, "wb") as out:
                            out.write("\n".join([json.dumps(x) for x in batch_coordinate]).encode())
                        batch_coordinate = []

            file = q_batches.get()

        if len(batch) != 0:
            file_name = datetime.strptime(batch[0].get("created_at"), "%a %b %d %H:%M:%S %z %Y").strftime("place_%Y-%m-%d_%H:%M:%S.json.bz2")
            with bz2.open(path + file_name, "wb") as out:
                out.write("\n".join([json.dumps(x) for x in batch]).encode())

        if len(batch_coordinate) != 0:
            file_name = datetime.strptime(batch_coordinate[0].get("created_at"), "%a %b %d %H:%M:%S %z %Y").strftime("geo_%Y-%m-%d_%H:%M:%S.json.bz2")
            with bz2.open(path + file_name, "wb") as out:
                out.write("\n".join([json.dumps(x) for x in batch_coordinate]).encode())

        unique_places = sorted([(k, v[0], v[1]) for k, v in unique_places.items()], key=lambda n: n[0], reverse=True)

        q_results.put(unique_places)
        q_results.put(None)
    except:
        print(traceback.format_exec())


if __name__ == '__main__':
    n_cores = 40
    base_path = "/mnt/erebor1/Daten/Tweetlocator/geotagged/"
    
    for folder_name in range(2008, 2021):
        path = base_path + str(folder_name) + "/"
        files = [f for f in listdir(path) if isfile(join(path, f)) and f[-6:] == "result"]
        print("Processing folder {}: has {} elements.".format(path, len(files))) 
        
        q_batches = Queue(100)
        q_results = Queue(n_cores)

        workers = [Process(target=run, args=(q_batches, q_results)) for _ in range(n_cores)]

        for w in workers:
            w.start()

        print("Starting workers and generating work batches.")
        for i, file in enumerate(files):
            if i % 50 == 0:
                print("Progress in folder {}: {}/{} ({}%)".format(path, i, files, round((100.0*i)/len(files), 2)))
            q_batches.put(join(path, file))

        for _ in range(n_cores):
            q_batches.put(None)

        # wait for result
        unique_places = {}
        remaining_nones = n_cores

        print("Collecting partial results.")
        while remaining_nones > 0:
            partial_result = q_results.get()
            if partial_result is None:
                remaining_nones -= 1
                print("{} results from workers remaining".format(remaining_nones))
            else:
                for element in partial_result:
                    k, c, v = element
                    if k not in unique_places:
                        unique_places[k] = [c, v]
                    else:
                        unique_places[k][0] += c

        print("Writing place summary")
        unique_places = sorted([(v[0], v[1]) for v in unique_places.values()], key=lambda n: n[0], reverse=True)

        with io.open("{}{}".format(path, "places.json"), "w", encoding="utf-8") as out:
            for elt in unique_places:
                out.write(str(elt) + "\n")


    # TODO lookup crawler geotagging starten
    # TODO ggf. cleanup auf server starten

