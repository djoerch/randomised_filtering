#!/usr/bin/env python

import numpy as np
import nibabel as nib

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from textwrap import dedent
from argparse import ArgumentParser, RawTextHelpFormatter

from randomised_filtering.streamline_indices import write_list_of_streamline_indices


DESC = dedent("""
    Create a .json file of randomly chosen streamline indices.
""")
EPILOG = dedent("""
    -- author:
        djoerch@gmail.com
""")


def build_argparser():
    p = ArgumentParser(
        description=DESC, epilog=EPILOG, formatter_class=RawTextHelpFormatter
    )

    p.add_argument('reference_file', help='Reference tractogram file.')
    p.add_argument(
        'num_streamlines', type=int, help='Number of randomly chosen streamlines.'
    )
    p.add_argument('output_file', help='Path to output file (.json).')
    p.add_argument(
        '--hist', required=False, help='Path to histogram plot of the created indices.'
    )

    return p


def main():

    args = vars(build_argparser().parse_args())

    tf = nib.streamlines.load(args['reference_file'], lazy_load=True)

    # idx_list = (tf.header['nb_streamlines'] * np.random.rand(args['num_streamlines'])).astype('int32').tolist()
    idx_list = np.random.choice(
        np.arange(tf.header['nb_streamlines']),
        size=args['num_streamlines'],
        replace=False
    ).tolist()
    write_list_of_streamline_indices(
        path_to_json_file=args['output_file'],
        list_sl_idx=idx_list,
        path_to_tractogram=args['reference_file']
    )

    if args.get('hist'):
        fig = plt.hist(np.array(idx_list))
        plt.savefig(args['hist'])


if __name__ == "__main__":
    main()
