"""
This script evaluates streamline votes across all experiment instances found
in a folder. It analyzes the intersection of the sets of fully "negative" (N)
streamlines and writes the results to a file. Additionally can write indices
of streamlines with only positive votes to a json file.

Command line args:
    --max_ar: maximum percentage of positive votes (acceptance rate) from SIFT
    experiments for a streamline to be considered "implausible", defaults to 0
    --output_name: name of json containing plausible streamlines (without file ending)

Author: antoniabhain@gmail.com
"""

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
        '--max_ar', required=False, help='maximum percentage of positive votes (acceptance rate) from SIFT experiments for a streamline to be considered implausible, defaults to 0'
    )
    p.add_argument(
        '--output_name', required=False, help='name of json containing plausible streamlines (without file ending)'
    )
    return p

def main():
    args = vars(build_argparser().parse_args())
    
    # get all relevant folders from the path (name must begin with OUTPUT_FOLDER_NAME)
    folders = evaluation_helper.get_output_folders(os.getcwd(), OUTPUT_FOLDER_NAME)
    folders.reverse()

    if args.get('max_ar'):
        max_percentage = int(args['max_ar'])
    else:
        max_percentage = 0

    smallest_subset = folders.pop(0)
    print("smallest subset", smallest_subset)
    print("max percentage", max_percentage)
    print("folders", folders)
    filepath = os.path.join(os.getcwd(), smallest_subset)

    # get fully negative streamlines from smallest subset
    streamline_index = evaluation_helper.process_subsets(filepath)
    streamlines_n_smallest_subset = set([ind[2] for ind in streamline_index if evaluation_helper.get_acceptance_rate(ind) <= max_percentage])

    len_neg_streamlines = len(streamlines_n_smallest_subset)
    print("Neg streamlines", len_neg_streamlines)
    print("# streamlines with <= %s%% P votes in smallest subset: %s" %(max_percentage, len_neg_streamlines))

    streamlines_n = []
    not_included = []
    positive = []
    not_seen = []
    s_i = [streamline_index]

    with open("implausible_streamlines_"+str(smallest_subset)+"_"+str(max_percentage)+".csv", "w") as f:

        f.write("# streamlines with <= %s%% P votes in %s: %s\n\n" %(max_percentage, smallest_subset, len_neg_streamlines))
        f.write("subset size;# streamlines in intersection;%% of streamlines in intersection;# streamlines not in intersection;\
        # streamlines with P votes;# streamlines not seen\n")

        # compare "strictest" set of plausible streamlines with those from the other randomized experiments
        for folder in folders:
            print("Looking at folder", folder)
            streamline_p_tmp, \
            streamline_n_tmp, \
            streamline_not_seen_tmp,\
             s_i_tmp = evaluation_helper.get_conditional_sets_from_folder(folder, max_percentage, get_positives=False)

            print("Checking index set intersections\n")
            included = streamlines_n_smallest_subset & streamline_n_tmp
            not_included_tmp = streamlines_n_smallest_subset - streamline_n_tmp

            not_included.append([folder, set(not_included_tmp)])

            intersection_positives = streamlines_n_smallest_subset & streamline_p_tmp
            positive.append([folder, intersection_positives])

            intersection_not_seen = streamlines_n_smallest_subset & streamline_not_seen_tmp
            not_seen.append([folder, intersection_not_seen])

            streamlines_n.append(streamline_n_tmp)
            s_i.append(s_i_tmp)

            f.write("%s;%s;%s%%;%s;%s;%s\n" % (folder, len(included), \
            round(100 * len(included) / (len_neg_streamlines - len(intersection_not_seen)),2), \
            len(not_included_tmp),
            len(intersection_positives),
            len(intersection_not_seen)))


        # intersect all sets one after another to check how streamline count is decreased by how many intersections
        intersect_all_neg = streamlines_n_smallest_subset
        for i,elem in enumerate(streamlines_n):
            intersect_all_neg = intersect_all_neg & elem
            f.write("left after intersection with %s:; %s\n" % (folders[i],len(intersect_all_neg)))

        f.write("\nIntersection between 100%%N streamlines from all sets: %s\n"
                % (len(intersect_all_neg)))

        amounts_votes = [sum([len(s[x][0])+len(s[x][1]) for s in s_i]) for x in intersect_all_neg]
        amounts_votes = np.sort(np.array(amounts_votes))
        print("Least votes:", amounts_votes[0])
        print("Most votes:", amounts_votes[-1])
        print("Median:", np.median(amounts_votes))
        print("Mean:", np.mean(amounts_votes))
        
        f.write("Intersection between all sets of streamlines not included: %s\n"% (len(evaluation_helper.intersect_all_sets_in_list(not_included))))
        f.write("Intersection between all sets of streamlines positive: %s\n"% (len(evaluation_helper.intersect_all_sets_in_list(positive))))
        f.write("Unification between all sets of streamlines positive: %s\n" % (len(evaluation_helper.unify_all_sets_in_list(positive))))
        f.write("Intersection between all sets of streamlines not seen: %s\n" % (len(evaluation_helper.intersect_all_sets_in_list(not_seen))))
        f.write("Unification between all sets of streamlines not seen: %s\n" % (len(evaluation_helper.unify_all_sets_in_list(not_seen))))    

        # write streamline indices if output file path is given
        if args.get('output_name'):
            streamline_indices.write_list_of_streamline_indices(args['output_name']+".json", \
                list(intersect_all_neg), os.path.join(os.getcwd(),"all.trk"))

if __name__ == '__main__':
    main()
