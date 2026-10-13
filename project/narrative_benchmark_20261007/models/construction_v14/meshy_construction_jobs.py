"""Bounded, idempotent Meshy MCP jobs for the two authorized v14 vault stages.

Uses the existing configured stdio MCP transport; never prints credentials.
Owns only construction_v14 files and meshy_construction_jobs_v14.json.
No refinement, Ultra passes, regeneration, Blender or Figma modifications.
"""
import hashlib
import json
import runpy
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'models/construction_v14'
JOURNAL = ROOT / 'meshy_construction_jobs_v14.json'
HELPERS = runpy.run_path(str(ROOT / 'scripts/meshy_mcp_jobs.py'), run_name='mcp_helpers')
PROMPTS = {
    'roman_vault_timber_centering': (
        'Roman concrete vault under construction on timber centering. One short '
        'arched corridor section with two rough masonry sidewalls. An exposed '
        'semicircular timber centering has thick readable curved ribs and upright '
        'wooden props. Only the back half of the rubble-and-mortar vault is built '
        'on top, leaving the front timber ribs clearly visible. One small bucket '
        'on a ledge. Compact isolated architectural museum maquette, simple robust '
        'physical geometry, neutral monochrome gray. No metal rebar, no '
        'wheelbarrow, no text, no people, no extra landscape, no dome or facade.'
    ),
    'roman_completed_vault_cutaway': (
        'Completed short Roman vaulted corridor cutaway section. One compact '
        'semicircular barrel vault with two thick sidewalls and a flat walkway. '
        'The near end is cut away to expose the thick solid rubble-concrete core '
        'inside the arch and sidewall. Thin brick-facing strips and one simplified '
        'stone pier are distinct physical surfaces, with robust readable large '
        'shapes. Neutral monochrome gray isolated architectural museum maquette. '
        'No dome, no temple, no exterior facade, no metal rebar, no people, no '
        'text, no landscape.'
    ),
}

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def write(jobs):
    OUT.mkdir(parents=True, exist_ok=True)
    JOURNAL.write_text(json.dumps(jobs, ensure_ascii=False, indent=2) + '\n')

def state(response):
    return {k: response.get(k) for k in
            ('task_id', 'id', 'status', 'progress', 'ai_model', 'model_type', 'error')
            if response.get(k) is not None}

def balance(client):
    response = client.call('meshy_check_balance', {'response_format': 'json'})
    value = response.get('balance')
    if not isinstance(value, (int, float)):
        raise RuntimeError('Unexpected credit balance schema')
    return {'balance': value, 'checked_at': now()}

def inspect_glb(path):
    data = path.read_bytes()
    magic, version, declared_size = struct.unpack_from('<III', data, 0)
    if magic != 0x46546C67 or version != 2 or declared_size != len(data):
        raise ValueError('Invalid GLB v2 header: ' + path.name)
    offset, document, bin_chunks = 12, None, 0
    while offset < len(data):
        size, kind = struct.unpack_from('<II', data, offset)
        chunk = data[offset + 8:offset + 8 + size]
        if kind == 0x4E4F534A:
            document = json.loads(chunk.rstrip(b' \x00'))
        elif kind == 0x004E4942:
            bin_chunks += 1
        offset += 8 + size
    if document is None or not bin_chunks:
        raise ValueError('GLB is missing JSON or geometry binary data')
    primitive_count = triangles = vertex_accessors = 0
    for mesh in document.get('meshes', []):
        for primitive in mesh.get('primitives', []):
            primitive_count += 1
            if primitive.get('mode', 4) != 4:
                raise ValueError('Unexpected non-triangle primitive')
            position = document['accessors'][primitive['attributes']['POSITION']]
            vertex_accessors += position['count']
            triangles += (document['accessors'][primitive['indices']]['count']
                          if 'indices' in primitive else position['count']) // 3
    return {'filename': path.name, 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest(), 'glb_version': version,
            'meshes': len(document.get('meshes', [])), 'primitives': primitive_count,
            'vertex_accessor_count_sum': vertex_accessors, 'triangles': triangles,
            'material_count': len(document.get('materials', [])),
            'textures': len(document.get('textures', [])),
            'images': len(document.get('images', [])), 'inspected_at': now()}

