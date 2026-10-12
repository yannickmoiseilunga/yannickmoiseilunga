"""Run: python -m unittest discover -s tests -v (includes V1 and V2)."""
import csv
import json
from pathlib import Path
import tempfile
import unittest

from principia.real_study import (power_plan,CATALOG,PROTOCOL,run_real_study,
    dataset_load,make_splits,train_info_proxy,law_forecast,register_custom_csv,
    save_real_study,require_sklearn)
from principia.local_benchmark import canonical,clean_record


class V2Checks(unittest.TestCase):
    def test_preregistered_minimum_and_power(self):
        p=power_plan()
        self.assertGreaterEqual(p['chosen_seeds'],20)
        self.assertGreater(p['alpha_family'],p['alpha_per_comparison'])
        self.assertEqual(len(PROTOCOL['primary_hypotheses']),4)

    def test_bundled_real_sources_are_distinct_and_binary(self):
        fingerprints=set()
        for name in CATALOG:
            X,y,dom,metadata=dataset_load(name)
            self.assertEqual(len(X),len(y));self.assertEqual(len(X),len(dom))
            self.assertEqual(set(y),{0,1})
            self.assertEqual(set(dom),{0,1})
            self.assertNotIn(metadata['sha256_values'],fingerprints)
            fingerprints.add(metadata['sha256_values'])

    def test_disjoint_domains(self):
        import numpy as np
        X,y,d,info=dataset_load('digits')
        a,b,c=make_splits(X,y,d,42,500)
        self.assertFalse(set(a)&set(b))
        self.assertFalse(set(a)&set(c))
        self.assertFalse(set(b)&set(c))
        self.assertTrue(np.all(d[a]==0))
        self.assertTrue(np.all(d[b]==0))
        self.assertTrue(np.all(d[c]==1))

    def test_train_only_diagnostic_excludes_test_labels(self):
        X,y,d,info=dataset_load('breast_cancer')
        train,iid,ood=make_splits(X,y,d,33,300)
        p1=train_info_proxy(X,y,train,33)
        y2=y.copy();y2[iid]=1-y2[iid];y2[ood]=1-y2[ood]
        p2=train_info_proxy(X,y2,train,33)
        self.assertEqual(p1,p2)

    def test_small_study_all_three_holdouts_and_negatives(self):
        run=run_real_study(seeds=2,master_seed=19,datasets=['breast_cancer','digits'],cap=350)
        self.assertEqual(len(run['failures']),0)
        self.assertEqual(len(run['rows']),2*2*4*3*2)
        self.assertEqual({r['test_type'] for r in run['forecast']['summary']},
            {'unseen_dataset','unseen_architecture','unseen_both'})
        self.assertEqual(len(run['hypotheses']),4)
        self.assertFalse(run['settings']['confirmatory_seed_count_met'])
        self.assertEqual(run['settings']['phase'],'exploratory_development')
        self.assertTrue(any(r['intervention']=='label_noise' for r in run['rows']))

    def test_outside_heldout_accuracy_does_not_influence_its_prediction(self):
        result=run_real_study(seeds=2,master_seed=123,datasets=['wine','digits'],cap=350)
        original=result['forecast']['predictions']
        rows=[dict(r) for r in result['rows']]
        # Changing ONLY the final test outcomes of one heldout ARCHITECTURE
        # cannot change the law's predicted values for that architecture.
        for r in rows:
            if r['model']=='tree':r['accuracy']=1-r['accuracy']
        altered=law_forecast(rows)['predictions']
        first=[p['predicted'] for p in original if p['test_type']=='unseen_architecture' and p['held_architecture']=='tree']
        second=[p['predicted'] for p in altered if p['test_type']=='unseen_architecture' and p['held_architecture']=='tree']
        self.assertEqual(len(first),len(second))
        for x,y in zip(first,second):self.assertAlmostEqual(x,y,places=11)

    def test_csv_site_split_preserved(self):
        import numpy as np
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'site.csv'
            with p.open('w',newline='') as f:
                w=csv.writer(f);w.writerow(['x','z','label','site'])
                for i in range(180):w.writerow([i%9,i%11,int(i%4==0),'plant_A' if i<100 else 'plant_B'])
            name=register_custom_csv(p,'label','site','plant_A')
            X,y,domain,details=dataset_load(name)
            self.assertEqual(details['training_domain'],'plant_A')
            self.assertEqual(sum(domain==1),80)
            self.assertEqual(details['domain_definition'],'user-supplied domain label; no test labels used in building domain')

    def test_reports_including_negative_predictions(self):
        a=run_real_study(seeds=2,master_seed=8,datasets=['wine','digits'],cap=300)
        with tempfile.TemporaryDirectory() as temp:
            saved=save_real_study(a,temp)
            root=Path(saved['directory'])
            for f in ('REPORT.md','law_predictions.csv','observations.csv',
                'PROTOCOL_FROZEN.json','excluded_runs.json','forecast_groups.json','dashboard.json'):
                self.assertTrue((root/f).exists(),f)
            report=(root/'REPORT.md').read_text()
            self.assertIn('exploratory',report)
            self.assertIn('Probe-only baseline',report)
            self.assertTrue(Path(saved['archive']).exists())

    def test_local_benchmark_scoring(self):
        self.assertEqual(canonical('3,000'),canonical('3000'))
        self.assertNotEqual(canonical('3 000'),canonical('3000'))
        self.assertEqual(clean_record({'question':'2+2','answer':4},1)['answer'],'4')
        with self.assertRaises(ValueError):clean_record({'question':'2+2'},1)


if __name__=='__main__':unittest.main()
