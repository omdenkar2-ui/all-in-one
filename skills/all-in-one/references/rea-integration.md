# REA integration

All in One bundles the published REA 6.4.0 workflow skill and its references.
Invoke `$all-in-one:reverse-engineer-anything` for supplied application artifacts,
binaries, managed code, packages or explicitly requested runtime investigation.
Keep ordinary source-repository questions with repository tools.

The plugin manifest registers a `rea` stdio MCP server. Its portable Node launcher
runs the fixed package request `npx -y rea-agents@6.4.0 mcp`; Windows uses the
upstream documented `cmd.exe /d /c` runner wrapper. Node.js 22.19+ in the 22.x
line, 24.11+ in the 24.x line, or 26+ and npm must already be available.
The first start can download the pinned runtime into npm's cache. The package
archive contains instructions and registration, not npm dependencies or engines.

A refreshed Codex chat or app restart is needed after installation to load the
new tools. Use the actual connected server schemas. Updating repository skill
files alone does not upgrade a running server. The matching CLI can also be used
as `npx -y rea-agents@6.4.0` followed by the requested command.

Static JavaScript and managed analysis do not need a native disassembler.
Native decompilation needs a separately configured supported provider such as
Ghidra, Hopper or IDA. The integration does not install these providers.
Follow the bundled REA recovery reference for an observed connection or provider
failure. Do not run all-provider diagnostics before every supported investigation.

REA analysis returns evidence, limitations and unknowns; it does not recover an
original source repository or establish behavior that was never observed.
Source attribution and exact bundled-file hashes live in
`integrations/rea/provenance.json` at the plugin root. Upstream skill files are
copied unchanged; Codex UI metadata and the MIT license are added separately.