def main(action):
    jobs = json.loads(JOURNAL.read_text()) if JOURNAL.exists() else {
        'created_at': now(), 'transport': 'Existing configured Meshy stdio MCP',
        'scope': 'Two illustrative Roman vault construction stages; not exact Colosseum replicas.',
        'max_tasks': 2, 'expected_each_credits': 20, 'max_total_credits': 40,
        'textures_or_refine_requested': False, 'tasks': {},
    }
    client = HELPERS['MCP']()
    try:
        if action == 'start':
            schemas = {t['name']: t for t in client.rpc('tools/list', {})['tools']
                       if t['name'] in ('meshy_text_to_3d', 'meshy_get_task_status',
                                        'meshy_download_model', 'meshy_check_balance')}
            (OUT / 'meshy_schema_evidence.json').write_text(
                json.dumps({'checked_at': now(), 'tools': schemas}, ensure_ascii=False, indent=2) + '\n')
            schema = schemas['meshy_text_to_3d']['inputSchema']['properties']
            if 'meshy-7.1' not in schema['ai_model']['enum']:
                raise RuntimeError('Authorized meshy-7.1 is not currently available')
            if '20 credits' not in schema['ai_model'].get('description', ''):
                raise RuntimeError('Unexpected cost description: generation stopped')
            jobs.setdefault('balance_before', balance(client))
            write(jobs)
            for name, prompt in PROMPTS.items():
                if name in jobs['tasks']:
                    continue
                if len(jobs['tasks']) >= 2:
                    raise RuntimeError('Two-task limit reached')
                if not 2 <= len(prompt) <= 800:
                    raise ValueError('Prompt is outside current schema bounds')
                before = balance(client)
                if before['balance'] < 20:
                    raise RuntimeError('Insufficient credits; no new job started')
                request = {'prompt': prompt, 'ai_model': 'meshy-7.1',
                           'model_type': 'standard', 'geometry_resolution': 'standard',
                           'should_remesh': True, 'topology': 'triangle',
                           'target_polycount': 20000, 'target_formats': ['glb'],
                           'response_format': 'json'}
                response = client.call('meshy_text_to_3d', request)
                task_id = HELPERS['find_id'](response)
                if not task_id:
                    raise RuntimeError('Creation response has no task id; do not retry blindly')
                jobs['tasks'][name] = {'task_id': task_id, 'request': request,
                                       'created_at': now(), 'created_response': state(response),
                                       'balance_before': before}
                write(jobs)
                after = balance(client)
                jobs['tasks'][name]['balance_after'] = after
                spent = before['balance'] - after['balance']
                jobs['tasks'][name]['observed_creation_credit_delta'] = spent
                write(jobs)
                print('CREATED', name, task_id, 'credit_delta', spent, flush=True)
                if spent < 0 or spent > 20:
                    jobs['stopped_for_unexpected_cost'] = {'task': name, 'delta': spent}
                    write(jobs)
                    raise RuntimeError('Unexpected credit delta; further generation stopped')
            jobs['balance_after_creation'] = balance(client)
            jobs['observed_total_creation_credit_delta'] = (
                jobs['balance_before']['balance'] - jobs['balance_after_creation']['balance'])
            write(jobs)
            print('CREDIT_SUMMARY', jobs['observed_total_creation_credit_delta'],
                  'remaining', jobs['balance_after_creation']['balance'], flush=True)
        elif action in ('poll', 'download'):
            for name, job in jobs['tasks'].items():
                response = client.call('meshy_get_task_status',
                    {'task_id': job['task_id'], 'task_type': 'text-to-3d',
                     'wait': False, 'response_format': 'json'})
                snapshot = {'checked_at': now(), **state(response)}
                job['latest_status'] = snapshot
                job.setdefault('status_history', []).append(snapshot)
                write(jobs)
                print('STATUS', name, json.dumps(snapshot, ensure_ascii=False), flush=True)
                if action == 'download' and response.get('status') == 'SUCCEEDED':
                    path = OUT / (name + '.glb')
                    if not path.exists():
                        result = client.call('meshy_download_model',
                            {'task_id': job['task_id'], 'task_type': 'text-to-3d',
                             'format': 'glb', 'include_textures': False, 'save_to': str(path)})
                        job['download_response'] = {k: result.get(k) for k in
                            ('local_path', 'file_size_bytes', 'project_dir') if result.get(k) is not None}
                        write(jobs)
                    if not path.exists():
                        raise RuntimeError('MCP download did not create the requested local GLB')
                    if 'file_inspection' not in job:
                        job['file_inspection'] = inspect_glb(path)
                        write(jobs)
                    print('MODEL_READY', name, json.dumps(job['file_inspection'], ensure_ascii=False), flush=True)
            if action == 'download':
                jobs['balance_after_download'] = balance(client)
                jobs['models_ready'] = all('file_inspection' in j for j in jobs['tasks'].values()) and len(jobs['tasks']) == 2
                write(jobs)
        else:
            raise ValueError('Expected start, poll or download')
    finally:
        client.close()

if __name__ == '__main__':
    main(sys.argv[1])
