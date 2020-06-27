# Use Cases
The scripts under *scripts* directory print usage messages with *--help* option. They support various options, including *--split* option to control the degree of parallelism.


## 1. Multi-channel speech separation model training (mixtures of a few utterances)

The separation model training data used in [1] can be generated as follows. 
You may want to modify configs/cmd.sh, depending on the queueing system you're using. 
```
./scripts/preprocess.sh  # Convert FLAC to WAV; remove silence. 
# Do simulation. 
./scripts/run.sh SimLibriUttmix-train train
./scripts/run.sh SimLibriUttmix-dev dev
./scripts/run.sh SimLibriUttmix-test test
```

The execution script supports the following options. 
```
$ ./scripts/run.sh --help

    ''
    < run.sh >

    Usage: run.sh [--split N] [--cfg FILE] [--times N] [--subsample X] [--onespkr X] [--vad] [--save_channels_separately] [--save_anechoic] [--help] dest-dir set

    Description: Preprocess the original LibriSpeech data.

    Args:
        dest-dir: Destination directory, relative to $EXPROOT/data.
        set: {train|dev|eval}, subset to process.

    Options:
        --split N                  : Split the data set into N subsets for parallel processing. N defaults to 32.
        --cfg FILE                 : Simulation configuration file. FILE defaults to <repo-root>/configs/2mix_reverb_stanoise.json.
        --times N                  : Each utterance is used N times. This could be used for data augmentation. N defaults to 1.
        --subsample X              : Use X*100 % of the files.
        --onespkr X                : Probability with which a purely single speaker sample is generated.
        --vad                      : Use VAD-segmented signals.
        --save_channels_separately : Save each output channel separately.
        --save_anechoic            : Save anechoic signals and RIRs.
        --help                     : Show this message.
    ''
```

## 2. Meeting-style audio simulation

The following will generate a set of meeting-style audio files. 
```
./scripts/preprocess.sh  # Convert FLAC to WAV; remove silence. 
# Do simulation.
./scripts/run_meetings.sh SimLibriCSS-train train 
./scripts/run_meetings.sh SimLibriCSS-dev dev 
./scripts/run_meetings.sh SimLibriCSS-test test 
```

The execution script supports the following options. 
```
$ ./scripts/run_meetings.sh --help

    ''
    < run_meetings.sh >

    Usage: run_meetings.sh [--split N] [--roomcfg FILE] [--dyncfg FILE] [--vad] [--help] dest-dir set

    Description: Preprocess the original LibriSpeech data.

    Args:
        dest-dir: Destination directory, relative to $EXPROOT/data.
        set: {train|dev|eval}, subset to process.

    Options:
        --split N                  : Split the data set into N subsets for parallel processing. N defaults to 32.
        --roomcfg FILE             : Room acoustics configuration file. FILE defaults to <repo-root>/configs/common/meeting_reverb.json.
        --dyncfg FILE              : Room acoustics configuration file. FILE defaults to <repo-root>/configs/common/meeting_dynamics.json.
        --vad                      : Use VAD-segmented signals.
        --save_channels_separately : Save each output channel separately.
        --help                     : Show this message.
    ''
```

### Notes on the meeting simulation configurations
- The room acoustics and speaker dynamics (i.e., how to arrange different utterances of different speakers to form sessions) are configured by the files specified with --roomcfg and --dyncfg, respectively. 
    - For the room acoustics, there are three template configuration files under configs/common. 
        - meeting_clean.json: single-channel output, no reverberation and noise. This may be used for verification purposes. 
        - meeting_reverb_mono.json: single-channel output, both reverberation and stationary noise added. If you don't need multi-channel audio, you could use this version. This is much faster than the multi-chanel simulation. 
        - meeting_reverb.json (default): 7-channel output, both reverberation and stationary diffuse noise added. 
    - For the speaker dynamics configuration, you can find one file, named meeting_dynamics.json, under configs/common. This uses the following settings which would be suitable for diarization learning. 
        - The number of speakers per session ranges from 2 to 8. 
        - Each session consists of 12 to 18 utterances.
        - Overlap time ratio is randomly picked from 0 to 0.3 s. 
        - Silence is randomly inserted between neighboring utterances with a probability of 0.1. 
- The current configuration was determined based on this doc https://docs.google.com/document/d/13WJvQAnYBj9n-7jSotqVvflYUqaZuUnL/edit?ts=5ef2b658 as well as feedback from Zili (thanks Zili). 



## 3. Experiment reproducibility

**CAUTION: THE CHECKSUMS ARE NOT YET UPDATED TO REFLECT THE LATEST CHANGES!!! PLEASE IGNORE THIS SECTION FOR NOW. THERE WILL BE MULTIPLE ITERATIONS BEFORE WE CAN REALLY FINALIZE THE SIMULATION SETTINGS.**

When the default option values are used (including --split), the simulation tools should generate the same data. You can check if your data exactly match the standard ones as follows. 
- Utterance mixing
    ```
    ./scripts/check_data.sh $EXPROOT/data/SimLibriCSS-test/wav utt train
    ./scripts/check_data.sh $EXPROOT/data/SimLibriCSS-test/wav utt dev
    ./scripts/check_data.sh $EXPROOT/data/SimLibriCSS-test/wav utt test
    ```
- Meeting-style simulation
    ```
    ./scripts/check_data.sh $EXPROOT/data/SimLibriCSS-test/wav mtg train
    ./scripts/check_data.sh $EXPROOT/data/SimLibriCSS-test/wav mtg dev
    ./scripts/check_data.sh $EXPROOT/data/SimLibriCSS-test/wav mtg test
    ```

CAUTION: The current implementation does not ensure repoducibility when the --split value is changed because the random seed is initialized for each process!!!



