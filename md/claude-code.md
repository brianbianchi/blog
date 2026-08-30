# What I've Learned About Claude Code

I've been using [Claude Code](https://code.claude.com/docs/en/overview) since the beginning of 2026, mostly on the $20 plan, which forces you to be deliberate about how you spend tokens. What actually changed how I work with it is my day-to-day workflow, the skills and MCPs I keep coming back to, and the habits that keep a session from burning through its context before I've gotten anything done.

## /init

`/init` is the command to run when you first open Claude Code in a project. Claude reads your entire codebase and writes a [`CLAUDE.md`](https://code.claude.com/docs/en/memory) file that becomes its permanent memory for the project.

Other AI agents, like [Codex](https://github.com/openai/codex) and [Cursor](https://cursor.com), use a shared [`AGENTS.md`](https://agents.md/) convention, but Claude uses its own `CLAUDE.md` file instead. The one saving grace is that `CLAUDE.md` can import other files, so if you already have an `AGENTS.md`, you can import it rather than dealing with a symlink.

There's also a newer, experimental version of `/init` behind an environment flag. Instead of just analyzing the codebase and writing the file, it interviews you, then recommends skills and hooks based on your answers. That's a nice touch.

After months of dealing with sloppy AI-generated code, you start to learn these models' quirks and bad habits, and your `CLAUDE.md` file evolves to correct for them. Mine currently includes:

- A quick description of the project and its current status
- My coding style preferences
- A "working philosophy" section I've been experimenting with
- A rule about user-facing capitalization: AI models default to ALL CAPS in UI text for some reason, and it's ugly
- A pull request language and format preference

## Skills

A skill is a `SKILL.md` file: a guide for something you do repeatedly that Claude can reference when it makes sense, or that you can explicitly invoke. Think best practices, a research workflow, or a repeatable process for implementing something.

Claude Code ships with a few default skills pre-installed, like code review and security review. Worth using as a bonus when Claude implements a feature.

I love that there's a whole community built around skills now — companies and experienced engineers packaging their best practices into a single file. It's useful for the agent, but it's also useful for me to read. Places I go to find them:

- **[skills.sh](https://www.skills.sh/)**, my go-to site for finding and installing skills
- Various GitHub repos that collect community skills

Some favorites:

- **[Matt Pocock's skills](https://github.com/mattpocock/skills)**, particularly his ["grill me" skill](https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md) for refining requirements and his ["improve codebase architecture" skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/improve-codebase-architecture/SKILL.md), which comes with a nice visual workflow
- **[Cursor's "thermonuclear code quality review" skill](https://thermonuclear-review-lesson.vercel.app/)**. Simplifies AI-generated code and cuts down on slop. Combines well with the codebase architecture skill above
- **[Shadcn's "improve" skill](https://github.com/shadcn/improve)**, which audits your codebase and writes plans for other agents to execute
- **[Superpowers](https://github.com/obra/superpowers)**, a whole methodology rather than a single skill. It bundles things like brainstorming, TDD, and worktree usage into one plugin, and the skills trigger automatically instead of needing to be invoked by name
- **[Impeccable](https://github.com/pbakaus/impeccable)**, a design-judgment skill for front-end work. It gives Claude a set of named commands like polish, audit, and critique so its UI decisions stop looking like default AI slop

Don't spam skills, and don't install a hundred at once. A lot of them are opinionated since everyone has their own idea of "good code," so it's worth sticking to one coherent set that matches your own style rather than mixing conflicting philosophies.

## Custom Commands

Before Skills, there were [custom slash commands](https://code.claude.com/docs/en/commands). These are markdown files living in `.claude/commands/` (project-level) or `~/.claude/commands/` (works across all your projects), invoked by typing `/` plus the filename. Anthropic now considers this format legacy in favor of Skills, but it still works, and it's still the simpler option for a single reusable prompt that doesn't need the extra structure a `SKILL.md` file expects. I keep a few of these around for one-off things I don't want to dignify with a whole skill folder.

## [Plan Mode](https://code.claude.com/docs/en/permission-modes)

Hitting Shift+Tab puts Claude into plan mode. Instead of immediately reading and making changes, Claude explores the codebase more thoroughly, writes up a full plan, and shows it to you before touching anything. You approve it or send it back.

This is a must for big tasks. You get higher-quality results because the model takes time to think before acting, and it's far easier to catch a mistake in a plan than in 3,000 lines of code spread across a dozen files. Skip it for small stuff like typos, variable renames, or minor design tweaks; it's overkill there and won't meaningfully improve the result.

A related workflow, popularized by Shadcn's "improve" skill, uses a smarter, more expensive model to write the plan, then hands it off to a cheaper, faster model to implement it. "Faster and cheaper" doesn't mean dumb anymore. A lot of these lighter models are quite capable, which is exactly why this saves money without sacrificing much quality. On Claude Code that might mean Opus for the plan and Sonnet for implementation. On other tools you can mix models from different providers entirely.

### /model

You don't need separate tools to pull off that plan-with-a-smart-model, implement-with-a-cheap-one trick. `/model opus`, `/model sonnet`, or `/model haiku` switches mid-session without losing your conversation history, and running `/model` with no argument opens a picker. There's also `opusplan`, which uses Opus while you're in plan mode and switches to Sonnet the moment you approve the plan and it starts writing code.

One catch: prompt caching is scoped per model, so every time you switch you throw away the cache you'd built up. Bouncing between models every few turns quietly costs more than it saves. Pick a model, get through a phase of work, then switch, rather than hopping back and forth.

## Verification

This isn't really a feature or command. It's a workflow, and honestly it's just good software engineering practice that AI makes more important, not less.

Verification means giving Claude a way to check its own work before it declares something done. Left alone, Claude has no real way of knowing if its output is correct; it just says it's done. With verification steps, it can actually check.

Ways to verify:

- **Tests.** Tell Claude to write the tests first, then implement. If you have it implement first and write tests after, it'll write tests that pass against its own code, which isn't testing, it's cheating. Don't let it test every single line either. Smarter models tend to over-test everything, which just bloats the codebase.
- **Type checkers and linters.** If your language supports them, tell Claude to run them before considering a task complete.
- **Screenshot testing and browser testing.** For front-end work: Claude can't actually see what it builds, so having it open the app, click around, and take screenshots lets it verify visually. This used to require MCPs; a lot of it is built in now.

## [MCPs](https://modelcontextprotocol.io/)

MCPs give Claude access to tools outside your codebase: GitHub, your database, Slack, analytics, deployments, and, for front-end work, a browser.

Ways I use them:

- Fetching design inspiration
- Database seeding (adding fake data to test features)
- Researching documentation
- Browser testing

You only need an MCP when Claude has to directly interact with something outside your codebase. There's no reason to reach for one for best practices or "how do I implement X"; that's what skills are for. Same rule as skills: don't install a pile of them, only use what's necessary.

## [Hooks](https://code.claude.com/docs/en/hooks)

If Skills and MCPs are how you extend what Claude knows and can reach, hooks are how you constrain what it's allowed to do. A hook is a script that fires on a lifecycle event. `PreToolUse` runs before Claude uses a tool and can block it outright, while `PostToolUse` runs after and can react to what happened. Both receive the tool name and its input as JSON on stdin.

Practical uses: a `PreToolUse` hook that blocks anything matching `rm -rf` before it ever runs, or one that stops edits to a `.env` file. A `PostToolUse` hook that runs your formatter automatically after every file edit, so you're not asking Claude to remember to do it. This is the one extensibility mechanism of the three that's actually about safety rather than capability, and it's worth setting up before you hand Claude anything destructive.

## Small But Convenient Features

**`/voice`.** Claude Code has a voice mode. Type `/voice` and talk; whatever you say becomes the prompt. It's easier to be descriptive out loud than typing, and it's faster if you're a slow typist.

**Mid-task questions.** A command lets you ask a question mid-task without interrupting Claude or touching the conversation history, so you can ask about something it already read or implemented. When you use it, Claude can't read files or run commands; it just answers from the existing conversation. Useful when you want to understand a decision it already made.

**Teleport / Remote Control.** Moves a session between the phone app, the web, and the terminal. Useful if you get an idea while out and want to start it on your phone, then pick it up later at your terminal.

**Shell mode.** Starting a message with `!` drops you into a normal terminal, except Claude also sees the output. A convenient shortcut for mixing manual shell commands into a session.

**`/radio`.** Opens Claude FM, lo-fi music to code to. That's the whole feature.

## Context Management

Claude Code tracks usage based on tokens, not the number of prompts you send. Every message, every file Claude reads, and every response it writes generates tokens. The goal is to make those tokens count, both for your usage limits and for Claude's actual performance, since the context window doubles as its short-term memory.

The more context you use, the worse Claude gets. It starts forgetting things, contradicting itself, making sloppy mistakes. Claude Code has two context limits, one around 300,000 tokens and one around a million (it defaults to the larger window). A bigger window doesn't push back the point where quality drops; it just extends the range over which that drop happens. In my experience, performance starts dipping somewhere around 100,000 to 200,000 tokens, and usage limits get eaten up fast well before that.

Check current usage with [`/context`](https://code.claude.com/docs/en/commands). Worth running before a big task.

Three things that actually help:

1. **Start a new session for every new task.** Every task after the first in a session degrades in quality, because a medium-to-large task can easily burn 50,000+ tokens on its own, and research or skill or MCP use can push that past 100,000. Stack multiple tasks in one session and you get worse output and burn through your usage limit faster.
2. **Don't let Claude go on research tangents.** If it starts exploring files or searching topics it doesn't need, stop it. Every file and page it reads costs tokens.
3. **Be specific in your prompts.** Vague prompts make Claude read everything to figure out what you want. If you already know which files or sources it should use, say so directly, especially for technical decisions.

Eventually you'll hit the context limit anyway, and Claude will run [`/compact`](https://code.claude.com/docs/en/commands) on its own, summarizing the whole conversation into a shorter version. If it compacts itself mid-task, that's your cue to start a new session; self-triggered compaction causes a noticeable quality drop. If you're confident a task doesn't need a separate conversation, run `/compact` yourself and tell it exactly what to preserve.

There are community tools built specifically around context optimization too, worth looking into if you want to push this further.

### Checking Usage and Cost

`/context` tells you how full the window is, but it doesn't tell you how close you are to your actual plan limit. `/usage` (aliases `/cost` and `/stats`) does that. On a Pro or Max plan it shows how you're tracking against your usage window and when it resets; on API billing it shows real token consumption and dollar cost. It also breaks down `/loop` runs individually, so you can see which automation is quietly eating your budget. Worth checking alongside `/context` before starting anything big, not after you've already hit the wall.

## Checkpoints and /rewind

Not every bad session needs a fresh start. Claude Code automatically saves a checkpoint after every prompt, and `/rewind` (or pressing Esc twice on an empty prompt) opens a menu of everything you've sent this session so you can jump back to any of them. From there you can restore the code and the conversation together, restore just the code while keeping the conversation (useful when the edits went sideways but the discussion leading up to them was fine), restore just the conversation while leaving your files alone (useful when you want to redirect without losing work already done), or summarize everything from that point forward to free up context.

It's a lighter tool than starting over, and it's worth reaching for before you nuke a session that's mostly fine but took one bad turn. Checkpoints don't cover symlinked or hard-linked files, and they get deleted along with the session after 30 days, so it's not a substitute for actual version control.

## /loop

`/loop` takes a task and a time interval and keeps running that task on schedule, essentially an AI cron job. It's how I keep projects moving when I'm not actively at the keyboard. Automations I've used:

- **Auto-implement a GitHub issue.** Each run, Claude picks an open issue and works on it, so there's a PR waiting when I check back.
- **Security and bug sweep.** Scans the codebase for known vulnerabilities or bugs, and files a GitHub issue for anything it finds.
- **Feature brainstorming.** Looks at the codebase, PRs, and issues, and suggests features that would actually help the project.

You can also trigger automations off specific events rather than a fixed interval. Worth trying if you have a project that sits idle between sessions.

## Goal-Persistence Mode

A separate mode takes a goal and keeps working until it's either met or Claude needs your help. For example: "make sure every test passes and there are no type errors." Claude keeps iterating until that's true, rather than stopping after one pass.

## Agents and Sub-Agents

The main Claude chat is the primary agent, the one you always talk to. A sub-agent is a smaller Claude instance spun up for one job: a researcher, a reviewer, a debugger. You can create as many as you want, each with its own context window; it does its job and reports a summary back to the primary agent. The easiest way to make one is just telling Claude what the sub-agent should do.

Most people can't run sub-agents constantly, though, because each one is its own full conversation running in parallel, and on the $20 plan even a small multi-agent setup can burn through your entire usage limit before the task finishes. Sub-agents still meaningfully improve implementation quality if you can afford to run them, especially on a higher plan.

## [Worktrees](https://code.claude.com/docs/en/worktrees)

Worktrees let you check out multiple branches of the same repo at once. Each worktree copies the project into its own folder, which suits parallel development with AI well: instead of working on one branch at a time and waiting around, you work on several simultaneously in fully isolated folders, so agents don't interfere with each other. My workflow is essentially one worktree per chat. Claude Code has native worktree support.

## Alternatives to Claude Code

Claude Code isn't the only option, and most of what's above carries over to other tools:

- **[Codex](https://github.com/openai/codex).** OpenAI's version. The one I personally use most; the usage limits have been noticeably more generous.
- **[Open Code](https://opencode.ai/).** An open-source alternative to Claude Code that lets you plug in any model.
- **[Pi](https://pi.dev/).** A more minimalist setup, good if you want to build your own workflow from scratch.
- **[Cursor](https://cursor.com).** An IDE-and-agent combo, my pick when I want an actual IDE. Supports multiple model providers; I like their in-house models along with Composer for speed and cost.
- **[VS Code](https://code.visualstudio.com) + [GitHub Copilot](https://github.com/features/copilot).** The original.
- **[T3 Code](https://t3.codes/).** An open-source control plane for coding agents. If you already pay for several subscriptions (Claude Code, Codex, Cursor), it lets you use all of them from one application instead of juggling separate tools. If you only have a Claude subscription, you'll probably prefer Claude Code's own interface.

Pick whatever fits your workflow and budget.