"""POST local photos to Figma's single-use asset URLs without logging URLs."""
import concurrent.futures
import json
import mimetypes
import sys
import urllib.error
import urllib.request
from pathlib import Path


def upload(task):
    path = Path(task['local_path'])
    content_type = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
    data = path.read_bytes()
    if len(data) > 10 * 1024 * 1024:
        return {'id': task['id'], 'node_id': task['node_id'], 'ok': False, 'error': 'asset exceeds 10MB'}
    request = urllib.request.Request(task['upload_url'], data=data,
                                     headers={'Content-Type': content_type}, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            body = response.read()
            status = response.status
        details = None
        try:
            details = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            pass
        return {'id': task['id'], 'node_id': task['node_id'], 'ok': 200 <= status < 300,
                'status': status, 'bytes': len(data), 'response_keys': list(details) if isinstance(details, dict) else []}
    except urllib.error.HTTPError as error:
        return {'id': task['id'], 'node_id': task['node_id'], 'ok': False, 'status': error.code}
    except Exception as error:
        return {'id': task['id'], 'node_id': task['node_id'], 'ok': False, 'error_type': type(error).__name__}


tasks = json.loads(sys.argv[1])
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    results = list(pool.map(upload, tasks))
print(json.dumps({'results': results, 'total': len(results), 'passed': sum(r['ok'] for r in results)}, ensure_ascii=False))
sys.exit(0 if all(r['ok'] for r in results) else 1)
