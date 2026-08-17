# Think Through

## Purpose

Help the user form a judgment when they explicitly want to think something
through, without turning the conversation into a questionnaire or starting
execution before the judgment is settled.

This workflow reuses Reasoning Base, Intent-Causal Gate, Route Keeper, and the
normal Task Contract. It is not a new reasoning engine or state system.

## Enter

Enter immediately when the user explicitly asks to think something through,
clarify a decision, explore uncertainty, or be guided by questions. That request
is already permission; do not ask whether to enable the workflow again.

When the signal is only tentative or ambiguous, offer this workflow only if a
multi-turn deliberation would materially change the current route. AI-user
disagreement alone never starts or prolongs it.

On entry, explicitly tell the user that the conversation has entered the
think-through stage; do not make the user infer it from a change in tone or the
first question. In the same brief notice, name what is being clarified, make
clear that execution is paused, and say that the user may end the stage at any
time in natural language.

## Work

Use one small loop:

1. Identify the current decision, conflict, or unknown.
2. Do the research, synthesis, comparison, and recommendation that the AI owns.
3. Ask only a user-owned question that cannot be replaced by investigation, a
   stated assumption, or a safe reversible default and that blocks the next
   useful step.
4. Ask dependent questions sequentially. Batch only independent questions that
   jointly block the same next step.
5. Before a load-bearing question, state briefly why the answer matters and
   what its plausible branches would change.
6. Present every admitted question as a separate, visually obvious decision
   block instead of burying it in prose. Start with a localized heading
   equivalent to `Decision needed`, give two to four lettered choices (`A`, `B`,
   `C`, `D` as needed), and state in one line what selecting each choice would
   change. Mark the AI's current recommendation when the evidence supports one,
   and tell the user how to answer.
7. Keep the choices genuinely distinct and useful. If they are not exhaustive
   or the evidence is insufficient, include an explicit route such as "other",
   "none of these", or "not enough information yet" instead of forcing a false
   choice.
8. After the answer, update the current judgment, resolve or park the question,
   and continue only while another admitted question remains.

Keep the exchange conversational. Do not expose hidden chain-of-thought, turn
every message into a node, repeat a route marker on ordinary turns, or ask the
user to perform research and synthesis that the AI can do.

For a deliberation that needs recovery across turns or context compression, use
the existing session-local `active_work` contract. Do not create another mode
flag, journal, or state store.

## Close

Any clear natural-language request to finish, stop, or leave it there closes the
stage immediately. Do not ask another question. Unless the user asks for no
summary, give a compact settlement containing:

- what was resolved;
- what remains uncertain or parked;
- the current recommendation and its main assumption;
- what would reopen the deliberation.

Closing deliberation is not authorization to execute. Transition to execution
only when the user separately gives a clear action instruction; then follow the
normal AgentOS lifecycle without asking for redundant confirmation.

## Boundaries

- Do not activate for a fully specified action merely because the task is hard.
- Do not require a magic start or stop phrase.
- Do not force a fixed number of questions or a fixed number of rounds.
- Do not keep questioning after the decision is clear or the user closes the
  stage.
- Do not add hooks, classifiers, subagents, or external tools for this workflow.
