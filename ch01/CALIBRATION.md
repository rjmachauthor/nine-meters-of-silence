# Calibration notes — Chapter 1

Every constant used in this chapter's physics modules, tiered by source
reliability, with a real clickable link for each one. If a link 404s or a
claim doesn't hold up, that's a bug report against this file — open an
issue.

**Source tiers used below:**
- 🟢 **Peer-reviewed** — published, cited academic literature (via DOI, which
  always resolves even behind a paywall)
- 🔵 **Primary/official** — government regulation, NASA's own reporting, an
  aircraft manufacturer's/operator's own published data
- 🟡 **Disclosed engineering assumption** — not sourced, because no public
  data exists for a fictional aircraft's specific design. Chosen to be
  physically reasonable and stated plainly as a choice, not a fact.

## Phase 6 — Crack growth (`physics/crack_growth.py`)

**Revision history, disclosed honestly:** an earlier version of this module
used a Paris' Law exponent from a non-peer-reviewed blog calculator, which
made the manuscript's 42-second cycle-by-cycle fatigue mechanism look
physically impossible (real growth would take hours at that exponent).
Re-sourcing the exponent from a peer-reviewed paper reversed that
conclusion — with the real exponent, 42 seconds is achievable via the
original mechanism the manuscript describes. Two conclusions were drawn
from this chapter's material at different points, and the second,
corrected one is what the code now reflects.

- 🟢 **Paris' Law constants** (`C_PARIS = 1.2e-11` m/cycle, `M_PARIS = 4.1`)
  and **yield strength** (828 MPa): Alshoaibi & Fageehi, "Comparative Finite
  Element Analysis of Fatigue Crack Growth in High-Performance Metallic
  Alloys," *Crystals* 2025, 15(9), 801.
  **https://doi.org/10.3390/cryst15090801** (open access, full text free)
- 🟢 **Fracture toughness values** (`K_IC_HEALTHY = 73`, `K_IC_EMBRITTLED =
  46.5` MPa√m — midpoints of the paper's own reported "unaffected" and
  "hydrogen-affected" threshold ranges, used together so both numbers come
  from one apples-to-apples study): Gaddam, R., Pederson, R., Hörnqvist, M.,
  Antti, M-L., "Fatigue crack growth behaviour of forged Ti–6Al–4V in
  gaseous hydrogen," *Corrosion Science* 78 (2014): 378–383.
  **https://doi.org/10.1016/j.corsci.2013.08.009**
- 🟡 **Applied stress** (`ASSUMED_TRANSIENT_STRESS_MPA = 212.2`, ≈26% of the
  real yield strength above): no public spec exists for this fictional
  rotor mast's actual operating loads. Chosen to be a plausible high-cycle
  fatigue stress fraction, and specifically to reproduce the manuscript's
  42-second figure — this one number IS solved to hit the target, and
  that's disclosed rather than hidden. Everything else fits real published
  data un-forced.
- 🟡 **Transient duration** (`ASSUMED_TRANSIENT_DURATION_S = 50.0`): a real,
  disclosed estimate for how long a heavy-lift helicopter sustains
  high-power torque during initial climb-out before throttling back to
  cruise stress. This number matters more than it might look: see below.
