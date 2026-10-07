"""Build only public configuration files. Never copy the app workspace recursively."""
import argparse,hashlib,html,json,re,shutil,urllib.parse,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FORBIDDEN_KEYS={"token","access_token","auth","authorization","password","passwd","secret","txsecret","txtime","sign","signature"}
def digest(data): return hashlib.sha256(data).hexdigest()
def public_url(value):
    url=urllib.parse.urlsplit(value)
    if url.scheme not in {"http","https"} or not url.hostname or url.username or url.password: raise ValueError("Invalid public URL")
    if FORBIDDEN_KEYS.intersection(k.lower() for k in urllib.parse.parse_qs(url.query)): raise ValueError("Do not publish credential/signed URLs")
def validate_catalog(data, uhd):
    if data.get("schemaVersion")!=1 or not isinstance(data.get("version"),int) or data["version"]<0: raise ValueError("Invalid version")
    channels=data.get("channels")
    if not isinstance(channels,list) or len(channels)>5000 or len({c['id'] for c in channels})!=len(channels): raise ValueError("Invalid channels")
    for c in channels:
        if not c.get("name") or not c.get("sources") or len(c['sources'])>8: raise ValueError("Incomplete channel")
        if uhd and (not c['id'].startswith('uhd-') or c.get('category')!='4K专区' or not c.get('smartSources')): raise ValueError("Not an independent UHD channel")
        if uhd and not any(s.get('enabled',True) and s.get('width',0)>=3840 and s.get('height',0)>=2160 for s in c['sources']): raise ValueError("No 2160P candidate")
        for s in c['sources']:
            public_url(s['url'])
            if s.get('headers'): raise ValueError("Do not publish custom headers")
            if not uhd and (not s.get('verified') or not s.get('reviewReference')): raise ValueError("Unreviewed default source")
def build(output):
    output.mkdir(parents=True,exist_ok=True)
    main=(ROOT/'config/channels.json').read_bytes();uhd=(ROOT/'config/uhd-channels.json').read_bytes();trial=(ROOT/'config/trial-channels.m3u').read_bytes()
    catalog=json.loads(main);ucatalog=json.loads(uhd);validate_catalog(catalog,False);validate_catalog(ucatalog,True)
    for line in trial.decode('utf-8-sig').splitlines():
        if line.startswith(('http://','https://')): public_url(line.strip())
    files={'channels.json':main,'uhd-channels.json':uhd,'trial-channels.m3u':trial}
    manifest={'schemaVersion':1,'catalogVersion':catalog['version'],'uhdVersion':ucatalog['version'],'uhdCount':len(ucatalog['channels']),'trialChannelCount':trial.count(b'#EXTINF:'),'sha256':{name:digest(body) for name,body in files.items()},'warnings':[{'channelId':'uhd-hebei-4k-trial','message':'当前线路声音异常待修复'}]}
    for name,body in files.items(): (output/name).write_bytes(body)
    (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (output/'.nojekyll').write_text('',encoding='utf-8')
    (output/'index.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>客厅电视 · 频道配置</title><style>body{max-width:760px;margin:60px auto;padding:24px;background:#0b1420;color:#e9f0f6;font:18px/1.8 system-ui}a{color:#62d9ca}section{padding:24px;border-radius:20px;background:#162338}small{color:#a5b5c6}</style><h1>客厅电视 · 频道配置</h1><section><p>配置版本 '+str(ucatalog['version'])+' · '+str(len(ucatalog['channels']))+' 个4K试播条目</p><p>河北当前线路声音异常待修复。其他已使用线路保持。</p><p><a href="uhd-channels.json">4K专区配置</a> · <a href="channels.json">正式频道配置</a></p><p><a href="trial-channels.m3u">49频道试播列表</a> · <a href="manifest.json">配置校验清单</a></p></section><p><small>本页只分发配置，不提供视频转播。正式审核频道当前为空。公开试播来源不代表长期稳定或第三方接入条件已经确认；仅导入有权使用的来源。配置不包含账号、签名密钥或观看记录。</small></p></html>','utf-8')
    return manifest
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'dist/remote-config-site');parser.add_argument('--zip',type=Path);args=parser.parse_args();manifest=build(args.output)
    allowed={'channels.json','uhd-channels.json','trial-channels.m3u','manifest.json','index.html','.nojekyll'}
    assert {p.name for p in args.output.iterdir()}==allowed,'Unexpected public files; refuse to package'
    if args.zip:
        with zipfile.ZipFile(args.zip,'w',zipfile.ZIP_DEFLATED) as z:
            for name in sorted(allowed):z.write(args.output/name,name)
        with zipfile.ZipFile(args.zip) as z:assert z.testzip() is None and set(z.namelist())==allowed
    print(json.dumps(manifest,ensure_ascii=False))
