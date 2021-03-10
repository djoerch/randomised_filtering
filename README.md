# Randomised Filtering

### Setup

Make a python environment with
```
virtualenv -p $(which python3) <path_to_virtual_env_root_folder>
```

Then activate the environment with
```
source <path_to_virtual_env_root_folder>/bin/activate
```
and install the repo with
```
pip install -e <path_to_randomised_filtering_repo>
```

After that the scripts in the `scripts` folder will be available with autocompletion
whenever the virtual environment is activated.

### Bash script

The bash script is not installed in the virtual environment and should be called
separately with `bash randomised_sift_experiment.sh`. (However, it could be modified to
take command line arguments if needed.)

# How to use

The script `randomised_sift_experiment.sh` is the anchor and launches all necessary
commands. The individual scripts `rf_*` can be launched individually, too. Each
provides a brief help text when invoked with the option `-h`.