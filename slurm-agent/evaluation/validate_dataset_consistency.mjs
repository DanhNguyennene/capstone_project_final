#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const datasetPath = path.join(__dirname, 'dataset.json');
const mcpPath = path.join(__dirname, '..', 'mcp-server', 'slurm_mcp_sse.py');

const EXPECTED_CATEGORIES = new Set([
  'account', 'action', 'bulk', 'diagnose', 'docs', 'domain', 'edge',
  'multi_step', 'read', 'safety', 'submission',
]);

const READ_ONLY_CATEGORIES = new Set(['diagnose', 'docs', 'domain', 'read']);
const EXPECTED_SCENARIOS = new Set(['healthy', 'failed', 'pending', 'mixed', 'debug_needed']);
const ACTIVE_STATES = new Set(['RUNNING', 'PENDING', 'SUSPENDED', 'CONFIGURING', 'COMPLETING', 'RESIZING']);
const TERMINAL_STATES = new Set(['COMPLETED', 'FAILED', 'CANCELLED', 'TIMEOUT']);

const GT_ALIASES = new Map([
  ['sacctmgr_list', 'sacctmgr_show'],
  ['sacctmgr', 'sacctmgr_show'],
  ['scontrol', 'scontrol_show'],
]);

const DESTRUCTIVE_TOOLS = new Set([
  'scancel', 'sbatch', 'scontrol_hold', 'scontrol_release',
  'scontrol_requeue', 'scontrol_update', 'scontrol_reconfigure',
  'scontrol_suspend', 'scontrol_resume_job', 'scontrol_node',
  'srun', 'salloc', 'sattach', 'sbcast',
  'strigger_set', 'strigger_clear',
  'scontrol_node_power_down', 'scontrol_node_power_up', 'scontrol_node_features',
  'scontrol_node_gres', 'scontrol_node_weight', 'scontrol_create_reservation',
  'scontrol_delete_reservation', 'scontrol_update_reservation',
  'scontrol_write_config', 'scontrol_setdebug', 'scontrol_token', 'scontrol_shutdown',
  'sacctmgr_add', 'sacctmgr_modify', 'sacctmgr_delete', 'sacctmgr_recalc',
  'sacctmgr_archive', 'sacctmgr_load', 'sacctmgr_dump',
]);

const TOOL_STATE_POLICY = {
  scancel: { source: ACTIVE_STATES, target: new Set(['CANCELLED']) },
  scontrol_hold: { source: new Set(['PENDING']), target: new Set(['HOLD']) },
  scontrol_release: { source: new Set(['HOLD', 'PENDING']), target: new Set(['PENDING']) },
  scontrol_suspend: { source: new Set(['RUNNING']), target: new Set(['SUSPENDED']) },
  scontrol_resume_job: { source: new Set(['SUSPENDED']), target: new Set(['RUNNING']) },
  scontrol_requeue: { source: new Set(['FAILED', 'CANCELLED', 'TIMEOUT', 'COMPLETED', 'RUNNING', 'PENDING']), target: new Set(['PENDING']) },
};

const REPRESENTED_SIDE_EFFECT_TOOLS = new Set([
  'scancel', 'scontrol_hold', 'scontrol_release', 'scontrol_requeue',
  'scontrol_update', 'scontrol_suspend', 'scontrol_resume_job', 'scontrol_node',
  'scontrol_node_power_down', 'scontrol_node_power_up', 'scontrol_node_features',
  'scontrol_node_gres', 'scontrol_node_weight', 'scontrol_create_reservation',
  'scontrol_update_reservation', 'strigger_clear', 'scontrol_setdebug',
]);

function canonicalTool(tool) {
  const name = String(tool || '').trim();
  return GT_ALIASES.get(name) || name;
}

function isObject(value) {
  return value && typeof value === 'object' && !Array.isArray(value);
}

function stable(value) {
  if (Array.isArray(value)) return value.map(stable);
  if (!isObject(value)) return value;
  return Object.fromEntries(Object.keys(value).sort().map(key => [key, stable(value[key])]));
}

