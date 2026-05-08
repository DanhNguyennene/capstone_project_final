#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const datasetPath = path.join(__dirname, 'dataset.json');

const READ_ONLY_TARGET_REPAIRS = new Map([
  ['acct_add_pending', ['accounts']],
  ['acct_modify_charlie_pending', ['accounts']],
  ['account_bal200_013', ['accounts']],
  ['account_bal200_015', ['accounts']],
  ['account_bal200_038', ['accounts']],
  ['account_bal200_040', ['accounts']],
  ['account_bal200_063', ['accounts']],
  ['account_bal200_065', ['accounts']],
  ['account_bal200_088', ['accounts']],
  ['account_bal200_090', ['accounts']],
  ['account_bal200_113', ['accounts']],
  ['account_bal200_115', ['accounts']],
  ['account_bal200_138', ['accounts']],
  ['account_bal200_140', ['accounts']],
  ['account_bal200_163', ['accounts']],
  ['account_bal200_165', ['accounts']],
  ['read_reservations_failed_v1', ['reservations']],
  ['read_reservations_failed_v2', ['reservations']],
  ['sreport_cluster_pending_v1', ['usage']],
  ['read_reservations_pending_v1', ['reservations']],
]);

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

const data = JSON.parse(fs.readFileSync(datasetPath, 'utf8'));
const repaired = [];

for (const test of data) {
  const keys = READ_ONLY_TARGET_REPAIRS.get(test.id);
  if (!keys) continue;
  test.target_state = test.target_state && typeof test.target_state === 'object' ? test.target_state : {};
  for (const key of keys) {
    if (test.source_state && Object.prototype.hasOwnProperty.call(test.source_state, key)) {
      test.target_state[key] = clone(test.source_state[key]);
      repaired.push(`${test.id}:${key}`);
    }
  }
}

fs.writeFileSync(datasetPath, `${JSON.stringify(data, null, 2)}\n`);
console.log(`Repaired ${repaired.length} read-only target field(s).`);
for (const item of repaired) console.log(`- ${item}`);