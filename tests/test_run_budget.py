"""Meaningful backend orchestration budget failure/continuation checks."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

SCRIPT=Path(__file__).resolve().parents[1]/'skills/all-in-one/scripts/run_budget.py'
spec=importlib.util.spec_from_file_location('run_budget',SCRIPT)
B=importlib.util.module_from_spec(spec); spec.loader.exec_module(B)

class RunBudgetTests(unittest.TestCase):
    def document(self,profile='thorough'):
        return {'schema_version':1,'profile':profile,'started_at':time.time(),'events':{}}

    def test_default_thorough_bounded_profiles(self):
        value=B.summary(self.document())
        self.assertTrue(value['allowed']); self.assertEqual(6,value['caps']['reviewer'])
        self.assertEqual(24000,value['caps']['token_target'])

    def test_reviewer_fanout_is_reserved_before_exceeding(self):
        d=self.document()
        for i in range(6): self.assertTrue(B.reserve(d,str(i),'reviewer','U'+str(i))['allowed'])
        rejected=B.reserve(d,'excess','reviewer','U7')
        self.assertFalse(rejected['allowed'])
        self.assertEqual(6,rejected['usage']['reviewer'])
        self.assertEqual(7,rejected['proposed_usage']['reviewer'])
        self.assertNotIn('excess',d['events'])

    def test_per_unit_review_limit(self):
        d=self.document()
        self.assertTrue(B.reserve(d,'r1','reviewer','U1')['allowed'])
        self.assertTrue(B.reserve(d,'r2','reviewer','U1')['allowed'])
        self.assertFalse(B.reserve(d,'r3','reviewer','U1')['allowed'])

    def test_batched_review_counts_one_job_and_every_covered_unit(self):
        d=self.document()
        self.assertTrue(B.reserve(d,'batch','reviewer',['U2','U1'])['allowed'])
        self.assertTrue(B.reserve(d,'batch','reviewer',['U1','U2'])['allowed'])
        value=B.summary(d)
        self.assertEqual(1,value['usage']['reviewer'])
        self.assertEqual({'U1':1,'U2':1},value['reviewers_by_unit'])
        self.assertTrue(B.reserve(d,'fix','reviewer','U1')['allowed'])
        self.assertFalse(B.reserve(d,'another','reviewer',['U1','U2'])['allowed'])
        self.assertEqual(1,B.summary(d)['reviewers_by_unit']['U2'])

    def test_invalid_review_coverage_is_not_reserved(self):
        for kind,units in [('reviewer',[]),('reviewer',['U1','U1']),('implementer',['U1','U2']),('reviewer',['U1']*33)]:
            d=self.document()
            with self.subTest(kind=kind,units=units),self.assertRaises(ValueError):
                B.reserve(d,'event',kind,units)
            self.assertFalse(d['events'])

    def test_single_list_string_and_legacy_review_replay_equivalent(self):
        d=self.document()
        B.reserve(d,'r1','reviewer',['U1'])
        B.reserve(d,'r1','reviewer','U1')
        d['events']['legacy']={'kind':'reviewer','unit':'U2'}
        B.reserve(d,'legacy','reviewer',['U2'])
        self.assertEqual(2,B.summary(d)['usage']['reviewer'])

    def test_repair_waves_are_bounded(self):
        d=self.document()
        for i in range(2): self.assertTrue(B.reserve(d,str(i),'repair_wave','RUN')['allowed'])
        self.assertFalse(B.reserve(d,'more','repair_wave','RUN')['allowed'])

    def test_reservation_replay_does_not_double_charge(self):
        d=self.document()
        B.reserve(d,'r1','reviewer','U1'); B.reserve(d,'r1','reviewer','U1')
        self.assertEqual(1,B.summary(d)['usage']['reviewer'])
        with self.assertRaises(ValueError): B.reserve(d,'r1','reviewer','U2')

    def test_observed_tokens_stop_future_dispatch_without_reset(self):
        d=self.document()
        self.assertFalse(B.record_usage(d,'turn',22000,20000,2000)['allowed'])
        self.assertFalse(B.reserve(d,'r1','reviewer','U1')['allowed'])
        self.assertEqual(24000,B.summary(d)['usage']['tokens'])

    def test_usage_replay_and_conflict(self):
        d=self.document()
        B.record_usage(d,'t1',100,40,50); B.record_usage(d,'t1',100,40,50)
        self.assertEqual(150,B.summary(d)['usage']['tokens'])
        with self.assertRaises(ValueError): B.record_usage(d,'t1',101,40,50)

    def test_admission_preserves_closing_capacity_without_spending_tokens(self):
        d=self.document('balanced')
        B.record_usage(d,'t1',8000,0,500)
        original=copy.deepcopy(d)
        value=B.assess(d,1200)
        self.assertFalse(value['allowed'])
        self.assertEqual(2400,value['closing_reserve_tokens'])
        self.assertEqual(1100,value['available_for_next_work'])
        self.assertEqual(original,d)
        self.assertTrue(B.assess(d,1100)['allowed'])

    def test_closing_admission_can_use_reserve_but_cannot_exceed_target(self):
        d=self.document('lean'); B.record_usage(d,'t1',4500,0,0)
        self.assertFalse(B.assess(d,500)['allowed'])
        self.assertTrue(B.assess(d,500,closing=True)['allowed'])
        self.assertFalse(B.assess(d,1501,closing=True)['allowed'])

    def test_admission_unknown_metering_is_disclosed_and_cannot_erase_limits(self):
        d=self.document()
        value=B.assess(d,1000)
        self.assertEqual('unavailable',value['token_meter'])
        self.assertTrue(value['planning_only'])
        d['started_at']-=901
        self.assertFalse(B.assess(d,1,closing=True)['allowed'])

    def test_admission_invalid_estimates_are_rejected(self):
        for value in (None,False,-1,0,1.5,'100',float('inf')):
            with self.subTest(value=value),self.assertRaises(ValueError):
                B.assess(self.document(),value)

    def test_cli_admission_reads_without_mutating_journal(self):
        with tempfile.TemporaryDirectory(prefix='aio admission ') as temporary:
            root=Path(temporary)
            def run(*args):
                return subprocess.run([sys.executable,'-B','-X','utf8',str(SCRIPT),*args,'--root',str(root)],
                    capture_output=True,text=True,encoding='utf-8',timeout=10)
            self.assertEqual(0,run('init','run/budget.json','--profile','lean').returncode)
            state=root/'run/budget.json'; before=state.read_bytes()
            result=run('assess','run/budget.json','--estimated-tokens','4900')
            self.assertEqual(1,result.returncode)
            self.assertFalse(json.loads(result.stdout)['allowed'])
            self.assertEqual(before,state.read_bytes())
            self.assertEqual(0,run('assess','run/budget.json','--estimated-tokens','4900','--closing').returncode)

    def test_invalid_token_accounting(self):
        for values in ((True,0,0),(-1,0,0),(5,6,0),(0,0,1.5)):
            with self.subTest(values=values),self.assertRaises(ValueError):
                B.record_usage(self.document(),'t1',*values)

    def test_wall_exhaustion_blocks_dispatch(self):
        d=self.document();d['started_at']-=901
        self.assertFalse(B.reserve(d,'r1','reviewer','U1')['allowed'])
        self.assertFalse(d['events'])

    def test_journal_rejects_foreign_fields_and_unknown_actions(self):
        d=self.document();d['caps']={'reviewer':999}
        with self.assertRaises(ValueError):B.validate(d)
        d=self.document();d['events']['x']={'kind':'raise_budget','unit':'U1'}
        with self.assertRaises(ValueError):B.validate(d)

    def test_replace_failure_preserves_prior_state_and_cleans_owned_pending(self):
        with tempfile.TemporaryDirectory(prefix='budget replace ') as temporary:
            state=Path(temporary)/'budget.json'
            state.write_text('prior state',encoding='utf-8')
            with patch.object(B.os,'replace',side_effect=PermissionError('sharing violation')),patch.object(B.time,'sleep'):
                with self.assertRaises(PermissionError):B.atomic_write(state,self.document())
            self.assertEqual('prior state',state.read_text(encoding='utf-8'))
            self.assertFalse(state.with_name('budget.json.pending').exists())
            B.atomic_write(state,self.document())
            B.validate(json.loads(state.read_text(encoding='utf-8')))

    def test_replace_retries_transient_failure_and_preserves_foreign_pending(self):
        with tempfile.TemporaryDirectory(prefix='budget transient ') as temporary:
            state=Path(temporary)/'budget.json'
            replace=B.os.replace
            attempts=[]
            def intermittent(*args):
                attempts.append(1)
                if len(attempts)==1:raise PermissionError('sharing violation')
                return replace(*args)
            with patch.object(B.os,'replace',side_effect=intermittent),patch.object(B.time,'sleep'):
                B.atomic_write(state,self.document())
            self.assertEqual(2,len(attempts))
            pending=state.with_name('budget.json.pending');pending.write_text('foreign',encoding='utf-8')
            with self.assertRaises(FileExistsError):B.atomic_write(state,self.document())
            self.assertEqual('foreign',pending.read_text(encoding='utf-8'))
    def test_cli_recovery_keeps_budget_and_refuses_reset(self):
        with tempfile.TemporaryDirectory(prefix='aio budget ') as temporary:
            root=Path(temporary)
            def run(*args):
                return subprocess.run([sys.executable,'-B','-X','utf8',str(SCRIPT),*args,'--root',str(root)],
                    capture_output=True,text=True,encoding='utf-8',timeout=10)
            self.assertEqual(0,run('init','run/budget.json').returncode)
            self.assertEqual(0,run('reserve','run/budget.json','--event-id','r1','--kind','reviewer','--unit','U1').returncode)
            self.assertEqual(1,run('init','run/budget.json').returncode)
            resumed=json.loads(run('check','run/budget.json').stdout)
            self.assertEqual(1,resumed['usage']['reviewer'])
            self.assertEqual(1,run('init','../escape.json').returncode)
            self.assertEqual(1,run('init','.git/config').returncode)

if __name__=='__main__':unittest.main()
