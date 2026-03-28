import time
import threading
from collections import defaultdict, deque
from typing import Callable, Dict, List
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class MetricsTracker:
    def __init__(self, per_route_window: int = 100):
        self._lock = threading.Lock()
        self.total_requests = 0
        self.total_time_ms = 0.0
        self.error_count = 0
        # Per-route: store last N durations
        self._per_route: Dict[str, deque] = defaultdict(lambda: deque(maxlen=per_route_window))
        self._per_route_count: Dict[str, int] = defaultdict(int)

    def add_metric(self, duration_ms: float, route: str = "", status_code: int = 200):
        with self._lock:
            self.total_requests += 1
            self.total_time_ms += duration_ms
            if status_code >= 500:
                self.error_count += 1
            if route:
                self._per_route[route].append(duration_ms)
                self._per_route_count[route] += 1

    def get_average(self) -> float:
        with self._lock:
            if self.total_requests == 0:
                return 0.0
            return self.total_time_ms / self.total_requests

    def get_stats(self) -> dict:
        with self._lock:
            avg = self.total_time_ms / self.total_requests if self.total_requests else 0.0
            # Top 10 slowest routes by average
            route_avgs = []
            for route, times in self._per_route.items():
                if times:
                    route_avgs.append({
                        "route": route,
                        "avg_ms": round(sum(times) / len(times), 2),
                        "requests": self._per_route_count[route],
                    })
            route_avgs.sort(key=lambda x: x["avg_ms"], reverse=True)
            return {
                "total_requests": self.total_requests,
                "avg_response_time_ms": round(avg, 2),
                "error_count": self.error_count,
                "error_rate_pct": round(self.error_count / self.total_requests * 100, 2) if self.total_requests else 0.0,
                "top_routes": route_avgs[:10],
            }


metrics_tracker = MetricsTracker()


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000

        route = request.url.path
        metrics_tracker.add_metric(duration_ms, route=route, status_code=response.status_code)

        return response
