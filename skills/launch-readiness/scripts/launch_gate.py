"""Check mobile readiness coverage and local evidence, not store/legal approval."""

import argparse
from datetime import date
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit


_CORE = Path(__file__).resolve().parents[2] / 'all-in-one/scripts/check_receipt.py'
_SPEC = importlib.util.spec_from_file_location('all_in_one_evidence_core', _CORE)
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

COMMON = frozenset(('release-build', 'core-flows', 'privacy-policy', 'data-inventory',
                    'permissions', 'security', 'store-metadata', 'review-access', 'legal-applicability'))
PLATFORM = {
    'ios': frozenset(('ios-review', 'ios-privacy', 'ios-release')),
    'android': frozenset(('android-google-audit', 'android-data-safety', 'android-release', 'android-testing')),
}
FEATURES = {'backend': 'backend-live', 'accounts': 'account-deletion', 'tracking': 'tracking',
            'payments': 'payments', 'ugc': 'ugc', 'children': 'children',
            'regulated_data': 'regulated-data', 'ai_generated_content': 'ai-content'}
SCOPE = ('Checks declared coverage, current-day policy records, digests and local evidence only; '
         'does not run tests, authenticate claims, validate legal advice or certify store approval.')


def required_checks(platforms, features):
    required = set(COMMON)
    for platform in platforms:
        required.update(PLATFORM.get(platform, ()))
    for feature, identifier in FEATURES.items():
        if features.get(feature) is True:
            required.add(identifier)
    if features.get('accounts') is True:
        if 'android' in platforms:
            required.add('android-web-deletion')
        if 'ios' in platforms:
            required.add('ios-account-deletion')
    return required


def hash_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def verify_hash(check, item, label):
    path = check.file(item.get('path'), label + '.path')
    digest = item.get('sha256')
    if not isinstance(digest, str) or not re.fullmatch(r'[a-fA-F0-9]{64}', digest):
        check.error(label + '.sha256 must be 64 hexadecimal characters')
    elif path:
        try:
            if hash_file(path) != digest.lower():
                check.error(label + '.sha256 differs from the current file')
        except OSError as error:
            check.error(label + ' cannot be read: ' + str(error))
    return path


