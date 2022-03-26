# Randomised Filtering

This repository provides the code for the experiments on the method called
_randomized SIFT_ (rSIFT) as described in

A. Hain, D. Jörgens, R. Moreno,
"_Assessing Individual Streamline Plausibility
Through Randomized Spherical-Deconvolution Informed Tractogram Filtering_",
manuscript submitted, 2022.

## Installation Instructions

#### Dependencies

Make sure that the following dependencies are installed:
 - Python 3.8
 - `mrtrix3` (follow instructions at
    https://mrtrix.readthedocs.io/en/latest/index.html)
 - `scilpy` (follow instructions at https://github.com/scilus/scilpy)

#### Installation

Create a virtual environment using by:
```
virtualenv -p $(which python3) <path_to_environment>
```

Then, install the package in the activated environment:
```
source <path_to_environment>/bin/activate
pip install -e <path_to_randomised_filtering_repo>
```

After that, the **python** scripts in the `scripts` folder will be available through
autocompletion in the command line whenever the virtual environment is activated.

## Data

 - Data must be downloaded from the Human Connectome Project website at 
   https://www.humanconnectome.org/study/hcp-young-adult.
 - Tractograms can be created following the description at
   https://zenodo.org/record/1477956#.YVTb3jqxU5l
 - For streamline compression, use the Dipy function `compress_streamlines`
   with tol_error=0.35
   (https://dipy.org/documentation/1.4.1./reference/dipy.tracking/#dipy.tracking.streamline.compress_streamlines)


## How to use

The script `sift_experiment.sh` is the anchor and launches all commands for one rSIFT
experiment. The individual scripts `rf_*` can be launched individually, too. Each
provides a brief help text when invoked with the option `-h`.

The collection of different rSIFT experiments (with different parameters) can be
launched using the script `main.sh`.
