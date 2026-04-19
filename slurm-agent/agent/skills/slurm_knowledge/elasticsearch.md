---
source_url: https://slurm.schedmd.com/elasticsearch.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:21:00 UTC
title: "Slurm Workload Manager - Elasticsearch Guide"
---

# Elasticsearch Guide
Slurm provides multiple Job Completion Plugins.
These plugins are an orthogonal way to provide historical job
[accounting](https://slurm.schedmd.com/accounting.html) data for finished jobs.
In most installations, Slurm is already configured with an
[AccountingStorageType](https://slurm.schedmd.com/slurm.conf.html)
plugin — usually slurmdbd . In these situations, the information
captured by a completion plugin is intentionally redundant.
The jobcomp/elasticsearch plugin can be used together with a web
layer on top of the Elasticsearch server — such as
[Kibana](https://www.elastic.co/products/kibana) — to
visualize your finished jobs and the state of your cluster. Some of these
visualization tools also let you easily create different types of dashboards,
diagrams, tables, histograms and/or apply customized filters when searching.
## Prerequisites[#prereq](https://slurm.schedmd.com/elasticsearch.html)
The plugin requires additional libraries for compilation:
- [libcurl](https://curl.se/libcurl) development files
- [JSON-C](https://slurm.schedmd.com/related_software.html)
## Configuration[#config](https://slurm.schedmd.com/elasticsearch.html)
The Elasticsearch instance should be running and reachable from the multiple
[SlurmctldHost](https://slurm.schedmd.com/slurm.conf.html) configured.
Refer to the [Elasticsearch Official Documentation](https://www.elastic.co/) for further details on setup and configuration.
There are three [slurm.conf](https://slurm.schedmd.com/slurm.conf.html) options related to
this plugin:
- [JobCompType](https://slurm.schedmd.com/slurm.conf.html) is used to select the job completion plugin type to activate. It should be set to jobcomp/elasticsearch . ```text JobCompType=jobcomp/elasticsearch ```
- [JobCompLoc](https://slurm.schedmd.com/slurm.conf.html) should be set to the Elasticsearch server URL endpoint (including the port number and the target index). ```text JobCompLoc= : / /_doc ``` NOTE : Since Elasticsearch 8.0 the APIs that accept types are removed, thereby moving to a typeless mode. The Slurm elasticsearch plugin in versions prior to 20.11 removed any trailing slashes from this option URL and appended a hardcoded /slurm/jobcomp suffix representing the /index/type respectively. Starting from Slurm 20.11 the URL is fully configurable and handed as-is without modification to the libcurl library functions. In addition, this also allows users to index data from different clusters to the same server but to different indices. NOTE : The Elasticsearch official documentation provides detailed information around these concepts, the type to typeless deprecation transition as well as reindex API references on how to copy data from one index to another if needed.
- [DebugFlags](https://slurm.schedmd.com/slurm.conf.html) could include the Elasticsearch flag for extra debugging purposes. ```text DebugFlags=Elasticsearch ``` It is a good idea to turn this on initially until you have verified that finished jobs are properly indexed. Note that you do not need to manually create the Elasticsearch index , since the plugin will automatically do so when trying to index the first job document.
## Visualization [#visualization](https://slurm.schedmd.com/elasticsearch.html)
Once jobs are being indexed, it is a good idea to use a web visualization
layer to analyze the data.
[Kibana](https://www.elastic.co/products/kibana) is a
recommended open-source data visualization plugin for Elasticsearch.
Once installed, an Elasticsearch index name or pattern has to be
configured to instruct Kibana to retrieve the data. Once data is loaded it is
possible to create tables where each row is a finished job, ordered by
any column you choose — the @end_time timestamp is suggested — and
any dashboards, graphs, or other analysis of interest.
## Testing and Debugging [#testing](https://slurm.schedmd.com/elasticsearch.html)
For debugging purposes, you can use the curl command or any similar
tool to perform REST requests against Elasticsearch directly. Some of the
following examples using the curl tool may be useful.
Query information assuming a slurm index name, including the
document count (which should be one per job indexed):
```text
$ curl -XGET http://localhost:9200/_cat/indices/slurm?v health status index uuid pri rep docs.count docs.deleted store.size pri.store.size yellow open slurm 103CW7GqQICiMQiSQv6M_g 5 1 9 0 142.8kb 142.8kb
```
Query all indexed jobs in the slurm index :
```text
$ curl -XGET 'http://localhost:9200/slurm/_search?pretty=true&q=*:*' | less
```
Delete the slurm index (caution!):
```text
$ curl -XDELETE http://localhost:9200/slurm {"acknowledged":true}
```
Query information about _cat options. More can be found in the
official documentation.
```text
$ curl -XGET http://localhost:9200/_cat
```
## Failure management [#failure_management](https://slurm.schedmd.com/elasticsearch.html)
When the primary slurmctld is shut down, information about all completed but
not yet indexed jobs held within the Elasticsearch plugin saved to a
file named elasticsearch_state , which is located in the
[StateSaveLocation](https://slurm.schedmd.com/slurm.conf.html). This
permits the plugin to restore the information when the slurmctld is restarted,
and will be sent to the Elasticsearch database when the connection is
restored.
## Acknowledgments[#ack](https://slurm.schedmd.com/elasticsearch.html)
The Elasticsearch plugin was created as part of Alejandro Sanchez's
[Master's Thesis](https://upcommons.upc.edu/handle/2117/79252).
