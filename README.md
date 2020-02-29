# Introduction 
The aim of this project is to provide a set of tools for generating training data for speech separation models. 

## Prerequisites
The following Python packages need to be installed in advance. 
- webrtcvad
- PySoundFile
- resampy
- pyrirgen
  - Linux: https://github.com/Marvin182/rir-generator
  - Windows: https://github.com/ty274/rir-generator)

## Steps
1. Download train-clean-100.tar.gz and train-clean360.tar.gz of LibriSpeech from http://www.openslr.org/12/, untar them, and put the generated directories, train-clean-100 and train-clean-360, under a single directory. 
2. Preprocess the orignal files (i.e., convert to WAV and remove silence). 
```
./scripts/preprocess.sh
```
Be sure to edit the directory names in this script. 
3. Run the following script to generate multi-channel speech mixture files. 
```
./scripts/run.sh
```
