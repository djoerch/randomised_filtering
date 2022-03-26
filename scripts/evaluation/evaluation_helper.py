"""
Utilities script for various streamline vote evaluations and index file analyses.

Author: antoniabhain@gmail.com
"""

import os
import json
import numpy as np

def build_streamline_index():
    """
    Prepares nested list with one entry for every of the 10M streamlines, for one subset size run of rSIFT:
    Each streamline entry l will contain:
        l[0]: list of subsets where the streamline was accepted by SIFT
        l[1]: list of subsets where the streamline was rejected by SIFT
        l[2]: index of the streamline
    The list still need to be filled - l[0] and l[1] will be empty for each l

    Args: None
    Returns: streamline_index: nested list of length 10 million
    """
    streamline_index = [[[], [], i] for i in range(10000000)]
    return streamline_index

def get_meta_streamline_index(folders, base_path=None):
    """
    Prepares streamline index and fills it with votes for every streamline
    across ALL experiment instances/subset sizes. Note that the subset numbers in each streamline's
    entry may occur multiple times since it's not indicated which subset size experiment they belong to.

    Args: folders: list of folders relevant for the evaluation
          base_path [optional]: path where folders are based
    """

    # get empty streamline index
    meta_streamline_index = build_streamline_index()

    if base_path == None:
        base_path = os.getcwd()

    # log positive and negative votes for streamlines across all subset sizes
    for folder in folders:
        path = os.path.join(base_path, folder)
        meta_streamline_index = process_subsets(path, streamline_index=meta_streamline_index)

    return np.array(meta_streamline_index)

def get_indices_from_json(filepath):
    """
    Loads streamline indices from a json file

    Args: filepath: path/name of file with the indices
    Returns: array of the streamline indices
    """

    with open(filepath) as f:
        data = json.loads(f.readline())
        ind_key = data["filenames"][0]
        ind = data[ind_key]
        ind = np.array(ind,dtype=np.int32)
    return ind

def build_vote_combination_dict(streamline_index, subsets):
    """
    Builds and returns a dictionary of all possible combinations of P/N votes,
    and the respective number of streamlines that have this combination of votes.

    Args: streamline index: nested list with entry for each streamline, and it's
          positive and negative votes (see build_streamline_index())
          subsets: amount of subsets in the experiment

    Returns: dictionary containing all combinations of P/N votes with P+N <=
             subsets as keys (p,n). dict values are amount of streamlines with
             exactly p positive and n negative votes.
    """
    #  prepare dict with keys for all possible combinations of P/N votes
    votedict = dict()
    for p in range(subsets + 1):
        for n in range(subsets + 1):
            if p + n > subsets:
                break
            votedict[(p, n)] = 0

    # fill dict with streamline counts for all P/N combinations
    for streamline in streamline_index:
        p = len(streamline[0])
        n = len(streamline[1])

        votedict[(p, n)] += 1

    return votedict

def intersect_all_sets_in_list(setlist):
    """
    Returns intersection of index sets within a list.

    Args: setlist: list of sets of indices. each entry is [foldername, set]
    Returns: intersection of all sets in the list
    """

    intersect_all = setlist[0][1]
    for elem in setlist:
        intersect_all = intersect_all & elem[1]
    return intersect_all

def unify_all_sets_in_list(setlist):
    """
    Returns unification of index sets within a list.

    Args: setlist: list of sets of indices
    Returns: unification of all sets in the list
    """

    unify_all = setlist[0][1]
    for elem in setlist:
        unify_all = unify_all | elem[1]
    return unify_all

def process_subsets(filepath, streamline_index=None):
    """
    Reads result files of plausible/implausible streamlines for one rSIFT
    instance/subset size and stores the results in streamline index.

    Args: filepath: path to look for subsets
          streamline index [optional]: nested list with entry for each streamline,
                and it's positive and negative votes (see
                build_streamline_index()), will be created if not given

    Returns:
          streamline index containing votes from all subsets for each streamline
    """

    print("\nProcessing subsets for", filepath)

    folder_contents = os.listdir(filepath)
    subsets = sum([x[-19:] == '_plausible_ref.json' for x in folder_contents])
    print("Found data for " + str(subsets) + " subsets.")
    print("\nPreparing streamline array...")

    if streamline_index == None:
        streamline_index = build_streamline_index()

    filename_plausible = "subset_%s_plausible_ref.json"
    filename_implausible = "subset_%s_implausible_ref.json"

    for subset in range(1, subsets + 1):
        # plausible
        name = filename_plausible % subset
        ind = get_indices_from_json(os.path.join(filepath, name))
        for i in ind:
            streamline_index[i][0].append(subset)

        # implausible
        name = filename_implausible % subset
        ind = get_indices_from_json(os.path.join(filepath, name))
        for i in ind:
            streamline_index[i][1].append(subset)

    return streamline_index

