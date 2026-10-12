import csv
import json
import math
import tempfile
import unittest
from pathlib import Path
from principia.worlds import analytic_bayes,sample
from principia.experiments import run_suite,_active_sensor,_arithmetic,_control,PRESETS
from principia.models import make_model
from principia.metrics import evaluate
from principia.reporting import save_run,compile_findings
from principia.prediction import cross_condition_predictions
from principia.external import csv_suite

class TestSyntheticScience(unittest.TestCase):
    def test_exact_blind_bound(self):
        q=analytic_bayes('blind')
        self.assertAlmostEqual(q['bayes_accuracy'],.5)
        self.assertAlmostEqual(q['mutual_information_bits'],0)
    def test_parity_carries_one_bit(self):
        q=analytic_bayes('parity')
        self.assertAlmostEqual(q['bayes_accuracy'],1)
        self.assertAlmostEqual(q['mutual_information_bits'],1)
        self.assertAlmostEqual(analytic_bayes('parity',feature_mask=[0])['mutual_information_bits'],0)
    def test_evidence_information_monotonic(self):
        a=analytic_bayes('sensors',feature_mask=[2]);b=analytic_bayes('sensors')
        self.assertGreaterEqual(b['mutual_information_bits']+1e-9,a['mutual_information_bits'])
        self.assertGreaterEqual(b['bayes_accuracy']+1e-9,a['bayes_accuracy'])
    def test_models_fit_small_task(self):
        x=[[0,0],[0,1],[1,0],[1,1]]*28;y=[0,1,1,0]*28
        weak=make_model('linear',True).fit(x,y,42)
        strong=make_model('interactions',True).fit(x,y,42)
        self.assertGreater(sum((strong.predict(t)>=.5)==v for t,v in zip(x,y)),100)
    def test_calibration_scores(self):
        m=evaluate([0,1,0,1],[.01,.99,.2,.8])
        self.assertEqual(m['accuracy'],1)
        self.assertLess(m['brier'],.05)
        self.assertLess(m['selective_risk_80'],.01)
    def test_paired_active_interventions(self):
        a=_active_sensor(42,1000,'no_tool');b=_active_sensor(42,1000,'adaptive')
        self.assertGreater(b[0],a[0]);self.assertEqual(a[1],0)
    def test_paired_candidates(self):
        a=_arithmetic(42,300,1,'first')
        b=_arithmetic(42,300,16,'process')
        self.assertGreater(b[0],a[0])
    def test_feedback(self):
        a=_control(42,600,'open_loop');b=_control(42,600,'closed_loop')
        self.assertGreater(b[0],a[0])
    def test_determinism_and_separation(self):
        a=run_suite('quick',123,include_predictions=False)
        b=run_suite('quick',123,include_predictions=False)
        vals=lambda r:[(x['experiment'],x['model'],x['seed'],x['domain'],x['accuracy']) for x in r['rows']]
        self.assertEqual(vals(a),vals(b))
        self.assertIn('weak_to_strong',{x['experiment'] for x in a['rows']})
        self.assertEqual(len(compile_findings(a)),12)
    def test_report_and_forecasts(self):
        with tempfile.TemporaryDirectory() as d:
            r=run_suite('quick',7,include_predictions=True)
            result=save_run(r,d)
            folder=Path(result['directory'])
            self.assertTrue((folder/'REPORT.md').is_file())
            self.assertTrue((folder/'predictions.csv').is_file())
            self.assertTrue((folder/'law_forecasts.csv').is_file())
            self.assertGreater(json.loads((folder/'law_validation.json').read_text())['n_conditions'],3)
            self.assertGreater(len((folder/'predictions.csv').read_text().splitlines()),100)
            self.assertEqual(len(r['hypotheses']),12)
    def test_csv_independent_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'toy.csv'
            with path.open('w',newline='') as f:
                w=csv.writer(f);w.writerow(['s','noise','label','region'])
                for i in range(100):w.writerow([int(i%2),int(i%3==0),int(i%2),'north' if i<60 else 'south'])
            r=csv_suite(path,'label','region','north',seeds=1)
            self.assertEqual(len(r['rows']),4)
            self.assertTrue(all(x['domain']=='other_domains_v_north' for x in r['rows']))
            self.assertTrue(all(x['n_train']==60 for x in r['rows']))

if __name__=='__main__':unittest.main()
