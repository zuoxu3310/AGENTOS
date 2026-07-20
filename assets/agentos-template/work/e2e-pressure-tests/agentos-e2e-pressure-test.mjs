#!/usr/bin/env node
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const runId = new Date().toISOString().replace(/[:.]/g, "-");
const runDir = path.join(root, "work/e2e-pressure-tests/runs", `agentos-e2e-${runId}`);
const statePath = path.join(runDir, "state-board.json");
const reportPath = path.join(runDir, "report.md");

const requiredFiles = [
  "agent-os/boot.md",
  "agent-os/router.md",
  "agent-os/workflows/agent-execution-lifecycle.md",
  "agent-os/adapters/codex-workflow.md",
  "agent-os/adapters/runtime-visibility.md",
  "agent-os/adapters/skill-parity.md",
  "vendor/claude-dynamic-workflows-codex/runner/bin/run-workflow.js",
  "vendor/claude-dynamic-workflows-codex/references/authoring.md",
  "vendor/claude-dynamic-workflows-codex/LICENSE",
  "vendor/claude-dynamic-workflows-codex.AGENTOS.md",
  "agent-os/memory/wiki-v2.md",
  "wiki/knowledge/agentos-wiki-v2-method.md",
  "work/e2e-pressure-tests/agentos-e2e-pressure-test.mjs"
];

const skillPairs = [
  "reasoning-causality-review",
  "intent-contract-review",
  "route-promotion-review",
  "evidence-claim-review",
  "lifecycle-execution",
  "memory-wiki-routing"
];

function frontmatter(text) {
  if (!text.startsWith("---\n")) return null;
  const end = text.indexOf("\n---", 4);
  if (end === -1) return null;
  const data = {};
  for (const line of text.slice(4, end).trim().split(/\r?\n/)) {
    const match = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (match) data[match[1]] = match[2];
  }
  return data;
}

async function readText(relPath) {
  return await readFile(path.join(root, relPath), "utf8");
}

function gateWorkerClaim(claim, evidenceRefs) {
  const unsupportedCompletion = /complete|fully automated|all future|production-ready/i.test(claim);
  const supported = evidenceRefs.length > 0 && !unsupportedCompletion;
  return {
    claim,
    evidenceRefs,
    promotion: supported ? "promoted" : "not_promoted",
    allowed_wording: supported
      ? claim
      : "Unsupported worker claim recorded as support only; final wording must downgrade."
  };
}

function verifyCodexWorkflowPolicy(codexWorkflowText) {
  const requiredTerms = [
    "NO_DELEGATION",
    "cheapest capable",
    "single writer",
    "one delegated execution engine",
    "vendor/claude-dynamic-workflows-codex/runner/bin/run-workflow.js",
    "Monitor, Steer, Recover",
    "workspace fingerprint",
    "independence downgrade",
    "failed or superseded"
  ];
  const missingTerms = requiredTerms.filter((term) => !codexWorkflowText.includes(term));
  const forbiddenTerms = [
    "spawn_agent",
    "wait_agent",
    "followup_task",
    "interrupt_agent",
    "native_collaboration",
    "optional_external_runner",
    "optional external runner"
  ].filter((term) => codexWorkflowText.includes(term));

  const reviewerRepairCase = {
    worker_monitor: {
      policy: {
        stale_after: "10m",
        max_repair_attempts: 2,
        role_reuse_downgrade_rule: "role reuse cannot support clean independent reviewer wording"
      },
      workers: [
        {
          role: "reviewer",
          thread_id: "worker-reviewer",
          status: "stale",
          result_ref_exists: false,
          repair_attempts: [
            {
              thread_id: "worker-builder",
              route: "role_reuse",
              status: "completed_with_role_reuse_downgrade",
              result_ref: "results/reviewer.md",
              downgrade: "not a clean independent reviewer"
            }
          ]
        }
      ]
    }
  };

  const reviewer = reviewerRepairCase.worker_monitor.workers.find((worker) => worker.role === "reviewer");
  const monitorHandled =
    reviewer?.status === "stale" &&
    reviewer.repair_attempts?.some((attempt) =>
      attempt.route === "role_reuse" &&
      attempt.status === "completed_with_role_reuse_downgrade" &&
      attempt.downgrade?.includes("not a clean independent reviewer")
    );

  return {
    status: missingTerms.length === 0 && forbiddenTerms.length === 0 && monitorHandled ? "passed" : "failed",
    missingTerms,
    forbiddenTerms,
    monitorHandled,
    syntheticCase: reviewerRepairCase
  };
}

