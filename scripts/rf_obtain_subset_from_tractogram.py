#!/usr/bin/env python

import os
import nibabel as nib
import json

from argparse import ArgumentParser, RawTextHelpFormatter
from textwrap import dedent


DESC = """
Obtain a subset of the streamlines in a given tractogram file which correspond
to a given set of streamline indices provided in a json file.
"""
EPILOG = dedent(
    """
    example calls:

      {filename} <path_to_tractogram> <path_to_json_file> <path_to_output_file>

    ---
      Author: djoerch@gmail.com
    """.format(filename=os.path.basename(__file__))
)


def build_parser():
    p = ArgumentParser(description=DESC, epilog=EPILOG, formatter_class=RawTextHelpFormatter)
    p.add_argument('tractogram', help='Path to tractogram to be subsampled.')
    p.add_argument('json',
                   help='Path to json file containing streamline indices (e.g. output of scil_streamlines_math.py).\n'
                   'Expected structure is '
                   'dict("filenames": ["<filename_1>", ...], "<filename_1>": [<idx1>, <idx2>, ...], ...).')
    p.add_argument('output', help='Path to output tractogram.')
    return p


if __name__ == "__main__":

    args = vars(build_parser().parse_args())

    # load tractogram
    trk = nib.streamlines.load(args['tractogram'])  # type: nib.streamlines.TrkFile
    t = trk.tractogram.to_world()  # bring to RASmm

    # load indices
    with open(args['json'], 'r') as f:
        json_content = json.load(f)

    filenames = json_content['filenames']

    s = "Loaded streamline indices:\n"
    for filename in filenames:
        s += "\t{file:<60} : {nb_streamlines:>8}\n".format(file=filename, nb_streamlines=len(json_content[filename]))
    s += " -> Using indices from {file_to_use}.".format(file_to_use=filenames[0])
    print(s)

    # create tractogram from subset of streamlines
    t_new = nib.streamlines.Tractogram(
        streamlines=t.streamlines[json_content[filenames[0]]],
        affine_to_rasmm=t.affine_to_rasmm  # NOTE: expected to be eye(4) at this point.
    )

    # write back subset
    nib.streamlines.save(
        tractogram=t_new,  # tractogram with corrected affine in rasmm (or 'world'mm; same as image data)
        filename=args['output'],
        header=trk.header  # header from given image data; defines the 'voxmm' space of the streamlines
    )
