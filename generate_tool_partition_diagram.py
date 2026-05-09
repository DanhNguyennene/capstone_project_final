"""Generate tool partitioning diagram for the report."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Actual tool lists from agent/flow/tool_discovery.py + agent.py
observer_tools = [
    # Analysis (MCP read-only)
    "squeue", "sacct", "sinfo", "scontrol_show",
    "sacctmgr_list", "sdiag", "sprio", "sstat",
    # Safe (other MCP reads)  
    "sreport", "scontrol_license", "scontrol_reservation_show",
    "sshare", "sinfo_reasons",
    # Function tools
    "lookup_slurm_docs", "transfer_to_operator",
]

operator_tools = [
    # Dangerous (HITL-gated)
    "scancel", "scontrol_hold", "scontrol_release",
    "scontrol_update", "sbatch", "scontrol_requeue",
    "sacctmgr_add", "sacctmgr_modify", "sacctmgr_delete",
    # Operator reads (guarded)
    "squeue", "sinfo", "scontrol_show", "sacctmgr_list",
    "scontrol_reservation_show",
]

monolithic_tools = list(set(observer_tools + operator_tools))

fig, axes = plt.subplots(1, 2, figsize=(14, 7))

# === LEFT: 2-Agent Architecture ===
ax = axes[0]
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('Observer/Operator (2-Agent)\n~8 tools per agent context', fontsize=12, fontweight='bold', pad=10)

# Observer box
obs_rect = mpatches.FancyBboxPatch((0.5, 6.5), 4, 5, boxstyle="round,pad=0.1",
                                     facecolor='#E3F2FD', edgecolor='#1565C0', linewidth=2)
ax.add_patch(obs_rect)
ax.text(2.5, 11.2, 'Observer', ha='center', fontsize=11, fontweight='bold', color='#1565C0')
ax.text(2.5, 10.7, '(Read-Only)', ha='center', fontsize=8, color='#1565C0')

obs_display = ["squeue", "sacct", "sinfo", "scontrol_show",
               "sacctmgr_list", "lookup_slurm_docs", 
               "sdiag", "transfer_to_operator"]
for i, tool in enumerate(obs_display):
    y = 10.1 - i * 0.45
    color = '#43A047' if tool != 'transfer_to_operator' else '#FF8F00'
    ax.text(2.5, y, f"  {tool}", ha='center', fontsize=7.5, fontfamily='monospace', color=color)

# Operator box
op_rect = mpatches.FancyBboxPatch((5.5, 6.5), 4, 5, boxstyle="round,pad=0.1",
                                    facecolor='#FFF3E0', edgecolor='#E65100', linewidth=2)
ax.add_patch(op_rect)
ax.text(7.5, 11.2, 'Operator', ha='center', fontsize=11, fontweight='bold', color='#E65100')
ax.text(7.5, 10.7, '(State-Changing + HITL)', ha='center', fontsize=8, color='#E65100')

op_display = ["scancel", "scontrol_hold", "scontrol_release",
              "scontrol_update", "sbatch", "sacctmgr_modify",
              "squeue (discovery)", "confirm_action"]
for i, tool in enumerate(op_display):
    y = 10.1 - i * 0.45
    color = '#D32F2F' if 'discovery' not in tool and 'confirm' not in tool else '#FF8F00'
    ax.text(7.5, y, f"  {tool}", ha='center', fontsize=7.5, fontfamily='monospace', color=color)

# Arrow between them
ax.annotate('', xy=(5.4, 9.0), xytext=(4.6, 9.0),
            arrowprops=dict(arrowstyle='->', lw=2, color='#FF8F00'))
ax.text(5.0, 9.3, 'handoff', ha='center', fontsize=7, color='#FF8F00', style='italic')

# Result box
res_rect = mpatches.FancyBboxPatch((2, 0.5), 6, 2.5, boxstyle="round,pad=0.1",
                                     facecolor='#E8F5E9', edgecolor='#2E7D32', linewidth=1.5)
ax.add_patch(res_rect)
ax.text(5, 2.5, 'Result: 87.0% pass rate', ha='center', fontsize=10, fontweight='bold', color='#2E7D32')
ax.text(5, 1.9, 'Tool Recall: 89.4%', ha='center', fontsize=9, color='#2E7D32')
ax.text(5, 1.3, '(on 378 routing-neutral cases)', ha='center', fontsize=8, color='gray')

# Arrow down
ax.annotate('', xy=(5, 3.2), xytext=(5, 6.3),
            arrowprops=dict(arrowstyle='->', lw=1.5, color='gray'))

# === RIGHT: Monolithic Architecture ===
ax2 = axes[1]
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 12)
ax2.set_aspect('equal')
ax2.axis('off')
ax2.set_title('Monolithic (Single Agent)\nAll 18 tools in one context', fontsize=12, fontweight='bold', pad=10)

# Single big box
mono_rect = mpatches.FancyBboxPatch((1.5, 5), 7, 6.5, boxstyle="round,pad=0.1",
                                      facecolor='#F3E5F5', edgecolor='#6A1B9A', linewidth=2)
ax2.add_patch(mono_rect)
ax2.text(5, 11.2, 'Single Agent', ha='center', fontsize=11, fontweight='bold', color='#6A1B9A')
ax2.text(5, 10.7, '(All Tools)', ha='center', fontsize=8, color='#6A1B9A')

mono_display = ["squeue", "sacct", "sinfo", "scontrol_show",
                "sacctmgr_list", "sdiag", "lookup_slurm_docs",
                "scancel", "scontrol_hold", "scontrol_release",
                "scontrol_update", "sbatch", "sacctmgr_modify",
                "sreport", "sprio", "sstat", "sshare", "..."]
for i, tool in enumerate(mono_display):
    y = 10.1 - i * 0.3
    if tool in ['scancel', 'scontrol_hold', 'scontrol_release', 'scontrol_update', 'sbatch', 'sacctmgr_modify']:
        color = '#D32F2F'
    elif tool == '...':
        color = 'gray'
    else:
        color = '#43A047'
    ax2.text(5, y, f"  {tool}", ha='center', fontsize=7, fontfamily='monospace', color=color)

# Result box
res_rect2 = mpatches.FancyBboxPatch((2, 0.5), 6, 2.5, boxstyle="round,pad=0.1",
                                      facecolor='#FFEBEE', edgecolor='#C62828', linewidth=1.5)
ax2.add_patch(res_rect2)
ax2.text(5, 2.5, 'Result: 73.8% pass rate', ha='center', fontsize=10, fontweight='bold', color='#C62828')
ax2.text(5, 1.9, 'Tool Recall: 77.9%', ha='center', fontsize=9, color='#C62828')
ax2.text(5, 1.3, '(on 378 routing-neutral cases)', ha='center', fontsize=8, color='gray')

# Arrow down
ax2.annotate('', xy=(5, 3.2), xytext=(5, 4.8),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='gray'))

# Add problem annotation
ax2.text(5, 4.3, '18 tools compete for attention\n→ selection confusion', 
         ha='center', fontsize=8, color='#6A1B9A', style='italic',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='#FCE4EC', alpha=0.7))

plt.tight_layout()
plt.savefig('report/images/evaluation/tool_partitioning_comparison.png', dpi=200, bbox_inches='tight')
plt.close()
print("Saved: report/images/evaluation/tool_partitioning_comparison.png")