def evaluate_subsets(streamline_index, subsets, name):
    """
    Evaluates vote distributions for all streamlines in streamline_index
    and writes the results to file.

    Args: streamline index: nested list with entry for each streamline, and it's
          positive and negative votes (see build_streamline_index)
          subsets: amount of subsets in the experiment
          name: name of the output file
    """

    print("\nEvaluating...")

    # get combinations of P/N votes and respective streamline counts
    statsdict = build_vote_combination_dict(streamline_index, subsets)

    print("Writing distribution by amount of votes...")

    if name == None:
        outputfilename = "results.csv"
    else:
        outputfilename = "results_"+name+".csv"
    
    with open(outputfilename, "w") as f:
        f.write("\n\nDistribution by amount of votes\n-----")

        num_streamlines = len(streamline_index)

        # go through streamlines with a total of 0 votes, 1 vote, 2 votes, ...
        for votesum in range(subsets+1):
            # first, get total # of streamlines with this amount of votes
            # (allows for percentage computation)
            streamline_sum = 0
            for p in range(votesum + 1):
                for n in range(votesum + 1):
                    if p + n != votesum:
                        continue
                    streamline_sum += statsdict[(p, n)]

            # write raw counts and percentage for all vote combinations summing
            # up  to [votesum]
            if streamline_sum > 0:
                f.write("\n%s votes: \n" % votesum)
                f.write("streamlines;%s;%s%%\n\n" % (streamline_sum,
                round(streamline_sum*100 / num_streamlines, 4)))

                for p in range(votesum + 1):
                    for n in range(votesum + 1):
                        if p + n != votesum:
                            continue
                        streamline_count = statsdict[(p, n)]
                        f.write("%sP %sN;%s;%s%% \n" % (p, n, streamline_count,
                        round(streamline_count*100 / streamline_sum, 2)))

        print("Writing amount of streamlines by percentage of P votes...")
        f.write("\n\nPercentage of P votes -- amount of streamlines\n-----\n")

        # get amount of streamlines which were seen at least once
        total_evaluated_streamlines = num_streamlines - statsdict[(0, 0)]

        # get fractions of streamlines by their percentage of P votes (acceptance rate)
        f.write("%% P votes;streamlines;%% of all streamlines with >= 1 vote (lower bound excl, upper bound incl)\n")
        # go in levels of 20%, range -20 to 120 to include EXACTLY 0% / 100% votes
        for lower_bound in range(-20, 120, 20):
            streamline_count = 0

            for combo, number in statsdict.items():
                p, n = combo
                if p + n > 0:
                    percentage_p = p * 100 / (p + n)
                    # not-so-nice-but-easy solution to include 100
                    if percentage_p > min(99.99999,lower_bound) and percentage_p <= lower_bound + 20:
                        streamline_count += number

            # write percentage range, raw streamline count, streamline percentage
            f.write("%s-%s%%;%s;%s%%\n"
            % (max(0,lower_bound), min(100,lower_bound + 20),
            streamline_count,
            round(streamline_count * 100 / total_evaluated_streamlines, 2)))

def get_acceptance_rate(streamline_stats):
    """Returns percentage of positive votes (acceptance rate) received by a specific streamline.

    Args: streamline stats: list of streamline statistics, represents the
          streamline's entry in streamline_index (see build_streamline_index())

    Return: the streamline's acceptance rate. -1 if the streamline had no votes.
    """

    if len(streamline_stats[0]) + len(streamline_stats[1]) == 0:
        return -1
    ar = len(streamline_stats[0])*100/(len(streamline_stats[0]) + len(streamline_stats[1]))
    return ar

def get_output_folders(path, folder_name):
    """
    Returns list of folders in path whose name starts with folder_name, sorts them
    """
    folders = [f for f in os.listdir(path) if f.startswith(folder_name)]

    # sort folders, if their name contains "_" and is followed by a number
    try:
        folders = sorted(folders, key=lambda x: int(x.split("_")[1] if len(x.split("_")) > 1 else 0))
    except ValueError:
        print("Could not sort output folders, will return unsorted list")
        
    return folders

def get_conditional_sets_from_folder(path, percentage, get_positives=True):
    """
    Helper function for intersect_plausible/intersect_implausible.

    Compiles sets of either fully positive/negative streamlines in the path
    (depending on which of the two is of interest).

    Also retrieves set of streamlines which did not fulfill the condition of
    fully positive/negative, and the set of streamlines which were not seen.

    Args: path: path in which to look for subset evaluations
          percentage: minimal/maximal percentage of positive votes necessary
          for streamline to count as fully positive/negative
          get_positives: whether to get fully positive or fully negative
          streamlines
    """
    filepath = os.path.join(os.getcwd(), path)
    streamline_index = process_subsets(filepath)

    streamline_p_tmp = []
    streamline_n_tmp = []
    streamline_never_seen_tmp = []

    # get P/N vote percentage for all streamlines and sort them into the
    # correspondig list
    for ind in streamline_index:
        ar = get_acceptance_rate(ind)

        if ar == -1:
            streamline_never_seen_tmp.append(ind[2])

        if get_positives:
            if ar >= percentage:
                streamline_p_tmp.append(ind[2])
            else:
                streamline_n_tmp.append(ind[2])
        else:
            if ar <= percentage:
                streamline_n_tmp.append(ind[2])
            else:
                streamline_p_tmp.append(ind[2])

    return set(streamline_p_tmp), set(streamline_n_tmp), set(streamline_never_seen_tmp), streamline_index
