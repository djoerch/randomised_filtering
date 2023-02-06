#!/usr/bin/env python

import os
import logging
import numpy as np
from copy import deepcopy

from dipy.io.streamline import load_tractogram, StatefulTractogram, Space, save_tractogram

from argparse import ArgumentParser, RawTextHelpFormatter
from textwrap import dedent


DESC = dedent(
    """
    Read tractogram and apply shift of streamlines such that the
    bounding box in VOX is in the positive part of the coorindate system.
    This can correct the invalid bounding box errors when using the StatefulTractogram
    class, however, the tractogram will still not match another nifti-file
    through this modification.
    """
)
EPILOG = dedent(
    """
    example calls:

      {filename} <path_to_tractogram> <path_to_output_tractogram>
    """.format(
        filename=os.path.basename(__file__)
    )
)


def build_parser():
    p = ArgumentParser(
        description=DESC, epilog=EPILOG, formatter_class=RawTextHelpFormatter
    )
    p.add_argument("tractogram_in", help="Path to tractogram to be adjusted.")
    p.add_argument("tractogram_out", help="Path to tractogram with adjusted header.")
    return p


if __name__ == "__main__":

    args = vars(build_parser().parse_args())

    logger = logging.getLogger(os.path.basename(__file__))
    logger.setLevel(logging.INFO)

    sft = load_tractogram(args["tractogram_in"], reference="same", bbox_valid_check=False)

    # 1. bring to voxel space
    sft.to_vox()
    sft.to_corner()

    # 2. find settings of the affine that would bring the streamlines
    #  to a valid state.
    bbox = sft.compute_bounding_box()
    shift_x = np.min(bbox[:, 0])
    shift_y = np.min(bbox[:, 1])
    shift_z = np.min(bbox[:, 2])
    if shift_x > 0:
        shift_x = 0
    if shift_y > 0:
        shift_y = 0
    if shift_z > 0:
        shift_z = 0
    logger.info(f"shift_x: {shift_x}, shift_y: {shift_y}, shift_z: {shift_z}")

    aff_vox2rasmm = deepcopy(sft.affine)
    aff_vox2rasmm[0:3, -1] = [shift_x, shift_y, shift_z]

    bbox = sft.compute_bounding_box()
    dimensions = [
        int(np.max(bbox[:, i]) - np.min(bbox[:, i]) + 2)
         for i in range(3)
    ]

    reference = (
        aff_vox2rasmm, dimensions, sft.voxel_sizes, sft.voxel_order
    )

    sft.to_rasmm()
    sft = StatefulTractogram(sft.streamlines, reference, space=Space.RASMM)
    sft.to_vox()

    save_tractogram(sft, args["tractogram_out"])
