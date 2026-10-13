"""Use the user's configured Meshy stdio MCP without printing credentials."""
import json, os, subprocess, select, time, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'models'
JOURNAL=ROOT/'meshy_jobs.json'
PROMPTS={
 'modern_reinforced_cutaway': 'An educational architectural cutaway maquette of a contemporary reinforced concrete building, three floors, one rectangular structural bay. Clean concrete columns, beams and floor slabs. The front right quarter is deliberately sectioned away to expose a thick continuous steel reinforcing cage inside two columns and one horizontal beam: longitudinal bars and closed rectangular stirrups, visibly distinct from the surrounding concrete shells. The exposed bars must be readable as physical geometry, not drawn lines or texture. Flat roof, open section, square footing, robust simplified proportions, neutral monochrome gray architectural museum model. No signage, no lettering, no people, no landscape, no roads, no extra buildings. One compact isolated object.',
 'roman_lime_clast_cutaway': 'Educational material specimen maquette: a single Roman concrete cube with the front upper right eighth cleanly cut away, revealing a stepped solid interior section. The dark gray mortar contains eight irregular pale lime nodules as clearly protruding solid rounded angular inclusions at different depths, plus a few larger rough stone aggregates. The contrast is a section through a dense material, not a hollow room or a dice. Large readable shapes, simple robust geometry, crisp cut faces, neutral monochrome gray museum teaching model. No text, no symbols, no base plinth, no background, no people, no surrounding scene. Inclusions must be actual distinct geometry, not just texture.',
 'roman_marine_breakwater': 'A compact educational maquette of an ancient Roman marine concrete breakwater pier, a single low L shaped massive masonry structure with a broad rectangular footing and thick blocky walls. The outer shell is partly cut away at its near corner to reveal a dense concrete core with large irregular volcanic stone aggregate inclusions bound in mortar. Show thick submerged foundation blocks and two squat rectangular pila supports, all physically connected. Simple coarse robust proportions, realistic ancient harbor engineering, neutral monochrome gray museum model. No lighthouse, no houses, no boats, no people, no water surface, no waves, no scenery, no text or signs. The main pier and exposed aggregate core must be easy to read from an elevated three quarter view.',
 'modern_reinforced_frame_v2': 'Three story reinforced concrete skeleton building under construction. Single compact rectangular structural bay, completely open front, no exterior walls, no facade panels, no window glass. Three flat floor slabs supported by four square concrete columns and horizontal beams. Two front columns have HALF of their concrete shell removed to expose the actual continuous thick vertical steel rebars and closed rectangular steel stirrup loops INSIDE the columns from footing to top floor. One front beam also exposes its reinforcing cage. Every bar must be a thick readable solid rod. Educational cutaway construction maquette, simple robust structural geometry, neutral gray concrete and darker gray steel. Flat surfaces, no roof ornaments, no steps, no text, no people or landscape.',
 'roman_lime_clast_solid_v2': 'A SOLID dense block of ancient Roman concrete, a single chunky rectangular stone specimen. One front vertical corner is diagonally sliced off, leaving a FLAT exposed diagonal cut face across the whole solid height. The concrete is solid throughout: absolutely no hollow recess, no cavity, no bowl, no walls around an empty room. The flat section reveals many small pale irregular rounded lime inclusions embedded FLUSH in the dark gray mortar matrix, and a few larger volcanic rock aggregate inclusions. The inclusions are physical solid geometry visible on the surface, not holes. A geological rock cross section teaching maquette, solid filled block, coarse simplified detail, monochrome gray, no lettering, no pedestal, no background.'
}

