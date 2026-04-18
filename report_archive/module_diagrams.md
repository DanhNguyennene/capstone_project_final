# System Module Diagrams - Conceptual View

This document contains all conceptual diagrams for each module of the Slurm Agent system.

---

## 1. Frontend Module

**Concept**: User interaction and real-time streaming interface

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'fontSize':'16px'}}}%%
flowchart LR
    User([User]) -->|Input| UI[React Frontend]
    UI -->|Establish| SSE[SSE Connection]
    SSE -->|Subscribe| Events[Event Stream]
    Events -->|Receive| Display{Render Event}
    Display -->|status| Status[Status Indicator]
    Display -->|content| Message[Chat Message]
    Display -->|chart| Chart[Mermaid Diagram]
    Status --> Ready[Display Ready]
    Message --> Ready
    Chart --> Ready
    Ready -->|Next Input| User
    
    style User fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
    style UI fill:#3b82f6,stroke:#2563eb,stroke-width:2px,color:#fff
    style SSE fill:#60a5fa,stroke:#3b82f6,stroke-width:2px,color:#fff
    style Chart fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff
    style Ready fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
```

**Key Components**:
- React UI with TypeScript
- SSE connection for real-time updates
- Event-driven rendering (status/content/chart)
- Mermaid.js for interactive diagrams

---

## 2. Agent Orchestration Module

**Concept**: Multi-agent system with reasoning and execution models

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'fontSize':'16px'}}}%%
flowchart TB
    Input([User Message]) --> Main[Main Agent<br/>Qwen3-Coder<br/>Reasoning Model]
    Main -->|Load| History[(Session History<br/>SQLite DB)]
    History --> Main
    
    Main -->|Decide| Router{Tool Router}
    
    Router -->|Data Query| Analysis[Analysis Sub-Agent<br/>GPT-OSS<br/>Tool Executor]
    Router -->|Cluster Action| Action[Action Sub-Agent<br/>GPT-OSS<br/>Tool Executor]
    Router -->|Visualization| Chart[Chart Tool<br/>Direct Call]
    
    Analysis -->|MCP Call| MCPTools[MCP Server]
    Action -->|MCP Call| MCPTools
    Chart -->|HTTP Call| MCPTools
    
    MCPTools -->|Return Data| Results[Results]
    Results -->|Format| Main
    Main -->|Save| History
    Main -->|Stream| Output([Response])
    
    style Input fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
    style Main fill:#3b82f6,stroke:#2563eb,stroke-width:3px,color:#fff
    style Analysis fill:#60a5fa,stroke:#3b82f6,stroke-width:2px,color:#fff
    style Action fill:#60a5fa,stroke:#3b82f6,stroke-width:2px,color:#fff
    style History fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff
    style Output fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
```

**Key Components**:
- Main Agent (Qwen3-Coder) for reasoning
- Sub-Agents (GPT-OSS) for precise tool execution
- SQLite for conversation history
- Tool router for delegation

---

## 3. MCP Server Module

**Concept**: Stateful SSE transport with tool routing

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'fontSize':'16px'}}}%%
flowchart TB
    Request([Agent Request]) -->|with session_id| MCP[MCP Server<br/>SSE Transport]
    
    MCP --> Route{Tool Router}
    
    Route -->|Read| Slurm[Slurm Queries<br/>squeue/sacct/sinfo]
    Route -->|Write| Actions[Slurm Actions<br/>scancel/sbatch]
    Route -->|Analyze| Scripts[📜 5 Analysis Scripts<br/>Bash - Cluster Diagnostics]
    Route -->|Visualize| Charts[📊 5 Chart Scripts<br/>Python - Mermaid Diagrams]
    
    Slurm --> Return[Return Result]
    Actions --> Return
    Scripts --> Return
    Charts --> Return
    
    Return -->|Stream via SSE| Response([SSE Event])
    
    style Request fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
    style MCP fill:#3b82f6,stroke:#2563eb,stroke-width:3px,color:#fff
    style Scripts fill:#f59e0b,stroke:#d97706,stroke-width:3px,color:#fff
    style Charts fill:#f59e0b,stroke:#d97706,stroke-width:3px,color:#fff
    style Response fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
