from os import listdir
from os.path import isfile, join
import json
import re


def find_recursive(path):
    folders = [join(path, f) for f in listdir(path) if not isfile(join(path, f))]
    result = [join(path, f) for f in listdir(path) if isfile(join(path, f)) if f == "places.json"]

    for folder in folders:
        result.extend(find_recursive(join(path, folder)))

    return result


if __name__ == '__main__':
    path = "/mnt/erebor1/Daten/Tweetlocator/place_tagged/"
    files = find_recursive(path)

    places_dict = {}

    for file in files:
        print("Processing file {}".format(file))
        if not any(map(file.__contains__, ["2014", "2015", "2016", "2017", "2018", "2019", "2020"])):
            continue
        with open(file, "r") as input:
            for line in input.readlines():
                
                """
                line = line[1:-2].split(", {")
                count = int(line[0])

                obj = re.sub("'", "\"", line[1])
                obj = "{" + re.sub("\\'", "\"", obj)

                try:
                    obj = json.loads(obj)
                except:
                    try:
                        
                        if "2015" in file:
                            if obj[:3] == "{\"f":
                                tmp = obj.split("\"full_name\": ")
                                tmp = tmp[1].split(", \"url\": ")
                                full_name = tmp[0]
                                tmp = tmp[1].split(", \"country\": ")
                                infix1 = tmp[0]
                                tmp = tmp[1].split(", \"place_type\": ")
                                country = tmp[0]
                                tmp = tmp[1].split(", \"name\": ")
                                infix2 = tmp[0]
                                name = tmp[1]

                                name = re.sub("[\\\"\'\\\'\"}]", "", name)
                                full_name = re.sub("[\\\"\'\\\'\"]", "", full_name)
                                country = re.sub("[\\\"\'\\\'\"]", "", country)

                                obj = "{\"full_name\": \"" + full_name.replace("\\", "") + \
                                      "\", \"url\": " + infix1 + \
                                      ", \"country\": \"" + country.replace("\\", "") + \
                                      "\", \"place_type\": " + infix2 + \
                                      ", \"name\": \"" + name.replace("\\", "") + "\"}"
                            else:
                                tmp = obj.split("\"country\": ")
                                prefix = tmp[0]
                                tmp = tmp[1].split(", \"place_type\": ")
                                country = tmp[0]
                                tmp = tmp[1].split(", \"full_name\": ")
                                infix1 = tmp[0]
                                tmp = tmp[1].split(", \"attributes\": ")
                                full_name = tmp[0]
                                tmp = tmp[1].split(", \"name\": ")
                                infix2 = tmp[0]

                            print("Done: {}".format(obj))
                        else:
                        
                        tmp = obj.split("\"name\": ")
                        prefix = tmp[0]
                        tmp = tmp[1].split(", \"full_name\": ")
                        name = tmp[0]
                        tmp = tmp[1].split(", \"country_code\": ")
                        full_name = tmp[0]
                        tmp = tmp[1].split(", \"country\": ")
                        cc = tmp[0]
                        tmp = tmp[1].split(", \"contained_within\": ")
                        country = tmp[0]
                        postfix = tmp[1]

                        name = re.sub("[\\\"\'\\\'\"]", "", name)
                        full_name = re.sub("[\\\"\'\\\'\"]", "", full_name)
                        country = re.sub("[\\\"\'\\\'\"]", "", country)

                        obj = prefix + "\"name\": \"" + name.replace("\\", "") + \
                              "\", \"full_name\": \"" + full_name.replace("\\", "") + \
                              "\", \"country_code\": " + cc + \
                              ", \"country\": \"" + country.replace("\\", "") + \
                              "\", \"contained_within\": " + postfix

                        obj = obj.replace("\"bounding_box\": None", "\"bounding_box\": []")
                        obj = json.loads(obj.replace('\\xa0', ' '))

                        if obj["id"] not in places_dict:
                            places_dict[obj["id"]] = obj
                            places_dict[obj["id"]]["counts"] = count
                        else:
                            places_dict[obj["id"]]["counts"] += count
                    except:
                        #print("Except: {}".format(obj))
                        continue
                """
                pass
                #counts, d = line.split(";")
                d = json.loads(line)
                if d["id"] not in places_dict:
                    places_dict[d["id"]] = d
                    #places_dict[obj["id"]]["counts"] = count
                else:
                    places_dict[d["id"]]["counts"] += d["counts"]

    sorted_places = sorted([(v["counts"], v) for v in places_dict.values()], key=lambda n: n[0], reverse=True)

    with open("place_summary.json", "w") as out:
        for _, v in sorted_places:
            out.write(json.dumps(v) + "\n")

