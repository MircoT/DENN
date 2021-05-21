# ⚠️ This repository is archived ⚠️

## TensorFlow version

Since version 0.12 is not necessary compile the library from source on MacOS. This is also for linux version but with an additional dependency.

To build the op for the official binary package simply use `make`, otherwise use the command `make OFFICIAL_BINARY=false`.

## TIPS

Search for symlinks:

```
# search
objdump -t DENN/DENNOp.so
# filter
objdump -t DENN/DENNOp.so | grep CheckOpMessageBuilder
# demangling
objdump -t DENN/DENNOp.so | grep CheckOpMessageBuilder | c++filt
# Search in whole folder
find -name '*.a' | xargs -t -n 1 objdump -t | grep something
```

## Build notes

* `C_FLAGS += -lprotobuf` is necessary because of `::tensorflow::protobuf::TextFormat::ParseFromString`, otherwise some functions will not be available

## Example benchmark test

```json
[
    {
        "name": "iris_dataset",
        "dataset_file": "./datasets/iris_15-B_5s.gz",
        "TOT_GEN": 1000,
        "GEN_STEP": 50,
        "TYPE": "double",
        "F": 0.8,
        "NP": 20,
        "de_types": [
            "rand/1/bin"
        ],
        "CR": 0.5,
        "levels": [
            {
                "shape": [[4,3], [3]],
                "init": [
                    {
                        "fx": {
                            "name": "random_uniform",
                            "kwargs": {
                                "seed": 1,
                                "minval": -1.0, 
                                "maxval": 1.0
                            }
                        }
                    },
                    [0.5, 0.5, 0.5]
                ],
                "preferred_device": "CPU",
                "fx": {
                    "name": "nn.softmax_cross_entropy_with_logits"
                }
            }
        ]
    }
]
```

## Execution

```bash
cd scripts
python benchmark.py config/configfile.json
```

You will find in the graph folder the exported graph. Open it with TensorBoard.
