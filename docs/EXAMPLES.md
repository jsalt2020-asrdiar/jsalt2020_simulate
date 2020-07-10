# Use Cases
The scripts under *scripts* directory print usage messages with *--help* option. They support various options, including *--split* to control the degree of parallelism.

Three typical use cases are described below. 
1. [Mixing truncated utterances](uttmix.md)
    - speech separation
2. [Long-form audio simulation](mtgsim.md)
    - speaker diarization
    - speech separation leveraging long acoustic context
    - joint speaker diarization and speech recognition
3. [Mixture of several untruncaed utterances](mtgsim.md)
    - speech separation
    - multi-talker ASR
    - bootstrapping the training for #2


## Changelog
- 7/10/2020
    - Fixed the high memory usage issue. 
    - **Reduced the default noise_points value to 8 to save computational cost. For most use cases, this will not affect the performance. However, if you want to use the previous set-up, change the value to 64.**


## General notes
- **It is advised that you do simulation on the test set first to see how the resultant audio files would look like before performing simulation on the training set, which usually takes much longer than doing so on the test set.**
- It is likely that the optimal simulation configurations differ across tasks. Therefore, too much emphasis is not put at this moment on cross-site data reproducibility, although it is currently being in the works. 


## Experiment reproducibility

**CAUTION: THE CHECKSUMS ARE NOT YET UPDATED TO REFLECT THE LATEST CHANGES!!! PLEASE IGNORE THIS SECTION FOR NOW. THERE WILL BE MULTIPLE ITERATIONS BEFORE WE CAN REALLY FINALIZE THE SIMULATION SETTINGS.**

When the default option values are used (including --split), the simulation tools should generate the same data. You can check if your data exactly match the standard ones as follows. 
- Utterance mixing
    ```
    ./scripts/check_data.sh $EXPROOT/data/SimLibriCSS-train/wav utt train
    ./scripts/check_data.sh $EXPROOT/data/SimLibriCSS-dev/wav utt dev
    ./scripts/check_data.sh $EXPROOT/data/SimLibriCSS-test/wav utt test
    ```
- Meeting-style simulation
    ```
    ./scripts/check_data.sh $EXPROOT/data/SimLibriCSS-train/wav mtg train
    ./scripts/check_data.sh $EXPROOT/data/SimLibriCSS-dev/wav mtg dev
    ./scripts/check_data.sh $EXPROOT/data/SimLibriCSS-test/wav mtg test
    ```


