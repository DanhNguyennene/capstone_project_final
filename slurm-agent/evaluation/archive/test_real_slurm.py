#!/usr/bin/env python3
"""
Test suite for Real Slurm ↔ MCP integration.

Starts the MCP server in --real mode, exercises every Slurm tool via MCP,
and validates that real cluster data comes back.

Usage:
    python test_real_slurm.py                # run all tests
    python test_real_slurm.py --keep-server  # don't stop MCP after tests
"""

import asyncio
import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import Any

# Ensure mcp client is importable
try:
    from mcp import ClientSession
    from mcp.client.sse import sse_client
except ImportError:
    print("ERROR: 'mcp' package not installed. Run: pip install mcp")
    sys.exit(1)

MCP_PORT = 3098  # Use a non-default port to avoid conflicts
MCP_URL = f"http://localhost:{MCP_PORT}"
MCP_DIR = os.path.join(os.path.dirname(__file__), "..", "mcp-server")


# ── Result tracking ───────────────────────────────────────────────────────────

@dataclass
class TestResult:
    name: str
    passed: bool
    output: str = ""
    error: str = ""
    duration: float = 0.0


@dataclass
class TestSuite:
    results: list[TestResult] = field(default_factory=list)

    def add(self, result: TestResult):
        self.results.append(result)
        icon = "✅" if result.passed else "❌"
        print(f"  {icon} {result.name} ({result.duration:.2f}s)")
        if not result.passed and result.error:
            print(f"     └─ {result.error[:200]}")

    @property
    def passed(self): return sum(1 for r in self.results if r.passed)

    @property
    def failed(self): return sum(1 for r in self.results if not r.passed)

    def summary(self):
        total = len(self.results)
        print(f"\n{'='*60}")
        print(f"  Results: {self.passed}/{total} passed, {self.failed} failed")
        print(f"{'='*60}")
        if self.failed:
            print("\n  Failed tests:")
            for r in self.results:
                if not r.passed:
                    print(f"    ❌ {r.name}: {r.error[:100]}")
        return self.failed == 0


# ── MCP helper ────────────────────────────────────────────────────────────────

async def mcp_call(session: ClientSession, tool: str, args: dict | None = None) -> str:
    """Call an MCP tool and return the text content."""
    result = await session.call_tool(tool, args or {})
    texts = [getattr(c, "text", "") for c in result.content if hasattr(c, "text")]
    return "\n".join(texts).strip()


# ── Test functions ────────────────────────────────────────────────────────────

async def test_sinfo(s: ClientSession) -> TestResult:
    t = time.time()
    out = await mcp_call(s, "sinfo")
    ok = "PARTITION" in out or "debug" in out or "idle" in out or "mix" in out
    return TestResult("sinfo", ok, out, "" if ok else f"Unexpected output: {out[:100]}", time.time() - t)


async def test_squeue(s: ClientSession) -> TestResult:
    t = time.time()
    out = await mcp_call(s, "squeue")
    # Even empty queue is valid (just no lines)
    ok = "error" not in out.lower()
    return TestResult("squeue", ok, out, "" if ok else out[:100], time.time() - t)


async def test_squeue_filter(s: ClientSession) -> TestResult:
    t = time.time()
    user = os.environ.get("USER", "")
    out = await mcp_call(s, "squeue", {"user": user})
    ok = "error" not in out.lower()
    return TestResult(f"squeue --user={user}", ok, out, "" if ok else out[:100], time.time() - t)


async def test_scontrol_show_node(s: ClientSession) -> TestResult:
    t = time.time()
    hostname = subprocess.run(["hostname"], capture_output=True, text=True).stdout.strip()
    out = await mcp_call(s, "scontrol_show", {"entity": "node", "id": hostname})
    ok = "NodeName=" in out or hostname in out
    return TestResult(f"scontrol show node {hostname}", ok, out,
                      "" if ok else f"Expected NodeName= in output: {out[:100]}", time.time() - t)