```

**Key Components**:
- SSE session management with session_id
- Tool routing to 5 categories
- Stateful bidirectional communication
- Response via SSE stream

---

## 4. Predefined Scripts Module

**Concept**: Pre-built analysis and visualization scripts

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'fontSize':'16px'}}}%%
flowchart LR
    subgraph Analysis["Analysis Scripts (Bash)"]
        direction TB
        A1[analyze_my_jobs.sh<br/>Current job status]
        A2[analyze_failed_jobs.sh<br/>Failure diagnostics]
        A3[analyze_pending_jobs.sh<br/>Queue bottlenecks]
        A4[analyze_cluster_status.sh<br/>Overall health]
        A5[analyze_gpu_resources.sh<br/>GPU availability]
    end
    
    subgraph Charts["Chart Scripts (Python)"]
        direction TB
        C1[chart_system_health.py<br/>Health dashboard]
        C2[chart_cluster_topology.py<br/>Node hierarchy]
        C3[chart_pending_analysis.py<br/>Queue diagnosis]
        C4[chart_job_lifecycle.py<br/>Job timeline]
        C5[chart_resource_map.py<br/>Resource allocation]
    end
    
    MCP[MCP Tool Router] -->|run_analysis| Analysis
    MCP -->|generate_chart| Charts
    
    Analysis -->|Execute| Slurm[Slurm Commands]
    Charts -->|Query + Generate| Mermaid[Mermaid Diagrams]
    
    Slurm -->|Output| Result[Structured Data]
    Mermaid -->|Output| Result
    Result --> Return([Return to Agent])
    
    style MCP fill:#3b82f6,stroke:#2563eb,stroke-width:3px,color:#fff
    style Analysis fill:#f59e0b,stroke:#d97706,stroke-width:2px
    style Charts fill:#f59e0b,stroke:#d97706,stroke-width:2px
    style Slurm fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff
    style Mermaid fill:#ec4899,stroke:#db2777,stroke-width:2px,color:#fff
    style Return fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
```

**Key Components**:
- 5 analysis scripts (Bash) - cluster diagnostics
- 5 chart scripts (Python) - Mermaid diagram generation
- Direct Slurm command execution
- Structured output for agent consumption

---

## 5. Confirmation/Safety Module

**Concept**: Safety guardrails for dangerous operations

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'fontSize':'16px'}}}%%
flowchart TB
    Request([Dangerous Action<br/>e.g. Cancel Job]) --> Guard{Guarded<br/>Wrapper}
    
    Guard -->|Queue| DB[(SQLite DB<br/>Pending Actions)]
    DB -->|Ask| User{User<br/>Confirms?}
    
    User -->|Yes| Execute[Execute via MCP]
    User -->|No| Cancel[Clear Queue]
    
    Execute -->|Success| Result1([✅ Completed])
    Cancel --> Result2([❌ Cancelled])
    
    Guard -.Safe Tool.-> Direct[Execute<br/>Immediately]
    Direct --> Result3([✅ Success])
    
    style Request fill:#3b82f6,stroke:#2563eb,stroke-width:3px,color:#fff
    style Guard fill:#f59e0b,stroke:#d97706,stroke-width:3px,color:#fff
    style DB fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff
    style Execute fill:#22c55e,stroke:#16a34a,stroke-width:2px,color:#fff
    style Cancel fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    style Result1 fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
    style Result2 fill:#ef4444,stroke:#dc2626,stroke-width:3px,color:#fff
    style Result3 fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
```

**Key Components**:
- Guarded wrapper intercepts dangerous operations
- SQLite persistent queue
- User confirmation flow
- Safe tools bypass confirmation

---

## 6. Session Management Module

**Concept**: Persistent conversation state and history

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'fontSize':'16px'}}}%%
flowchart TB
    Start([New Request]) --> Check{Has<br/>session_id?}
    
    Check -->|No| Create[Create New Session]
    Create -->|Generate ID| NewID[session_id]
    NewID -->|Initialize| DB1[(SQLite Database)]
    DB1 -->|Empty History| Context1[New Context]
    
    Check -->|Yes| Lookup[Lookup Session]
    Lookup -->|Query| DB2[(SQLite Database)]
    DB2 -->|Load History| Filter[Filter Chart Artifacts]
    Filter -->|Clean Text| History[Conversation History]
    History -->|Load Pending| Actions[(Pending Actions DB)]
    Actions --> Context2[Session Context]
    
    Context1 --> Process[Process Request]
    Context2 --> Process
    
    Process -->|Agent Run| Generate[Generate Response]
    Generate -->|Save Items| DB2
    Generate -->|Update| Activity[last_activity Timestamp]
    
    Activity -->|Check| Cleanup{Session<br/>Expired?}
    Cleanup -->|No| Keep[Keep Alive]
    Cleanup -->|Yes - 5min timeout| Remove[Remove Session]
    
    Keep --> Ready([Ready for Next])
    Remove --> End([Session Closed])
    
    style Start fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
    style DB1 fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff
    style DB2 fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff
    style Actions fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff
    style Filter fill:#3b82f6,stroke:#2563eb,stroke-width:2px,color:#fff
    style Keep fill:#22c55e,stroke:#16a34a,stroke-width:2px,color:#fff
    style Remove fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    style Ready fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
```

