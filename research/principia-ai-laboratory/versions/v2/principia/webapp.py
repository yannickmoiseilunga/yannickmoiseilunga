"""Local-only threaded browser workbench; no third-party dependencies.
The worker writes reports atomically into separate timestamped folders.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import shutil
import threading
import traceback
import urllib.parse
import webbrowser
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .experiments import PRESETS,run_suite
from .external import csv_suite,ollama_models,ollama_suite
from .reporting import save_run
from .real_study import run_real_study,save_real_study,power_plan,CATALOG,OPENML_CATALOG,register_custom_csv,CUSTOM_SOURCES
from .text_study import run_text_study,save_text
from .local_benchmark import run_local_benchmark,save_local

ROOT=Path(__file__).resolve().parent.parent
STATIC=ROOT/'static'; REPORTS=ROOT/'reports';REPORTS.mkdir(exist_ok=True)
_lock=threading.RLock()
_state={'status':'idle','progress':None,'run':None,'error':None,'kind':None}


def safe_name(name):
    if not re.fullmatch(r'[A-Za-z0-9_\-]+',name): raise ValueError('Invalid run id')
    return name


def run_worker(kind,args):
    def progress(p):
        with _lock:_state['progress']=p
    try:
        if kind=='synthetic':
            data=run_suite(args['preset'],int(args['seed']),progress,include_predictions=True)
            result=save_run(data,REPORTS)
            folder=Path(result['directory'])
        elif kind=='real':
            if args.get('external_path'):
                custom=register_custom_csv(args['external_path'],args['external_target'],args['external_domain'],args.get('external_base'))
                args['datasets'].append(custom)
            data=run_real_study(args.get('seeds'),int(args.get('seed',42)),args.get('datasets'),int(args.get('cap',900)),progress)
            result=save_real_study(data,REPORTS);folder=Path(result['directory'])
        elif kind=='text':
            data=run_text_study(int(args.get('seeds',20)),int(args.get('seed',42)),progress)
            result=save_text(data,REPORTS);folder=Path(result['directory'])
        elif kind=='local':
            result=run_local_benchmark(args['model'],args['path'],int(args['count']),progress)
            saved=save_local(result,REPORTS);folder=Path(saved['directory'])
        elif kind=='csv':
            data=csv_suite(args['path'],args['target'],args.get('domain') or None,args.get('train_domain') or None,
                           int(args['seed']),int(args.get('seeds',3)))
            result=save_run(data,REPORTS)
            folder=Path(result['directory'])
        else:
            result=ollama_suite(args['model'],int(args['count']),int(args['seed']),progress)
            # Local model results include raw responses in a standalone file (not synthetic reports).
            import datetime as dt
            folder=REPORTS/('ollama_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+str(args['seed']))
            folder.mkdir(exist_ok=True)
            (folder/'model_experiment.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
            (folder/'dashboard.json').write_text(json.dumps({'rows':[{'experiment':'ollama_math','model':result['model'],
                'domain':'test','accuracy':result['accuracy'],'seed':args['seed'],'n_test':result['attempted']}],
                'settings':{'preset':'ollama','seed':args['seed']},'findings':[],'corollary_map':{}},indent=2),encoding='utf-8')
        zippath=REPORTS/(folder.name+'.zip')
        with zipfile.ZipFile(zippath,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p in folder.rglob('*'):
                if p.is_file():z.write(p,arcname=folder.name+'/'+str(p.relative_to(folder)))
        with _lock:_state.update(status='finished',run=folder.name,error=None,progress={'completed':1,'total':1,'detail':'Reports saved'})
    except Exception as exc:
        traceback.print_exc()
        with _lock:_state.update(status='failed',error=f'{type(exc).__name__}: {exc}',progress=None)


class Handler(BaseHTTPRequestHandler):
    server_version='PrincipiaAILab/2.0'
    def log_message(self,format,*args):pass
    def json_response(self,obj,status=200):
        body=json.dumps(obj,allow_nan=False).encode()
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)))
        self.end_headers();self.wfile.write(body)
    def do_GET(self):
        parsed=urllib.parse.urlsplit(self.path);path=parsed.path
        params=urllib.parse.parse_qs(parsed.query)
        if path=='/api/power':
            return self.json_response({'power':power_plan(),'datasets':CATALOG,'extra_datasets':OPENML_CATALOG})
        if path=='/api/status':
            with _lock:data=dict(_state)
            return self.json_response(data)
        if path=='/api/runs':
            runs=sorted([x.name for x in REPORTS.iterdir() if x.is_dir() and (x/'dashboard.json').is_file()],reverse=True)
            return self.json_response({'runs':runs[:60]})
        if path=='/api/models':
            try:return self.json_response({'models':ollama_models()})
            except Exception as exc:return self.json_response({'models':[],'notice':'Local Ollama unavailable: '+str(exc)})
        if path in ('/api/result','/api/download'):
            try:
                name=safe_name(params.get('run',[''])[0]);target=REPORTS/name
                if path=='/api/result':
                    data=(target/'dashboard.json').read_bytes()
                    ct='application/json; charset=utf-8';fname=None
                else:
                    data=(REPORTS/(name+'.zip')).read_bytes()
                    ct='application/zip';fname=name+'.zip'
                self.send_response(200);self.send_header('Content-Type',ct)
                if fname:self.send_header('Content-Disposition','attachment; filename="'+fname+'"')
                self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
                return
            except (ValueError,FileNotFoundError):return self.json_response({'error':'Run not found'},404)
        filename='index.html' if path=='/' else path.lstrip('/')
        safe={'index.html','app.js','style.css'}
        if filename not in safe:return self.json_response({'error':'Not found'},404)
        data=(STATIC/filename).read_bytes()
        ctype='text/html' if filename.endswith('.html') else 'text/javascript' if filename.endswith('.js') else 'text/css'
        self.send_response(200);self.send_header('Content-Type',ctype+'; charset=utf-8')
        self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_POST(self):
        path=urllib.parse.urlsplit(self.path).path
        if path not in ('/api/start','/api/csv','/api/ollama','/api/real','/api/text','/api/local'):return self.json_response({'error':'Not found'},404)
        length=int(self.headers.get('Content-Length','0'))
        if not 0<length<=12_000_000:return self.json_response({'error':'Input body exceeds 12 MB limit'},413)
        try:args=json.loads(self.rfile.read(length))
        except (ValueError,UnicodeDecodeError):return self.json_response({'error':'Invalid JSON'},400)
        if not isinstance(args,dict):return self.json_response({'error':'JSON object expected'},400)
        kind={'/api/start':'synthetic','/api/csv':'csv','/api/ollama':'ollama',
               '/api/real':'real','/api/text':'text','/api/local':'local'}[path]
        try:
            if kind=='synthetic':
                args['preset']=str(args.get('preset','quick'))
                if args['preset'] not in PRESETS:raise ValueError('Unknown preset')
                args['seed']=int(args.get('seed',42))
            elif kind=='real':
                args['seed']=int(args.get('seed',42));args['seeds']=int(args.get('seeds',20))
                args['cap']=int(args.get('cap',900))
                if not 2<=args['seeds']<=100:raise ValueError('Seeds must be between 2 and 100')
                if not 100<=args['cap']<=3000:raise ValueError('Training cap must be between 100 and 3000')
                ds=args.get('datasets',list(CATALOG))
                required=1 if args.get('external_csv') is not None else 2
                if not isinstance(ds,list) or not required<=len(ds)<=7 or any(x not in CATALOG and x not in OPENML_CATALOG for x in ds):
                    raise ValueError('Specify 2-7 registered datasets, counting any external CSV')
                args['datasets']=list(dict.fromkeys(ds))
                csv_blob=args.get('external_csv')
                if csv_blob is not None:
                    if not isinstance(csv_blob,str) or len(csv_blob)>9_000_000:raise ValueError('Real-domain CSV exceeds 9 MB upload limit')
                    if not args.get('external_target') or not args.get('external_domain'):
                        raise ValueError('External CSV requires target and domain column names')
            elif kind=='text':
                args['seed']=int(args.get('seed',42));args['seeds']=int(args.get('seeds',20))
                if not 2<=args['seeds']<=100:raise ValueError('Seed count 2-100')
            elif kind=='local':
                args['count']=int(args.get('count',50))
                if not 1<=args['count']<=200:raise ValueError('Question count 1-200')
                if not isinstance(args.get('model'),str) or not args['model']:raise ValueError('Select an installed Ollama model')
                filename=Path(str(args.get('filename','benchmark.jsonl'))).name
                content=args.get('content','')
                if not filename.endswith('.jsonl'):raise ValueError('Upload .jsonl')
                if not isinstance(content,str) or len(content)>10_000_000:raise ValueError('Benchmark JSONL too large')
            elif kind=='csv':
                filename=Path(str(args.get('filename','data.csv'))).name
                if not filename.lower().endswith('.csv'):raise ValueError('CSV file required')
                content=args.get('content','')
                if not isinstance(content,str) or len(content)>10_000_000:raise ValueError('CSV content too large')
                if not args.get('target'):raise ValueError('Select a target column')
                args['seed']=int(args.get('seed',42));args['seeds']=int(args.get('seeds',3))
                if not 1<=args['seeds']<=20:raise ValueError('Seed count must be 1 to 20')
            else:
                args['count']=int(args.get('count',15));args['seed']=int(args.get('seed',42))
                if not isinstance(args.get('model'),str) or not args['model']:raise ValueError('Select an Ollama model')
                if not 5<=args['count']<=200:raise ValueError('5-200 local model tasks')
        except (ValueError,TypeError) as exc:return self.json_response({'error':str(exc)},400)
        with _lock:
            if _state['status']=='running':return self.json_response({'error':'A study is already running'},409)
            if kind=='real' and args.get('external_csv') is not None:
                import uuid
                uploads=REPORTS/'uploads';uploads.mkdir(exist_ok=True)
                p=uploads/(uuid.uuid4().hex+'_real.csv')
                p.write_text(args.pop('external_csv'),encoding='utf-8')
                args['external_path']=str(p)
            if kind in ('csv','local'):
                uploads=REPORTS/'uploads';uploads.mkdir(exist_ok=True)
                import uuid
                p=uploads/(uuid.uuid4().hex+'_'+filename)
                p.write_text(content,encoding='utf-8')
                args['path']=str(p);del args['content']
            _state.update(status='running',run=None,error=None,kind=kind,progress={'completed':0,'total':1,'detail':'Starting'})
            worker=threading.Thread(target=run_worker,args=(kind,args),daemon=True)
            worker.start()
        return self.json_response({'started':True},202)


def serve(port=0,open_browser=True):
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    server.daemon_threads=True
    address='http://127.0.0.1:'+str(server.server_port)
    print('\nPrincipia AI Laboratory — local URL: '+address)
    print('The V1/small bundled real-data studies work offline; OpenML, text and Ollama are optional. Ctrl+C to stop.\n')
    if open_browser:threading.Timer(.8,lambda:webbrowser.open(address)).start()
    try:server.serve_forever(poll_interval=.4)
    except KeyboardInterrupt:pass
    finally:server.server_close()
