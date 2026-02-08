"""Priority queue: drain by severity (P0 first)."""

from __future__ import annotations

import heapq

from ai.models.report import Severity
from ai.routing.types import RoutedAlert

SEVERITY_PRIORITY: dict[Severity, int] = {
    Severity.P0: 0,
    Severity.P1: 1,
    Severity.P2: 2,
    Severity.P3: 3,
}


class PriorityAlertQueue:
    """FIFO by severity; drain() returns P0 first."""

    def __init__(self) -> None:
        self._heap: list[tuple[int, int, RoutedAlert]] = []
        self._seq = 0

    def add(self, routed_alert: RoutedAlert) -> None:
        priority = SEVERITY_PRIORITY.get(routed_alert.report.severity, 4)
        self._seq += 1
        heapq.heappush(self._heap, (priority, self._seq, routed_alert))

    def drain(self) -> list[RoutedAlert]:
        out: list[RoutedAlert] = []
        while self._heap:
            _, _, routed = heapq.heappop(self._heap)
            out.append(routed)
        return out

    def __len__(self) -> int:
        return len(self._heap)
