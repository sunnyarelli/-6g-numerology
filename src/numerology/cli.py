"""Print the NR numerology table and per-scenario feasibility for 6G candidates."""
from __future__ import annotations

import argparse

from .core import SCENARIOS, Numerology, Scenario, assess, recommend


def print_table() -> None:
    print(f"{'mu':>3}{'SCS kHz':>9}{'slot us':>9}{'symbol us':>11}{'CP ns':>8}{'CP ovh':>8}"
          f"{'lat. slot us':>14}{'lat. 2sym us':>14}")
    for mu in range(7):
        n = Numerology(mu)
        print(f"{mu:>3}{n.scs_hz / 1e3:>9.0f}{n.slot_s * 1e6:>9.2f}{n.useful_symbol_s * 1e6:>11.3f}"
              f"{n.cp_s * 1e9:>8.0f}{n.cp_overhead * 100:>7.1f}%"
              f"{n.latency_s() * 1e6:>14.1f}{n.latency_s(symbols=2) * 1e6:>14.1f}")


def print_scenario(s: Scenario) -> None:
    print(f"\n{s.name}: DS {s.delay_spread_s * 1e9:.0f} ns, {s.speed_kmh:.0f} km/h "
          f"(fd {s.max_doppler_hz:.0f} Hz), max {s.max_rb} RB")
    for a in assess(s):
        flags = "".join(["" if a.cp_ok else " CP<DS", "" if a.rb_ok else " RB>cap",
                         "" if a.ici_ok else " ICI"])
        print(f"  mu={a.numerology.mu} {a.numerology.scs_hz / 1e3:>4.0f} kHz  {a.n_rb:>5} RB  "
              f"ICI SIR {a.ici_sir_db:5.1f} dB  {'OK' if a.feasible else 'x '}{flags}")
    r = recommend(s)
    print(f"  -> robust mu={r['robust']}, low-latency mu={r['low_latency']}")


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description="NR / 6G numerology explorer")
    p.add_argument("--fc", type=float, help="custom scenario carrier [Hz]")
    p.add_argument("--bw", type=float, default=200e6, help="bandwidth [Hz]")
    p.add_argument("--ds", type=float, default=300e-9, help="rms delay spread [s]")
    p.add_argument("--speed", type=float, default=120.0, help="UE speed [km/h]")
    p.add_argument("--max-rb", type=int, default=275)
    a = p.parse_args(argv)

    print_table()
    scenarios = [Scenario("custom", a.fc, a.bw, a.ds, a.speed, a.max_rb)] if a.fc else SCENARIOS
    for s in scenarios:
        print_scenario(s)


if __name__ == "__main__":
    main()
