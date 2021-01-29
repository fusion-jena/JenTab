# Wikidata Lookup Service

This service provides the proxy to Wikidata's search API.

## Endpoints

| Name            | Type | Data   (type)            | Description |
|-----------------|------|-----------               |----------------|
| look_for        | POST | text (string)            | looks up the Wikidata lookup API for a single query element given by "**text**"|
| look_for_lst    | POST | texts (list of strings)  | hits the Wikidata lookup API given a list of queries "**texts**" |


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

Environment variables for configuration (can also be set via docker-compose.yml):

| Name                  | Default | Description                                                                |
|-----------------------|---------|----------------------------------------------------------------------------|
| MAX_PARALLEL_REQUESTS | 5       | maximum number of parallel requests. Used to prevent IP-bans from Wikidata |
| DEFAULT_DELAY         | 10      | default delay upon HTTP error (429, 500, ...); in seconds                  |
| MAX_RETRIES           | 5       | maximum number of retries upon HTTP errors                                 |
| CACHE_DISABLED        | False   | disabled caching of Wikidata responses                                     |
