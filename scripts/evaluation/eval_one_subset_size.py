"""
This script evaluates streamline votes in a folder containing both plausible/
implausible index .jsons and write main statistics them to a result file.

Command line args: [optional] 
--folder_path: path to experiment folder, as seen from cwd, will otherwise use cwd
--json_path: path to json file containing indices that are relevant for
the statistics. Will otherwise evaluate for all streamlines.

Author: antoniabhain@gmail.com
"""

import json
import os
from argparse import ArgumentParser, RawTextHelpFormatter

import evaluation_helper

def build_argparser():
    p = ArgumentParser(
        formatter_class=RawTextHelpFormatter
    )
    p.add_argument(
        '--folder_path', required=False, help='path to experiment folder, as seen from cwd'
    )
    p.add_argument(
        '--json_path', required=False, help='path to json file containing indices that are relevant for the statistics'
    )
    return p

def main():
    args = vars(build_argparser().parse_args())
    
    filepath = os.getcwd()

    if args.get('folder_path'):
        name = args['folder_path']
        print("Looking in folder", name)
        filepath = os.path.join(filepath, name)
    else:
        name = None

    # determine number of subsets
    subsets = sum([x[-19:] == '_plausible_ref.json' for x in os.listdir(filepath)])    
        
    if args.get('json_path'):
        json_path = args['json_path']        
        print("Analyzing only indices from", json_path)
        ind = evaluation_helper.get_indices_from_json(json_path)

    # get vote statistics for every of the 10M streamlines
    streamline_index = evaluation_helper.process_subsets(filepath)

    # call function that evaluates votes and writes them to [name].csv
    if args.get('json_path'):
        evaluation_helper.evaluate_subsets(np.array(streamline_index)[ind], subsets, name)
    else:
        evaluation_helper.evaluate_subsets(streamline_index, subsets, name)


if __name__ == '__main__':
    main()
