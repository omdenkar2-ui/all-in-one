# Backend scope modes

Use the user's explicit mode or clear scope instruction; otherwise retain **HOLD SCOPE**. Record the selected mode with the brief when it affects a decision. These modes change the questions and proposals, not the accepted requirements, existing authorization or evidence standard.

| Mode | Analysis within the backend brief |
| --- | --- |
| **SCOPE EXPANSION** | Explore a more valuable backend outcome and adjacent capabilities. Compare proposed additions with the current goal, effort, operational cost, failure behavior and constraints. Keep ambitious claims as hypotheses until supported. |
| **SELECTIVE EXPANSION** | First strengthen the accepted outcome, then offer a small set of independent additions with explicit benefit, cost, risk and dependencies. Preserve the current brief while those options are undecided. |
| **HOLD SCOPE**, default | Clarify the accepted outcome and the least complex viable approach. Trace applicable failure paths, recovery, security and observable success; flag ambiguity or unnecessary machinery without introducing new product behavior. |
| **SCOPE REDUCTION** | Propose a smaller viable backend core and identify the consequence of each deferral. Preserve security, durability and other binding guarantees; a lower-cost implementation that meets them is an alternative, not a requirement cut. |

Keep proposed additions/cuts distinct from accepted `R` requirements. Each scope change needs the user's trusted acceptance unless already authorized by the request; a mode choice alone is not that acceptance. Carry settled choices forward and disclose any infeasibility rather than silently changing them. A rejected or deferred optional proposal is not a blocker for the accepted brief.

Use the original controller journal, limits and remaining deadline for all analysis and any bounded prototype. Modes neither reset budgets nor launch additional agents or experiments by default. Return the accepted brief, material alternatives, unresolved proposals and planning readiness to the caller. A standalone brainstorm remains a brief; it does not authorize implementation.
