# Use Cases
The scripts under *scripts* directory print usage messages with *--help* option. They support various options, including *--split* option to control the degree of parallelism.

Three typical use cases are described below. 
1. [Mixture of truncated utterances](#Multi-channel-speech-separation-training-using-the-configuration-of-the-original-LibriCSS-paper)
    - speech separation
2. [Long-form audio simulation](#Meeting-style-audio-simulation-for-diarization-module-training)
    - speaker diarization
    - speech separation leveraging long acoustic context
    - multi-talker ASR possibly with speaker diarization
3. [Mixture of several untruncaed utterances](#Mixing-a-few-untruncated-utterances)
    - speech separation
    - multi-talker ASR
    - bootstrapping the training for #2


## General notes
- **It is advised that you do simulation on the test set first to see how the resultant audio files would look like before performing simulation on the training set, which usually takes much longer than doing so on the test set.**
- It is likely that the optimal simulation configurations differ across tasks. Therefore, too much emphasis is not put at this moment on cross-site data reproducibility, although it is currently being in the works. 



## Multi-channel speech separation training using the configuration of the original LibriCSS paper

The separation model training data used in [1] can be generated as follows. 
You may want to modify configs/cmd.sh, depending on the queueing system you're using. 
```
./scripts/preprocess.sh  # Convert FLAC to WAV; remove silence. 
# Do simulation. 
./scripts/run.sh --vad SimLibriUttmix-train train
./scripts/run.sh --vad SimLibriUttmix-dev dev
./scripts/run.sh --vad SimLibriUttmix-test test
```
The results are generated under $EXPROOT/SimLibriUttmix-{train,dev,test}, where EXPROOT is defined in path.sh. 
Look for a file named mixlog.json under the result directory to see how each simulated audio segment was created.  


Also, the execution script supports the following options. 
```
$ ./scripts/run.sh --help

    ''
    < run.sh >

    Usage: run.sh [--split N] [--cfg FILE] [--times N] [--subsample X] [--onespkr X] [--save_channels_separately] [--vad] [--save_anechoic] [--help] dest-dir set

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
        --save_image               : Save source images instead of anechoic signals and RIRs.
        --save_channels_separately : Save each output channel separately.
        --help                     : Show this message.
    ''
```


### Notes
- It is important to note that this simulation scheme trims the original LibriSpeech utterances so that the length of the resultant mixture signals does not exceed a certain threshold (10 seconds by default). Therefore, this is supposed to be used only for separation model training. It is also noteworthy that a similar configuration was found to be helpful in prior investigation [2].
- (7/2/20) The default behavior has been changed to save the RIRs and anechoic signals instead of the microphone images. If you want to save the microphone images, add --save_imave option. 
- Refer to materials/conv_sample.conv_sample.py to see how to re-synthesize microphone signals based on the RIRs and anechoic signals. 




## Meeting-style audio simulation for diarization module training

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
        - With these settings, each resultant session tends to last for 1-3 minutes. 
- The current configuration was determined based on this doc https://docs.google.com/document/d/13WJvQAnYBj9n-7jSotqVvflYUqaZuUnL/edit?ts=5ef2b658 as well as the feedback received. 
- Two things must be noted regarding the overlap time ratio. 
    - Each utterance of the original LibriSpeech corpus is assumed not to contain silence for simplicity, which is not actually true. Ideally, the overlap time ratio should be calculated based on forced alignment results. This is currently put in the backlog. 
    - The actual overlap time ratio can be lower than the target overlap time ratio due to the variation of the utterance lengths. For example, imagine mixing a 20-s utterance and a 5-s utterance. The overlap time ration cannot be greater than 5/20=0.25. 



## Mixing a few untruncated utterances

TBD.



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




## References

[1] Z. Chen, T. Yoshioka, L. Lu, T. Zhou, Z. Meng, Y. Luo, J. Wu, X. Xiao, J. Li, "Continuous Speech Separation: Dataset and Analysis," 2020 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), Barcelona, Spain, 2020, pp. 7284-7288, doi: 10.1109/ICASSP40776.2020.9053426.

[2] T. Yoshioka, H. Erdogan, Z. Chen and F. Alleva, "Multi-Microphone Neural Speech Separation for Far-Field Multi-Talker Speech Recognition," 2018 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), Calgary, AB, 2018, pp. 5739-5743, doi: 10.1109/ICASSP.2018.8462081.