class MCP:
 def __init__(self):
  cfg=json.load(open('/Users/um-yunsang/.claude.json'))['mcpServers']['meshy']
  env=os.environ.copy();env.update(cfg.get('env',{}))
  self.p=subprocess.Popen([cfg['command'],*cfg['args']],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,env=env,text=True,bufsize=1)
  self.n=0
  self.rpc('initialize',{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'roman-narrative-modeling','version':'1.0'}})
  self.p.stdin.write(json.dumps({'jsonrpc':'2.0','method':'notifications/initialized'})+'\n');self.p.stdin.flush()
 def rpc(self,method,params,timeout=55):
  self.n+=1;n=self.n
  self.p.stdin.write(json.dumps({'jsonrpc':'2.0','id':n,'method':method,'params':params})+'\n');self.p.stdin.flush()
  end=time.monotonic()+timeout
  while time.monotonic()<end:
   if select.select([self.p.stdout],[],[],0.5)[0]:
    line=self.p.stdout.readline()
    try:r=json.loads(line)
    except json.JSONDecodeError:continue
    if r.get('id')==n:
     if 'error' in r:raise RuntimeError(str(r['error']))
     return r['result']
   elif self.p.poll() is not None:raise RuntimeError('Meshy MCP exited')
  raise TimeoutError(method)
 def call(self,name,args):
  r=self.rpc('tools/call',{'name':name,'arguments':args})
  if r.get('isError'):raise RuntimeError(str(r.get('content')))
  if r.get('structuredContent') is not None:return r['structuredContent']
  texts=[c['text'] for c in r.get('content',[]) if c.get('type')=='text']
  for t in texts:
   try:return json.loads(t)
   except json.JSONDecodeError:pass
  return {'message':'\n'.join(texts)}
 def close(self):
  self.p.terminate()
  try:self.p.wait(timeout=3)
  except subprocess.TimeoutExpired:self.p.kill();self.p.wait()

def find_id(data):
 if isinstance(data,dict):
  for key in ['task_id','id','result']:
   if isinstance(data.get(key),str):return data[key]
  for v in data.values():
   x=find_id(v)
   if x:return x
 return None

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 jobs=json.load(open(JOURNAL)) if JOURNAL.exists() else {'transport':'Meshy MCP stdio @0.6.0','tasks':{}}
 client=MCP()
 try:
  action=sys.argv[1]
  if action=='schema':
   ts=client.rpc('tools/list',{})['tools']
   for t in ts:
    if t['name'] in ['meshy_text_to_3d','meshy_get_task_status','meshy_download_model']:
     print(t['name'],json.dumps(t.get('inputSchema'),ensure_ascii=False))
  elif action=='start':
   jobs['balance_before']=client.call('meshy_check_balance',{'response_format':'json'})
   JOURNAL.write_text(json.dumps(jobs,ensure_ascii=False,indent=2))
   for name,prompt in PROMPTS.items():
    if name in jobs['tasks']:continue
    assert 2<=len(prompt)<=800
    args={'prompt':prompt,'ai_model':'meshy-7.1','model_type':'standard','geometry_resolution':'standard','should_remesh':True,'topology':'triangle','target_polycount':20000,'target_formats':['glb'],'response_format':'json'}
    r=client.call('meshy_text_to_3d',args)
    tid=find_id(r)
    if not tid:raise RuntimeError('Task response has no id: '+str(r))
    jobs['tasks'][name]={'task_id':tid,'request':args,'created_response':r}
    JOURNAL.write_text(json.dumps(jobs,ensure_ascii=False,indent=2))
    print(name,tid,flush=True)
   jobs['balance_after_creation']=client.call('meshy_check_balance',{'response_format':'json'})
   JOURNAL.write_text(json.dumps(jobs,ensure_ascii=False,indent=2));print('balance',jobs['balance_after_creation'],flush=True)
  elif action in ['poll','download']:
   for name,j in jobs['tasks'].items():
    r=client.call('meshy_get_task_status',{'task_id':j['task_id'],'task_type':'text-to-3d','wait':False,'response_format':'json'})
    j['latest_status']=r
    print(name,json.dumps({k:r.get(k) for k in ['status','progress','task_id']},ensure_ascii=False),flush=True)
    if action=='download':
     target=OUT/(name+'.glb')
     if not target.exists():
      j['download_response']=client.call('meshy_download_model',{'task_id':j['task_id'],'task_type':'text-to-3d','format':'glb','include_textures':False,'save_to':str(target)})
      print('saved',target.name,target.stat().st_size if target.exists() else 'not yet',flush=True)
    JOURNAL.write_text(json.dumps(jobs,ensure_ascii=False,indent=2))
  elif action=='balance':print(client.call('meshy_check_balance',{'response_format':'json'}))
 finally:client.close()

if __name__=='__main__':main()
