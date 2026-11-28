# Building Codebases Agents Can Be Trusted With

In [a talk on turning slop into gold](https://youtu.be/O_zcc6Xl12g), Lauren Tan describes how their team ships a steadily growing stream of agent-written pull requests to production, many of them merged overnight, while keeping the revert rate at about half a percent. The thesis is that the new job of a software engineer is to massively increase output while maintaining, or even improving, code quality. The key ingredient is trust: not blind trust in agents, but an environment built so that agents do the right thing by default.

## The trust pyramid

Investment in an agent's environment can be pictured as an inverted pyramid. The wide top is where most of the effort belongs, and each layer below it deserves less:

1. **The codebase itself.** Good API design, sound architecture, and regular refactoring.
2. **Deterministic checks.** Lint rules, type systems, compilers, and tests.
3. **Verification.** Runtime and formal verification that find bugs, check invariants, and confirm the agent understood the intent behind a change.
4. **Prose.** Rules, skills, and `AGENTS.md` files for the things that genuinely require judgment.

The first two layers constrain what an agent can do. Prose sits at the narrow bottom because it is the least enforceable. The principle that ties the layers together is simple:

**Whenever an agent needs correcting, turn the correction into a deterministic check or an architectural change instead of another line in a rules file.**

Repeat this enough times and there is less and less to look for in code review, until agents can merge most of their own pull requests.

## Layer 1: The codebase

Agents generate output from their input, and the codebase is one of the largest inputs they receive. Code used to arrive a few pull requests at a time. Now a single engineer directs hundreds of agents, and changes arrive in something closer to a continuous stream.

In that environment, the codebase behaves like a garden. Every workaround, anti-pattern, and piece of deprecated code looks like an established convention, and the next agent will copy it. Like weeds, bad patterns spread quickly. The guardrails in a codebase act as the foundation that new code grows around, so the goal is to keep it as clean as possible and ensure agents are always copying the good examples.

The team built Dune, an internal client framework for their Electron app (roughly "Next.js for Electron"), to encode lessons learned as constraints. Two examples stand out.

**Ban APIs that require nuance.** Anything that takes expertise to use well tends to produce slop. React's `useEffect` is the classic example: it has legitimate uses, but it is frequently misused, and agents are not good at using it correctly. The team banned it from product code and allows it only inside framework internals, which eliminates the problem categorically.

**Encode context in the directory structure.** A recurring bug was agents importing main-process code into the renderer process, causing long tasks and visible jank. The fix was to create two top-level directories, `electron-main` and `electron-renderer`, and forbid imports between them using a dependency graph analyzer and lint rules.

## Layer 2: Deterministic checks

Architectural rules only hold if something enforces them. Lint rules, type systems, and compilers do this without relying on an agent's judgment. Both rules from the previous section take only a few lines of ESLint configuration. A minimal version looks like this:

```js
// eslint.config.js
import importPlugin from "eslint-plugin-import";

export default [
  {
    files: ["src/**/*.{ts,tsx}"],
    ignores: ["src/framework/**"],
    rules: {
      "no-restricted-imports": ["error", {
        paths: [{
          name: "react",
          importNames: ["useEffect"],
          message: "useEffect is reserved for framework internals. Derive the value during render or use a framework hook.",
        }],
      }],
    },
  },
  {
    files: ["src/**/*.{ts,tsx}"],
    plugins: { import: importPlugin },
    rules: {
      "import/no-restricted-paths": ["error", {
        zones: [
          {
            target: "./src/electron-renderer",
            from: "./src/electron-main",
            message: "Renderer code cannot import main-process code. Expose the behavior over IPC instead.",
          },
          {
            target: "./src/electron-main",
            from: "./src/electron-renderer",
            message: "Main-process code cannot import renderer code.",
          },
        ],
      }],
    },
  },
];
```

The error messages matter as much as the rules. An agent that hits one of these errors is told what to do instead, which keeps it from inventing a new workaround.

### Why a lint rule beats a comment

The alternative to a check is usually a comment, and agents often use Markdown and code comments as a place to justify not doing the right thing. At Cursor, agents leaned heavily on imperative timers such as `setTimeout`, `requestAnimationFrame`, and `requestIdleCallback` as quick fixes. The timers were papering over a clash between VS Code's imperative architecture and React's declarative one. The agents wrote comments explaining why each workaround was justified, the pattern spread, and the constant creation and destruction of timers triggered frequent garbage collection and degraded the app's performance.

On the new project, the team banned nearly all comments. Comments go stale, humans rarely read them, and they give agents an escape hatch. Most importantly, comments are not enforceable. A comment telling the next agent not to do something cannot be trusted. A lint rule can, especially one whose error message points the agent toward the root cause instead of a workaround.

## Layer 3: Verification

Code review on the team has largely shifted to reviewing verification artifacts: videos, screenshots, diagrams, and formal proofs.

**Runtime verification** gives an agent a way to run the code and use the same debugging tools a human would, such as the Chrome DevTools Protocol. Two techniques make this more effective:

- A **feature map**, which works like a site map of every feature in the application from the user's point of view. It gives humans and agents a shared vocabulary, so an agent does not have to guess what "the thing in the left sidebar" refers to.
- **Custom CLIs** inside skills, so agents reuse the same tested driver every time instead of improvising one, which also reduces token usage.

**Formal verification** is a newer addition. The team uses [TLA+](https://lamport.azurewebsites.net/tla/tla.html) to model check major user flows, such as notifications across multiple devices and platforms, and [Lean](https://lean-lang.org/) to prove properties of algorithms, such as confirming that a custom virtualization library does not flicker or jitter. Property-based UI testing with Bombadil adds another layer. Both approaches have already found real bugs, though neither is treated as a silver bullet. Tan also built a skill that renders state charts of user flows, which are easier to review alongside screenshots and videos than the code itself.

Verification is where most of the tokens go. Tan reports that the majority of their token usage is spent verifying work rather than generating it. None of these techniques are new. Model checking, property-based testing, and runtime verification are established tools that were often too expensive to write and maintain. Agents reduce that cost enough that it is now economical to test far more thoroughly than before.

## Layer 4: Prose

Rules, skills, and `AGENTS.md` files still have a place, but only for decisions that require judgment. A useful test is whether two reasonable reviewers could disagree about the outcome. If they could not, the decision belongs in a check.

Deciding when to extract a shared abstraction is a good example. Sometimes three similar components should be merged, and sometimes they should stay separate. No lint rule can tell the difference, because the answer depends on whether the components are likely to change together. A rule such as "Prefer duplication until a third use case appears, and extract only when the call sites change for the same reason" gives an agent a heuristic without pretending to be a law.

Prose has two weaknesses. Agents can ignore it, and they tend to over-rotate on it, treating a minor correction as a rule that can never be broken. Writing each rule as a heuristic with its reasoning attached helps an agent recognize when an exception applies. Anything that can be expressed as a check belongs in one of the layers above.

## Foundations before factories

It is tempting to jump straight to building a "software factory" that automates everything. The talk recommends building the foundations first: improve the codebase when correcting an agent, add a lint rule to prevent new occurrences of an anti-pattern, clean up the existing ones, and make verification strong.

If the inner coding loop produces slop, automating it only produces more slop, and fixing it requires throwing ever more tokens at the problem.

With solid foundations, automation becomes straightforward. On Tan's team, every new release automatically spins up agents that fuzz the entire application by using it like a real user, open a fix pull request for each bug they find, and auto-merge those fixes. That only works because the codebase is good enough that pull requests tend to be good by default. Despite the higher velocity and a growing number of contributors, the app has become faster on startup, typing, and switching chats since launch.
