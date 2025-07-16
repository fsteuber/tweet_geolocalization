import bz2
import json
from os import listdir
from os.path import isfile, join
import io
from multiprocessing import Process, Queue
from datetime import datetime
import traceback
import re
import os

path = "/mnt/erebor1/Daten/Tweetlocator/"


def run(q_batches, q_results):
    global path
    batch = []
    batch_coordinate = []
    file_ = q_batches.get()
    file_size = 5 * 10 ** 5
    unique_places = {}
    
    while file_ is not None:
        with bz2.open(file_, "rb") as content:
            for line in content:
                try:
                    tweet = json.loads(line)

                    place = tweet.get("place")

                    if place is not None:
                        country = place.get("country")
                        country = re.sub("[\\\"\'\\\'\"]", "", country).replace("\\", "")

                        name = place.get("name")
                        name = re.sub("[\\\"\'\\\'\"]", "", name).replace("\\", "")

                        full_name = place.get("full_name")
                        full_name = re.sub("[\\\"\'\\\'\"]", "", full_name).replace("\\", "")

                        place["country"] = country
                        place["name"] = name
                        place["full_name"] = full_name

                        tweet["place"] = place


                        pid = place.get("id")
                        if pid not in unique_places:
                            unique_places[pid] = place
                            unique_places[pid]["counts"] = 1
                        else:
                            unique_places[pid]["counts"] += 1
                except:
                    print(traceback.format_exc())

        file_ = q_batches.get()

    # unique_places = sorted([(k, v[0], v[1]) for k, v in unique_places.items()], key=lambda n: n[0], reverse=True)
    q_results.put(unique_places)
    q_results.put(None)


if __name__ == '__main__':
    n_cores = 45
    base_path = "/mnt/erebor1/Daten/Tweetlocator/place_tagged/"
    
    for folder_name in range(2014, 2021):
        if folder_name != 2015:
            continue
        path = base_path + str(folder_name) + "/"
        files = [f for f in listdir(path) if isfile(join(path, f)) and f[-3:] == "bz2"]
        print("Processing folder {}: has {} elements.".format(path, len(files))) 
        
        q_batches = Queue(n_cores)
        q_results = Queue(n_cores)

        workers = [Process(target=run, args=(q_batches, q_results)) for _ in range(n_cores)]

        for w in workers:
            w.start()

        print("Starting workers and generating work batches.")

        for i, file in enumerate(files):
            if i % 50 == 0:
                print("Progress in folder {}: {}/{} ({}%)".format(path, i, len(files), round((100.0*i)/len(files), 2)))
            q_batches.put(path + file)

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
                for k, v in partial_result.items():
                    if k not in unique_places:
                        unique_places[k] = v
                    else:
                        unique_places[k]["counts"] += v["counts"]

        print("Writing place summary")
        unique_places = sorted([(v["counts"], v) for v in unique_places.values()], key=lambda n: n[0], reverse=True)
        
        with io.open("{}{}".format(path, "places.json"), "w") as out:
            for _, place_dict in unique_places:
                out.write(json.dumps(place_dict) + "\n")