**Key Components**:
- session_id based tracking
- SQLite persistent storage
- Chart artifact filtering (removes HTML from history)
- Session timeout (5 minutes)
- Context preservation across requests

---

---

## 7. Agent Tool Access & Safety Model

**Concept**: Role-based tool access with safety guardrails

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'fontSize':'14px'}}}%%
flowchart TB
    subgraph MainAgent["Main Agent - Qwen3-Coder (Orchestrator)"]
        M1[analyze_cluster<br/>Call Analysis Sub-Agent]
        M2[manage_jobs<br/>Call Action Sub-Agent]
        M3[generate_chart<br/>Direct HTTP Call]
        M4[confirm_action<br/>Execute Queued Actions]
        M5[cancel_action<br/>Clear Queue]
        M6[check_pending_actions<br/>View Queue]
    end
    
    subgraph AnalysisSub["Analysis Sub-Agent - GPT-OSS (Read-Only)"]
        direction TB
        A1[run_analysis<br/>Predefined Scripts]
        A2[squeue<br/>Query Jobs]
        A3[sacct<br/>Job History]
        A4[sinfo<br/>Node Status]
        A5[scontrol_show<br/>Detailed Info]
        A6[web_search<br/>Documentation]
    end
    
    subgraph ActionSub["Action Sub-Agent - GPT-OSS (Read + Write)"]
        direction TB
        subgraph Safe["✅ Safe Tools (No Confirmation)"]
            S1[squeue, sacct, sinfo<br/>Read-Only Queries]
            S2[srun, salloc<br/>Interactive Execution]
            S3[sacctmgr_show, sreport<br/>Accounting Queries]
            S4[web_search<br/>Documentation]
        end
        
        subgraph Dangerous["⚠️ Dangerous Tools (Need Confirmation)"]
            D1[scancel<br/>Cancel Jobs]
            D2[sbatch<br/>Submit Jobs]
            D3[scontrol_hold/release<br/>Job Control]
            D4[scontrol_update<br/>Modify Jobs]
            D5[scontrol_create/delete<br/>Admin Operations]
            D6[sacctmgr_add/modify/delete<br/>Account Management]
        end
    end
    
    M1 -->|Delegates to| AnalysisSub
    M2 -->|Delegates to| ActionSub
    
    AnalysisSub -->|All tools are SAFE| MCP1[MCP Server]
    Safe -->|Execute Immediately| MCP2[MCP Server]
    Dangerous -->|Queue for Confirmation| Queue[(Pending Actions<br/>SQLite DB)]
    
    Queue -->|User confirms via| M4
    M4 -->|Execute All| MCP3[MCP Server]
    
    style MainAgent fill:#e0e7ff,stroke:#4f46e5,stroke-width:3px
    style AnalysisSub fill:#dbeafe,stroke:#1d4ed8,stroke-width:3px
    style ActionSub fill:#dcfce7,stroke:#16a34a,stroke-width:3px
    style Safe fill:#d1fae5,stroke:#10b981,stroke-width:2px
    style Dangerous fill:#fee2e2,stroke:#dc2626,stroke-width:3px
    style Queue fill:#fef3c7,stroke:#d97706,stroke-width:2px
    
    style A1 fill:#bfdbfe,stroke:#3b82f6
    style A2 fill:#bfdbfe,stroke:#3b82f6
    style A3 fill:#bfdbfe,stroke:#3b82f6
    style A4 fill:#bfdbfe,stroke:#3b82f6
    style A5 fill:#bfdbfe,stroke:#3b82f6
    style A6 fill:#bfdbfe,stroke:#3b82f6
    
    style D1 fill:#fecaca,stroke:#ef4444
    style D2 fill:#fecaca,stroke:#ef4444
    style D3 fill:#fecaca,stroke:#ef4444
    style D4 fill:#fecaca,stroke:#ef4444
    style D5 fill:#fecaca,stroke:#ef4444
    style D6 fill:#fecaca,stroke:#ef4444
