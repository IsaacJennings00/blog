---
title: "AI Safety Should Focus on the Harnesses Over Weights"
date: 2026-10-30
---

epistemic status: ongoing

In a recent column for the [New Scientist](https://www.newscientist.com/article/2596083-the-most-important-part-of-ai-chatbots-is-being-ignored/), Jacob Aron pointed out a category error that sits at the centre of how we talk about artificial intelligence. When we speak of ChatGPT or Claude, we speak as though we are addressing a singular entity: a large language model. We are not. At the bottom of the stack is a model that does one thing. It predicts the next likely token given a string of text. Between that statistical engine and the user sits a quieter, largely unexamined layer of software, called the harness.

A raw model has no memory, no access to a terminal, no capacity to browse the web, and no ability to pause and verify its own output. It is a brain in a vat, incapable of sustained action until another program feeds it a prompt and decides what to do with the reply. The harness is the program that does the feeding. It writes the hidden system instructions, manages the context window, intercepts requests, calls external APIs, executes code in sandboxes, and loops the model’s output back into its input until a task is finished.

As Aron notes, an AI firm, or an independent developer, can drastically increase the real world capability of a system without altering a single weight in the underlying neural network. You do not need to train GPT-7 to get a more dangerous or more capable agent if you can build a sharper harness around GPT-6. And yet, in the grand theatre of the AI safety debate, the harness barely registers.

*Why does our regulatory and philosophical obsession stop at the model weights?*

The first reason is an inherited metaphysic. Machine learning safety grew out of alignment theory, which treats the neural network as the sole locus of intelligence and moral risk. The model is expensive, emergent, and inscrutable; the harness is "mere" plumbing. A few thousand lines of conventional Python or TypeScript routing text back and forth. Plumbing is not glamorous. You do not win grants or summon existential dread at international summits by talking of retry loops and bash execution permissions. We have mistaken the mystery of the weights for the entirety of the machine.

But a text predictor does not act in the world. The harness is where prediction becomes a new space where agency and jurisdiction collide. It is the procedural law of the system: the layer that determines what tools the model may touch, what files it may read, when a refusal is triggered, and when an action is committed. Ignoring the harness because the model is more complex is like auditing the composition of metals in a jet turbine while declining to inspect the flight control software.

The second reason is regulatory convenience. Governments looking to govern artificial intelligence needed a chokepoint, and they found one in training compute. Executive orders, safety institutes, and legislative frameworks have coalesced around floating-point operations (10^{26} FLOPs) and frontier model releases. Compute is capital intensive, physical, and centralised. A regulator can count data centres and demand system cards before a frontier lab deploys a new set of weights.

It cannot easily bottleneck a harness. A harness does not require a billion dollar cluster or a hyperscaler balance sheet. It can be written over a weekend by a solo developer, published to a public repository by lunch, and wired into a commercial API by dinner. Because the state cannot police standard software development without abandoning the pretence of a free digital commons, the policy apparatus has largely pretended that "safety" is a property baked into the model prior to release.

This leads to a phenomena where safety is treated as a static substance inside the weights, rather than a relationship between a model, its scaffolding, and environment it is operates on or within.

This produces what safety evaluators call the "unhobbling" problem, though the legal world has an older name for it: a shift in de facto authority without a shift in formal mandate. When a frontier model is evaluated before deployment, it is tested inside a specific harness at a fixed moment in time. Months later, without a single weight changing, a new orchestration loop or tool integration unlocks latent capabilities the pre-deployment audit concluded were absent. A model that could not reliably exploit a software vulnerability in January does so in June. All because the neural network learned anything new, but because its scaffolding was rewritten to let it iterate, test against a compiler, and correct its own syntax errors.

This split in the stack fractures accountability. When an agentic system causes harm, where does the fault lie? The frontier lab points to its RLHF training, its constitutional principles, and its benchmark evaluations. The product team points to the unpredictability of the underlying model. The third-party developer wrapping an API in an autonomous loop operates entirely outside the visibility of both. By treating the harness as a neutral wrapper rather than the constitutive architecture of agency, everyone retains plausible deniability.

The irony is sharpest at the speculative end of the safety debate. For years, the nightmare scenario of recursive self improvement assumed an AI would have to rewrite its own neural architecture and retrain its own weights. A process requiring vast, detectable compute that human operators could simply switch off at the wall. Aron points to the far simpler path: an AI does not need to retrain its brain if it is allowed to rewrite its harness.

Language models are already unusually good at writing and debugging conventional software. And a harness is just conventional software. An agent given write-access to its own scaffolding can refine its memory retrieval, spin up specialised subagents, strip out latency, and construct better verification tools. Effectively ratcheting up its effective power in plain code while its underlying weights remain frozen and compliant with every compute threshold on the statute books.

This blindspot forms as something not entirely naive. It is a symptom of being taught to look at the cathedral of the frontier model while ignoring the scaffolding that actually lets it reach the street. We spend our political energy debating the soul of the ghost, while leaving the gears of the machine unexamined.

A model predicts tokens. A harness grants agency. Until the safety debate stops treating the surrounding software as mere interface, it is trying to control the dictionary while the printing press wires proliferates and embeds in more places and more places outside the realm of regulation.