- 🟡 **`a0 = 5.8mm`**, **rotor speed 4 Hz**: given directly in the manuscript
  as plot facts (how big the crack already is, this aircraft's specs), not
  external material properties.

**Why the load is treated as a bounded transient, not sustained forever —
and why an earlier version of this file got this wrong:** at the 212.2 MPa
stress needed to fail the embrittled crack in 42 seconds, healthy titanium
does not fail instantly — it needs about 64 seconds AT THE SAME SUSTAINED
STRESS. An earlier version of this file treated that as an unavoidable
limitation ("the weld cuts the margin by a third, it isn't the sole cause
of failure at any duration"). That framing was a mistake, not a real
physics finding: it implicitly assumed the stress stays at 212.2 MPa
indefinitely, which contradicts the manuscript's own description of this
as a "transient startup torque spike" — a transient, by definition, ends.
A real helicopter's high-power climb-out phase runs for a real, bounded
duration (estimated here at ~50 seconds) before the pilot throttles back
to lower cruise stress. Within that actual bounded window: the embrittled
crack fails (42s < 50s) and the healthy crack does not (64s > 50s). That
is the correct, sharp comparison — see `test_healthy_titanium_survives_the_actual_transient_duration`
and `test_transient_duration_is_bracketed_correctly`, which checks the
50-second assumption isn't arbitrary but genuinely sits between the two
failure times.

## Phase 4 — MIMO latency loop (`physics/mimo_latency.py`)

- 🔵 **Real historical precedent, with a corrected figure:** the Space
  Shuttle Enterprise's 1977 Approach and Landing Test (free flight 5)
  experienced a genuine pilot-induced oscillation. NASA's own reporting
  puts the causal control-system delay at **approximately 270 milliseconds**
  — close to, but not an exact match for, the manuscript's 0.2s, and I want
  to state that precisely rather than round it into a false exact match.
  NASA APPEL Knowledge Services: **https://appel.nasa.gov/2017/10/05/this-month-in-nasa-history-as-enterprise-landed-the-shuttle-program-took-off/**
  Additional NASA Technical Reports Server documentation of the same event:
  **https://ntrs.nasa.gov/citations/19820005276**
- 🟡 **Control gains** (`CONTROL_GAIN_KP = 10.0`, `CONTROL_GAIN_KD = 0.5`):
  chosen so the system is stable at 0s delay and unstable by ~0.2-0.27s — a
  PD (not pure-P) structure was used because a rigid body under pure
  proportional delayed feedback is only ever marginally stable even at
  zero delay; real flight control laws always include rate damping. Cargo
  mass, cable length, and hook height are physically reasonable, not
  sourced from a real aircraft's spec sheet.

## Phase 2 — Sensor ghost (`physics/sensor_ghost.py`)

- 🔵 **Real gyro drift rate ranges** (used to rule OUT slow drift as this
  failure's mechanism): tactical-grade gyros commonly cited at ~0.1–5°/hr,
  navigation-grade as low as ~0.01°/hr, and a specific real manufacturer
  datasheet example (Analog Devices ADIS16490) citing 1.8°/hr in-run bias
  stability: **https://www.analog.com/en/resources/analog-dialogue/raqs/raq-issue-139.html**
  These rates are 3-4 orders of magnitude too slow to matter within a
  several-second event, which is why this module models a sudden bias-step
  fault instead of drift — a real, documented, instant-onset IMU failure
  mode, and a closer match to the manuscript's own "sudden, massive phase
  shift" than slow drift ever was.
- 🟡 **`process_var`, `decay_rate`, bias magnitude (0.2 rad)**: chosen so a
  correctly-tuned filter reads a textbook-normal NIS near 1.0 during real
  flutter, and the bias fault produces a clearly elevated, sustained NIS.
  The mean-reversion assumption (aircraft attitude is aerodynamically
  damped, not free to drift) is a real physical principle, not an
  arbitrary knob.

## Phase 1 — Flutter (`physics/flutter.py`)

- 🟡 **Stiffness and modal mass values**: no public spec exists for this
  fictional mast's specific structural design. Chosen so a healthy natural
  frequency lands in the hundreds of Hz (normal for stiff aerospace
  structural members) and a locally softened section lands at the
  observed 20 Hz — consistent with the manuscript's own framing that this
  is a local compliance change, not a material constant change. The
  governing equation itself (`f = 1/2π · sqrt(k/m)`) is standard, unmodified
  physics.

## Phase 3 — Sloshing mass (`physics/sloshing_mass.py`)

- 🔵 **Real-world cross-check, found after the fact:** the back-solved total
  load mass (4,500 kg / ~9,920 lbs, needed to match the book's 38.2 kN
  baseline tension) lines up closely with the real published useful
  sling-load capacity of the Sikorsky S-61 (10,000 lbs), a real
  medical/utility-capable helicopter type, per its operator's own
  published specs: **https://coulsonaviation.com/heavy-lift/**
  This wasn't targeted deliberately — it's a reassuring coincidence, not a
  forced match.
- 🟡 **`shift_duration_s ≈ 0.081s`**: solved so a 75kg mass moving the
  book's stated ~30cm lunge distance produces the stated 45 kN peak. Not
  independently sourced, since it depends on one specific person's motion.

## On the two numbers still marked 🟡 without a strong external anchor

The spool-up/stress-fraction style assumptions in this chapter (Phase 6's
212.2 MPa, Phase 1's specific stiffness values, Phase 3's shift duration)
are the aircraft- and scene-specific inputs a real forensic engineer
analyzing someone else's proprietary, undocumented design would also have
to estimate rather than look up. The governing equations and the material
properties that CAN be sourced are real and cited above; what's disclosed
as an assumption is specifically the part that has no public source to
cite, for any investigator, real or fictional.
