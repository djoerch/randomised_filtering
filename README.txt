############
## README ## 
############

Installation Instructions
-------------------------

Please first make sure that Python 3.8 and Anaconda (https://www.anaconda.com/products/individual#linux) are installed, and that conda is exported to your PATH 

To set up the environment and install all necessary dependencies and software, use the following steps:

apt install python3.8-venv
python3 -m venv randomized_filtering
source randomized_filtering/bin/activate
python3 -m pip install -r requirements.txt
conda install -c mrtrix3 mrtrix3
wget https://github.com/scilus/scilpy/archive/master.zip
unzip master.zip
rm master.zip
pip install -e scilpy-master


Data
----
Data must be downloaded from the Human Connectome Project Website (https://www.humanconnectome.org/study/hcp-young-adult), which requires (free) registration.

Afterwards, tractograms can be created in the following way: https://zenodo.org/record/1477956#.YVTb3jqxU5l
For streamline compression, please use the Dipy function (https://dipy.org/documentation/1.4.1./reference/dipy.tracking/#dipy.tracking.benchmarks.bench_streamline.compress_streamlines) with tol_error=0.35


---

Descriptions on how to use each script is commented into the code, as well as indications on who is/are the code's author(s).

Author: Antonia Hain (s8anhain@stud.uni-saarland.de)


