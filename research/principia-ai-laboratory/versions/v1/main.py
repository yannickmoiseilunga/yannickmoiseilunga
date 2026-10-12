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


def main(argv=None):
    parser=argparse.ArgumentParser(description='Run reproducible artificial intelligence corollary experiments, without Python packages or API keys.')
    parser.add_argument('--run',action='store_true',help='Run synthetic suite in CLI instead of opening dashboard')
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
