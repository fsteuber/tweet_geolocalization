from os import listdir
from os.path import isfile, join
import json
import regex as re
import bz2
import pickle
import numpy as np
import time
from sklearn.cluster import KMeans

train_data = None
base_path = "/mnt/erebor1/Daten/Tweetlocator/"


def find_recursive(path):
    folders = [join(path, f) for f in listdir(path) if not isfile(join(path, f))]
    result = [join(path, f) for f in listdir(path) if isfile(join(path, f)) if f[-3:] == "bz2"]

    for folder in folders:
        result.extend(find_recursive(join(path, folder)))

    return result


def centroid(polygon):
    return polygon[0].mean(axis=0)


def check_dump(dump=False, N=100000):
    global train_data
    global base_path
    ts = int(time.time())
    for k, v in train_data.items():
        if len(v) > N or dump:
            with open(base_path + "{}-{}.texts".format(k, ts), "w") as train_file:
                with open(base_path + "{}-{}.labels".format(k, ts), "w") as label_file:
                    for text, label in v:
                        train_file.write("{}\n".format(text))
                        label_file.write("{}\n".format(label))
            train_data[k] = []


if __name__ == '__main__':
    path = base_path + "place_tagged/2020/"
    files = find_recursive(path)
    place_model = pickle.load(open(base_path + "{}.cluster".format(150), "rb"))

    languages = ["en", "de", "ru", "fr", "es", "pt", "ar", "zh", "ko"]  # restrict on some languages for the prototype

    train_data = {l: [] for l in languages}  # one array for each language

    for file_path in files:
        with bz2.open(file_path, "r") as file:
            for tweet in file.readlines():

                tweet = json.loads(tweet)
                lang = tweet.get("lang")

                if lang not in languages:
                    continue

                place = tweet.get("place")
                if place is None:
                    continue
                try:
                    place = place.get("bounding_box").get("coordinates")
                except:
                    continue

                place = centroid(np.asarray(place)).reshape(1, -1)
                target_label = place_model.predict(place)[0]

                text = re.sub(r'[\s]+', ' ',  # remove multiple space characters
                          re.sub(r'\b\w{1,2}\b', '',  # remove tokens with less than 3 characters
                          re.sub(r'[^\p{Arabic}\p{Greek}\p{Cyrillic}\p{Latin}\p{Han}\p{Hangul} ]', '',  # some dirty multilingual regex ;-)
                          re.sub(r'[\n\t]', ' ',  # remove linebreaks and tabs
                          re.sub(r'@\w+', '',  # remove @ annotations
                          re.sub(r'https?:\/\/.*[\r\n]*', '',
                          tweet.get("text"))))))).strip()  # remove urls

                if len(text.split(" ")) == 0:
                    continue

                train_data[lang].append((text, target_label))
        check_dump()
    check_dump(dump=True)

