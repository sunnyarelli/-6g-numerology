# 6g-numerology

[![CI](https://github.com/sunnyarelli/-6g-numerology/actions/workflows/ci.yml/badge.svg)](https://github.com/sunnyarelli/-6g-numerology/actions/workflows/ci.yml)

OFDM **numerology and frame-structure explorer** for NR and candidate 6G deployments. The Rel-20 6G study revisits
numerology for FR3 and wider carriers: which subcarrier spacing balances CP length (delay spread), ICI (Doppler),
RB count per carrier and latency?

Pure Python.

## What it does

- Exact TS 38.211 timing: Tc, κ = 64, normal CP of 144·κ·2^-μ·Tc, slot and symbol durations for μ = 0…6.
- Per-numerology RB count, FFT size, sample rate, CP overhead, and a slot / mini-slot latency estimate.
- Scenario check (carrier, bandwidth, rms delay spread, speed, RB cap):
  - **CP ≥ 3 × rms delay spread**
  - **Doppler ICI SIR ≥ 25 dB**, using `(π·f_d/Δf)²/3`
  - **N_RB ≤ cap** (275 in NR; raise it to explore 6G wider carriers)
- Recommends the most robust (smallest feasible SCS) and the lowest-latency (largest feasible SCS) numerology.

## Quick start

```bash
pip install -e ".[dev]"
pytest -q
numerology                                         # built-in FR1 / FR3 / FR2 / 6G scenarios
numerology --fc 12e9 --bw 400e6 --ds 150e-9 --speed 250 --max-rb 550
```

Sample output:

```
 mu  SCS kHz  slot us  symbol us   CP ns  CP ovh  lat. slot us  lat. 2sym us
  0       15  1000.00     66.667    4688    6.7%        3500.0         500.0
  1       30   500.00     33.333    2344    6.7%        1750.0         250.0
  2       60   250.00     16.667    1172    6.7%         875.0         125.0
  3      120   125.00      8.333     586    6.7%         437.5          62.5
  ...

FR3 macro 7 GHz / 200 MHz: DS 363 ns, 120 km/h (fd 778 Hz), max 275 RB
  mu=1   30 kHz    546 RB  ICI SIR  26.5 dB  x  RB>cap
  mu=2   60 kHz    273 RB  ICI SIR  32.6 dB  OK
  mu=3  120 kHz    136 RB  ICI SIR  38.6 dB  x  CP<DS
```

The FR3 high-speed-train scenario (10 GHz, 500 km/h) has **no** feasible NR numerology under these criteria. That
kind of finding motivates the 6G work on extended CP, Doppler-robust reference signals and new waveforms.

## Assumptions and limitations

- Normal CP only. The longer first symbol of every 0.5 ms is ignored in per-symbol figures but included in the CP overhead.
- Spectral utilization defaults to 98.3 %, close to the TS 38.101 maximum transmission bandwidth.
- The latency model is 0.5 TTI alignment + 1 TTI transmission + 2 TTI processing. It is meant for comparing
  numerologies, not as a spec-accurate budget.

## References

- 3GPP TS 38.211 §4 (numerology, frame structure), §5.3 (OFDM baseband)
- 3GPP TS 38.101-1/-2 (max transmission bandwidth configuration)
- 3GPP TR 38.913 / IMT-2030 requirements (latency targets)

## License

MIT
