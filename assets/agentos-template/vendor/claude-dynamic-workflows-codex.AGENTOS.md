# AgentOS Vendor Record

- Upstream: `https://github.com/scasella/claude-dynamic-workflows-codex`
- Pinned commit: `16524bea870a51ac7bfb3dc7dce77e333c7a56e1`
- Upstream version: `0.2.0`
- Imported: `2026-07-19`
- License: MIT; the upstream `LICENSE` is preserved in the vendored directory.

The vendored directory is the unmodified Dynamic Workflow execution engine.
AgentOS policy and Codex entry behavior belong in
`agent-os/adapters/codex-workflow.md` and
`.agents/skills/dynamic-workflow/`, not in vendor source.

Offline verification:

```bash
npm test --prefix vendor/claude-dynamic-workflows-codex/runner
```
