# Introduction 
This repository provides a set of tools for generating training data for speech enhancement and separation models. 

## Prerequisites

### Automatic installation

Run the following commands to set up an environment. 
```
conda env create -f environment.yml  # Create a conda environment with all dependencies, except for pyrirgen, installed. 
conda activate jsalt2020_simulate
./install.sh <your-data-dir>  # Specify the location where you want the data to be stored.
source ./path.sh  # This is created by install.sh. 
./download.sh  # Download the clean subset of LibriSpeech. 
```


### Manual installation

1. The following Python packages need to be installed in advance. 
- webrtcvad
- PySoundFile
- resampy
- pyrirgen (https://github.com/Marvin182/rir-generator)

2. Create path.sh with the following line. 
```
export EXPROOT=<your-data-dir>
```

3. Download train-clean-100.tar.gz and train-clean360.tar.gz of LibriSpeech from http://www.openslr.org/12/, untar them, and put the generated directories, train-clean-100 and train-clean-360, under a single directory. This can be done by running the following script. 
```
./download.sh
```


## Examples

### Multi-channel speech separation model training

[1] Z. Chen, T. Yoshioka, L. Lu, T. Zhou, Z. Meng, Y. Luo, J. Wu, X. Xiao, J. Li, "Continuous Speech Separation: Dataset and Analysis," ICASSP 2020 - 2020 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), Barcelona, Spain, 2020, pp. 7284-7288, doi: 10.1109/ICASSP40776.2020.9053426.

The following recipe generates the separation model training data used in [1]. 

1. Preprocess the orignal files (i.e., convert to WAV and remove silence). 
    ```
    ./scripts/preprocess.sh
    ```
    Be sure to edit the directory names in this script. 

    You may also want to modify configs/cmd.sh depending on the queueing system you are using. 

2. Run the following script to generate multi-channel speech mixture files. 
    ```
    ./scripts/run.sh
    ```



## Plan

The following is a list of things that are desired to be added. 
- Generating "meeting-ish" signals to support the SSD work. 
- Add pyroomacoustics as an RIR generation engine. 



