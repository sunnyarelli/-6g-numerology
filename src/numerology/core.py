"""OFDM numerology / frame-structure explorer for NR and candidate 6G configurations.

Timing follows TS 38.211: Tc = 1/(480 kHz * 4096), kappa = 64, normal CP of
144*kappa*2^-mu Tc, with 16*kappa Tc added to the first symbol of every 0.5 ms.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil, log2, log10, pi

C = 299_792_458.0
TC = 1 / (480e3 * 4096)
KAPPA = 64
SYMBOLS_PER_SLOT = 14


@dataclass(frozen=True)
class Numerology:
    mu: int

    @property
    def scs_hz(self) -> float:
        return 15e3 * 2 ** self.mu

    @property
    def slots_per_ms(self) -> int:
        return 2 ** self.mu

    @property
    def slot_s(self) -> float:
        return 1e-3 / self.slots_per_ms

    @property
    def useful_symbol_s(self) -> float:
        return 2048 * KAPPA * 2 ** -self.mu * TC

    @property
    def cp_s(self) -> float:
        """Normal CP of a regular (not the half-subframe-boundary) symbol."""
        return 144 * KAPPA * 2 ** -self.mu * TC

    @property
    def cp_overhead(self) -> float:
        return 1 - SYMBOLS_PER_SLOT * self.useful_symbol_s / self.slot_s

    def n_rb(self, bandwidth_hz: float, utilization: float = 0.983) -> int:
        return int(bandwidth_hz * utilization // (12 * self.scs_hz))

    def fft_size(self, bandwidth_hz: float, utilization: float = 0.983) -> int:
        n_sc = 12 * self.n_rb(bandwidth_hz, utilization)
        return 2 ** max(7, ceil(log2(n_sc / 0.85)))     # keep >= 15 % oversampling

    def sample_rate_hz(self, bandwidth_hz: float) -> float:
        return self.fft_size(bandwidth_hz) * self.scs_hz

    def ici_sir_db(self, doppler_hz: float) -> float:
        """Approximate SIR from Doppler-induced ICI, (pi fd T)^2 / 3 (Jakes, small fd*T)."""
        x = pi * doppler_hz / self.scs_hz
        return float("inf") if x == 0 else -10 * log10(x ** 2 / 3)

    def latency_s(self, symbols: int = SYMBOLS_PER_SLOT, processing_tti: float = 2.0) -> float:
        """One-way air-interface latency estimate: 0.5 TTI alignment + 1 TTI + processing."""
        tti = self.slot_s * symbols / SYMBOLS_PER_SLOT
        return tti * (1.5 + processing_tti)


@dataclass
class Scenario:
    name: str
    fc_hz: float
    bandwidth_hz: float
    delay_spread_s: float           # rms delay spread
    speed_kmh: float
    max_rb: int = 275               # NR limit per carrier; 6G may relax it (set higher to explore)
    min_ici_sir_db: float = 25.0
    ds_factor: float = 3.0          # CP should cover ~3x rms delay spread

    @property
    def max_doppler_hz(self) -> float:
        return self.speed_kmh / 3.6 * self.fc_hz / C


@dataclass
class Assessment:
    numerology: Numerology
    n_rb: int
    cp_ok: bool
    ici_sir_db: float
    rb_ok: bool
    ici_ok: bool

    @property
    def feasible(self) -> bool:
        return self.cp_ok and self.rb_ok and self.ici_ok


def assess(s: Scenario, mus=range(7)) -> list:
    out = []
    for mu in mus:
        n = Numerology(mu)
        sir = n.ici_sir_db(s.max_doppler_hz)
        nrb = n.n_rb(s.bandwidth_hz)
        out.append(Assessment(n, nrb, n.cp_s >= s.ds_factor * s.delay_spread_s, sir,
                              0 < nrb <= s.max_rb, sir >= s.min_ici_sir_db))
    return out


def recommend(s: Scenario) -> dict:
    """Most robust (smallest feasible SCS, longest CP) and lowest-latency (largest feasible SCS)."""
    ok = [a for a in assess(s) if a.feasible]
    if not ok:
        return {"robust": None, "low_latency": None}
    return {"robust": ok[0].numerology.mu, "low_latency": ok[-1].numerology.mu}


SCENARIOS = [
    Scenario("FR1 macro 3.5 GHz / 100 MHz", 3.5e9, 100e6, 363e-9, 120),
    Scenario("FR3 macro 7 GHz / 200 MHz", 7e9, 200e6, 363e-9, 120),
    Scenario("FR3 UMi 15 GHz / 400 MHz", 15e9, 400e6, 129e-9, 60),
    Scenario("FR3 HST 10 GHz / 200 MHz", 10e9, 200e6, 100e-9, 500),
    Scenario("FR2 hotspot 28 GHz / 400 MHz", 28e9, 400e6, 66e-9, 30),
    Scenario("6G 15 GHz / 800 MHz, 550 RB cap", 15e9, 800e6, 129e-9, 60, max_rb=550),
]