def validate(report, root, as_of=None):
    try:
        workspace = Path(root).resolve(strict=True)
        if not workspace.is_dir():
            return ['root must be an existing workspace directory'], []
    except (TypeError, ValueError, OSError, RuntimeError) as error:
        return ['root cannot be resolved: ' + str(error)], []
    today = as_of or date.today()
    check = _MODULE._Validation(workspace)
    data = check.obj(report, 'report', ('schema_version', 'verdict', 'source', 'app',
                                      'policy_review', 'builds', 'checks', 'blockers'))
    if type(data.get('schema_version')) is not int or data.get('schema_version') != 1:
        check.error('schema_version must be integer 1')
    check.enum(data.get('verdict'), 'verdict', ('ready_for_submission', 'blocked', 'review_needed'))
    if data.get('verdict') != 'ready_for_submission':
        check.error('verdict must be ready_for_submission to pass the launch gate')
    source = check.obj(data.get('source'), 'source', ('path', 'sha256'))
    verify_hash(check, source, 'source')
    app = check.obj(data.get('app'), 'app', ('name', 'developer_entity', 'platforms', 'markets', 'features'))
    for key in ('name', 'developer_entity'):
        check.string(app.get(key), 'app.' + key)
    platforms = []
    seen_platforms = set()
    for index, platform in enumerate(check.seq(app.get('platforms'), 'app.platforms', nonempty=True)):
        if check.enum(platform, f'app.platforms[{index}]', ('ios', 'android')):
            if platform in seen_platforms:
                check.error('app.platforms contains duplicates')
            seen_platforms.add(platform)
            platforms.append(platform)
    for index, market in enumerate(check.seq(app.get('markets'), 'app.markets', nonempty=True)):
        check.string(market, f'app.markets[{index}]')
    features = check.obj(app.get('features'), 'app.features', tuple(FEATURES))
    for feature in FEATURES:
        if type(features.get(feature)) is not bool:
            check.error(f'app.features.{feature} must be an established boolean; unknown cannot support readiness')
    needed = sorted(required_checks(platforms, features))

    policy = check.obj(data.get('policy_review'), 'policy_review', ('checked_on', 'sources', 'evidence'))
    if policy.get('checked_on') != today.isoformat():
        check.error('policy_review.checked_on must match the actual audit day ' + today.isoformat())
    check.files(policy.get('evidence'), 'policy_review.evidence', nonempty=True)
    policy_paths = set()
    for index, url in enumerate(check.seq(policy.get('sources'), 'policy_review.sources', nonempty=True)):
        check.https(url, f'policy_review.sources[{index}]')
        if isinstance(url, str):
            try:
                parsed = urlsplit(url)
                policy_paths.add((parsed.hostname, parsed.path.rstrip('/')))
            except ValueError:
                pass
    official = []
    if 'ios' in platforms:
        official += [('developer.apple.com', '/app-store/review/guidelines'),
                     ('developer.apple.com', '/app-store/app-privacy-details')]
    if 'android' in platforms:
        official += [('support.google.com', '/googleplay/android-developer/answer/10144311'),
                     ('support.google.com', '/googleplay/android-developer/answer/10787469')]
        if features.get('accounts') is True:
            official += [('support.google.com', '/googleplay/android-developer/answer/13327111')]
    for reference in official:
        if reference not in policy_paths:
            check.error('Missing current official policy reference: https://' + ''.join(reference))

    build_platforms = set()
    for index, item in enumerate(check.seq(data.get('builds'), 'builds', nonempty=True)):
        label = f'builds[{index}]'
        build = check.obj(item, label, ('platform', 'path', 'sha256'))
        platform = build.get('platform')
        if check.enum(platform, label + '.platform', ('ios', 'android')):
            if platform in build_platforms:
                check.error('Duplicate build platform ' + platform)
            build_platforms.add(platform)
            if platform not in platforms:
                check.error('Build platform is outside declared scope: ' + platform)
        path = verify_hash(check, build, label)
        if path and platform in ('ios', 'android'):
            allowed = ('.ipa', '.zip') if platform == 'ios' else ('.aab', '.apk')
            if path.suffix.lower() not in allowed:
                check.error(label + '.path must identify a mobile release artifact')
    for platform in platforms:
        if platform not in build_platforms:
            check.error('Missing candidate build for ' + platform)

    results = {}
    seen_checks = set()
    for index, item in enumerate(check.seq(data.get('checks'), 'checks')):
        label = f'checks[{index}]'
        result = check.obj(item, label, ('id', 'status', 'evidence'), ('reason', 'command', 'exit_code'))
        if check.identifier(result.get('id'), label + '.id', seen_checks):
            results[result['id']] = result
        check.enum(result.get('status'), label + '.status', ('pass', 'fail', 'unverified', 'not_applicable'))
        check.files(result.get('evidence'), label + '.evidence', nonempty=result.get('status') == 'pass')
        if result.get('status') in ('fail', 'unverified'):
            check.error(label + ' is failed or unverified')
        if result.get('status') != 'pass' or 'reason' in result:
            check.string(result.get('reason'), label + '.reason')
        if 'command' in result or 'exit_code' in result:
            check.string(result.get('command'), label + '.command')
            exit_code = result.get('exit_code')
            if type(exit_code) is not int:
                check.error(label + '.exit_code must be an integer, never a boolean')
            elif result.get('status') == 'pass' and exit_code != 0:
                check.error(label + '.exit_code must be 0 for a passed command')
    for identifier in needed:
        if identifier not in results or results[identifier].get('status') != 'pass':
            check.error('Required launch check must pass: ' + identifier)
    blockers = check.seq(data.get('blockers'), 'blockers')
    for index, blocker in enumerate(blockers):
        check.string(blocker, f'blockers[{index}]')
    if blockers:
        check.error('blockers must be empty before submission readiness')
    return check.errors, needed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--as-of', type=date.fromisoformat, help='Actual audit date if host timezone differs; default local today')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--requirements', action='store_true', help='List matrix requirements; does not assert readiness')
    args = parser.parse_args(argv)
    try:
        with args.report.open(encoding='utf-8-sig') as stream:
            report = json.load(stream, object_pairs_hook=_MODULE._unique_json_object)
        errors, needed = validate(report, args.root, args.as_of)
    except (OSError, ValueError, UnicodeError, RecursionError) as error:
        errors, needed = ['Cannot read report: ' + str(error)], []
    if args.requirements:
        print(json.dumps({'required_checks': needed, 'scope': 'Matrix listing only; no readiness claim.'}))
        return 0 if needed else 1
    result = {'valid': not errors, 'errors': errors, 'required_checks': needed, 'scope': SCOPE}
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print('Submission evidence gate passed.' if not errors else 'Submission readiness is not established:')
        for error in errors:
            print('- ' + error)
        print(SCOPE)
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
