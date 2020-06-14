# jsalt2020-simulate
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
    - [pyrirgen](https://github.com/Marvin182/rir-generator)

2. Create path.sh with the following line. 
    ```
    export EXPROOT=<your-data-dir>
    ```

3. Download train-clean-100.tar.gz and train-clean360.tar.gz of LibriSpeech from http://www.openslr.org/12/, untar them, and put the generated directories, train-clean-100 and train-clean-360, under a single directory. This can be done by running the following script. 
    ```
    ./download.sh
    ```


## Examples

### 1. Multi-channel speech separation model training

[1] Z. Chen, T. Yoshioka, L. Lu, T. Zhou, Z. Meng, Y. Luo, J. Wu, X. Xiao, J. Li, "Continuous Speech Separation: Dataset and Analysis," ICASSP 2020 - 2020 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), Barcelona, Spain, 2020, pp. 7284-7288, doi: 10.1109/ICASSP40776.2020.9053426.

The separation model training data used in [1] can be generated as follows. 
You may want to modify configs/cmd.sh, depending on the queueing system you're using. 
```
./scripts/preprocess.sh  # Convert FLAC to WAV; remove silence. 
./scripts/run.sh  # Do simulation. 
```

### 2. Meeting-style audio simulation

The following will generate a set of meeting-style audio files, each consisting of three speakers each with three utterances. There are some sessions that have fewer speakers because the number of utterances per speaker is not uniform in the LibriSpeech training set. 
```
./scripts/preprocess.sh  # Convert FLAC to WAV; remove silence. 
./scripts/run_meetings.sh  # Do simulation. 
```


## Plan

See [TODO.md](TODO.md). 
