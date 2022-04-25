## Run parser

```
PYTHONPATH='.' python3 parser/main.py --input_dir ~/Yandex.Disk.localized/NL/PS  --datasets_path ~/pokerai-master/data/datasets --nicknames_path ~/pokerai-master/data/nicknames.txt
```

* input_dir - directory with directories which contains zip archives
* nicknames_path - Path to filename with top players nick names
* datasets_path - directory with resulting datasets. Parser produces one dataset per input file.

## Merge resulting datasets

```
import os
import shutil

filenames = os.listdir('/Users/shulgin/pokerai-master/data/datasets')

with open('/Users/shulgin/pokerai-master/data/dataset.tmp.csv', 'wb') as outfile:
    for filename in filenames:
        with open(os.path.join('/Users/shulgin/pokerai-master/data/datasets', filename), 'rb') as readfile:
            shutil.copyfileobj(readfile, outfile)
```

```
export DSNAME=dataset.bb.csv &&  head -n 1 dataset.tmp.csv >> $DSNAME && sed '/hand_id,player_name,street/d' dataset.tmp.csv >> $DSNAME
```