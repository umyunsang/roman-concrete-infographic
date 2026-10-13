"""Call configured official Figma MCP through Codex's app-server; no model inference."""
import argparse, json, queue, subprocess, threading, time
from pathlib import Path

def call(tool, arguments, timeout=150):
    proc = subprocess.Popen(
        ['codex', 'app-server', '--stdio', '-c', 'mcp_servers.node_repl.enabled=false',
         '-c', 'mcp_servers.higgsfield.enabled=false'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        text=True, bufsize=1)
    messages = queue.Queue()
    threading.Thread(target=lambda: [messages.put(line) for line in proc.stdout], daemon=True).start()
    def request(ident, method, params):
        proc.stdin.write(json.dumps({'id': ident, 'method': method, 'params': params}) + '\n')
        proc.stdin.flush()
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            try:
                result = json.loads(messages.get(timeout=1))
            except queue.Empty:
                continue
            except json.JSONDecodeError:
                continue
            if result.get('id') == ident:
                if 'error' in result:
                    raise RuntimeError(json.dumps(result['error']))
                return result['result']
        raise TimeoutError(method)
    try:
        request(1, 'initialize', {'clientInfo': {'name': 'figma_canvas_workflow', 'version': '1.0'},
                                  'capabilities': {'experimentalApi': True}})
        proc.stdin.write(json.dumps({'method': 'initialized', 'params': {}}) + '\n')
        proc.stdin.flush()
        thread = request(2, 'thread/start', {'cwd': str(Path(__file__).resolve().parents[1]),
                                           'ephemeral': True})
        return request(3, 'mcpServer/tool/call', {'threadId': thread['thread']['id'],
                                                'server': 'figma', 'tool': tool, 'arguments': arguments})
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=4)
        except subprocess.TimeoutExpired:
            proc.kill()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tool')
    parser.add_argument('--input', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = call(args.tool, json.loads(args.input.read_text()) if args.input else {})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    for item in result.get('content', []):
        if item.get('type') == 'text':
            print(item['text'])
    if result.get('isError'):
        raise SystemExit(1)
