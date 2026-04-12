# Exit Codes and Signal Reference

**When to use:** User asks about exit codes, signal numbers, why a job was killed, or what an error code means.

## Exit Code Format
Slurm displays `ExitCode:Signal` (e.g., `0:9` means exit=0, signal=9/SIGKILL).
In `sacct`, combined code is `128 + signal` (e.g., signal 9 → exit 137).

## Common Exit Codes
| Code | Meaning | Fix |
|------|---------|-----|
| 0 | Success | — |
| 1 | Generic application error | Check stderr/stdout for traceback |
| 2 | Shell misuse / bad syntax | Check script for syntax errors |
| 3 | Cannot execute | Check permissions: `chmod +x script.sh` |
| 126 | Cannot execute (permissions) | Fix file permissions |
| 127 | Command not found | Add `module load` for required software |
| 128 | Invalid exit argument | Check `exit` calls in script |
| 130 | SIGINT (Ctrl+C / scancel --signal=INT) | Job was interrupted |
| 134 | SIGABRT (assertion failure) | Debug application logic |
| 137 | SIGKILL (OOM) | Increase `--mem` by 20-50% |
| 139 | SIGSEGV (segfault) | Memory bug, debug with valgrind |
| 143 | SIGTERM (walltime) | Increase `--time` or add checkpointing |

## Signal Numbers
| Signal | Number | Default Action | Common Cause |
|--------|--------|---------------|--------------|
| SIGHUP | 1 | Terminate | Terminal disconnect |
| SIGINT | 2 | Terminate | Ctrl+C / user cancel |
| SIGQUIT | 3 | Core dump | Ctrl+\ |
| SIGILL | 4 | Core dump | Bad binary / wrong arch |
| SIGABRT | 6 | Core dump | abort() / assertion |
| SIGBUS | 7 | Core dump | Bad memory access / FS error |
| SIGFPE | 8 | Core dump | Divide by zero |
| SIGKILL | 9 | Terminate (uncatchable) | OOM-killer or admin `scancel -s KILL` |
| SIGSEGV | 11 | Core dump | Null pointer / buffer overflow |
| SIGPIPE | 13 | Terminate | Broken pipe |
| SIGALRM | 14 | Terminate | Alarm timer |
| SIGTERM | 15 | Terminate | Walltime or `scancel` |
| SIGXCPU | 24 | Core dump | CPU time limit |
| SIGXFSZ | 25 | Core dump | File size limit |

## Steps
1. Call `diagnose_job(job_id=<id>)` for full diagnosis with hints.
2. Call `sacct(job_id=<id>)` to see ExitCode, State, MaxRSS.
3. If 137: OOM → suggest increasing --mem.
4. If 143: walltime → suggest increasing --time.
5. If 127: command not found → suggest module load.
6. If 139: segfault → suggest debugging with gdb/valgrind.

## Output Format
State the exit code, signal, root cause, and one specific fix.
