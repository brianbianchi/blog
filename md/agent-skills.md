# Building a Feature with Agent Skills

An agent can build an entire feature in the time it takes to make a cup of coffee, which raises an uncomfortable question about what the engineer is there for. Three popular skill libraries offer overlapping answers:

- [**Matt Pocock's skills**](https://github.com/mattpocock/skills) focus on getting decisions out of the engineer's head before any code is written, and on learning from each session afterward.
- [**Superpowers**](https://github.com/obra/superpowers), by Jesse Vincent, is a full development methodology: plan in small steps, build with subagents, test first, and prove the work is done.
- [**Impeccable**](https://github.com/pbakaus/impeccable), by Paul Bakaus, gives the agent a design vocabulary and a detector for the generic look of AI-built interfaces.

Each library covers the whole lifecycle to some degree, but each is strongest at a different stage. This post builds one feature using each library where it does the most good.

| Stage | Library | Skills |
| --- | --- | --- |
| Decide | Matt Pocock, Impeccable | `grill-with-docs`, `to-spec`, `init`, `shape` |
| Plan | Superpowers | `writing-plans`, `using-git-worktrees` |
| Build | Superpowers | `subagent-driven-development`, `test-driven-development` |
| Polish the UI | Impeccable | `critique`, `audit`, `harden`, `polish` |
| Review and ship | Superpowers, Matt Pocock | `verification-before-completion`, `requesting-code-review`, `pr` |
| Learn | Matt Pocock | `retro` |

## The feature

Imagine a coffee subscription app and a one-sentence prompt: *let users pause their subscription.* Ten minutes later there is a Pause button, the tests pass, and the feature works.

Then a customer pauses on the 29th and still receives a bag of coffee on the 1st, because it had already been roasted and packed. Someone had to decide what happens to that bag, and the agent made that decision. It also decided whether billing stops immediately or at the end of the month, how long a pause can last, and what the reminder email says. The pause screen it built uses a purple gradient, a card nested inside a card, and gray text on a colored background, because that is what agents produce when nobody tells them otherwise.

A one-sentence prompt leaves every gap open, and the agent fills each one with a guess. Each stage below closes a different kind of gap.

## Decide: grilling

Matt Pocock's answer to the silent guess is to reverse the conversation. Before any code exists, the agent interviews the engineer. His [`grilling`](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md) skill maps the feature as a **design tree**, where every decision branches into the decisions that depend on it. The **frontier** is every decision whose prerequisites are already settled. The agent asks the whole frontier in one numbered round, with a recommended answer for each question:

```
❓ Q1 - When does billing stop? Should billing stop at the end of
the current billing period rather than immediately?
➡️ Yes. The customer has already paid for this month.

❓ Q2 - What happens to a packed bag? If the next bag is already
packed when the customer pauses, should it still ship, with the
pause starting after it?
➡️ Yes. Cancelling a roasted bag wastes coffee.
```

Questions are worded so that "yes" accepts the recommendation, which keeps rounds fast. Facts are the agent's job: if an answer is in the code, a subagent looks it up instead of asking. Decisions are the engineer's, and no code is written until the frontier is empty.

The [`grill-with-docs`](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md) variant runs the same interview and also writes documentation as it goes, including a glossary kept in the repository. When the engineer mentions that customers can skip a month, the agent asks whether *skip* means the same thing as *pause*, and records the answer:

```md
## Pause
No deliveries and no charges until the resume date.
Avoid: hold, freeze, suspend.

## Skip
One delivery is missed. Billing continues as normal.
```

Once the tree is settled, [`to-spec`](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-spec/SKILL.md) writes up the problem, the solution, and a numbered list of user stories, such as "As a customer who pauses after my bag is packed, I still receive that bag, and my pause starts after it."

Superpowers has its own front end for this stage, [`brainstorming`](https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md), which draws out intent and plays the design back in chunks for approval. It covers similar ground. Grilling is more systematic about finding every decision, while brainstorming is more conversational.

Impeccable contributes here too, before any UI exists. Running [`/impeccable init`](https://impeccable.style/docs) once per project reads the code, asks only what it cannot infer about who the product is for and what it must do, and writes a `PRODUCT.md` that every later design command reads. Running `shape` plans the pause screen's UX before any markup exists.

## Plan: bite-sized tasks

Superpowers takes the approved spec and turns it into a plan with [`writing-plans`](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md). Its README sets the bar memorably: the plan should be clear enough for "an enthusiastic junior engineer with poor taste, no judgement, no project context, and an aversion to testing to follow." Each task takes two to five minutes and names exact file paths, complete code, and a verification step:

```md
### Task 3: Ship the packed bag before the pause starts

Files: src/billing/pause.ts, src/billing/pause.test.ts

1. Add a failing test: pausing after the pack date still
   schedules exactly one delivery.
2. Run `npm test -- pause` and confirm it fails.
3. In `startPause()`, move the pause start to the day after
   any delivery already packed.
4. Run the test again and confirm it passes. Commit.
```

[`using-git-worktrees`](https://github.com/obra/superpowers/blob/main/skills/using-git-worktrees/SKILL.md) then creates an isolated workspace on a new branch and confirms the existing tests pass before any changes are made.

Matt Pocock's equivalent, [`to-tickets`](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md), cuts work into larger vertical slices, each sized to fit in a single fresh context window. The two approaches suit different work. Small, fully specified tasks suit a plan that agents will execute without supervision, while larger tickets suit work tracked in an issue tracker.

## Build: subagents and tests first

[`subagent-driven-development`](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md) dispatches a fresh subagent for each task, so every task starts with a clean context. After each task, a review checks the work in two stages: first for compliance with the spec, then for code quality. The Superpowers README notes that it is not uncommon for agents to work autonomously for a couple of hours this way without drifting from the plan.

Every task runs under [`test-driven-development`](https://github.com/obra/superpowers/blob/main/skills/test-driven-development/SKILL.md), whose central rule is written as an iron law: **no production code without a failing test first.** The skill goes further than most TDD advice. Code written before its test is deleted, not adapted.

For Task 3, the subagent writes the packed-bag test and runs it before touching `startPause()`:

```
FAIL  src/billing/pause.test.ts
  ✕ pausing after the pack date still schedules exactly one delivery
    Expected deliveries: 1
    Received deliveries: 0
```

Only then does it change the code, and the same test passes. The spec-compliance review earns its place a few tasks later. A subagent implements resume and its tests pass, but they only check that the subscription's status returns to active. The reviewer compares the work against the user story ("As a customer who resumes, my next bag ships on my usual schedule"), finds that no delivery is ever rescheduled, and sends the task back.

## Polish the UI: a design vocabulary

The pause screen now works, and it still looks like every other agent-built page. Impeccable's README lists the usual tells: Inter for everything, purple-to-blue gradients, cards nested in cards, gray text on colored backgrounds, and a rounded-square icon tile above every heading.

Impeccable addresses this with named commands, each backed by a playbook for one specific move. Targets should be narrow, because a single section reviewed closely beats a whole page at a glance:

```
/impeccable critique the pause screen
/impeccable audit the pause confirmation
/impeccable harden the pause screen
/impeccable polish settings
```

`critique` scores the design against usability heuristics and ranks what to fix first. `audit` checks accessibility, performance, theming, and responsive behavior, with findings ranked from P0 to P3. `harden` covers error states and edge cases, such as a resume date in the past or a very long plan name, and `polish` is the final pass before shipping.

The most valuable piece is deterministic. Impeccable's detector runs 62 rules that flag the tells above, plus problems like cramped padding and skipped heading levels, with no model involved. The installer offers a design hook that scans every UI file the agent edits and returns the findings before the agent calls the work done. On the first draft of the pause screen, it flags all three problems from the opening:

```
src/pause/PauseScreen.tsx
  12:3  gradient-purple-blue     Purple-to-blue gradient background
  18:5  nested-card              Card nested inside a card
  24:7  low-contrast-on-color    Gray text on a colored background
```

The same detector runs in CI:

```bash
npx impeccable detect --sarif src/ > impeccable.sarif
```

## Review and ship

Before declaring the feature finished, Superpowers' [`verification-before-completion`](https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md) enforces another iron law: **no completion claims without fresh verification evidence.** The agent must run the tests and show the output, not report that they should pass.

[`requesting-code-review`](https://github.com/obra/superpowers/blob/main/skills/requesting-code-review/SKILL.md) reviews the branch against the plan and blocks progress on critical issues. Reading the whole branch, it finds a bug no single task could show: a customer who pauses and resumes within the same billing period is charged twice, because resuming starts a new billing period instead of continuing the current one. Matt Pocock's [`code-review`](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md) takes a similar approach, running two reviews in parallel subagents, one against the spec and one against the project's coding standards. Both libraries reach the same conclusion: the agent that wrote the code is the worst one to review it.

For the pull request, Matt Pocock's [`pr`](https://github.com/mattpocock/skills/blob/main/skills/engineering/pr/SKILL.md) skill adds a section worth borrowing whatever else is in use:

```md
## Merge danger

Two-way door. Adds a nullable `paused_until` column to `subscriptions`;
rolling back drops the column with no data loss.

Blast radius: billing. A bug here could skip or double a charge.
```

## Learn: retro

The last step belongs to Matt Pocock's [`retro`](https://github.com/mattpocock/skills/blob/main/skills/engineering/retro/SKILL.md). Before the chat is cleared, the agent reads back through the session and suggests changes to the repository, the checks, and the instructions. Agents do not complain. They push through problems until the feature works, and the struggle stays buried in the transcript unless something surfaces it.

In this session, the agent spent ten minutes searching for the billing code, so the retro suggests one line in the agent instructions pointing to it. It also called the payment provider directly twice, which the codebase never does, so that becomes a lint rule. Pocock advises against letting the agent apply its own findings, because it ends up chasing false positives. The retro only suggests, and the engineer chooses what to keep.

## Costs and trade-offs

**Overlapping skills compete.** All three libraries have opinions about planning, and two of them review code. Installing all three without choosing means the agent may brainstorm and grill, or run two reviews. Pick one library per stage and leave the overlapping skills uninstalled or uninvoked.

This matters more because the libraries trigger differently. Superpowers skills trigger automatically: a bootstrap skill tells the agent that if there is even a 1% chance a skill applies, it must invoke it. Matt Pocock's skills mostly run only when their name is typed. Automatic triggering means the process happens without anyone remembering to ask for it, but it also means Superpowers' `brainstorming` may start before anyone types `grill-with-docs`. Explicit invocation keeps the engineer in control of when each step runs.

**Structure can outlive its usefulness.** Process written for weaker models can box in stronger ones, such as a plan split into two-minute tasks for a change a current model could make in one pass. The one-context-window ticket and the two-to-five-minute task are rules of thumb for today's models, not constants. Pocock deletes skills once they stop earning their place. He retired one for resolving merge conflicts because "the agent works through an in-progress merge or rebase conflict without a dedicated skill." That habit applies to any library.

**The human's time is not free.** Twenty grilling questions is a real interruption, and a full plan for a one-line fix costs more than it saves. The process earns its keep on features like the pause button, where the expensive mistakes are decisions nobody noticed they were making.

**Is this waterfall?** Not quite. The spec lives as an issue in the tracker, and once the work ships, the issue is closed and nobody maintains it again. By then its decisions live in the code, the tests, and the glossary. Waterfall front-loads a document that must stay correct for months. This front-loads a conversation that only needs to stay correct for an afternoon.

## What the engineer is for

Across all three libraries, the agent writes nearly every line. What remains for the engineer are the decisions only they can make: what happens to the packed bag, whether *skip* means *pause*, which of the critique's findings matter, and which of the retro's suggestions to keep. The skills exist to make sure those decisions get asked, rather than silently guessed.
