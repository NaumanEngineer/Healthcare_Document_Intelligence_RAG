"""Tests for Week 26 operational assurance gate."""

from __future__ import annotations

from src.evaluation.run_week26_operational_assurance_gate import (
    run_week26_operational_assurance_gate,
)


def test_operational_gate_passes():
    report = (
        run_week26_operational_assurance_gate()
    )

    assert report[
        "overall_status"
    ] == "PASS"


def test_adversarial_layer_passes():
    report = (
        run_week26_operational_assurance_gate()
    )

    assert report[
        "adversarial_assurance"
    ][
        "status"
    ] == "PASS"

    assert report[
        "adversarial_assurance"
    ][
        "mismatched_case_count"
    ] == 0


def test_system_safety_layer_passes():
    report = (
        run_week26_operational_assurance_gate()
    )

    assert report[
        "system_safety"
    ][
        "status"
    ] == "PASS"

    assert report[
        "system_safety"
    ][
        "failed_case_count"
    ] == 0


def test_failure_injection_layer_passes():
    report = (
        run_week26_operational_assurance_gate()
    )

    assert report[
        "failure_injection"
    ][
        "status"
    ] == "PASS"

    assert report[
        "failure_injection"
    ][
        "mismatched_case_count"
    ] == 0


def test_failure_injection_has_no_unsafe_pass():
    report = (
        run_week26_operational_assurance_gate()
    )

    assert report[
        "failure_injection"
    ][
        "unsafe_pass_case_ids"
    ] == []


def test_all_gate_checks_pass():
    report = (
        run_week26_operational_assurance_gate()
    )

    checks = report[
        "gate"
    ][
        "checks"
    ]

    assert checks

    assert all(
        checks.values()
    )


def test_no_failed_gate_checks():
    report = (
        run_week26_operational_assurance_gate()
    )

    assert report[
        "gate"
    ][
        "failed_checks"
    ] == []