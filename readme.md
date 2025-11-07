# Django, OpenSearch, Prometheus, and Grafana Performance Project

This project integrates Django with **OpenSearch**, **PostgreSQL**, **Prometheus**, and **Grafana** to analyze the performance of different search operations and expose real-time metrics.  

It also includes full support for **remote debugging** in VSCode within a **Docker Compose** environment..  


---


## General Structure


The environment includes the following services defined in `docker-compose.yml`:  



| Service --> Local Port --> Description  
|-----------|---------------|-------------|  
| **Django (App)** --> `8000` --> Main API application |  
| **PostgreSQL** --> `5435` --> Relational database |  
| **OpenSearch** --> `9200` --> Distributed search engine |  
| **OpenSearch Dashboards** --> `5601` --> Web interface for OpenSearch |  
| **Prometheus** --> `9090` --> Metrics monitoring |  
| **Grafana** --> `3000` --> Dashboard visualization |  


---


## Environment Setup


### Prerequisites
Make sure you have installed:  
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/)
- [Visual Studio Code](https://code.visualstudio.com/)


---


### Launching the Environment


Run the following command from the project root:  

docker compose up --build  

This will:  
Build the Django image  
Launch all containers (Postgres, OpenSearch, Prometheus, Grafana)  
Automatically apply Django migrations  
If DEBUG_MODE=True, it will wait for the VSCode debugger to attach  


Debug:  

```
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Attach Django (Docker)",
      "type": "python",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      },
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}",
          "remoteRoot": "/app"
        }
      ],
      "django": true,
      "justMyCode": false
    }
  ]
}
```


Monitoring and Metrics  
| Service               | Local URL                                                                               |  
| --------------------- | --------------------------------------------------------------------------------------- |  
| Django                | [http://localhost:8000](http://localhost:8000)                                          |  
| Django metrics        | [http://localhost:8000](http://localhost:8000/metrics)                                  |  
| OpenSearch            | [http://localhost:9200](http://localhost:9200)                                          |  
| OpenSearch Dashboards | [http://localhost:5601](http://localhost:5601)                                          |  
| Prometheus            | [http://localhost:9090](http://localhost:9090)                                          |  
| Grafana               | [http://localhost:3000](http://localhost:3000) (user: `admin` / pass: `admin`         ) |  


---


## Grafana Dashboard — “OpenSearch Performance”

Below is a complete **dashboard JSON** you can import directly into Grafana.  

This dashboard includes the following panels:  

| Panel                         | Metric                           | Description                                      |  
| ----------------------------- | -------------------------------- | ------------------------------------------------ |  
| 🔹 `Get by ID Duration`       | `opensearch_get_by_id_seconds`   | Time in milliseconds for queries by `_id`.       |  
| 🔹 `Search Duration`          | `opensearch_search_seconds`      | Average duration of general searches (`search`). |  
| 🔹 `Template Search Duration` | `opensearch_template_seconds`    | Average duration of Mustache template searches.  |  
| 🔹 `Documents Returned`       | `opensearch_search_result_count` | Number of documents returned per query.          |  


---


### How to Import the Dashboard

1. Go to Grafana at http://localhost:3000  
User: admin | Password: admin  


2. After connecting Grafana to Prometheus, go to:  
Dashboards → + Import  


3. Paste the following JSON into the text box and click **Load**.  


---

### Dashboard JSON

```
json
{
"id": null,
"title": "OpenSearch Performance Dashboard",
"tags": ["opensearch", "performance", "django"],
"timezone": "browser",
"schemaVersion": 39,
"version": 1,
"refresh": "5s",
"panels": [
 {
   "type": "timeseries",
   "title": "OpenSearch - Get by ID Duration (ms)",
   "targets": [
     {
       "expr": "rate(opensearch_get_by_id_seconds_sum[1m]) / rate(opensearch_get_by_id_seconds_count[1m]) * 1000",
       "legendFormat": "get_by_id"
     }
   ],
   "datasource": { "type": "prometheus", "uid": "prometheus" },
   "fieldConfig": {
     "defaults": {
       "unit": "milliseconds",
       "decimals": 2,
       "color": { "mode": "palette-classic" }
     }
   }
 },
 {
   "type": "timeseries",
   "title": "OpenSearch - Search Duration (ms)",
   "targets": [
     {
       "expr": "rate(opensearch_search_seconds_sum[1m]) / rate(opensearch_search_seconds_count[1m]) * 1000",
       "legendFormat": "search"
     }
   ],
   "datasource": { "type": "prometheus", "uid": "prometheus" },
   "fieldConfig": {
     "defaults": {
       "unit": "milliseconds",
       "decimals": 2,
       "color": { "mode": "palette-classic" }
     }
   }
 },
 {
   "type": "timeseries",
   "title": "OpenSearch - Template Duration (ms)",
   "targets": [
     {
       "expr": "rate(opensearch_template_seconds_sum[1m]) / rate(opensearch_template_seconds_count[1m]) * 1000",
       "legendFormat": "template"
     }
   ],
   "datasource": { "type": "prometheus", "uid": "prometheus" },
   "fieldConfig": {
     "defaults": {
       "unit": "milliseconds",
       "decimals": 2,
       "color": { "mode": "palette-classic" }
     }
   }
 },
 {
   "type": "stat",
   "title": "Documents Returned (Last Query)",
   "targets": [
     {
       "expr": "opensearch_search_result_count",
       "legendFormat": "count"
     }
   ],
   "datasource": { "type": "prometheus", "uid": "prometheus" },
   "fieldConfig": {
     "defaults": {
       "unit": "short",
       "color": { "mode": "thresholds" },
       "thresholds": {
         "mode": "absolute",
         "steps": [
           { "color": "green", "value": null },
           { "color": "orange", "value": 100 },
           { "color": "red", "value": 500 }
         ]
       }
     }
   },
   "options": {
     "reduceOptions": { "calcs": ["lastNotNull"], "fields": "" },
     "orientation": "auto",
     "colorMode": "value",
     "graphMode": "none",
     "justifyMode": "center"
   }
 }
]
}
```

---


## Hypothesis on OpenSearch Query Performance

The purpose of this application is to empirically validate the performance behavior of three different query methods in OpenSearch:  
1) irect lookup by `_id`,  
2) standard `search` queries using boolean clauses,  
3) Mustache-based template searches.  

These measurements were collected and visualized using Prometheus and Grafana.


---


### 1. Query by `_id` (`get_by_id_document`) — **the fastest method**
Average recorded:: **≈ 9 ms**  

The `_id` query is the fastest because OpenSearch performs a **direct access** to the document without scanning inverted indexes or applying analyzers.  
Its computational complexity is **O(1)**.  

However, this approach has two notable drawbacks:  

- **Persisting `_id` in SQL:**  
To correlate documents with relational data, the `_id` must also be stored in a SQL table, which adds write operations.

- **Synchronization after reindexing:**  
If a document changes and is reindexed, a new _id may be generated.  
This requires **updating the SQL record**, which involves additional read/write operations.  

**Conclusion:**  
Ideal for high-speed, point lookups, but costly to maintain and synchronize across systems.  


---

### 2. Query using `search` with `must` — **slower than `_id`**
Average recorded: **≈ 19 ms**  

This method forces OpenSearch to process:  

- Inverted index trees  
- Field tokenization  
- Boolean clause evaluation  
- Merging of results across nested fields  

Its time complexity approaches **O(log N)**, since OpenSearch uses binary search and optimized segment lookups internally.

**Conclusion:**  
More flexible than direct `_id` lookup, but inherently slower due to the complexity of its data structures.  

---

### 3. Query using Mustache Template — high initial latency, strong subsequent performance
First execution: **≈ 900 ms – 1 s**  
Subsequent executions: **≈ 10 – 12 ms**  

This method was initially the slowest because it involves extra steps:  

1. Loading the `.mustache` file from disk.  
2. Serializing and registering the template in OpenSearch (`/_scripts/{template_name}`).  
3. Executing the search with dynamic parameters.  

However, after the first execution, the template remains **cached in OpenSearch memory**, removing the need for reloading or recompiling it.  

 **Conclusion:**  
While the first run has high latency due to I/O and compilation overhead, subsequent queries run at speeds comparable to `_id` searches — combining **high performance with scalability**.

