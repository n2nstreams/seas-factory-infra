#!/usr/bin/env python3
"""
Lightweight budget guardrails and circuit breaker utilities for agent jobs.

- BudgetGuard: enforce per-job token/cost budgets
- CircuitBreaker: stop runaway loops on consecutive failures
"""
from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Optional


@dataclass
class BudgetGuard:
    max_tokens: int
    max_cost_usd: float
    tokens_used: int = 0
    cost_used_usd: float = 0.0

    def can_spend(self, tokens: int, cost_usd: float) -> bool:
        if self.tokens_used + tokens > self.max_tokens:
            return False
        if self.cost_used_usd + cost_usd > self.max_cost_usd:
            return False
        return True

    def record_spend(self, tokens: int, cost_usd: float) -> None:
        if not self.can_spend(tokens, cost_usd):
            raise RuntimeError("Budget exceeded: refusing to continue")
        self.tokens_used += tokens
        self.cost_used_usd += cost_usd


@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    reset_timeout_sec: int = 60
    consecutive_failures: int = 0
    opened_at_epoch_sec: Optional[float] = None

    def record_success(self) -> None:
        self.consecutive_failures = 0
        self.opened_at_epoch_sec = None

    def record_failure(self) -> None:
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.failure_threshold:
            self.opened_at_epoch_sec = time.time()

    @property
    def is_open(self) -> bool:
        if self.opened_at_epoch_sec is None:
            return False
        if (time.time() - self.opened_at_epoch_sec) >= self.reset_timeout_sec:
            # Half-open state; allow next attempt
            self.consecutive_failures = 0
            self.opened_at_epoch_sec = None
            return False
        return True


