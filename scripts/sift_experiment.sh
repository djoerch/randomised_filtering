#!/usr/bin/env bash

# -- desc
#  Runs SIFT experiment for one subject.
#
# Args: BASE_PATH: path to folder with subject data
#       RANDOMIZED: 0 for sequential, 1 for randomized (rSIFT).
#       NUM_REALISATIONS: number of repetitions (amount of subsets)
#       SAMPLE_SIZE: size of each subset
#       OUTPUT_FOLDER: name of folder where results will be put. will be
#                     created as sub-folder of BASE_PATH
#
# -- author
#  djoerch@gmail.com, antoniabhain@gmail.com


# parameters
BASE_PATH="${1}"
RANDOMIZED="${2}"
NUM_REALISATIONS="${3}"
SAMPLE_SIZE="${4}"
OUTPUT_FOLDER="${5}"  # all generated files will be put in here
TRACTOGRAM_NAME="all.trk"


BOOTSTRAP_IDS=$(seq 1 "${NUM_REALISATIONS}")


function wait_commands {
# args: 1 - process id, 2 - ...
    while [[ ${#@} -gt 0 ]]
    do
        wait "${1}"
        echo "Process ${1} is finished."
        shift
    done
}


echo
echo " - - $(date)"
echo "  base path: ${BASE_PATH}"
echo "  number of bootstrap realisations: ${NUM_REALISATIONS}"
echo "  number of streamlines per realisation: ${SAMPLE_SIZE}"
echo

echo " path $PWD"


PATH_TO_OUTPUT_FOLDER="${BASE_PATH}/${OUTPUT_FOLDER}"
mkdir -p "${PATH_TO_OUTPUT_FOLDER}"


#obtain index files
for i in ${BOOTSTRAP_IDS}
do
  # RANDOMIZED is 1 for randomized indices, 0 for sequential indices
  # --set  only necessary for sequential indices (indicates which batch to use)
    rf_create_streamline_indices.py \
        --set "${i}" \
        --hist "${PATH_TO_OUTPUT_FOLDER}/subset_${i}.png" \
        "${BASE_PATH}/${TRACTOGRAM_NAME}" \
        "${SAMPLE_SIZE}" \
        "${RANDOMIZED}" \
        "${PATH_TO_OUTPUT_FOLDER}/subset_${i}.json"
done

# obtain subsets
running_commands=()

JSONLIST=$(ls ${PATH_TO_OUTPUT_FOLDER}/* | grep json)
rf_obtain_subsets_from_tractogram.py \
    ${BASE_PATH}/${TRACTOGRAM_NAME} \
    "${JSONLIST}" #\

# wait for all running commands to finish
wait_commands ${running_commands[@]}

# convert to tck (needed to run SIFT)
running_commands=()
for tractofile in $(ls ${PATH_TO_OUTPUT_FOLDER}/* | grep subset | grep trk)
do
    scil_convert_tractogram.py \
        --reference "${BASE_PATH}/data.nii.gz" \
        "${tractofile}" \
        "${tractofile%.trk}.tck"
    running_commands+=($!)
done
wait_commands ${running_commands[@]}

# call SIFT
for tractofile in $(ls ${PATH_TO_OUTPUT_FOLDER}/* | grep subset | grep tck)
do
    tcksift \
        "${tractofile}" \
        "${BASE_PATH}/WM_FODs.mif" \
        "${tractofile%.tck}_sift.tck" \
        -out_selection "${tractofile%.tck}_selection.txt"
done

# convert selection files (binary) to index files
for selection_file in $(ls ${PATH_TO_OUTPUT_FOLDER}/* | grep selection.txt)
do
    rf_streamline_indices_from_mrtrix_selection.py \
        "${selection_file}" \
        "${selection_file%_selection.txt}.trk" \
        "${selection_file%_selection.txt}"
done

# transform index files to reference index files
# (will convert indices from sub-tractogram to indices in the full tractogram
for i in ${BOOTSTRAP_IDS}
do
    rf_transform_indices_reference.py \
        "${PATH_TO_OUTPUT_FOLDER}/subset_${i}.json" \
        "${PATH_TO_OUTPUT_FOLDER}/subset_${i}_plausible_indices.json" \
        "${PATH_TO_OUTPUT_FOLDER}/subset_${i}_plausible_ref.json"
    rf_transform_indices_reference.py \
        "${PATH_TO_OUTPUT_FOLDER}/subset_${i}.json" \
        "${PATH_TO_OUTPUT_FOLDER}/subset_${i}_implausible_indices.json" \
        "${PATH_TO_OUTPUT_FOLDER}/subset_${i}_implausible_ref.json"
done

# discard subset tractogram files for efficient use of space
rm ${PATH_TO_OUTPUT_FOLDER}/*.trk
rm ${PATH_TO_OUTPUT_FOLDER}/*.tck

wait_commands ${running_commands[@]}
