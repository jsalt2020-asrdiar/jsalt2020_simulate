# jsalt2020-simulate
This repository provides a set of tools for generating training data for speech enhancement, speech separation, multi-talker speech recognition, and speaker diarization by simulation. Simulated development and evaluation sets can also be created. 

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

3. Download and untar the LibriSpeech corpus from http://www.openslr.org/12/, untar them, which can be performed with the following script. 
    ```
    ./download.sh
    ```


## Examples

See [EXAMPLES.md](EXAMPLES.md).

## Plan

See [TODO.md](TODO.md). 


## References

[1] Z. Chen, T. Yoshioka, L. Lu, T. Zhou, Z. Meng, Y. Luo, J. Wu, X. Xiao, J. Li, "Continuous Speech Separation: Dataset and Analysis," ICASSP 2020 - 2020 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), Barcelona, Spain, 2020, pp. 7284-7288, doi: 10.1109/ICASSP40776.2020.9053426.
