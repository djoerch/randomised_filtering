"""
Evaluates vote statistics across multiple subset sizes.

Command line args: [optional]
--json_path: path to json file containing indices that are relevant for
the statistics. Will otherwise evaluate for all streamlines.

Author: antoniabhain@gmail.com
"""

import json
import os
import numpy as np
from argparse import ArgumentParser, RawTextHelpFormatter

import evaluation_helper

OUTPUT_FOLDER_NAME="output"

# amount of subsets used across all experiment instances (purely theoretical max votes received by a streamline).
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
    
    if args.get('json_path'):
        json_path = args['json_path']        
        print("Analyzing only indices from", json_path)
        ind = evaluation_helper.get_indices_from_json(json_path)
        
    # get all relevant folders from the path (name must begin with OUTPUT_FOLDER_NAME)
    folders = evaluation_helper.get_output_folders(filepath, OUTPUT_FOLDER_NAME)

    # get vote distributions for each streamline across all subset sizes in one variable
    meta_streamline_index = evaluation_helper.get_meta_streamline_index(folders)

    # evaluate relevant streamlines and write vote distributions to file
    if args.get('json_path'):
        evaluation_helper.evaluate_subsets(np.array(meta_streamline_index)[ind], MAX_SUBSETS,"all")
    else:
        evaluation_helper.evaluate_subsets(meta_streamline_index, MAX_SUBSETS,"all")

if __name__ == '__main__':
    main()
