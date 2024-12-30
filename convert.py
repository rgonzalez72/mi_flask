#! /usr/bin/env python3

import sys
import json

with open(sys.argv[1]) as fp:
    D = json.load(fp)

for entry in D:
    ing_dict = {}
    for i in entry["ingredients"]:
        if len(i) > 0:
            ing_dict [i] = {}

    entry ["ingredients"] = ing_dict

with open (sys.argv[1], "w", encoding='utf8') as fp:
    json.dump (D, fp, indent=4, ensure_ascii=False)
