These notes won't be helpful for users. 

### Generating MD5 checksums

The checksum files were generated as follows. 
```
./scripts/utils/gen_md5.sh $EXPROOT/SimLibriUttmix-train/wav materials/md5sum/v0.0.1/utt-train.txt
./scripts/utils/gen_md5.sh $EXPROOT/data/SimLibriUttmix-dev/wav materials/md5sum/v0.0.1/utt-dev.txt
./scripts/utils/gen_md5.sh $EXPROOT/data/SimLibriUttmix-test/wav materials/md5sum/v0.0.1/utt-test.txt

./scripts/utils/gen_md5.sh $EXPROOT/SimLibriCSS-train/wav materials/md5sum/v0.0.1/mtg-train.txt
./scripts/utils/gen_md5.sh $EXPROOT/data/SimLibriCSS-dev/wav materials/md5sum/v0.0.1/mtg-dev.txt
./scripts/utils/gen_md5.sh $EXPROOT/data/SimLibriCSS-test/wav materials/md5sum/v0.0.1/mtg-test.txt
```

