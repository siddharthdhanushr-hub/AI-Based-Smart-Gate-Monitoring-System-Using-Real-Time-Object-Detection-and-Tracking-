"""
2D Vector Geometry and Gate Line Crossing Mathematics.
Computes segment intersection and signed cross-product directional classification.
"""

from typing import Tuple, List, Optional
import math


class Point:
    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

    def to_tuple(self) -> Tuple[int, int]:
        return int(round(self.x)), int(round(self.y))

    def distance_to(self, other: "Point") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"


class GateLine:
    """Represents a virtual gate line segment defined by endpoints P1 and P2."""

    def __init__(self, p1: Tuple[float, float], p2: Tuple[float, float]):
        self.p1 = Point(p1[0], p1[1])
        self.p2 = Point(p2[0], p2[1])

    @property
    def length(self) -> float:
        return self.p1.distance_to(self.p2)

    def cross_product_sign(self, p: Point) -> float:
        """
        Calculates signed 2D cross-product (determinant):
        (p2.x - p1.x)*(p.y - p1.y) - (p2.y - p1.y)*(p.x - p1.x)
        Positive indicates one side of the directed line, negative indicates the other.
        """
        return (self.p2.x - self.p1.x) * (p.y - self.p1.y) - (self.p2.y - self.p1.y) * (p.x - self.p1.x)

    @staticmethod
    def _orientation(p: Point, q: Point, r: Point) -> int:
        """
        Finds orientation of ordered triplet (p, q, r).
        0 -> Collinear
        1 -> Clockwise
        2 -> Counterclockwise
        """
        val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
        if abs(val) < 1e-6:
            return 0
        return 1 if val > 0 else 2

    @staticmethod
    def _on_segment(p: Point, q: Point, r: Point) -> bool:
        """Given collinear points p, q, r, checks if point q lies on segment pr."""
        return (
            q.x <= max(p.x, r.x) and q.x >= min(p.x, r.x) and
            q.y <= max(p.y, r.y) and q.y >= min(p.y, r.y)
        )

    def intersects(self, seg_start: Point, seg_end: Point) -> bool:
        """
        Determines whether segment [seg_start, seg_end] intersects the gate line [p1, p2].
        """
        p1, q1 = self.p1, self.p2
        p2, q2 = seg_start, seg_end

        o1 = self._orientation(p1, q1, p2)
        o2 = self._orientation(p1, q1, q2)
        o3 = self._orientation(p2, q2, p1)
        o4 = self._orientation(p2, q2, q1)

        # General case
        if o1 != o2 and o3 != o4:
            return True

        # Special Cases (collinear on-segment)
        if o1 == 0 and self._on_segment(p1, p2, q1):
            return True
        if o2 == 0 and self._on_segment(p1, q2, q1):
            return True
        if o3 == 0 and self._on_segment(p2, p1, q2):
            return True
        if o4 == 0 and self._on_segment(p2, q1, q2):
            return True

        return False

    def classify_movement_direction(self, pt_prev: Point, pt_curr: Point) -> Optional[str]:
        """
        Checks if movement from pt_prev to pt_curr crosses the gate line.
        If it does, returns 'ENTRY' or 'EXIT'.
        Returns None if no crossing occurs.
        """
        if not self.intersects(pt_prev, pt_curr):
            return None

        sign_prev = self.cross_product_sign(pt_prev)
        sign_curr = self.cross_product_sign(pt_curr)

        # Standard convention: moving from negative half-plane to positive -> ENTRY
        # moving from positive half-plane to negative -> EXIT
        if sign_prev < 0 and sign_curr >= 0:
            return "ENTRY"
        elif sign_prev > 0 and sign_curr <= 0:
            return "EXIT"

        return None
