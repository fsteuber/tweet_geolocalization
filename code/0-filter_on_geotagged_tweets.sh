function processfile () {
xzcat $1 | jq -c "select(.coordinates != null or .place != null)" | bzip2 > $1.result
}

export -f processfile
ls data/raw_tweets/*.xz | parallel -j 40 processfile {}
mv data/raw_tweets/*.result data/geotagged/