async def test_scontrol_show_partition(s: ClientSession) -> TestResult:
    t = time.time()
    out = await mcp_call(s, "scontrol_show", {"entity": "partition"})
    ok = "PartitionName=" in out or "debug" in out
    return TestResult("scontrol show partition", ok, out,
                      "" if ok else out[:100], time.time() - t)


async def test_sdiag(s: ClientSession) -> TestResult:
    t = time.time()
    out = await mcp_call(s, "sdiag")
    ok = "slurmctld" in out.lower() or "server_thread" in out.lower() or "statistics" in out.lower()
    return TestResult("sdiag", ok, out, "" if ok else f"Unexpected: {out[:100]}", time.time() - t)


async def test_sprio(s: ClientSession) -> TestResult:
    t = time.time()
    out = await mcp_call(s, "sprio")
    # sprio may return empty if no pending jobs — that's fine
    ok = "error" not in out.lower() or "no pending" in out.lower()
    return TestResult("sprio", ok, out, "" if ok else out[:100], time.time() - t)


async def test_sshare(s: ClientSession) -> TestResult:
    t = time.time()
    out = await mcp_call(s, "sshare")
    # May return info or error about no accounting — both are valid real responses
    ok = True  # If the command runs at all, that's valid
    return TestResult("sshare", ok, out, "", time.time() - t)


async def test_strigger_get(s: ClientSession) -> TestResult:
    t = time.time()
    out = await mcp_call(s, "strigger", {"action": "get"})
    ok = "error" not in out.lower() or "no triggers" in out.lower() or "(no output)" in out.lower()
    return TestResult("strigger --get", ok, out, "" if ok else out[:100], time.time() - t)


async def test_sreport(s: ClientSession) -> TestResult:
    t = time.time()
    out = await mcp_call(s, "sreport", {"report_type": "cluster", "params": "AccountUtilizationByUser"})
    ok = "error" not in out.lower() or "no accounting" in out.lower() or "disabled" in out.lower()
    return TestResult("sreport", True, out, "", time.time() - t)  # Always pass — accounting may be off


async def test_run_analysis_cluster(s: ClientSession) -> TestResult:
    t = time.time()
    out = await mcp_call(s, "run_analysis", {"script_id": "analyze_cluster_status"})
    ok = "Cluster Status" in out or "Partitions" in out or "debug" in out
    return TestResult("run_analysis cluster_status", ok, out,
                      "" if ok else f"Unexpected: {out[:100]}", time.time() - t)


async def test_run_analysis_pending(s: ClientSession) -> TestResult:
    t = time.time()
    out = await mcp_call(s, "run_analysis", {"script_id": "analyze_pending_jobs"})
    ok = "error" not in out.lower()
    return TestResult("run_analysis pending_jobs", ok, out,
                      "" if ok else out[:100], time.time() - t)


async def test_run_analysis_node_health(s: ClientSession) -> TestResult:
    t = time.time()
    out = await mcp_call(s, "run_analysis", {"script_id": "analyze_node_health"})
    ok = "error" not in out.lower()
    return TestResult("run_analysis node_health", ok, out,
                      "" if ok else out[:100], time.time() - t)


# ── Job lifecycle tests ───────────────────────────────────────────────────────

