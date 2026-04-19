---
source_url: https://slurm.schedmd.com/rest_api.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:21:43 UTC
title: "Slurm Workload Manager -"
---

# Slurm Workload Manager -

- # Slurm REST API API to access and control Slurm More information: [https://www.schedmd.com/](https://www.schedmd.com/) Contact Info: [sales@schedmd.com](https://slurm.schedmd.com/sales@schedmd.com) Version: Slurm-25.11.5 BasePath: Apache 2.0 https://www.apache.org/licenses/LICENSE-2.0.html ## Access APIKey KeyParamName:X-SLURM-USER-NAME KeyInQuery:false KeyInHeader:true
- APIKey KeyParamName:X-SLURM-USER-TOKEN KeyInQuery:false KeyInHeader:true
- HTTP Basic Authentication
## Methods
[ Jump to [Models](https://slurm.schedmd.com/rest_api.html) ]
### Table of Contents
#### [Slurm](https://slurm.schedmd.com/rest_api.html)
- [delete /slurm/v0.0.44/job/{job_id}](https://slurm.schedmd.com/rest_api.html)
- [delete /slurm/v0.0.44/jobs/](https://slurm.schedmd.com/rest_api.html)
- [delete /slurm/v0.0.44/node/{node_name}](https://slurm.schedmd.com/rest_api.html)
- [delete /slurm/v0.0.44/reservation/{reservation_name}](https://slurm.schedmd.com/rest_api.html)
- [get /slurm/v0.0.44/diag/](https://slurm.schedmd.com/rest_api.html)
- [get /slurm/v0.0.44/job/{job_id}](https://slurm.schedmd.com/rest_api.html)
- [get /slurm/v0.0.44/jobs/](https://slurm.schedmd.com/rest_api.html)
- [get /slurm/v0.0.44/jobs/state/](https://slurm.schedmd.com/rest_api.html)
- [get /slurm/v0.0.44/licenses/](https://slurm.schedmd.com/rest_api.html)
- [get /slurm/v0.0.44/node/{node_name}](https://slurm.schedmd.com/rest_api.html)
- [get /slurm/v0.0.44/nodes/](https://slurm.schedmd.com/rest_api.html)
- [get /slurm/v0.0.44/partition/{partition_name}](https://slurm.schedmd.com/rest_api.html)
- [get /slurm/v0.0.44/partitions/](https://slurm.schedmd.com/rest_api.html)
- [get /slurm/v0.0.44/ping/](https://slurm.schedmd.com/rest_api.html)
- [get /slurm/v0.0.44/reconfigure/](https://slurm.schedmd.com/rest_api.html)
- [get /slurm/v0.0.44/reservation/{reservation_name}](https://slurm.schedmd.com/rest_api.html)
- [get /slurm/v0.0.44/reservations/](https://slurm.schedmd.com/rest_api.html)
- [get /slurm/v0.0.44/resources/{job_id}](https://slurm.schedmd.com/rest_api.html)
- [get /slurm/v0.0.44/shares](https://slurm.schedmd.com/rest_api.html)
- [post /slurm/v0.0.44/job/{job_id}](https://slurm.schedmd.com/rest_api.html)
- [post /slurm/v0.0.44/job/allocate](https://slurm.schedmd.com/rest_api.html)
- [post /slurm/v0.0.44/job/submit](https://slurm.schedmd.com/rest_api.html)
- [post /slurm/v0.0.44/new/node/](https://slurm.schedmd.com/rest_api.html)
- [post /slurm/v0.0.44/node/{node_name}](https://slurm.schedmd.com/rest_api.html)
- [post /slurm/v0.0.44/nodes/](https://slurm.schedmd.com/rest_api.html)
- [post /slurm/v0.0.44/reservation](https://slurm.schedmd.com/rest_api.html)
- [post /slurm/v0.0.44/reservations/](https://slurm.schedmd.com/rest_api.html)
#### [Slurmdb](https://slurm.schedmd.com/rest_api.html)
- [delete /slurmdb/v0.0.44/account/{account_name}](https://slurm.schedmd.com/rest_api.html)
- [delete /slurmdb/v0.0.44/association/](https://slurm.schedmd.com/rest_api.html)
- [delete /slurmdb/v0.0.44/associations/](https://slurm.schedmd.com/rest_api.html)
- [delete /slurmdb/v0.0.44/cluster/{cluster_name}](https://slurm.schedmd.com/rest_api.html)
- [delete /slurmdb/v0.0.44/qos/{qos}](https://slurm.schedmd.com/rest_api.html)
- [delete /slurmdb/v0.0.44/user/{name}](https://slurm.schedmd.com/rest_api.html)
- [delete /slurmdb/v0.0.44/wckey/{id}](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/account/{account_name}](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/accounts/](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/association/](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/associations/](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/cluster/{cluster_name}](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/clusters/](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/config](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/diag/](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/instance/](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/instances/](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/job/{job_id}](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/jobs/](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/ping/](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/qos/](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/qos/{qos}](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/tres/](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/user/{name}](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/users/](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/wckey/{id}](https://slurm.schedmd.com/rest_api.html)
- [get /slurmdb/v0.0.44/wckeys/](https://slurm.schedmd.com/rest_api.html)
- [post /slurmdb/v0.0.44/accounts/](https://slurm.schedmd.com/rest_api.html)
- [post /slurmdb/v0.0.44/accounts_association/](https://slurm.schedmd.com/rest_api.html)
- [post /slurmdb/v0.0.44/associations/](https://slurm.schedmd.com/rest_api.html)
- [post /slurmdb/v0.0.44/clusters/](https://slurm.schedmd.com/rest_api.html)
- [post /slurmdb/v0.0.44/config](https://slurm.schedmd.com/rest_api.html)
- [post /slurmdb/v0.0.44/job/{job_id}](https://slurm.schedmd.com/rest_api.html)
- [post /slurmdb/v0.0.44/jobs/](https://slurm.schedmd.com/rest_api.html)
- [post /slurmdb/v0.0.44/qos/](https://slurm.schedmd.com/rest_api.html)
- [post /slurmdb/v0.0.44/tres/](https://slurm.schedmd.com/rest_api.html)
- [post /slurmdb/v0.0.44/users/](https://slurm.schedmd.com/rest_api.html)
- [post /slurmdb/v0.0.44/users_association/](https://slurm.schedmd.com/rest_api.html)
- [post /slurmdb/v0.0.44/wckeys/](https://slurm.schedmd.com/rest_api.html)
# Slurm
[Up](https://slurm.schedmd.com/rest_api.html)
```text
delete /slurm/v0.0.44/job/{job_id}
```
cancel or signal job ( slurmV0044DeleteJob )
### Path parameters
job_id (required)
Path Parameter — Job ID default: null
### Query parameters
signal (optional)
Query Parameter — Signal to send to Job default: null
flags (optional)
Query Parameter — Signalling flags default: null
### Return type
[v0.0.44_openapi_kill_job_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ],
"status" : [ {
"federation" : {
"sibling" : "sibling"
},
"job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"error" : {
"code" : 0,
"string" : "string",
"message" : "message"
},
"step_id" : "step_id"
}, {
"federation" : {
"sibling" : "sibling"
},
"job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"error" : {
"code" : 0,
"string" : "string",
"message" : "message"
},
"step_id" : "step_id"
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
job signal result
[v0.0.44_openapi_kill_job_resp](https://slurm.schedmd.com/rest_api.html)
#### default
job signal result
[v0.0.44_openapi_kill_job_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
delete /slurm/v0.0.44/jobs/
```
send signal to list of jobs ( slurmV0044DeleteJobs )
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_kill_jobs_msg [v0.0.44_kill_jobs_msg](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Return type
[v0.0.44_openapi_kill_jobs_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ],
"status" : [ {
"federation" : {
"sibling" : "sibling"
},
"job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"error" : {
"code" : 0,
"string" : "string",
"message" : "message"
},
"step_id" : "step_id"
}, {
"federation" : {
"sibling" : "sibling"
},
"job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"error" : {
"code" : 0,
"string" : "string",
"message" : "message"
},
"step_id" : "step_id"
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
description of jobs to signal
[v0.0.44_openapi_kill_jobs_resp](https://slurm.schedmd.com/rest_api.html)
#### default
description of jobs to signal
[v0.0.44_openapi_kill_jobs_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
delete /slurm/v0.0.44/node/{node_name}
```
delete node ( slurmV0044DeleteNode )
### Path parameters
node_name (required)
Path Parameter — Node name default: null
### Return type
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
node delete request result
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
#### default
node delete request result
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
delete /slurm/v0.0.44/reservation/{reservation_name}
```
delete a reservation ( slurmV0044DeleteReservation )
### Path parameters
reservation_name (required)
Path Parameter — Reservation name default: null
### Return type
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
reservation delete request result
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
#### default
reservation delete request result
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurm/v0.0.44/diag/
```
get diagnostics ( slurmV0044GetDiag )
### Return type
[v0.0.44_openapi_diag_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ],
"statistics" : {
"bf_cycle_max" : 7,
"rpcs_by_message_type" : [ {
"cycle_last" : 0,
"average_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"type_id" : 7,
"queued" : 0,
"count" : 9,
"dropped" : 9,
"message_type" : "message_type",
"total_time" : 5,
"cycle_max" : 7
}, {
"cycle_last" : 0,
"average_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"type_id" : 7,
"queued" : 0,
"count" : 9,
"dropped" : 9,
"message_type" : "message_type",
"total_time" : 5,
"cycle_max" : 7
} ],
"bf_backfilled_het_jobs" : 6,
"bf_table_size" : 4,
"schedule_cycle_depth" : 1,
"bf_depth_sum" : 5,
"job_states_ts" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"bf_queue_len" : 4,
"jobs_started" : 8,
"schedule_cycle_max" : 9,
"server_thread_count" : 6,
"bf_queue_len_sum" : 6,
"bf_cycle_last" : 0,
"bf_exit" : {
"state_changed" : 3,
"bf_max_time" : 8,
"bf_max_job_start" : 0,
"bf_node_space_size" : 7,
"end_job_queue" : 6,
"bf_max_job_test" : 4
},
"agent_thread_count" : 5,
"jobs_completed" : 9,
"bf_depth_mean" : 3,
"bf_depth_try_sum" : 3,
"schedule_cycle_mean" : 7,
"bf_table_size_sum" : 1,
"agent_queue_size" : 1,
"jobs_failed" : 3,
"bf_last_depth_try" : 7,
"req_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"bf_cycle_counter" : 5,
"schedule_queue_length" : 9,
"bf_queue_len_mean" : 0,
"schedule_exit" : {
"max_sched_time" : 5,
"licenses" : 9,
"default_queue_depth" : 7,
"max_job_start" : 1,
"max_rpc_cnt" : 4,
"end_job_queue" : 6
},
"jobs_canceled" : 6,
"schedule_cycle_sum" : 2,
"jobs_submitted" : 6,
"schedule_cycle_mean_depth" : 1,
"schedule_cycle_per_minute" : 1,
"req_time_start" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"jobs_running" : 1,
"bf_last_backfilled_jobs" : 6,
"bf_last_depth" : 3,
"bf_backfilled_jobs" : 2,
"rpcs_by_user" : [ {
"average_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user_id" : 4,
"count" : 6,
"total_time" : 8,
"user" : "user"
}, {
"average_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user_id" : 4,
"count" : 6,
"total_time" : 8,
"user" : "user"
} ],
"bf_cycle_mean" : 6,
"pending_rpcs_by_hostlist" : [ {
"type_id" : 0,
"count" : [ "count", "count" ],
"message_type" : "message_type"
}, {
"type_id" : 0,
"count" : [ "count", "count" ],
"message_type" : "message_type"
} ],
"dbd_agent_queue_size" : 2,
"bf_table_size_mean" : 4,
"jobs_pending" : 6,
"agent_count" : 5,
"bf_cycle_sum" : 7,
"parts_packed" : 0,
"bf_active" : true,
"bf_depth_mean_try" : 3,
"gettimeofday_latency" : 7,
"pending_rpcs" : [ {
"type_id" : 4,
"count" : 3,
"message_type" : "message_type"
}, {
"type_id" : 4,
"count" : 3,
"message_type" : "message_type"
} ],
"schedule_cycle_total" : 4,
"bf_when_last_cycle" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"schedule_cycle_last" : 3
}
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
diagnostic results
[v0.0.44_openapi_diag_resp](https://slurm.schedmd.com/rest_api.html)
#### default
diagnostic results
[v0.0.44_openapi_diag_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurm/v0.0.44/job/{job_id}
```
get job info ( slurmV0044GetJob )
### Path parameters
job_id (required)
Path Parameter — Job ID default: null
### Query parameters
update_time (optional)
Query Parameter — Query jobs updated more recently than this time (UNIX timestamp) default: null
flags (optional)
Query Parameter — Query flags default: null
### Return type
[v0.0.44_openapi_job_info_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"last_backfill" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"jobs" : [ {
"container" : "container",
"cluster" : "cluster",
"stdin_expanded" : "stdin_expanded",
"time_minimum" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"memory_per_tres" : "memory_per_tres",
"scheduled_nodes" : "scheduled_nodes",
"qos" : "qos",
"resize_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"eligible_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpus_per_tres" : "cpus_per_tres",
"preemptable_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tasks" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"system_comment" : "system_comment",
"federation_siblings_active" : "federation_siblings_active",
"tasks_per_tres" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tasks_per_core" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"accrue_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"dependency" : "dependency",
"group_name" : "group_name",
"profile" : [ "NOT_SET", "NOT_SET" ],
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"tres_per_job" : "tres_per_job",
"failed_node" : "failed_node",
"derived_exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"priority_by_partition" : [ {
"partition" : "partition",
"priority" : 6
}, {
"partition" : "partition",
"priority" : 6
} ],
"maximum_switch_wait_time" : 9,
"core_spec" : 6,
"mcs_label" : "mcs_label",
"required_nodes" : "required_nodes",
"tres_bind" : "tres_bind",
"user_id" : 9,
"selinux_context" : "selinux_context",
"exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"federation_origin" : "federation_origin",
"container_id" : "container_id",
"shared" : [ "none", "none" ],
"tasks_per_board" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user_name" : "user_name",
"stderr_expanded" : "stderr_expanded",
"flags" : [ "KILL_INVALID_DEPENDENCY", "KILL_INVALID_DEPENDENCY" ],
"standard_input" : "standard_input",
"admin_comment" : "admin_comment",
"cores_per_socket" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"step_id" : {
"sluid" : "sluid",
"job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"step_het_component" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"step_id" : "step_id"
},
"job_state" : [ "PENDING", "PENDING" ],
"tasks_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"current_working_directory" : "current_working_directory",
"standard_error" : "standard_error",
"array_job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"cluster_features" : "cluster_features",
"partition" : "partition",
"segment_size" : 4,
"threads_per_core" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tres_alloc_str" : "tres_alloc_str",
"memory_per_cpu" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpu_frequency_minimum" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"node_count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"power" : {
"flags" : [ "", "" ]
},
"deadline" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"mail_type" : [ "BEGIN", "BEGIN" ],
"memory_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"state_reason" : "state_reason",
"het_job_offset" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"end_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"sockets_per_board" : 5,
"nice" : 1,
"last_sched_evaluation" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tres_per_node" : "tres_per_node",
"burst_buffer" : "burst_buffer",
"licenses" : "licenses",
"excluded_nodes" : "excluded_nodes",
"array_max_tasks" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"het_job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"sockets_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"prefer" : "prefer",
"time_limit" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"minimum_cpus_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tasks_per_socket" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"batch_host" : "batch_host",
"max_cpus" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"job_size_str" : [ "job_size_str", "job_size_str" ],
"hold" : true,
"cpu_frequency_maximum" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"features" : "features",
"het_job_id_set" : "het_job_id_set",
"state_description" : "state_description",
"submit_line" : "submit_line",
"array_task_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"licenses_allocated" : "licenses_allocated",
"minimum_tmp_disk_per_node" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"tres_req_str" : "tres_req_str",
"burst_buffer_state" : "burst_buffer_state",
"cron" : "cron",
"allocating_node" : "allocating_node",
"tres_per_socket" : "tres_per_socket",
"array_task_string" : "array_task_string",
"submit_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"wckey" : "wckey",
"max_nodes" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"batch_flag" : true,
"start_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"name" : "name",
"preempt_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"contiguous" : true,
"job_resources" : {
"nodes" : {
"allocation" : [ {
"memory" : {
"used" : 2,
"allocated" : 4
},
"cpus" : {
"count" : 9,
"used" : 3
},
"name" : "name",
"index" : 7,
"sockets" : [ {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
}, {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
} ]
}, {
"memory" : {
"used" : 2,
"allocated" : 4
},
"cpus" : {
"count" : 9,
"used" : 3
},
"name" : "name",
"index" : 7,
"sockets" : [ {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
}, {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
} ]
} ],
"count" : 2,
"select_type" : [ "AVAILABLE", "AVAILABLE" ],
"whole" : true,
"list" : "list"
},
"threads_per_core" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpus" : 1,
"select_type" : [ "CPU", "CPU" ]
},
"billable_tres" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"federation_siblings_viable" : "federation_siblings_viable",
"cpus_per_task" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"batch_features" : "batch_features",
"thread_spec" : 1,
"cpu_frequency_governor" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"gres_detail" : [ "gres_detail", "gres_detail" ],
"stdout_expanded" : "stdout_expanded",
"network" : "network",
"restart_cnt" : 1,
"resv_name" : "resv_name",
"extra" : "extra",
"delay_boot" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"reboot" : true,
"cpus" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"standard_output" : "standard_output",
"pre_sus_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"suspend_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"association_id" : 0,
"command" : "command",
"tres_freq" : "tres_freq",
"requeue" : true,
"tres_per_task" : "tres_per_task",
"mail_user" : "mail_user",
"nodes" : "nodes",
"group_id" : 5,
"job_id" : 5,
"comment" : "comment",
"account" : "account",
"required_switches" : 7
}, {
"container" : "container",
"cluster" : "cluster",
"stdin_expanded" : "stdin_expanded",
"time_minimum" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"memory_per_tres" : "memory_per_tres",
"scheduled_nodes" : "scheduled_nodes",
"qos" : "qos",
"resize_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"eligible_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpus_per_tres" : "cpus_per_tres",
"preemptable_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tasks" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"system_comment" : "system_comment",
"federation_siblings_active" : "federation_siblings_active",
"tasks_per_tres" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tasks_per_core" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"accrue_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"dependency" : "dependency",
"group_name" : "group_name",
"profile" : [ "NOT_SET", "NOT_SET" ],
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"tres_per_job" : "tres_per_job",
"failed_node" : "failed_node",
"derived_exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"priority_by_partition" : [ {
"partition" : "partition",
"priority" : 6
}, {
"partition" : "partition",
"priority" : 6
} ],
"maximum_switch_wait_time" : 9,
"core_spec" : 6,
"mcs_label" : "mcs_label",
"required_nodes" : "required_nodes",
"tres_bind" : "tres_bind",
"user_id" : 9,
"selinux_context" : "selinux_context",
"exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"federation_origin" : "federation_origin",
"container_id" : "container_id",
"shared" : [ "none", "none" ],
"tasks_per_board" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user_name" : "user_name",
"stderr_expanded" : "stderr_expanded",
"flags" : [ "KILL_INVALID_DEPENDENCY", "KILL_INVALID_DEPENDENCY" ],
"standard_input" : "standard_input",
"admin_comment" : "admin_comment",
"cores_per_socket" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"step_id" : {
"sluid" : "sluid",
"job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"step_het_component" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"step_id" : "step_id"
},
"job_state" : [ "PENDING", "PENDING" ],
"tasks_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"current_working_directory" : "current_working_directory",
"standard_error" : "standard_error",
"array_job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"cluster_features" : "cluster_features",
"partition" : "partition",
"segment_size" : 4,
"threads_per_core" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tres_alloc_str" : "tres_alloc_str",
"memory_per_cpu" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpu_frequency_minimum" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"node_count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"power" : {
"flags" : [ "", "" ]
},
"deadline" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"mail_type" : [ "BEGIN", "BEGIN" ],
"memory_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"state_reason" : "state_reason",
"het_job_offset" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"end_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"sockets_per_board" : 5,
"nice" : 1,
"last_sched_evaluation" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tres_per_node" : "tres_per_node",
"burst_buffer" : "burst_buffer",
"licenses" : "licenses",
"excluded_nodes" : "excluded_nodes",
"array_max_tasks" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"het_job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"sockets_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"prefer" : "prefer",
"time_limit" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"minimum_cpus_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tasks_per_socket" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"batch_host" : "batch_host",
"max_cpus" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"job_size_str" : [ "job_size_str", "job_size_str" ],
"hold" : true,
"cpu_frequency_maximum" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"features" : "features",
"het_job_id_set" : "het_job_id_set",
"state_description" : "state_description",
"submit_line" : "submit_line",
"array_task_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"licenses_allocated" : "licenses_allocated",
"minimum_tmp_disk_per_node" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"tres_req_str" : "tres_req_str",
"burst_buffer_state" : "burst_buffer_state",
"cron" : "cron",
"allocating_node" : "allocating_node",
"tres_per_socket" : "tres_per_socket",
"array_task_string" : "array_task_string",
"submit_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"wckey" : "wckey",
"max_nodes" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"batch_flag" : true,
"start_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"name" : "name",
"preempt_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"contiguous" : true,
"job_resources" : {
"nodes" : {
"allocation" : [ {
"memory" : {
"used" : 2,
"allocated" : 4
},
"cpus" : {
"count" : 9,
"used" : 3
},
"name" : "name",
"index" : 7,
"sockets" : [ {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
}, {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
} ]
}, {
"memory" : {
"used" : 2,
"allocated" : 4
},
"cpus" : {
"count" : 9,
"used" : 3
},
"name" : "name",
"index" : 7,
"sockets" : [ {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
}, {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
} ]
} ],
"count" : 2,
"select_type" : [ "AVAILABLE", "AVAILABLE" ],
"whole" : true,
"list" : "list"
},
"threads_per_core" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpus" : 1,
"select_type" : [ "CPU", "CPU" ]
},
"billable_tres" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"federation_siblings_viable" : "federation_siblings_viable",
"cpus_per_task" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"batch_features" : "batch_features",
"thread_spec" : 1,
"cpu_frequency_governor" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"gres_detail" : [ "gres_detail", "gres_detail" ],
"stdout_expanded" : "stdout_expanded",
"network" : "network",
"restart_cnt" : 1,
"resv_name" : "resv_name",
"extra" : "extra",
"delay_boot" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"reboot" : true,
"cpus" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"standard_output" : "standard_output",
"pre_sus_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"suspend_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"association_id" : 0,
"command" : "command",
"tres_freq" : "tres_freq",
"requeue" : true,
"tres_per_task" : "tres_per_task",
"mail_user" : "mail_user",
"nodes" : "nodes",
"group_id" : 5,
"job_id" : 5,
"comment" : "comment",
"account" : "account",
"required_switches" : 7
} ],
"last_update" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
job(s) information
[v0.0.44_openapi_job_info_resp](https://slurm.schedmd.com/rest_api.html)
#### default
job(s) information
[v0.0.44_openapi_job_info_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurm/v0.0.44/jobs/
```
get list of jobs ( slurmV0044GetJobs )
### Query parameters
update_time (optional)
Query Parameter — Query jobs updated more recently than this time (UNIX timestamp) default: null
flags (optional)
Query Parameter — Query flags default: null
### Return type
[v0.0.44_openapi_job_info_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"last_backfill" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"jobs" : [ {
"container" : "container",
"cluster" : "cluster",
"stdin_expanded" : "stdin_expanded",
"time_minimum" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"memory_per_tres" : "memory_per_tres",
"scheduled_nodes" : "scheduled_nodes",
"qos" : "qos",
"resize_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"eligible_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpus_per_tres" : "cpus_per_tres",
"preemptable_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tasks" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"system_comment" : "system_comment",
"federation_siblings_active" : "federation_siblings_active",
"tasks_per_tres" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tasks_per_core" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"accrue_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"dependency" : "dependency",
"group_name" : "group_name",
"profile" : [ "NOT_SET", "NOT_SET" ],
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"tres_per_job" : "tres_per_job",
"failed_node" : "failed_node",
"derived_exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"priority_by_partition" : [ {
"partition" : "partition",
"priority" : 6
}, {
"partition" : "partition",
"priority" : 6
} ],
"maximum_switch_wait_time" : 9,
"core_spec" : 6,
"mcs_label" : "mcs_label",
"required_nodes" : "required_nodes",
"tres_bind" : "tres_bind",
"user_id" : 9,
"selinux_context" : "selinux_context",
"exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"federation_origin" : "federation_origin",
"container_id" : "container_id",
"shared" : [ "none", "none" ],
"tasks_per_board" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user_name" : "user_name",
"stderr_expanded" : "stderr_expanded",
"flags" : [ "KILL_INVALID_DEPENDENCY", "KILL_INVALID_DEPENDENCY" ],
"standard_input" : "standard_input",
"admin_comment" : "admin_comment",
"cores_per_socket" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"step_id" : {
"sluid" : "sluid",
"job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"step_het_component" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"step_id" : "step_id"
},
"job_state" : [ "PENDING", "PENDING" ],
"tasks_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"current_working_directory" : "current_working_directory",
"standard_error" : "standard_error",
"array_job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"cluster_features" : "cluster_features",
"partition" : "partition",
"segment_size" : 4,
"threads_per_core" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tres_alloc_str" : "tres_alloc_str",
"memory_per_cpu" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpu_frequency_minimum" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"node_count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"power" : {
"flags" : [ "", "" ]
},
"deadline" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"mail_type" : [ "BEGIN", "BEGIN" ],
"memory_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"state_reason" : "state_reason",
"het_job_offset" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"end_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"sockets_per_board" : 5,
"nice" : 1,
"last_sched_evaluation" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tres_per_node" : "tres_per_node",
"burst_buffer" : "burst_buffer",
"licenses" : "licenses",
"excluded_nodes" : "excluded_nodes",
"array_max_tasks" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"het_job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"sockets_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"prefer" : "prefer",
"time_limit" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"minimum_cpus_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tasks_per_socket" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"batch_host" : "batch_host",
"max_cpus" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"job_size_str" : [ "job_size_str", "job_size_str" ],
"hold" : true,
"cpu_frequency_maximum" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"features" : "features",
"het_job_id_set" : "het_job_id_set",
"state_description" : "state_description",
"submit_line" : "submit_line",
"array_task_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"licenses_allocated" : "licenses_allocated",
"minimum_tmp_disk_per_node" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"tres_req_str" : "tres_req_str",
"burst_buffer_state" : "burst_buffer_state",
"cron" : "cron",
"allocating_node" : "allocating_node",
"tres_per_socket" : "tres_per_socket",
"array_task_string" : "array_task_string",
"submit_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"wckey" : "wckey",
"max_nodes" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"batch_flag" : true,
"start_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"name" : "name",
"preempt_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"contiguous" : true,
"job_resources" : {
"nodes" : {
"allocation" : [ {
"memory" : {
"used" : 2,
"allocated" : 4
},
"cpus" : {
"count" : 9,
"used" : 3
},
"name" : "name",
"index" : 7,
"sockets" : [ {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
}, {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
} ]
}, {
"memory" : {
"used" : 2,
"allocated" : 4
},
"cpus" : {
"count" : 9,
"used" : 3
},
"name" : "name",
"index" : 7,
"sockets" : [ {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
}, {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
} ]
} ],
"count" : 2,
"select_type" : [ "AVAILABLE", "AVAILABLE" ],
"whole" : true,
"list" : "list"
},
"threads_per_core" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpus" : 1,
"select_type" : [ "CPU", "CPU" ]
},
"billable_tres" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"federation_siblings_viable" : "federation_siblings_viable",
"cpus_per_task" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"batch_features" : "batch_features",
"thread_spec" : 1,
"cpu_frequency_governor" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"gres_detail" : [ "gres_detail", "gres_detail" ],
"stdout_expanded" : "stdout_expanded",
"network" : "network",
"restart_cnt" : 1,
"resv_name" : "resv_name",
"extra" : "extra",
"delay_boot" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"reboot" : true,
"cpus" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"standard_output" : "standard_output",
"pre_sus_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"suspend_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"association_id" : 0,
"command" : "command",
"tres_freq" : "tres_freq",
"requeue" : true,
"tres_per_task" : "tres_per_task",
"mail_user" : "mail_user",
"nodes" : "nodes",
"group_id" : 5,
"job_id" : 5,
"comment" : "comment",
"account" : "account",
"required_switches" : 7
}, {
"container" : "container",
"cluster" : "cluster",
"stdin_expanded" : "stdin_expanded",
"time_minimum" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"memory_per_tres" : "memory_per_tres",
"scheduled_nodes" : "scheduled_nodes",
"qos" : "qos",
"resize_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"eligible_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpus_per_tres" : "cpus_per_tres",
"preemptable_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tasks" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"system_comment" : "system_comment",
"federation_siblings_active" : "federation_siblings_active",
"tasks_per_tres" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tasks_per_core" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"accrue_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"dependency" : "dependency",
"group_name" : "group_name",
"profile" : [ "NOT_SET", "NOT_SET" ],
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"tres_per_job" : "tres_per_job",
"failed_node" : "failed_node",
"derived_exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"priority_by_partition" : [ {
"partition" : "partition",
"priority" : 6
}, {
"partition" : "partition",
"priority" : 6
} ],
"maximum_switch_wait_time" : 9,
"core_spec" : 6,
"mcs_label" : "mcs_label",
"required_nodes" : "required_nodes",
"tres_bind" : "tres_bind",
"user_id" : 9,
"selinux_context" : "selinux_context",
"exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"federation_origin" : "federation_origin",
"container_id" : "container_id",
"shared" : [ "none", "none" ],
"tasks_per_board" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user_name" : "user_name",
"stderr_expanded" : "stderr_expanded",
"flags" : [ "KILL_INVALID_DEPENDENCY", "KILL_INVALID_DEPENDENCY" ],
"standard_input" : "standard_input",
"admin_comment" : "admin_comment",
"cores_per_socket" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"step_id" : {
"sluid" : "sluid",
"job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"step_het_component" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"step_id" : "step_id"
},
"job_state" : [ "PENDING", "PENDING" ],
"tasks_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"current_working_directory" : "current_working_directory",
"standard_error" : "standard_error",
"array_job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"cluster_features" : "cluster_features",
"partition" : "partition",
"segment_size" : 4,
"threads_per_core" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tres_alloc_str" : "tres_alloc_str",
"memory_per_cpu" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpu_frequency_minimum" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"node_count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"power" : {
"flags" : [ "", "" ]
},
"deadline" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"mail_type" : [ "BEGIN", "BEGIN" ],
"memory_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"state_reason" : "state_reason",
"het_job_offset" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"end_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"sockets_per_board" : 5,
"nice" : 1,
"last_sched_evaluation" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tres_per_node" : "tres_per_node",
"burst_buffer" : "burst_buffer",
"licenses" : "licenses",
"excluded_nodes" : "excluded_nodes",
"array_max_tasks" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"het_job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"sockets_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"prefer" : "prefer",
"time_limit" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"minimum_cpus_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tasks_per_socket" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"batch_host" : "batch_host",
"max_cpus" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"job_size_str" : [ "job_size_str", "job_size_str" ],
"hold" : true,
"cpu_frequency_maximum" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"features" : "features",
"het_job_id_set" : "het_job_id_set",
"state_description" : "state_description",
"submit_line" : "submit_line",
"array_task_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"licenses_allocated" : "licenses_allocated",
"minimum_tmp_disk_per_node" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"tres_req_str" : "tres_req_str",
"burst_buffer_state" : "burst_buffer_state",
"cron" : "cron",
"allocating_node" : "allocating_node",
"tres_per_socket" : "tres_per_socket",
"array_task_string" : "array_task_string",
"submit_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"wckey" : "wckey",
"max_nodes" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"batch_flag" : true,
"start_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"name" : "name",
"preempt_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"contiguous" : true,
"job_resources" : {
"nodes" : {
"allocation" : [ {
"memory" : {
"used" : 2,
"allocated" : 4
},
"cpus" : {
"count" : 9,
"used" : 3
},
"name" : "name",
"index" : 7,
"sockets" : [ {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
}, {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
} ]
}, {
"memory" : {
"used" : 2,
"allocated" : 4
},
"cpus" : {
"count" : 9,
"used" : 3
},
"name" : "name",
"index" : 7,
"sockets" : [ {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
}, {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
} ]
} ],
"count" : 2,
"select_type" : [ "AVAILABLE", "AVAILABLE" ],
"whole" : true,
"list" : "list"
},
"threads_per_core" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpus" : 1,
"select_type" : [ "CPU", "CPU" ]
},
"billable_tres" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"federation_siblings_viable" : "federation_siblings_viable",
"cpus_per_task" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"batch_features" : "batch_features",
"thread_spec" : 1,
"cpu_frequency_governor" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"gres_detail" : [ "gres_detail", "gres_detail" ],
"stdout_expanded" : "stdout_expanded",
"network" : "network",
"restart_cnt" : 1,
"resv_name" : "resv_name",
"extra" : "extra",
"delay_boot" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"reboot" : true,
"cpus" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"standard_output" : "standard_output",
"pre_sus_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"suspend_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"association_id" : 0,
"command" : "command",
"tres_freq" : "tres_freq",
"requeue" : true,
"tres_per_task" : "tres_per_task",
"mail_user" : "mail_user",
"nodes" : "nodes",
"group_id" : 5,
"job_id" : 5,
"comment" : "comment",
"account" : "account",
"required_switches" : 7
} ],
"last_update" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
job(s) information
[v0.0.44_openapi_job_info_resp](https://slurm.schedmd.com/rest_api.html)
#### default
job(s) information
[v0.0.44_openapi_job_info_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurm/v0.0.44/jobs/state/
```
get list of job states ( slurmV0044GetJobsState )
### Query parameters
job_id (optional)
Query Parameter — CSV list of Job IDs to search for default: null
### Return type
[v0.0.44_openapi_job_info_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"last_backfill" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"jobs" : [ {
"container" : "container",
"cluster" : "cluster",
"stdin_expanded" : "stdin_expanded",
"time_minimum" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"memory_per_tres" : "memory_per_tres",
"scheduled_nodes" : "scheduled_nodes",
"qos" : "qos",
"resize_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"eligible_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpus_per_tres" : "cpus_per_tres",
"preemptable_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tasks" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"system_comment" : "system_comment",
"federation_siblings_active" : "federation_siblings_active",
"tasks_per_tres" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tasks_per_core" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"accrue_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"dependency" : "dependency",
"group_name" : "group_name",
"profile" : [ "NOT_SET", "NOT_SET" ],
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"tres_per_job" : "tres_per_job",
"failed_node" : "failed_node",
"derived_exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"priority_by_partition" : [ {
"partition" : "partition",
"priority" : 6
}, {
"partition" : "partition",
"priority" : 6
} ],
"maximum_switch_wait_time" : 9,
"core_spec" : 6,
"mcs_label" : "mcs_label",
"required_nodes" : "required_nodes",
"tres_bind" : "tres_bind",
"user_id" : 9,
"selinux_context" : "selinux_context",
"exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"federation_origin" : "federation_origin",
"container_id" : "container_id",
"shared" : [ "none", "none" ],
"tasks_per_board" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user_name" : "user_name",
"stderr_expanded" : "stderr_expanded",
"flags" : [ "KILL_INVALID_DEPENDENCY", "KILL_INVALID_DEPENDENCY" ],
"standard_input" : "standard_input",
"admin_comment" : "admin_comment",
"cores_per_socket" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"step_id" : {
"sluid" : "sluid",
"job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"step_het_component" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"step_id" : "step_id"
},
"job_state" : [ "PENDING", "PENDING" ],
"tasks_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"current_working_directory" : "current_working_directory",
"standard_error" : "standard_error",
"array_job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"cluster_features" : "cluster_features",
"partition" : "partition",
"segment_size" : 4,
"threads_per_core" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tres_alloc_str" : "tres_alloc_str",
"memory_per_cpu" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpu_frequency_minimum" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"node_count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"power" : {
"flags" : [ "", "" ]
},
"deadline" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"mail_type" : [ "BEGIN", "BEGIN" ],
"memory_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"state_reason" : "state_reason",
"het_job_offset" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"end_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"sockets_per_board" : 5,
"nice" : 1,
"last_sched_evaluation" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tres_per_node" : "tres_per_node",
"burst_buffer" : "burst_buffer",
"licenses" : "licenses",
"excluded_nodes" : "excluded_nodes",
"array_max_tasks" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"het_job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"sockets_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"prefer" : "prefer",
"time_limit" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"minimum_cpus_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tasks_per_socket" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"batch_host" : "batch_host",
"max_cpus" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"job_size_str" : [ "job_size_str", "job_size_str" ],
"hold" : true,
"cpu_frequency_maximum" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"features" : "features",
"het_job_id_set" : "het_job_id_set",
"state_description" : "state_description",
"submit_line" : "submit_line",
"array_task_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"licenses_allocated" : "licenses_allocated",
"minimum_tmp_disk_per_node" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"tres_req_str" : "tres_req_str",
"burst_buffer_state" : "burst_buffer_state",
"cron" : "cron",
"allocating_node" : "allocating_node",
"tres_per_socket" : "tres_per_socket",
"array_task_string" : "array_task_string",
"submit_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"wckey" : "wckey",
"max_nodes" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"batch_flag" : true,
"start_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"name" : "name",
"preempt_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"contiguous" : true,
"job_resources" : {
"nodes" : {
"allocation" : [ {
"memory" : {
"used" : 2,
"allocated" : 4
},
"cpus" : {
"count" : 9,
"used" : 3
},
"name" : "name",
"index" : 7,
"sockets" : [ {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
}, {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
} ]
}, {
"memory" : {
"used" : 2,
"allocated" : 4
},
"cpus" : {
"count" : 9,
"used" : 3
},
"name" : "name",
"index" : 7,
"sockets" : [ {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
}, {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
} ]
} ],
"count" : 2,
"select_type" : [ "AVAILABLE", "AVAILABLE" ],
"whole" : true,
"list" : "list"
},
"threads_per_core" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpus" : 1,
"select_type" : [ "CPU", "CPU" ]
},
"billable_tres" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"federation_siblings_viable" : "federation_siblings_viable",
"cpus_per_task" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"batch_features" : "batch_features",
"thread_spec" : 1,
"cpu_frequency_governor" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"gres_detail" : [ "gres_detail", "gres_detail" ],
"stdout_expanded" : "stdout_expanded",
"network" : "network",
"restart_cnt" : 1,
"resv_name" : "resv_name",
"extra" : "extra",
"delay_boot" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"reboot" : true,
"cpus" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"standard_output" : "standard_output",
"pre_sus_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"suspend_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"association_id" : 0,
"command" : "command",
"tres_freq" : "tres_freq",
"requeue" : true,
"tres_per_task" : "tres_per_task",
"mail_user" : "mail_user",
"nodes" : "nodes",
"group_id" : 5,
"job_id" : 5,
"comment" : "comment",
"account" : "account",
"required_switches" : 7
}, {
"container" : "container",
"cluster" : "cluster",
"stdin_expanded" : "stdin_expanded",
"time_minimum" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"memory_per_tres" : "memory_per_tres",
"scheduled_nodes" : "scheduled_nodes",
"qos" : "qos",
"resize_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"eligible_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpus_per_tres" : "cpus_per_tres",
"preemptable_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tasks" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"system_comment" : "system_comment",
"federation_siblings_active" : "federation_siblings_active",
"tasks_per_tres" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tasks_per_core" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"accrue_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"dependency" : "dependency",
"group_name" : "group_name",
"profile" : [ "NOT_SET", "NOT_SET" ],
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"tres_per_job" : "tres_per_job",
"failed_node" : "failed_node",
"derived_exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"priority_by_partition" : [ {
"partition" : "partition",
"priority" : 6
}, {
"partition" : "partition",
"priority" : 6
} ],
"maximum_switch_wait_time" : 9,
"core_spec" : 6,
"mcs_label" : "mcs_label",
"required_nodes" : "required_nodes",
"tres_bind" : "tres_bind",
"user_id" : 9,
"selinux_context" : "selinux_context",
"exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"federation_origin" : "federation_origin",
"container_id" : "container_id",
"shared" : [ "none", "none" ],
"tasks_per_board" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user_name" : "user_name",
"stderr_expanded" : "stderr_expanded",
"flags" : [ "KILL_INVALID_DEPENDENCY", "KILL_INVALID_DEPENDENCY" ],
"standard_input" : "standard_input",
"admin_comment" : "admin_comment",
"cores_per_socket" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"step_id" : {
"sluid" : "sluid",
"job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"step_het_component" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"step_id" : "step_id"
},
"job_state" : [ "PENDING", "PENDING" ],
"tasks_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"current_working_directory" : "current_working_directory",
"standard_error" : "standard_error",
"array_job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"cluster_features" : "cluster_features",
"partition" : "partition",
"segment_size" : 4,
"threads_per_core" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tres_alloc_str" : "tres_alloc_str",
"memory_per_cpu" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpu_frequency_minimum" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"node_count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"power" : {
"flags" : [ "", "" ]
},
"deadline" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"mail_type" : [ "BEGIN", "BEGIN" ],
"memory_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"state_reason" : "state_reason",
"het_job_offset" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"end_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"sockets_per_board" : 5,
"nice" : 1,
"last_sched_evaluation" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tres_per_node" : "tres_per_node",
"burst_buffer" : "burst_buffer",
"licenses" : "licenses",
"excluded_nodes" : "excluded_nodes",
"array_max_tasks" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"het_job_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"sockets_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"prefer" : "prefer",
"time_limit" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"minimum_cpus_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"tasks_per_socket" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"batch_host" : "batch_host",
"max_cpus" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"job_size_str" : [ "job_size_str", "job_size_str" ],
"hold" : true,
"cpu_frequency_maximum" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"features" : "features",
"het_job_id_set" : "het_job_id_set",
"state_description" : "state_description",
"submit_line" : "submit_line",
"array_task_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"licenses_allocated" : "licenses_allocated",
"minimum_tmp_disk_per_node" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"tres_req_str" : "tres_req_str",
"burst_buffer_state" : "burst_buffer_state",
"cron" : "cron",
"allocating_node" : "allocating_node",
"tres_per_socket" : "tres_per_socket",
"array_task_string" : "array_task_string",
"submit_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"wckey" : "wckey",
"max_nodes" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"batch_flag" : true,
"start_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"name" : "name",
"preempt_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"contiguous" : true,
"job_resources" : {
"nodes" : {
"allocation" : [ {
"memory" : {
"used" : 2,
"allocated" : 4
},
"cpus" : {
"count" : 9,
"used" : 3
},
"name" : "name",
"index" : 7,
"sockets" : [ {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
}, {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
} ]
}, {
"memory" : {
"used" : 2,
"allocated" : 4
},
"cpus" : {
"count" : 9,
"used" : 3
},
"name" : "name",
"index" : 7,
"sockets" : [ {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
}, {
"cores" : [ {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
}, {
"index" : 1,
"status" : [ "INVALID", "INVALID" ]
} ],
"index" : 7
} ]
} ],
"count" : 2,
"select_type" : [ "AVAILABLE", "AVAILABLE" ],
"whole" : true,
"list" : "list"
},
"threads_per_core" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpus" : 1,
"select_type" : [ "CPU", "CPU" ]
},
"billable_tres" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"federation_siblings_viable" : "federation_siblings_viable",
"cpus_per_task" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"batch_features" : "batch_features",
"thread_spec" : 1,
"cpu_frequency_governor" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"gres_detail" : [ "gres_detail", "gres_detail" ],
"stdout_expanded" : "stdout_expanded",
"network" : "network",
"restart_cnt" : 1,
"resv_name" : "resv_name",
"extra" : "extra",
"delay_boot" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"reboot" : true,
"cpus" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"standard_output" : "standard_output",
"pre_sus_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"suspend_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"association_id" : 0,
"command" : "command",
"tres_freq" : "tres_freq",
"requeue" : true,
"tres_per_task" : "tres_per_task",
"mail_user" : "mail_user",
"nodes" : "nodes",
"group_id" : 5,
"job_id" : 5,
"comment" : "comment",
"account" : "account",
"required_switches" : 7
} ],
"last_update" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
job(s) state information
[v0.0.44_openapi_job_info_resp](https://slurm.schedmd.com/rest_api.html)
#### default
job(s) state information
[v0.0.44_openapi_job_info_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurm/v0.0.44/licenses/
```
get all Slurm tracked license info ( slurmV0044GetLicenses )
### Return type
[v0.0.44_openapi_licenses_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"licenses" : [ {
"Used" : 6,
"LastUpdate" : 7,
"Total" : 0,
"Remote" : true,
"LastConsumed" : 5,
"LastDeficit" : 2,
"LicenseName" : "LicenseName",
"Free" : 1,
"Nodes" : "Nodes",
"Reserved" : 5
}, {
"Used" : 6,
"LastUpdate" : 7,
"Total" : 0,
"Remote" : true,
"LastConsumed" : 5,
"LastDeficit" : 2,
"LicenseName" : "LicenseName",
"Free" : 1,
"Nodes" : "Nodes",
"Reserved" : 5
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"last_update" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
results of get all licenses
[v0.0.44_openapi_licenses_resp](https://slurm.schedmd.com/rest_api.html)
#### default
results of get all licenses
[v0.0.44_openapi_licenses_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurm/v0.0.44/node/{node_name}
```
get node info ( slurmV0044GetNode )
### Path parameters
node_name (required)
Path Parameter — Node name default: null
### Query parameters
update_time (optional)
Query Parameter — Query jobs updated more recently than this time (UNIX timestamp) default: null
flags (optional)
Query Parameter — Query flags default: null
### Return type
[v0.0.44_openapi_nodes_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"nodes" : [ {
"reason" : "reason",
"gpu_spec" : "gpu_spec",
"slurmd_start_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"features" : [ "features", "features" ],
"hostname" : "hostname",
"cores" : 6,
"reason_changed_at" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"reservation" : "reservation",
"tres" : "tres",
"cpu_binding" : 5,
"state" : [ "INVALID", "INVALID" ],
"sockets" : 9,
"energy" : {
"current_watts" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"base_consumed_energy" : 3,
"last_collected" : 7,
"consumed_energy" : 2,
"previous_consumed_energy" : 4,
"average_watts" : 9
},
"partitions" : [ "partitions", "partitions" ],
"topology" : "topology",
"gres_drained" : "gres_drained",
"weight" : 8,
"version" : "version",
"gres_used" : "gres_used",
"mcs_label" : "mcs_label",
"real_memory" : 1,
"instance_id" : "instance_id",
"burstbuffer_network_address" : "burstbuffer_network_address",
"port" : 1,
"name" : "name",
"resume_after" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"temporary_disk" : 6,
"tres_used" : "tres_used",
"effective_cpus" : 7,
"instance_type" : "instance_type",
"external_sensors" : "{}",
"cert_flags" : [ "TOKEN_SET", "TOKEN_SET" ],
"res_cores_per_gpu" : 6,
"boards" : 0,
"alloc_cpus" : 1,
"active_features" : [ "active_features", "active_features" ],
"reason_set_by_user" : "reason_set_by_user",
"free_mem" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"alloc_idle_cpus" : 4,
"extra" : "extra",
"operating_system" : "operating_system",
"power" : "{}",
"tls_cert_last_renewal" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"architecture" : "architecture",
"owner" : "owner",
"cluster_name" : "cluster_name",
"address" : "address",
"cpus" : 2,
"tres_weighted" : 5.025004791520295,
"gres" : "gres",
"threads" : 9,
"boot_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"alloc_memory" : 7,
"specialized_memory" : 1,
"specialized_cpus" : "specialized_cpus",
"specialized_cores" : 1,
"last_busy" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"comment" : "comment",
"next_state_after_reboot" : [ "INVALID", "INVALID" ],
"cpu_load" : 5
}, {
"reason" : "reason",
"gpu_spec" : "gpu_spec",
"slurmd_start_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"features" : [ "features", "features" ],
"hostname" : "hostname",
"cores" : 6,
"reason_changed_at" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"reservation" : "reservation",
"tres" : "tres",
"cpu_binding" : 5,
"state" : [ "INVALID", "INVALID" ],
"sockets" : 9,
"energy" : {
"current_watts" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"base_consumed_energy" : 3,
"last_collected" : 7,
"consumed_energy" : 2,
"previous_consumed_energy" : 4,
"average_watts" : 9
},
"partitions" : [ "partitions", "partitions" ],
"topology" : "topology",
"gres_drained" : "gres_drained",
"weight" : 8,
"version" : "version",
"gres_used" : "gres_used",
"mcs_label" : "mcs_label",
"real_memory" : 1,
"instance_id" : "instance_id",
"burstbuffer_network_address" : "burstbuffer_network_address",
"port" : 1,
"name" : "name",
"resume_after" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"temporary_disk" : 6,
"tres_used" : "tres_used",
"effective_cpus" : 7,
"instance_type" : "instance_type",
"external_sensors" : "{}",
"cert_flags" : [ "TOKEN_SET", "TOKEN_SET" ],
"res_cores_per_gpu" : 6,
"boards" : 0,
"alloc_cpus" : 1,
"active_features" : [ "active_features", "active_features" ],
"reason_set_by_user" : "reason_set_by_user",
"free_mem" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"alloc_idle_cpus" : 4,
"extra" : "extra",
"operating_system" : "operating_system",
"power" : "{}",
"tls_cert_last_renewal" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"architecture" : "architecture",
"owner" : "owner",
"cluster_name" : "cluster_name",
"address" : "address",
"cpus" : 2,
"tres_weighted" : 5.025004791520295,
"gres" : "gres",
"threads" : 9,
"boot_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"alloc_memory" : 7,
"specialized_memory" : 1,
"specialized_cpus" : "specialized_cpus",
"specialized_cores" : 1,
"last_busy" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"comment" : "comment",
"next_state_after_reboot" : [ "INVALID", "INVALID" ],
"cpu_load" : 5
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"last_update" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
node information
[v0.0.44_openapi_nodes_resp](https://slurm.schedmd.com/rest_api.html)
#### default
node information
[v0.0.44_openapi_nodes_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurm/v0.0.44/nodes/
```
get node(s) info ( slurmV0044GetNodes )
### Query parameters
update_time (optional)
Query Parameter — Query jobs updated more recently than this time (UNIX timestamp) default: null
flags (optional)
Query Parameter — Query flags default: null
### Return type
[v0.0.44_openapi_nodes_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"nodes" : [ {
"reason" : "reason",
"gpu_spec" : "gpu_spec",
"slurmd_start_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"features" : [ "features", "features" ],
"hostname" : "hostname",
"cores" : 6,
"reason_changed_at" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"reservation" : "reservation",
"tres" : "tres",
"cpu_binding" : 5,
"state" : [ "INVALID", "INVALID" ],
"sockets" : 9,
"energy" : {
"current_watts" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"base_consumed_energy" : 3,
"last_collected" : 7,
"consumed_energy" : 2,
"previous_consumed_energy" : 4,
"average_watts" : 9
},
"partitions" : [ "partitions", "partitions" ],
"topology" : "topology",
"gres_drained" : "gres_drained",
"weight" : 8,
"version" : "version",
"gres_used" : "gres_used",
"mcs_label" : "mcs_label",
"real_memory" : 1,
"instance_id" : "instance_id",
"burstbuffer_network_address" : "burstbuffer_network_address",
"port" : 1,
"name" : "name",
"resume_after" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"temporary_disk" : 6,
"tres_used" : "tres_used",
"effective_cpus" : 7,
"instance_type" : "instance_type",
"external_sensors" : "{}",
"cert_flags" : [ "TOKEN_SET", "TOKEN_SET" ],
"res_cores_per_gpu" : 6,
"boards" : 0,
"alloc_cpus" : 1,
"active_features" : [ "active_features", "active_features" ],
"reason_set_by_user" : "reason_set_by_user",
"free_mem" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"alloc_idle_cpus" : 4,
"extra" : "extra",
"operating_system" : "operating_system",
"power" : "{}",
"tls_cert_last_renewal" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"architecture" : "architecture",
"owner" : "owner",
"cluster_name" : "cluster_name",
"address" : "address",
"cpus" : 2,
"tres_weighted" : 5.025004791520295,
"gres" : "gres",
"threads" : 9,
"boot_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"alloc_memory" : 7,
"specialized_memory" : 1,
"specialized_cpus" : "specialized_cpus",
"specialized_cores" : 1,
"last_busy" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"comment" : "comment",
"next_state_after_reboot" : [ "INVALID", "INVALID" ],
"cpu_load" : 5
}, {
"reason" : "reason",
"gpu_spec" : "gpu_spec",
"slurmd_start_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"features" : [ "features", "features" ],
"hostname" : "hostname",
"cores" : 6,
"reason_changed_at" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"reservation" : "reservation",
"tres" : "tres",
"cpu_binding" : 5,
"state" : [ "INVALID", "INVALID" ],
"sockets" : 9,
"energy" : {
"current_watts" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"base_consumed_energy" : 3,
"last_collected" : 7,
"consumed_energy" : 2,
"previous_consumed_energy" : 4,
"average_watts" : 9
},
"partitions" : [ "partitions", "partitions" ],
"topology" : "topology",
"gres_drained" : "gres_drained",
"weight" : 8,
"version" : "version",
"gres_used" : "gres_used",
"mcs_label" : "mcs_label",
"real_memory" : 1,
"instance_id" : "instance_id",
"burstbuffer_network_address" : "burstbuffer_network_address",
"port" : 1,
"name" : "name",
"resume_after" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"temporary_disk" : 6,
"tres_used" : "tres_used",
"effective_cpus" : 7,
"instance_type" : "instance_type",
"external_sensors" : "{}",
"cert_flags" : [ "TOKEN_SET", "TOKEN_SET" ],
"res_cores_per_gpu" : 6,
"boards" : 0,
"alloc_cpus" : 1,
"active_features" : [ "active_features", "active_features" ],
"reason_set_by_user" : "reason_set_by_user",
"free_mem" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"alloc_idle_cpus" : 4,
"extra" : "extra",
"operating_system" : "operating_system",
"power" : "{}",
"tls_cert_last_renewal" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"architecture" : "architecture",
"owner" : "owner",
"cluster_name" : "cluster_name",
"address" : "address",
"cpus" : 2,
"tres_weighted" : 5.025004791520295,
"gres" : "gres",
"threads" : 9,
"boot_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"alloc_memory" : 7,
"specialized_memory" : 1,
"specialized_cpus" : "specialized_cpus",
"specialized_cores" : 1,
"last_busy" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"comment" : "comment",
"next_state_after_reboot" : [ "INVALID", "INVALID" ],
"cpu_load" : 5
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"last_update" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
node(s) information
[v0.0.44_openapi_nodes_resp](https://slurm.schedmd.com/rest_api.html)
#### default
node(s) information
[v0.0.44_openapi_nodes_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurm/v0.0.44/partition/{partition_name}
```
get partition info ( slurmV0044GetPartition )
### Path parameters
partition_name (required)
Path Parameter — Partition name default: null
### Query parameters
update_time (optional)
Query Parameter — Query partitions updated more recently than this time (UNIX timestamp) default: null
flags (optional)
Query Parameter — Query flags default: null
### Return type
[v0.0.44_openapi_partition_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"partitions" : [ {
"cluster" : "cluster",
"cpus" : {
"task_binding" : 6,
"total" : 1
},
"topology" : "topology",
"timeouts" : {
"resume" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"suspend" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"groups" : {
"allowed" : "allowed"
},
"alternate" : "alternate",
"select_type" : [ "CPU", "CPU" ],
"suspend_time" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"priority" : {
"tier" : 4,
"job_factor" : 2
},
"node_sets" : "node_sets",
"maximums" : {
"shares" : 7,
"nodes" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"over_time_limit" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpus_per_node" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"cpus_per_socket" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"partition_memory_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"oversubscribe" : {
"jobs" : 9,
"flags" : [ "force", "force" ]
},
"memory_per_cpu" : 2,
"time" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"partition_memory_per_cpu" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"nodes" : {
"configured" : "configured",
"total" : 0,
"allowed_allocation" : "allowed_allocation"
},
"partition" : {
"state" : [ "INACTIVE", "INACTIVE" ]
},
"qos" : {
"deny" : "deny",
"allowed" : "allowed",
"assigned" : "assigned"
},
"defaults" : {
"partition_memory_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"memory_per_cpu" : 5,
"time" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"job" : "job",
"partition_memory_per_cpu" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"name" : "name",
"tres" : {
"configured" : "configured",
"billing_weights" : "billing_weights"
},
"accounts" : {
"deny" : "deny",
"allowed" : "allowed"
},
"minimums" : {
"nodes" : 3
},
"grace_time" : 5
}, {
"cluster" : "cluster",
"cpus" : {
"task_binding" : 6,
"total" : 1
},
"topology" : "topology",
"timeouts" : {
"resume" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"suspend" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"groups" : {
"allowed" : "allowed"
},
"alternate" : "alternate",
"select_type" : [ "CPU", "CPU" ],
"suspend_time" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"priority" : {
"tier" : 4,
"job_factor" : 2
},
"node_sets" : "node_sets",
"maximums" : {
"shares" : 7,
"nodes" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"over_time_limit" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpus_per_node" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"cpus_per_socket" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"partition_memory_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"oversubscribe" : {
"jobs" : 9,
"flags" : [ "force", "force" ]
},
"memory_per_cpu" : 2,
"time" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"partition_memory_per_cpu" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"nodes" : {
"configured" : "configured",
"total" : 0,
"allowed_allocation" : "allowed_allocation"
},
"partition" : {
"state" : [ "INACTIVE", "INACTIVE" ]
},
"qos" : {
"deny" : "deny",
"allowed" : "allowed",
"assigned" : "assigned"
},
"defaults" : {
"partition_memory_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"memory_per_cpu" : 5,
"time" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"job" : "job",
"partition_memory_per_cpu" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"name" : "name",
"tres" : {
"configured" : "configured",
"billing_weights" : "billing_weights"
},
"accounts" : {
"deny" : "deny",
"allowed" : "allowed"
},
"minimums" : {
"nodes" : 3
},
"grace_time" : 5
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"last_update" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
partition information
[v0.0.44_openapi_partition_resp](https://slurm.schedmd.com/rest_api.html)
#### default
partition information
[v0.0.44_openapi_partition_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurm/v0.0.44/partitions/
```
get all partition info ( slurmV0044GetPartitions )
### Query parameters
update_time (optional)
Query Parameter — Query partitions updated more recently than this time (UNIX timestamp) default: null
flags (optional)
Query Parameter — Query flags default: null
### Return type
[v0.0.44_openapi_partition_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"partitions" : [ {
"cluster" : "cluster",
"cpus" : {
"task_binding" : 6,
"total" : 1
},
"topology" : "topology",
"timeouts" : {
"resume" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"suspend" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"groups" : {
"allowed" : "allowed"
},
"alternate" : "alternate",
"select_type" : [ "CPU", "CPU" ],
"suspend_time" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"priority" : {
"tier" : 4,
"job_factor" : 2
},
"node_sets" : "node_sets",
"maximums" : {
"shares" : 7,
"nodes" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"over_time_limit" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpus_per_node" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"cpus_per_socket" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"partition_memory_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"oversubscribe" : {
"jobs" : 9,
"flags" : [ "force", "force" ]
},
"memory_per_cpu" : 2,
"time" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"partition_memory_per_cpu" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"nodes" : {
"configured" : "configured",
"total" : 0,
"allowed_allocation" : "allowed_allocation"
},
"partition" : {
"state" : [ "INACTIVE", "INACTIVE" ]
},
"qos" : {
"deny" : "deny",
"allowed" : "allowed",
"assigned" : "assigned"
},
"defaults" : {
"partition_memory_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"memory_per_cpu" : 5,
"time" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"job" : "job",
"partition_memory_per_cpu" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"name" : "name",
"tres" : {
"configured" : "configured",
"billing_weights" : "billing_weights"
},
"accounts" : {
"deny" : "deny",
"allowed" : "allowed"
},
"minimums" : {
"nodes" : 3
},
"grace_time" : 5
}, {
"cluster" : "cluster",
"cpus" : {
"task_binding" : 6,
"total" : 1
},
"topology" : "topology",
"timeouts" : {
"resume" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"suspend" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"groups" : {
"allowed" : "allowed"
},
"alternate" : "alternate",
"select_type" : [ "CPU", "CPU" ],
"suspend_time" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"priority" : {
"tier" : 4,
"job_factor" : 2
},
"node_sets" : "node_sets",
"maximums" : {
"shares" : 7,
"nodes" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"over_time_limit" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"cpus_per_node" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"cpus_per_socket" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"partition_memory_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"oversubscribe" : {
"jobs" : 9,
"flags" : [ "force", "force" ]
},
"memory_per_cpu" : 2,
"time" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"partition_memory_per_cpu" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"nodes" : {
"configured" : "configured",
"total" : 0,
"allowed_allocation" : "allowed_allocation"
},
"partition" : {
"state" : [ "INACTIVE", "INACTIVE" ]
},
"qos" : {
"deny" : "deny",
"allowed" : "allowed",
"assigned" : "assigned"
},
"defaults" : {
"partition_memory_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"memory_per_cpu" : 5,
"time" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"job" : "job",
"partition_memory_per_cpu" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"name" : "name",
"tres" : {
"configured" : "configured",
"billing_weights" : "billing_weights"
},
"accounts" : {
"deny" : "deny",
"allowed" : "allowed"
},
"minimums" : {
"nodes" : 3
},
"grace_time" : 5
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"last_update" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
partition information
[v0.0.44_openapi_partition_resp](https://slurm.schedmd.com/rest_api.html)
#### default
partition information
[v0.0.44_openapi_partition_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurm/v0.0.44/ping/
```
ping test ( slurmV0044GetPing )
### Return type
[v0.0.44_openapi_ping_array_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"pings" : [ {
"mode" : "mode",
"responding" : true,
"hostname" : "hostname",
"latency" : 0,
"pinged" : "pinged",
"primary" : true
}, {
"mode" : "mode",
"responding" : true,
"hostname" : "hostname",
"latency" : 0,
"pinged" : "pinged",
"primary" : true
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
results of ping test
[v0.0.44_openapi_ping_array_resp](https://slurm.schedmd.com/rest_api.html)
#### default
results of ping test
[v0.0.44_openapi_ping_array_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurm/v0.0.44/reconfigure/
```
request slurmctld reconfigure ( slurmV0044GetReconfigure )
### Return type
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
reconfigure request result
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
#### default
reconfigure request result
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurm/v0.0.44/reservation/{reservation_name}
```
get reservation info ( slurmV0044GetReservation )
### Path parameters
reservation_name (required)
Path Parameter — Reservation name default: null
### Query parameters
update_time (optional)
Query Parameter — Query reservations updated more recently than this time (UNIX timestamp) default: null
### Return type
[v0.0.44_openapi_reservation_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"reservations" : [ {
"end_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"flags" : [ "MAINT", "MAINT" ],
"groups" : "groups",
"users" : "users",
"max_start_delay" : 6,
"features" : "features",
"start_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"burst_buffer" : "burst_buffer",
"licenses" : "licenses",
"partition" : "partition",
"watts" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"core_specializations" : [ {
"node" : "node",
"core" : "core"
}, {
"node" : "node",
"core" : "core"
} ],
"name" : "name",
"tres" : "tres",
"accounts" : "accounts",
"node_count" : 1,
"node_list" : "node_list",
"purge_completed" : {
"time" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"core_count" : 0
}, {
"end_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"flags" : [ "MAINT", "MAINT" ],
"groups" : "groups",
"users" : "users",
"max_start_delay" : 6,
"features" : "features",
"start_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"burst_buffer" : "burst_buffer",
"licenses" : "licenses",
"partition" : "partition",
"watts" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"core_specializations" : [ {
"node" : "node",
"core" : "core"
}, {
"node" : "node",
"core" : "core"
} ],
"name" : "name",
"tres" : "tres",
"accounts" : "accounts",
"node_count" : 1,
"node_list" : "node_list",
"purge_completed" : {
"time" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"core_count" : 0
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"last_update" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
reservation information
[v0.0.44_openapi_reservation_resp](https://slurm.schedmd.com/rest_api.html)
#### default
reservation information
[v0.0.44_openapi_reservation_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurm/v0.0.44/reservations/
```
get all reservation info ( slurmV0044GetReservations )
### Query parameters
update_time (optional)
Query Parameter — Query reservations updated more recently than this time (UNIX timestamp) default: null
### Return type
[v0.0.44_openapi_reservation_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"reservations" : [ {
"end_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"flags" : [ "MAINT", "MAINT" ],
"groups" : "groups",
"users" : "users",
"max_start_delay" : 6,
"features" : "features",
"start_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"burst_buffer" : "burst_buffer",
"licenses" : "licenses",
"partition" : "partition",
"watts" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"core_specializations" : [ {
"node" : "node",
"core" : "core"
}, {
"node" : "node",
"core" : "core"
} ],
"name" : "name",
"tres" : "tres",
"accounts" : "accounts",
"node_count" : 1,
"node_list" : "node_list",
"purge_completed" : {
"time" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"core_count" : 0
}, {
"end_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"flags" : [ "MAINT", "MAINT" ],
"groups" : "groups",
"users" : "users",
"max_start_delay" : 6,
"features" : "features",
"start_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"burst_buffer" : "burst_buffer",
"licenses" : "licenses",
"partition" : "partition",
"watts" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"core_specializations" : [ {
"node" : "node",
"core" : "core"
}, {
"node" : "node",
"core" : "core"
} ],
"name" : "name",
"tres" : "tres",
"accounts" : "accounts",
"node_count" : 1,
"node_list" : "node_list",
"purge_completed" : {
"time" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"core_count" : 0
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"last_update" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
reservation information
[v0.0.44_openapi_reservation_resp](https://slurm.schedmd.com/rest_api.html)
#### default
reservation information
[v0.0.44_openapi_reservation_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurm/v0.0.44/resources/{job_id}
```
get resource layout info ( slurmV0044GetResources )
### Path parameters
job_id (required)
Path Parameter — Job ID default: null
### Return type
[v0.0.44_openapi_resource_layout_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"nodes" : [ {
"node" : "node",
"channel" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"gres" : [ {
"name" : "name",
"count" : 5,
"index" : "index",
"type" : "type"
}, {
"name" : "name",
"count" : 5,
"index" : "index",
"type" : "type"
} ],
"cores_per_socket" : 6,
"mem_alloc" : 1,
"core_bitmap" : "core_bitmap",
"sockets_per_node" : 0
}, {
"node" : "node",
"channel" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"gres" : [ {
"name" : "name",
"count" : 5,
"index" : "index",
"type" : "type"
}, {
"name" : "name",
"count" : 5,
"index" : "index",
"type" : "type"
} ],
"cores_per_socket" : 6,
"mem_alloc" : 1,
"core_bitmap" : "core_bitmap",
"sockets_per_node" : 0
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
resource layout information
[v0.0.44_openapi_resource_layout_resp](https://slurm.schedmd.com/rest_api.html)
#### default
resource layout information
[v0.0.44_openapi_resource_layout_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurm/v0.0.44/shares
```
get fairshare info ( slurmV0044GetShares )
### Query parameters
accounts (optional)
Query Parameter — Accounts to query default: null
users (optional)
Query Parameter — Users to query default: null
### Return type
[v0.0.44_openapi_shares_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"shares" : {
"shares" : [ {
"cluster" : "cluster",
"parent" : "parent",
"shares_normalized" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"usage" : 1,
"fairshare" : {
"level" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"factor" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
}
},
"type" : [ "USER", "USER" ],
"effective_usage" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"shares" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"partition" : "partition",
"usage_normalized" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"name" : "name",
"tres" : {
"run_seconds" : [ {
"name" : "name",
"value" : {
"number" : 2,
"set" : true,
"infinite" : true
}
}, {
"name" : "name",
"value" : {
"number" : 2,
"set" : true,
"infinite" : true
}
} ],
"usage" : [ {
"name" : "name",
"value" : 6.027456183070403
}, {
"name" : "name",
"value" : 6.027456183070403
} ],
"group_minutes" : [ {
"name" : "name",
"value" : {
"number" : 2,
"set" : true,
"infinite" : true
}
}, {
"name" : "name",
"value" : {
"number" : 2,
"set" : true,
"infinite" : true
}
} ]
},
"id" : 0
}, {
"cluster" : "cluster",
"parent" : "parent",
"shares_normalized" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"usage" : 1,
"fairshare" : {
"level" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"factor" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
}
},
"type" : [ "USER", "USER" ],
"effective_usage" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"shares" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"partition" : "partition",
"usage_normalized" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"name" : "name",
"tres" : {
"run_seconds" : [ {
"name" : "name",
"value" : {
"number" : 2,
"set" : true,
"infinite" : true
}
}, {
"name" : "name",
"value" : {
"number" : 2,
"set" : true,
"infinite" : true
}
} ],
"usage" : [ {
"name" : "name",
"value" : 6.027456183070403
}, {
"name" : "name",
"value" : 6.027456183070403
} ],
"group_minutes" : [ {
"name" : "name",
"value" : {
"number" : 2,
"set" : true,
"infinite" : true
}
}, {
"name" : "name",
"value" : {
"number" : 2,
"set" : true,
"infinite" : true
}
} ]
},
"id" : 0
} ],
"total_shares" : 5
},
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
shares information
[v0.0.44_openapi_shares_resp](https://slurm.schedmd.com/rest_api.html)
#### default
shares information
[v0.0.44_openapi_shares_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurm/v0.0.44/job/{job_id}
```
update job ( slurmV0044PostJob )
### Path parameters
job_id (required)
Path Parameter — Job ID default: null
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_job_desc_msg [v0.0.44_job_desc_msg](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Return type
[v0.0.44_openapi_job_post_response](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"results" : [ {
"job_id" : 0,
"why" : "why",
"error_code" : 6,
"step_id" : "step_id",
"error" : "error"
}, {
"job_id" : 0,
"why" : "why",
"error_code" : 6,
"step_id" : "step_id",
"error" : "error"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
job update result
[v0.0.44_openapi_job_post_response](https://slurm.schedmd.com/rest_api.html)
#### default
job update result
[v0.0.44_openapi_job_post_response](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurm/v0.0.44/job/allocate
```
submit new job allocation without any steps that must be signaled to stop ( slurmV0044PostJobAllocate )
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_job_alloc_req [v0.0.44_job_alloc_req](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Return type
[v0.0.44_openapi_job_alloc_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"job_id" : 0,
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"job_submit_user_msg" : "job_submit_user_msg",
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
job allocation response
[v0.0.44_openapi_job_alloc_resp](https://slurm.schedmd.com/rest_api.html)
#### default
job allocation response
[v0.0.44_openapi_job_alloc_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurm/v0.0.44/job/submit
```
submit new job ( slurmV0044PostJobSubmit )
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_job_submit_req [v0.0.44_job_submit_req](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Return type
[v0.0.44_openapi_job_submit_response](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"job_id" : 0,
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"step_id" : "step_id",
"job_submit_user_msg" : "job_submit_user_msg",
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
job submission response
[v0.0.44_openapi_job_submit_response](https://slurm.schedmd.com/rest_api.html)
#### default
job submission response
[v0.0.44_openapi_job_submit_response](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurm/v0.0.44/new/node/
```
create node ( slurmV0044PostNewNode )
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_openapi_create_node_req [v0.0.44_openapi_create_node_req](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Return type
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
node create request result
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
#### default
node create request result
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurm/v0.0.44/node/{node_name}
```
update node properties ( slurmV0044PostNode )
### Path parameters
node_name (required)
Path Parameter — Node name default: null
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_update_node_msg [v0.0.44_update_node_msg](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Return type
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
node update request result
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
#### default
node update request result
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurm/v0.0.44/nodes/
```
batch update node(s) ( slurmV0044PostNodes )
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_update_node_msg [v0.0.44_update_node_msg](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Return type
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
batch node update request result
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
#### default
batch node update request result
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurm/v0.0.44/reservation
```
create or update a reservation ( slurmV0044PostReservation )
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_reservation_desc_msg [v0.0.44_reservation_desc_msg](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Return type
[v0.0.44_openapi_reservation_mod_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"reservations" : [ {
"end_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"flags" : [ "MAINT", "MAINT" ],
"groups" : [ "groups", "groups" ],
"users" : [ "users", "users" ],
"max_start_delay" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"duration" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"features" : "features",
"start_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"burst_buffer" : "burst_buffer",
"licenses" : [ "licenses", "licenses" ],
"partition" : "partition",
"name" : "name",
"comment" : "comment",
"tres" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"accounts" : [ "accounts", "accounts" ],
"node_count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"node_list" : [ "node_list", "node_list" ],
"purge_completed" : {
"time" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"core_count" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}, {
"end_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"flags" : [ "MAINT", "MAINT" ],
"groups" : [ "groups", "groups" ],
"users" : [ "users", "users" ],
"max_start_delay" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"duration" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"features" : "features",
"start_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"burst_buffer" : "burst_buffer",
"licenses" : [ "licenses", "licenses" ],
"partition" : "partition",
"name" : "name",
"comment" : "comment",
"tres" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"accounts" : [ "accounts", "accounts" ],
"node_count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"node_list" : [ "node_list", "node_list" ],
"purge_completed" : {
"time" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"core_count" : {
"number" : 5,
"set" : true,
"infinite" : true
}
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
reservation description
[v0.0.44_openapi_reservation_mod_resp](https://slurm.schedmd.com/rest_api.html)
#### default
reservation description
[v0.0.44_openapi_reservation_mod_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurm/v0.0.44/reservations/
```
create or update reservations ( slurmV0044PostReservations )
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_reservation_mod_req [v0.0.44_reservation_mod_req](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Return type
[v0.0.44_openapi_reservation_mod_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"reservations" : [ {
"end_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"flags" : [ "MAINT", "MAINT" ],
"groups" : [ "groups", "groups" ],
"users" : [ "users", "users" ],
"max_start_delay" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"duration" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"features" : "features",
"start_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"burst_buffer" : "burst_buffer",
"licenses" : [ "licenses", "licenses" ],
"partition" : "partition",
"name" : "name",
"comment" : "comment",
"tres" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"accounts" : [ "accounts", "accounts" ],
"node_count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"node_list" : [ "node_list", "node_list" ],
"purge_completed" : {
"time" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"core_count" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}, {
"end_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"flags" : [ "MAINT", "MAINT" ],
"groups" : [ "groups", "groups" ],
"users" : [ "users", "users" ],
"max_start_delay" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"duration" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"features" : "features",
"start_time" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"burst_buffer" : "burst_buffer",
"licenses" : [ "licenses", "licenses" ],
"partition" : "partition",
"name" : "name",
"comment" : "comment",
"tres" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"accounts" : [ "accounts", "accounts" ],
"node_count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"node_list" : [ "node_list", "node_list" ],
"purge_completed" : {
"time" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"core_count" : {
"number" : 5,
"set" : true,
"infinite" : true
}
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
reservation descriptions
[v0.0.44_openapi_reservation_mod_resp](https://slurm.schedmd.com/rest_api.html)
#### default
reservation descriptions
[v0.0.44_openapi_reservation_mod_resp](https://slurm.schedmd.com/rest_api.html)
# Slurmdb
[Up](https://slurm.schedmd.com/rest_api.html)
```text
delete /slurmdb/v0.0.44/account/{account_name}
```
Delete account ( slurmdbV0044DeleteAccount )
### Path parameters
account_name (required)
Path Parameter — Account name default: null
### Return type
[v0.0.44_openapi_accounts_removed_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"removed_accounts" : [ "removed_accounts", "removed_accounts" ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
Status of account deletion request
[v0.0.44_openapi_accounts_removed_resp](https://slurm.schedmd.com/rest_api.html)
#### default
Status of account deletion request
[v0.0.44_openapi_accounts_removed_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
delete /slurmdb/v0.0.44/association/
```
Delete association ( slurmdbV0044DeleteAssociation )
### Query parameters
account (optional)
Query Parameter — CSV accounts list default: null
cluster (optional)
Query Parameter — CSV clusters list default: null
default_qos (optional)
Query Parameter — CSV QOS list default: null
Include deleted associations (optional)
Query Parameter — default: null
Include usage (optional)
Query Parameter — default: null
Filter to only defaults (optional)
Query Parameter — default: null
Include the raw QOS or delta_qos (optional)
Query Parameter — default: null
Include sub acct information (optional)
Query Parameter — default: null
Exclude parent id/name (optional)
Query Parameter — default: null
Exclude limits from parents (optional)
Query Parameter — default: null
format (optional)
Query Parameter — Ignored; process JSON manually to control output format default: null
id (optional)
Query Parameter — CSV ID list default: null
parent_account (optional)
Query Parameter — CSV names of parent account default: null
partition (optional)
Query Parameter — CSV partition name list default: null
qos (optional)
Query Parameter — CSV QOS list default: null
usage_end (optional)
Query Parameter — Usage end (UNIX timestamp) default: null
usage_start (optional)
Query Parameter — Usage start (UNIX timestamp) default: null
user (optional)
Query Parameter — CSV user list default: null
### Return type
[v0.0.44_openapi_assocs_removed_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"removed_associations" : [ "removed_associations", "removed_associations" ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
Status of associations delete request
[v0.0.44_openapi_assocs_removed_resp](https://slurm.schedmd.com/rest_api.html)
#### default
Status of associations delete request
[v0.0.44_openapi_assocs_removed_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
delete /slurmdb/v0.0.44/associations/
```
Delete associations ( slurmdbV0044DeleteAssociations )
### Query parameters
account (optional)
Query Parameter — CSV accounts list default: null
cluster (optional)
Query Parameter — CSV clusters list default: null
default_qos (optional)
Query Parameter — CSV QOS list default: null
Include deleted associations (optional)
Query Parameter — default: null
Include usage (optional)
Query Parameter — default: null
Filter to only defaults (optional)
Query Parameter — default: null
Include the raw QOS or delta_qos (optional)
Query Parameter — default: null
Include sub acct information (optional)
Query Parameter — default: null
Exclude parent id/name (optional)
Query Parameter — default: null
Exclude limits from parents (optional)
Query Parameter — default: null
format (optional)
Query Parameter — Ignored; process JSON manually to control output format default: null
id (optional)
Query Parameter — CSV ID list default: null
parent_account (optional)
Query Parameter — CSV names of parent account default: null
partition (optional)
Query Parameter — CSV partition name list default: null
qos (optional)
Query Parameter — CSV QOS list default: null
usage_end (optional)
Query Parameter — Usage end (UNIX timestamp) default: null
usage_start (optional)
Query Parameter — Usage start (UNIX timestamp) default: null
user (optional)
Query Parameter — CSV user list default: null
### Return type
[v0.0.44_openapi_assocs_removed_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"removed_associations" : [ "removed_associations", "removed_associations" ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
List of associations deleted
[v0.0.44_openapi_assocs_removed_resp](https://slurm.schedmd.com/rest_api.html)
#### default
List of associations deleted
[v0.0.44_openapi_assocs_removed_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
delete /slurmdb/v0.0.44/cluster/{cluster_name}
```
Delete cluster ( slurmdbV0044DeleteCluster )
### Path parameters
cluster_name (required)
Path Parameter — Cluster name default: null
### Query parameters
classification (optional)
Query Parameter — Type of machine default: null
cluster (optional)
Query Parameter — CSV cluster list default: null
federation (optional)
Query Parameter — CSV federation list default: null
flags (optional)
Query Parameter — Query flags default: null
format (optional)
Query Parameter — Ignored; process JSON manually to control output format default: null
rpc_version (optional)
Query Parameter — CSV RPC version list default: null
usage_end (optional)
Query Parameter — Usage end (UNIX timestamp) default: null
usage_start (optional)
Query Parameter — Usage start (UNIX timestamp) default: null
with_deleted (optional)
Query Parameter — Include deleted clusters default: null
with_usage (optional)
Query Parameter — Include usage default: null
### Return type
[v0.0.44_openapi_clusters_removed_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"deleted_clusters" : [ "deleted_clusters", "deleted_clusters" ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
Result of delete cluster request
[v0.0.44_openapi_clusters_removed_resp](https://slurm.schedmd.com/rest_api.html)
#### default
Result of delete cluster request
[v0.0.44_openapi_clusters_removed_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
delete /slurmdb/v0.0.44/qos/{qos}
```
Delete QOS ( slurmdbV0044DeleteSingleQos )
### Path parameters
qos (required)
Path Parameter — QOS name default: null
### Return type
[v0.0.44_openapi_slurmdbd_qos_removed_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"removed_qos" : [ "removed_qos", "removed_qos" ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
results of ping test
[v0.0.44_openapi_slurmdbd_qos_removed_resp](https://slurm.schedmd.com/rest_api.html)
#### default
results of ping test
[v0.0.44_openapi_slurmdbd_qos_removed_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
delete /slurmdb/v0.0.44/user/{name}
```
Delete user ( slurmdbV0044DeleteUser )
### Path parameters
name (required)
Path Parameter — User name default: null
### Return type
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
Result of user delete request
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
#### default
Result of user delete request
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
delete /slurmdb/v0.0.44/wckey/{id}
```
Delete wckey ( slurmdbV0044DeleteWckey )
### Path parameters
id (required)
Path Parameter — WCKey ID default: null
### Return type
[v0.0.44_openapi_wckey_removed_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"deleted_wckeys" : [ "deleted_wckeys", "deleted_wckeys" ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
Result of wckey deletion request
[v0.0.44_openapi_wckey_removed_resp](https://slurm.schedmd.com/rest_api.html)
#### default
Result of wckey deletion request
[v0.0.44_openapi_wckey_removed_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/account/{account_name}
```
Get account info ( slurmdbV0044GetAccount )
### Path parameters
account_name (required)
Path Parameter — Account name default: null
### Query parameters
with_assocs (optional)
Query Parameter — Include associations default: null
with_coords (optional)
Query Parameter — Include coordinators default: null
with_deleted (optional)
Query Parameter — Include deleted default: null
### Return type
[v0.0.44_openapi_accounts_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"accounts" : [ {
"associations" : [ {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
}, {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
} ],
"coordinators" : [ {
"name" : "name",
"direct" : true
}, {
"name" : "name",
"direct" : true
} ],
"organization" : "organization",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"description" : "description"
}, {
"associations" : [ {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
}, {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
} ],
"coordinators" : [ {
"name" : "name",
"direct" : true
}, {
"name" : "name",
"direct" : true
} ],
"organization" : "organization",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"description" : "description"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
List of accounts
[v0.0.44_openapi_accounts_resp](https://slurm.schedmd.com/rest_api.html)
#### default
List of accounts
[v0.0.44_openapi_accounts_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/accounts/
```
Get account list ( slurmdbV0044GetAccounts )
### Query parameters
description (optional)
Query Parameter — CSV description list default: null
DELETED (optional)
Query Parameter — include deleted associations default: null
WithAssociations (optional)
Query Parameter — query includes associations default: null
WithCoordinators (optional)
Query Parameter — query includes coordinators default: null
NoUsersAreCoords (optional)
Query Parameter — remove users as coordinators default: null
UsersAreCoords (optional)
Query Parameter — users are coordinators default: null
### Return type
[v0.0.44_openapi_accounts_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"accounts" : [ {
"associations" : [ {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
}, {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
} ],
"coordinators" : [ {
"name" : "name",
"direct" : true
}, {
"name" : "name",
"direct" : true
} ],
"organization" : "organization",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"description" : "description"
}, {
"associations" : [ {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
}, {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
} ],
"coordinators" : [ {
"name" : "name",
"direct" : true
}, {
"name" : "name",
"direct" : true
} ],
"organization" : "organization",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"description" : "description"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
List of accounts
[v0.0.44_openapi_accounts_resp](https://slurm.schedmd.com/rest_api.html)
#### default
List of accounts
[v0.0.44_openapi_accounts_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/association/
```
Get association info ( slurmdbV0044GetAssociation )
### Query parameters
account (optional)
Query Parameter — CSV accounts list default: null
cluster (optional)
Query Parameter — CSV clusters list default: null
default_qos (optional)
Query Parameter — CSV QOS list default: null
Include deleted associations (optional)
Query Parameter — default: null
Include usage (optional)
Query Parameter — default: null
Filter to only defaults (optional)
Query Parameter — default: null
Include the raw QOS or delta_qos (optional)
Query Parameter — default: null
Include sub acct information (optional)
Query Parameter — default: null
Exclude parent id/name (optional)
Query Parameter — default: null
Exclude limits from parents (optional)
Query Parameter — default: null
format (optional)
Query Parameter — Ignored; process JSON manually to control output format default: null
id (optional)
Query Parameter — CSV ID list default: null
parent_account (optional)
Query Parameter — CSV names of parent account default: null
partition (optional)
Query Parameter — CSV partition name list default: null
qos (optional)
Query Parameter — CSV QOS list default: null
usage_end (optional)
Query Parameter — Usage end (UNIX timestamp) default: null
usage_start (optional)
Query Parameter — Usage start (UNIX timestamp) default: null
user (optional)
Query Parameter — CSV user list default: null
### Return type
[v0.0.44_openapi_assocs_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"associations" : [ {
"lineage" : "lineage",
"cluster" : "cluster",
"shares_raw" : 1,
"max" : {
"jobs" : {
"total" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"active" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"accruing" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"per" : {
"submitted" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"accruing" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"wall_clock" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"tres" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"minutes" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"per" : {
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"per" : {
"node" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"group" : {
"minutes" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"active" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"per" : {
"account" : {
"wall_clock" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
}
},
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"is_default" : true,
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"parent_account" : "parent_account",
"default" : {
"qos" : "qos"
},
"min" : {
"priority_threshold" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"partition" : "partition",
"qos" : [ "qos", "qos" ],
"comment" : "comment",
"id" : 7,
"user" : "user",
"account" : "account"
}, {
"lineage" : "lineage",
"cluster" : "cluster",
"shares_raw" : 1,
"max" : {
"jobs" : {
"total" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"active" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"accruing" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"per" : {
"submitted" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"accruing" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"wall_clock" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"tres" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"minutes" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"per" : {
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"per" : {
"node" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"group" : {
"minutes" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"active" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"per" : {
"account" : {
"wall_clock" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
}
},
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"is_default" : true,
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"parent_account" : "parent_account",
"default" : {
"qos" : "qos"
},
"min" : {
"priority_threshold" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"partition" : "partition",
"qos" : [ "qos", "qos" ],
"comment" : "comment",
"id" : 7,
"user" : "user",
"account" : "account"
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
List of associations
[v0.0.44_openapi_assocs_resp](https://slurm.schedmd.com/rest_api.html)
#### default
List of associations
[v0.0.44_openapi_assocs_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/associations/
```
Get association list ( slurmdbV0044GetAssociations )
### Query parameters
account (optional)
Query Parameter — CSV accounts list default: null
cluster (optional)
Query Parameter — CSV clusters list default: null
default_qos (optional)
Query Parameter — CSV QOS list default: null
Include deleted associations (optional)
Query Parameter — default: null
Include usage (optional)
Query Parameter — default: null
Filter to only defaults (optional)
Query Parameter — default: null
Include the raw QOS or delta_qos (optional)
Query Parameter — default: null
Include sub acct information (optional)
Query Parameter — default: null
Exclude parent id/name (optional)
Query Parameter — default: null
Exclude limits from parents (optional)
Query Parameter — default: null
format (optional)
Query Parameter — Ignored; process JSON manually to control output format default: null
id (optional)
Query Parameter — CSV ID list default: null
parent_account (optional)
Query Parameter — CSV names of parent account default: null
partition (optional)
Query Parameter — CSV partition name list default: null
qos (optional)
Query Parameter — CSV QOS list default: null
usage_end (optional)
Query Parameter — Usage end (UNIX timestamp) default: null
usage_start (optional)
Query Parameter — Usage start (UNIX timestamp) default: null
user (optional)
Query Parameter — CSV user list default: null
### Return type
[v0.0.44_openapi_assocs_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"associations" : [ {
"lineage" : "lineage",
"cluster" : "cluster",
"shares_raw" : 1,
"max" : {
"jobs" : {
"total" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"active" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"accruing" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"per" : {
"submitted" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"accruing" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"wall_clock" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"tres" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"minutes" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"per" : {
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"per" : {
"node" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"group" : {
"minutes" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"active" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"per" : {
"account" : {
"wall_clock" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
}
},
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"is_default" : true,
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"parent_account" : "parent_account",
"default" : {
"qos" : "qos"
},
"min" : {
"priority_threshold" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"partition" : "partition",
"qos" : [ "qos", "qos" ],
"comment" : "comment",
"id" : 7,
"user" : "user",
"account" : "account"
}, {
"lineage" : "lineage",
"cluster" : "cluster",
"shares_raw" : 1,
"max" : {
"jobs" : {
"total" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"active" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"accruing" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"per" : {
"submitted" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"accruing" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"wall_clock" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"tres" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"minutes" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"per" : {
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"per" : {
"node" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"group" : {
"minutes" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"active" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"per" : {
"account" : {
"wall_clock" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
}
},
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"is_default" : true,
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"parent_account" : "parent_account",
"default" : {
"qos" : "qos"
},
"min" : {
"priority_threshold" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"partition" : "partition",
"qos" : [ "qos", "qos" ],
"comment" : "comment",
"id" : 7,
"user" : "user",
"account" : "account"
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
List of associations
[v0.0.44_openapi_assocs_resp](https://slurm.schedmd.com/rest_api.html)
#### default
List of associations
[v0.0.44_openapi_assocs_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/cluster/{cluster_name}
```
Get cluster info ( slurmdbV0044GetCluster )
### Path parameters
cluster_name (required)
Path Parameter — Cluster name default: null
### Query parameters
classification (optional)
Query Parameter — Type of machine default: null
cluster (optional)
Query Parameter — CSV cluster list default: null
federation (optional)
Query Parameter — CSV federation list default: null
flags (optional)
Query Parameter — Query flags default: null
format (optional)
Query Parameter — Ignored; process JSON manually to control output format default: null
rpc_version (optional)
Query Parameter — CSV RPC version list default: null
usage_end (optional)
Query Parameter — Usage end (UNIX timestamp) default: null
usage_start (optional)
Query Parameter — Usage start (UNIX timestamp) default: null
with_deleted (optional)
Query Parameter — Include deleted clusters default: null
with_usage (optional)
Query Parameter — Include usage default: null
### Return type
[v0.0.44_openapi_clusters_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"clusters" : [ {
"associations" : {
"root" : {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
}
},
"controller" : {
"port" : 0,
"host" : "host"
},
"nodes" : "nodes",
"flags" : [ "DELETED", "DELETED" ],
"name" : "name",
"rpc_version" : 6,
"tres" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"select_plugin" : "select_plugin"
}, {
"associations" : {
"root" : {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
}
},
"controller" : {
"port" : 0,
"host" : "host"
},
"nodes" : "nodes",
"flags" : [ "DELETED", "DELETED" ],
"name" : "name",
"rpc_version" : 6,
"tres" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"select_plugin" : "select_plugin"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
Cluster information
[v0.0.44_openapi_clusters_resp](https://slurm.schedmd.com/rest_api.html)
#### default
Cluster information
[v0.0.44_openapi_clusters_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/clusters/
```
Get cluster list ( slurmdbV0044GetClusters )
### Query parameters
update_time (optional)
Query Parameter — Query reservations updated more recently than this time (UNIX timestamp) default: null
### Return type
[v0.0.44_openapi_clusters_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"clusters" : [ {
"associations" : {
"root" : {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
}
},
"controller" : {
"port" : 0,
"host" : "host"
},
"nodes" : "nodes",
"flags" : [ "DELETED", "DELETED" ],
"name" : "name",
"rpc_version" : 6,
"tres" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"select_plugin" : "select_plugin"
}, {
"associations" : {
"root" : {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
}
},
"controller" : {
"port" : 0,
"host" : "host"
},
"nodes" : "nodes",
"flags" : [ "DELETED", "DELETED" ],
"name" : "name",
"rpc_version" : 6,
"tres" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"select_plugin" : "select_plugin"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
List of clusters
[v0.0.44_openapi_clusters_resp](https://slurm.schedmd.com/rest_api.html)
#### default
List of clusters
[v0.0.44_openapi_clusters_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/config
```
Dump all configuration information ( slurmdbV0044GetConfig )
### Return type
[v0.0.44_openapi_slurmdbd_config_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"associations" : [ {
"lineage" : "lineage",
"cluster" : "cluster",
"shares_raw" : 1,
"max" : {
"jobs" : {
"total" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"active" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"accruing" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"per" : {
"submitted" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"accruing" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"wall_clock" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"tres" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"minutes" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"per" : {
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"per" : {
"node" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"group" : {
"minutes" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"active" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"per" : {
"account" : {
"wall_clock" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
}
},
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"is_default" : true,
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"parent_account" : "parent_account",
"default" : {
"qos" : "qos"
},
"min" : {
"priority_threshold" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"partition" : "partition",
"qos" : [ "qos", "qos" ],
"comment" : "comment",
"id" : 7,
"user" : "user",
"account" : "account"
}, {
"lineage" : "lineage",
"cluster" : "cluster",
"shares_raw" : 1,
"max" : {
"jobs" : {
"total" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"active" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"accruing" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"per" : {
"submitted" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"accruing" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"wall_clock" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"tres" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"minutes" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"per" : {
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"per" : {
"node" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"group" : {
"minutes" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"active" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"per" : {
"account" : {
"wall_clock" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
}
},
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"is_default" : true,
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"parent_account" : "parent_account",
"default" : {
"qos" : "qos"
},
"min" : {
"priority_threshold" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"partition" : "partition",
"qos" : [ "qos", "qos" ],
"comment" : "comment",
"id" : 7,
"user" : "user",
"account" : "account"
} ],
"qos" : [ {
"flags" : [ "NOT_SET", "NOT_SET" ],
"name" : "name",
"usage_threshold" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"description" : "description",
"usage_factor" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"id" : 3,
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"limits" : {
"min" : {
"priority_threshold" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"tres" : {
"per" : {
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
}
},
"max" : {
"jobs" : {
"count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"per" : {
"user" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"account" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"active_jobs" : {
"per" : {
"user" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"account" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
}
},
"accruing" : {
"per" : {
"user" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"account" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"tres" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"minutes" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"per" : {
"qos" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"user" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"account" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"per" : {
"node" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"user" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"account" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"wall_clock" : {
"per" : {
"qos" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"job" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"active_jobs" : {
"count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"accruing" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"factor" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"grace_time" : 2
},
"preempt" : {
"mode" : [ "DISABLED", "DISABLED" ],
"exempt_time" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"list" : [ "list", "list" ]
}
}, {
"flags" : [ "NOT_SET", "NOT_SET" ],
"name" : "name",
"usage_threshold" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"description" : "description",
"usage_factor" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"id" : 3,
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"limits" : {
"min" : {
"priority_threshold" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"tres" : {
"per" : {
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
}
},
"max" : {
"jobs" : {
"count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"per" : {
"user" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"account" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"active_jobs" : {
"per" : {
"user" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"account" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
}
},
"accruing" : {
"per" : {
"user" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"account" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"tres" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"minutes" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"per" : {
"qos" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"user" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"account" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"per" : {
"node" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"user" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"account" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"wall_clock" : {
"per" : {
"qos" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"job" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"active_jobs" : {
"count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"accruing" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"factor" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"grace_time" : 2
},
"preempt" : {
"mode" : [ "DISABLED", "DISABLED" ],
"exempt_time" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"list" : [ "list", "list" ]
}
} ],
"wckeys" : [ {
"cluster" : "cluster",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"id" : 9,
"user" : "user"
}, {
"cluster" : "cluster",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"id" : 9,
"user" : "user"
} ],
"instances" : [ {
"cluster" : "cluster",
"instance_id" : "instance_id",
"extra" : "extra",
"node_name" : "node_name",
"time" : {
"time_start" : 1,
"time_end" : 1
},
"instance_type" : "instance_type"
}, {
"cluster" : "cluster",
"instance_id" : "instance_id",
"extra" : "extra",
"node_name" : "node_name",
"time" : {
"time_start" : 1,
"time_end" : 1
},
"instance_type" : "instance_type"
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"tres" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"accounts" : [ {
"associations" : [ {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
}, {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
} ],
"coordinators" : [ {
"name" : "name",
"direct" : true
}, {
"name" : "name",
"direct" : true
} ],
"organization" : "organization",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"description" : "description"
}, {
"associations" : [ {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
}, {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
} ],
"coordinators" : [ {
"name" : "name",
"direct" : true
}, {
"name" : "name",
"direct" : true
} ],
"organization" : "organization",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"description" : "description"
} ],
"clusters" : [ {
"associations" : {
"root" : {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
}
},
"controller" : {
"port" : 0,
"host" : "host"
},
"nodes" : "nodes",
"flags" : [ "DELETED", "DELETED" ],
"name" : "name",
"rpc_version" : 6,
"tres" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"select_plugin" : "select_plugin"
}, {
"associations" : {
"root" : {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
}
},
"controller" : {
"port" : 0,
"host" : "host"
},
"nodes" : "nodes",
"flags" : [ "DELETED", "DELETED" ],
"name" : "name",
"rpc_version" : 6,
"tres" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"select_plugin" : "select_plugin"
} ],
"users" : [ {
"associations" : [ {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
}, {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
} ],
"default" : {
"qos" : 1,
"wckey" : "wckey",
"account" : "account"
},
"administrator_level" : [ "Not Set", "Not Set" ],
"old_name" : "old_name",
"wckeys" : [ {
"cluster" : "cluster",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"id" : 9,
"user" : "user"
}, {
"cluster" : "cluster",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"id" : 9,
"user" : "user"
} ],
"coordinators" : [ {
"name" : "name",
"direct" : true
}, {
"name" : "name",
"direct" : true
} ],
"flags" : [ "NONE", "NONE" ],
"name" : "name"
}, {
"associations" : [ {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
}, {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
} ],
"default" : {
"qos" : 1,
"wckey" : "wckey",
"account" : "account"
},
"administrator_level" : [ "Not Set", "Not Set" ],
"old_name" : "old_name",
"wckeys" : [ {
"cluster" : "cluster",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"id" : 9,
"user" : "user"
}, {
"cluster" : "cluster",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"id" : 9,
"user" : "user"
} ],
"coordinators" : [ {
"name" : "name",
"direct" : true
}, {
"name" : "name",
"direct" : true
} ],
"flags" : [ "NONE", "NONE" ],
"name" : "name"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
slurmdbd configuration
[v0.0.44_openapi_slurmdbd_config_resp](https://slurm.schedmd.com/rest_api.html)
#### default
slurmdbd configuration
[v0.0.44_openapi_slurmdbd_config_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/diag/
```
Get slurmdb diagnostics ( slurmdbV0044GetDiag )
### Return type
[v0.0.44_openapi_slurmdbd_stats_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ],
"statistics" : {
"time_start" : 0,
"RPCs" : [ {
"rpc" : "rpc",
"count" : 7,
"time" : {
"average" : 1,
"total" : 4
}
}, {
"rpc" : "rpc",
"count" : 7,
"time" : {
"average" : 1,
"total" : 4
}
} ],
"rollups" : {
"daily" : {
"duration" : {
"last" : 3,
"max" : 2,
"time" : 4
},
"count" : 7,
"last_run" : 9
},
"monthly" : {
"duration" : {
"last" : 1,
"max" : 1,
"time" : 6
},
"count" : 7,
"last_run" : 1
},
"hourly" : {
"duration" : {
"last" : 5,
"max" : 5,
"time" : 2
},
"count" : 6,
"last_run" : 1
}
},
"users" : [ {
"count" : 5,
"time" : {
"average" : 1,
"total" : 4
},
"user" : "user"
}, {
"count" : 5,
"time" : {
"average" : 1,
"total" : 4
},
"user" : "user"
} ]
}
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
Dictionary of statistics
[v0.0.44_openapi_slurmdbd_stats_resp](https://slurm.schedmd.com/rest_api.html)
#### default
Dictionary of statistics
[v0.0.44_openapi_slurmdbd_stats_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/instance/
```
Get instance info ( slurmdbV0044GetInstance )
### Query parameters
cluster (optional)
Query Parameter — CSV clusters list default: null
extra (optional)
Query Parameter — CSV extra list default: null
format (optional)
Query Parameter — Ignored; process JSON manually to control output format default: null
instance_id (optional)
Query Parameter — CSV instance_id list default: null
instance_type (optional)
Query Parameter — CSV instance_type list default: null
node_list (optional)
Query Parameter — Ranged node string default: null
time_end (optional)
Query Parameter — Time end (UNIX timestamp) default: null
time_start (optional)
Query Parameter — Time start (UNIX timestamp) default: null
### Return type
[v0.0.44_openapi_instances_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"instances" : [ {
"cluster" : "cluster",
"instance_id" : "instance_id",
"extra" : "extra",
"node_name" : "node_name",
"time" : {
"time_start" : 1,
"time_end" : 1
},
"instance_type" : "instance_type"
}, {
"cluster" : "cluster",
"instance_id" : "instance_id",
"extra" : "extra",
"node_name" : "node_name",
"time" : {
"time_start" : 1,
"time_end" : 1
},
"instance_type" : "instance_type"
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
List of instances
[v0.0.44_openapi_instances_resp](https://slurm.schedmd.com/rest_api.html)
#### default
List of instances
[v0.0.44_openapi_instances_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/instances/
```
Get instance list ( slurmdbV0044GetInstances )
### Query parameters
cluster (optional)
Query Parameter — CSV clusters list default: null
extra (optional)
Query Parameter — CSV extra list default: null
format (optional)
Query Parameter — Ignored; process JSON manually to control output format default: null
instance_id (optional)
Query Parameter — CSV instance_id list default: null
instance_type (optional)
Query Parameter — CSV instance_type list default: null
node_list (optional)
Query Parameter — Ranged node string default: null
time_end (optional)
Query Parameter — Time end (UNIX timestamp) default: null
time_start (optional)
Query Parameter — Time start (UNIX timestamp) default: null
### Return type
[v0.0.44_openapi_instances_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"instances" : [ {
"cluster" : "cluster",
"instance_id" : "instance_id",
"extra" : "extra",
"node_name" : "node_name",
"time" : {
"time_start" : 1,
"time_end" : 1
},
"instance_type" : "instance_type"
}, {
"cluster" : "cluster",
"instance_id" : "instance_id",
"extra" : "extra",
"node_name" : "node_name",
"time" : {
"time_start" : 1,
"time_end" : 1
},
"instance_type" : "instance_type"
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
List of instances
[v0.0.44_openapi_instances_resp](https://slurm.schedmd.com/rest_api.html)
#### default
List of instances
[v0.0.44_openapi_instances_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/job/{job_id}
```
Get job info ( slurmdbV0044GetJob )
This endpoint may return multiple job entries since job_id is not a unique key - only the tuple (cluster, job_id, start_time) is unique. If the requested job_id is a component of a heterogeneous job all components are returned.
### Path parameters
job_id (required)
Path Parameter — Job ID default: null
### Return type
[v0.0.44_openapi_slurmdbd_jobs_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"jobs" : [ {
"container" : "container",
"cluster" : "cluster",
"stdin_expanded" : "stdin_expanded",
"stdin" : "stdin",
"stdout" : "stdout",
"stderr_expanded" : "stderr_expanded",
"flags" : [ "NONE", "NONE" ],
"used_gres" : "used_gres",
"association" : {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
},
"allocation_nodes" : 0,
"working_directory" : "working_directory",
"qosreq" : "qosreq",
"constraints" : "constraints",
"required" : {
"memory_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"CPUs" : 9,
"memory_per_cpu" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"stdout_expanded" : "stdout_expanded",
"hold" : true,
"restart_cnt" : 6,
"partition" : "partition",
"segment_size" : 9,
"qos" : "qos",
"array" : {
"task" : "task",
"job_id" : 6,
"task_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"limits" : {
"max" : {
"running" : {
"tasks" : 1
}
}
}
},
"het" : {
"job_id" : 5,
"job_offset" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"submit_line" : "submit_line",
"extra" : "extra",
"reservation" : {
"requested" : "requested",
"name" : "name",
"id" : 8
},
"block" : "block",
"tres" : {
"requested" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"allocated" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"state" : {
"reason" : "reason",
"current" : [ "PENDING", "PENDING" ]
},
"mcs" : {
"label" : "label"
},
"group" : "group",
"wckey" : {
"wckey" : "wckey",
"flags" : [ "ASSIGNED_DEFAULT", "ASSIGNED_DEFAULT" ]
},
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"stderr" : "stderr",
"steps" : [ {
"nodes" : {
"count" : 6,
"range" : "range",
"list" : [ "list", "list" ]
},
"task" : {
"distribution" : "distribution"
},
"exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"kill_request_user" : "kill_request_user",
"CPU" : {
"governor" : "governor",
"requested_frequency" : {
"min" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"max" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"pid" : "pid",
"step" : {
"stdin_expanded" : "stdin_expanded",
"stdin" : "stdin",
"stdout" : "stdout",
"stderr_expanded" : "stderr_expanded",
"name" : "name",
"id" : "id",
"stderr" : "stderr",
"stdout_expanded" : "stdout_expanded"
},
"tres" : {
"consumed" : {
"average" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"min" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"max" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"requested" : {
"average" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"min" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"max" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"allocated" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"time" : {
"elapsed" : 6,
"total" : {
"seconds" : 2,
"microseconds" : 6
},
"system" : {
"seconds" : 6,
"microseconds" : 1
},
"start" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"limit" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"end" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user" : {
"seconds" : 6,
"microseconds" : 5
},
"suspended" : 3
},
"state" : [ "PENDING", "PENDING" ],
"tasks" : {
"count" : 3
},
"statistics" : {
"CPU" : {
"actual_frequency" : 3
},
"energy" : {
"consumed" : {
"number" : 2,
"set" : true,
"infinite" : true
}
}
}
}, {
"nodes" : {
"count" : 6,
"range" : "range",
"list" : [ "list", "list" ]
},
"task" : {
"distribution" : "distribution"
},
"exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"kill_request_user" : "kill_request_user",
"CPU" : {
"governor" : "governor",
"requested_frequency" : {
"min" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"max" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"pid" : "pid",
"step" : {
"stdin_expanded" : "stdin_expanded",
"stdin" : "stdin",
"stdout" : "stdout",
"stderr_expanded" : "stderr_expanded",
"name" : "name",
"id" : "id",
"stderr" : "stderr",
"stdout_expanded" : "stdout_expanded"
},
"tres" : {
"consumed" : {
"average" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"min" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"max" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"requested" : {
"average" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"min" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"max" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"allocated" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"time" : {
"elapsed" : 6,
"total" : {
"seconds" : 2,
"microseconds" : 6
},
"system" : {
"seconds" : 6,
"microseconds" : 1
},
"start" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"limit" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"end" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user" : {
"seconds" : 6,
"microseconds" : 5
},
"suspended" : 3
},
"state" : [ "PENDING", "PENDING" ],
"tasks" : {
"count" : 3
},
"statistics" : {
"CPU" : {
"actual_frequency" : 3
},
"energy" : {
"consumed" : {
"number" : 2,
"set" : true,
"infinite" : true
}
}
}
} ],
"script" : "script",
"failed_node" : "failed_node",
"derived_exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"licenses" : "licenses",
"nodes" : "nodes",
"job_id" : 9,
"exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"name" : "name",
"kill_request_user" : "kill_request_user",
"comment" : {
"administrator" : "administrator",
"system" : "system",
"job" : "job"
},
"time" : {
"elapsed" : 7,
"total" : {
"seconds" : 6,
"microseconds" : 7
},
"system" : {
"seconds" : 1,
"microseconds" : 1
},
"eligible" : 9,
"start" : 4,
"limit" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"end" : 3,
"submission" : 7,
"planned" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user" : {
"seconds" : 1,
"microseconds" : 4
},
"suspended" : 1
},
"user" : "user",
"account" : "account"
}, {
"container" : "container",
"cluster" : "cluster",
"stdin_expanded" : "stdin_expanded",
"stdin" : "stdin",
"stdout" : "stdout",
"stderr_expanded" : "stderr_expanded",
"flags" : [ "NONE", "NONE" ],
"used_gres" : "used_gres",
"association" : {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
},
"allocation_nodes" : 0,
"working_directory" : "working_directory",
"qosreq" : "qosreq",
"constraints" : "constraints",
"required" : {
"memory_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"CPUs" : 9,
"memory_per_cpu" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"stdout_expanded" : "stdout_expanded",
"hold" : true,
"restart_cnt" : 6,
"partition" : "partition",
"segment_size" : 9,
"qos" : "qos",
"array" : {
"task" : "task",
"job_id" : 6,
"task_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"limits" : {
"max" : {
"running" : {
"tasks" : 1
}
}
}
},
"het" : {
"job_id" : 5,
"job_offset" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"submit_line" : "submit_line",
"extra" : "extra",
"reservation" : {
"requested" : "requested",
"name" : "name",
"id" : 8
},
"block" : "block",
"tres" : {
"requested" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"allocated" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"state" : {
"reason" : "reason",
"current" : [ "PENDING", "PENDING" ]
},
"mcs" : {
"label" : "label"
},
"group" : "group",
"wckey" : {
"wckey" : "wckey",
"flags" : [ "ASSIGNED_DEFAULT", "ASSIGNED_DEFAULT" ]
},
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"stderr" : "stderr",
"steps" : [ {
"nodes" : {
"count" : 6,
"range" : "range",
"list" : [ "list", "list" ]
},
"task" : {
"distribution" : "distribution"
},
"exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"kill_request_user" : "kill_request_user",
"CPU" : {
"governor" : "governor",
"requested_frequency" : {
"min" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"max" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"pid" : "pid",
"step" : {
"stdin_expanded" : "stdin_expanded",
"stdin" : "stdin",
"stdout" : "stdout",
"stderr_expanded" : "stderr_expanded",
"name" : "name",
"id" : "id",
"stderr" : "stderr",
"stdout_expanded" : "stdout_expanded"
},
"tres" : {
"consumed" : {
"average" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"min" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"max" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"requested" : {
"average" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"min" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"max" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"allocated" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"time" : {
"elapsed" : 6,
"total" : {
"seconds" : 2,
"microseconds" : 6
},
"system" : {
"seconds" : 6,
"microseconds" : 1
},
"start" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"limit" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"end" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user" : {
"seconds" : 6,
"microseconds" : 5
},
"suspended" : 3
},
"state" : [ "PENDING", "PENDING" ],
"tasks" : {
"count" : 3
},
"statistics" : {
"CPU" : {
"actual_frequency" : 3
},
"energy" : {
"consumed" : {
"number" : 2,
"set" : true,
"infinite" : true
}
}
}
}, {
"nodes" : {
"count" : 6,
"range" : "range",
"list" : [ "list", "list" ]
},
"task" : {
"distribution" : "distribution"
},
"exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"kill_request_user" : "kill_request_user",
"CPU" : {
"governor" : "governor",
"requested_frequency" : {
"min" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"max" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"pid" : "pid",
"step" : {
"stdin_expanded" : "stdin_expanded",
"stdin" : "stdin",
"stdout" : "stdout",
"stderr_expanded" : "stderr_expanded",
"name" : "name",
"id" : "id",
"stderr" : "stderr",
"stdout_expanded" : "stdout_expanded"
},
"tres" : {
"consumed" : {
"average" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"min" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"max" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"requested" : {
"average" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"min" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"max" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"allocated" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"time" : {
"elapsed" : 6,
"total" : {
"seconds" : 2,
"microseconds" : 6
},
"system" : {
"seconds" : 6,
"microseconds" : 1
},
"start" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"limit" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"end" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user" : {
"seconds" : 6,
"microseconds" : 5
},
"suspended" : 3
},
"state" : [ "PENDING", "PENDING" ],
"tasks" : {
"count" : 3
},
"statistics" : {
"CPU" : {
"actual_frequency" : 3
},
"energy" : {
"consumed" : {
"number" : 2,
"set" : true,
"infinite" : true
}
}
}
} ],
"script" : "script",
"failed_node" : "failed_node",
"derived_exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"licenses" : "licenses",
"nodes" : "nodes",
"job_id" : 9,
"exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"name" : "name",
"kill_request_user" : "kill_request_user",
"comment" : {
"administrator" : "administrator",
"system" : "system",
"job" : "job"
},
"time" : {
"elapsed" : 7,
"total" : {
"seconds" : 6,
"microseconds" : 7
},
"system" : {
"seconds" : 1,
"microseconds" : 1
},
"eligible" : 9,
"start" : 4,
"limit" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"end" : 3,
"submission" : 7,
"planned" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user" : {
"seconds" : 1,
"microseconds" : 4
},
"suspended" : 1
},
"user" : "user",
"account" : "account"
} ],
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
Job description
[v0.0.44_openapi_slurmdbd_jobs_resp](https://slurm.schedmd.com/rest_api.html)
#### default
Job description
[v0.0.44_openapi_slurmdbd_jobs_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/jobs/
```
Get job list ( slurmdbV0044GetJobs )
### Query parameters
account (optional)
Query Parameter — CSV account list default: null
association (optional)
Query Parameter — CSV association list default: null
cluster (optional)
Query Parameter — CSV cluster list default: null
constraints (optional)
Query Parameter — CSV constraint list default: null
scheduler_unset (optional)
Query Parameter — Schedule bits not set default: null
scheduled_on_submit (optional)
Query Parameter — Job was started on submit default: null
scheduled_by_main (optional)
Query Parameter — Job was started from main scheduler default: null
scheduled_by_backfill (optional)
Query Parameter — Job was started from backfill default: null
job_started (optional)
Query Parameter — Job start RPC was received default: null
job_altered (optional)
Query Parameter — Job record has been altered default: null
exit_code (optional)
Query Parameter — Job exit code (numeric) default: null
show_duplicates (optional)
Query Parameter — Include duplicate job entries default: null
skip_steps (optional)
Query Parameter — Exclude job step details default: null
disable_truncate_usage_time (optional)
Query Parameter — Do not truncate the time to usage_start and usage_end default: null
whole_hetjob (optional)
Query Parameter — Include details on all hetjob components default: null
disable_whole_hetjob (optional)
Query Parameter — Only show details on specified hetjob components default: null
disable_wait_for_result (optional)
Query Parameter — Tell dbd not to wait for the result default: null
usage_time_as_submit_time (optional)
Query Parameter — Use usage_time as the submit_time of the job default: null
show_batch_script (optional)
Query Parameter — Include job script default: null
show_job_environment (optional)
Query Parameter — Include job environment default: null
format (optional)
Query Parameter — Ignored; process JSON manually to control output format default: null
groups (optional)
Query Parameter — CSV group list default: null
job_name (optional)
Query Parameter — CSV job name list default: null
partition (optional)
Query Parameter — CSV partition name list default: null
qos (optional)
Query Parameter — CSV QOS name list default: null
reason (optional)
Query Parameter — CSV reason list default: null
reservation (optional)
Query Parameter — CSV reservation name list default: null
reservation_id (optional)
Query Parameter — CSV reservation ID list default: null
state (optional)
Query Parameter — CSV state list default: null
step (optional)
Query Parameter — CSV step id list default: null
end_time (optional)
Query Parameter — Usage end (UNIX timestamp) default: null
start_time (optional)
Query Parameter — Usage start (UNIX timestamp) default: null
node (optional)
Query Parameter — Ranged node string where jobs ran default: null
users (optional)
Query Parameter — CSV user name list default: null
wckey (optional)
Query Parameter — CSV WCKey list default: null
### Return type
[v0.0.44_openapi_slurmdbd_jobs_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"jobs" : [ {
"container" : "container",
"cluster" : "cluster",
"stdin_expanded" : "stdin_expanded",
"stdin" : "stdin",
"stdout" : "stdout",
"stderr_expanded" : "stderr_expanded",
"flags" : [ "NONE", "NONE" ],
"used_gres" : "used_gres",
"association" : {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
},
"allocation_nodes" : 0,
"working_directory" : "working_directory",
"qosreq" : "qosreq",
"constraints" : "constraints",
"required" : {
"memory_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"CPUs" : 9,
"memory_per_cpu" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"stdout_expanded" : "stdout_expanded",
"hold" : true,
"restart_cnt" : 6,
"partition" : "partition",
"segment_size" : 9,
"qos" : "qos",
"array" : {
"task" : "task",
"job_id" : 6,
"task_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"limits" : {
"max" : {
"running" : {
"tasks" : 1
}
}
}
},
"het" : {
"job_id" : 5,
"job_offset" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"submit_line" : "submit_line",
"extra" : "extra",
"reservation" : {
"requested" : "requested",
"name" : "name",
"id" : 8
},
"block" : "block",
"tres" : {
"requested" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"allocated" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"state" : {
"reason" : "reason",
"current" : [ "PENDING", "PENDING" ]
},
"mcs" : {
"label" : "label"
},
"group" : "group",
"wckey" : {
"wckey" : "wckey",
"flags" : [ "ASSIGNED_DEFAULT", "ASSIGNED_DEFAULT" ]
},
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"stderr" : "stderr",
"steps" : [ {
"nodes" : {
"count" : 6,
"range" : "range",
"list" : [ "list", "list" ]
},
"task" : {
"distribution" : "distribution"
},
"exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"kill_request_user" : "kill_request_user",
"CPU" : {
"governor" : "governor",
"requested_frequency" : {
"min" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"max" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"pid" : "pid",
"step" : {
"stdin_expanded" : "stdin_expanded",
"stdin" : "stdin",
"stdout" : "stdout",
"stderr_expanded" : "stderr_expanded",
"name" : "name",
"id" : "id",
"stderr" : "stderr",
"stdout_expanded" : "stdout_expanded"
},
"tres" : {
"consumed" : {
"average" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"min" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"max" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"requested" : {
"average" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"min" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"max" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"allocated" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"time" : {
"elapsed" : 6,
"total" : {
"seconds" : 2,
"microseconds" : 6
},
"system" : {
"seconds" : 6,
"microseconds" : 1
},
"start" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"limit" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"end" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user" : {
"seconds" : 6,
"microseconds" : 5
},
"suspended" : 3
},
"state" : [ "PENDING", "PENDING" ],
"tasks" : {
"count" : 3
},
"statistics" : {
"CPU" : {
"actual_frequency" : 3
},
"energy" : {
"consumed" : {
"number" : 2,
"set" : true,
"infinite" : true
}
}
}
}, {
"nodes" : {
"count" : 6,
"range" : "range",
"list" : [ "list", "list" ]
},
"task" : {
"distribution" : "distribution"
},
"exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"kill_request_user" : "kill_request_user",
"CPU" : {
"governor" : "governor",
"requested_frequency" : {
"min" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"max" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"pid" : "pid",
"step" : {
"stdin_expanded" : "stdin_expanded",
"stdin" : "stdin",
"stdout" : "stdout",
"stderr_expanded" : "stderr_expanded",
"name" : "name",
"id" : "id",
"stderr" : "stderr",
"stdout_expanded" : "stdout_expanded"
},
"tres" : {
"consumed" : {
"average" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"min" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"max" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"requested" : {
"average" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"min" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"max" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"allocated" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"time" : {
"elapsed" : 6,
"total" : {
"seconds" : 2,
"microseconds" : 6
},
"system" : {
"seconds" : 6,
"microseconds" : 1
},
"start" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"limit" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"end" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user" : {
"seconds" : 6,
"microseconds" : 5
},
"suspended" : 3
},
"state" : [ "PENDING", "PENDING" ],
"tasks" : {
"count" : 3
},
"statistics" : {
"CPU" : {
"actual_frequency" : 3
},
"energy" : {
"consumed" : {
"number" : 2,
"set" : true,
"infinite" : true
}
}
}
} ],
"script" : "script",
"failed_node" : "failed_node",
"derived_exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"licenses" : "licenses",
"nodes" : "nodes",
"job_id" : 9,
"exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"name" : "name",
"kill_request_user" : "kill_request_user",
"comment" : {
"administrator" : "administrator",
"system" : "system",
"job" : "job"
},
"time" : {
"elapsed" : 7,
"total" : {
"seconds" : 6,
"microseconds" : 7
},
"system" : {
"seconds" : 1,
"microseconds" : 1
},
"eligible" : 9,
"start" : 4,
"limit" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"end" : 3,
"submission" : 7,
"planned" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user" : {
"seconds" : 1,
"microseconds" : 4
},
"suspended" : 1
},
"user" : "user",
"account" : "account"
}, {
"container" : "container",
"cluster" : "cluster",
"stdin_expanded" : "stdin_expanded",
"stdin" : "stdin",
"stdout" : "stdout",
"stderr_expanded" : "stderr_expanded",
"flags" : [ "NONE", "NONE" ],
"used_gres" : "used_gres",
"association" : {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
},
"allocation_nodes" : 0,
"working_directory" : "working_directory",
"qosreq" : "qosreq",
"constraints" : "constraints",
"required" : {
"memory_per_node" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"CPUs" : 9,
"memory_per_cpu" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"stdout_expanded" : "stdout_expanded",
"hold" : true,
"restart_cnt" : 6,
"partition" : "partition",
"segment_size" : 9,
"qos" : "qos",
"array" : {
"task" : "task",
"job_id" : 6,
"task_id" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"limits" : {
"max" : {
"running" : {
"tasks" : 1
}
}
}
},
"het" : {
"job_id" : 5,
"job_offset" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"submit_line" : "submit_line",
"extra" : "extra",
"reservation" : {
"requested" : "requested",
"name" : "name",
"id" : 8
},
"block" : "block",
"tres" : {
"requested" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"allocated" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"state" : {
"reason" : "reason",
"current" : [ "PENDING", "PENDING" ]
},
"mcs" : {
"label" : "label"
},
"group" : "group",
"wckey" : {
"wckey" : "wckey",
"flags" : [ "ASSIGNED_DEFAULT", "ASSIGNED_DEFAULT" ]
},
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"stderr" : "stderr",
"steps" : [ {
"nodes" : {
"count" : 6,
"range" : "range",
"list" : [ "list", "list" ]
},
"task" : {
"distribution" : "distribution"
},
"exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"kill_request_user" : "kill_request_user",
"CPU" : {
"governor" : "governor",
"requested_frequency" : {
"min" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"max" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"pid" : "pid",
"step" : {
"stdin_expanded" : "stdin_expanded",
"stdin" : "stdin",
"stdout" : "stdout",
"stderr_expanded" : "stderr_expanded",
"name" : "name",
"id" : "id",
"stderr" : "stderr",
"stdout_expanded" : "stdout_expanded"
},
"tres" : {
"consumed" : {
"average" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"min" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"max" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"requested" : {
"average" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"min" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"max" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"allocated" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"time" : {
"elapsed" : 6,
"total" : {
"seconds" : 2,
"microseconds" : 6
},
"system" : {
"seconds" : 6,
"microseconds" : 1
},
"start" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"limit" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"end" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user" : {
"seconds" : 6,
"microseconds" : 5
},
"suspended" : 3
},
"state" : [ "PENDING", "PENDING" ],
"tasks" : {
"count" : 3
},
"statistics" : {
"CPU" : {
"actual_frequency" : 3
},
"energy" : {
"consumed" : {
"number" : 2,
"set" : true,
"infinite" : true
}
}
}
}, {
"nodes" : {
"count" : 6,
"range" : "range",
"list" : [ "list", "list" ]
},
"task" : {
"distribution" : "distribution"
},
"exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"kill_request_user" : "kill_request_user",
"CPU" : {
"governor" : "governor",
"requested_frequency" : {
"min" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"max" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"pid" : "pid",
"step" : {
"stdin_expanded" : "stdin_expanded",
"stdin" : "stdin",
"stdout" : "stdout",
"stderr_expanded" : "stderr_expanded",
"name" : "name",
"id" : "id",
"stderr" : "stderr",
"stdout_expanded" : "stdout_expanded"
},
"tres" : {
"consumed" : {
"average" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"min" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"max" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"requested" : {
"average" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"min" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"max" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"allocated" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
},
"time" : {
"elapsed" : 6,
"total" : {
"seconds" : 2,
"microseconds" : 6
},
"system" : {
"seconds" : 6,
"microseconds" : 1
},
"start" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"limit" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"end" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user" : {
"seconds" : 6,
"microseconds" : 5
},
"suspended" : 3
},
"state" : [ "PENDING", "PENDING" ],
"tasks" : {
"count" : 3
},
"statistics" : {
"CPU" : {
"actual_frequency" : 3
},
"energy" : {
"consumed" : {
"number" : 2,
"set" : true,
"infinite" : true
}
}
}
} ],
"script" : "script",
"failed_node" : "failed_node",
"derived_exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"licenses" : "licenses",
"nodes" : "nodes",
"job_id" : 9,
"exit_code" : {
"return_code" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"signal" : {
"name" : "name",
"id" : {
"number" : 2,
"set" : true,
"infinite" : true
}
},
"status" : [ "INVALID", "INVALID" ]
},
"name" : "name",
"kill_request_user" : "kill_request_user",
"comment" : {
"administrator" : "administrator",
"system" : "system",
"job" : "job"
},
"time" : {
"elapsed" : 7,
"total" : {
"seconds" : 6,
"microseconds" : 7
},
"system" : {
"seconds" : 1,
"microseconds" : 1
},
"eligible" : 9,
"start" : 4,
"limit" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"end" : 3,
"submission" : 7,
"planned" : {
"number" : 2,
"set" : true,
"infinite" : true
},
"user" : {
"seconds" : 1,
"microseconds" : 4
},
"suspended" : 1
},
"user" : "user",
"account" : "account"
} ],
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
List of jobs
[v0.0.44_openapi_slurmdbd_jobs_resp](https://slurm.schedmd.com/rest_api.html)
#### default
List of jobs
[v0.0.44_openapi_slurmdbd_jobs_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/ping/
```
ping test ( slurmdbV0044GetPing )
### Return type
[v0.0.44_openapi_slurmdbd_ping_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"pings" : [ {
"responding" : true,
"hostname" : "hostname",
"latency" : 0,
"primary" : true
}, {
"responding" : true,
"hostname" : "hostname",
"latency" : 0,
"primary" : true
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
results of ping test
[v0.0.44_openapi_slurmdbd_ping_resp](https://slurm.schedmd.com/rest_api.html)
#### default
results of ping test
[v0.0.44_openapi_slurmdbd_ping_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/qos/
```
Get QOS list ( slurmdbV0044GetQos )
### Query parameters
description (optional)
Query Parameter — CSV description list default: null
Include deleted QOS (optional)
Query Parameter — default: null
id (optional)
Query Parameter — CSV QOS id list default: null
format (optional)
Query Parameter — Ignored; process JSON manually to control output format default: null
name (optional)
Query Parameter — CSV QOS name list default: null
preempt_mode (optional)
Query Parameter — PreemptMode used when jobs in this QOS are preempted default: null
### Return type
[v0.0.44_openapi_slurmdbd_qos_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"qos" : [ {
"flags" : [ "NOT_SET", "NOT_SET" ],
"name" : "name",
"usage_threshold" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"description" : "description",
"usage_factor" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"id" : 3,
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"limits" : {
"min" : {
"priority_threshold" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"tres" : {
"per" : {
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
}
},
"max" : {
"jobs" : {
"count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"per" : {
"user" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"account" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"active_jobs" : {
"per" : {
"user" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"account" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
}
},
"accruing" : {
"per" : {
"user" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"account" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"tres" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"minutes" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"per" : {
"qos" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"user" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"account" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"per" : {
"node" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"user" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"account" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"wall_clock" : {
"per" : {
"qos" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"job" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"active_jobs" : {
"count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"accruing" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"factor" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"grace_time" : 2
},
"preempt" : {
"mode" : [ "DISABLED", "DISABLED" ],
"exempt_time" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"list" : [ "list", "list" ]
}
}, {
"flags" : [ "NOT_SET", "NOT_SET" ],
"name" : "name",
"usage_threshold" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"description" : "description",
"usage_factor" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"id" : 3,
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"limits" : {
"min" : {
"priority_threshold" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"tres" : {
"per" : {
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
}
},
"max" : {
"jobs" : {
"count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"per" : {
"user" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"account" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"active_jobs" : {
"per" : {
"user" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"account" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
}
},
"accruing" : {
"per" : {
"user" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"account" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"tres" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"minutes" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"per" : {
"qos" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"user" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"account" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"per" : {
"node" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"user" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"account" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"wall_clock" : {
"per" : {
"qos" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"job" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"active_jobs" : {
"count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"accruing" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"factor" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"grace_time" : 2
},
"preempt" : {
"mode" : [ "DISABLED", "DISABLED" ],
"exempt_time" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"list" : [ "list", "list" ]
}
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
List of QOS
[v0.0.44_openapi_slurmdbd_qos_resp](https://slurm.schedmd.com/rest_api.html)
#### default
List of QOS
[v0.0.44_openapi_slurmdbd_qos_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/qos/{qos}
```
Get QOS info ( slurmdbV0044GetSingleQos )
### Path parameters
qos (required)
Path Parameter — QOS name default: null
### Query parameters
with_deleted (optional)
Query Parameter — Query includes deleted QOS default: null
### Return type
[v0.0.44_openapi_slurmdbd_qos_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"qos" : [ {
"flags" : [ "NOT_SET", "NOT_SET" ],
"name" : "name",
"usage_threshold" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"description" : "description",
"usage_factor" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"id" : 3,
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"limits" : {
"min" : {
"priority_threshold" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"tres" : {
"per" : {
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
}
},
"max" : {
"jobs" : {
"count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"per" : {
"user" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"account" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"active_jobs" : {
"per" : {
"user" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"account" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
}
},
"accruing" : {
"per" : {
"user" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"account" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"tres" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"minutes" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"per" : {
"qos" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"user" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"account" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"per" : {
"node" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"user" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"account" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"wall_clock" : {
"per" : {
"qos" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"job" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"active_jobs" : {
"count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"accruing" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"factor" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"grace_time" : 2
},
"preempt" : {
"mode" : [ "DISABLED", "DISABLED" ],
"exempt_time" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"list" : [ "list", "list" ]
}
}, {
"flags" : [ "NOT_SET", "NOT_SET" ],
"name" : "name",
"usage_threshold" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"description" : "description",
"usage_factor" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"id" : 3,
"priority" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"limits" : {
"min" : {
"priority_threshold" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"tres" : {
"per" : {
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
}
},
"max" : {
"jobs" : {
"count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"per" : {
"user" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"account" : {
"number" : 5,
"set" : true,
"infinite" : true
}
},
"active_jobs" : {
"per" : {
"user" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"account" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
}
},
"accruing" : {
"per" : {
"user" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"account" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"tres" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"minutes" : {
"total" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"per" : {
"qos" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"user" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"account" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"per" : {
"node" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"job" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"user" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"account" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ]
}
},
"wall_clock" : {
"per" : {
"qos" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"job" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"active_jobs" : {
"count" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"accruing" : {
"number" : 5,
"set" : true,
"infinite" : true
}
}
},
"factor" : {
"number" : 4.145608029883936,
"set" : true,
"infinite" : true
},
"grace_time" : 2
},
"preempt" : {
"mode" : [ "DISABLED", "DISABLED" ],
"exempt_time" : {
"number" : 5,
"set" : true,
"infinite" : true
},
"list" : [ "list", "list" ]
}
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
QOS information
[v0.0.44_openapi_slurmdbd_qos_resp](https://slurm.schedmd.com/rest_api.html)
#### default
QOS information
[v0.0.44_openapi_slurmdbd_qos_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/tres/
```
Get TRES info ( slurmdbV0044GetTres )
### Return type
[v0.0.44_openapi_tres_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"TRES" : [ {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
}, {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
List of TRES
[v0.0.44_openapi_tres_resp](https://slurm.schedmd.com/rest_api.html)
#### default
List of TRES
[v0.0.44_openapi_tres_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/user/{name}
```
Get user info ( slurmdbV0044GetUser )
### Path parameters
name (required)
Path Parameter — User name default: null
### Query parameters
with_deleted (optional)
Query Parameter — Include deleted users default: null
with_assocs (optional)
Query Parameter — Include associations default: null
with_coords (optional)
Query Parameter — Include coordinators default: null
with_wckeys (optional)
Query Parameter — Include WCKeys default: null
### Return type
[v0.0.44_openapi_users_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"users" : [ {
"associations" : [ {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
}, {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
} ],
"default" : {
"qos" : 1,
"wckey" : "wckey",
"account" : "account"
},
"administrator_level" : [ "Not Set", "Not Set" ],
"old_name" : "old_name",
"wckeys" : [ {
"cluster" : "cluster",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"id" : 9,
"user" : "user"
}, {
"cluster" : "cluster",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"id" : 9,
"user" : "user"
} ],
"coordinators" : [ {
"name" : "name",
"direct" : true
}, {
"name" : "name",
"direct" : true
} ],
"flags" : [ "NONE", "NONE" ],
"name" : "name"
}, {
"associations" : [ {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
}, {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
} ],
"default" : {
"qos" : 1,
"wckey" : "wckey",
"account" : "account"
},
"administrator_level" : [ "Not Set", "Not Set" ],
"old_name" : "old_name",
"wckeys" : [ {
"cluster" : "cluster",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"id" : 9,
"user" : "user"
}, {
"cluster" : "cluster",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"id" : 9,
"user" : "user"
} ],
"coordinators" : [ {
"name" : "name",
"direct" : true
}, {
"name" : "name",
"direct" : true
} ],
"flags" : [ "NONE", "NONE" ],
"name" : "name"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
List of users
[v0.0.44_openapi_users_resp](https://slurm.schedmd.com/rest_api.html)
#### default
List of users
[v0.0.44_openapi_users_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/users/
```
Get user list ( slurmdbV0044GetUsers )
### Query parameters
admin_level (optional)
Query Parameter — Administrator level default: null
default_account (optional)
Query Parameter — CSV default account list default: null
default_wckey (optional)
Query Parameter — CSV default WCKey list default: null
with_assocs (optional)
Query Parameter — With associations default: null
with_coords (optional)
Query Parameter — With coordinators default: null
with_deleted (optional)
Query Parameter — With deleted default: null
with_wckeys (optional)
Query Parameter — With WCKeys default: null
without_defaults (optional)
Query Parameter — Exclude defaults default: null
### Return type
[v0.0.44_openapi_users_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"users" : [ {
"associations" : [ {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
}, {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
} ],
"default" : {
"qos" : 1,
"wckey" : "wckey",
"account" : "account"
},
"administrator_level" : [ "Not Set", "Not Set" ],
"old_name" : "old_name",
"wckeys" : [ {
"cluster" : "cluster",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"id" : 9,
"user" : "user"
}, {
"cluster" : "cluster",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"id" : 9,
"user" : "user"
} ],
"coordinators" : [ {
"name" : "name",
"direct" : true
}, {
"name" : "name",
"direct" : true
} ],
"flags" : [ "NONE", "NONE" ],
"name" : "name"
}, {
"associations" : [ {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
}, {
"cluster" : "cluster",
"partition" : "partition",
"id" : 5,
"user" : "user",
"account" : "account"
} ],
"default" : {
"qos" : 1,
"wckey" : "wckey",
"account" : "account"
},
"administrator_level" : [ "Not Set", "Not Set" ],
"old_name" : "old_name",
"wckeys" : [ {
"cluster" : "cluster",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"id" : 9,
"user" : "user"
}, {
"cluster" : "cluster",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"id" : 9,
"user" : "user"
} ],
"coordinators" : [ {
"name" : "name",
"direct" : true
}, {
"name" : "name",
"direct" : true
} ],
"flags" : [ "NONE", "NONE" ],
"name" : "name"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
List of users
[v0.0.44_openapi_users_resp](https://slurm.schedmd.com/rest_api.html)
#### default
List of users
[v0.0.44_openapi_users_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/wckey/{id}
```
Get wckey info ( slurmdbV0044GetWckey )
### Path parameters
id (required)
Path Parameter — WCKey ID default: null
### Return type
[v0.0.44_openapi_wckey_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"wckeys" : [ {
"cluster" : "cluster",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"id" : 9,
"user" : "user"
}, {
"cluster" : "cluster",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"id" : 9,
"user" : "user"
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
Description of wckey
[v0.0.44_openapi_wckey_resp](https://slurm.schedmd.com/rest_api.html)
#### default
Description of wckey
[v0.0.44_openapi_wckey_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
get /slurmdb/v0.0.44/wckeys/
```
Get wckey list ( slurmdbV0044GetWckeys )
### Query parameters
cluster (optional)
Query Parameter — CSV cluster name list default: null
format (optional)
Query Parameter — Ignored; process JSON manually to control output format default: null
id (optional)
Query Parameter — CSV ID list default: null
name (optional)
Query Parameter — CSV name list default: null
only_defaults (optional)
Query Parameter — Only query defaults default: null
usage_end (optional)
Query Parameter — Usage end (UNIX timestamp) default: null
usage_start (optional)
Query Parameter — Usage start (UNIX timestamp) default: null
user (optional)
Query Parameter — CSV user list default: null
with_usage (optional)
Query Parameter — Include usage default: null
with_deleted (optional)
Query Parameter — Include deleted WCKeys default: null
### Return type
[v0.0.44_openapi_wckey_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"wckeys" : [ {
"cluster" : "cluster",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"id" : 9,
"user" : "user"
}, {
"cluster" : "cluster",
"name" : "name",
"flags" : [ "DELETED", "DELETED" ],
"accounting" : [ {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
}, {
"start" : 7,
"id" : 5,
"TRES" : {
"name" : "name",
"count" : 0,
"id" : 7,
"type" : "type"
},
"allocated" : {
"seconds" : 5
},
"id_alt" : 2
} ],
"id" : 9,
"user" : "user"
} ],
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
List of wckeys
[v0.0.44_openapi_wckey_resp](https://slurm.schedmd.com/rest_api.html)
#### default
List of wckeys
[v0.0.44_openapi_wckey_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurmdb/v0.0.44/accounts/
```
Add/update list of accounts ( slurmdbV0044PostAccounts )
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_openapi_accounts_resp [v0.0.44_openapi_accounts_resp](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Return type
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
Status of account update request
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
#### default
Status of account update request
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurmdb/v0.0.44/accounts_association/
```
Add accounts with conditional association ( slurmdbV0044PostAccountsAssociation )
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_openapi_accounts_add_cond_resp [v0.0.44_openapi_accounts_add_cond_resp](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Return type
[v0.0.44_openapi_accounts_add_cond_resp_str](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ],
"added_accounts" : "added_accounts"
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
Status of account addition request
[v0.0.44_openapi_accounts_add_cond_resp_str](https://slurm.schedmd.com/rest_api.html)
#### default
Status of account addition request
[v0.0.44_openapi_accounts_add_cond_resp_str](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurmdb/v0.0.44/associations/
```
Set associations info ( slurmdbV0044PostAssociations )
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_openapi_assocs_resp [v0.0.44_openapi_assocs_resp](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Return type
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
status of associations update
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
#### default
status of associations update
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurmdb/v0.0.44/clusters/
```
Get cluster list ( slurmdbV0044PostClusters )
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_openapi_clusters_resp [v0.0.44_openapi_clusters_resp](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Query parameters
update_time (optional)
Query Parameter — Query reservations updated more recently than this time (UNIX timestamp) default: null
### Return type
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
Result of modify clusters request
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
#### default
Result of modify clusters request
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurmdb/v0.0.44/config
```
Load all configuration information ( slurmdbV0044PostConfig )
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_openapi_slurmdbd_config_resp [v0.0.44_openapi_slurmdbd_config_resp](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Return type
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
slurmdbd configuration
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
#### default
slurmdbd configuration
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurmdb/v0.0.44/job/{job_id}
```
Update job ( slurmdbV0044PostJob )
### Path parameters
job_id (required)
Path Parameter — Job ID default: null
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_job_modify [v0.0.44_job_modify](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Return type
[v0.0.44_openapi_job_modify_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"results" : [ "results", "results" ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
Job update results
[v0.0.44_openapi_job_modify_resp](https://slurm.schedmd.com/rest_api.html)
#### default
Job update results
[v0.0.44_openapi_job_modify_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurmdb/v0.0.44/jobs/
```
Update jobs ( slurmdbV0044PostJobs )
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_openapi_job_modify_req [v0.0.44_openapi_job_modify_req](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Return type
[v0.0.44_openapi_job_modify_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"results" : [ "results", "results" ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
Job update results
[v0.0.44_openapi_job_modify_resp](https://slurm.schedmd.com/rest_api.html)
#### default
Job update results
[v0.0.44_openapi_job_modify_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurmdb/v0.0.44/qos/
```
Add or update QOSs ( slurmdbV0044PostQos )
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_openapi_slurmdbd_qos_resp [v0.0.44_openapi_slurmdbd_qos_resp](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Query parameters
description (optional)
Query Parameter — CSV description list default: null
Include deleted QOS (optional)
Query Parameter — default: null
id (optional)
Query Parameter — CSV QOS id list default: null
format (optional)
Query Parameter — Ignored; process JSON manually to control output format default: null
name (optional)
Query Parameter — CSV QOS name list default: null
preempt_mode (optional)
Query Parameter — PreemptMode used when jobs in this QOS are preempted default: null
### Return type
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
QOS update response
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
#### default
QOS update response
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurmdb/v0.0.44/tres/
```
Add TRES ( slurmdbV0044PostTres )
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_openapi_tres_resp [v0.0.44_openapi_tres_resp](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Return type
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
TRES update result
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
#### default
TRES update result
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurmdb/v0.0.44/users/
```
Update users ( slurmdbV0044PostUsers )
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_openapi_users_resp [v0.0.44_openapi_users_resp](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Return type
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
Status of user update request
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
#### default
Status of user update request
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurmdb/v0.0.44/users_association/
```
Add users with conditional association ( slurmdbV0044PostUsersAssociation )
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_openapi_users_add_cond_resp [v0.0.44_openapi_users_add_cond_resp](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Query parameters
update_time (optional)
Query Parameter — Query partitions updated more recently than this time (UNIX timestamp) default: null
flags (optional)
Query Parameter — Query flags default: null
### Return type
[v0.0.44_openapi_users_add_cond_resp_str](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"added_users" : "added_users",
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
Add list of users with conditional association
[v0.0.44_openapi_users_add_cond_resp_str](https://slurm.schedmd.com/rest_api.html)
#### default
Add list of users with conditional association
[v0.0.44_openapi_users_add_cond_resp_str](https://slurm.schedmd.com/rest_api.html)
[Up](https://slurm.schedmd.com/rest_api.html)
```text
post /slurmdb/v0.0.44/wckeys/
```
Add or update wckeys ( slurmdbV0044PostWckeys )
### Consumes
This API call consumes the following media types via the Content-Type request header:
- application/json
### Request body
v0.0.44_openapi_wckey_resp [v0.0.44_openapi_wckey_resp](https://slurm.schedmd.com/rest_api.html) (optional)
Body Parameter —
### Query parameters
cluster (optional)
Query Parameter — CSV cluster name list default: null
format (optional)
Query Parameter — Ignored; process JSON manually to control output format default: null
id (optional)
Query Parameter — CSV ID list default: null
name (optional)
Query Parameter — CSV name list default: null
only_defaults (optional)
Query Parameter — Only query defaults default: null
usage_end (optional)
Query Parameter — Usage end (UNIX timestamp) default: null
usage_start (optional)
Query Parameter — Usage start (UNIX timestamp) default: null
user (optional)
Query Parameter — CSV user list default: null
with_usage (optional)
Query Parameter — Include usage default: null
with_deleted (optional)
Query Parameter — Include deleted WCKeys default: null
### Return type
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
### Example data
Content-Type: application/json
```text
{
"meta" : {
"slurm" : {
"cluster" : "cluster",
"release" : "release",
"version" : {
"major" : "major",
"minor" : "minor",
"micro" : "micro"
}
},
"plugin" : {
"accounting_storage" : "accounting_storage",
"name" : "name",
"type" : "type",
"data_parser" : "data_parser"
},
"client" : {
"source" : "source",
"user" : "user",
"group" : "group"
},
"command" : [ "command", "command" ]
},
"warnings" : [ {
"description" : "description",
"source" : "source"
}, {
"description" : "description",
"source" : "source"
} ],
"errors" : [ {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
}, {
"description" : "description",
"source" : "source",
"error" : "error",
"error_number" : 7
} ]
}
```
### Produces
This API call produces the following media types according to the Accept request header;
the media type will be conveyed by the Content-Type response header.
- application/json
### Responses
#### 200
Result of wckey addition or update request
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
#### default
Result of wckey addition or update request
[v0.0.44_openapi_resp](https://slurm.schedmd.com/rest_api.html)
## Models
[ Jump to [Methods](https://slurm.schedmd.com/rest_api.html) ]
### Table of Contents
- [v0.0.44_account -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_account_short -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_accounting -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_accounts_add_cond -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_acct_gather_energy -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_assoc -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_assoc_rec_set -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_assoc_shares_obj_wrap -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_assoc_short -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_bf_exit_fields -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_cluster_rec -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_controller_ping -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_coord -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_cron_entry -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_float64_no_val_struct -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_instance -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_job -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_job_alloc_req -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_job_array_response_msg_entry -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_job_desc_msg -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_job_info -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_job_modify -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_job_res -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_job_res_core -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_job_res_node -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_job_res_socket -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_job_submit_req -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_kill_jobs_msg -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_kill_jobs_resp_job -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_license -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_node -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_node_gres_layout -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_node_resource_layout -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_accounts_add_cond_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_accounts_add_cond_resp_str -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_accounts_removed_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_accounts_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_assocs_removed_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_assocs_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_clusters_removed_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_clusters_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_create_node_req -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_diag_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_error -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_instances_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_job_alloc_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_job_info_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_job_modify_req -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_job_modify_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_job_post_response -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_job_submit_response -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_kill_job_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_kill_jobs_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_licenses_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_meta -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_nodes_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_partition_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_ping_array_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_reservation_mod_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_reservation_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_resource_layout_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_shares_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_slurmdbd_config_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_slurmdbd_jobs_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_slurmdbd_ping_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_slurmdbd_qos_removed_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_slurmdbd_qos_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_slurmdbd_stats_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_tres_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_users_add_cond_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_users_add_cond_resp_str -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_users_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_warning -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_wckey_removed_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_openapi_wckey_resp -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_part_prio -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_partition_info -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_process_exit_code_verbose -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_qos -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_reservation_core_spec -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_reservation_desc_msg -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_reservation_info -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_reservation_mod_req -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_rollup_stats -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_schedule_exit_fields -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_shares_float128_tres -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_shares_resp_msg -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_shares_uint64_tres -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_slurm_step_id -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_slurmdbd_ping -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_stats_msg -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_stats_msg_rpc_dump -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_stats_msg_rpc_queue -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_stats_msg_rpc_type -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_stats_msg_rpc_user -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_stats_rec -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_stats_rpc -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_stats_user -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_step -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_tres -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_uint16_no_val_struct -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_uint32_no_val_struct -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_uint64_no_val_struct -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_update_node_msg -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_user -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_user_short -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_users_add_cond -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_wckey -](https://slurm.schedmd.com/rest_api.html)
- [v0.0.44_wckey_tag_struct -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_accounting_allocated -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_assoc_default -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_assoc_max -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_assoc_max_jobs -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_assoc_max_jobs_per -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_assoc_max_per -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_assoc_max_per_account -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_assoc_max_tres -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_assoc_max_tres_group -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_assoc_max_tres_minutes -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_assoc_max_tres_per -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_assoc_min -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_assoc_shares_obj_wrap_fairshare -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_assoc_shares_obj_wrap_tres -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_cluster_rec_associations -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_cluster_rec_controller -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_cron_entry_line -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_instance_time -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_array -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_array_limits -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_array_limits_max -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_array_limits_max_running -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_comment -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_desc_msg_rlimits -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_het -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_info_power -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_mcs -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_modify_tres -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_required -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_res_node_cpus -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_res_node_memory -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_res_nodes -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_reservation -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_state -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_time -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_time_system -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_time_total -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_time_user -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_job_tres -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_kill_jobs_resp_job_error -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_kill_jobs_resp_job_federation -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_openapi_meta_client -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_openapi_meta_plugin -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_openapi_meta_slurm -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_openapi_meta_slurm_version -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_partition_info_accounts -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_partition_info_cpus -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_partition_info_defaults -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_partition_info_groups -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_partition_info_maximums -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_partition_info_maximums_oversubscribe -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_partition_info_minimums -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_partition_info_nodes -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_partition_info_partition -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_partition_info_priority -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_partition_info_qos -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_partition_info_timeouts -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_partition_info_tres -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_process_exit_code_verbose_signal -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_qos_limits -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_qos_limits_max -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_qos_limits_max_active_jobs -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_qos_limits_max_jobs -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_qos_limits_max_jobs_active_jobs -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_qos_limits_max_jobs_active_jobs_per -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_qos_limits_max_tres -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_qos_limits_max_tres_minutes -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_qos_limits_max_tres_minutes_per -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_qos_limits_max_tres_per -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_qos_limits_max_wall_clock -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_qos_limits_max_wall_clock_per -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_qos_limits_min -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_qos_limits_min_tres -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_qos_limits_min_tres_per -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_qos_preempt -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_reservation_info_purge_completed -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_rollup_stats_daily -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_rollup_stats_daily_duration -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_rollup_stats_hourly -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_rollup_stats_hourly_duration -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_rollup_stats_monthly -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_rollup_stats_monthly_duration -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_stats_rpc_time -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_step_CPU -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_step_CPU_requested_frequency -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_step_nodes -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_step_statistics -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_step_statistics_CPU -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_step_statistics_energy -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_step_step -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_step_task -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_step_tasks -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_step_time -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_step_time_system -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_step_time_total -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_step_time_user -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_step_tres -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_step_tres_consumed -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_step_tres_requested -](https://slurm.schedmd.com/rest_api.html)
- [v0_0_44_user_default -](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_account - [Up](https://slurm.schedmd.com/rest_api.html)
associations (optional)
[array[v0.0.44_assoc_short]](https://slurm.schedmd.com/rest_api.html)
coordinators (optional)
[array[v0.0.44_coord]](https://slurm.schedmd.com/rest_api.html)
description
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary string describing the account
name
[String](https://slurm.schedmd.com/rest_api.html) Account name
organization
[String](https://slurm.schedmd.com/rest_api.html) Organization to which the account belongs
flags (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Flags associated with this account
Enum:
### v0.0.44_account_short - [Up](https://slurm.schedmd.com/rest_api.html)
description (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary string describing the account
organization (optional)
[String](https://slurm.schedmd.com/rest_api.html) Organization to which the account belongs
### v0.0.44_accounting - [Up](https://slurm.schedmd.com/rest_api.html)
allocated (optional)
[v0_0_44_accounting_allocated](https://slurm.schedmd.com/rest_api.html)
id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Association ID or Workload characterization key ID format: int32
id_alt (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Alternate ID (not currently used) format: int32
start (optional)
[Long](https://slurm.schedmd.com/rest_api.html) When the record was started (UNIX timestamp) (UNIX timestamp or time string recognized by Slurm (e.g., '[MM/DD[/YY]-]HH:MM[:SS]')) format: int64
TRES (optional)
[v0.0.44_tres](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_accounts_add_cond - [Up](https://slurm.schedmd.com/rest_api.html)
accounts
[array[String]](https://slurm.schedmd.com/rest_api.html)
association (optional)
[v0.0.44_assoc_rec_set](https://slurm.schedmd.com/rest_api.html)
clusters (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_acct_gather_energy - [Up](https://slurm.schedmd.com/rest_api.html)
average_watts (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Average power consumption, in watts format: int32
base_consumed_energy (optional)
[Long](https://slurm.schedmd.com/rest_api.html) The energy consumed between when the node was powered on and the last time it was registered by slurmd, in joules format: int64
consumed_energy (optional)
[Long](https://slurm.schedmd.com/rest_api.html) The energy consumed between the last time the node was registered by the slurmd daemon and the last node energy accounting sample, in joules format: int64
current_watts (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
previous_consumed_energy (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Previous value of consumed_energy format: int64
last_collected (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Time when energy data was last retrieved (UNIX timestamp) (UNIX timestamp or time string recognized by Slurm (e.g., '[MM/DD[/YY]-]HH:MM[:SS]')) format: int64
### v0.0.44_assoc - [Up](https://slurm.schedmd.com/rest_api.html)
accounting (optional)
[array[v0.0.44_accounting]](https://slurm.schedmd.com/rest_api.html)
account (optional)
[String](https://slurm.schedmd.com/rest_api.html) Account name
cluster (optional)
[String](https://slurm.schedmd.com/rest_api.html) Cluster name
comment (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary comment
default (optional)
[v0_0_44_assoc_default](https://slurm.schedmd.com/rest_api.html)
flags (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Flags on the association
Enum:
max (optional)
[v0_0_44_assoc_max](https://slurm.schedmd.com/rest_api.html)
id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Unique ID (Association ID) format: int32
is_default (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) Is default association for user
lineage (optional)
[String](https://slurm.schedmd.com/rest_api.html) Complete path up the hierarchy to the root association
min (optional)
[v0_0_44_assoc_min](https://slurm.schedmd.com/rest_api.html)
parent_account (optional)
[String](https://slurm.schedmd.com/rest_api.html) Name of parent account
partition (optional)
[String](https://slurm.schedmd.com/rest_api.html) Partition name
priority (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
qos (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) List of QOS names
shares_raw (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Allocated shares used for fairshare calculation format: int32
user
[String](https://slurm.schedmd.com/rest_api.html) User name
### v0.0.44_assoc_rec_set - [Up](https://slurm.schedmd.com/rest_api.html)
comment (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary comment
defaultqos (optional)
[String](https://slurm.schedmd.com/rest_api.html) Default QOS
grpjobs (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
grpjobsaccrue (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
grpsubmitjobs (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
grptres (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
grptresmins (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
grptresrunmins (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
grpwall (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
maxjobs (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
maxjobsaccrue (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
maxsubmitjobs (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
maxtresminsperjob (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
maxtresrunmins (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
maxtresperjob (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
maxtrespernode (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
maxwalldurationperjob (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
minpriothresh (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
parent (optional)
[String](https://slurm.schedmd.com/rest_api.html) Name of parent account
priority (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
qoslevel (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) List of QOS names
fairshare (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Allocated shares used for fairshare calculation format: int32
### v0.0.44_assoc_shares_obj_wrap - [Up](https://slurm.schedmd.com/rest_api.html)
id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Association ID format: int32
cluster (optional)
[String](https://slurm.schedmd.com/rest_api.html) Cluster name
name (optional)
[String](https://slurm.schedmd.com/rest_api.html) Share name
parent (optional)
[String](https://slurm.schedmd.com/rest_api.html) Parent name
partition (optional)
[String](https://slurm.schedmd.com/rest_api.html) Partition name
shares_normalized (optional)
[v0.0.44_float64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
shares (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
tres (optional)
[v0_0_44_assoc_shares_obj_wrap_tres](https://slurm.schedmd.com/rest_api.html)
effective_usage (optional)
[v0.0.44_float64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
usage_normalized (optional)
[v0.0.44_float64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
usage (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Measure of tresbillableunits usage format: int64
fairshare (optional)
[v0_0_44_assoc_shares_obj_wrap_fairshare](https://slurm.schedmd.com/rest_api.html)
type (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) User or account association
Enum:
### v0.0.44_assoc_short - [Up](https://slurm.schedmd.com/rest_api.html)
account (optional)
[String](https://slurm.schedmd.com/rest_api.html) Account name
cluster (optional)
[String](https://slurm.schedmd.com/rest_api.html) Cluster name
partition (optional)
[String](https://slurm.schedmd.com/rest_api.html) Partition name
user
[String](https://slurm.schedmd.com/rest_api.html) User name
id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Numeric association ID format: int32
### v0.0.44_bf_exit_fields - [Up](https://slurm.schedmd.com/rest_api.html)
end_job_queue (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Reached end of queue format: int32
bf_max_job_start (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Reached number of jobs allowed to start format: int32
bf_max_job_test (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Reached number of jobs allowed to be tested format: int32
bf_max_time (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Reached maximum allowed scheduler time format: int32
bf_node_space_size (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Reached table size limit format: int32
state_changed (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) System state changed format: int32
### v0.0.44_cluster_rec - [Up](https://slurm.schedmd.com/rest_api.html)
controller (optional)
[v0_0_44_cluster_rec_controller](https://slurm.schedmd.com/rest_api.html)
flags (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Flags
Enum:
name (optional)
[String](https://slurm.schedmd.com/rest_api.html) ClusterName
nodes (optional)
[String](https://slurm.schedmd.com/rest_api.html) Node names
select_plugin (optional)
[String](https://slurm.schedmd.com/rest_api.html)
associations (optional)
[v0_0_44_cluster_rec_associations](https://slurm.schedmd.com/rest_api.html)
rpc_version (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) RPC version used in the cluster format: int32
tres (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_controller_ping - [Up](https://slurm.schedmd.com/rest_api.html)
hostname (optional)
[String](https://slurm.schedmd.com/rest_api.html) Target for ping
pinged (optional)
[String](https://slurm.schedmd.com/rest_api.html) Ping result
responding
[Boolean](https://slurm.schedmd.com/rest_api.html) If ping RPC responded with pong from controller
latency (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Number of microseconds it took to successfully ping or timeout format: int64
mode (optional)
[String](https://slurm.schedmd.com/rest_api.html) The operating mode of the responding slurmctld
primary
[Boolean](https://slurm.schedmd.com/rest_api.html) Is responding slurmctld the primary controller (Is responding slurmctld the primary controller)
### v0.0.44_coord - [Up](https://slurm.schedmd.com/rest_api.html)
name
[String](https://slurm.schedmd.com/rest_api.html) User name
direct (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) Indicates whether the coordinator was directly assigned to this account
### v0.0.44_cron_entry - [Up](https://slurm.schedmd.com/rest_api.html)
flags (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Flags
Enum:
minute (optional)
[String](https://slurm.schedmd.com/rest_api.html) Ranged string specifying eligible minute values (e.g. 0-10,50)
hour (optional)
[String](https://slurm.schedmd.com/rest_api.html) Ranged string specifying eligible hour values (e.g. 0-5,23)
day_of_month (optional)
[String](https://slurm.schedmd.com/rest_api.html) Ranged string specifying eligible day of month values (e.g. 0-10,29)
month (optional)
[String](https://slurm.schedmd.com/rest_api.html) Ranged string specifying eligible month values (e.g. 0-5,12)
day_of_week (optional)
[String](https://slurm.schedmd.com/rest_api.html) Ranged string specifying eligible day of week values (e.g.0-3,7)
specification (optional)
[String](https://slurm.schedmd.com/rest_api.html) Complete time specification (* means valid for all allowed values) - minute hour day_of_month month day_of_week
command (optional)
[String](https://slurm.schedmd.com/rest_api.html) Command to run
line (optional)
[v0_0_44_cron_entry_line](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_float64_no_val_struct - [Up](https://slurm.schedmd.com/rest_api.html)
set (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) True if number has been set; False if number is unset
infinite (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) True if number has been set to infinite; "set" and "number" will be ignored
number (optional)
[Double](https://slurm.schedmd.com/rest_api.html) If "set" is True the number will be set with value; otherwise ignore number contents format: double
### v0.0.44_instance - [Up](https://slurm.schedmd.com/rest_api.html)
cluster (optional)
[String](https://slurm.schedmd.com/rest_api.html) Cluster name
extra (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary string used for node filtering if extra constraints are enabled
instance_id (optional)
[String](https://slurm.schedmd.com/rest_api.html) Cloud instance ID
instance_type (optional)
[String](https://slurm.schedmd.com/rest_api.html) Cloud instance type
node_name (optional)
[String](https://slurm.schedmd.com/rest_api.html) NodeName
time (optional)
[v0_0_44_instance_time](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_job - [Up](https://slurm.schedmd.com/rest_api.html)
account (optional)
[String](https://slurm.schedmd.com/rest_api.html) Account the job ran under
comment (optional)
[v0_0_44_job_comment](https://slurm.schedmd.com/rest_api.html)
allocation_nodes (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) List of nodes allocated to the job format: int32
array (optional)
[v0_0_44_job_array](https://slurm.schedmd.com/rest_api.html)
association (optional)
[v0.0.44_assoc_short](https://slurm.schedmd.com/rest_api.html)
block (optional)
[String](https://slurm.schedmd.com/rest_api.html) The name of the block to be used (used with Blue Gene systems)
cluster (optional)
[String](https://slurm.schedmd.com/rest_api.html) Cluster name
constraints (optional)
[String](https://slurm.schedmd.com/rest_api.html) Feature(s) the job requested as a constraint
container (optional)
[String](https://slurm.schedmd.com/rest_api.html) Absolute path to OCI container bundle
derived_exit_code (optional)
[v0.0.44_process_exit_code_verbose](https://slurm.schedmd.com/rest_api.html)
time (optional)
[v0_0_44_job_time](https://slurm.schedmd.com/rest_api.html)
exit_code (optional)
[v0.0.44_process_exit_code_verbose](https://slurm.schedmd.com/rest_api.html)
extra (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary string used for node filtering if extra constraints are enabled
failed_node (optional)
[String](https://slurm.schedmd.com/rest_api.html) Name of node that caused job failure
flags (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Flags associated with this job
Enum:
group (optional)
[String](https://slurm.schedmd.com/rest_api.html) Group ID of the user that owns the job
het (optional)
[v0_0_44_job_het](https://slurm.schedmd.com/rest_api.html)
job_id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Job ID format: int32
name (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job name
licenses (optional)
[String](https://slurm.schedmd.com/rest_api.html) License(s) required by the job
mcs (optional)
[v0_0_44_job_mcs](https://slurm.schedmd.com/rest_api.html)
nodes (optional)
[String](https://slurm.schedmd.com/rest_api.html) Node(s) allocated to the job
partition (optional)
[String](https://slurm.schedmd.com/rest_api.html) Partition assigned to the job
hold (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) Hold (true) or release (false) job (Job held)
priority (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
qos (optional)
[String](https://slurm.schedmd.com/rest_api.html) Quality of Service assigned to the job
qosreq (optional)
[String](https://slurm.schedmd.com/rest_api.html) Requested QOS
required (optional)
[v0_0_44_job_required](https://slurm.schedmd.com/rest_api.html)
kill_request_user (optional)
[String](https://slurm.schedmd.com/rest_api.html) User ID that requested termination of the job
restart_cnt (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) How many times this job has been requeued/restarted format: int32
reservation (optional)
[v0_0_44_job_reservation](https://slurm.schedmd.com/rest_api.html)
script (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job batch script contents; only the first component in a HetJob is populated or honored
segment_size (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Requested segment size format: int32
stdin_expanded (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job stdin with expanded fields
stdout_expanded (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job stdout with expanded fields
stderr_expanded (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job stderr with expanded fields
stdout (optional)
[String](https://slurm.schedmd.com/rest_api.html) Path to stdout file
stderr (optional)
[String](https://slurm.schedmd.com/rest_api.html) Path to stderr file
stdin (optional)
[String](https://slurm.schedmd.com/rest_api.html) Path to stdin file
state (optional)
[v0_0_44_job_state](https://slurm.schedmd.com/rest_api.html)
steps (optional)
[array[v0.0.44_step]](https://slurm.schedmd.com/rest_api.html)
submit_line (optional)
[String](https://slurm.schedmd.com/rest_api.html) Command used to submit the job
tres (optional)
[v0_0_44_job_tres](https://slurm.schedmd.com/rest_api.html)
used_gres (optional)
[String](https://slurm.schedmd.com/rest_api.html) Generic resources used by job
user (optional)
[String](https://slurm.schedmd.com/rest_api.html) User that owns the job
wckey (optional)
[v0.0.44_wckey_tag_struct](https://slurm.schedmd.com/rest_api.html)
working_directory (optional)
[String](https://slurm.schedmd.com/rest_api.html) Path to current working directory
### v0.0.44_job_alloc_req - [Up](https://slurm.schedmd.com/rest_api.html)
hetjob (optional)
[array[v0.0.44_job_desc_msg]](https://slurm.schedmd.com/rest_api.html)
job (optional)
[v0.0.44_job_desc_msg](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_job_array_response_msg_entry - [Up](https://slurm.schedmd.com/rest_api.html)
job_id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Job ID for updated job format: int32
step_id (optional)
[String](https://slurm.schedmd.com/rest_api.html) Step ID for updated job
error (optional)
[String](https://slurm.schedmd.com/rest_api.html) Verbose update status or error
error_code (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Verbose update status or error format: int32
why (optional)
[String](https://slurm.schedmd.com/rest_api.html) Update response message
### v0.0.44_job_desc_msg - [Up](https://slurm.schedmd.com/rest_api.html)
account (optional)
[String](https://slurm.schedmd.com/rest_api.html) Account associated with the job
account_gather_frequency (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job accounting and profiling sampling intervals in seconds
admin_comment (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary comment made by administrator
allocation_node_list (optional)
[String](https://slurm.schedmd.com/rest_api.html) Local node making the resource allocation
allocation_node_port (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Port to send allocation confirmation to format: int32
argv (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
array (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job array index value specification
batch_features (optional)
[String](https://slurm.schedmd.com/rest_api.html) Features required for batch script's node
begin_time (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
flags (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Job flags
Enum:
burst_buffer (optional)
[String](https://slurm.schedmd.com/rest_api.html) Burst buffer specifications
clusters (optional)
[String](https://slurm.schedmd.com/rest_api.html) Clusters that a federated job can run on
cluster_constraint (optional)
[String](https://slurm.schedmd.com/rest_api.html) Required features that a federated cluster must have to have a sibling job submitted to it
comment (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary comment made by user
contiguous (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) True if job requires contiguous nodes
container (optional)
[String](https://slurm.schedmd.com/rest_api.html) Absolute path to OCI container bundle
container_id (optional)
[String](https://slurm.schedmd.com/rest_api.html) OCI container ID
core_specification (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Specialized core count format: int32
thread_specification (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Specialized thread count format: int32
cpu_binding (optional)
[String](https://slurm.schedmd.com/rest_api.html) Method for binding tasks to allocated CPUs
cpu_binding_flags (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Flags for CPU binding
Enum:
cpu_frequency (optional)
[String](https://slurm.schedmd.com/rest_api.html) Requested CPU frequency range
[-p2][:p3]
cpus_per_tres (optional)
[String](https://slurm.schedmd.com/rest_api.html) Semicolon delimited list of TRES=# values values indicating how many CPUs should be allocated for each specified TRES (currently only used for gres/gpu)
crontab (optional)
[v0.0.44_cron_entry](https://slurm.schedmd.com/rest_api.html)
deadline (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Latest time that the job may start (UNIX timestamp) (UNIX timestamp or time string recognized by Slurm (e.g., '[MM/DD[/YY]-]HH:MM[:SS]')) format: int64
delay_boot (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of seconds after job eligible start that nodes will be rebooted to satisfy feature specification format: int32
dependency (optional)
[String](https://slurm.schedmd.com/rest_api.html) Other jobs that must meet certain criteria before this job can start
end_time (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Expected end time (UNIX timestamp) (UNIX timestamp or time string recognized by Slurm (e.g., '[MM/DD[/YY]-]HH:MM[:SS]')) format: int64
environment (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
rlimits (optional)
[v0_0_44_job_desc_msg_rlimits](https://slurm.schedmd.com/rest_api.html)
excluded_nodes (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
extra (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary string used for node filtering if extra constraints are enabled
constraints (optional)
[String](https://slurm.schedmd.com/rest_api.html) Comma-separated list of features that are required
group_id (optional)
[String](https://slurm.schedmd.com/rest_api.html) Group ID of the user that owns the job
hetjob_group (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Unique sequence number applied to this component of the heterogeneous job format: int32
immediate (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) If true, exit if resources are not available within the time period specified
job_id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Job ID format: int32
kill_on_node_fail (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) If true, kill job on node failure
licenses (optional)
[String](https://slurm.schedmd.com/rest_api.html) License(s) required by the job
mail_type (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Mail event type(s)
Enum:
mail_user (optional)
[String](https://slurm.schedmd.com/rest_api.html) User to receive email notifications
mcs_label (optional)
[String](https://slurm.schedmd.com/rest_api.html) Multi-Category Security label on the job
memory_binding (optional)
[String](https://slurm.schedmd.com/rest_api.html) Binding map for map/mask_cpu
memory_binding_type (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Method for binding tasks to memory
Enum:
memory_per_tres (optional)
[String](https://slurm.schedmd.com/rest_api.html) Semicolon delimited list of TRES=# values indicating how much memory in megabytes should be allocated for each specified TRES (currently only used for gres/gpu)
name (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job name
network (optional)
[String](https://slurm.schedmd.com/rest_api.html) Network specs for job step
nice (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Requested job priority change format: int32
tasks (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of tasks format: int32
oom_kill_step (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Kill whole step in case of OOM in one of the tasks format: int32
open_mode (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Open mode used for stdout and stderr files
Enum:
reserve_ports (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Port to send various notification msg to format: int32
overcommit (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) Overcommit resources
partition (optional)
[String](https://slurm.schedmd.com/rest_api.html) Partition assigned to the job
distribution_plane_size (optional)
[v0.0.44_uint16_no_val_struct](https://slurm.schedmd.com/rest_api.html)
power_flags (optional)
[array[oas_any_type_not_mapped]](https://slurm.schedmd.com/rest_api.html)
prefer (optional)
[String](https://slurm.schedmd.com/rest_api.html) Comma-separated list of features that are preferred but not required
hold (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) Hold (true) or release (false) job (Job held)
priority (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
profile (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Profile used by the acct_gather_profile plugin
Enum:
qos (optional)
[String](https://slurm.schedmd.com/rest_api.html) Quality of Service assigned to the job
reboot (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) Node reboot requested before start
required_nodes (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
requeue (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) Determines whether the job may be requeued
reservation (optional)
[String](https://slurm.schedmd.com/rest_api.html) Name of reservation to use
script (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job batch script contents; only the first component in a HetJob is populated or honored
shared (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) How the job can share resources with other jobs, if at all
Enum:
site_factor (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Site-specific priority factor format: int32
spank_environment (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
step_id (optional)
[v0.0.44_slurm_step_id](https://slurm.schedmd.com/rest_api.html)
distribution (optional)
[String](https://slurm.schedmd.com/rest_api.html) Layout
time_limit (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
time_minimum (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
tres_bind (optional)
[String](https://slurm.schedmd.com/rest_api.html) Task to TRES binding directives
tres_freq (optional)
[String](https://slurm.schedmd.com/rest_api.html) TRES frequency directives
tres_per_job (optional)
[String](https://slurm.schedmd.com/rest_api.html) Comma-separated list of TRES=# values to be allocated for every job
tres_per_node (optional)
[String](https://slurm.schedmd.com/rest_api.html) Comma-separated list of TRES=# values to be allocated for every node
tres_per_socket (optional)
[String](https://slurm.schedmd.com/rest_api.html) Comma-separated list of TRES=# values to be allocated for every socket
tres_per_task (optional)
[String](https://slurm.schedmd.com/rest_api.html) Comma-separated list of TRES=# values to be allocated for every task
user_id (optional)
[String](https://slurm.schedmd.com/rest_api.html) User ID that owns the job
wait_all_nodes (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) If true, wait to start until after all nodes have booted
kill_warning_flags (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Flags related to job signals
Enum:
kill_warning_signal (optional)
[String](https://slurm.schedmd.com/rest_api.html) Signal to send when approaching end time (e.g. "10" or "USR1")
kill_warning_delay (optional)
[v0.0.44_uint16_no_val_struct](https://slurm.schedmd.com/rest_api.html)
current_working_directory (optional)
[String](https://slurm.schedmd.com/rest_api.html) Working directory to use for the job
cpus_per_task (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of CPUs required by each task format: int32
minimum_cpus (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Minimum number of CPUs required format: int32
maximum_cpus (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Maximum number of CPUs required format: int32
nodes (optional)
[String](https://slurm.schedmd.com/rest_api.html) Node count range specification (e.g. 1-15:4)
minimum_nodes (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Minimum node count format: int32
maximum_nodes (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Maximum node count format: int32
minimum_boards_per_node (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Boards per node required format: int32
minimum_sockets_per_board (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Sockets per board required format: int32
sockets_per_node (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Sockets per node required format: int32
threads_per_core (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Threads per core required format: int32
tasks_per_node (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of tasks to invoke on each node format: int32
tasks_per_socket (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of tasks to invoke on each socket format: int32
tasks_per_core (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of tasks to invoke on each core format: int32
tasks_per_board (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of tasks to invoke on each board format: int32
ntasks_per_tres (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of tasks that can access each GPU format: int32
minimum_cpus_per_node (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Minimum number of CPUs per node format: int32
memory_per_cpu (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
memory_per_node (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
temporary_disk_per_node (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Minimum tmp disk space required per node format: int32
selinux_context (optional)
[String](https://slurm.schedmd.com/rest_api.html) SELinux context
required_switches (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
segment_size (optional)
[v0.0.44_uint16_no_val_struct](https://slurm.schedmd.com/rest_api.html)
standard_error (optional)
[String](https://slurm.schedmd.com/rest_api.html) Path to stderr file
standard_input (optional)
[String](https://slurm.schedmd.com/rest_api.html) Path to stdin file
standard_output (optional)
[String](https://slurm.schedmd.com/rest_api.html) Path to stdout file
wait_for_switch (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Maximum time to wait for switches in seconds format: int32
wckey (optional)
[String](https://slurm.schedmd.com/rest_api.html) Workload characterization key
x11 (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) X11 forwarding options
Enum:
x11_magic_cookie (optional)
[String](https://slurm.schedmd.com/rest_api.html) Magic cookie for X11 forwarding
x11_target_host (optional)
[String](https://slurm.schedmd.com/rest_api.html) Hostname or UNIX socket if x11_target_port=0
x11_target_port (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) TCP port format: int32
### v0.0.44_job_info - [Up](https://slurm.schedmd.com/rest_api.html)
account (optional)
[String](https://slurm.schedmd.com/rest_api.html) Account associated with the job
accrue_time (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
admin_comment (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary comment made by administrator
allocating_node (optional)
[String](https://slurm.schedmd.com/rest_api.html) Local node making the resource allocation
array_job_id (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
array_task_id (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
array_max_tasks (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
array_task_string (optional)
[String](https://slurm.schedmd.com/rest_api.html) String expression of task IDs in this record
association_id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Unique identifier for the association format: int32
batch_features (optional)
[String](https://slurm.schedmd.com/rest_api.html) Features required for batch script's node
batch_flag (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) True if batch job
batch_host (optional)
[String](https://slurm.schedmd.com/rest_api.html) Name of host running batch script
flags (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Job flags
Enum:
burst_buffer (optional)
[String](https://slurm.schedmd.com/rest_api.html) Burst buffer specifications
burst_buffer_state (optional)
[String](https://slurm.schedmd.com/rest_api.html) Burst buffer state details
cluster (optional)
[String](https://slurm.schedmd.com/rest_api.html) Cluster name
cluster_features (optional)
[String](https://slurm.schedmd.com/rest_api.html) List of required cluster features
command (optional)
[String](https://slurm.schedmd.com/rest_api.html) Executed command
comment (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary comment
container (optional)
[String](https://slurm.schedmd.com/rest_api.html) Absolute path to OCI container bundle
container_id (optional)
[String](https://slurm.schedmd.com/rest_api.html) OCI container ID
contiguous (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) True if job requires contiguous nodes
core_spec (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Specialized core count format: int32
thread_spec (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Specialized thread count format: int32
cores_per_socket (optional)
[v0.0.44_uint16_no_val_struct](https://slurm.schedmd.com/rest_api.html)
billable_tres (optional)
[v0.0.44_float64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
cpus_per_task (optional)
[v0.0.44_uint16_no_val_struct](https://slurm.schedmd.com/rest_api.html)
cpu_frequency_minimum (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
cpu_frequency_maximum (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
cpu_frequency_governor (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
cpus_per_tres (optional)
[String](https://slurm.schedmd.com/rest_api.html) Semicolon delimited list of TRES=# values indicating how many CPUs should be allocated for each specified TRES (currently only used for gres/gpu)
cron (optional)
[String](https://slurm.schedmd.com/rest_api.html) Time specification for scrontab job
deadline (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
delay_boot (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
dependency (optional)
[String](https://slurm.schedmd.com/rest_api.html) Other jobs that must meet certain criteria before this job can start
derived_exit_code (optional)
[v0.0.44_process_exit_code_verbose](https://slurm.schedmd.com/rest_api.html)
eligible_time (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
end_time (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
excluded_nodes (optional)
[String](https://slurm.schedmd.com/rest_api.html) Comma-separated list of nodes that may not be used
exit_code (optional)
[v0.0.44_process_exit_code_verbose](https://slurm.schedmd.com/rest_api.html)
extra (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary string used for node filtering if extra constraints are enabled
failed_node (optional)
[String](https://slurm.schedmd.com/rest_api.html) Name of node that caused job failure
features (optional)
[String](https://slurm.schedmd.com/rest_api.html) Comma-separated list of features that are required
federation_origin (optional)
[String](https://slurm.schedmd.com/rest_api.html) Origin cluster's name (when using federation)
federation_siblings_active (optional)
[String](https://slurm.schedmd.com/rest_api.html) Active sibling job names
federation_siblings_viable (optional)
[String](https://slurm.schedmd.com/rest_api.html) Viable sibling job names
gres_detail (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
group_id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Group ID of the user that owns the job format: int32
group_name (optional)
[String](https://slurm.schedmd.com/rest_api.html) Group name of the user that owns the job
het_job_id (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
het_job_id_set (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job ID range for all heterogeneous job components
het_job_offset (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
job_id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Job ID format: int32
job_resources (optional)
[v0.0.44_job_res](https://slurm.schedmd.com/rest_api.html)
job_size_str (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
job_state (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Current state
Enum:
last_sched_evaluation (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
licenses (optional)
[String](https://slurm.schedmd.com/rest_api.html) License(s) required by the job
licenses_allocated (optional)
[String](https://slurm.schedmd.com/rest_api.html) License(s) allocated to the job
mail_type (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Mail event type(s)
Enum:
mail_user (optional)
[String](https://slurm.schedmd.com/rest_api.html) User to receive email notifications
max_cpus (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
max_nodes (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
mcs_label (optional)
[String](https://slurm.schedmd.com/rest_api.html) Multi-Category Security label on the job
memory_per_tres (optional)
[String](https://slurm.schedmd.com/rest_api.html) Semicolon delimited list of TRES=# values indicating how much memory in megabytes should be allocated for each specified TRES (currently only used for gres/gpu)
name (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job name
network (optional)
[String](https://slurm.schedmd.com/rest_api.html) Network specs for the job
nodes (optional)
[String](https://slurm.schedmd.com/rest_api.html) Node(s) allocated to the job
nice (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Requested job priority change format: int32
tasks_per_core (optional)
[v0.0.44_uint16_no_val_struct](https://slurm.schedmd.com/rest_api.html)
tasks_per_tres (optional)
[v0.0.44_uint16_no_val_struct](https://slurm.schedmd.com/rest_api.html)
tasks_per_node (optional)
[v0.0.44_uint16_no_val_struct](https://slurm.schedmd.com/rest_api.html)
tasks_per_socket (optional)
[v0.0.44_uint16_no_val_struct](https://slurm.schedmd.com/rest_api.html)
tasks_per_board (optional)
[v0.0.44_uint16_no_val_struct](https://slurm.schedmd.com/rest_api.html)
cpus (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
node_count (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
tasks (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
partition (optional)
[String](https://slurm.schedmd.com/rest_api.html) Partition assigned to the job
prefer (optional)
[String](https://slurm.schedmd.com/rest_api.html) Feature(s) the job requested but that are not required
memory_per_cpu (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
memory_per_node (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
minimum_cpus_per_node (optional)
[v0.0.44_uint16_no_val_struct](https://slurm.schedmd.com/rest_api.html)
minimum_tmp_disk_per_node (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
power (optional)
[v0_0_44_job_info_power](https://slurm.schedmd.com/rest_api.html)
preempt_time (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
preemptable_time (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
pre_sus_time (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
hold (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) Hold (true) or release (false) job (Job held)
priority (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
priority_by_partition (optional)
[array[v0.0.44_part_prio]](https://slurm.schedmd.com/rest_api.html)
profile (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Profile used by the acct_gather_profile plugin
Enum:
qos (optional)
[String](https://slurm.schedmd.com/rest_api.html) Quality of Service assigned to the job, if pending the QOS requested
reboot (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) Node reboot requested before start
required_nodes (optional)
[String](https://slurm.schedmd.com/rest_api.html) Comma-separated list of required nodes
required_switches (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Maximum number of switches format: int32
requeue (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) Determines whether the job may be requeued
resize_time (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
restart_cnt (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of job restarts format: int32
resv_name (optional)
[String](https://slurm.schedmd.com/rest_api.html) Name of reservation to use
scheduled_nodes (optional)
[String](https://slurm.schedmd.com/rest_api.html) List of nodes scheduled to be used for the job
segment_size (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Requested segment size format: int32
selinux_context (optional)
[String](https://slurm.schedmd.com/rest_api.html) SELinux context
shared (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) How the job can share resources with other jobs, if at all
Enum:
step_id (optional)
[v0.0.44_slurm_step_id](https://slurm.schedmd.com/rest_api.html)
sockets_per_board (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of sockets per board required format: int32
sockets_per_node (optional)
[v0.0.44_uint16_no_val_struct](https://slurm.schedmd.com/rest_api.html)
start_time (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
state_description (optional)
[String](https://slurm.schedmd.com/rest_api.html) Optional details for state_reason
state_reason (optional)
[String](https://slurm.schedmd.com/rest_api.html) Reason for current Pending or Failed state
standard_input (optional)
[String](https://slurm.schedmd.com/rest_api.html) Path to stdin file
standard_output (optional)
[String](https://slurm.schedmd.com/rest_api.html) Path to stdout file
standard_error (optional)
[String](https://slurm.schedmd.com/rest_api.html) Path to stderr file
stdin_expanded (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job stdin with expanded fields
stdout_expanded (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job stdout with expanded fields
stderr_expanded (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job stderr with expanded fields
submit_time (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
submit_line (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job submit line (e.g. 'sbatch -N3 job.sh job_arg'
suspend_time (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
system_comment (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary comment from slurmctld
time_limit (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
time_minimum (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
threads_per_core (optional)
[v0.0.44_uint16_no_val_struct](https://slurm.schedmd.com/rest_api.html)
tres_bind (optional)
[String](https://slurm.schedmd.com/rest_api.html) Task to TRES binding directives
tres_freq (optional)
[String](https://slurm.schedmd.com/rest_api.html) TRES frequency directives
tres_per_job (optional)
[String](https://slurm.schedmd.com/rest_api.html) Comma-separated list of TRES=# values to be allocated per job
tres_per_node (optional)
[String](https://slurm.schedmd.com/rest_api.html) Comma-separated list of TRES=# values to be allocated per node
tres_per_socket (optional)
[String](https://slurm.schedmd.com/rest_api.html) Comma-separated list of TRES=# values to be allocated per socket
tres_per_task (optional)
[String](https://slurm.schedmd.com/rest_api.html) Comma-separated list of TRES=# values to be allocated per task
tres_req_str (optional)
[String](https://slurm.schedmd.com/rest_api.html) TRES requested by the job
tres_alloc_str (optional)
[String](https://slurm.schedmd.com/rest_api.html) TRES used by the job
user_id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) User ID that owns the job format: int32
user_name (optional)
[String](https://slurm.schedmd.com/rest_api.html) User name that owns the job
maximum_switch_wait_time (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Maximum time to wait for switches in seconds format: int32
wckey (optional)
[String](https://slurm.schedmd.com/rest_api.html) Workload characterization key
current_working_directory (optional)
[String](https://slurm.schedmd.com/rest_api.html) Working directory to use for the job
### v0.0.44_job_modify - [Up](https://slurm.schedmd.com/rest_api.html)
comment (optional)
[v0_0_44_job_comment](https://slurm.schedmd.com/rest_api.html)
derived_exit_code (optional)
[v0.0.44_process_exit_code_verbose](https://slurm.schedmd.com/rest_api.html)
extra (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary string used for node filtering if extra constraints are enabled
tres (optional)
[v0_0_44_job_modify_tres](https://slurm.schedmd.com/rest_api.html)
wckey (optional)
[String](https://slurm.schedmd.com/rest_api.html) Workload characterization key
### v0.0.44_job_res - [Up](https://slurm.schedmd.com/rest_api.html)
select_type
[array[String]](https://slurm.schedmd.com/rest_api.html) Scheduler consumable resource selection type
Enum:
nodes (optional)
[v0_0_44_job_res_nodes](https://slurm.schedmd.com/rest_api.html)
cpus
[Integer](https://slurm.schedmd.com/rest_api.html) Number of allocated CPUs format: int32
threads_per_core
[v0.0.44_uint16_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_job_res_core - [Up](https://slurm.schedmd.com/rest_api.html)
index
[Integer](https://slurm.schedmd.com/rest_api.html) Core index format: int32
status
[array[String]](https://slurm.schedmd.com/rest_api.html) Core status
Enum:
### v0.0.44_job_res_node - [Up](https://slurm.schedmd.com/rest_api.html)
index
[Integer](https://slurm.schedmd.com/rest_api.html) Node index format: int32
name
[String](https://slurm.schedmd.com/rest_api.html) Node name
cpus (optional)
[v0_0_44_job_res_node_cpus](https://slurm.schedmd.com/rest_api.html)
memory (optional)
[v0_0_44_job_res_node_memory](https://slurm.schedmd.com/rest_api.html)
sockets
[array[v0.0.44_job_res_socket]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_job_res_socket - [Up](https://slurm.schedmd.com/rest_api.html)
index
[Integer](https://slurm.schedmd.com/rest_api.html) Core index format: int32
cores
[array[v0.0.44_job_res_core]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_job_submit_req - [Up](https://slurm.schedmd.com/rest_api.html)
script (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job batch script contents; Same as the script field in jobs[0] or job.
jobs (optional)
[array[v0.0.44_job_desc_msg]](https://slurm.schedmd.com/rest_api.html)
job (optional)
[v0.0.44_job_desc_msg](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_kill_jobs_msg - [Up](https://slurm.schedmd.com/rest_api.html)
account (optional)
[String](https://slurm.schedmd.com/rest_api.html) Filter jobs to a specific account
flags (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Filter jobs according to flags
Enum:
job_name (optional)
[String](https://slurm.schedmd.com/rest_api.html) Filter jobs to a specific name
jobs (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
partition (optional)
[String](https://slurm.schedmd.com/rest_api.html) Filter jobs to a specific partition
qos (optional)
[String](https://slurm.schedmd.com/rest_api.html) Filter jobs to a specific QOS
reservation (optional)
[String](https://slurm.schedmd.com/rest_api.html) Filter jobs to a specific reservation
signal (optional)
[String](https://slurm.schedmd.com/rest_api.html) Signal to send to jobs
job_state (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Filter jobs to a specific state
Enum:
user_id (optional)
[String](https://slurm.schedmd.com/rest_api.html) Filter jobs to a specific numeric user id
user_name (optional)
[String](https://slurm.schedmd.com/rest_api.html) Filter jobs to a specific user name
wckey (optional)
[String](https://slurm.schedmd.com/rest_api.html) Filter jobs to a specific wckey
nodes (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_kill_jobs_resp_job - [Up](https://slurm.schedmd.com/rest_api.html)
error (optional)
[v0_0_44_kill_jobs_resp_job_error](https://slurm.schedmd.com/rest_api.html)
step_id
[String](https://slurm.schedmd.com/rest_api.html) Job or Step ID that signaling failed
job_id
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
federation (optional)
[v0_0_44_kill_jobs_resp_job_federation](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_license - [Up](https://slurm.schedmd.com/rest_api.html)
LicenseName (optional)
[String](https://slurm.schedmd.com/rest_api.html) Name of the license
Total (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Total number of licenses present format: int32
Used (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of licenses in use format: int32
Free (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of licenses currently available format: int32
Remote (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) Indicates whether licenses are served by the database
Reserved (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of licenses reserved format: int32
LastConsumed (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Last known number of licenses that were consumed in the license manager (Remote Only) format: int32
LastDeficit (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of "missing licenses" from the cluster's perspective format: int32
LastUpdate (optional)
[Long](https://slurm.schedmd.com/rest_api.html) When the license information was last updated (UNIX Timestamp) (UNIX timestamp or time string recognized by Slurm (e.g., '[MM/DD[/YY]-]HH:MM[:SS]')) format: int64
Nodes (optional)
[String](https://slurm.schedmd.com/rest_api.html) HRes nodes
### v0.0.44_node - [Up](https://slurm.schedmd.com/rest_api.html)
architecture (optional)
[String](https://slurm.schedmd.com/rest_api.html) Computer architecture
burstbuffer_network_address (optional)
[String](https://slurm.schedmd.com/rest_api.html) Alternate network path to be used for sbcast network traffic
boards (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of Baseboards in nodes with a baseboard controller format: int32
boot_time (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
tls_cert_last_renewal (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
cert_flags (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Certmgr status flags
Enum:
cluster_name (optional)
[String](https://slurm.schedmd.com/rest_api.html) Cluster name (only set in federated environments)
cores (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of cores in a single physical processor socket format: int32
specialized_cores (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of cores reserved for system use format: int32
cpu_binding (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Default method for binding tasks to allocated CPUs format: int32
cpu_load (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) CPU load as reported by the OS format: int32
free_mem (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
cpus (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Total CPUs, including cores and threads format: int32
effective_cpus (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of effective CPUs (excluding specialized CPUs) format: int32
specialized_cpus (optional)
[String](https://slurm.schedmd.com/rest_api.html) Abstract CPU IDs on this node reserved for exclusive use by slurmd and slurmstepd
energy (optional)
[v0.0.44_acct_gather_energy](https://slurm.schedmd.com/rest_api.html)
external_sensors (optional)
[Object](https://slurm.schedmd.com/rest_api.html)
extra (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary string used for node filtering if extra constraints are enabled
power (optional)
[Object](https://slurm.schedmd.com/rest_api.html)
features (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
active_features (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
gpu_spec (optional)
[String](https://slurm.schedmd.com/rest_api.html) CPU cores reserved for jobs that also use a GPU
gres (optional)
[String](https://slurm.schedmd.com/rest_api.html) Generic resources
gres_drained (optional)
[String](https://slurm.schedmd.com/rest_api.html) Drained generic resources
gres_used (optional)
[String](https://slurm.schedmd.com/rest_api.html) Generic resources currently in use
instance_id (optional)
[String](https://slurm.schedmd.com/rest_api.html) Cloud instance ID
instance_type (optional)
[String](https://slurm.schedmd.com/rest_api.html) Cloud instance type
last_busy (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
mcs_label (optional)
[String](https://slurm.schedmd.com/rest_api.html) Multi-Category Security label
specialized_memory (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Combined memory limit, in MB, for Slurm compute node daemons format: int64
name (optional)
[String](https://slurm.schedmd.com/rest_api.html) NodeName
next_state_after_reboot (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) The state the node will be assigned after rebooting
Enum:
address (optional)
[String](https://slurm.schedmd.com/rest_api.html) NodeAddr, used to establish a communication path
hostname (optional)
[String](https://slurm.schedmd.com/rest_api.html) NodeHostname
state (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Node state(s) applicable to this node
Enum:
operating_system (optional)
[String](https://slurm.schedmd.com/rest_api.html) Operating system reported by the node
owner (optional)
[String](https://slurm.schedmd.com/rest_api.html) User allowed to run jobs on this node (unset if no restriction)
partitions (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
port (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) TCP port number of the slurmd format: int32
real_memory (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Total memory in MB on the node format: int64
res_cores_per_gpu (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of CPU cores per GPU restricted to GPU jobs format: int32
comment (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary comment
reason (optional)
[String](https://slurm.schedmd.com/rest_api.html) Describes why the node is in a "DOWN", "DRAINED", "DRAINING", "FAILING" or "FAIL" state
reason_changed_at (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
reason_set_by_user (optional)
[String](https://slurm.schedmd.com/rest_api.html) User who set the reason
resume_after (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
reservation (optional)
[String](https://slurm.schedmd.com/rest_api.html) Name of reservation containing this node
alloc_memory (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Total memory in MB currently allocated for jobs format: int64
alloc_cpus (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Total number of CPUs currently allocated for jobs format: int32
alloc_idle_cpus (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Total number of idle CPUs format: int32
tres_used (optional)
[String](https://slurm.schedmd.com/rest_api.html) Trackable resources currently allocated for jobs
tres_weighted (optional)
[Double](https://slurm.schedmd.com/rest_api.html) Ignored. Was weighted number of billable trackable resources allocated format: double
slurmd_start_time (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
sockets (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of physical processor sockets/chips on the node format: int32
threads (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of logical threads in a single physical core format: int32
temporary_disk (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Total size in MB of temporary disk storage in TmpFS format: int32
weight (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Weight of the node for scheduling purposes format: int32
topology (optional)
[String](https://slurm.schedmd.com/rest_api.html) Topology
tres (optional)
[String](https://slurm.schedmd.com/rest_api.html) Configured trackable resources
version (optional)
[String](https://slurm.schedmd.com/rest_api.html) Slurmd version
### v0.0.44_node_gres_layout - [Up](https://slurm.schedmd.com/rest_api.html)
name
[String](https://slurm.schedmd.com/rest_api.html) GRES name
type (optional)
[String](https://slurm.schedmd.com/rest_api.html) GRES type (optional)
count (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Count format: int64
index (optional)
[String](https://slurm.schedmd.com/rest_api.html) Index
### v0.0.44_node_resource_layout - [Up](https://slurm.schedmd.com/rest_api.html)
node
[String](https://slurm.schedmd.com/rest_api.html) Node name
sockets_per_node (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Sockets per node format: int32
cores_per_socket (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Cores per socket format: int32
mem_alloc (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Allocated memory format: int64
core_bitmap (optional)
[String](https://slurm.schedmd.com/rest_api.html) Abstract core bitmap
channel (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
gres (optional)
[array[v0.0.44_node_gres_layout]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_accounts_add_cond_resp - [Up](https://slurm.schedmd.com/rest_api.html)
association_condition
[v0.0.44_accounts_add_cond](https://slurm.schedmd.com/rest_api.html)
account (optional)
[v0.0.44_account_short](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_accounts_add_cond_resp_str - [Up](https://slurm.schedmd.com/rest_api.html)
added_accounts
[String](https://slurm.schedmd.com/rest_api.html) added_accounts
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_accounts_removed_resp - [Up](https://slurm.schedmd.com/rest_api.html)
removed_accounts
[array[String]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_accounts_resp - [Up](https://slurm.schedmd.com/rest_api.html)
accounts
[array[v0.0.44_account]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_assocs_removed_resp - [Up](https://slurm.schedmd.com/rest_api.html)
removed_associations
[array[String]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_assocs_resp - [Up](https://slurm.schedmd.com/rest_api.html)
associations
[array[v0.0.44_assoc]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_clusters_removed_resp - [Up](https://slurm.schedmd.com/rest_api.html)
deleted_clusters
[array[String]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_clusters_resp - [Up](https://slurm.schedmd.com/rest_api.html)
clusters
[array[v0.0.44_cluster_rec]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_create_node_req - [Up](https://slurm.schedmd.com/rest_api.html)
node_conf
[String](https://slurm.schedmd.com/rest_api.html) Node configuration line
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_diag_resp - [Up](https://slurm.schedmd.com/rest_api.html)
statistics
[v0.0.44_stats_msg](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_error - [Up](https://slurm.schedmd.com/rest_api.html)
description (optional)
[String](https://slurm.schedmd.com/rest_api.html) Long form error description
error_number (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Slurm numeric error identifier format: int32
error (optional)
[String](https://slurm.schedmd.com/rest_api.html) Short form error description
source (optional)
[String](https://slurm.schedmd.com/rest_api.html) Source of error or where error was first detected
### v0.0.44_openapi_instances_resp - [Up](https://slurm.schedmd.com/rest_api.html)
instances
[array[v0.0.44_instance]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_job_alloc_resp - [Up](https://slurm.schedmd.com/rest_api.html)
job_id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Submitted Job ID format: int32
job_submit_user_msg (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job submission user message
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_job_info_resp - [Up](https://slurm.schedmd.com/rest_api.html)
jobs
[array[v0.0.44_job_info]](https://slurm.schedmd.com/rest_api.html)
last_backfill
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
last_update
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_job_modify_req - [Up](https://slurm.schedmd.com/rest_api.html)
job_id_list (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
job_rec (optional)
[v0.0.44_job_modify](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_job_modify_resp - [Up](https://slurm.schedmd.com/rest_api.html)
results
[array[String]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_job_post_response - [Up](https://slurm.schedmd.com/rest_api.html)
results (optional)
[array[v0.0.44_job_array_response_msg_entry]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_job_submit_response - [Up](https://slurm.schedmd.com/rest_api.html)
job_id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) submitted Job ID format: int32
step_id (optional)
[String](https://slurm.schedmd.com/rest_api.html) submitted Step ID
job_submit_user_msg (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job submission user message
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_kill_job_resp - [Up](https://slurm.schedmd.com/rest_api.html)
status
[array[v0.0.44_kill_jobs_resp_job]](https://slurm.schedmd.com/rest_api.html) List of jobs signal responses
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_kill_jobs_resp - [Up](https://slurm.schedmd.com/rest_api.html)
status
[array[v0.0.44_kill_jobs_resp_job]](https://slurm.schedmd.com/rest_api.html) List of jobs signal responses
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_licenses_resp - [Up](https://slurm.schedmd.com/rest_api.html)
licenses
[array[v0.0.44_license]](https://slurm.schedmd.com/rest_api.html)
last_update
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_meta - [Up](https://slurm.schedmd.com/rest_api.html)
plugin (optional)
[v0_0_44_openapi_meta_plugin](https://slurm.schedmd.com/rest_api.html)
client (optional)
[v0_0_44_openapi_meta_client](https://slurm.schedmd.com/rest_api.html)
command (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
slurm (optional)
[v0_0_44_openapi_meta_slurm](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_nodes_resp - [Up](https://slurm.schedmd.com/rest_api.html)
nodes
[array[v0.0.44_node]](https://slurm.schedmd.com/rest_api.html)
last_update
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_partition_resp - [Up](https://slurm.schedmd.com/rest_api.html)
partitions
[array[v0.0.44_partition_info]](https://slurm.schedmd.com/rest_api.html)
last_update
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_ping_array_resp - [Up](https://slurm.schedmd.com/rest_api.html)
pings
[array[v0.0.44_controller_ping]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_reservation_mod_resp - [Up](https://slurm.schedmd.com/rest_api.html)
reservations
[array[v0.0.44_reservation_desc_msg]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_reservation_resp - [Up](https://slurm.schedmd.com/rest_api.html)
reservations
[array[v0.0.44_reservation_info]](https://slurm.schedmd.com/rest_api.html)
last_update
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_resource_layout_resp - [Up](https://slurm.schedmd.com/rest_api.html)
nodes
[array[v0.0.44_node_resource_layout]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_resp - [Up](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_shares_resp - [Up](https://slurm.schedmd.com/rest_api.html)
shares
[v0.0.44_shares_resp_msg](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_slurmdbd_config_resp - [Up](https://slurm.schedmd.com/rest_api.html)
clusters (optional)
[array[v0.0.44_cluster_rec]](https://slurm.schedmd.com/rest_api.html)
tres (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
accounts (optional)
[array[v0.0.44_account]](https://slurm.schedmd.com/rest_api.html)
users (optional)
[array[v0.0.44_user]](https://slurm.schedmd.com/rest_api.html)
qos (optional)
[array[v0.0.44_qos]](https://slurm.schedmd.com/rest_api.html)
wckeys (optional)
[array[v0.0.44_wckey]](https://slurm.schedmd.com/rest_api.html)
associations (optional)
[array[v0.0.44_assoc]](https://slurm.schedmd.com/rest_api.html)
instances (optional)
[array[v0.0.44_instance]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_slurmdbd_jobs_resp - [Up](https://slurm.schedmd.com/rest_api.html)
jobs
[array[v0.0.44_job]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_slurmdbd_ping_resp - [Up](https://slurm.schedmd.com/rest_api.html)
pings
[array[v0.0.44_slurmdbd_ping]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_slurmdbd_qos_removed_resp - [Up](https://slurm.schedmd.com/rest_api.html)
removed_qos
[array[String]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_slurmdbd_qos_resp - [Up](https://slurm.schedmd.com/rest_api.html)
qos
[array[v0.0.44_qos]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_slurmdbd_stats_resp - [Up](https://slurm.schedmd.com/rest_api.html)
statistics
[v0.0.44_stats_rec](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_tres_resp - [Up](https://slurm.schedmd.com/rest_api.html)
TRES
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_users_add_cond_resp - [Up](https://slurm.schedmd.com/rest_api.html)
association_condition
[v0.0.44_users_add_cond](https://slurm.schedmd.com/rest_api.html)
user
[v0.0.44_user_short](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_users_add_cond_resp_str - [Up](https://slurm.schedmd.com/rest_api.html)
added_users
[String](https://slurm.schedmd.com/rest_api.html) added_users
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_users_resp - [Up](https://slurm.schedmd.com/rest_api.html)
users
[array[v0.0.44_user]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_warning - [Up](https://slurm.schedmd.com/rest_api.html)
description (optional)
[String](https://slurm.schedmd.com/rest_api.html) Long form warning description
source (optional)
[String](https://slurm.schedmd.com/rest_api.html) Source of warning or where warning was first detected
### v0.0.44_openapi_wckey_removed_resp - [Up](https://slurm.schedmd.com/rest_api.html)
deleted_wckeys
[array[String]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_openapi_wckey_resp - [Up](https://slurm.schedmd.com/rest_api.html)
wckeys
[array[v0.0.44_wckey]](https://slurm.schedmd.com/rest_api.html)
meta (optional)
[v0.0.44_openapi_meta](https://slurm.schedmd.com/rest_api.html)
errors (optional)
[array[v0.0.44_openapi_error]](https://slurm.schedmd.com/rest_api.html)
warnings (optional)
[array[v0.0.44_openapi_warning]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_part_prio - [Up](https://slurm.schedmd.com/rest_api.html)
partition (optional)
[String](https://slurm.schedmd.com/rest_api.html) Partition name
priority (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Prospective job priority if it runs in this partition format: int32
### v0.0.44_partition_info - [Up](https://slurm.schedmd.com/rest_api.html)
nodes (optional)
[v0_0_44_partition_info_nodes](https://slurm.schedmd.com/rest_api.html)
accounts (optional)
[v0_0_44_partition_info_accounts](https://slurm.schedmd.com/rest_api.html)
groups (optional)
[v0_0_44_partition_info_groups](https://slurm.schedmd.com/rest_api.html)
qos (optional)
[v0_0_44_partition_info_qos](https://slurm.schedmd.com/rest_api.html)
alternate (optional)
[String](https://slurm.schedmd.com/rest_api.html) Alternate - Partition name of alternate partition to be used if the state of this partition is DRAIN or INACTIVE
tres (optional)
[v0_0_44_partition_info_tres](https://slurm.schedmd.com/rest_api.html)
cluster (optional)
[String](https://slurm.schedmd.com/rest_api.html) Cluster name
select_type (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Scheduler consumable resource selection type
Enum:
cpus (optional)
[v0_0_44_partition_info_cpus](https://slurm.schedmd.com/rest_api.html)
defaults (optional)
[v0_0_44_partition_info_defaults](https://slurm.schedmd.com/rest_api.html)
grace_time (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) GraceTime - Grace time in seconds to be extended to a job which has been selected for preemption format: int32
maximums (optional)
[v0_0_44_partition_info_maximums](https://slurm.schedmd.com/rest_api.html)
minimums (optional)
[v0_0_44_partition_info_minimums](https://slurm.schedmd.com/rest_api.html)
name (optional)
[String](https://slurm.schedmd.com/rest_api.html) PartitionName - Name by which the partition may be referenced
node_sets (optional)
[String](https://slurm.schedmd.com/rest_api.html) NodeSets - Comma-separated list of nodesets which are associated with this partition
priority (optional)
[v0_0_44_partition_info_priority](https://slurm.schedmd.com/rest_api.html)
timeouts (optional)
[v0_0_44_partition_info_timeouts](https://slurm.schedmd.com/rest_api.html)
topology (optional)
[String](https://slurm.schedmd.com/rest_api.html) Topology - Name of the topology, defined in topology.yaml, used by jobs in this partition
partition (optional)
[v0_0_44_partition_info_partition](https://slurm.schedmd.com/rest_api.html)
suspend_time (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_process_exit_code_verbose - [Up](https://slurm.schedmd.com/rest_api.html)
status (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Status given by return code
Enum:
return_code (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
signal (optional)
[v0_0_44_process_exit_code_verbose_signal](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_qos - [Up](https://slurm.schedmd.com/rest_api.html)
description (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary description
flags (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Flags, to avoid modifying current values specify NOT_SET
Enum:
id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Unique ID format: int32
limits (optional)
[v0_0_44_qos_limits](https://slurm.schedmd.com/rest_api.html)
name (optional)
[String](https://slurm.schedmd.com/rest_api.html) Name
preempt (optional)
[v0_0_44_qos_preempt](https://slurm.schedmd.com/rest_api.html)
priority (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
usage_factor (optional)
[v0.0.44_float64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
usage_threshold (optional)
[v0.0.44_float64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_reservation_core_spec - [Up](https://slurm.schedmd.com/rest_api.html)
node (optional)
[String](https://slurm.schedmd.com/rest_api.html) Name of reserved node
core (optional)
[String](https://slurm.schedmd.com/rest_api.html) IDs of reserved cores
### v0.0.44_reservation_desc_msg - [Up](https://slurm.schedmd.com/rest_api.html)
accounts (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
burst_buffer (optional)
[String](https://slurm.schedmd.com/rest_api.html) BurstBuffer
comment (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary string
core_count (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
duration (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
end_time (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
features (optional)
[String](https://slurm.schedmd.com/rest_api.html) Requested node features. Multiple values may be "&" separated if all features are required (AND operation) or separated by "|" if any of the specified features are required (OR operation). Parenthesis are also supported for features to be ANDed together with counts of nodes having the specified features.
flags (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Flags associated with this reservation. Note, to remove flags use "NO_" prefixed flag excluding NO_HOLD_JOBS_AFTER_END
Enum:
groups (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
licenses (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
max_start_delay (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
name (optional)
[String](https://slurm.schedmd.com/rest_api.html) ReservationName
node_count (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
node_list (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
partition (optional)
[String](https://slurm.schedmd.com/rest_api.html) Partition used to reserve nodes from. This will attempt to allocate all nodes in the specified partition unless you request fewer resources than are available with core_cnt, node_cnt or tres.
purge_completed (optional)
[v0_0_44_reservation_info_purge_completed](https://slurm.schedmd.com/rest_api.html)
start_time (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
tres (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
users (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_reservation_info - [Up](https://slurm.schedmd.com/rest_api.html)
accounts (optional)
[String](https://slurm.schedmd.com/rest_api.html) Comma-separated list of permitted accounts
burst_buffer (optional)
[String](https://slurm.schedmd.com/rest_api.html) BurstBuffer - Burst buffer resources reserved
core_count (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) CoreCnt - Number of cores reserved format: int32
core_specializations (optional)
[array[v0.0.44_reservation_core_spec]](https://slurm.schedmd.com/rest_api.html)
end_time (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
features (optional)
[String](https://slurm.schedmd.com/rest_api.html) Features - Expression describing the reservation's required node features
flags (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Flags associated with this reservation
Enum:
groups (optional)
[String](https://slurm.schedmd.com/rest_api.html) Groups - Comma-separated list of permitted groups
licenses (optional)
[String](https://slurm.schedmd.com/rest_api.html) Licenses - Comma-separated list of licenses reserved
max_start_delay (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) MaxStartDelay - Maximum time an eligible job not requesting this reservation can delay a job requesting it in seconds format: int32
name (optional)
[String](https://slurm.schedmd.com/rest_api.html) ReservationName - Name of the reservation
node_count (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) NodeCnt - Number of nodes reserved format: int32
node_list (optional)
[String](https://slurm.schedmd.com/rest_api.html) Nodes - Comma-separated list of node names and/or node ranges reserved
partition (optional)
[String](https://slurm.schedmd.com/rest_api.html) PartitionName - Partition used to reserve nodes from
purge_completed (optional)
[v0_0_44_reservation_info_purge_completed](https://slurm.schedmd.com/rest_api.html)
start_time (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
watts (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
tres (optional)
[String](https://slurm.schedmd.com/rest_api.html) Comma-separated list of required TRES
users (optional)
[String](https://slurm.schedmd.com/rest_api.html) Comma-separated list of permitted users
### v0.0.44_reservation_mod_req - [Up](https://slurm.schedmd.com/rest_api.html)
reservations (optional)
[array[v0.0.44_reservation_desc_msg]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_rollup_stats - [Up](https://slurm.schedmd.com/rest_api.html)
hourly (optional)
[v0_0_44_rollup_stats_hourly](https://slurm.schedmd.com/rest_api.html)
daily (optional)
[v0_0_44_rollup_stats_daily](https://slurm.schedmd.com/rest_api.html)
monthly (optional)
[v0_0_44_rollup_stats_monthly](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_schedule_exit_fields - [Up](https://slurm.schedmd.com/rest_api.html)
end_job_queue (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Reached end of queue format: int32
default_queue_depth (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Reached number of jobs allowed to be tested format: int32
max_job_start (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Reached number of jobs allowed to start format: int32
max_rpc_cnt (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Reached RPC limit format: int32
max_sched_time (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Reached maximum allowed scheduler time format: int32
licenses (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Blocked on licenses format: int32
### v0.0.44_shares_float128_tres - [Up](https://slurm.schedmd.com/rest_api.html)
name (optional)
[String](https://slurm.schedmd.com/rest_api.html) TRES name
value (optional)
[BigDecimal](https://slurm.schedmd.com/rest_api.html) TRES value
### v0.0.44_shares_resp_msg - [Up](https://slurm.schedmd.com/rest_api.html)
shares (optional)
[array[v0.0.44_assoc_shares_obj_wrap]](https://slurm.schedmd.com/rest_api.html)
total_shares (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Total number of shares format: int64
### v0.0.44_shares_uint64_tres - [Up](https://slurm.schedmd.com/rest_api.html)
name (optional)
[String](https://slurm.schedmd.com/rest_api.html) TRES name
value (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_slurm_step_id - [Up](https://slurm.schedmd.com/rest_api.html)
sluid (optional)
[String](https://slurm.schedmd.com/rest_api.html) SLUID (Slurm Lexicographically-sortable Unique ID)
job_id (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
step_het_component (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
step_id (optional)
[String](https://slurm.schedmd.com/rest_api.html) Job step ID
### v0.0.44_slurmdbd_ping - [Up](https://slurm.schedmd.com/rest_api.html)
hostname
[String](https://slurm.schedmd.com/rest_api.html) Target for ping
responding
[Boolean](https://slurm.schedmd.com/rest_api.html) If ping RPC responded with pong from slurmdbd
latency
[Long](https://slurm.schedmd.com/rest_api.html) Number of microseconds it took to successfully ping or timeout format: int64
primary
[Boolean](https://slurm.schedmd.com/rest_api.html) Is responding slurmdbd the primary controller (Is responding slurmctld the primary controller)
### v0.0.44_stats_msg - [Up](https://slurm.schedmd.com/rest_api.html)
parts_packed (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Zero if only RPC statistic included format: int32
req_time (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
req_time_start (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
server_thread_count (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of current active slurmctld threads format: int32
agent_queue_size (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of enqueued outgoing RPC requests in an internal retry list format: int32
agent_count (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of agent threads format: int32
agent_thread_count (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Total number of active threads created by all agent threads format: int32
dbd_agent_queue_size (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of messages for SlurmDBD that are queued format: int32
gettimeofday_latency (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Latency of 1000 calls to the gettimeofday() syscall in microseconds, as measured at controller startup format: int32
schedule_cycle_max (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Max time of any scheduling cycle in microseconds since last reset format: int32
schedule_cycle_last (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Time in microseconds for last scheduling cycle format: int32
schedule_cycle_sum (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Total run time in microseconds for all scheduling cycles since last reset format: int64
schedule_cycle_total (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of scheduling cycles since last reset format: int32
schedule_cycle_mean (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Mean time in microseconds for all scheduling cycles since last reset format: int64
schedule_cycle_mean_depth (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Mean of the number of jobs processed in a scheduling cycle format: int64
schedule_cycle_per_minute (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Number of scheduling executions per minute format: int64
schedule_cycle_depth (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Total number of jobs processed in scheduling cycles format: int32
schedule_exit (optional)
[v0.0.44_schedule_exit_fields](https://slurm.schedmd.com/rest_api.html)
schedule_queue_length (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of jobs pending in queue format: int32
jobs_submitted (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of jobs submitted since last reset format: int32
jobs_started (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of jobs started since last reset format: int32
jobs_completed (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of jobs completed since last reset format: int32
jobs_canceled (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of jobs canceled since the last reset format: int32
jobs_failed (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of jobs failed due to slurmd or other internal issues since last reset format: int32
jobs_pending (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of jobs pending at the time of listed in job_state_ts format: int32
jobs_running (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of jobs running at the time of listed in job_state_ts format: int32
job_states_ts (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
bf_backfilled_jobs (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of jobs started through backfilling since last slurm start format: int32
bf_last_backfilled_jobs (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of jobs started through backfilling since last reset format: int32
bf_backfilled_het_jobs (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of heterogeneous job components started through backfilling since last Slurm start format: int32
bf_cycle_counter (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of backfill scheduling cycles since last reset format: int32
bf_cycle_mean (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Mean time in microseconds of backfilling scheduling cycles since last reset format: int64
bf_depth_mean (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Mean number of eligible to run jobs processed during all backfilling scheduling cycles since last reset format: int64
bf_depth_mean_try (optional)
[Long](https://slurm.schedmd.com/rest_api.html) The subset of Depth Mean that the backfill scheduler attempted to schedule format: int64
bf_cycle_sum (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Total time in microseconds of backfilling scheduling cycles since last reset format: int64
bf_cycle_last (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Execution time in microseconds of last backfill scheduling cycle format: int32
bf_cycle_max (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Execution time in microseconds of longest backfill scheduling cycle format: int32
bf_exit (optional)
[v0.0.44_bf_exit_fields](https://slurm.schedmd.com/rest_api.html)
bf_last_depth (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of processed jobs during last backfilling scheduling cycle format: int32
bf_last_depth_try (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of processed jobs during last backfilling scheduling cycle that had a chance to start using available resources format: int32
bf_depth_sum (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Total number of jobs processed during all backfilling scheduling cycles since last reset format: int32
bf_depth_try_sum (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Subset of bf_depth_sum that the backfill scheduler attempted to schedule format: int32
bf_queue_len (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of jobs pending to be processed by backfilling algorithm format: int32
bf_queue_len_mean (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Mean number of jobs pending to be processed by backfilling algorithm format: int64
bf_queue_len_sum (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Total number of jobs pending to be processed by backfilling algorithm since last reset format: int32
bf_table_size (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of different time slots tested by the backfill scheduler in its last iteration format: int32
bf_table_size_sum (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Total number of different time slots tested by the backfill scheduler format: int32
bf_table_size_mean (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Mean number of different time slots tested by the backfill scheduler format: int64
bf_when_last_cycle (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
bf_active (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) Backfill scheduler currently running
rpcs_by_message_type (optional)
[array[v0.0.44_stats_msg_rpc_type]](https://slurm.schedmd.com/rest_api.html) RPCs by type
rpcs_by_user (optional)
[array[v0.0.44_stats_msg_rpc_user]](https://slurm.schedmd.com/rest_api.html) RPCs by user
pending_rpcs (optional)
[array[v0.0.44_stats_msg_rpc_queue]](https://slurm.schedmd.com/rest_api.html) Pending RPCs
pending_rpcs_by_hostlist (optional)
[array[v0.0.44_stats_msg_rpc_dump]](https://slurm.schedmd.com/rest_api.html) Pending RPCs by hostlist
### v0.0.44_stats_msg_rpc_dump - [Up](https://slurm.schedmd.com/rest_api.html)
type_id
[Integer](https://slurm.schedmd.com/rest_api.html) Message type as integer format: int32
message_type
[String](https://slurm.schedmd.com/rest_api.html) Message type as string (Slurm RPC message type)
count
[array[String]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_stats_msg_rpc_queue - [Up](https://slurm.schedmd.com/rest_api.html)
type_id
[Integer](https://slurm.schedmd.com/rest_api.html) Message type as integer format: int32
message_type
[String](https://slurm.schedmd.com/rest_api.html) Message type as string (Slurm RPC message type)
count
[Integer](https://slurm.schedmd.com/rest_api.html) Number of pending RPCs queued format: int32
### v0.0.44_stats_msg_rpc_type - [Up](https://slurm.schedmd.com/rest_api.html)
type_id
[Integer](https://slurm.schedmd.com/rest_api.html) Message type as integer format: int32
message_type
[String](https://slurm.schedmd.com/rest_api.html) Message type as string (Slurm RPC message type)
count
[Integer](https://slurm.schedmd.com/rest_api.html) Number of RPCs received format: int32
queued
[Integer](https://slurm.schedmd.com/rest_api.html) Number of RPCs queued format: int32
dropped
[Long](https://slurm.schedmd.com/rest_api.html) Number of RPCs dropped format: int64
cycle_last
[Integer](https://slurm.schedmd.com/rest_api.html) Number of RPCs processed within the last RPC queue cycle format: int32
cycle_max
[Integer](https://slurm.schedmd.com/rest_api.html) Maximum number of RPCs processed within a RPC queue cycle since start format: int32
total_time
[Long](https://slurm.schedmd.com/rest_api.html) Total time spent processing RPC in seconds format: int64
average_time
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_stats_msg_rpc_user - [Up](https://slurm.schedmd.com/rest_api.html)
user_id
[Integer](https://slurm.schedmd.com/rest_api.html) User ID (numeric) format: int32
user
[String](https://slurm.schedmd.com/rest_api.html) User name
count
[Integer](https://slurm.schedmd.com/rest_api.html) Number of RPCs received format: int32
total_time
[Long](https://slurm.schedmd.com/rest_api.html) Total time spent processing RPC in seconds format: int64
average_time
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_stats_rec - [Up](https://slurm.schedmd.com/rest_api.html)
time_start (optional)
[Long](https://slurm.schedmd.com/rest_api.html) When data collection started (UNIX timestamp) (UNIX timestamp or time string recognized by Slurm (e.g., '[MM/DD[/YY]-]HH:MM[:SS]')) format: int64
rollups (optional)
[v0.0.44_rollup_stats](https://slurm.schedmd.com/rest_api.html)
RPCs (optional)
[array[v0.0.44_stats_rpc]](https://slurm.schedmd.com/rest_api.html)
users (optional)
[array[v0.0.44_stats_user]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_stats_rpc - [Up](https://slurm.schedmd.com/rest_api.html)
rpc (optional)
[String](https://slurm.schedmd.com/rest_api.html) RPC type
count (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of RPCs processed format: int32
time (optional)
[v0_0_44_stats_rpc_time](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_stats_user - [Up](https://slurm.schedmd.com/rest_api.html)
user (optional)
[String](https://slurm.schedmd.com/rest_api.html) User ID
count (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of RPCs processed format: int32
time (optional)
[v0_0_44_stats_rpc_time](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_step - [Up](https://slurm.schedmd.com/rest_api.html)
time (optional)
[v0_0_44_step_time](https://slurm.schedmd.com/rest_api.html)
exit_code (optional)
[v0.0.44_process_exit_code_verbose](https://slurm.schedmd.com/rest_api.html)
nodes (optional)
[v0_0_44_step_nodes](https://slurm.schedmd.com/rest_api.html)
tasks (optional)
[v0_0_44_step_tasks](https://slurm.schedmd.com/rest_api.html)
pid (optional)
[String](https://slurm.schedmd.com/rest_api.html) Deprecated; Process ID
CPU (optional)
[v0_0_44_step_CPU](https://slurm.schedmd.com/rest_api.html)
kill_request_user (optional)
[String](https://slurm.schedmd.com/rest_api.html) User ID that requested termination of the step
state (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Current state
Enum:
statistics (optional)
[v0_0_44_step_statistics](https://slurm.schedmd.com/rest_api.html)
step (optional)
[v0_0_44_step_step](https://slurm.schedmd.com/rest_api.html)
task (optional)
[v0_0_44_step_task](https://slurm.schedmd.com/rest_api.html)
tres (optional)
[v0_0_44_step_tres](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_tres - [Up](https://slurm.schedmd.com/rest_api.html)
type
[String](https://slurm.schedmd.com/rest_api.html) TRES type (CPU, MEM, etc)
name (optional)
[String](https://slurm.schedmd.com/rest_api.html) TRES name (if applicable)
id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) ID used in the database format: int32
count (optional)
[Long](https://slurm.schedmd.com/rest_api.html) TRES count (0 if listed generically) format: int64
### v0.0.44_uint16_no_val_struct - [Up](https://slurm.schedmd.com/rest_api.html)
set (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) True if number has been set; False if number is unset
infinite (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) True if number has been set to infinite; "set" and "number" will be ignored
number (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) If "set" is True the number will be set with value; otherwise ignore number contents format: int32
### v0.0.44_uint32_no_val_struct - [Up](https://slurm.schedmd.com/rest_api.html)
set (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) True if number has been set; False if number is unset
infinite (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) True if number has been set to infinite; "set" and "number" will be ignored
number (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) If "set" is True the number will be set with value; otherwise ignore number contents format: int32
### v0.0.44_uint64_no_val_struct - [Up](https://slurm.schedmd.com/rest_api.html)
set (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) True if number has been set; False if number is unset
infinite (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) True if number has been set to infinite; "set" and "number" will be ignored
number (optional)
[Long](https://slurm.schedmd.com/rest_api.html) If "set" is True the number will be set with value; otherwise ignore number contents format: int64
### v0.0.44_update_node_msg - [Up](https://slurm.schedmd.com/rest_api.html)
comment (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary comment
cpu_bind (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Default method for binding tasks to allocated CPUs format: int32
extra (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary string used for node filtering if extra constraints are enabled
features (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
features_act (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
gres (optional)
[String](https://slurm.schedmd.com/rest_api.html) Generic resources
address (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
hostname (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
name (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
state (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) New state to assign to the node
Enum:
reason (optional)
[String](https://slurm.schedmd.com/rest_api.html) Reason for node being DOWN or DRAINING
reason_uid (optional)
[String](https://slurm.schedmd.com/rest_api.html) User ID to associate with the reason (needed if user root is sending message)
resume_after (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
topology_str (optional)
[String](https://slurm.schedmd.com/rest_api.html) Topology
weight (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_user - [Up](https://slurm.schedmd.com/rest_api.html)
administrator_level (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) AdminLevel granted to the user
Enum:
associations (optional)
[array[v0.0.44_assoc_short]](https://slurm.schedmd.com/rest_api.html)
coordinators (optional)
[array[v0.0.44_coord]](https://slurm.schedmd.com/rest_api.html)
default (optional)
[v0_0_44_user_default](https://slurm.schedmd.com/rest_api.html)
flags (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Flags associated with this user
Enum:
name
[String](https://slurm.schedmd.com/rest_api.html) User name
old_name (optional)
[String](https://slurm.schedmd.com/rest_api.html) Previous user name
wckeys (optional)
[array[v0.0.44_wckey]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_user_short - [Up](https://slurm.schedmd.com/rest_api.html)
adminlevel (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) AdminLevel granted to the user
Enum:
defaultqos (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Default QOS format: int32
defaultaccount (optional)
[String](https://slurm.schedmd.com/rest_api.html) Default account
defaultwckey (optional)
[String](https://slurm.schedmd.com/rest_api.html) Default WCKey
### v0.0.44_users_add_cond - [Up](https://slurm.schedmd.com/rest_api.html)
accounts (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
association (optional)
[v0.0.44_assoc_rec_set](https://slurm.schedmd.com/rest_api.html)
clusters (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
partitions (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
users
[array[String]](https://slurm.schedmd.com/rest_api.html)
wckeys (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
### v0.0.44_wckey - [Up](https://slurm.schedmd.com/rest_api.html)
accounting (optional)
[array[v0.0.44_accounting]](https://slurm.schedmd.com/rest_api.html)
cluster
[String](https://slurm.schedmd.com/rest_api.html) Cluster name
id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Unique ID for this user-cluster-wckey combination format: int32
name
[String](https://slurm.schedmd.com/rest_api.html) WCKey name
user
[String](https://slurm.schedmd.com/rest_api.html) User name
flags (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Flags associated with this WCKey
Enum:
### v0.0.44_wckey_tag_struct - [Up](https://slurm.schedmd.com/rest_api.html)
wckey
[String](https://slurm.schedmd.com/rest_api.html) WCKey name
flags
[array[String]](https://slurm.schedmd.com/rest_api.html) Active flags
Enum:
### v0_0_44_accounting_allocated - [Up](https://slurm.schedmd.com/rest_api.html)
seconds (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Number of seconds allocated format: int64
### v0_0_44_assoc_default - [Up](https://slurm.schedmd.com/rest_api.html)
qos (optional)
[String](https://slurm.schedmd.com/rest_api.html) Default QOS
### v0_0_44_assoc_max - [Up](https://slurm.schedmd.com/rest_api.html)
jobs (optional)
[v0_0_44_assoc_max_jobs](https://slurm.schedmd.com/rest_api.html)
tres (optional)
[v0_0_44_assoc_max_tres](https://slurm.schedmd.com/rest_api.html)
per (optional)
[v0_0_44_assoc_max_per](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_assoc_max_jobs - [Up](https://slurm.schedmd.com/rest_api.html)
per (optional)
[v0_0_44_assoc_max_jobs_per](https://slurm.schedmd.com/rest_api.html)
active (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
accruing (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
total (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_assoc_max_jobs_per - [Up](https://slurm.schedmd.com/rest_api.html)
count (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
accruing (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
submitted (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
wall_clock (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_assoc_max_per - [Up](https://slurm.schedmd.com/rest_api.html)
account (optional)
[v0_0_44_assoc_max_per_account](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_assoc_max_per_account - [Up](https://slurm.schedmd.com/rest_api.html)
wall_clock (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_assoc_max_tres - [Up](https://slurm.schedmd.com/rest_api.html)
total (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
group (optional)
[v0_0_44_assoc_max_tres_group](https://slurm.schedmd.com/rest_api.html)
minutes (optional)
[v0_0_44_assoc_max_tres_minutes](https://slurm.schedmd.com/rest_api.html)
per (optional)
[v0_0_44_assoc_max_tres_per](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_assoc_max_tres_group - [Up](https://slurm.schedmd.com/rest_api.html)
minutes (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
active (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_assoc_max_tres_minutes - [Up](https://slurm.schedmd.com/rest_api.html)
total (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
per (optional)
[v0_0_44_qos_limits_min_tres_per](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_assoc_max_tres_per - [Up](https://slurm.schedmd.com/rest_api.html)
job (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
node (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_assoc_min - [Up](https://slurm.schedmd.com/rest_api.html)
priority_threshold (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_assoc_shares_obj_wrap_fairshare - [Up](https://slurm.schedmd.com/rest_api.html)
factor (optional)
[v0.0.44_float64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
level (optional)
[v0.0.44_float64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_assoc_shares_obj_wrap_tres - [Up](https://slurm.schedmd.com/rest_api.html)
run_seconds (optional)
[array[v0.0.44_shares_uint64_tres]](https://slurm.schedmd.com/rest_api.html)
group_minutes (optional)
[array[v0.0.44_shares_uint64_tres]](https://slurm.schedmd.com/rest_api.html)
usage (optional)
[array[v0.0.44_shares_float128_tres]](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_cluster_rec_associations - [Up](https://slurm.schedmd.com/rest_api.html)
root (optional)
[v0.0.44_assoc_short](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_cluster_rec_controller - [Up](https://slurm.schedmd.com/rest_api.html)
host (optional)
[String](https://slurm.schedmd.com/rest_api.html) ControlHost
port (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) ControlPort format: int32
### v0_0_44_cron_entry_line - [Up](https://slurm.schedmd.com/rest_api.html)
start (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Start of this entry in file format: int32
end (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) End of this entry in file format: int32
### v0_0_44_instance_time - [Up](https://slurm.schedmd.com/rest_api.html)
time_end (optional)
[Long](https://slurm.schedmd.com/rest_api.html) When the instance will end (UNIX timestamp) (UNIX timestamp or time string recognized by Slurm (e.g., '[MM/DD[/YY]-]HH:MM[:SS]')) format: int64
time_start (optional)
[Long](https://slurm.schedmd.com/rest_api.html) When the instance will start (UNIX timestamp) (UNIX timestamp or time string recognized by Slurm (e.g., '[MM/DD[/YY]-]HH:MM[:SS]')) format: int64
### v0_0_44_job_array - [Up](https://slurm.schedmd.com/rest_api.html)
job_id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Job ID of job array, or 0 if N/A format: int32
limits (optional)
[v0_0_44_job_array_limits](https://slurm.schedmd.com/rest_api.html)
task_id (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
task (optional)
[String](https://slurm.schedmd.com/rest_api.html) String expression of task IDs in this record
### v0_0_44_job_array_limits - [Up](https://slurm.schedmd.com/rest_api.html)
max (optional)
[v0_0_44_job_array_limits_max](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_job_array_limits_max - [Up](https://slurm.schedmd.com/rest_api.html)
running (optional)
[v0_0_44_job_array_limits_max_running](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_job_array_limits_max_running - [Up](https://slurm.schedmd.com/rest_api.html)
tasks (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Maximum number of simultaneously running tasks, 0 if no limit format: int32
### v0_0_44_job_comment - [Up](https://slurm.schedmd.com/rest_api.html)
administrator (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary comment made by administrator
job (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary comment made by user
system (optional)
[String](https://slurm.schedmd.com/rest_api.html) Arbitrary comment from slurmctld
### v0_0_44_job_desc_msg_rlimits - [Up](https://slurm.schedmd.com/rest_api.html)
cpu (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
fsize (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
data (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
stack (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
core (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
rss (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
nproc (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
nofile (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
memlock (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
as (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_job_het - [Up](https://slurm.schedmd.com/rest_api.html)
job_id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Heterogeneous job ID, if applicable format: int32
job_offset (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_job_info_power - [Up](https://slurm.schedmd.com/rest_api.html)
flags (optional)
[array[oas_any_type_not_mapped]](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_job_mcs - [Up](https://slurm.schedmd.com/rest_api.html)
label (optional)
[String](https://slurm.schedmd.com/rest_api.html) Multi-Category Security label on the job
### v0_0_44_job_modify_tres - [Up](https://slurm.schedmd.com/rest_api.html)
allocated (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_job_required - [Up](https://slurm.schedmd.com/rest_api.html)
CPUs (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Minimum number of CPUs required format: int32
memory_per_cpu (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
memory_per_node (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_job_res_node_cpus - [Up](https://slurm.schedmd.com/rest_api.html)
count (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Total number of CPUs assigned to job format: int32
used (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Total number of CPUs used by job format: int32
### v0_0_44_job_res_node_memory - [Up](https://slurm.schedmd.com/rest_api.html)
used (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Total memory (MiB) used by job format: int64
allocated (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Total memory (MiB) allocated to job format: int64
### v0_0_44_job_res_nodes - [Up](https://slurm.schedmd.com/rest_api.html)
count (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of allocated nodes format: int32
select_type (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Node scheduling selection method
Enum:
list (optional)
[String](https://slurm.schedmd.com/rest_api.html) Node(s) allocated to the job
whole (optional)
[Boolean](https://slurm.schedmd.com/rest_api.html) Whether whole nodes were allocated
allocation (optional)
[array[v0.0.44_job_res_node]](https://slurm.schedmd.com/rest_api.html) Job resources for a node
### v0_0_44_job_reservation - [Up](https://slurm.schedmd.com/rest_api.html)
id (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Unique identifier of requested reservation format: int32
name (optional)
[String](https://slurm.schedmd.com/rest_api.html) Name of reservation to use
requested (optional)
[String](https://slurm.schedmd.com/rest_api.html) Comma-separated list of requested reservation names
### v0_0_44_job_state - [Up](https://slurm.schedmd.com/rest_api.html)
current (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Current state
Enum:
reason (optional)
[String](https://slurm.schedmd.com/rest_api.html) Reason for previous Pending or Failed state
### v0_0_44_job_time - [Up](https://slurm.schedmd.com/rest_api.html)
elapsed (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Elapsed time in seconds format: int32
eligible (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Time when the job became eligible to run (UNIX timestamp) (UNIX timestamp or time string recognized by Slurm (e.g., '[MM/DD[/YY]-]HH:MM[:SS]')) format: int64
end (optional)
[Long](https://slurm.schedmd.com/rest_api.html) End time (UNIX timestamp) (UNIX timestamp or time string recognized by Slurm (e.g., '[MM/DD[/YY]-]HH:MM[:SS]')) format: int64
planned (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
start (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Time execution began (UNIX timestamp) (UNIX timestamp or time string recognized by Slurm (e.g., '[MM/DD[/YY]-]HH:MM[:SS]')) format: int64
submission (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Time when the job was submitted (UNIX timestamp) (UNIX timestamp or time string recognized by Slurm (e.g., '[MM/DD[/YY]-]HH:MM[:SS]')) format: int64
suspended (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Total time in suspended state in seconds format: int32
system (optional)
[v0_0_44_job_time_system](https://slurm.schedmd.com/rest_api.html)
limit (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
total (optional)
[v0_0_44_job_time_total](https://slurm.schedmd.com/rest_api.html)
user (optional)
[v0_0_44_job_time_user](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_job_time_system - [Up](https://slurm.schedmd.com/rest_api.html)
seconds (optional)
[Long](https://slurm.schedmd.com/rest_api.html) System CPU time used by the job in seconds format: int64
microseconds (optional)
[Long](https://slurm.schedmd.com/rest_api.html) System CPU time used by the job in microseconds format: int64
### v0_0_44_job_time_total - [Up](https://slurm.schedmd.com/rest_api.html)
seconds (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Sum of System and User CPU time used by the job in seconds format: int64
microseconds (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Sum of System and User CPU time used by the job in microseconds format: int64
### v0_0_44_job_time_user - [Up](https://slurm.schedmd.com/rest_api.html)
seconds (optional)
[Long](https://slurm.schedmd.com/rest_api.html) User CPU time used by the job in seconds format: int64
microseconds (optional)
[Long](https://slurm.schedmd.com/rest_api.html) User CPU time used by the job in microseconds format: int64
### v0_0_44_job_tres - [Up](https://slurm.schedmd.com/rest_api.html)
allocated (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
requested (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_kill_jobs_resp_job_error - [Up](https://slurm.schedmd.com/rest_api.html)
string (optional)
[String](https://slurm.schedmd.com/rest_api.html) String error encountered signaling job
code (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Numeric error encountered signaling job format: int32
message (optional)
[String](https://slurm.schedmd.com/rest_api.html) Error message why signaling job failed
### v0_0_44_kill_jobs_resp_job_federation - [Up](https://slurm.schedmd.com/rest_api.html)
sibling (optional)
[String](https://slurm.schedmd.com/rest_api.html) Name of federation sibling (may be empty for non-federation)
### v0_0_44_openapi_meta_client - [Up](https://slurm.schedmd.com/rest_api.html)
source (optional)
[String](https://slurm.schedmd.com/rest_api.html) Client source description
user (optional)
[String](https://slurm.schedmd.com/rest_api.html) Client user (if known)
group (optional)
[String](https://slurm.schedmd.com/rest_api.html) Client group (if known)
### v0_0_44_openapi_meta_plugin - [Up](https://slurm.schedmd.com/rest_api.html)
type (optional)
[String](https://slurm.schedmd.com/rest_api.html) Slurm plugin type (if applicable)
name (optional)
[String](https://slurm.schedmd.com/rest_api.html) Slurm plugin name (if applicable)
data_parser (optional)
[String](https://slurm.schedmd.com/rest_api.html) Slurm data_parser plugin
accounting_storage (optional)
[String](https://slurm.schedmd.com/rest_api.html) Slurm accounting plugin
### v0_0_44_openapi_meta_slurm - [Up](https://slurm.schedmd.com/rest_api.html)
version (optional)
[v0_0_44_openapi_meta_slurm_version](https://slurm.schedmd.com/rest_api.html)
release (optional)
[String](https://slurm.schedmd.com/rest_api.html) Slurm release string
cluster (optional)
[String](https://slurm.schedmd.com/rest_api.html) Slurm cluster name
### v0_0_44_openapi_meta_slurm_version - [Up](https://slurm.schedmd.com/rest_api.html)
major (optional)
[String](https://slurm.schedmd.com/rest_api.html) Slurm release major version
micro (optional)
[String](https://slurm.schedmd.com/rest_api.html) Slurm release micro version
minor (optional)
[String](https://slurm.schedmd.com/rest_api.html) Slurm release minor version
### v0_0_44_partition_info_accounts - [Up](https://slurm.schedmd.com/rest_api.html)
allowed (optional)
[String](https://slurm.schedmd.com/rest_api.html) AllowAccounts - Comma-separated list of accounts which may execute jobs in the partition
deny (optional)
[String](https://slurm.schedmd.com/rest_api.html) DenyAccounts - Comma-separated list of accounts which may not execute jobs in the partition
### v0_0_44_partition_info_cpus - [Up](https://slurm.schedmd.com/rest_api.html)
task_binding (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) CpuBind - Default method controlling how tasks are bound to allocated resources format: int32
total (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) TotalCPUs - Number of CPUs available in this partition format: int32
### v0_0_44_partition_info_defaults - [Up](https://slurm.schedmd.com/rest_api.html)
memory_per_cpu (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Raw value for DefMemPerCPU or DefMemPerNode format: int64
partition_memory_per_cpu (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
partition_memory_per_node (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
time (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
job (optional)
[String](https://slurm.schedmd.com/rest_api.html) JobDefaults - Comma-separated list of job default values (this field is only used to set new defaults)
### v0_0_44_partition_info_groups - [Up](https://slurm.schedmd.com/rest_api.html)
allowed (optional)
[String](https://slurm.schedmd.com/rest_api.html) AllowGroups - Comma-separated list of group names which may execute jobs in this partition
### v0_0_44_partition_info_maximums - [Up](https://slurm.schedmd.com/rest_api.html)
cpus_per_node (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
cpus_per_socket (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
memory_per_cpu (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Raw value for MaxMemPerCPU or MaxMemPerNode format: int64
partition_memory_per_cpu (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
partition_memory_per_node (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
nodes (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
shares (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) OverSubscribe - Controls the ability of the partition to execute more than one job at a time on each resource format: int32
oversubscribe (optional)
[v0_0_44_partition_info_maximums_oversubscribe](https://slurm.schedmd.com/rest_api.html)
time (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
over_time_limit (optional)
[v0.0.44_uint16_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_partition_info_maximums_oversubscribe - [Up](https://slurm.schedmd.com/rest_api.html)
jobs (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Maximum number of jobs allowed to oversubscribe resources format: int32
flags (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Flags applicable to the OverSubscribe setting
Enum:
### v0_0_44_partition_info_minimums - [Up](https://slurm.schedmd.com/rest_api.html)
nodes (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) MinNodes - Minimum count of nodes which may be allocated to any single job format: int32
### v0_0_44_partition_info_nodes - [Up](https://slurm.schedmd.com/rest_api.html)
allowed_allocation (optional)
[String](https://slurm.schedmd.com/rest_api.html) AllocNodes - Comma-separated list of nodes from which users can submit jobs in the partition
configured (optional)
[String](https://slurm.schedmd.com/rest_api.html) Nodes - Comma-separated list of nodes which are associated with this partition
total (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) TotalNodes - Number of nodes available in this partition format: int32
### v0_0_44_partition_info_partition - [Up](https://slurm.schedmd.com/rest_api.html)
state (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) Current state(s)
Enum:
### v0_0_44_partition_info_priority - [Up](https://slurm.schedmd.com/rest_api.html)
job_factor (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) PriorityJobFactor - Partition factor used by priority/multifactor plugin in calculating job priority format: int32
tier (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) PriorityTier - Controls the order in which the scheduler evaluates jobs from different partitions format: int32
### v0_0_44_partition_info_qos - [Up](https://slurm.schedmd.com/rest_api.html)
allowed (optional)
[String](https://slurm.schedmd.com/rest_api.html) AllowQOS - Comma-separated list of Qos which may execute jobs in the partition
deny (optional)
[String](https://slurm.schedmd.com/rest_api.html) DenyQOS - Comma-separated list of Qos which may not execute jobs in the partition
assigned (optional)
[String](https://slurm.schedmd.com/rest_api.html) QOS - QOS name containing limits that will apply to all jobs in this partition
### v0_0_44_partition_info_timeouts - [Up](https://slurm.schedmd.com/rest_api.html)
resume (optional)
[v0.0.44_uint16_no_val_struct](https://slurm.schedmd.com/rest_api.html)
suspend (optional)
[v0.0.44_uint16_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_partition_info_tres - [Up](https://slurm.schedmd.com/rest_api.html)
billing_weights (optional)
[String](https://slurm.schedmd.com/rest_api.html) TRESBillingWeights - Billing weights of each tracked TRES type that will be used in calculating the usage of a job
configured (optional)
[String](https://slurm.schedmd.com/rest_api.html) TRES - Number of each applicable TRES type available in this partition
### v0_0_44_process_exit_code_verbose_signal - [Up](https://slurm.schedmd.com/rest_api.html)
id (optional)
[v0.0.44_uint16_no_val_struct](https://slurm.schedmd.com/rest_api.html)
name (optional)
[String](https://slurm.schedmd.com/rest_api.html) Signal sent to process (name)
### v0_0_44_qos_limits - [Up](https://slurm.schedmd.com/rest_api.html)
grace_time (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) GraceTime - Preemption grace time in seconds to be extended to a job which has been selected for preemption format: int32
max (optional)
[v0_0_44_qos_limits_max](https://slurm.schedmd.com/rest_api.html)
factor (optional)
[v0.0.44_float64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
min (optional)
[v0_0_44_qos_limits_min](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_qos_limits_max - [Up](https://slurm.schedmd.com/rest_api.html)
active_jobs (optional)
[v0_0_44_qos_limits_max_active_jobs](https://slurm.schedmd.com/rest_api.html)
jobs (optional)
[v0_0_44_qos_limits_max_jobs](https://slurm.schedmd.com/rest_api.html)
tres (optional)
[v0_0_44_qos_limits_max_tres](https://slurm.schedmd.com/rest_api.html)
wall_clock (optional)
[v0_0_44_qos_limits_max_wall_clock](https://slurm.schedmd.com/rest_api.html)
accruing (optional)
[v0_0_44_qos_limits_max_jobs_active_jobs](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_qos_limits_max_active_jobs - [Up](https://slurm.schedmd.com/rest_api.html)
accruing (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
count (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_qos_limits_max_jobs - [Up](https://slurm.schedmd.com/rest_api.html)
count (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
active_jobs (optional)
[v0_0_44_qos_limits_max_jobs_active_jobs](https://slurm.schedmd.com/rest_api.html)
per (optional)
[v0_0_44_qos_limits_max_jobs_active_jobs_per](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_qos_limits_max_jobs_active_jobs - [Up](https://slurm.schedmd.com/rest_api.html)
per (optional)
[v0_0_44_qos_limits_max_jobs_active_jobs_per](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_qos_limits_max_jobs_active_jobs_per - [Up](https://slurm.schedmd.com/rest_api.html)
account (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
user (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_qos_limits_max_tres - [Up](https://slurm.schedmd.com/rest_api.html)
total (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
minutes (optional)
[v0_0_44_qos_limits_max_tres_minutes](https://slurm.schedmd.com/rest_api.html)
per (optional)
[v0_0_44_qos_limits_max_tres_per](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_qos_limits_max_tres_minutes - [Up](https://slurm.schedmd.com/rest_api.html)
total (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
per (optional)
[v0_0_44_qos_limits_max_tres_minutes_per](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_qos_limits_max_tres_minutes_per - [Up](https://slurm.schedmd.com/rest_api.html)
qos (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
job (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
account (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
user (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_qos_limits_max_tres_per - [Up](https://slurm.schedmd.com/rest_api.html)
account (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
job (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
node (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
user (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_qos_limits_max_wall_clock - [Up](https://slurm.schedmd.com/rest_api.html)
per (optional)
[v0_0_44_qos_limits_max_wall_clock_per](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_qos_limits_max_wall_clock_per - [Up](https://slurm.schedmd.com/rest_api.html)
qos (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
job (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_qos_limits_min - [Up](https://slurm.schedmd.com/rest_api.html)
priority_threshold (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
tres (optional)
[v0_0_44_qos_limits_min_tres](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_qos_limits_min_tres - [Up](https://slurm.schedmd.com/rest_api.html)
per (optional)
[v0_0_44_qos_limits_min_tres_per](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_qos_limits_min_tres_per - [Up](https://slurm.schedmd.com/rest_api.html)
job (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_qos_preempt - [Up](https://slurm.schedmd.com/rest_api.html)
list (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
mode (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html) PreemptMode - Mechanism used to preempt jobs or enable gang scheduling
Enum:
exempt_time (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_reservation_info_purge_completed - [Up](https://slurm.schedmd.com/rest_api.html)
time (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_rollup_stats_daily - [Up](https://slurm.schedmd.com/rest_api.html)
count (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of daily rollups since last_run format: int32
last_run (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Last time daily rollup ran (UNIX timestamp) (UNIX timestamp or time string recognized by Slurm (e.g., '[MM/DD[/YY]-]HH:MM[:SS]')) format: int64
duration (optional)
[v0_0_44_rollup_stats_daily_duration](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_rollup_stats_daily_duration - [Up](https://slurm.schedmd.com/rest_api.html)
last (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Total time spent doing daily daily rollup (seconds) format: int64
max (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Longest daily rollup time (seconds) format: int64
time (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Total time spent doing daily rollups (seconds) format: int64
### v0_0_44_rollup_stats_hourly - [Up](https://slurm.schedmd.com/rest_api.html)
count (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of hourly rollups since last_run format: int32
last_run (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Last time hourly rollup ran (UNIX timestamp) (UNIX timestamp or time string recognized by Slurm (e.g., '[MM/DD[/YY]-]HH:MM[:SS]')) format: int64
duration (optional)
[v0_0_44_rollup_stats_hourly_duration](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_rollup_stats_hourly_duration - [Up](https://slurm.schedmd.com/rest_api.html)
last (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Total time spent doing last daily rollup (seconds) format: int64
max (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Longest hourly rollup time (seconds) format: int64
time (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Total time spent doing hourly rollups (seconds) format: int64
### v0_0_44_rollup_stats_monthly - [Up](https://slurm.schedmd.com/rest_api.html)
count (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of monthly rollups since last_run format: int32
last_run (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Last time monthly rollup ran (UNIX timestamp) (UNIX timestamp or time string recognized by Slurm (e.g., '[MM/DD[/YY]-]HH:MM[:SS]')) format: int64
duration (optional)
[v0_0_44_rollup_stats_monthly_duration](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_rollup_stats_monthly_duration - [Up](https://slurm.schedmd.com/rest_api.html)
last (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Total time spent doing monthly daily rollup (seconds) format: int64
max (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Longest monthly rollup time (seconds) format: int64
time (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Total time spent doing monthly rollups (seconds) format: int64
### v0_0_44_stats_rpc_time - [Up](https://slurm.schedmd.com/rest_api.html)
average (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Average RPC processing time in microseconds format: int64
total (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Total RPC processing time in microseconds format: int64
### v0_0_44_step_CPU - [Up](https://slurm.schedmd.com/rest_api.html)
requested_frequency (optional)
[v0_0_44_step_CPU_requested_frequency](https://slurm.schedmd.com/rest_api.html)
governor (optional)
[String](https://slurm.schedmd.com/rest_api.html) Requested CPU frequency governor in kHz
### v0_0_44_step_CPU_requested_frequency - [Up](https://slurm.schedmd.com/rest_api.html)
min (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
max (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_step_nodes - [Up](https://slurm.schedmd.com/rest_api.html)
count (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Number of nodes in the job step format: int32
range (optional)
[String](https://slurm.schedmd.com/rest_api.html) Node(s) allocated to the job step
list (optional)
[array[String]](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_step_statistics - [Up](https://slurm.schedmd.com/rest_api.html)
CPU (optional)
[v0_0_44_step_statistics_CPU](https://slurm.schedmd.com/rest_api.html)
energy (optional)
[v0_0_44_step_statistics_energy](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_step_statistics_CPU - [Up](https://slurm.schedmd.com/rest_api.html)
actual_frequency (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Average weighted CPU frequency of all tasks in kHz format: int64
### v0_0_44_step_statistics_energy - [Up](https://slurm.schedmd.com/rest_api.html)
consumed (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_step_step - [Up](https://slurm.schedmd.com/rest_api.html)
id (optional)
[String](https://slurm.schedmd.com/rest_api.html) Step ID (Slurm job step ID)
name (optional)
[String](https://slurm.schedmd.com/rest_api.html) Step name
stderr (optional)
[String](https://slurm.schedmd.com/rest_api.html) Path to stderr file
stdin (optional)
[String](https://slurm.schedmd.com/rest_api.html) Path to stdin file
stdout (optional)
[String](https://slurm.schedmd.com/rest_api.html) Path to stdout file
stderr_expanded (optional)
[String](https://slurm.schedmd.com/rest_api.html) Step stderr with expanded fields
stdin_expanded (optional)
[String](https://slurm.schedmd.com/rest_api.html) Step stdin with expanded fields
stdout_expanded (optional)
[String](https://slurm.schedmd.com/rest_api.html) Step stdout with expanded fields
### v0_0_44_step_task - [Up](https://slurm.schedmd.com/rest_api.html)
distribution (optional)
[String](https://slurm.schedmd.com/rest_api.html) The layout of the step was when it was running
### v0_0_44_step_tasks - [Up](https://slurm.schedmd.com/rest_api.html)
count (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Total number of tasks format: int32
### v0_0_44_step_time - [Up](https://slurm.schedmd.com/rest_api.html)
elapsed (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Elapsed time in seconds format: int32
end (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
start (optional)
[v0.0.44_uint64_no_val_struct](https://slurm.schedmd.com/rest_api.html)
suspended (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Total time in suspended state in seconds format: int32
system (optional)
[v0_0_44_step_time_system](https://slurm.schedmd.com/rest_api.html)
limit (optional)
[v0.0.44_uint32_no_val_struct](https://slurm.schedmd.com/rest_api.html)
total (optional)
[v0_0_44_step_time_total](https://slurm.schedmd.com/rest_api.html)
user (optional)
[v0_0_44_step_time_user](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_step_time_system - [Up](https://slurm.schedmd.com/rest_api.html)
seconds (optional)
[Long](https://slurm.schedmd.com/rest_api.html) System CPU time used by the step in seconds format: int64
microseconds (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) System CPU time used by the step in microseconds format: int32
### v0_0_44_step_time_total - [Up](https://slurm.schedmd.com/rest_api.html)
seconds (optional)
[Long](https://slurm.schedmd.com/rest_api.html) Total CPU time used by the step in seconds format: int64
microseconds (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Total CPU time used by the step in microseconds format: int32
### v0_0_44_step_time_user - [Up](https://slurm.schedmd.com/rest_api.html)
seconds (optional)
[Long](https://slurm.schedmd.com/rest_api.html) User CPU time used by the step in seconds format: int64
microseconds (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) User CPU time used by the step in microseconds format: int32
### v0_0_44_step_tres - [Up](https://slurm.schedmd.com/rest_api.html)
requested (optional)
[v0_0_44_step_tres_requested](https://slurm.schedmd.com/rest_api.html)
consumed (optional)
[v0_0_44_step_tres_consumed](https://slurm.schedmd.com/rest_api.html)
allocated (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_step_tres_consumed - [Up](https://slurm.schedmd.com/rest_api.html)
max (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
min (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
average (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
total (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_step_tres_requested - [Up](https://slurm.schedmd.com/rest_api.html)
max (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
min (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
average (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
total (optional)
[array[v0.0.44_tres]](https://slurm.schedmd.com/rest_api.html)
### v0_0_44_user_default - [Up](https://slurm.schedmd.com/rest_api.html)
qos (optional)
[Integer](https://slurm.schedmd.com/rest_api.html) Default QOS format: int32
account (optional)
[String](https://slurm.schedmd.com/rest_api.html) Default account
wckey (optional)
[String](https://slurm.schedmd.com/rest_api.html) Default WCKey
