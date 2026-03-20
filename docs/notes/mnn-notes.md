
- Copy all schema files to `pwd`.
- Copy the mnn file to `pwd`.
- Run the following:

```
flatc --raw-binary --json -o output -- MNN.fbs -- yolov5su.mnn
```

The resulting json will be in a new folder called `output`.
