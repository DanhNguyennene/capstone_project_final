#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, '..');

const args = new Map();
for (let index = 2; index < process.argv.length; index += 1) {
  const token = process.argv[index];
  if (token.startsWith('--')) {
    const next = process.argv[index + 1];
    if (next && !next.startsWith('--')) {
      args.set(token, next);
      index += 1;
    } else {
      args.set(token, 'true');
    }
  }
}

const datasetPath = path.resolve(root, args.get('--dataset') || 'evaluation/dataset.json');
const outputPath = path.resolve(root, args.get('--out') || 'training/out/specialist_sft.jsonl');
const maxRows = Number.parseInt(args.get('--limit') || '0', 10);

const TOOL_ALIASES = new Map([
  ['sacctmgr_list', 'sacctmgr_show'],
  ['sacctmgr', 'sacctmgr_show'],
  ['scontrol', 'scontrol_show'],
]);

function stable(value) {
  if (Array.isArray(value)) return value.map(stable);
  if (!value || typeof value !== 'object') return value;
  return Object.fromEntries(Object.keys(value).sort().map(key => [key, stable(value[key])]));
}

function compactState(state = {}) {
  const jobs = Object.entries(state.jobs || {}).map(([id, job]) => ({
    id,
    state: job.state,
    user: job.user,
    name: job.name,
    partition: job.partition,
  }));
  const nodes = Object.entries(state.nodes || {}).map(([name, node]) => ({
    name,
    state: node.state,
    partition: node.partition,
  }));
  return stable({ jobs, nodes });
}

function changedState(source = {}, target = {}) {
  const changedJobs = [];
  const sourceJobs = source.jobs || {};
  const targetJobs = target.jobs || {};
  const ids = new Set([...Object.keys(sourceJobs), ...Object.keys(targetJobs)]);
  for (const id of [...ids].sort()) {
    const before = sourceJobs[id] || null;
    const after = targetJobs[id] || null;
    if (JSON.stringify(stable(before)) !== JSON.stringify(stable(after))) {
      changedJobs.push({ id, before, after });
    }
  }

  const changedNodes = [];
  const sourceNodes = source.nodes || {};
  const targetNodes = target.nodes || {};
  const names = new Set([...Object.keys(sourceNodes), ...Object.keys(targetNodes)]);
  for (const name of [...names].sort()) {
    const before = sourceNodes[name] || null;
    const after = targetNodes[name] || null;
    if (JSON.stringify(stable(before)) !== JSON.stringify(stable(after))) {
      changedNodes.push({ name, before, after });
    }
  }

  return stable({ jobs: changedJobs, nodes: changedNodes });
}

function routeName(handoff) {
  return handoff ? 'operator' : 'observer';
}

function buildUserMessage(row) {
  return JSON.stringify(stable({
    task: 'Plan the Slurm-specialist behavior for this user request.',
    id: row.id,
    category: row.category,
    scenario: row.scenario,
    user_request: row.input,
    source_state: compactState(row.source_state),
  }), null, 2);
}

function buildAssistantMessage(row) {
  const gt = row.ground_truth || {};
  const tools = Array.isArray(gt.tools) ? gt.tools.map(tool => TOOL_ALIASES.get(String(tool)) || String(tool)) : [];
  return JSON.stringify(stable({
    route: routeName(Boolean(gt.handoff)),
    tools,
    requires_handoff: Boolean(gt.handoff),
    requires_confirmation: Boolean(gt.hitl),
    response_keywords: Array.isArray(gt.keywords) ? gt.keywords : [],
    expected_state_change: changedState(row.source_state, row.target_state),
  }));
}

function main() {
  const dataset = JSON.parse(fs.readFileSync(datasetPath, 'utf8'));
  if (!Array.isArray(dataset)) throw new Error('dataset must be a JSON array');

  const rows = Number.isFinite(maxRows) && maxRows > 0 ? dataset.slice(0, maxRows) : dataset;
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });

  const system = [
    'You are the Slurm specialist planner inside a tool-grounded HPC assistant.',
    'Return JSON only.',
    'Choose the expected Slurm tools, Observer/Operator route, HITL confirmation requirement, response evidence keywords, and expected state change.',
    'Do not execute commands and do not invent unsupported tools.',
  ].join(' ');

  const lines = rows.map(row => JSON.stringify({
    messages: [
      { role: 'system', content: system },
      { role: 'user', content: buildUserMessage(row) },
      { role: 'assistant', content: buildAssistantMessage(row) },
    ],
    metadata: {
      id: row.id,
      category: row.category,
      scenario: row.scenario,
    },
  }));

  fs.writeFileSync(outputPath, `${lines.join('\n')}\n`);
  console.log(`wrote ${lines.length} specialist SFT samples -> ${path.relative(root, outputPath)}`);
}

main();