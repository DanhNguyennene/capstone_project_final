import json

with open('data/agent_sft_v2.jsonl') as f:
    rows = [json.loads(l) for l in f]

print(f'Total rows: {len(rows)}')
r = rows[0]
print('Keys:', sorted(r.keys()))
print()

# Check for tool output content
TARGET_TOOLS = {'sdiag','sprio','sshare','sreport','sacctmgr_list',
                'sacctmgr_show_problems','scontrol_reservation_show',
                'scontrol_show_config','strigger_get'}

# Look in messages for tool result content
messages = r.get('messages', [])
print(f'messages: {len(messages)} entries, first type: {messages[0].get("role") if messages else "N/A"}')

# Find rows that have tool outputs stored
tool_output_rows = 0
sample_tool_outputs = {}

for row in rows:
    msgs = row.get('messages', [])
    sc = row.get('scenario', '?')
    for m in msgs:
        if m.get('role') == 'tool':
            content = str(m.get('content', ''))
            # check if any scenario-aware tool output is embedded
            for marker in ['SlurmctldDebug', 'GrpCPUMins', 'State=INACTIVE', 'State=ACTIVE',
                           'Jobs submitted', 'EffectvUsage', 'CPUHours', 'MaxJobsPerUser']:
                if marker in content:
                    tool_output_rows += 1
                    key = (marker, sc)
                    if key not in sample_tool_outputs:
                        sample_tool_outputs[key] = content[:200]
                    break

print(f'\nRows with embedded tool outputs: {tool_output_rows}')
print()
for (marker, sc), sample in sorted(sample_tool_outputs.items()):
    print(f'[{sc}] marker={marker}')
    print(f'  {sample[:150].replace(chr(10)," ")}')
    print()
