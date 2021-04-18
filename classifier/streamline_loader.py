"""
Helper functions for network training/testing, specifically data loading.

-- author antoniabhain@gmail.com
"""
import nibabel as nib
import json
import numpy as np

def get_indices_from_json(filepath):
    """
    Loads streamline indices from a json file

    Args: filepath: path/name of file with the indices
    Returns: array of the streamline indices
    """
    
    with open(filepath,"r") as f:
        data = json.loads(f.readline())
        ind_key = data["filenames"][0]
        ind = data[ind_key]
    return ind

def get_streamlines_from_trk(filepath):
    """ Loads trk and returns streamline array """
    return np.asarray(nib.streamlines.trk.TrkFile.load(filepath).tractogram.streamlines)

def get_min_max(streamlines):
    """ Determines and returns min/max of coordinates in every dimension """
    
    print("getting min coordinates")
    testmin = np.array([np.min(tmp, axis=0) for tmp in streamlines])
    print("getting max coordinates")
    testmax = np.array([np.max(tmp, axis=0) for tmp in streamlines])

    mincoord = np.min(testmin, axis=0)
    maxcoord = np.max(testmax, axis=0)
    return mincoord, maxcoord

def normalize_streamlines(streamlines, mincoord=None, maxcoord=None):
    """
    Normalize streamline coordinates
    
    Args: streamlines: array of all streamlines
          mincoord [optional]: coordinate with pre-determined minimum values
          maxcoord [optional]: coordinate with pre-determined maximum values
    """
    # option of determining min, max - needs to be separate if data from one subject is normalized in separate batches
    try:
        if mincoord == None or maxcoord == None:
            mincoord, maxcoord = get_min_max(streamlines)
    except ValueError:
        pass

    print("normalizing streamlines")
    print("min", mincoord)
    print("max", maxcoord)
    return np.asarray([((s - mincoord)/(maxcoord - mincoord))*2 - 1 for s in streamlines])

def load_data(trk_path, json_path_pos, json_path_neg, normalize=False):
    """
    Loads streamline data for one subject, optional normalization.
    
    Args: trk_path: Path to tractogram file (.trk)
          json_path_pos: Path to file with indices of streamlines which should count into plausible set
          json_path_neg: Path to file with indices of streamlines which should count into implausible set
          normalize: whether streamlines should be normalized or not
    
    Returns: pos_streamlines: Set of positive/plausible streamlines
             neg_streamlines: Set of negative/implausible streamlines
             o_streamlines: Set of other/inconclusive streamlines
    """
    
    print("Loading data from", trk_path)

    # load streamlnes
    all_streamlines = get_streamlines_from_trk(trk_path)

    if normalize:
        all_streamlines = normalize_streamlines(all_streamlines)

    # get indices from pseudo ground truth
    pos_indices = get_indices_from_json(json_path_pos)
    neg_indices = get_indices_from_json(json_path_neg)
    set_p = set(pos_indices)
    set_n = set(neg_indices)

    # find inconclusive streamlines
    pos_streamlines = all_streamlines[pos_indices]
    neg_streamlines = all_streamlines[neg_indices]
    o_indices = [r for r in range(len(all_streamlines)) if (not r in set_p and not r in set_n)]
    o_streamlines = all_streamlines[o_indices]

    return pos_streamlines, neg_streamlines, o_streamlines
