#!/usr/bin/env bash
# fix-slurm.sh — Fix slurmctld startup failures
# Handles: cons_res→cons_tres migration, SlurmUser mismatch, permissions
# Run with: sudo bash fix-slurm.sh

set -e
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e "${YELLOW}=== Slurm Controller Fix ===${NC}"

# 1. Check SelectType config
echo -n "Checking slurm.conf SelectType... "
SELECT=$(grep -oP 'SelectType=\K.*' /etc/slurm/slurm.conf 2>/dev/null || echo "NOT FOUND")
echo "$SELECT"

if [[ "$SELECT" == "select/cons_res" ]]; then
    echo -e "${YELLOW}Updating cons_res → cons_tres in slurm.conf${NC}"
    sed -i 's|SelectType=select/cons_res|SelectType=select/cons_tres|' /etc/slurm/slurm.conf
elif [[ "$SELECT" == "select/cons_tres" ]]; then
    echo -e "${GREEN}Config is correct (cons_tres)${NC}"
else
    echo -e "${RED}Unexpected SelectType: $SELECT${NC}"
    exit 1
fi

# 2. Fix SlurmUser mismatch (systemd unit runs as 'slurm', conf must match)
UNIT_USER=$(grep -oP '^User=\K.*' /usr/lib/systemd/system/slurmctld.service 2>/dev/null || echo "")
CONF_USER=$(grep -oP '^SlurmUser=\K.*' /etc/slurm/slurm.conf 2>/dev/null || echo "")
if [[ -n "$UNIT_USER" && "$CONF_USER" != "$UNIT_USER" ]]; then
    echo -e "${YELLOW}Fixing SlurmUser mismatch: conf='${CONF_USER}' → '${UNIT_USER}' (matches systemd unit)${NC}"
    sed -i "s|^SlurmUser=.*|SlurmUser=${UNIT_USER}|" /etc/slurm/slurm.conf
else
    echo -e "${GREEN}SlurmUser is correct (${CONF_USER})${NC}"
fi

# 3. Clear stale state (slurmctld caches old plugin name)
echo "Clearing stale state files..."
rm -f /var/spool/slurmctld/node_state \
      /var/spool/slurmctld/part_state \
      /var/spool/slurmctld/job_state \
      /var/spool/slurmctld/resv_state \
      /var/spool/slurmctld/trigger_state 2>/dev/null
echo -e "${GREEN}  ✓ State cleared${NC}"

# 4. Ensure spool directories + log file exist with correct ownership
SLURM_USER="${UNIT_USER:-slurm}"
for dir in /var/spool/slurmctld /var/spool/slurmd /var/log; do
    mkdir -p "$dir"
done
touch /var/log/slurmctld.log
chown "$SLURM_USER:$SLURM_USER" /var/log/slurmctld.log
chown -R "$SLURM_USER:$SLURM_USER" /var/spool/slurmctld 2>/dev/null || true
echo -e "${GREEN}  ✓ Permissions set for ${SLURM_USER}${NC}"

# 4. Restart daemons
echo "Restarting slurmctld..."
systemctl restart slurmctld
sleep 2

if systemctl is-active --quiet slurmctld; then
    echo -e "${GREEN}  ✓ slurmctld is running${NC}"
else
    echo -e "${RED}  ✗ slurmctld failed to start${NC}"
    journalctl -u slurmctld --no-pager -n 10
    exit 1
fi

echo "Restarting slurmd..."
systemctl restart slurmd
sleep 1

if systemctl is-active --quiet slurmd; then
    echo -e "${GREEN}  ✓ slurmd is running${NC}"
else
    echo -e "${RED}  ✗ slurmd failed to start${NC}"
    journalctl -u slurmd --no-pager -n 10
    exit 1
fi

# 5. Bring node online (it starts as UNKNOWN after state clear)
echo "Setting node to idle..."
sleep 1
scontrol update NodeName=$(hostname) State=idle 2>/dev/null || true

# 6. Verify
echo ""
echo -e "${YELLOW}=== Verification ===${NC}"
echo "--- sinfo ---"
timeout 5 sinfo || echo -e "${RED}sinfo timed out${NC}"
echo ""
echo "--- squeue ---"
timeout 5 squeue || echo -e "${RED}squeue timed out${NC}"
echo ""
echo -e "${GREEN}=== Done! Slurm is ready for --real mode ===${NC}"
echo "Run: ./start.sh --real"
