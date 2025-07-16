split -n l/10 tweets.combined tweets-split.
cat tweets-split.ac tweets-split.ad tweets-split.ae tweets-split.af tweets-split.ag tweets-split.ah tweets-split.ai tweets-split.aj > tweets.train1
cp tweets-split.aa tweets.test1
cp tweets-split.ab tweets.valid1
cat tweets-split.ad tweets-split.ae tweets-split.af tweets-split.ag tweets-split.ah tweets-split.ai tweets-split.aj tweets-split.aa > tweets.train2
cp tweets-split.ab tweets.test2
cp tweets-split.ac tweets.valid2
cat tweets-split.ae tweets-split.af tweets-split.ag tweets-split.ah tweets-split.ai tweets-split.aj tweets-split.aa tweets-split.ab > tweets.train3
cp tweets-split.ac tweets.test3
cp tweets-split.ad tweets.valid3
cat tweets-split.af tweets-split.ag tweets-split.ah tweets-split.ai tweets-split.aj tweets-split.aa tweets-split.ab tweets-split.ac > tweets.train4
cp tweets-split.ad tweets.test4
cp tweets-split.ae tweets.valid4
cat tweets-split.ag tweets-split.ah tweets-split.ai tweets-split.aj tweets-split.aa tweets-split.ab tweets-split.ac tweets-split.ad > tweets.train5
cp tweets-split.ae tweets.test5
cp tweets-split.af tweets.valid5
cat tweets-split.ah tweets-split.ai tweets-split.aj tweets-split.aa tweets-split.ab tweets-split.ac tweets-split.ad tweets-split.ae > tweets.train6
cp tweets-split.af tweets.test6
cp tweets-split.ag tweets.valid6
cat tweets-split.ai tweets-split.aj tweets-split.aa tweets-split.ab tweets-split.ac tweets-split.ad tweets-split.ae tweets-split.af > tweets.train7
cp tweets-split.ag tweets.test7
cp tweets-split.ah tweets.valid7
cat tweets-split.aj tweets-split.aa tweets-split.ab tweets-split.ac tweets-split.ad tweets-split.ae tweets-split.af tweets-split.ag > tweets.train8
cp tweets-split.ah tweets.test8
cp tweets-split.ai tweets.valid8
cat tweets-split.aa tweets-split.ab tweets-split.ac tweets-split.ad tweets-split.ae tweets-split.af tweets-split.ag tweets-split.ah > tweets.train9
cp tweets-split.ai tweets.test9
cp tweets-split.aj tweets.valid9
cat tweets-split.ab tweets-split.ac tweets-split.ad tweets-split.ae tweets-split.af tweets-split.ag tweets-split.ah tweets-split.ai > tweets.train10
cp tweets-split.aj tweets.test10
cp tweets-split.aa tweets.valid10

