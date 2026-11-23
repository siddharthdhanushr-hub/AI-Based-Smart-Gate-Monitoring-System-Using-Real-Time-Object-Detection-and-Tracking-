"""
Unit tests for 2D vector geometry and gate line crossing calculations.
"""

import pytest
from backend.app.counting.gate_geometry import GateLine, Point


@pytest.fixture
def horizontal_gate_line():
    # Horizontal line from (100, 300) to (500, 300)
    return GateLine((100, 300), (500, 300))


def test_gate_line_intersection(horizontal_gate_line):
    # Segment crossing through the gate line
    pt_above = Point(300, 200)
    pt_below = Point(300, 400)
    assert horizontal_gate_line.intersects(pt_above, pt_below) is True


def test_gate_line_non_intersection(horizontal_gate_line):
    # Segment completely above the gate line
    p1 = Point(300, 100)
    p2 = Point(300, 250)
    assert horizontal_gate_line.intersects(p1, p2) is False

    # Segment outside horizontal span
    p3 = Point(50, 200)
    p4 = Point(50, 400)
    assert horizontal_gate_line.intersects(p3, p4) is False


def test_direction_classification_entry(horizontal_gate_line):
    # Moving from top (negative cross-product) to bottom (positive cross-product)
    pt_prev = Point(300, 200)
    pt_curr = Point(300, 400)
    direction = horizontal_gate_line.classify_movement_direction(pt_prev, pt_curr)
    assert direction == "ENTRY"


def test_direction_classification_exit(horizontal_gate_line):
    # Moving from bottom to top
    pt_prev = Point(300, 400)
    pt_curr = Point(300, 200)
    direction = horizontal_gate_line.classify_movement_direction(pt_prev, pt_curr)
    assert direction == "EXIT"


def test_direction_classification_parallel_movement(horizontal_gate_line):
    # Moving parallel above the line
    pt_prev = Point(150, 200)
    pt_curr = Point(350, 200)
    direction = horizontal_gate_line.classify_movement_direction(pt_prev, pt_curr)
    assert direction is None
