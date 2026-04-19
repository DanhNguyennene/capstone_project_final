---
source_url: https://slurm.schedmd.com/SLUG17/cli_filter-slug2017/cli_filter.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:34 UTC
title: "cli_filter"
---

# cli_filter

```text
function slurm_job_submit(req, partitions, uid)
return check_qos(req, nil)
end
function slurm_job_modify(req, desc, partitions, uid)
return check_qos(req, desc)
end
function check_qos(req, desc)
local qos = read_str_field(req, desc, "qos")
if qos == "premium" then
slurm.log_user('premium job disabled at present, please use regular')
return slurm.ERROR
end
local user_balance, acct_balance, cost_est
user_balance = get_user_balance(job, desc)
cost_est = get_cost_estimate(job, desc)
if user_balance < cost_est then
req['qos'] = 'scavenger'
end
return slurm.SUCCESS
end
function read_str_field(req, desc, field)
local value = ""
if desc ~= nil and desc[field] ~= nil then
value = desc[field]
end
if req ~= nil and req[field] ~= nil then
value = req[field]
end
return value
end
```