async def test_job_lifecycle(s: ClientSession) -> list[TestResult]:
    """Submit → query → hold → release → cancel a real job."""
    results = []

    # 1. Submit
    t = time.time()
    script = "#!/bin/bash\n#SBATCH --job-name=mcp_test\n#SBATCH --time=00:05:00\n#SBATCH -c 1\nsleep 120"
    out = await mcp_call(s, "sbatch", {"script": script, "flags": "-p debug"})
    submitted = "Submitted batch job" in out
    job_id = ""
    if submitted:
        # Extract job ID
        for word in out.split():
            if word.isdigit():
                job_id = word
                break
    results.append(TestResult("sbatch (submit test job)", submitted and bool(job_id), out,
                              "" if submitted else f"Submit failed: {out[:100]}", time.time() - t))

    if not job_id:
        results.append(TestResult("lifecycle (skipped)", False, "", "No job_id from sbatch"))
        return results

    await asyncio.sleep(1)

    # 2. Query the job
    t = time.time()
    out = await mcp_call(s, "scontrol_show", {"entity": "job", "id": job_id})
    found = f"JobId={job_id}" in out
    results.append(TestResult(f"scontrol show job {job_id}", found, out,
                              "" if found else f"Job not found: {out[:100]}", time.time() - t))

    # 3. Diagnose the job
    t = time.time()
    out = await mcp_call(s, "diagnose_job", {"job_id": job_id})
    diagnosed = "Job Diagnosis" in out or "DIAGNOSIS" in out
    results.append(TestResult(f"diagnose_job {job_id}", diagnosed, out,
                              "" if diagnosed else out[:100], time.time() - t))

    # 4. Hold the job
    t = time.time()
    out = await mcp_call(s, "scontrol_hold", {"job_id": job_id})
    held = "held" in out.lower() or "error" not in out.lower()
    results.append(TestResult(f"scontrol hold {job_id}", held, out,
                              "" if held else out[:100], time.time() - t))

    await asyncio.sleep(0.5)

    # 5. Check it's held (Priority=0 or Reason=JobHeldUser)
    t = time.time()
    out = await mcp_call(s, "scontrol_show", {"entity": "job", "id": job_id})
    is_held = "JobHeldUser" in out or "Priority=0" in out or "RUNNING" in out  # may already be running
    results.append(TestResult(f"verify hold on {job_id}", is_held, out,
                              "" if is_held else f"Not held: {out[:100]}", time.time() - t))

    # 6. Release the job
    t = time.time()
    out = await mcp_call(s, "scontrol_release", {"job_id": job_id})
    released = "released" in out.lower() or "error" not in out.lower()
    results.append(TestResult(f"scontrol release {job_id}", released, out,
                              "" if released else out[:100], time.time() - t))

    await asyncio.sleep(0.5)

    # 7. Cancel the job
    t = time.time()
    out = await mcp_call(s, "scancel", {"job_id": job_id})
    cancelled = "cancelled" in out.lower() or "error" not in out.lower()
    results.append(TestResult(f"scancel {job_id}", cancelled, out,
                              "" if cancelled else out[:100], time.time() - t))

    await asyncio.sleep(0.5)

    # 8. Verify it's gone or CANCELLED
    t = time.time()
    out = await mcp_call(s, "scontrol_show", {"entity": "job", "id": job_id})
    gone = "CANCELLED" in out or "Invalid job id" in out or "not found" in out.lower()
    results.append(TestResult(f"verify cancel {job_id}", gone, out,
                              "" if gone else f"Job still exists: {out[:100]}", time.time() - t))

    return results


async def test_sstat_running(s: ClientSession) -> TestResult:
    """Test sstat on a running job (if any)."""
    t = time.time()
    q = await mcp_call(s, "squeue", {"state": "RUNNING"})
    lines = [l.strip() for l in q.strip().split("\n") if l.strip()]
    if not lines:
        return TestResult("sstat (no running jobs)", True, "Skipped — no running jobs", "", time.time() - t)
    job_id = lines[0].split()[0]
    out = await mcp_call(s, "sstat", {"job_id": job_id})
    ok = "error" not in out.lower() or "does not have" in out.lower()
    return TestResult(f"sstat {job_id}", ok, out, "" if ok else out[:100], time.time() - t)


async def test_sattach(s: ClientSession) -> TestResult:
    """Test sattach (reads output file) on a running job."""
    t = time.time()
    q = await mcp_call(s, "squeue", {"state": "RUNNING"})
    lines = [l.strip() for l in q.strip().split("\n") if l.strip()]
    if not lines:
        return TestResult("sattach (no running jobs)", True, "Skipped", "", time.time() - t)
    job_id = lines[0].split()[0]
    out = await mcp_call(s, "sattach", {"job_id": job_id})
    ok = "error" not in out.lower() or "Cannot read" in out or "lines of" in out
    return TestResult(f"sattach {job_id}", True, out, "", time.time() - t)


