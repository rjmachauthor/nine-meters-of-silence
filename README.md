# Nine Meters of Silence — Companion Simulations

![tests](https://github.com/rjmachauthor/nine-meters-of-silence/actions/workflows/tests.yml/badge.svg)

*Nine Meters of Silence* is a technothriller that leans on real engineering — fracture
mechanics, control theory, state estimation — to drive its plot. This repo is
where those claims get checked. Every technical number in the book that shows
up here has:

1. A **physics module** — the actual equations, implemented plainly
2. A **test** — asserting the book's stated number falls out of the real math
3. A **notebook** — an animation you can run and play with, no install required

If a claim can't survive its own test, that's a bug in the manuscript, and the
manuscript gets fixed — not the test.

## Run it yourself

Each notebook has a "Open in Colab" badge — click it, hit Run All, no local
setup needed. Or clone the repo and run locally:

```bash
pip install -r requirements.txt
pytest ch01/tests/ -v
jupyter notebook ch01/notebooks/
```

## Claims table

| Chapter | Phase | Claim | Real-world concept | Verified |
|---|---|---|---|---|
| 1 — Thermal Suicide | 6 — The Weld and the Countdown | Embrittled titanium spar fails in 42s via fatigue crack growth (real peer-reviewed Paris' Law constants + hydrogen-embrittlement K_IC data) | LEFM stress intensity + Paris' Law fatigue crack growth | ✅ [test](ch01/tests/test_crack_growth.py) + [notebook](ch01/notebooks/phase6_countdown.ipynb) — see [sources](ch01/CALIBRATION.md) |
| 1 — Thermal Suicide | 4 — MIMO Latency Loop | A ~0.2-0.27s control delay turns a stable system into a self-sustaining oscillation — matches the real 1977 Space Shuttle Enterprise PIO incident | Coupled MIMO state-space feedback, induced instability | ✅ [test](ch01/tests/test_mimo_latency.py) + [notebook](ch01/notebooks/phase4_mimo_latency.ipynb) — see [sources](ch01/CALIBRATION.md) |
| 1 — Thermal Suicide | 2 — The Sensor Ghost | IMU residuals stay flat during real flutter; a sudden bias fault (not slow drift — real drift is 1000x too slow) would blow the residual up instead | Kalman filter residual analysis (NIS) | ✅ [test](ch01/tests/test_sensor_ghost.py) + [notebook](ch01/notebooks/phase2_sensor_ghost.ipynb) — see [sources](ch01/CALIBRATION.md) |
| 1 — Thermal Suicide | 1 — Flutter | 20 Hz acoustic spike from aeroelastic flutter, well below a healthy mast's natural frequency | Structural resonance / effective stiffness loss | ✅ [test](ch01/tests/test_flutter.py) |
| 1 — Thermal Suicide | 3 — Sloshing Mass | Cable tension spikes 38.2 kN → 45 kN; implied load mass matches a real helicopter's rated sling capacity | Coupled pendulum + impulsive mass shift (fuel-slosh analogy) | ✅ [test](ch01/tests/test_sloshing_mass.py) — see [sources](ch01/CALIBRATION.md) |

Every claim above links to `ch01/CALIBRATION.md`, which lists a real,
clickable source (DOI, government regulation, or manufacturer/operator
data) for every sourced constant, tiered by reliability, and states
plainly which remaining numbers are disclosed engineering assumptions
rather than sourced facts.

## How this repo's math actually works (and how it's different from a first-principles simulation)

This is **not** a case of writing the physics first and letting the numbers
decide the story, the way Andy Weir famously worked out real orbital
mechanics for *The Martian* before writing the scenes around them. Here it
runs the other direction: the manuscript's numbers came first, and specific
loading parameters in each physics module were back-solved to reproduce
them.

To be direct about exactly what that means: the **governing equations are
real and unmodified** — Paris' Law, LEFM stress intensity, Kalman filtering,
these are standard, unaltered textbook physics. What's fitted, per chapter,
are specific inputs (a stress range, a growth-rate constant) chosen so the
real equations output the manuscript's stated result. Every fitted constant
is disclosed by name in that chapter's `CALIBRATION.md`, alongside which
values were pulled from published material data and which were solved for.

This is closer to how real forensic failure analysis works than it is to
first-principles design: an investigator doesn't run a blind simulation and
hope it matches a fracture surface — they start from the observed failure
and solve backward for the loading history that explains it. That's also,
not coincidentally, exactly what this book's protagonist does for a living.
Nothing here is hidden or discovered after the fact — if you want to check
that a fitted value is physically reasonable rather than invented, that's
what `CALIBRATION.md` is for.

## Structure

Each chapter gets its own folder, split three ways so the "is this true"
layer stays independent of the "does this look cool" layer:

```
ch01/
├── CALIBRATION.md   which constants are real vs. back-solved, and why
├── physics/         pure functions, no plotting, importable and testable
├── tests/           pytest assertions checking the book's stated numbers
└── notebooks/       Colab-ready animations, built on top of physics/
```

## Non-technical chapters

Not every chapter in the book is hard-SF. The literary/character-driven
chapters aren't forced into this framework — no simulations bolted onto
scenes that don't need them. What *does* apply everywhere is continuity
tracking (character timelines, recurring motifs, internal consistency
rules) — see `continuity/` (in progress) for that layer.
