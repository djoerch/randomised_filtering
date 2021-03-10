#!/usr/bin/env bash

# -- desc
#  Small experiment to see if different runs of sift on random subsets of a whole brain tractogram
#   lead to different selections of streamlines. If so, it is worth to do larger experiments on randomised
#   application of tractogram filtering with sift or other approaches.
#
# -- author
#  danjorg@kth.se


BASE_PATH=/home/djoergens/randomised_filtering/dataset/599671
# PATH_TO_SIMG=/mnt/raid5/djoergens/singularity_test/dec_tab_commit_sandbox.sif


NUM_REALISATIONS=1
SAMPLE_SIZE=100000


BOOTSTRAP_IDS=$(seq 1 ${NUM_REALISATIONS})


OUTPUT_FOLDER=output  # all generated files will be put in here


function wait_commands {
# args: 1 - process id, 2 - ...

    while [[ ${#@} -gt 0 ]]
    do
        wait ${1}
        echo "Process ${1} is finished."
        shift
    done

}


echo
echo " - - $(date)"
echo "  base path: ${BASE_PATH}"
echo "  singularity image: ${PATH_TO_SIMG}"
echo "  number of bootstrap realisations: ${NUM_REALISATIONS}"
echo "  number of streamlines per realisation: ${SAMPLE_SIZE}"
echo


PATH_TO_OUTPUT_FOLDER="${BASE_PATH}/${OUTPUT_FOLDER}"
mkdir -p ${PATH_TO_OUTPUT_FOLDER}

# obtain index files
for i in ${BOOTSTRAP_IDS}
do
    rf_create_random_streamline_indices.py \
        ${BASE_PATH}/All_10M_corrected.trk \
        ${SAMPLE_SIZE} \
        ${PATH_TO_OUTPUT_FOLDER}/subset_${i}.json \
        --hist ${PATH_TO_OUTPUT_FOLDER}/subset_${i}.png
done


# obtain subsets
running_commands=()
for jsonfile in $(ls ${PATH_TO_OUTPUT_FOLDER}/* | grep json)
do
    rf_obtain_subset_from_tractogram.py \
        ${BASE_PATH}/All_10M_corrected.trk \
        ${jsonfile} \
        ${jsonfile%.json}.trk &
    running_commands+=($!)  # add process id to running command list
done

# wait for all running commands to finish
wait_commands ${running_commands[@]}


# convert to tck
running_commands=()
for tractofile in $(ls ${PATH_TO_OUTPUT_FOLDER}/* | grep subset | grep trk)
do
    scil_convert_tractogram.py \
        --reference ${BASE_PATH}/data.nii.gz \
        ${tractofile} \
        ${tractofile%.trk}.tck &
#    cmd='source "${PATH_TO_VENV_SCILPY}/bin/activate" && '"scil_convert_tractogram.py --reference ${BASE_PATH}/data.nii.gz ${tractofile} ${tractofile%.trk}.tck"
#    singularity \
#        exec ${PATH_TO_SIMG} \
#        bash -c "${cmd}" &
    running_commands+=($!)
done
wait_commands ${running_commands[@]}


# call sift
for tractofile in $(ls ${PATH_TO_OUTPUT_FOLDER}/* | grep subset | grep tck)
do
    tcksift \
        ${tractofile} \
        ${BASE_PATH}/WM_FODs.mif \
        ${tractofile%.tck}_sift.tck \
        -out_selection ${tractofile%.tck}_selection.txt
#    cmd="tcksift ${tractofile} ${BASE_PATH}/WM_FODs.mif ${tractofile%.tck}_sift.tck -out_selection ${tractofile%.tck}_selection.txt"
#    singularity \
#        exec ${PATH_TO_SIMG} \
#        bash -c "${cmd}"
done


# convert selection files to index files
for selection_file in $(ls ${PATH_TO_OUTPUT_FOLDER}/* | grep selection.txt)
do
    rf_streamline_indices_from_mrtrix_selection.py \
        ${selection_file} \
        ${selection_file%_selection.txt}.trk \
        ${selection_file%_selection.txt}
done


# transform index files to reference tractogram
for i in ${BOOTSTRAP_IDS}
do
    rf_transform_indices_reference.py \
        ${PATH_TO_OUTPUT_FOLDER}/subset_${i}.json \
        ${PATH_TO_OUTPUT_FOLDER}/subset_${i}_plausible_indices.json \
        ${PATH_TO_OUTPUT_FOLDER}/subset_${i}_plausible_ref.json
    rf_transform_indices_reference.py \
        ${PATH_TO_OUTPUT_FOLDER}/subset_${i}.json \
        ${PATH_TO_OUTPUT_FOLDER}/subset_${i}_implausible_indices.json \
        ${PATH_TO_OUTPUT_FOLDER}/subset_${i}_implausible_ref.json
done


# perform voting
eval rf_analyse_index_files.py \
    ${PATH_TO_OUTPUT_FOLDER}/subset_{1..${NUM_REALISATIONS}}_plausible_ref.json \
    --out-basename ${PATH_TO_OUTPUT_FOLDER}/subsets_plausible
eval rf_analyse_index_files.py \
    ${PATH_TO_OUTPUT_FOLDER}/subset_{1..${NUM_REALISATIONS}}_implausible_ref.json \
    --out-basename ${PATH_TO_OUTPUT_FOLDER}/subsets_implausible


# extract tractograms from resulting vote index files
#running_commands=()
#for idx_file in $(ls ${PATH_TO_OUTPUT_FOLDER} | grep subsets_ | grep ible_votes | grep json)
#do
#    rf_obtain_subset_from_tractogram.py \
#        ${PATH_TO_OUTPUT_FOLDER}/All_10M_corrected.trk \
#        ${idx_file} \
#        ${idx_file%.json}.trk &
#    running_commands+=($!)  # add process id to running command list
#done
#wait_commands ${running_commands[@]}


#for idx_file in $(ls ${PATH_TO_OUTPUT_FOLDER} | grep subsets_ | grep ible_min_votes | grep json)
#do
#    rf_obtain_subset_from_tractogram.py \
#        ${BASE_PATH}/All_10M_corrected.trk \
#        ${idx_file} \
#        ${idx_file%.json}.trk
#done


# make confusion matrix
mkdir ${PATH_TO_OUTPUT_FOLDER}/conf_mat
running_commands=()
for i in ${BOOTSTRAP_IDS}
do
    for j in ${BOOTSTRAP_IDS}
    do
        rf_analyse_index_files.py \
            ${PATH_TO_OUTPUT_FOLDER}/subset_${i}_plausible_ref.json \
            ${PATH_TO_OUTPUT_FOLDER}/subset_${j}_implausible_ref.json \
            --out-basename ${PATH_TO_OUTPUT_FOLDER}/conf_mat/subsets_plausible_${i}_implausible_${j} &
        running_commands+=($!)  # add process id to running command list
    done
done
wait_commands ${running_commands[@]}


# sum rows of confusion matrix
running_commands=()
for i in ${BOOTSTRAP_IDS}
do
    eval rf_analyse_index_files.py \
        ${PATH_TO_OUTPUT_FOLDER}/conf_mat/subsets_plausible_${i}_implausible_{1..${NUM_REALISATIONS}}_votes_2.json \
        --out-basename ${PATH_TO_OUTPUT_FOLDER}/conf_mat/subsets_plausible_${i}_implausible_all &
    running_commands+=($!)  # add process id to running command list
done
wait_commands ${running_commands[@]}


# nb-votes-based conf_mat
running_commands=()
for i in $(seq 1 ${NUM_REALISATIONS})
do
    for j in $(seq 1 ${NUM_REALISATIONS})
    do
        rf_analyse_index_files.py \
            ${PATH_TO_OUTPUT_FOLDER}/subsets_plausible_votes_${i}.json \
            ${PATH_TO_OUTPUT_FOLDER}/subsets_implausible_votes_${j}.json \
            --out-basename ${PATH_TO_OUTPUT_FOLDER}/conf_mat/subsets_plausible_votes_${i}_implausible_votes_${j} &
        running_commands+=($!)  # add process id to running command list
    done
done
wait_commands ${running_commands[@]}