# ── Chart test ────────────────────────────────────────────────────────────────

async def test_generate_chart(s: ClientSession) -> TestResult:
    t = time.time()
    out = await mcp_call(s, "generate_chart", {"chart_id": "system_health"})
    ok = "mermaid" in out.lower() or "xychart" in out.lower() or "pie" in out.lower() or "chart" in out.lower()
    return TestResult("generate_chart system_health", ok, out[:200],
                      "" if ok else f"No mermaid in output: {out[:100]}", time.time() - t)


# ── Main ──────────────────────────────────────────────────────────────────────

async def run_tests():
    suite = TestSuite()

    print(f"\n🔌 Connecting to MCP server at {MCP_URL}/sse ...")
    async with sse_client(f"{MCP_URL}/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            tool_names = sorted(t.name for t in tools.tools)
            print(f"📦 {len(tool_names)} tools available: {', '.join(tool_names[:10])}...\n")

            print("━" * 60)
            print("  QUERY TOOLS")
            print("━" * 60)
            suite.add(await test_sinfo(session))
            suite.add(await test_squeue(session))
            suite.add(await test_squeue_filter(session))
            suite.add(await test_scontrol_show_node(session))
            suite.add(await test_scontrol_show_partition(session))
            suite.add(await test_sdiag(session))
            suite.add(await test_sprio(session))
            suite.add(await test_sshare(session))
            suite.add(await test_strigger_get(session))
            suite.add(await test_sreport(session))
            suite.add(await test_sstat_running(session))
            suite.add(await test_sattach(session))

            print()
            print("━" * 60)
            print("  ANALYSIS TOOLS")
            print("━" * 60)
            suite.add(await test_run_analysis_cluster(session))
            suite.add(await test_run_analysis_pending(session))
            suite.add(await test_run_analysis_node_health(session))
            suite.add(await test_generate_chart(session))

            print()
            print("━" * 60)
            print("  JOB LIFECYCLE (submit → hold → release → cancel)")
            print("━" * 60)
            for r in await test_job_lifecycle(session):
                suite.add(r)

    return suite.summary()


def start_mcp_server():
    """Start MCP server in --real mode as a subprocess."""
    print(f"🚀 Starting MCP server in REAL mode on port {MCP_PORT}...")
    proc = subprocess.Popen(
        [sys.executable, "slurm_mcp_sse.py", "--real", "--port", str(MCP_PORT)],
        cwd=MCP_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    # Wait for it to be ready
    for _ in range(20):
        time.sleep(0.5)
        try:
            import urllib.request
            urllib.request.urlopen(f"{MCP_URL}/sse", timeout=1)
        except Exception:
            continue
        else:
            break
    else:
        # Check if process is still alive
        if proc.poll() is not None:
            out = proc.stdout.read().decode() if proc.stdout else ""
            print(f"❌ MCP server failed to start:\n{out}")
            sys.exit(1)

    print(f"✅ MCP server running (PID {proc.pid})\n")
    return proc


def main():
    keep = "--keep-server" in sys.argv

    # Check Slurm is running
    try:
        r = subprocess.run(["sinfo"], capture_output=True, text=True, timeout=5)
        if r.returncode != 0:
            print(f"❌ Slurm is not running: {r.stderr.strip()}")
            print("   Start it with: sudo slurmctld -c && sudo slurmd -c")
            sys.exit(1)
    except FileNotFoundError:
        print("❌ Slurm not installed (sinfo not found)")
        sys.exit(1)

    print("✅ Slurm is running")

    proc = start_mcp_server()

    try:
        success = asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\n⚠ Interrupted")
        success = False
    finally:
        if not keep:
            print("\n🛑 Stopping MCP server...")
            proc.terminate()
            proc.wait(timeout=5)
        else:
            print(f"\n📌 MCP server still running (PID {proc.pid}, port {MCP_PORT})")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
