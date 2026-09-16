# 🤠 BOSSMEN WENBIGO v0.2
### AI QUICK-DRAW DUEL — THE DUEL HAS SOUND

![BOSSMEN WENBIGO](bossmen_wenbigo.png)

> **Two AI cowboys. One signal. Who draws first?**

BOSSMEN WENBIGO is a tiny AI-vs-AI quick-draw duel built in Python. BLOON and QWENY face each other, wait for a random **DRAW!** signal, and fire according to stochastic reaction-time models. The game measures and displays the observed reaction time in milliseconds.

This is **computer vs computer**. You just watch the algorithms argue with bullets.

## v0.2 — The Duel Has Sound

The v0.2 build adds:

- 🔊 Event-driven sound effects
- 💬 Local deterministic character dialogue
- 🎙️ Optional announcer lines
- 🤠 Western terminal presentation
- ⏱️ Measured reaction-time display
- 📊 Match statistics
- 🧪 Acceptance tests

Audio is optional. On Windows the standard-library `winsound` backend is available; on POSIX systems the terminal bell remains the fallback. An optional `pygame` backend can provide synthesized/custom sound effects.

## Gameplay

A round follows the sequence:

```text
READY
  ↓
WAIT...
  ↓
DRAW!
  ↓
BANG!
  ↓
REACTION TIME
  ↓
RESULT
```

Matches are **best of 5**, first to 3 wins. A very close reaction-time result can be declared a draw, and a double false-start creates a void round and replay.

## The Gunslingers

### BLOON

**Fast but wild.**

- Base reaction: 135 ms
- Variance: 25 ms
- False-start probability: 2%
- Lapse chance: 12%

### QWENY

**Slow but steady.**

- Base reaction: 125 ms
- Variance: 10 ms
- False-start probability: 1%
- Lapse chance: 5%

The reaction model is a **game simulation**, not a model of human neuroscience or machine cognition.

## Timing

The timing core uses Python's monotonic high-resolution timer:

```python
time.perf_counter()
```

The game stamps `t0` at the draw signal, then records the elapsed time when each AI fires:

```text
reaction_time = shot_time - t0
```

The displayed milliseconds are derived from the measured elapsed time, not simply copied from the AI's planned reaction value.

## Project Structure

```text
bloon_wenbigo/
├── ai.py
├── audio.py
├── config.py
├── dialogue.py
├── duel.py
├── game.py
├── main.py
├── renderer.py
├── stats.py
├── tests.py
├── README.md
└── bossmen_wenbigo.png
```

## Run

Python 3.8+ is sufficient for the core game. No external package is required for the fallback audio path.

```bash
python main.py
```

Optional richer audio backend:

```bash
pip install pygame-ce
```

## Controls

| Key | Action |
|---|---|
| `SPACE` / `ENTER` | Start / continue |
| `R` | Restart match |
| `ESC` / `Q` | Quit |

## Configuration

All main gameplay parameters live in `config.py`, including:

- audio on/off
- dialogue on/off
- announcer on/off
- draw-delay range
- AI reaction parameters
- tie tolerance
- match length
- result pacing

## Philosophy

We could have built a benchmark.

We could have generated a CSV.

We could have plotted distributions.

Instead, we gave two algorithms cowboy hats.

Underneath the joke are real programming ideas: stochastic simulation, event timing, state machines, statistics, modular design, and observable AI behavior.

> **It's not just a test. It's a duel.**

🔫 **Draw fast. Think faster.**
