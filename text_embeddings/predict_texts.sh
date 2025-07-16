#!/bin/bash

function processfile() {
fasttext predict-prob tweets.model1.bin $1 10 0.05 > $1.pred
}

export -f processfile

ls ../data/feature_files/*.texts | parallel -j 80 processfile {}


