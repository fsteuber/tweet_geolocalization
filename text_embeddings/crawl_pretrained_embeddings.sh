cat emb_locations.txt | while read f; do curl "${f} -O; done;
