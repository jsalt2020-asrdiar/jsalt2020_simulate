#!/usr/bin/env python3
# encoding: utf-8

# Copyright 2020 Shanghai Jiao Tong University (Wangyou Zhang)
#  Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)

import argparse
import json


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('jsons', type=str, nargs='+',
                        help='json files')
    args = parser.parse_args()

    json_list = []
    for js in args.jsons:
        with open(js) as f:
            data = json.load(f)

        # flatten the json lists
        if isinstance(data, list):
            json_list.extend(data)
        else:
            json_list.append(data)

    jsonstring = json.dumps(json_list, indent=2)
    print(jsonstring)
