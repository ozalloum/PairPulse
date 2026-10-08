"""Derive compact tables from retained release-validation mode records."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from pairpulse import SauterPulse,sauter_exact_occupation,integrated_density

def save(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,default=Path('validation'));a=ap.parse_args()
    with (a.data/'mode_results.csv').open() as f: rows=list(csv.DictReader(f))
    failures=[r for r in rows if r['status']!='ok']
    for r in rows:
        if r['status']=='ok':
            for k in ('p','tail','rtol','coefficient','E0','tau','occupation','diagnostic','exact','absolute_error','resolved_relative_error'):
                r[k]=float(r[k]) if r.get(k) not in ('',None) else None
    def select(**kw): return [r for r in rows if r['status']=='ok' and all(r[k]==v for k,v in kw.items())]
    def worst(rs,k): return max((r[k] for r in rs if r[k] is not None),default=None)
    integration=[]
    for case in ('single','double'):
        for method in ('dirac','qke'):
            rs=select(study='integration',case=case,method=method)
            ref={r['p']:r['occupation'] for r in rs if r['rtol']==2e-12 and r['coefficient']==.045}
            for tol in (2e-8,2e-10,2e-12):
                for c in (.18,.09,.045):
                    part=[r for r in rs if r['rtol']==tol and r['coefficient']==c]
                    integration.append(dict(case=case,method=method,rtol=tol,coefficient=c,modes=len(part),
                        max_reference_difference=max(abs(r['occupation']-ref[r['p']]) for r in part),
                        max_exact_error=worst(part,'absolute_error'),max_diagnostic=worst(part,'diagnostic')))
    save(a.data/'integration_summary.csv',integration)
    windows=[]
    for case in ('single','double'):
        for method in ('dirac','qke'):
            rs=select(study='window',case=case,method=method)
            ref={r['p']:r['occupation'] for r in rs if r['tail']==20}
            for tail in (12,16,20):
                part=[r for r in rs if r['tail']==tail]
                windows.append(dict(case=case,method=method,tail=tail,max_reference_difference=max(abs(r['occupation']-ref[r['p']]) for r in part),max_exact_error=worst(part,'absolute_error')))
    save(a.data/'window_summary.csv',windows)
    params=[]
    for e in (.1,.3,.8):
        for t in (.5,2.,5.):
            rs=select(study='parameter',E0=e,tau=t)
            for method in ('dirac','qke'):
                part=[r for r in rs if r['method']==method]
                params.append(dict(E0=e,tau=t,method=method,modes=len(part),
                    pmax=max(abs(r['p']) for r in part),min_exact=min(r['exact'] for r in part),
                    max_exact=max(r['exact'] for r in part),max_absolute_error=worst(part,'absolute_error'),
                    resolved_modes=sum(r['resolved_relative_error'] is not None for r in part),
                    max_resolved_relative_error=worst(part,'resolved_relative_error'),
                    negative_occupations=sum(r['occupation']<0 for r in part),
                    out_of_bounds_beyond_1e_10=sum(r['occupation']<-1e-10 or r['occupation']>1+1e-10 for r in part),
                    max_diagnostic=worst(part,'diagnostic')))
    save(a.data/'parameter_summary.csv',params)
    software=[]
    for case in ('single','double'):
        rs=select(study='software',case=case)
        ref={r['p']:r['occupation'] for r in rs if r['method']=='qutip_vern9'}
        for method in ('dirac','qke','qutip_vern9'):
            part=[r for r in rs if r['method']==method]
            software.append(dict(case=case,method=method,modes=len(part),
                max_qutip_difference=max(abs(r['occupation']-ref[r['p']]) for r in part),
                max_exact_error=worst(part,'absolute_error'),max_diagnostic=worst(part,'diagnostic')))
    save(a.data/'software_summary.csv',software)
    quad=[];control=[]
    for case,base in [('single',1.5),('double',1.8)]:
        rs=sorted(select(study='quadrature',case=case),key=lambda r:r['p'])
        p=np.array([r['p'] for r in rs]);f=np.array([r['occupation'] for r in rs])
        for bound,n in [(base,41),(base,81),(base,161),(2*base,321),(3*base,481)]:
            target=np.linspace(-bound,bound,n)
            indices=[int(np.argmin(abs(p-x))) for x in target]
            assert np.max(abs(p[indices]-target))<1e-12
            num=integrated_density(target,f[indices])
            exact=integrated_density(target,[sauter_exact_occupation(x,SauterPulse(.3,2)) for x in target]) if case=='single' else None
            quad.append(dict(case=case,pmax=bound,points=n,spacing=2*bound/(n-1),numerical_density=num,exact_grid_density=exact,
                             ode_density_difference=abs(num-exact) if exact is not None else None))
        for tail,coef in [(12,.09),(16,.09),(20,.045)]:
            cr=sorted(select(study='yield_controls',case=case,tail=float(tail),coefficient=coef),key=lambda r:r['p'])
            density=integrated_density([r['p'] for r in cr],[r['occupation'] for r in cr])
            ref=next(r['numerical_density'] for r in quad if r['case']==case and r['points']==81)
            control.append(dict(case=case,tail=tail,coefficient=coef,points=81,density=density,relative_reference_difference=abs(density-ref)/abs(ref)))
    save(a.data/'quadrature_summary.csv',quad);save(a.data/'yield_control_summary.csv',control)
    custom=select(study='custom');customdiff=[]
    for p in [-1.5,-.75,0,.75,1.5]:
        r=[r for r in custom if r['p']==p];ref=next(v['occupation'] for v in r if v['tail']==8 and v['coefficient']==.045 and v['method']=='qutip_vern9')
        customdiff.extend(abs(v['occupation']-ref) for v in r)
    summary={'completed_evaluations':len(rows),'failed_evaluations':len(failures),
        'parameter_max_absolute_error':max(r['max_absolute_error'] for r in params),
        'parameter_max_resolved_relative_error':max(r['max_resolved_relative_error'] for r in params if r['max_resolved_relative_error'] is not None),
        'parameter_negative_occupations':sum(r['negative_occupations'] for r in params),
        'parameter_bound_violations':sum(r['out_of_bounds_beyond_1e_10'] for r in params),
        'integration_max_refinement_difference':max(r['max_reference_difference'] for r in integration),
        'software_max_difference':max(r['max_qutip_difference'] for r in software),
        'gaussian_max_difference_to_refined_qutip':max(customdiff),
        'yield_control_max_relative_difference':max(r['relative_reference_difference'] for r in control)}
    for case in ('single','double'):
        vals=[r for r in quad if r['case']==case]
        summary[case+'_fixed_grid_last_relative_change']=abs(vals[2]['numerical_density']-vals[1]['numerical_density'])/vals[2]['numerical_density']
        summary[case+'_last_domain_relative_change']=abs(vals[4]['numerical_density']-vals[3]['numerical_density'])/vals[4]['numerical_density']
        summary[case+'_final_density']=vals[4]['numerical_density']
    summary['criteria_passed']=(summary['failed_evaluations']==0 and summary['parameter_max_absolute_error']<1e-10
        and summary['parameter_max_resolved_relative_error']<1e-5 and summary['parameter_bound_violations']==0
        and summary['integration_max_refinement_difference']<1e-10 and summary['software_max_difference']<1e-10
        and all(summary[case+'_last_domain_relative_change']<1e-4 and summary[case+'_fixed_grid_last_relative_change']<1e-4 for case in ('single','double'))
        and summary['yield_control_max_relative_difference']<1e-4 and max(customdiff)<1e-10)
    (a.data/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
