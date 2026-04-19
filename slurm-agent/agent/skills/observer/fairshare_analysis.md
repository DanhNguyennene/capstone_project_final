# Fairshare and Priority Analysis

**When to use:** User asks about job priority, why their job is behind others, fairshare scores, or how to improve scheduling position.

## Key Concepts
- Slurm priority = FairShare + Age + QOS + Partition + Nice factors.
- **FairShare**: ratio of `(allocated shares) / (actual usage)`. Score 1.0 = perfect; <0.5 = over-utilized.
- `sprio` shows per-factor priority breakdown for queued jobs.
- `sshare` shows fairshare tree with current usage vs allocated shares.
- Usage decays over time (PriorityDecayHalfLife in slurm.conf).

## Steps

### Step 1 – Show pending jobs with priority breakdown
```
sprio(user="<user>")
```
Or for all pending jobs: `sprio()` (may be verbose).
Columns: `JOBID`, `PARTITION`, `PRIORITY`, `FAIRSHARE`, `AGE`, `QOS`.

### Step 2 – Show fairshare tree
```
sshare(user="<user>")
```
Or for an account: `sshare(account="<account>")`.
Key columns: `Account`, `User`, `RawShares`, `NormShares`, `RawUsage`, `NormUsage`, `LevelFS` (the fairshare score).
- `LevelFS` < 0.5 → high usage, lower priority.
- `LevelFS` > 1.0 → under-utilized, higher priority.

### Step 3 – Check QOS priority boost
```
sacctmgr_list(entity="qos", params="format=Name,Priority,GrpTRES,MaxTRESPJ,MaxWall")
```
Find the user's QOS and note the Priority factor.

### Step 4 – Interpret
- If FairShare score is low: user has used more than their allocated share recently.
- If QOS priority is 0: no boost from QOS.
- Age factor grows the longer a job waits (resets on requeue).
- Suggest waiting (depletion through time decay) or requesting a high-priority QOS.

## Output Format
Provide a table of the top-priority pending jobs with factor breakdown, then one sentence explaining the primary bottleneck (fairshare vs QOS vs age).
