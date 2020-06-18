# Use Cases
The scripts under *scripts* directory print usage messages with *--help* option. They support various options, including *--split* option to control the degree of parallelism.


## 1. Multi-channel speech separation model training

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

    Usage: run.sh [--split N] [--cfg FILE] [--onespkr X] [--vad] [--help] dest-dir set

    Description: Preprocess the original LibriSpeech data.

    Args:
        dest-dir: Destination directory, relative to $EXPROOT/data.
        set: {train|dev|eval}, subset to process.

    Options:
        --split N   : Split the data set into N subsets for parallel processing. N defaults to 32.
        --cfg FILE  : Simulation configuration file. FILE defaults to <repo-root>/configs/2mix_reverb_stanoise.json.
        --onespkr X : Probability with which a purely single speaker sample is generated.
        --vad       : Use VAD-segmented signals.
        --help      : Show this message.
    ''
```

## 2. Meeting-style audio simulation

The following will generate a set of meeting-style audio files, each consisting of three speakers each with three utterances. There are some sessions that have fewer speakers because the number of utterances per speaker is not uniform in the LibriSpeech training set. 
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

    Usage: run_meetings.sh [--split N] [--vad] [--help] dest-dir set

    Description: Preprocess the original LibriSpeech data.

    Args:
        dest-dir: Destination directory, relative to $EXPROOT/data.
        set: {train|dev|eval}, subset to process.

    Options:
        --split N: Split the data set into N subsets for parallel processing. N defaults to 32.
        --cfg FILE  : Room acoustics configuration file. FILE defaults to <repo-root>/configs/meeting_reverb.json.
        --overlap X : Overlap time ratio, which defaults to 0.3.
        --utt-per-spkr N : Number of utterances per speaker in each session, which defaults to 3.
        --spkr-per-sess N : Number of speakers per session, which defaults to 3.
        --vad       : Use VAD-segmented signals.
        --help      : Show this message.
    ''
```
