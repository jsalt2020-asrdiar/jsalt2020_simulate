# Multi-channel speech separation training using the original LibriCSS paper configuration

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

    Usage: run.sh [--split N] [--cfg FILE] [--times N] [--subsample X] [--onespkr X] [--save_channels_separately] [--vad] [--save_image] [--help] dest-dir set

    Description: Reverberate, mix, and noise-corrupt speech signals.

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


## Notes
- It is important to note that this simulation scheme trims the original LibriSpeech utterances so that the length of the resultant mixture signals does not exceed a certain threshold (10 seconds by default). Therefore, this is supposed to be used only for separation model training. It is also noteworthy that a similar configuration was found to be helpful in prior investigation [2].
- (7/2/20) The default behavior has been changed to save the RIRs and anechoic signals instead of the microphone images. If you want to save the microphone images, add --save_imave option. 
- Refer to materials/conv_sample/conv_sample.py to see how to re-synthesize microphone signals based on the RIRs and anechoic signals. 





## References

[1] Z. Chen, T. Yoshioka, L. Lu, T. Zhou, Z. Meng, Y. Luo, J. Wu, X. Xiao, J. Li, "Continuous Speech Separation: Dataset and Analysis," 2020 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), Barcelona, Spain, 2020, pp. 7284-7288, doi: 10.1109/ICASSP40776.2020.9053426.

[2] T. Yoshioka, H. Erdogan, Z. Chen and F. Alleva, "Multi-Microphone Neural Speech Separation for Far-Field Multi-Talker Speech Recognition," 2018 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), Calgary, AB, 2018, pp. 5739-5743, doi: 10.1109/ICASSP.2018.8462081.

