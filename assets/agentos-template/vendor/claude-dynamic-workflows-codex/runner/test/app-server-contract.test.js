// Deterministic integration coverage for the real App Server boundary.
//
// A child process speaks the same newline-delimited JSON-RPC protocol as
// `codex app-server`. This exercises the production AppServerClient and
// codexAgent wiring without credentials, network access, or model spend:
// initialize/model-list, thread+turn start, streamed output, token usage,
// server-initiated tool requests, schema plumbing, and cleanup.

import assert from "node:assert/strict";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { codexAgent, shutdownClient } from "../src/codexAgent.js";
import { resetMeter } from "../src/meter.js";

const ROOT = await mkdtemp(join(tmpdir(), "wf-app-server-contract-"));
const SERVER = join(ROOT, "fake-app-server.mjs");
const AUDIT = join(ROOT, "frames.jsonl");

// The fake deliberately writes one non-JSON startup line. The production client
// tolerates harmless stdout noise while still parsing subsequent JSON frames.
await writeFile(
  SERVER,
  String.raw`
import { appendFileSync } from "node:fs";
import { createInterface } from "node:readline";

const auditPath = process.argv[2];
const threadId = "fake-thread";
const turnId = "fake-turn";
const toolRequestId = 9001;

const record = (direction, frame) => appendFileSync(
  auditPath,
  JSON.stringify({ direction, frame }) + "\n",
);
const send = (frame) => process.stdout.write(JSON.stringify(frame) + "\n");

process.stdout.write("fake app-server startup log\n");

const emitTurn = () => {
  send({ method: "thread/tokenUsage/updated", params: {
    threadId,
    tokenUsage: { total: { inputTokens: 10, outputTokens: 2, reasoningOutputTokens: 3 } },
  } });
  send({ method: "item/agentMessage/delta", params: {
    threadId, itemId: "message-1", delta: '{"answer":"hello"}',
  } });
  send({ method: "item/completed", params: {
    threadId, item: { type: "agentMessage", text: '{"answer":"hello"}' },
  } });
  send({ method: "turn/completed", params: {
    threadId, turn: { id: turnId, status: "completed" },
  } });
};

const rl = createInterface({ input: process.stdin });
rl.on("line", (line) => {
  let frame;
  try {
    frame = JSON.parse(line);
  } catch {
    return;
  }
  record("client", frame);

  if (!frame.method) {
    if (frame.id === toolRequestId) setTimeout(emitTurn, 10);
    return;
  }

  if (frame.method === "initialize") {
    send({ id: frame.id, result: {} });
  } else if (frame.method === "model/list") {
    send({ id: frame.id, result: { data: [{ id: "gpt-5.5", isDefault: true }] } });
  } else if (frame.method === "thread/start") {
    send({ id: frame.id, result: { thread: { id: threadId } } });
  } else if (frame.method === "turn/start") {
    send({ id: frame.id, result: { turn: { id: turnId } } });
    // Delay the bidirectional request so the client's turn listeners are in place.
    setTimeout(() => send({
      id: toolRequestId,
      method: "item/tool/call",
      params: { threadId, name: "unexpected-tool", arguments: {} },
    }), 10);
  }
});
`,
);

try {
  resetMeter();
  const progress = [];
  const metrics = [];
  const result = await codexAgent("schema please", {
    model: "gpt-5.5",
    effort: "low",
    sandbox: "read-only",
    cwd: ROOT,
    retries: 0,
    schema: { type: "object", properties: { answer: { type: "string" } } },
    clientOptions: { command: process.execPath, args: [SERVER, AUDIT] },
    onProgress: (text) => progress.push(text),
    onMetrics: (value) => metrics.push(value),
  });

  assert.deepEqual(result, { answer: "hello" }, "schema output is parsed through the real client path");
  assert.ok(progress.length > 0, "streamed output reaches the progress callback");
  assert.equal(progress.at(-1), '{"answer":"hello"}');
  assert.equal(metrics.length, 1, "one completed turn emits one metrics record");
  assert.equal(metrics[0].model, "gpt-5.5");
  assert.deepEqual(metrics[0].tokens, { input: 10, output: 2, reasoning: 3, total: 15 });

  const frames = (await readFile(AUDIT, "utf8"))
    .trim()
    .split("\n")
    .map((line) => JSON.parse(line));
  const clientFrames = frames.filter((entry) => entry.direction === "client").map((entry) => entry.frame);

  const initialize = clientFrames.find((frame) => frame.method === "initialize");
  assert.equal(initialize.params.clientInfo.name, "codex-workflows");
  assert.equal(initialize.params.clientInfo.title, "Codex Workflows Runner");
  assert.match(initialize.params.clientInfo.version, /^\d+\.\d+\.\d+$/);

  const modelList = clientFrames.find((frame) => frame.method === "model/list");
  assert.deepEqual(modelList.params, { limit: 200, includeHidden: true });

  const threadStart = clientFrames.find((frame) => frame.method === "thread/start");
  assert.equal(threadStart.params.approvalPolicy, "never");
  assert.equal(threadStart.params.sandbox, "read-only");
  assert.equal(threadStart.params.cwd, ROOT);
  assert.equal(threadStart.params.model, "gpt-5.5");

  const turnStart = clientFrames.find((frame) => frame.method === "turn/start");
  assert.equal(turnStart.params.threadId, "fake-thread");
  assert.equal(turnStart.params.model, "gpt-5.5");
  assert.equal(turnStart.params.effort, "low");
  assert.deepEqual(turnStart.params.input, [{ type: "text", text: "schema please" }]);
  assert.deepEqual(turnStart.params.outputSchema.required, ["answer"]);
  assert.equal(turnStart.params.outputSchema.additionalProperties, false);

  // The client must answer a stray server request defensively so the turn cannot
  // deadlock when approvalPolicy is "never".
  const toolResponse = clientFrames.find((frame) => frame.id === 9001 && !frame.method);
  assert.deepEqual(toolResponse.result, {
    success: false,
    contentItems: [{ type: "inputText", text: "No dynamic tool handler is registered." }],
  });
} finally {
  await shutdownClient();
  resetMeter();
  await rm(ROOT, { recursive: true, force: true });
}

console.log("app-server contract checks passed ✓");
