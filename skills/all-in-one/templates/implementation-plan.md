# Backend implementation plan

## Work source
Record the accepted contract path and SHA-256, scope, delivery destination, and binding decisions.

## Units
Each unit records ID, outcome, dependencies, owned files, consumed/produced interfaces, failure cases, and verification command/assertion.
The integrator owns shared integration, final checks, and canonical commits.

## Durable ledger
Track each unit as planned, running, complete, blocked, or failed. Record actual changes, results and evidence paths, decisions, and review findings.
On resume compare source identity and current files before repeating work.

## Final gates
Record required checks, independent review scope, blocker resolution, delivery evidence, and remaining nonblocking follow-ups.
An exhausted retry budget preserves a blocked state and next action; it does not waive acceptance.
