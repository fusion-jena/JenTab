# Work Manager Service

Distributing tables as units of work and collecting the results, errors and audit records.

## Setup
### Docker 
```bash
docker-compose -f docker-compose.manager.yml up
```
### Native
If you run under a `linux` distribution, you can easily use the `gunicorn` command
```bash
gunicorn --config ./gunicorn.py --preload wsgi:app
```

If you run under `Windows` and you faced some errors with `gunicorn`, alternatively you can serve using `waitress`

```bash
waitress-serve --host 0.0.0.0 --port=5100 wsgi:app
```

## Endpoints

### `POST /getWork`

Retrieve a new package of work.

**Parameters**
* `client` ... GUID for the requesting client.

**Output**
```JSON
{
  "name": "ABCDEF",
  "orientation": "Horizontal",
  "targets": {
    "cea": [{
      "sub_id": 0,
      "obj_id": 1,
      "mapped": "http://..."
    }, ... ],
    "cpa": [{
      "row_id": 0,
      "col_id": 1,
      "mapped": "http://..."
    }, ...],
    "cta": [ 0, ... ]
  },
  "header": [ "col0", "col1", ... ],
  "data":   [ [], [], ... ],
}
```

**Errors**
* 401

### `PUT /storeResult/<table>/` and `PUT /storeError/<table>/`

Store the result or resulting error for a given table. The full body of the request will be stored in the corresponding file.

`client` parameter should be part of the URL (GET-parameter).

**Parameters**
* `client` ... GUID for the requesting client.
* `<body>` ... contents to be stored

**Output**
* 200

**Errors**
* 401
* 404
* 410

## Errors

* 401 Unauthorized ... missing client ID
* 404 Not Found ... the corresponding assignment could not be found
* 410 Gone ... no more work is available

## Maintenance
A way to rest tables with issues to be re-processed by clients. You can find this module under `maintenance` dir. We provide 4 options
1. `resetErrors.py` rest tables that appear in errors. aka. no results found for those.
2. `resetFullMissCea.py` reset tables with no successfull creation of CEA task.
3. `resetPartialMissCea.py` reset tables with partial CEA mappings.
4. `manualTables.py` reset tables that exists under *manualTables* dir (your own choice).

## Other Features
Besides the main endpoint, GUI shows the following: 
* Coverage of the data per task.
* Processed vs. remaining tables
* The number of connected clients/runner.
* Estimated time until complete the remaining tables.
* Fetch Missing mapping (button), it retrieves a current snipet of the dataset, shows tables with no/missing mappings for the 3 tasks.
* Fetch Audit (button), retrieve the audit records in the creation and selection phases.
  