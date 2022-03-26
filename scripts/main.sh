#!/usr/bin/env bash

# -- desc
# Main script for convenience. Allows to run all SIFT experiments for one subject,
#   one after another. An option is provided to run the experiment on sequential sets
#   of streamlines from a tractogram or randomized (rSIFT) s.t. the average streamline
#   is evaluated 5 times fo each subset size.
#
# -- args
#  BASE_PATH - path to folder with subject data
#     folder must contain tractogram (named all.trk) in trk format,
#     diffusion data (data.nii.gz, as downloaded from Human Connectome Project )
#     and FODs (WM_FODs.mif, as created following the descriptions on
#     https://doi.org/10.5281/zenodo.1477956)
#  RANDOMIZED - 0 for sequential, 1 for randomized.
#
# -- author 
# antoniabhain@gmail.com


if [ "${1}" == "--help" ] ; then
  echo "Main script for tractogram filtering experiment."
  echo "First argument: path to folder with subject data, must contain tractogram " \
       "(named all.trk) in trk format, diffusion data (data.nii.gz, as downloaded " \
       "from Human Connectome Project ) and FODs (WM_FODs.mif, as created following " \
       "the descriptions on https://doi.org/10.5281/zenodo.1477956)"
  echo "Second argument: 1 for randomized filtering (rSIFT), 0 for sequential filtering"
  exit 0
fi

BASE_PATH="${1}" # path with the tractogram
RANDOMIZED="${2}" # 0 for no (run sequential experiment), 1 for yes

# check if we want to do sequential case where every streamline (of 10M) is seen once
#  or randomized experiment with every streamline seen 5 times.
#  change appropriately if your tractogram contains != 10M streamlines or you want
#  more/less votes per streamlines
if [ "${2}" == "1" ] ; then
  NUM_STREAMLINES=50000000
else
  NUM_STREAMLINES=10000000
fi

# list of all subset sizes to use
SUBSET_SIZES=(10000000 5000000 2500000 1250000 625000 500000 250000)

EXP_IDS=$(seq 0 $((${#SUBSET_SIZES[@]}-1)))

for i in ${EXP_IDS}
do
  REPS=$(( NUM_STREAMLINES / SUBSET_SIZES[i] ))
  SIZE="${SUBSET_SIZES[$i]}"
  echo "starting experiment in $BASE_PATH, $REPS repetitions, " \
       "subset size ${SIZE} (randomized: ${RANDOMIZED})"
  bash -e sift_experiment.sh "${BASE_PATH}" "${RANDOMIZED}" "${REPS}" "${SIZE}" \
    "output_${SIZE}"
done
