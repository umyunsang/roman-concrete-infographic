import concurrent.futures, hashlib, json, time, urllib.request, urllib.error, mimetypes
from pathlib import Path
from figma_call import call

ROOT=Path(__file__).resolve().parents[1]
ASSETS={
 'pantheon-cutaway':ROOT/'outputs/pantheon-cutaway-concept.png',
 'R1':ROOT/'evidence/references/trajan.png',
 'R2':ROOT/'evidence/references/kowloon-portfolio.jpg',
 'R3':ROOT/'evidence/references/notre-dame.png',
 'colosseum-photo':ROOT/'source-images/image8.jpg',
 'pantheon-exterior':ROOT/'evidence/images/pantheon-exterior.jpg',
 'pantheon-interior':ROOT/'evidence/images/pantheon-interior.jpg',
 'pantheon-section':ROOT/'evidence/images/pantheon-section.png',
 '2023-mechanism':ROOT/'evidence/images/2023-mechanism.jpg',
 '2023-experiment':ROOT/'evidence/images/2023-experiment.jpg',
 '2025-production':ROOT/'evidence/images/2025-production.png',
}

def objects(result):
    if result.get('isError'):
        raise RuntimeError('Figma tool reported an error: '+str(result.get('content')))
    out=[]
    if isinstance(result.get('structuredContent'),dict):out.append(result['structuredContent'])
    for item in result.get('content',[]):
        if item.get('type')=='text':
            try:out.append(json.loads(item['text']))
            except json.JSONDecodeError:pass
    return out

def result_file(path):
    return next(o for o in objects(json.loads(Path(path).read_text())) if isinstance(o,dict))

def upload_images(key,targets):
    result=call('upload_assets',{'fileKey':key,'count':len(targets),'nodeIds':[t['nodeId'] for t in targets],'scaleMode':'FIT'})
    info=next(o for o in objects(result) if isinstance(o,dict) and 'uploads' in o)
    def post(pair):
        target,entry=pair;path=ASSETS[target['key']]
        request=urllib.request.Request(entry['submitUrl'],data=path.read_bytes(),method='POST',headers={'Content-Type':mimetypes.guess_type(path.name)[0] or 'application/octet-stream'})
        with urllib.request.urlopen(request,timeout=45) as r:body=json.loads(r.read());status=r.status
        if not body.get('success') or not body.get('imageHash'):
            raise RuntimeError('Asset upload did not confirm a stored image')
        return {'nodeId':target['nodeId'],'asset':target['key'],'http_status':status,'imageHash':body['imageHash'],'scaleMode':target.get('scaleMode','FIT')}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        return list(pool.map(post,zip(targets,info['uploads'])))

def apply_image_fills(key,page_id,uploads):
    data=[{'id':x['nodeId'],'hash':x['imageHash'],'scaleMode':x.get('scaleMode','FIT')} for x in uploads]
    code="const page=await figma.getNodeByIdAsync("+json.dumps(page_id)+");if(figma.editorType==='figma')await figma.setCurrentPageAsync(page);const specs="+json.dumps(data)+";const out=[];for(const s of specs){const n=await figma.getNodeByIdAsync(s.id);if(!n||!('fills' in n))throw new Error('Invalid image target');n.fills=[{type:'IMAGE',imageHash:s.hash,scaleMode:s.scaleMode}];out.push({id:n.id,type:n.fills[0].type,imageHash:n.fills[0].imageHash});}return {mutatedNodeIds:out.map(x=>x.id),images:out};"
    return call('use_figma',{'fileKey':key,'code':code,'description':'Bind confirmed uploaded image hashes to canvas image targets and verify IMAGE paints','skillNames':'figma-use'})

def fetch_asset(url,magic):
    request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'image/avif,image/webp,image/apng,image/*,application/pdf,*/*;q=0.8'})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request,timeout=30) as r:data=r.read();status=r.status
        except urllib.error.HTTPError as error:
            if error.code==404 and attempt<4:
                time.sleep(2)
                continue
            raise
        if data.startswith(magic):return data
        if status!=202:break
        time.sleep(2)
    raise RuntimeError('Asset fetch did not return requested format; HTTP '+str(status))

def capture(key,node,dest,max_dimension=3000):
    r=call('get_screenshot',{'fileKey':key,'nodeId':node,'maxDimension':max_dimension})
    info=next(o for o in objects(r) if isinstance(o,dict) and 'image_url' in o)
    data=fetch_asset(info['image_url'],b'\x89PNG');dest=Path(dest);dest.write_bytes(data)
    return {'path':str(dest),'bytes':len(data),'width':info.get('width'),'height':info.get('height'),'sha256':hashlib.sha256(data).hexdigest()}

def export_pdf(key,node,dest):
    r=call('download_assets',{'fileKey':key,'nodeId':node})
    def urls(value):
        if isinstance(value,dict):
            for k,v in value.items():
                if isinstance(v,str) and v.startswith(('https://','http://')):yield v
                elif isinstance(v,(dict,list)):yield from urls(v)
        elif isinstance(value,list):
            for v in value:yield from urls(v)
    candidates=[]
    for obj in objects(r):
        if isinstance(obj,dict):candidates.extend(urls(obj.get('export',obj)))
    for url in candidates:
        try:data=fetch_asset(url,b'%PDF')
        except Exception:continue
        dest=Path(dest);dest.write_bytes(data)
        return {'path':str(dest),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    raise RuntimeError('No PDF export was returned')
