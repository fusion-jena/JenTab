# Generic Lookup Service

* Provides access to a prepopulated cache for label to candidate mappings.

## Quick Setup 

* ```hypercorn main:app -c python:asgi_config.py```

## Endpoints

| Name            | Type | Data   (type)              | Description |
|-----------------|------|-----------                 |----------------|
| look_for        | POST | needle (string)            | looks up in the cache for a single query element given by "**needle**"|
| look_for_lst    | POST | needles (list of strings)  | hits the Wikidata lookup API given a list of queries "**needles**" |


Term(s) has to be provided form-encoded using the parameter `text`.

**Output format**

* Provided input terms are used as keys in a dictionary.
* Each term might have multiple mappings

```json
{
  "[term]": [{
    "label": "Label of the entitiy",
    "uri":   "URI of the respective entity"
  }, ...
  ]
}
```

## Configuration
| Name                  | Default | Description                                                                |
|-----------------------|---------|----------------------------------------------------------------------------|
| CACHE_PATH | under assets folder, check [config.py](/config.py)       | Defines where the precomupted database should be accessed "lookup.db3" |

* More information about how the precomputed Generic_lookup database, please refer to our paper(s)
* More information about `assets` structure, check [assets/README.md](https://github.com/fusion-jena/JenTab/tree/main/assets)
* To download the lookup.db3, [check here](https://github.com/fusion-jena/JenTab_precomputed_lookup).
