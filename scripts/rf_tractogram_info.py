#!/usr/bin/env python

import os
import nibabel as nib
import pandas as pd

from argparse import ArgumentParser, RawTextHelpFormatter
from textwrap import dedent
from tqdm import tqdm


DESC = "Query information from a given tractogram file opened with nibabel."
EPILOG = dedent(
    """
    example calls:

      {filename} <path_to_tractogram>
      {filename} <path_to_tractogram> --query nb_streamlines

    ---
      Author: djoerch@gmail.com
    """.format(filename=os.path.basename(__file__))
)


def build_parser():
    p = ArgumentParser(
        description=DESC, epilog=EPILOG, formatter_class=RawTextHelpFormatter
    )
    p.add_argument('tractogram', nargs='+', help='Path to tractogram to be queried.')
    p.add_argument(
        '--query',
        action='append',
        required=False,
        default=[],
        help='Name of header field which should be printed.'
    )
    p.add_argument(
        '--delimiter',
        default=',',
        help='Character to be used as separator in csv dump. (Default: ",")'
    )
    ag = p.add_mutually_exclusive_group(required=False)
    ag.add_argument(
        '--to-clipboard', action='store_true',
        help='Copy data as table data to system clipboard to be pated in a spreadsheet.'
    )
    ag.add_argument(
        '--to-csv', metavar='PATH_TO_CSV', dest='path_to_csv_file',
        help='Path to csv to dump the table data to.'
    )
    return p


if __name__ == "__main__":
    args = vars(build_parser().parse_args())

    header = ['filename'] + args['query']
    table = list()

    for filepath in tqdm(
            args['tractogram'],
            desc="Looping over tractograms",
            ncols=100
    ):

        t = nib.streamlines.load(filepath, lazy_load=True)

        if len(args['query']) == 0:
            print(t.header)  # print header in case of no queries
        else:
            table.append([
                filepath,
                *[t.header[query] for query in args['query']]
            ])

    f = pd.DataFrame(table, columns=header)

    # print the data
    if args['to_clipboard']:
        f.to_clipboard()
    elif args.get('path_to_csv_file'):
        f.to_csv(args['path_to_csv_file'], sep=args['delimiter'])
    else:
        print(f)
