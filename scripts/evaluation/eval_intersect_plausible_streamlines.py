"""
This script evaluates streamline votes across all experiment instances found
in a folder. It analyzes the intersection of the sets of fully "positive" (P)
streamlines and writes the results to a file. Additionally can write indices
of streamlines with only positive votes to a json file.

Command line args:
    --min_ar: minimum percentage of positive votes (acceptance rate) from SIFT
    experiments for a streamline to be considered "plausible", defaults to 100
    --output_name: name of json containing plausible streamlines (without file ending)

Author: antoniabhain@gmail.com
"""

import json
import os
import itertools
import numpy as np
import streamline_indices
from argparse import ArgumentParser, RawTextHelpFormatter

import evaluation_helper


OUTPUT_FOLDER_NAME="output"

def build_argparser():
    p = ArgumentParser(
        formatter_class=RawTextHelpFormatter
    )
    p.add_argument(
        '--min_ar', required=False, help='minimum percentage of positive votes (acceptance rate) from SIFT experiments for a streamline to be considered plausible, defaults to 100'
    )
    p.add_argument(
        '--output_name', required=False, help='name of json containing plausible streamlines (without file ending)'
    )
    return p


def main():
    args = vars(build_argparser().parse_args())
    
    # get all relevant folders from the path (name must begin with OUTPUT_FOLDER_NAME)
    folders = evaluation_helper.get_output_folders(os.getcwd(), OUTPUT_FOLDER_NAME)

    if args.get('min_ar'):
        min_percentage = int(args['min_ar'])
    else:
        min_percentage = 100

    # get folder of experiment with biggest subset size because it has the
    # least amount of streamlines with fully positive votes
    biggest_subset = folders.pop(0)
    print("biggest subset", biggest_subset)
    print("min percentage", min_percentage)
    print("folders", folders)
    filepath = os.path.join(os.getcwd(), biggest_subset)

    # get vote statistics for every of the 10M streamlines
    streamline_index = evaluation_helper.process_subsets(filepath)

    # get indices of streamlines which fulfill minimum percentage of P votes
    streamlines_p_biggest_subset = \
        set([ind[2] for ind in streamline_index if \
        evaluation_helper.get_acceptance_rate(ind) >= min_percentage])

    len_pos_streamlines = len(streamlines_p_biggest_subset)

    # save results from all experiment instances in lists for later use
    # streamlines with only P votes in other experiment instances
    streamlines_p = []

    # streamlines in streamlines_p_biggest_subset which were not included
    # in fully P sets of other experiment instances
    not_included = []

    # streamlines in streamlines_p_biggest_subset with negative votes in other
    # experiment instances
    negative = []

    # streamlines in streamlines_p_biggest_subset which were not seen in other
    # experiment instances
    not_seen = []

    # streamline votes from all experiment instances
    s_i = [streamline_index]

    with open("plausible_streamlines_"+str(biggest_subset)+"_"+str(min_percentage)+".csv", "w") as f:
        
        f.write("# streamlines with >= %s%% P votes in %s: %s\n\n" %(min_percentage, biggest_subset, len_pos_streamlines))
        f.write("subset size;# streamlines in intersection;%% of streamlines in intersection;# streamlines not in intersection;\
        # streamlines with N votes;# streamlines not seen\n")

        # compare "strictest" set of plausible streamlines with those from the other experiment instances
        for folder in folders:
            print("Looking at folder", folder)

            # get sets of streamline indices from other experiment instance
            streamline_p_tmp, \
            streamline_n_tmp, \
            streamline_not_seen_tmp, \
            s_i_tmp = evaluation_helper.get_conditional_sets_from_folder(folder, \
                get_positives=True, percentage=min_percentage)

            print("Checking index set intersections\n")
            included = streamlines_p_biggest_subset & streamline_p_tmp

            not_included_tmp = streamlines_p_biggest_subset - streamline_p_tmp
            not_included.append([folder, set(not_included_tmp)])
            negative.append([folder, streamlines_p_biggest_subset & \
                streamline_n_tmp])
            not_seen.append([folder, streamlines_p_biggest_subset & \
                streamline_not_seen_tmp])

            streamlines_p.append(streamline_p_tmp)
            s_i.append(s_i_tmp)

            f.write("%s;%s;%s%%;%s;%s;%s\n" % (folder, len(included), \
            round(100 * len(included) / (len_pos_streamlines - len(streamline_not_seen_tmp & streamlines_p_biggest_subset)),2), \
            len(not_included_tmp), len(streamlines_p_biggest_subset & streamline_n_tmp), len(streamline_not_seen_tmp & streamlines_p_biggest_subset)))


        # get streamlines which only had P votes in every experiment instanc
        intersect_all_pos = streamlines_p_biggest_subset
        for i,elem in enumerate(streamlines_p):
            intersect_all_pos = intersect_all_pos & elem
            f.write("left after intersection with %s:; %s\n" % (folders[i],len(intersect_all_pos)))

        f.write("\nIntersection between 100%%P streamlines from all sets: %s\n"% (len(intersect_all_pos)))

        # short analysis about the amounts of votes
        amounts_votes = [sum([len(s[x][0])+len(s[x][1]) for s in s_i]) for x in intersect_all_pos]
        amounts_votes = np.sort(np.array(amounts_votes))
        print("Least votes:", amounts_votes[0])
        print("Most votes:", amounts_votes[-1])
        print("Median:", np.median(amounts_votes))
        print("Mean:", np.mean(amounts_votes))

        f.write("Intersection between all sets of streamlines not included: %s\n"% (len(evaluation_helper.intersect_all_sets_in_list(not_included))))
        f.write("Intersection between all sets of streamlines negative: %s\n"% (len(evaluation_helper.intersect_all_sets_in_list(negative))))
        f.write("Unification between all sets of streamlines negative: %s\n" % (len(evaluation_helper.unify_all_sets_in_list(negative))))
        f.write("Intersection between all sets of streamlines not seen: %s\n" % (len(evaluation_helper.intersect_all_sets_in_list(not_seen))))
        f.write("Unification between all sets of streamlines not seen: %s\n" % (len(evaluation_helper.unify_all_sets_in_list(not_seen))))

        # write streamline indices if output file path is given
        if args.get('output_name'):
            streamline_indices.write_list_of_streamline_indices(args['output_name']+".json", list(intersect_all_pos), os.path.join(os.getcwd(),"all.trk"))

if __name__ == '__main__':
    main()
