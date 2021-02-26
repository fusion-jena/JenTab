# Runner
 
* Client Service communicates all other individual services. 

## How it works?
* Retrieves new work package, i.e., table from `Manager`.
* Preprocess it using chain of calls to `CleanCells`, `Language Prediction` and `Type Prediction`
* Submit the processed version of the table to `Approach`
* Submit results/error to the `Manager`

## Configuration

| Name                  | Default | Description                                                                |
|-----------------------|---------|----------------------------------------------------------------------------|
| manager_url | 'http://127.0.0.1:5100'      | Manager URL|
| USER_NAME | 'YouManagerUsername'      | Username to access manager|
| USER_PASSWORD | 'YouManagerPassword'      | password to access manager|
| BATCH_SIZE | 500      |  If a column is too long, use this value to batch processing it. Used in prepareData|
| client_id | newid      | # identifier for this runner node|
