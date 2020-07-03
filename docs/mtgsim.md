# Meeting-style audio simulation 

## 1. Generating long-form audio for diarization training

The following will generate a set of meeting-style audio files. 
```
./scripts/preprocess.sh  # Convert FLAC to WAV.
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

    Usage: run_meetings.sh [--split N] [--roomcfg FILE] [--dyncfg FILE] [--vad] [--save_image] [--save_channels_separately] [--help] dest-dir set

    Description: Preprocess the original LibriSpeech data.

    Args:
        dest-dir: Destination directory, relative to $EXPROOT/data.
        set: {train|dev|eval}, subset to process.

    Options:
        --split N                  : Split the data set into N subsets for parallel processing. N defaults to 32.
        --roomcfg FILE             : Room acoustics configuration file. FILE defaults to <repo-root>/configs/common/meeting_reverb.json.
        --dyncfg FILE              : Room acoustics configuration file. FILE defaults to <repo-root>/configs/common/meeting_dynamics.json.
        --vad                      : Use VAD-segmented signals. Not recommended.
        --save_image               : Save source images instead of anechoic signals and RIRs.
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


## 2. Using run_meeting.sh for utterance-mixture generation

The meeting simulation script, run_meeting.sh, can also be used to mix a few utterances by using configs/common/uttmix_dynamics.json as the speaker dynamics configuration file. 
```
./scripts/preprocess.sh  # Convert FLAC to WAV.
# Do simulation.
./scripts/run_meetings.sh --dyncfg ./configs/common/uttmix_dynamics.json SimLibriCSS-short-train train
./scripts/run_meetings.sh --dyncfg ./configs/common/uttmix_dynamics.json SimLibriCSS-short-dev dev
./scripts/run_meetings.sh --dyncfg ./configs/common/uttmix_dynamics.json SimLibriCSS-short-test test
```
Unlike run.sh, this does not truncate the original LibriSpeech utterances. Therefore, the generated data can also be used for ASR training. Also, note that this mixes utterances of up to three speakers. If you want to generate only 1- or 2-speaker signals, modify the "speakers_per_session" value in uttmix_dynamics.json. 