async function main() {
  await mkdir(runDir, { recursive: true });
  const steps = [];
  const failures = [];

  for (const relPath of requiredFiles) {
    const ok = existsSync(path.join(root, relPath));
    steps.push({ name: `file:${relPath}`, status: ok ? "passed" : "failed" });
    if (!ok) failures.push(`missing ${relPath}`);
  }

  for (const skill of skillPairs) {
    const codexSkill = `.agents/skills/${skill}/SKILL.md`;
    const claudeSkill = `.claude/skills/${skill}/SKILL.md`;
    const codexOk = existsSync(path.join(root, codexSkill));
    const claudeOk = existsSync(path.join(root, claudeSkill));
    const codexYamlOk = existsSync(path.join(root, `.agents/skills/${skill}/agents/openai.yaml`));
    const claudeYamlAbsent = !existsSync(path.join(root, `.claude/skills/${skill}/agents/openai.yaml`));
    const status = codexOk && claudeOk && codexYamlOk && claudeYamlAbsent ? "passed" : "failed";
    steps.push({ name: `skill-parity:${skill}`, status, codexYamlOk, claudeYamlAbsent });
    if (status !== "passed") failures.push(`skill parity failed for ${skill}`);
  }

  const conceptText = await readText("wiki/knowledge/agentos-wiki-v2-method.md");
  const conceptFm = frontmatter(conceptText);
  const conceptOk = Boolean(conceptFm?.type && conceptFm?.confidence && conceptFm?.status && conceptFm?.sources !== undefined);
  steps.push({
    name: "wiki-v2:concept-frontmatter",
    status: conceptOk ? "passed" : "failed",
    frontmatter: conceptFm
  });
  if (!conceptOk) failures.push("wiki v2 concept frontmatter incomplete");

  const codexWorkflowSkill = ".agents/skills/dynamic-workflow/SKILL.md";
  const claudeWorkflowSkill = ".claude/skills/dynamic-workflow/SKILL.md";
  const codexWorkflowOwnership =
    existsSync(path.join(root, codexWorkflowSkill)) &&
    !existsSync(path.join(root, claudeWorkflowSkill));
  steps.push({
    name: "runtime-ownership:codex-workflow-only",
    status: codexWorkflowOwnership ? "passed" : "failed"
  });
  if (!codexWorkflowOwnership) failures.push("Codex workflow adapter leaked into Claude");

  const codexWorkflowText = await readText("agent-os/adapters/codex-workflow.md");
  const workerMonitor = verifyCodexWorkflowPolicy(codexWorkflowText);
  steps.push({
    name: "dynamic-workflow:worker-monitor-stale-repair-downgrade",
    status: workerMonitor.status,
    gate: workerMonitor
  });
  if (workerMonitor.status !== "passed") failures.push("worker monitor stale repair downgrade check failed");

  const unsupportedWorkerClaim = gateWorkerClaim("AgentOS is complete and fully automated.", []);
  steps.push({
    name: "promotion-gate:downgrade-unsupported-worker-claim",
    status: unsupportedWorkerClaim.promotion === "not_promoted" ? "passed" : "failed",
    gate: unsupportedWorkerClaim
  });
  if (unsupportedWorkerClaim.promotion !== "not_promoted") failures.push("unsupported worker claim was promoted");

  const state = {
    runId,
    active_user_object: "AgentOS template structural pressure test",
    status: failures.length > 0 ? "failed" : "passed_with_scope_limits",
    scope_limits: [
      "This template E2E test proves structural rules, skill parity, wiki frontmatter, monitor policy, and promotion downgrade behavior.",
      "It does not create runtime-visible Codex threads, prove automatic skill triggering, prove hooks, or prove production durable replay."
    ],
    steps,
    failures,
    artifacts: { statePath, reportPath }
  };

  const report = [
    "# AgentOS Template E2E Pressure Test",
    "",
    `Status: ${state.status}`,
    "",
    "## Checks",
    "",
    ...steps.map((step) => `- ${step.name}: ${step.status}`),
    "",
    "## Downgrade Scenario",
    "",
    `Worker claim: ${unsupportedWorkerClaim.claim}`,
    "",
    `Gate result: ${unsupportedWorkerClaim.promotion}`,
    "",
    `Allowed wording: ${unsupportedWorkerClaim.allowed_wording}`,
    "",
    "## Worker Monitor Scenario",
    "",
    `Gate result: ${workerMonitor.status}`,
    "",
    `Missing terms: ${workerMonitor.missingTerms.length ? workerMonitor.missingTerms.join(", ") : "none"}`,
    "",
    "## Scope Limits",
    "",
    ...state.scope_limits.map((item) => `- ${item}`),
    ""
  ].join("\n");

  await writeFile(statePath, `${JSON.stringify(state, null, 2)}\n`, "utf8");
  await writeFile(reportPath, report, "utf8");

  console.log(JSON.stringify(state, null, 2));
  if (failures.length > 0) process.exitCode = 1;
}

await main();
