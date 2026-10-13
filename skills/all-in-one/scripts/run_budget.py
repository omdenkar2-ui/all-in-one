"""Reserve bounded backend orchestration work; model usage is caller-observed.

This journal enforces its recorded dispatch/repair counters and elapsed-time
limit. It cannot intercept model calls or attest provider billing/usage.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import sys
import time

spec = importlib.util.spec_from_file_location('_aio_plan_budget', Path(__file__).with_name('plan_gate.py'))
plan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plan)
SCOPE = 'Journal counters/time only; observed model tokens are a soft target, not a provider billing cap.'
PROFILES = {
    'lean': {'implementer': 1, 'reviewer': 1, 'reviewer_per_unit': 1, 'repair_wave': 2, 'wall_seconds': 300, 'token_target': 6000},
    'balanced': {'implementer': 3, 'reviewer': 3, 'reviewer_per_unit': 2, 'repair_wave': 2, 'wall_seconds': 600, 'token_target': 12000},
    'thorough': {'implementer': 4, 'reviewer': 6, 'reviewer_per_unit': 2, 'repair_wave': 2, 'wall_seconds': 900, 'token_target': 24000},
}

def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_:.\-]{1,128}', value):
        raise ValueError('invalid event/unit identifier')

def nonnegative(value):
    if type(value) is not int or value < 0:
        raise ValueError('usage must be a nonnegative integer')

def summary(document, now=None):
    usage = {kind: 0 for kind in ('implementer', 'reviewer', 'repair_wave', 'tokens')}
    per_unit = {}
    events = document['events']
    if not isinstance(events, dict) or len(events) > 128:
        raise ValueError('invalid or excessive event journal')
    for key, event in events.items():
        identifier(key)
        if not isinstance(event, dict): raise ValueError('event must be an object')
        kind = event.get('kind')
        if kind == 'usage':
            if set(event) != {'kind', 'input_tokens', 'cached_input_tokens', 'output_tokens'}:
                raise ValueError('invalid usage event')
            for name in ('input_tokens', 'cached_input_tokens', 'output_tokens'): nonnegative(event[name])
            if event['cached_input_tokens'] > event['input_tokens']:
                raise ValueError('cached input exceeds total input')
            # Count all reported input plus output; cache discount is not a billing assertion.
            usage['tokens'] += event['input_tokens'] + event['output_tokens']
        elif kind in ('implementer', 'reviewer', 'repair_wave'):
            if set(event) == {'kind', 'unit'}:
                identifier(event['unit'])
                units = [event['unit']]
            elif kind == 'reviewer' and set(event) == {'kind', 'units'}:
                units = event['units']
                if not isinstance(units, list) or not 1 <= len(units) <= 32:
                    raise ValueError('invalid reviewer coverage')
                for unit in units: identifier(unit)
                if len(set(units)) != len(units): raise ValueError('duplicate reviewer coverage')
            else: raise ValueError('invalid reservation event')
            usage[kind] += 1
            if kind == 'reviewer':
                for unit in units: per_unit[unit] = per_unit.get(unit, 0) + 1
        else: raise ValueError('unknown event kind')
    caps = PROFILES[document['profile']]
    elapsed = max(0, (time.time() if now is None else now) - document['started_at'])
    reasons = []
    for kind in ('implementer', 'reviewer', 'repair_wave'):
        if usage[kind] > caps[kind]: reasons.append(kind + ' dispatch limit exceeded')
    if any(count > caps['reviewer_per_unit'] for count in per_unit.values()):
        reasons.append('unit reviewer limit exceeded')
    if elapsed >= caps['wall_seconds']: reasons.append('wall-time budget exhausted')
    if usage['tokens'] >= caps['token_target']: reasons.append('observed token target reached')
    return {'allowed': not reasons, 'reasons': reasons, 'profile': document['profile'],
            'caps': caps, 'usage': usage, 'reviewers_by_unit': per_unit, 'elapsed_seconds': elapsed, 'scope': SCOPE}

def validate(document):
    if not isinstance(document, dict) or set(document) != {'schema_version', 'profile', 'started_at', 'events'}:
        raise ValueError('invalid budget journal fields')
    if type(document['schema_version']) is not int or document['schema_version'] != 1 or document['profile'] not in PROFILES:
        raise ValueError('unsupported budget journal')
    started = document['started_at']
    if type(started) not in (int, float) or not 0 < started <= time.time() + 1:
        raise ValueError('invalid start time')
    summary(document)

def reserve(document, event_id, kind, unit):
    validate(document)
    identifier(event_id)
    if kind not in ('implementer', 'reviewer', 'repair_wave'): raise ValueError('unknown reservation kind')
    if isinstance(unit, list):
        if kind != 'reviewer' or not 1 <= len(unit) <= 32:
            raise ValueError('multiple units require a bounded reviewer scope')
        for covered in unit: identifier(covered)
        if len(set(unit)) != len(unit): raise ValueError('duplicate reviewer coverage')
        event = {'kind': kind, 'units': sorted(unit)}
    else:
        identifier(unit)
        event = {'kind': kind, 'units': [unit]} if kind == 'reviewer' else {'kind': kind, 'unit': unit}
    prior = document['events'].get(event_id)
    if prior is not None:
        if kind == 'reviewer' and prior.get('kind') == 'reviewer' and 'unit' in prior:
            prior = {'kind': 'reviewer', 'units': [prior['unit']]}
        if prior != event: raise ValueError('event identity conflict')
        return summary(document)
    before = summary(document)
    if not before['allowed']: return before
    # Check the next reservation before mutating the accepted journal.
    candidate = {**document, 'events': {**document['events'], event_id: event}}
    after = summary(candidate)
    if after['allowed']:
        document['events'][event_id] = event
        return after
    return {**before, 'allowed': False, 'reasons': after['reasons'],
            'proposed_usage': after['usage'], 'proposed_reviewers_by_unit': after['reviewers_by_unit']}

def record_usage(document, event_id, input_tokens, cached_input_tokens, output_tokens):
    validate(document); identifier(event_id)
    event = {'kind':'usage', 'input_tokens':input_tokens, 'cached_input_tokens':cached_input_tokens, 'output_tokens':output_tokens}
    candidate = {**document, 'events': {**document['events'], event_id:event}}
    summary(candidate)
    if event_id in document['events'] and document['events'][event_id] != event:
        raise ValueError('event identity conflict')
    document['events'][event_id] = event
    return summary(document)

def assess(document, estimated_tokens, closing=False):
    """Read-only admission estimate; does not reserve or attest provider tokens."""
    validate(document)
    if type(estimated_tokens) is not int or estimated_tokens <= 0:
        raise ValueError('estimated tokens must be a positive integer')
    if type(closing) is not bool:
        raise ValueError('closing must be a boolean')
    result = summary(document)
    target = result['caps']['token_target']
    reserve_tokens = target // 5
    available = max(0, target - result['usage']['tokens'] - (0 if closing else reserve_tokens))
    reasons = list(result['reasons'])
    if estimated_tokens > available:
        reasons.append('estimated next work would consume closing reserve' if not closing
                       else 'estimated closing work exceeds remaining soft target')
    return {**result, 'allowed': not reasons, 'reasons': reasons,
            'estimated_next_tokens': estimated_tokens,
            'closing_reserve_tokens': reserve_tokens,
            'available_for_next_work': available, 'closing': closing,
            'token_meter': 'caller-reported-partial' if any(e['kind'] == 'usage'
                          for e in document['events'].values()) else 'unavailable',
            'planning_only': True}

def atomic_write(state, document):
    temporary = state.with_name(state.name + '.pending')
    identity = None
    try:
        # Refuse a pre-existing file. Cleanup is limited to our newly created inode.
        with temporary.open('x', encoding='utf-8') as stream:
            owned = os.fstat(stream.fileno())
            identity = (owned.st_dev, owned.st_ino)
            json.dump(document, stream, indent=2)
        for attempt in range(5):
            try:
                os.replace(temporary, state)
                return
            except PermissionError:
                if attempt == 4: raise
                time.sleep(0.02)
    finally:
        if identity is not None:
            try:
                remaining = temporary.stat(follow_symlinks=False)
                if stat.S_ISREG(remaining.st_mode) and (remaining.st_dev, remaining.st_ino) == identity:
                    temporary.unlink()
            except FileNotFoundError:
                pass

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('init', 'check', 'reserve', 'usage', 'assess'))
    parser.add_argument('state')
    parser.add_argument('--root', required=True)
    parser.add_argument('--profile', choices=tuple(PROFILES), default='thorough')
    parser.add_argument('--event-id'); parser.add_argument('--unit', action='append')
    parser.add_argument('--kind', choices=('implementer','reviewer','repair_wave'))
    parser.add_argument('--input-tokens', type=int, default=0)
    parser.add_argument('--cached-input-tokens', type=int, default=0)
    parser.add_argument('--output-tokens', type=int, default=0)
    parser.add_argument('--estimated-tokens', type=int)
    parser.add_argument('--closing', action='store_true')
    args = parser.parse_args()
    lock_fd = None
    lock = None
    try:
        root = Path(args.root).resolve()
        validator = plan._PlanValidation(root)
        state = validator.owned_path(args.state, 'state')
        if validator.errors or state is None: raise ValueError('; '.join(validator.errors))
        if args.operation not in ('check', 'assess'):
            state.parent.mkdir(parents=True, exist_ok=True)
            lock = state.with_name(state.name + '.lock')
            lock_fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        if args.operation == 'init':
            document = {'schema_version':1, 'profile':args.profile, 'started_at':time.time(), 'events':{}}
            # Do not reset a consumed budget on resume.
            with state.open('x', encoding='utf-8') as stream: json.dump(document, stream, indent=2)
        else:
            document = json.loads(state.read_text(encoding='utf-8'), object_pairs_hook=plan._core._unique_json_object)
            validate(document)
        if args.operation == 'reserve':
            units = args.unit or ['RUN']
            result = reserve(document, args.event_id, args.kind, units[0] if len(units) == 1 else units)
        elif args.operation == 'usage':
            result = record_usage(document, args.event_id, args.input_tokens, args.cached_input_tokens, args.output_tokens)
        elif args.operation == 'assess':
            result = assess(document, args.estimated_tokens, closing=args.closing)
        else: result = summary(document)
        if args.operation in ('reserve','usage'):
            atomic_write(state, document)
        print(json.dumps(result))
        return 0 if result['allowed'] else 1
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({'allowed':False,'reasons':[str(error)],'scope':SCOPE}))
        return 1
    finally:
        if lock_fd is not None:
            os.close(lock_fd)
            lock.unlink()

if __name__ == '__main__': sys.exit(main())
