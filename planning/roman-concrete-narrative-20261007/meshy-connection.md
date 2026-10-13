# Meshy MCP connection discovery

## Scope
Read-only capability discovery; no model jobs, config writes, or installs. Write ownership is this file only.

## Plan
1. [complete] Find existing MCP transport and credential source safely.
2. [complete] Verify callable local MCP runtime and tool schemas.
3. [complete] Deliver connection method and constraints to root.

## Findings
- Runtime session does not expose a Meshy tool in ALL_TOOLS.
- `~/.claude.json` has `mcpServers.meshy`: stdio command `sh`, args `-c`, `cd "$HOME/Documents/로마콘크리트_3D/assets/meshy" && exec npx -y @meshy-ai/meshy-mcp-server@0.6.0`. Secret env name `MESHY_API_KEY`, never emitted.
- No Meshy config found in Codex global config, Claude Desktop config, or Roman project-local .mcp.json/.codex/config.toml.
- Existing `scripts/meshy_client.py` uses the same secret source to call Meshy REST, not MCP.
- Read-only `balance` request succeeded live and returned 800 credits.
- Existing Roman harbor asset `assets/meshy/L09_harbor_breakwater.glb` is present (7,208,896 bytes). Several core and support GLBs already exist; root should decide whether to reuse or regenerate.
- npm default `_npx` cache has no existing Meshy package directory in the inspected path.

## Progress
- Read planning-with-files entrypoint and existing root plan.
- Inspected only Meshy server names, transport, executable, args, and env names.
- Meshy auth and read-only balance verified.

## Memory
Quick registry search found Roman narrative near matches only; not used for connection conclusions.

## Verified MCP runtime
- Configured stdio server successfully initialized with protocol `2024-11-05`, server name `@meshy-ai/meshy-mcp-server`, version `0.6.0`.
- `tools/list` returned 24 tools, including `meshy_text_to_3d`, `meshy_get_task_status`, `meshy_download_model`, and `meshy_check_balance`.
- Actual MCP `tools/call` to `meshy_check_balance` returned structuredContent `{"balance":800}`. This verifies MCP, beyond direct REST.
- Child servers terminated after requests; no model jobs were created.
- `npx -y` resolved the already-configured version through local npm cache. No global install or configuration was performed.

## Relevant tool parameters
### meshy_text_to_3d
Required: `prompt` (2–800 characters). Useful explicit arguments: `ai_model:"meshy-7.1"`, `model_type:"standard"`, `geometry_resolution:"standard"`, `should_remesh:true`, `topology:"triangle"`, `target_polycount:100000`, `target_formats:["glb"]`, `response_format:"json"`. Standard untextured preview costs 20 credits per the MCP workflow guide; textures/refine are separate jobs. `meshy-t2` with `model_type:"smart-topology"` costs 5 and supports 100–15000 faces.
### meshy_get_task_status
Required: `task_id`. Use `task_type:"text-to-3d"`, `wait:false`, `response_format:"json"` to avoid long blocking calls. Default wait=true can block up to 300 seconds; do not use for the root interactive loop.
### meshy_download_model
Required: `task_id`. Use `task_type:"text-to-3d"`, `format:"glb"`, `include_textures:false`, `save_to:"/absolute/path/desired.glb"`. The tool downloads locally. A GLB is suitable for existing Blender import workflows; no extra paid format conversion is needed.

## Runnable stdio pattern
This is the proven connection pattern. Read configuration in process, inherit env, never print configuration or secret env values. Calls shown below are read-only. Adapt the final tools/call only after the root determines authorization.

```python
import json, os, subprocess, select, time
cfg = json.load(open('/Users/um-yunsang/.claude.json'))['mcpServers']['meshy']
env = os.environ.copy()
env.update(cfg.get('env', {}))
p = subprocess.Popen(
    [cfg['command'], *cfg['args']],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    env=env, text=True, bufsize=1,
)
def rpc(request_id, method, params, timeout=30):
    payload = {'jsonrpc': '2.0', 'id': request_id, 'method': method, 'params': params}
    p.stdin.write(json.dumps(payload) + chr(10))
    p.stdin.flush()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if select.select([p.stdout], [], [], 1)[0]:
            try:
                response = json.loads(p.stdout.readline())
            except json.JSONDecodeError:
                continue
            if response.get('id') == request_id:
                return response
        elif p.poll() is not None:
            raise RuntimeError('Meshy server exited')
    raise TimeoutError(method)
try:
    init = rpc(1, 'initialize', {
        'protocolVersion': '2024-11-05', 'capabilities': {},
        'clientInfo': {'name': 'roman-concrete-client', 'version': '1.0'},
    })
    p.stdin.write(json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'}) + chr(10))
    p.stdin.flush()
    response = rpc(2, 'tools/call', {
        'name': 'meshy_check_balance', 'arguments': {'response_format': 'json'},
    })
    print(response['result'].get('structuredContent', {}))
finally:
    p.terminate()
    try:
        p.wait(timeout=3)
    except subprocess.TimeoutExpired:
        p.kill()
        p.wait()
```

## Authorization boundary
The MCP initialize response includes a workflow guide requesting cost confirmation before credit-consuming calls. This is tool-provided guidance, not a system approval gate. The user has directly requested Meshy modeling; root must interpret scope and prior explicit approvals, keep the chosen paid batch concrete, and avoid unnecessary unrequested jobs. This discovery lane was explicitly read-only.

## Final status
Connection discovery complete; secret-preserving stdio MCP is available without adding it to global Codex configuration.
