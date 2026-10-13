"""Meshy REST 클라이언트(키는 ~/.claude.json의 meshy MCP 설정에서 읽고 출력하지 않음).

사용: python3 meshy_client.py balance
      python3 meshy_client.py t2d <id> "<prompt>" [polycount]   # 텍스트→3D 미리보기(형태만) 생성·대기·GLB 저장
      python3 meshy_client.py i2d <id> <image_path_or_url> [polycount]  # 이미지→3D
"""
import json, os, sys, time, base64, urllib.request, mimetypes

API = 'https://api.meshy.ai'
OUT = os.path.expanduser('~/Documents/로마콘크리트_3D/assets/meshy')


def key():
    cfg = json.load(open(os.path.expanduser('~/.claude.json')))
    return cfg['mcpServers']['meshy']['env']['MESHY_API_KEY']


def req(method, path, body=None):
    r = urllib.request.Request(API + path, method=method, headers={'Authorization': f'Bearer {key()}', 'Content-Type': 'application/json'},
                               data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.loads(resp.read().decode())


def wait(kind, tid, every=10, limit=1800):
    t0 = time.time()
    while time.time() - t0 < limit:
        st = req('GET', f'/openapi/{kind}/{tid}')
        print(f"  {st.get('status')} {st.get('progress')}%", flush=True)
        if st.get('status') in ('SUCCEEDED', 'FAILED', 'CANCELED', 'EXPIRED'):
            return st
        time.sleep(every)
    raise TimeoutError(tid)


def save(st, name):
    os.makedirs(OUT, exist_ok=True)
    url = (st.get('model_urls') or {}).get('glb')
    path = os.path.join(OUT, f'{name}.glb')
    urllib.request.urlretrieve(url, path)
    json.dump({k: st.get(k) for k in ('id', 'status', 'prompt', 'art_style', 'created_at', 'thumbnail_url')}, open(os.path.join(OUT, f'{name}.json'), 'w'), ensure_ascii=False, indent=1)
    print('saved', path, os.path.getsize(path))
    return path


def main():
    cmd = sys.argv[1]
    if cmd == 'balance':
        print(req('GET', '/openapi/v1/balance'))
    elif cmd == 't2d':
        name, prompt = sys.argv[2], sys.argv[3]
        poly = int(sys.argv[4]) if len(sys.argv) > 4 else 100000
        tid = req('POST', '/openapi/v2/text-to-3d', {'mode': 'preview', 'prompt': prompt, 'art_style': 'realistic',
                                                      'should_remesh': True, 'topology': 'triangle', 'target_polycount': poly})['result']
        print('task', tid)
        st = wait('v2/text-to-3d', tid)
        if st['status'] == 'SUCCEEDED':
            save(st, name)
        else:
            print('failed', st.get('task_error'))
    elif cmd == 'i2d':
        name, src = sys.argv[2], sys.argv[3]
        poly = int(sys.argv[4]) if len(sys.argv) > 4 else 100000
        if os.path.exists(src):
            mt = mimetypes.guess_type(src)[0] or 'image/png'
            src = f'data:{mt};base64,' + base64.b64encode(open(src, 'rb').read()).decode()
        tid = req('POST', '/openapi/v1/image-to-3d', {'image_url': src, 'should_texture': False, 'should_remesh': True,
                                                      'topology': 'triangle', 'target_polycount': poly})['result']
        print('task', tid)
        st = wait('v1/image-to-3d', tid)
        if st['status'] == 'SUCCEEDED':
            save(st, name)
        else:
            print('failed', st.get('task_error'))


if __name__ == '__main__':
    main()
