# Generating `schema.json`

1. schema.fbs -> schema.bfbs

    ```sh
    flatc -o output --binary --schema schema.fbs
    ```

2. reflection.fbs + schema.bfbs -> schema.json

    ```sh
    flatc -o output --strict-json --json reflection.fbs -- output/schema.bfbs
    ```

4. you now have `output/schema.json`