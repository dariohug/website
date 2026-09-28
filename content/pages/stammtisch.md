---
title: "Stammtisch: a Schieber Jass AI"
---

**Stammtisch** plays *Schieber*, the Swiss Jass variant, and coaches you through
your own games. It is a C++17 engine — rules and Weis/Stöck on bitboards, an
exact double-dummy solver, a PIMC search and its own neural-network inference —
with a thin Python layer for training, review and the arena.

Code on GitHub: [dariohug/stammtisch](https://github.com/dariohug/stammtisch).

**[Play a round against it →](/stammtisch/play/)** — the whole engine is compiled to
WebAssembly and runs in your browser. Nothing is sent to a server, because there
is no server: pick an opponent from the table below, play one seat or your whole
team, and leave the coach on if you want every decision judged as you make it.

## The idea

Jass is a game of *imperfect* information: you see your nine cards and the cards
already played, never the other three hands. So the engine does the obvious
thing — it guesses, many times over.

For every card it could play it samples complete deals that are consistent with
everything it knows: its own hand, the played cards, who failed to follow suit,
the Weis that were shown. Each sample is then played out by a fast policy until
only the last few tricks remain, and those are solved **exactly** by the
double-dummy solver. Averaging over the samples gives each card an expected
value in card points. That is PIMC — perfect-information Monte Carlo.

Two things make the guesses good rather than uniform. The samples are weighted
by what the opponents' trump call and card play revealed about their hands. And
the playout policy is not random but a network trained by imitation on
**65.6 million human decisions** from 1'821'878 real Swisslos games.

The exact endgame is what keeps the whole thing honest, and it is cheap only
because it is late: with five tricks left a solve averages 1.15 ms, with eight
it averages 1.8 seconds. The search stops guessing exactly when guessing would
start to hurt.

| agent | what it does | Elo |
|---|---|---|
| `pimc:roll=strong` | search, played out by the distilled net | 1654 |
| `pimc` | search, played out by the imitation net | 1651 |
| `net:strong` | one net pass, distilled from the search | 1628 |
| `net` | one net pass, imitating 65.6 M human decisions | 1620 |
| `heuristic` | hand-written rules, no network at all | 1500 |

Elo comes from a duplicate-deal gauntlet: every pair plays the same deals with
the seats swapped, so the cards cancel out and only the play is measured. All
five are selectable in the browser version. In wasm a `pimc` move takes about
100 ms, the networks answer instantly.

## The coach

The same machinery that picks a move can judge one. Write a round down in a
small text format and the review estimates, for every decision you made, how
many card points each alternative was worth — from *your* information, not with
all cards open. A separate hindsight column shows the best card with everything
visible, which is exact and only appears in the last tricks.

A decision only counts as a mistake when the loss exceeds twice its standard
error, so sampling noise is never reported as a blunder. Each real mistake gets
a one-line reason taken from the actual trick. The
[browser version](/stammtisch/play/) runs the same coach live, one decision at a
time.

![A reviewed round: each trick with the engine's verdict on every decision, the point loss with its standard error, and a one-line reason for each mistake](/projects/stammtisch_review.png)

The training data are the Swisslos Schieber logs prepared by HSLU
(Prof. Thomas Koller) for the *Deep Learning for Games* module: 1'821'878 games
played between October 2017 and April 2018. Used with permission; the raw logs
are not redistributed here, only the networks trained from them.

## Validating the rules

Before trusting any of it, the engine replays all 1'821'878 logged games and
checks every card against its own rule implementation. All of them pass. It is
also differentially tested against HSLU's `jass-kit`, the reference
implementation — which turned up a bug in the reference: when two trumps are
already in a trick, `jass-kit` picks the highest by card index rather than by
trump rank, so it permits undertrumping in about 0.15 % of random positions. The
human data contains no such move, so only the reference is wrong.

## The report

The full progress log — plan, data, engine, agents, arena and validation — is
below.

<div class="pdf-embed"><embed src="/projects/stammtisch_report.pdf" type="application/pdf"></div>

[Download the PDF](/projects/stammtisch_report.pdf)