```

**Key Components**:

### **Tool Access Matrix**

| Tool Category | Tool Name | Agent Access | Safety | Description | Reason |
|--------------|-----------|--------------|--------|-------------|---------|
| **Query Tools** | `squeue` | Analysis, Action | ✅ Safe | View job queue status | Read-only, no state change |
| | `sacct` | Analysis, Action | ✅ Safe | Query job history & accounting | Read-only, historical data |
| | `sinfo` | Analysis, Action | ✅ Safe | View node/partition status | Read-only, cluster info |
| | `scontrol_show` | Analysis, Action | ✅ Safe | Detailed job/node info | Read-only, diagnostic |
| **Analysis** | `run_analysis` | Analysis | ✅ Safe | Execute predefined scripts | Read-only queries only |
| | `web_search` | Analysis, Action | ✅ Safe | Search documentation/solutions | External, no cluster impact |
| **Interactive** | `srun` | Action | ✅ Safe | Run command on nodes | User's own allocation |
| | `salloc` | Action | ✅ Safe | Allocate resources | User's own resources |
| **Reporting** | `sacctmgr_show` | Action | ✅ Safe | View accounts/users/QOS | Read-only accounting |
| | `sreport` | Action | ✅ Safe | Generate usage reports | Read-only statistics |
| **Job Control** | `scancel` | Action | ⚠️ Dangerous | Cancel jobs | Terminates running jobs |
| | `sbatch` | Action | ⚠️ Dangerous | Submit batch job | Creates new jobs |
| | `scontrol_hold` | Action | ⚠️ Dangerous | Prevent job from starting | Modifies job state |
| | `scontrol_release` | Action | ⚠️ Dangerous | Allow held job to run | Modifies job state |
| | `scontrol_update` | Action | ⚠️ Dangerous | Change job parameters | Alters running jobs |
| | `scontrol_requeue` | Action | ⚠️ Dangerous | Restart failed job | Resets job state |
| **Admin Ops** | `scontrol_create` | Action | ⚠️ Dangerous | Create partition/reservation | Changes cluster config |
| | `scontrol_delete` | Action | ⚠️ Dangerous | Delete partition/reservation | Removes cluster resources |
| | `scontrol_reconfigure` | Action | ⚠️ Dangerous | Reload Slurm config | Affects entire cluster |
| **Accounting** | `sacctmgr_add` | Action | ⚠️ Dangerous | Add account/user/QOS | Modifies accounting DB |
| | `sacctmgr_modify` | Action | ⚠️ Dangerous | Update account settings | Changes permissions |
| | `sacctmgr_delete` | Action | ⚠️ Dangerous | Remove account/user | Revokes access |
| **Visualization** | `generate_chart` | Main Agent | ✅ Safe | Create Mermaid diagrams | Read-only visualization |
| **Confirmation** | `confirm_action` | Main Agent | 🔐 Protected | Execute queued actions | User-approved only |
| | `cancel_action` | Main Agent | 🔐 Protected | Clear action queue | User control |
| | `check_pending_actions` | Main Agent | ✅ Safe | View queued actions | Read-only queue status |

### **Safety Model**
1. **Analysis Sub-Agent** → Only safe tools → Execute immediately
2. **Action Sub-Agent + Safe Tool** → Execute immediately
3. **Action Sub-Agent + Dangerous Tool** → Queue to DB → User confirms → Execute
4. **Main Agent** → Never directly calls Slurm tools → Delegates to sub-agents

### **Compact Table for Slides**

| Tool Category | Main | Analysis | Action | Safety | Purpose |
|--------------|------|----------|--------|--------|---------|
| **Slurm Query** (squeue/sacct/sinfo) | ❌ | ✅ | ✅ | ✅ | Query cluster state |
| **Analysis Scripts** (5 bash scripts) | ❌ | ✅ | ❌ | ✅ | Predefined diagnostics |
| **Chart Scripts** (5 python scripts) | ✅ | ❌ | ❌ | ✅ | Mermaid visualization |
| **Web Search** | ❌ | ✅ | ✅ | ✅ | Documentation lookup |
| **Interactive** (srun/salloc) | ❌ | ❌ | ✅ | ✅ | User resources |
| **Job Control** (scancel/sbatch) | ❌ | ❌ | ✅ | ⚠️ | Modify jobs |
| **Admin Ops** (scontrol_*) | ❌ | ❌ | ✅ | ⚠️ | Cluster config |
| **Accounting** (sacctmgr_*) | ❌ | ❌ | ✅ | ⚠️ | User/account mgmt |
| **Confirmation** (confirm/cancel) | ✅ | ❌ | ❌ | 🔐 | User approval |

**Legend**: ✅ Access | ❌ No Access | ⚠️ Needs confirmation | 🔐 Protected flow

---

## Summary

All 7 modules work together to provide:
- **Stateful conversational AI** for HPC cluster management
- **Safety guardrails** for dangerous operations
- **Role-based tool access** with least-privilege principle
- **Pre-built analysis and visualization** tools
- **Persistent session state** across requests
- **Real-time streaming** user experience
