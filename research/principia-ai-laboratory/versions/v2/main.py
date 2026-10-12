#!/usr/bin/env python3
"""Principia Artificial Intelligence Laboratory. Python 3.10+, offline-first."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from principia.experiments import PRESETS,run_suite
from principia.external import csv_suite,ollama_suite
from principia.reporting import save_run
from principia.webapp import serve
from principia.real_study import run_real_study,save_real_study, power_plan,register_custom_csv
from principia.text_study import run_text_study,save_text
from principia.local_benchmark import run_local_benchmark,save_local


def main(argv=None):
    parser=argparse.ArgumentParser(description='Run the V1 synthetic lab and the V2 preregistered real-data laboratory. V2 needs optional research dependencies.')
    parser.add_argument('--run',action='store_true',help='Run synthetic suite in CLI instead of opening dashboard')
    parser.add_argument('--real-study',action='store_true',help='V2 real-dataset / unseen-architecture investigation')
    parser.add_argument('--text-study',action='store_true',help='V2 optional real text-modality investigation (downloads 20 Newsgroups)')
    parser.add_argument('--local-benchmark',help='V2 local pretrained Ollama evaluation from benchmark JSONL')
    parser.add_argument('--model',default='',help='Installed Ollama model for --local-benchmark')
    parser.add_argument('--seeds',type=int,default=None,help='Seeds for real or text studies; default from prospective power plan')
    parser.add_argument('--datasets',default='breast_cancer,wine,iris,digits',help='Comma-delimited real datasets, including optional openml_* codes')
    parser.add_argument('--cap',type=int,default=900,help='Cap empirical training records per seed')
    parser.add_argument('--real-csv',action='append',default=[],help='Additional site/time grouped real CSV; may be repeated')
    parser.add_argument('--real-target',default='label',help='Binary 0/1 CSV target')
    parser.add_argument('--real-domain',default='domain',help='CSV site/time/environment grouping')
    parser.add_argument('--real-base',default=None,help='Value of CSV domain representing the train environment')
    parser.add_argument('--preset',choices=list(PRESETS),default='quick')
    parser.add_argument('--seed',type=int,default=42)
    parser.add_argument('--port',type=int,default=0,help='Local dashboard TCP port, 0 = automatically choose a free port')
    parser.add_argument('--no-browser',action='store_true',help='Do not automatically open the default browser')
    parser.add_argument('--csv',help='Run an independent binary CSV benchmark')
    parser.add_argument('--target',default='label',help='0/1 target column in CSV')
    parser.add_argument('--domain',help='Optional domain column to hold out')
    parser.add_argument('--train-domain',help='Optional specific domain to train on')
    parser.add_argument('--ollama',help='Optional locally installed Ollama model name')
    parser.add_argument('--items',type=int,default=20,help='Number of arithmetic tasks for Ollama')
    args=parser.parse_args(argv)
    root=Path(__file__).resolve().parent/'reports'
    if args.real_study:
        dsets=[v.strip() for v in args.datasets.split(',') if v.strip()]
        for path in args.real_csv:
            imported=register_custom_csv(path,args.real_target,args.real_domain,args.real_base)
            dsets.append(imported)
        print('Prospective power assumptions (NOT confirmatory for development data):',power_plan(),flush=True)
        real=run_real_study(args.seeds,args.seed,dsets,args.cap,progress=lambda p:print('\r'+p['detail'][:72],end='',flush=True) if p['completed']%5==0 or p['completed']==p['total'] else None)
        dest=save_real_study(real,root)
        print('\nReport:',str(Path(dest['directory'])/'REPORT.md'))
        print('Run archive:',dest['archive'])
        for summ in real['forecast']['summary']:
            print('Predictions:',summ)
        return 0
    if args.text_study:
        text=run_text_study(args.seeds or 20,args.seed,progress=lambda p:print('\r'+p['detail'][:75],end='',flush=True) if p['completed']%5==0 else None)
        saved=save_text(text,root)
        print('\nText study report:',saved['directory']);return 0
    if args.local_benchmark:
        if not args.model:parser.error('--model <installed Ollama model> is required for --local-benchmark')
        data=run_local_benchmark(args.model,args.local_benchmark,args.items)
        saved=save_local(data,root)
        print('Pretrained model report:',saved['directory']);print('Accuracy:',data['summary']);return 0
    if args.run or args.csv:
        if args.csv:out=csv_suite(args.csv,args.target,args.domain,args.train_domain,args.seed)
        else:
            def report(p):
                if p['completed']%20==0 or p['completed']==p['total']:
                    print(f"\r{p['completed']}/{p['total']} observations · {p['detail'][:42]:42}",end='',flush=True)
            out=run_suite(args.preset,args.seed,report)
        result=save_run(out,root)
        print('\nReport: '+str(Path(result['directory'])/'REPORT.md'))
        print('Findings: '+str(Path(result['directory'])/'findings.json'))
        for f in result['findings']:
            print(f"{f['id']}: {f['status']} (effect {f['effect']:+.3f})")
        return 0
    if args.ollama:
        result=ollama_suite(args.ollama,args.items,args.seed)
        root.mkdir(exist_ok=True)
        target=root/'ollama_cli.json';target.write_text(json.dumps(result,indent=2))
        print('Local model accuracy:',result['accuracy'],'Attempts:',result['attempted'],'Saved:',target)
        return 0
    serve(port=args.port,open_browser=not args.no_browser)
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except Exception as exc:
        print(f'Error: {type(exc).__name__}: {exc}',file=sys.stderr)
        sys.exit(1)
