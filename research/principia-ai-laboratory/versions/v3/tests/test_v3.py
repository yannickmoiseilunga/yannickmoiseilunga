"""V3 deterministic safety, algebra, provenance and measurement-separation tests."""
import unittest
import math
import csv
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from principia import transport_law as tl
from principia import real_study as v2


class TransportV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=tl.source_rows_from_v2()
    def test_frozen_source(self):
        self.assertEqual(len(self.source),1920)
        self.assertEqual(set(x['dataset'] for x in self.source),set(tl.RESEARCH_SOURCES))
    def test_itl_in_range(self):
        vals=tl.fits_and_predicts(self.source,self.source[:20]);self.assertTrue(all(0<=x<=1 for x in vals))
    def test_test_label_independence(self):
        rows=[dict(x) for x in self.source[:20]]
        a=tl.fits_and_predicts(self.source,rows)
        for r in rows:r['accuracy']='0.001';r['brier']='0.995'
        b=tl.fits_and_predicts(self.source,rows)
        self.assertEqual(a.tolist(),b.tolist())
    def test_missing_unseen_features(self):
        x=dict(self.source[0]);x['model']='gnb'
        self.assertEqual(tl.v2_features_with_unseen([x]).shape,(1,15))
    def test_impossibility_exact(self):
        r=tl.no_free_lunch_witness()
        self.assertAlmostEqual(r['world_one_accuracy']+r['world_two_accuracy'],1)
        self.assertAlmostEqual(r['minimax_absolute_error_lower_bound'],abs(r['world_one_accuracy']-r['world_two_accuracy'])/2)
    def test_seeds_are_minimum_20(self):
        self.assertEqual(tl.PROTOCOL['min_seeds'],20)
        with self.assertRaises(ValueError):tl.run(seeds=19)
    def test_unseen_data_sources(self):
        for name in tl.EXTERNAL_SOURCES:
            X,y,dom=tl.source_data(name)
            self.assertEqual(len(X),len(y));self.assertEqual(len(y),len(dom))
            self.assertEqual(set(y),{0,1});self.assertEqual(set(dom),{0,1})
    def test_nominal_modes(self):
        self.assertEqual(tl.REGIMES,['clean','label_noise','sensor_dropout'])
    def test_fitted_reference_rejects_unseen_labels(self):
        rows=[dict(x) for x in self.source[:6]]
        a,_,_=tl.previous_law(self.source,rows)
        for r in rows:r['accuracy']='0.001';r['brier']='0.995'
        b,_,_=tl.previous_law(self.source,rows)
        self.assertEqual(a.tolist(),b.tolist())
    def test_reproducible_probe(self):
        a=tl.make_rows('iris',42,which_models=['gnb'])
        b=tl.make_rows('iris',42,which_models=['gnb'])
        self.assertEqual(a,b)

if __name__=='__main__':unittest.main()
