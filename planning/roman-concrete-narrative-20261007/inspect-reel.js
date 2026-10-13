const p = await attachBrowserTab('0093DFB205F6B1D5FEDB927F500EBF0B');
const data = await p.evaluate(() => {
  const v=document.querySelector('video'); v.pause();
  const resources=performance.getEntriesByType('resource').map(r=>r.name).filter(u=>/\.mp4|\.m4a|\.mpd/.test(u));
  const scripts=Array.from(document.querySelectorAll('script')).filter(s=>s.type==='application/json').map(s=>s.textContent);
  return {url:location.href,video:{duration:v.duration,width:v.videoWidth,height:v.videoHeight,rect:v.getBoundingClientRect().toJSON()},resources,scripts};
});
await fs.mkdir('roman-reel-evidence',{recursive:true});
await fs.writeFile('roman-reel-evidence/reel-page-data.json',JSON.stringify(data));
await p.screenshot({path:await fs.resolvePath('roman-reel-evidence/reel-browser.png')});
console.log({url:data.url,video:data.video,resources:data.resources.length,scripts:data.scripts.length,screenshot:'reel-browser.png'});
