import pytest

from numerology.core import Numerology, Scenario, assess, recommend


@pytest.mark.parametrize("mu,scs,slot_us", [(0, 15e3, 1000), (1, 30e3, 500), (3, 120e3, 125), (6, 960e3, 15.625)])
def test_scs_and_slot(mu, scs, slot_us):
    n = Numerology(mu)
    assert n.scs_hz == scs
    assert n.slot_s * 1e6 == pytest.approx(slot_us)


def test_ts38211_cp_length_15khz():
    assert Numerology(0).cp_s * 1e6 == pytest.approx(4.6875, abs=1e-4)
    assert Numerology(0).useful_symbol_s * 1e6 == pytest.approx(66.667, abs=1e-3)


def test_cp_overhead_is_numerology_independent():
    assert Numerology(0).cp_overhead == pytest.approx(Numerology(4).cp_overhead, abs=1e-12)
    assert 0.06 < Numerology(1).cp_overhead < 0.075


def test_rb_count_close_to_ts38101():
    # TS 38.101-1: 100 MHz @ 30 kHz -> 273 RB
    assert 265 <= Numerology(1).n_rb(100e6) <= 275


def test_fft_size_power_of_two():
    n = Numerology(1).fft_size(100e6)
    assert n == 4096


def test_ici_worsens_with_doppler_and_improves_with_scs():
    assert Numerology(0).ici_sir_db(1000) < Numerology(0).ici_sir_db(100)
    assert Numerology(2).ici_sir_db(1000) > Numerology(0).ici_sir_db(1000)


def test_recommendation_respects_constraints():
    s = Scenario("t", 3.5e9, 100e6, 363e-9, 120)
    rec = recommend(s)
    feasible = {a.numerology.mu for a in assess(s) if a.feasible}
    assert rec["robust"] == min(feasible) and rec["low_latency"] == max(feasible)
    assert 0 not in feasible            # 100 MHz @ 15 kHz exceeds 275 RB


def test_infeasible_scenario_returns_none():
    s = Scenario("t", 30e9, 2e9, 2e-6, 500)
    assert recommend(s) == {"robust": None, "low_latency": None}
