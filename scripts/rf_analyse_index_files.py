#!/usr/bin/env python

import os
import json
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from argparse import ArgumentParser, RawTextHelpFormatter
from textwrap import dedent, indent
from tqdm import tqdm
from typing import List

from utils.streamline_indices import write_list_of_streamline_indices


DESC = """
Analyse set of given index files
"""
EPILOG = dedent(
    """
    example calls:

      {filename} subset_5M_0_plausible_ref.json subset_5M_1_plausible_ref.json hist_plausible.png

    ---
      Author: danjorg@kth.se
    """.format(filename=os.path.basename(__file__))
)


def build_parser():
    p = ArgumentParser(description=DESC, epilog=EPILOG, formatter_class=RawTextHelpFormatter)
    p.add_argument('index_files', nargs='+', help='Path to index files in same reference space.')
    p.add_argument('--hist', required=False, help='Path to plot file.')
    p.add_argument('--stats', action='store_true', help='Print statistics.')
    p.add_argument('--out-basename', required=False, help='Path to file basename of output index files.')
    return p


def read_index_list_from_file(json_file: str) -> List[int]:
    """
    Read index list and reference tractogram filename from index file.

    Parameters
    ----------
    json_file : str
        path to json index file

    Returns
    -------
    path_to_ref_tractogram : str
        path to reference tractogram
    idx_list : List[int]
        list of streamline indices in the reference tractogram
    """
    with open(json_file, 'r') as f:
        idx_list = json.load(f)
        return idx_list['filenames'][0], idx_list[idx_list['filenames'][0]]


if __name__ == "__main__":
    args = vars(build_parser().parse_args())

    idx_list = []
    for idx_file in args['index_files']:
        ref_file, l = read_index_list_from_file(idx_file)
        print('NOTE: reference file for {idx_file} is "{ref_file}".'.format(idx_file=idx_file, ref_file=ref_file))
        idx_list.extend(l)

    idx_arr = np.array(idx_list)
    count_idx, counts = np.unique(idx_arr, return_counts=True)

    if args.get('stats'):
        print("Statistics:\n{}".format(indent(str(pd.Series(counts).describe()), " "*4)))

    if args.get('hist'):
        plt.hist(counts)
        plt.savefig(args['hist'])

    if args.get('out_basename'):
        print('NOTE: It is assumed here that all index files have the same reference file. CHECK THIS!')
        for i in tqdm(range(1, len(args['index_files']) + 1), desc="Writing index files for vote counts"):
            write_list_of_streamline_indices(
                path_to_json_file=args['out_basename'] + '_votes_{}.json'.format(i),
                list_sl_idx=count_idx[counts==i].tolist(),
                path_to_tractogram=ref_file
            )
        for i in tqdm(range(1, len(args['index_files']) + 1), desc="Writing index files for min vote counts"):
            write_list_of_streamline_indices(
                path_to_json_file=args['out_basename'] + '_min_votes_{}.json'.format(i),
                list_sl_idx=count_idx[counts>=i].tolist(),
                path_to_tractogram=ref_file
            )
