"""
Retrieves percentage of positives votes received by streamlines across all ex-
periment instances/subset sizes. Either for all streamlines or a set of stream-
lines of interest.

Command line args:
--json_path: path to json file containing indices that are relevant for
the statistics. Will otherwise evaluate for all streamlines.

Author: Antonia Hain (s8anhain@stud.uni-saarland.de)
"""

import json
import sys
import os
import numpy as np
from argparse import ArgumentParser, RawTextHelpFormatter

import evaluation_helper

OUTPUT_FOLDER_NAME="output"
MAX_SUBSETS = 455

def build_argparser():
    p = ArgumentParser(
        formatter_class=RawTextHelpFormatter
    )
    p.add_argument(
        '--json_path', required=False, help='path to json file containing indices that are relevant for the statistics'
    )
    return p


def main():
    args = vars(build_argparser().parse_args())
    
    filepath = os.getcwd()

    # get all relevant folders from the path (name must begin with OUTPUT_FOLDER_NAME)
    folders = evaluation_helper.get_output_folders(filepath, OUTPUT_FOLDER_NAME)

    # get vote distributions for each streamline across all subset sizes in one variable
    meta_streamline_index = evaluation_helper.get_meta_streamline_index(folders)

    # get relevant streamlines
    if args.get('json_path'):
        jsonpath = args['json_path']
        print("Analyzing only indices from", jsonpath)
        ind = evaluation_helper.get_indices_from_json(jsonpath)
        entries = meta_streamline_index[ind]
        name = jsonpath.split(".")[0]
    else:
        entries = meta_streamline_index
        name = ""

    # get acceptance rates for all streamlines of interests and write to file.
    result = np.array([[entry[2],evaluation_helper.get_pos_percentage(entry)] for entry in entries])
    np.savetxt("percentages_"+name+".txt", result)

if __name__ == '__main__':
    main()
