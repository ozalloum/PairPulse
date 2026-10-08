"""Run the declared release validation; retain individual successes and failures.

Install PairPulse and requirements-validation.txt first. Run from any directory:
python scripts/validate_release.py --output validation --workers 4
No archived result file is overwritten. QuTiP is a validation-only dependency.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.metadata as im
import json
import math
import os
from pathlib import Path
import platform
import sys
import time
import subprocess
from datetime import datetime, timezone
import numpy as np
from scipy.special import erf
from pairpulse import SauterPulse, PulseTrain, solve_dirac_mode, solve_qke_mode, sauter_exact_occupation

PROTOCOL = {
    "version": 1,
    "occupation_absolute_tolerance": 1e-10,
    "resolved_occupation_floor": 1e-10,
    "resolved_relative_tolerance": 1e-5,
    "yield_relative_tolerance": 1e-4,
    "interpretation": "Empirical checks, not certified error bounds. Refined numerical runs are not exact.",
    "integration": {"tail": 20, "rtol": [2e-8,2e-10,2e-12], "atol_over_rtol": .01,
                    "step_coefficients": [.18,.09,.045], "momenta": [-1.5,-.75,0,.75,1.5]},
    "window": {"tails": [12,16,20], "rtol": 2e-12, "coefficient": .045},
    "parameters": {"amplitudes": [.1,.3,.8], "durations": [.5,2,5],
                   "momenta": "13 equally spaced in +/- max(1.5,E0*tau+2/tau)",
                   "tail":20,"rtol":2e-12,"coefficient":.09},
    "quadrature": {"single_bounds": [1.5,3,4.5], "double_bounds":[1.8,3.6,5.4],
                   "fixed_domain_counts":[41,81,161],"extended_counts":[321,481],
                   "tail":20,"rtol":2e-12,"coefficient":.09},
    "qutip": {"method":"vern9", "normalize_output":False,"tail":20,"rtol":2e-12,
              "coefficient":.09,"modes_per_case":41},
    "custom_pulse": {"E":"0.3 exp(-(t/2)^2)","A":"-0.3 sqrt(pi) erf(t/2)",
                     "momenta":[-1.5,-.75,0,.75,1.5],"tails":[6,8],"coefficients":[.09,.045]},
}

class GaussianPulse:
    def field(self,t): return .3*np.exp(-(np.asarray(t)/2)**2)
    def potential(self,t): return -.3*np.sqrt(np.pi)*erf(np.asarray(t)/2)
    def time_window(self,tail_factor=12): return -2*tail_factor,2*tail_factor

def pulse_for(case,e0=.3,tau=2):
    if case=="single": return SauterPulse(e0,tau)
    if case=="double": return PulseTrain([SauterPulse(.3,1.1,-3.5),SauterPulse(.3,1.1,3.5)])
    return GaussianPulse()

def qutip_mode(p,pulse,tail,rtol,coef):
    import qutip as qt
    t0,tf=pulse.time_window(tail)
    # Eigensystems and time evolution are built in QuTiP, without PairPulse's
    # RHS or eigenvector helper. The prescribed analytic potential is shared.
    h0=qt.sigmaz()+(p-float(pulse.potential(t0)))*qt.sigmax()
    hf=qt.sigmaz()+(p-float(pulse.potential(tf)))*qt.sigmax()
    initial=h0.eigenstates()[1][0]
    positive=hf.eigenstates()[1][-1]
    samples=np.linspace(t0,tf,257)
    cap=coef/np.sqrt(1+np.max(np.abs(p-pulse.potential(samples)))**2)
    h=[qt.sigmaz()+p*qt.sigmax(),[qt.sigmax(),lambda t: -float(pulse.potential(t))]]
    sol=qt.sesolve(h,initial,[t0,tf],options={"method":"vern9","rtol":rtol,
        "atol":rtol/100,"max_step":cap,"nsteps":1000000,
        "normalize_output":False,"store_states":True,"progress_bar":""})
    state=sol.states[-1]
    return float(abs(positive.overlap(state))**2),float(abs(state.norm()**2-1)),-1,(t0,tf)

def run_job(job):
    row=dict(job); start=time.perf_counter()
    pulse=pulse_for(job["case"],job["E0"],job["tau"])
    try:
        args=dict(tail_factor=job["tail"],rtol=job["rtol"],atol=job["rtol"]/100,
                  max_step_coefficient=job["coefficient"])
        if job["method"]=="qutip_vern9":
            value,diag,nfev,span=qutip_mode(job["p"],pulse,job["tail"],job["rtol"],job["coefficient"])
        else:
            fun=solve_dirac_mode if job["method"]=="dirac" else solve_qke_mode
            result=fun(job["p"],pulse,**args)
            value,diag,nfev,span=result.occupation,result.diagnostic,result.nfev,result.time_span
        exact=sauter_exact_occupation(job["p"],pulse) if job["case"]=="single" else None
        error=abs(value-exact) if exact is not None else None
        relative=error/exact if exact is not None and exact>=PROTOCOL["resolved_occupation_floor"] else None
        row.update(occupation=value,diagnostic=diag,nfev=nfev,t0=span[0],tf=span[1],exact=exact,
                   absolute_error=error,resolved_relative_error=relative,status="ok",failure="")
    except Exception as exc:
        row.update(status="failed",failure=f"{type(exc).__name__}: {exc}")
    row["wall_seconds"]=time.perf_counter()-start
    return row

def jobs():
    out=[]
    def add(study,case,p,method,tail=20,rtol=2e-12,coef=.09,e0=.3,tau=2):
        out.append(dict(study=study,case=case,p=float(p),method=method,tail=tail,
                        rtol=rtol,coefficient=coef,E0=e0,tau=tau))
    for case in ["single","double"]:
        for p in PROTOCOL["integration"]["momenta"]:
            for method in ["dirac","qke"]:
                for tol in PROTOCOL["integration"]["rtol"]:
                    for coef in [.18,.09,.045]: add("integration",case,p,method,rtol=tol,coef=coef)
                for tail in [12,16,20]: add("window",case,p,method,tail=tail,coef=.045)
        bound=1.5 if case=="single" else 1.8
        for p in np.linspace(-bound,bound,41):
            for method in ["dirac","qke","qutip_vern9"]: add("software",case,p,method)
        # Entire coarse grid also checks integrated effects of endpoint and cap changes.
        for p in np.linspace(-bound,bound,81):
            for tail,coef in [(12,.09),(16,.09),(20,.045)]:
                add("yield_controls",case,p,"qke",tail=tail,coef=coef)
    for e0 in [.1,.3,.8]:
        for tau in [.5,2,5]:
            bound=max(1.5,e0*tau+2/tau)
            for p in np.linspace(-bound,bound,13):
                for method in ["dirac","qke"]: add("parameter", "single",p,method,e0=e0,tau=tau)
    # A nested grid permits exact subsampling at unchanged nodes; no assumed symmetry.
    for case,bound in [("single",4.5),("double",5.4)]:
        for p in np.linspace(-bound,bound,481): add("quadrature",case,p,"qke")
    for p in [-1.5,-.75,0,.75,1.5]:
        for tail in [6,8]:
            for coef in [.09,.045]:
                for method in ["dirac","qke","qutip_vern9"]:
                    add("custom", "gaussian",p,method,tail=tail,coef=coef)
    return out

def write_csv(path,rows):
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(rows)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path)
    ap.add_argument("--worker-input",type=Path);ap.add_argument("--worker-output",type=Path)
    ap.add_argument("--workers",type=int,default=4);args=ap.parse_args()
    if args.worker_input:
        rows=[]
        for job in json.loads(args.worker_input.read_text()):
            rows.append(run_job(job))
            if len(rows)%25==0: write_csv(args.worker_output,rows)
        write_csv(args.worker_output,rows)
        return
    if args.output is None or args.workers<1: ap.error("--output and positive --workers are required")
    args.output.mkdir(parents=True,exist_ok=True)
    if (args.output/"mode_results.csv").exists():
        raise SystemExit("Use a fresh output directory to preserve existing evidence.")
    protocol=dict(PROTOCOL,declared_at_utc=datetime.now(timezone.utc).isoformat())
    (args.output/"protocol.json").write_text(json.dumps(protocol,indent=2)+"\n")
    todo=jobs();rows=[];started=time.perf_counter()
    metadata={"python":sys.version,"platform":platform.platform(),"processor":platform.processor(),
              "cpu_count":os.cpu_count(),"workers":args.workers,"command":sys.argv,
              "packages":{p:im.version(p) for p in ["pairpulse","numpy","scipy","matplotlib","qutip","nbclient","ipykernel"]},
              "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "started_at_utc":datetime.now(timezone.utc).isoformat(),"planned_jobs":len(todo)}
    (args.output/"environment.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print(f"Declared protocol and {len(todo)} mode evaluations",flush=True)
    # File-backed subprocess shards also work where Windows named pipes are
    # unavailable. Each evaluation is independent; this is not a timing benchmark.
    worker_dir=args.output/"workers";worker_dir.mkdir(exist_ok=True)
    processes=[];handles=[]
    for index in range(args.workers):
        inp=worker_dir/f"jobs_{index}.json";out=worker_dir/f"results_{index}.csv"
        inp.write_text(json.dumps(todo[index::args.workers]))
        log=(worker_dir/f"worker_{index}.log").open("w");handles.append(log)
        processes.append(subprocess.Popen([sys.executable,str(Path(__file__).resolve()),
            "--worker-input",str(inp.resolve()),"--worker-output",str(out.resolve())],stdout=log,stderr=log))
    while any(p.poll() is None for p in processes):
        time.sleep(10)
        count=sum(max(0,len(p.read_text().splitlines())-1) for p in worker_dir.glob("results_*.csv"))
        print(f"Saved {count}/{len(todo)}; elapsed {time.perf_counter()-started:.1f}s",flush=True)
    for h in handles: h.close()
    if any(p.returncode for p in processes): raise RuntimeError("Worker failed; inspect retained worker logs")
    for index in range(args.workers):
        with (worker_dir/f"results_{index}.csv").open(newline="") as f: rows.extend(csv.DictReader(f))
    write_csv(args.output/"mode_results.csv",rows)
    metadata.update(elapsed_seconds=time.perf_counter()-started,completed_jobs=len(rows),
                    failures=sum(r["status"]!="ok" for r in rows))
    (args.output/"environment.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print(json.dumps(metadata,indent=2),flush=True)

if __name__=="__main__": main()