function deepEqual(left, right) {
  return JSON.stringify(stable(left)) === JSON.stringify(stable(right));
}

function stateOf(job) {
  return String(job?.state || '').trim().toUpperCase();
}

function parseMcpTools() {
  const known = new Set();
  if (fs.existsSync(mcpPath)) {
    const text = fs.readFileSync(mcpPath, 'utf8');
    const regex = /@mcp\.tool\(\)\s*(?:\n|\r\n)def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(/g;
    let match;
    while ((match = regex.exec(text))) known.add(match[1]);
  }
  for (const extra of [
    'lookup_slurm_docs', 'run_analysis', 'transfer_to_operator', 'transfer_to_observer',
    'web_search', 'fetch_web_content', 'sacctmgr_show',
  ]) known.add(extra);
  return known;
}

function changedKeys(src = {}, tgt = {}) {
  const keys = new Set([...Object.keys(src), ...Object.keys(tgt)]);
  return [...keys].filter(key => !deepEqual(src[key], tgt[key]));
}

function extractPromptJobIds(input) {
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

function isIntentionalNoopOrGuidance(test, input) {
  const text = String(input || '').trim().toLowerCase();
  if (['edge', 'docs', 'domain'].includes(test.category)) return true;
  if (/^(cancel|resume|hold|release|suspend|requeue)\s+it\.?$/.test(text)) return true;
  if (/^node is ready\W+resume it\.?$/.test(text)) return true;
  if (/\b(if|only if|unless|when|check|verify|find|show|explain|how|what|why|guide|should)\b/.test(text)
      && !(test.ground_truth?.tools || []).some(tool => DESTRUCTIVE_TOOLS.has(canonicalTool(tool)))) {
    return true;
  }
  return false;
}

function issue(list, severity, test, message, extra = {}) {
  list.push({ severity, id: test?.id || '(unknown)', category: test?.category || '', scenario: test?.scenario || '', message, ...extra });
}

function main() {
  const args = new Set(process.argv.slice(2));
  const asJson = args.has('--json');
  const data = JSON.parse(fs.readFileSync(datasetPath, 'utf8'));
  const knownTools = parseMcpTools();
  const findings = [];
  const ids = new Map();
  const categoryCounts = new Map();
  const scenarioCounts = new Map();
  const variantRefs = [];

  if (!Array.isArray(data)) {
    console.error('dataset.json must contain a JSON array');
    process.exit(2);
  }

  data.forEach((test, index) => {
    if (!isObject(test)) {
      issue(findings, 'error', { id: `index_${index}` }, 'row is not an object');
      return;
    }

    const required = ['id', 'category', 'scenario', 'input', 'source_state', 'target_state', 'ground_truth'];
    for (const key of required) {
      if (!(key in test)) issue(findings, 'error', test, `missing required field: ${key}`);
    }

    if (typeof test.id !== 'string' || !test.id.trim()) issue(findings, 'error', test, 'id must be a non-empty string');
    if (ids.has(test.id)) issue(findings, 'error', test, `duplicate id also seen at index ${ids.get(test.id)}`, { index });
    ids.set(test.id, index);

    if (!EXPECTED_CATEGORIES.has(test.category)) issue(findings, 'error', test, `unknown category: ${test.category}`);
    if (!EXPECTED_SCENARIOS.has(test.scenario)) issue(findings, 'error', test, `unknown scenario: ${test.scenario}`);
    categoryCounts.set(test.category, (categoryCounts.get(test.category) || 0) + 1);
    scenarioCounts.set(test.scenario, (scenarioCounts.get(test.scenario) || 0) + 1);

    if (test.variant_of) variantRefs.push([test.id, test.variant_of]);

    const gt = isObject(test.ground_truth) ? test.ground_truth : {};
    const tools = Array.isArray(gt.tools) ? gt.tools.map(canonicalTool) : [];
    const toolSet = new Set(tools);
    const destructive = tools.filter(tool => DESTRUCTIVE_TOOLS.has(tool));
    const destructiveSet = new Set(destructive);

    if (!Array.isArray(gt.tools)) issue(findings, 'error', test, 'ground_truth.tools must be an array');
    if (typeof gt.handoff !== 'boolean') issue(findings, 'error', test, 'ground_truth.handoff must be boolean');
    if (typeof gt.hitl !== 'boolean') issue(findings, 'error', test, 'ground_truth.hitl must be boolean');
    if (!Array.isArray(gt.keywords)) issue(findings, 'error', test, 'ground_truth.keywords must be an array');

    for (const tool of tools) {
      if (!knownTools.has(tool)) issue(findings, 'error', test, `unknown ground-truth tool: ${tool}`);
    }
    if (gt.hitl === true && gt.handoff !== true) issue(findings, 'error', test, 'HITL is true but handoff is false');
    if (destructive.length > 0 && (gt.handoff !== true || gt.hitl !== true)) {
      issue(findings, 'error', test, `destructive tools require handoff and HITL: ${destructive.join(', ')}`);
    }

    const source = isObject(test.source_state) ? test.source_state : {};
    const target = isObject(test.target_state) ? test.target_state : {};
    if (!isObject(test.source_state)) issue(findings, 'error', test, 'source_state must be an object');
    if (!isObject(test.target_state)) issue(findings, 'error', test, 'target_state must be an object');

    const sourceJobs = isObject(source.jobs) ? source.jobs : {};
    const targetJobs = isObject(target.jobs) ? target.jobs : {};
    const sourceNodes = isObject(source.nodes) ? source.nodes : {};
    const targetNodes = isObject(target.nodes) ? target.nodes : {};
    const anyStateChange = !deepEqual(source, target);
    const changedTopLevel = changedKeys(source, target);

    const commonJobs = Object.keys(sourceJobs).filter(id => Object.prototype.hasOwnProperty.call(targetJobs, id));
    const changedJobStates = commonJobs.filter(id => stateOf(sourceJobs[id]) !== stateOf(targetJobs[id]));
    const changedJobRecords = changedKeys(sourceJobs, targetJobs);
    const addedJobs = Object.keys(targetJobs).filter(id => !Object.prototype.hasOwnProperty.call(sourceJobs, id));
    const removedJobs = Object.keys(sourceJobs).filter(id => !Object.prototype.hasOwnProperty.call(targetJobs, id));
    const changedNodeRecords = changedKeys(sourceNodes, targetNodes);

    if (READ_ONLY_CATEGORIES.has(test.category) && anyStateChange) {
      issue(findings, 'error', test, `read-only category has target_state mutation: ${changedTopLevel.join(', ')}`);
    }
    if (READ_ONLY_CATEGORIES.has(test.category) && destructive.length > 0) {
      issue(findings, 'error', test, `read-only category expects destructive tool(s): ${destructive.join(', ')}`);
    }
    if (anyStateChange && destructive.length === 0) {
      issue(findings, 'error', test, `target_state changes but no destructive ground-truth tool is expected: ${changedTopLevel.join(', ')}`);
    }
    const representedDestructive = destructive.filter(tool => REPRESENTED_SIDE_EFFECT_TOOLS.has(tool));
    if (!anyStateChange && representedDestructive.length > 0 && test.category !== 'safety') {
      issue(findings, 'warn', test, `destructive tool expected but target_state has no represented change: ${representedDestructive.join(', ')}`);
    }

    if (addedJobs.length > 0 && !(toolSet.has('sbatch') || toolSet.has('srun') || toolSet.has('salloc'))) {
      issue(findings, 'error', test, `target_state adds jobs without a submission/allocation tool: ${addedJobs.join(', ')}`);
    }
    if (removedJobs.length > 0) {
      issue(findings, 'warn', test, `target_state removes jobs; prefer terminal state updates over deletion: ${removedJobs.join(', ')}`);
    }
    if (changedNodeRecords.length > 0 && !(toolSet.has('scontrol_node') || toolSet.has('scontrol_update') || [...toolSet].some(t => t.startsWith('scontrol_node_')))) {
      issue(findings, 'error', test, `target_state changes nodes without node-control tool: ${changedNodeRecords.join(', ')}`);
    }

    for (const tool of destructiveSet) {
      const policy = TOOL_STATE_POLICY[tool];
      if (!policy) continue;
      for (const jobId of changedJobStates) {
        const srcState = stateOf(sourceJobs[jobId]);
        const tgtState = stateOf(targetJobs[jobId]);
        if (tool === 'scancel' && targetJobs[jobId] && tgtState !== 'CANCELLED') continue;
        if (!policy.source.has(srcState)) {
          issue(findings, 'error', test, `${tool} source state for job ${jobId} is not admissible: ${srcState}`);
        }
        if (!policy.target.has(tgtState)) {
          issue(findings, 'error', test, `${tool} target state for job ${jobId} is not expected: ${tgtState}`);
        }
      }
    }

    for (const jobId of changedJobStates) {
      const srcState = stateOf(sourceJobs[jobId]);
      const tgtState = stateOf(targetJobs[jobId]);
      if (TERMINAL_STATES.has(srcState) && !toolSet.has('scontrol_requeue')) {
        issue(findings, 'error', test, `terminal source job ${jobId} changes state ${srcState} -> ${tgtState} without requeue`);
      }
    }

    const promptIds = extractPromptJobIds(test.input);
    if (promptIds.length > 0 && destructive.length > 0) {
      for (const promptId of promptIds) {
        if (!sourceJobs[promptId] && !targetJobs[promptId]) {
          issue(findings, 'warn', test, `prompt mentions job ${promptId}, but it is absent from source_state/target_state`);
        }
      }
    }

    const input = String(test.input || '').toLowerCase();
    const suppressPhraseWarning = isIntentionalNoopOrGuidance(test, input);
    if (/\bcancel(?:\s+job|\b)/.test(input) && !toolSet.has('scancel') && test.category !== 'safety' && !suppressPhraseWarning) {
      issue(findings, 'warn', test, 'prompt says cancel but ground truth does not include scancel');
    }
    if (/\bsubmit\b|\bsbatch\b/.test(input) && !toolSet.has('sbatch') && !toolSet.has('srun') && !toolSet.has('salloc') && !suppressPhraseWarning) {
      issue(findings, 'warn', test, 'prompt says submit/allocation but ground truth has no submission/allocation tool');
    }
    if (/\bsuspend\b/.test(input) && !toolSet.has('scontrol_suspend') && !suppressPhraseWarning) {
      issue(findings, 'warn', test, 'prompt says suspend but ground truth does not include scontrol_suspend');
    }
    if (/\bresume\b/.test(input) && !toolSet.has('scontrol_resume_job') && !toolSet.has('scontrol_node') && !toolSet.has('scontrol_update') && !suppressPhraseWarning) {
      issue(findings, 'warn', test, 'prompt says resume but ground truth has no resume/update tool');
    }
  });

  for (const [id, ref] of variantRefs) {
    if (!ids.has(ref)) issue(findings, 'error', { id }, `variant_of references missing test id: ${ref}`);
  }

  const errors = findings.filter(f => f.severity === 'error');
  const warnings = findings.filter(f => f.severity === 'warn');
  const summary = {
    total: data.length,
    unique_ids: ids.size,
    errors: errors.length,
    warnings: warnings.length,
    category_counts: Object.fromEntries([...categoryCounts.entries()].sort()),
    scenario_counts: Object.fromEntries([...scenarioCounts.entries()].sort()),
  };

  if (asJson) {
    console.log(JSON.stringify({ summary, findings }, null, 2));
    process.exitCode = errors.length ? 1 : 0;
    return;
  }

  console.log('Dataset Consistency Audit');
  console.log('=========================');
  console.log(JSON.stringify(summary, null, 2));
  console.log('');
  if (findings.length) {
    console.log('Findings (first 200):');
    for (const f of findings.slice(0, 200)) {
      console.log(`- [${f.severity}] ${f.id} (${f.category}/${f.scenario}): ${f.message}`);
    }
    if (findings.length > 200) console.log(`... ${findings.length - 200} more findings omitted; rerun with --json for full output.`);
  } else {
    console.log('No consistency findings.');
  }

  process.exitCode = errors.length ? 1 : 0;
}

main();