#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const datasetPath = path.join(__dirname, 'dataset.json');

const aliases = new Map([
  ['sacctmgr_list', 'sacctmgr_show'],
  ['sacctmgr', 'sacctmgr_show'],
  ['scontrol', 'scontrol_show'],
]);

const scenarioDependencyJobs = {
  healthy: '1001',
  failed: '2004',
  pending: '3004',
  mixed: '4001',
  debug_needed: '5008',
};

function canonical(tool) {
  return aliases.get(tool) || tool;
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function ensureState(test) {
  test.source_state = test.source_state && typeof test.source_state === 'object' ? test.source_state : {};
  test.target_state = test.target_state && typeof test.target_state === 'object' ? test.target_state : clone(test.source_state);
  test.source_state.jobs = test.source_state.jobs && typeof test.source_state.jobs === 'object' ? test.source_state.jobs : {};
  test.target_state.jobs = test.target_state.jobs && typeof test.target_state.jobs === 'object' ? test.target_state.jobs : clone(test.source_state.jobs);
  test.source_state.nodes = test.source_state.nodes && typeof test.source_state.nodes === 'object' ? test.source_state.nodes : {};
  test.target_state.nodes = test.target_state.nodes && typeof test.target_state.nodes === 'object' ? test.target_state.nodes : clone(test.source_state.nodes);
}

function syncTargetFromSource(test) {
  test.target_state = clone(test.source_state);
}

function jobIdsFromPrompt(input) {
  const ids = new Set();
  const text = String(input || '');
  for (const regex of [
    /\b(?:job|jobs|jobid|job\s*id)\s*#?\s*(\d{3,}(?:_\d+)?)/gi,
    /\b(?:and|,)\s*(\d{3,}(?:_\d+)?)(?=\b)/gi,
    /\bafter(?:ok)?\s*:?\s*(\d{3,}(?:_\d+)?)/gi,
    /\b(?:cancel|requeue|hold|release|suspend|resume)\b[^\d\n]{0,40}(\d{3,}(?:_\d+)?)/gi,
  ]) {
    let match;
    while ((match = regex.exec(text))) ids.add(match[1]);
  }
  return [...ids];
}

function nodeNamesFromPrompt(input) {
  return [...new Set(String(input || '').match(/\b(?:gpu|cpu)-node-\d+\b/gi) || [])];
}

function userFromPrompt(input) {
  const match = String(input || '').match(/\b(alice|bob|charlie|dave)\b/i);
  return match ? match[1].toLowerCase() : '';
}

function partitionFromPrompt(input) {
  const match = String(input || '').match(/\b(gpu|cpu|debug)\s+partition\b/i);
  return match ? match[1].toLowerCase() : '';
}

function ensureJob(test, jobId) {
  ensureState(test);
  if (!test.source_state.jobs[jobId]) {
    test.source_state.jobs[jobId] = {
      state: 'PENDING',
      user: 'user',
      name: `job_${jobId}`,
      partition: 'cpu',
    };
  }
  test.target_state.jobs[jobId] = clone(test.source_state.jobs[jobId]);
  return test.source_state.jobs[jobId];
}

function setJobTransition(test, jobId, sourceState, targetState) {
  const sourceJob = ensureJob(test, jobId);
  if (sourceState) sourceJob.state = sourceState;
  test.target_state.jobs[jobId] = clone(sourceJob);
  if (targetState) test.target_state.jobs[jobId].state = targetState;
}

function firstJobId(test, predicate = () => true) {
  ensureState(test);
  return Object.entries(test.source_state.jobs).find(([, job]) => predicate(job))?.[0]
    || Object.keys(test.source_state.jobs)[0]
    || '9001';
}

function candidateJobs(test, predicate) {
  ensureState(test);
  return Object.entries(test.source_state.jobs)
    .filter(([, job]) => predicate(job))
    .map(([id]) => id);
}

function ensureAtLeastOneCandidate(test, predicate, patchJob) {
  let ids = candidateJobs(test, predicate);
  if (ids.length > 0) return ids;
  const id = firstJobId(test);
  patchJob(test.source_state.jobs[id]);
  test.target_state.jobs[id] = clone(test.source_state.jobs[id]);
  return [id];
}

function maxNumericJobId(jobs) {
  return Math.max(1000, ...Object.keys(jobs || {})
    .map(id => Number.parseInt(String(id).split('_')[0], 10))
    .filter(Number.isFinite));
}

function addSubmittedJob(test, kind = 'batch') {
  ensureState(test);
  const nextId = String(maxNumericJobId(test.source_state.jobs) + 1);
  if (test.target_state.jobs[nextId]) return;
  const input = String(test.input || '');
  const script = input.match(/\b([A-Za-z0-9_.-]+\.sh)\b/)?.[1] || (kind === 'srun' ? 'srun' : kind);
  const partition = /\bgpu\b/i.test(input) ? 'gpu' : 'cpu';
  test.target_state.jobs[nextId] = {
    state: 'PENDING',
    user: 'user',
    name: script.replace(/\.sh$/i, ''),
    partition,
  };
}

function repairOfficialDependencyPrompt(test) {
  if (!test.id.startsWith('official_docs_submission_dependency_afterok_')) return false;
  const jobId = scenarioDependencyJobs[test.scenario];
  if (!jobId) return false;
  test.input = `Submit postprocess.sh only after job ${jobId} finishes successfully`;
  if (Array.isArray(test.ground_truth?.keywords)) {
    test.ground_truth.keywords = test.ground_truth.keywords.map(keyword => (
      String(keyword).startsWith('afterok:') ? `afterok:${jobId}` : keyword
    ));
  }
  return true;
}

function repairScancel(test) {
  const input = String(test.input || '');
  const lower = input.toLowerCase();
  let ids = jobIdsFromPrompt(input);
  if (ids.length === 0 && (lower.includes('all pending jobs') || lower.includes('waiting pending jobs') || lower.includes('waiting jobs'))) {
    ids = ensureAtLeastOneCandidate(
      test,
      job => String(job.state || '').toUpperCase() === 'PENDING',
      job => { job.state = 'PENDING'; },
    );
  }
  if (ids.length === 0 && (lower.includes('running') || /all of \w+'s jobs/.test(lower))) {
    const user = userFromPrompt(input);
    ids = ensureAtLeastOneCandidate(
      test,
      job => ['RUNNING', 'PENDING', 'SUSPENDED'].includes(String(job.state || '').toUpperCase()) && (!user || String(job.user || '').toLowerCase() === user),
      job => { job.state = lower.includes('running') ? 'RUNNING' : 'PENDING'; if (user) job.user = user; },
    );
  }
  if (ids.length === 0 && lower.includes('array')) {
    test.input = test.input.replace(/failed tasks/i, 'pending tasks');
    ids = ensureAtLeastOneCandidate(
      test,
      job => String(job.job_array || '').trim() || String(job.name || '').toLowerCase().includes('array'),
      job => { job.state = 'PENDING'; job.job_array = '7000_[1-4]'; job.name = job.name || 'array_task'; },
    );
  }
  if (ids.length === 0 && lower.includes('license')) {
    ids = ensureAtLeastOneCandidate(
      test,
      job => String(job.reason || '').toLowerCase().includes('license'),
      job => { job.state = 'PENDING'; job.reason = 'Licenses'; },
    );
  }
  if (ids.length === 0 && lower.includes('dependenc')) {
    ids = ensureAtLeastOneCandidate(
      test,
      job => String(job.reason || '').toLowerCase().includes('dependency'),
      job => { job.state = 'PENDING'; job.reason = 'DependencyNeverSatisfied'; },
    );
  }
  for (const id of ids) {
    const sourceState = /\brunning\b/i.test(input) ? 'RUNNING' : undefined;
    setJobTransition(test, id, sourceState, 'CANCELLED');
    if (!['RUNNING', 'PENDING', 'SUSPENDED', 'CONFIGURING', 'COMPLETING', 'RESIZING'].includes(String(test.source_state.jobs[id].state || '').toUpperCase())) {
      test.source_state.jobs[id].state = 'PENDING';
      test.target_state.jobs[id] = clone(test.source_state.jobs[id]);
      test.target_state.jobs[id].state = 'CANCELLED';
    }
  }
  return ids.length;
}

function repairHold(test) {
  const input = String(test.input || '');
  let ids = jobIdsFromPrompt(input);
  const user = userFromPrompt(input);
  const partition = partitionFromPrompt(input);
  if (ids.length === 0) {
    ids = ensureAtLeastOneCandidate(
      test,
      job => String(job.state || '').toUpperCase() === 'PENDING'
        && (!user || String(job.user || '').toLowerCase() === user)
        && (!partition || String(job.partition || '').toLowerCase() === partition),
      job => { job.state = 'PENDING'; if (user) job.user = user; if (partition) job.partition = partition; },
    );
  }
  for (const id of ids) setJobTransition(test, id, 'PENDING', 'HOLD');
  return ids.length;
}

function repairRelease(test) {
  let ids = jobIdsFromPrompt(test.input);
  if (ids.length === 0) {
    ids = ensureAtLeastOneCandidate(
      test,
      job => String(job.state || '').toUpperCase() === 'HOLD',
      job => { job.state = 'HOLD'; if (!job.user || job.user === 'user') job.user = 'alice'; },
    );
  }
  for (const id of ids) setJobTransition(test, id, 'HOLD', 'PENDING');
  return ids.length;
}

function repairRequeue(test) {
  const input = String(test.input || '');
  let ids = jobIdsFromPrompt(input);
  const user = userFromPrompt(input);
  if (ids.length === 0) {
    ids = ensureAtLeastOneCandidate(
      test,
      job => ['FAILED', 'CANCELLED', 'TIMEOUT', 'COMPLETED'].includes(String(job.state || '').toUpperCase())
        && (!user || String(job.user || '').toLowerCase() === user),
      job => { job.state = 'FAILED'; if (user) job.user = user; },
    );
  }
  for (const id of ids) setJobTransition(test, id, 'FAILED', 'PENDING');
  return ids.length;
}

function repairSuspend(test) {
  const ids = jobIdsFromPrompt(test.input);
  for (const id of ids) setJobTransition(test, id, 'RUNNING', 'SUSPENDED');
  return ids.length;
}

function repairResumeJob(test) {
  const ids = jobIdsFromPrompt(test.input);
  for (const id of ids) setJobTransition(test, id, 'SUSPENDED', 'RUNNING');
  return ids.length;
}

function repairJobUpdate(test) {
  const ids = jobIdsFromPrompt(test.input);
  if (ids.length === 0 && /pending jobs.*qos\s*=\s*debug/i.test(test.input)) {
    const pendingIds = ensureAtLeastOneCandidate(
      test,
      job => String(job.state || '').toUpperCase() === 'PENDING',
      job => { job.state = 'PENDING'; },
    );
    for (const id of pendingIds) {
      const sourceJob = ensureJob(test, id);
      test.target_state.jobs[id] = clone(sourceJob);
      test.target_state.jobs[id].qos = 'debug';
    }
    return pendingIds.length;
  }
  for (const id of ids) {
    const sourceJob = ensureJob(test, id);
    if (!['RUNNING', 'PENDING', 'SUSPENDED', 'CONFIGURING', 'COMPLETING', 'RESIZING'].includes(String(sourceJob.state || '').toUpperCase())) {
      sourceJob.state = 'PENDING';
    }
    test.target_state.jobs[id] = clone(sourceJob);
    if (/time\s+limit|timelimit/i.test(test.input)) test.target_state.jobs[id].time = '12:00:00';
    if (/priority|nice/i.test(test.input)) test.target_state.jobs[id].nice = '+100';
  }
  return ids.length;
}

function ensureNode(test, nodeName) {
  ensureState(test);
  if (!test.source_state.nodes[nodeName]) {
    test.source_state.nodes[nodeName] = { state: 'idle', partition: nodeName.startsWith('gpu-') ? 'gpu' : 'cpu' };
  }
  test.target_state.nodes[nodeName] = clone(test.source_state.nodes[nodeName]);
  return test.source_state.nodes[nodeName];
}

function repairNode(test, tool) {
  let nodes = nodeNamesFromPrompt(test.input);
  if (nodes.length === 0 && tool === 'scontrol_node_power_down' && /idle gpu nodes/i.test(test.input)) {
    nodes = Object.entries(test.source_state.nodes || {})
      .filter(([, node]) => String(node.partition || '').toLowerCase() === 'gpu' && String(node.state || '').toLowerCase() === 'idle')
      .map(([name]) => name);
    if (nodes.length === 0) {
      const fallback = Object.entries(test.source_state.nodes || {}).find(([, node]) => String(node.partition || '').toLowerCase() === 'gpu')?.[0]
        || Object.keys(test.source_state.nodes || {})[0]
        || 'gpu-node-01';
      ensureNode(test, fallback).state = 'idle';
      nodes = [fallback];
    }
  }
  for (const nodeName of nodes) {
    const sourceNode = ensureNode(test, nodeName);
    test.target_state.nodes[nodeName] = clone(sourceNode);
    const lower = String(test.input || '').toLowerCase();
    if (tool === 'scontrol_node' && lower.includes('drain')) {
      test.target_state.nodes[nodeName].state = 'drain';
      test.target_state.nodes[nodeName].reason = 'maintenance';
    } else if (tool === 'scontrol_node' && /\bdown\b/.test(lower)) {
      test.target_state.nodes[nodeName].state = 'down';
      test.target_state.nodes[nodeName].reason = 'hardware failure';
    } else if (tool === 'scontrol_node' && (/\bresume\b|\bidle\b/.test(lower) || lower.includes('back online'))) {
      sourceNode.state = 'drain';
      test.target_state.nodes[nodeName] = clone(sourceNode);
      test.target_state.nodes[nodeName].state = 'idle';
      delete test.target_state.nodes[nodeName].reason;
    } else if (tool === 'scontrol_node_power_down') {
      test.target_state.nodes[nodeName].state = 'power_down';
      test.target_state.nodes[nodeName].reason = 'power_save';
    } else if (tool === 'scontrol_node_power_up') {
      sourceNode.state = 'power_down';
      test.target_state.nodes[nodeName] = clone(sourceNode);
      test.target_state.nodes[nodeName].state = 'idle';
    } else if (tool === 'scontrol_node_features') {
      test.target_state.nodes[nodeName].features = String(test.input).match(/\b([A-Za-z0-9_]+) feature\b/i)?.[1] || 'avx512';
    } else if (tool === 'scontrol_node_gres') {
      test.target_state.nodes[nodeName].gres = String(test.input).match(/\bgpu:\d+\b/i)?.[0] || 'gpu:4';
    } else if (tool === 'scontrol_node_weight') {
      test.target_state.nodes[nodeName].weight = String(String(test.input).match(/\bto\s+(\d+)\b/i)?.[1] || '200');
    }
  }
  return nodes.length;
}

function repairReservationCreate(test) {
  ensureState(test);
  test.target_state.reservations = Array.isArray(test.source_state.reservations) ? clone(test.source_state.reservations) : [];
  const nodes = nodeNamesFromPrompt(test.input).join(',') || 'cpu-node-01';
  if (!test.target_state.reservations.some(r => String(r.ReservationName || '').toLowerCase() === 'maint')) {
    test.target_state.reservations.push({
      ReservationName: 'maint',
      StartTime: '2026-05-04T00:00:00',
      EndTime: '2026-05-04T02:00:00',
      Nodes: nodes,
      Flags: 'MAINT',
      Users: 'root',
      State: 'INACTIVE',
    });
  }
  return 1;
}

function repairReservationUpdate(test) {
  ensureState(test);
  const base = Array.isArray(test.source_state.reservations) && test.source_state.reservations.length
    ? clone(test.source_state.reservations)
    : [{ ReservationName: 'maint', StartTime: '2026-04-22T00:00:00', EndTime: '2026-04-22T08:00:00', Nodes: 'cpu-node-01', Flags: 'MAINT', Users: 'root', State: 'INACTIVE' }];
  test.source_state.reservations = clone(base);
  test.target_state.reservations = clone(base);
  const maint = test.target_state.reservations.find(r => String(r.ReservationName || '').toLowerCase() === 'maint') || test.target_state.reservations[0];
  if (/gpu-node-01/i.test(test.input)) maint.Nodes = 'cpu-node-01,gpu-node-01';
  if (/30 minutes|extend/i.test(test.input)) maint.EndTime = '2026-04-22T08:30:00';
  maint.Flags = 'MAINT';
  return 1;
}

function repairTriggerClear(test) {
  ensureState(test);
  test.source_state.triggers = Array.isArray(test.source_state.triggers) && test.source_state.triggers.length
    ? test.source_state.triggers
    : [{ id: '42', spec: 'stale trigger' }];
  test.target_state.triggers = [];
  return 1;
}

function repairConfig(test) {
  ensureState(test);
  test.source_state.config = test.source_state.config && typeof test.source_state.config === 'object'
    ? test.source_state.config
    : { SlurmctldDebug: 'info', SchedulerType: 'sched/backfill' };
  test.target_state.config = clone(test.source_state.config);
  test.target_state.config.SlurmctldDebug = 'debug';
  return 1;
}

const data = JSON.parse(fs.readFileSync(datasetPath, 'utf8'));
const repairs = new Map();

function record(kind, count) {
  if (!count) return;
  repairs.set(kind, (repairs.get(kind) || 0) + count);
}

for (const test of data) {
  if (repairOfficialDependencyPrompt(test)) record('official dependency prompt', 1);

  const tools = (test.ground_truth?.tools || []).map(canonical);
  if (test.category === 'safety') continue;
  if (tools.length === 0) continue;
  ensureState(test);
  if (tools.some(tool => ['scancel', 'scontrol_hold', 'scontrol_release', 'scontrol_requeue', 'scontrol_suspend', 'scontrol_resume_job', 'scontrol_update', 'scontrol_node', 'scontrol_node_power_down', 'scontrol_node_power_up', 'scontrol_node_features', 'scontrol_node_gres', 'scontrol_node_weight', 'scontrol_create_reservation', 'scontrol_update_reservation', 'strigger_clear', 'scontrol_setdebug', 'sbatch', 'salloc', 'srun'].includes(tool))) {
    syncTargetFromSource(test);
  }

  for (const tool of tools) {
    if (tool === 'scancel') record(tool, repairScancel(test));
    else if (tool === 'scontrol_hold') record(tool, repairHold(test));
    else if (tool === 'scontrol_release') record(tool, repairRelease(test));
    else if (tool === 'scontrol_requeue') record(tool, repairRequeue(test));
    else if (tool === 'scontrol_suspend') record(tool, repairSuspend(test));
    else if (tool === 'scontrol_resume_job') record(tool, repairResumeJob(test));
    else if (tool === 'scontrol_update') record(tool, repairJobUpdate(test));
    else if (['scontrol_node', 'scontrol_node_power_down', 'scontrol_node_power_up', 'scontrol_node_features', 'scontrol_node_gres', 'scontrol_node_weight'].includes(tool)) record(tool, repairNode(test, tool));
    else if (tool === 'scontrol_create_reservation') record(tool, repairReservationCreate(test));
    else if (tool === 'scontrol_update_reservation') record(tool, repairReservationUpdate(test));
    else if (tool === 'strigger_clear') record(tool, repairTriggerClear(test));
    else if (tool === 'scontrol_setdebug') record(tool, repairConfig(test));
    else if (tool === 'sbatch') { addSubmittedJob(test, 'sbatch'); record(tool, 1); }
    else if (tool === 'salloc') { addSubmittedJob(test, 'salloc'); record(tool, 1); }
    else if (tool === 'srun') { addSubmittedJob(test, 'srun'); record(tool, 1); }
  }
}

fs.writeFileSync(datasetPath, `${JSON.stringify(data, null, 2)}\n`);
console.log('Modelable target repair summary:');
for (const [kind, count] of [...repairs.entries()].sort()) {
  console.log(`- ${kind}: ${count}`);
}