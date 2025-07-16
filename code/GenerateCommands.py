from itertools import product
import numpy as np
from os import system

if __name__ == '__main__':
    base_path = "/mnt/erebor1/Daten/Tweetlocator/text_embeddings/"
    path_fasttext = base_path + "fasttext/"
    path_knn = base_path + "knn/"

    languages = ["de", "ru", "fr", "es", "pt", "ar", "zh", "ko", "en"]  # restrict on some languages for the prototype

    # 1. Step: Merge language dependant partial text- and language files
    with open(base_path + "merge_partial_files.sh", "w") as file:
        # divide into a clear folder structure
        file.write("mkdir fasttext\n")
        file.write("mkdir knn\n")
        file.write("mkdir backup\n")

        for lang in languages:
            # merge files depending on language tag
            file.write("cat {}*.texts > {}.texts.full\n".format(lang, lang))
            file.write("cat {}*.labels > {}.labels.full\n".format(lang, lang))

            # create one sub-folder for each language for each approach
            file.write("mkdir fasttext/{}\n".format(lang))
            file.write("mkdir knn/{}\n".format(lang))

            # copy files into corresponding folder
            file.write("cp {}.texts.full fasttext/{}/\n".format(lang, lang))
            file.write("cp {}.labels.full fasttext/{}/\n".format(lang, lang))
            file.write("cp {}.texts.full knn/{}/\n".format(lang, lang))
            file.write("cp {}.labels.full knn/{}/\n".format(lang, lang))

        # move remaining files into a backup folder
        file.write("mv *.texts backup/\n")
        file.write("mv *.labels backup/\n")
        file.write("mv *.full backup/\n")

    # 2. Create proper Training Files for (a) FastText and (b) kNN-Classifier

    # (a) Training File for FastText
    with open(path_fasttext + "create_training_files_fasttext.sh", "w") as file:
        for lang in languages:
            lang_folder = lang + "/" + lang
            # merge label file and text file into one
            file.write("paste -d ' ' {}.labels.full {}.texts.full > {}.combined.full\n" .format(lang_folder,
                                                                                                lang_folder,
                                                                                                lang_folder))
            # preceed each individual line with the __label__ identificator for fasttext
            file.write("sed -i -e 's/^/__label__/' {}.combined.full\n".format(lang_folder))

    # (b) Training File for kNN-Classifier
    with open(path_knn + "create_training_files_knn.sh", "w") as file:
        for lang in languages:
            lang_folder = lang + "/" + lang
            # merge label file and text file into one
            file.write("paste -d ' ' {}.labels.full {}.texts.full > {}.combined.full\n".format(lang_folder,
                                                                                               lang_folder,
                                                                                               lang_folder))
        for lang in languages:
            # python script for computing matrix of sentence vectors from <lang>.combined.full file
            file.write("python create_feature_matrices_knn.py -l {}\n".format(lang))

    # 3. Create Train/Test/Valid Splits for Cross-Evaluation for (a) FastText and (b) kNN-Classifier

    # (a) TTV Splits for FastText
    with open(path_fasttext + "train_test_valid_split_fasttext.sh", "w") as file:
        for lang in languages:
            lang_folder = lang + "/" + lang
            file.write("split -n l/10 {}.combined.full {}-splits.\n" .format(lang_folder, lang_folder))
            for i in range(10):
                # starts with i = 0 and chr(97) = 'a'
                train_str = "cat "
                for j in range(i+2, i+10):
                    train_str += "{}-splits.a{} ".format(lang_folder,
                                                         chr(97 + (j % 10)))
                file.write("{}> {}.train{}\n".format(train_str,
                                                     lang_folder,
                                                     i+1))  # train
                file.write("cp {}-splits.a{} {}.test{}\n".format(lang_folder,
                                                                 chr(97 + i),
                                                                 lang_folder,
                                                                 i+1))  # test
                file.write("cp {}-splits.a{} {}.valid{}\n".format(lang_folder,
                                                                  chr(97 + ((i + 1) % 10)),
                                                                  lang_folder,
                                                                  i+1))  # valid

    # (b) TTV Splits for kNN-Classifier

    # 4. Train Models: (a) FastText and (b) kNN-Classifier

    # (a) Training of FastText
    FASTTEXT = "/mnt/erebor1/Daten/ABI2/fasttext_pretrained/fastText/fasttext"
    PRET_VEC = "/mnt/erebor1/Daten/ABI2/FastText/"

    with open(path_fasttext + "start_training_fasttext.sh", "w") as file:
        for lang in languages:
            lang_folder = lang + "/" + lang
            for i in range(1, 11):
                file.write("{} supervised -input {}.train{} -output {}.model{} -pretrainedVectors {}wiki.{}.align.vec "
                           "-dim 300 -autotune-validation {}.valid{} -autotune-duration 43200 -thread 40\n".format(FASTTEXT,
                                                                                                       lang_folder,
                                                                                                        i,
                                                                                                        lang_folder,
                                                                                                        i,
                                                                                                        PRET_VEC,
                                                                                                        lang,
                                                                                                        lang_folder,
                                                                                                        i))


    # 5. Evaluation of (a) FastText and (b) kNN-Classifier

    # (a) Evaluation of FastText
    pre = "text_embeddings/fasttext/"

    for lang in languages:
        for i in range(1, 11):
            lang_folder = pre + lang + "/" + lang
            with open("{}.test{}.sh".format(lang_folder, i), "w") as file:
                for n, t in product(range(1, 4), np.arange(0., 0.61, 0.15)):
                    t = round(t, 2)
                    file.write("echo \"{} {}\" >> {}.eval{}; {} test {}.model{}.bin {}.test{} "
                               "{} {} >> {}.eval{}\n".format(n,
                                                                      t,
                                                                      lang,
                                                                      i,
                                                                      FASTTEXT,
                                                                      lang,
                                                                      i,
                                                                      lang,
                                                                      i,
                                                                      n,
                                                                      t,
                                                             lang,
                                                             i))
            system("chmod +x {}.test{}.sh".format(lang_folder, i))


    # 7. Make all scripts executable
    system("chmod +x {}".format(base_path + "merge_partial_files.sh"))
    system("chmod +x {}".format(path_fasttext + "create_training_files_fasttext.sh"))
    system("chmod +x {}".format(path_knn + "create_training_files_knn.sh"))
    system("chmod +x {}".format(path_fasttext + "train_test_valid_split_fasttext.sh"))
    system("chmod +x {}".format(path_fasttext + "start_training_fasttext.sh"))
    system("chmod +x {}".format(path_fasttext + "test_models_fasttext.sh"))

