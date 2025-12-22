#!/usr/bin/env python3
"""
Cost Configuration - Settings for cost tracking system.

Loads configuration from environment variables and config files.

Usage:
    from lib.cost_config import CostConfig, get_config

    config = get_config()
    print(config.budget_limit)
    print(config.currency_rates)
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Default values
DEFAULT_BUDGET_LIMIT = 15.00
DEFAULT_WARNING_PERCENT = 75
DEFAULT_CRITICAL_PERCENT = 90
DEFAULT_AUTO_STOP = True

DEFAULT_CURRENCY_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "BRL": 6.10,
    "CAD": 1.36,
    "AUD": 1.53,
    "JPY": 149.50,
}

DEFAULT_DISPLAY_CURRENCIES = ["USD", "EUR", "GBP", "BRL"]


@dataclass
class CostConfig:
    """Cost tracking configuration."""

    # Budget settings
    budget_context: float = 3.00
    budget_dev: float = 15.00
    budget_review: float = 5.00

    # Alert thresholds
    warning_percent: int = DEFAULT_WARNING_PERCENT
    critical_percent: int = DEFAULT_CRITICAL_PERCENT
    auto_stop: bool = DEFAULT_AUTO_STOP

    # Currency settings
    display_currency: str = "USD"
    currency_rates: dict[str, float] = field(default_factory=lambda: DEFAULT_CURRENCY_RATES.copy())
    display_currencies: list[str] = field(default_factory=lambda: DEFAULT_DISPLAY_CURRENCIES.copy())

    @classmethod
    def from_env(cls) -> "CostConfig":
        """Load configuration from environment variables."""
        config = cls()

        # Budget limits
        if os.getenv("MAX_BUDGET_CONTEXT"):
            config.budget_context = float(os.getenv("MAX_BUDGET_CONTEXT"))
        if os.getenv("MAX_BUDGET_DEV"):
            config.budget_dev = float(os.getenv("MAX_BUDGET_DEV"))
        if os.getenv("MAX_BUDGET_REVIEW"):
            config.budget_review = float(os.getenv("MAX_BUDGET_REVIEW"))

        # Alert thresholds
        if os.getenv("COST_WARNING_PERCENT"):
            config.warning_percent = int(os.getenv("COST_WARNING_PERCENT"))
        if os.getenv("COST_CRITICAL_PERCENT"):
            config.critical_percent = int(os.getenv("COST_CRITICAL_PERCENT"))
        if os.getenv("COST_AUTO_STOP"):
            config.auto_stop = os.getenv("COST_AUTO_STOP").lower() in ("true", "1", "yes")

        # Currency settings
        if os.getenv("COST_DISPLAY_CURRENCY"):
            config.display_currency = os.getenv("COST_DISPLAY_CURRENCY")

        # Currency rates from environment
        if os.getenv("CURRENCY_RATE_EUR"):
            config.currency_rates["EUR"] = float(os.getenv("CURRENCY_RATE_EUR"))
        if os.getenv("CURRENCY_RATE_GBP"):
            config.currency_rates["GBP"] = float(os.getenv("CURRENCY_RATE_GBP"))
        if os.getenv("CURRENCY_RATE_BRL"):
            config.currency_rates["BRL"] = float(os.getenv("CURRENCY_RATE_BRL"))

        return config

    @classmethod
    def from_file(cls, config_path: Path) -> "CostConfig":
        """Load configuration from JSON file."""
        config = cls()

        if not config_path.exists():
            return config

        try:
            with open(config_path) as f:
                data = json.load(f)

            # Budget limits
            if "budget_context" in data:
                config.budget_context = float(data["budget_context"])
            if "budget_dev" in data:
                config.budget_dev = float(data["budget_dev"])
            if "budget_review" in data:
                config.budget_review = float(data["budget_review"])

            # Alert thresholds
            if "warning_percent" in data:
                config.warning_percent = int(data["warning_percent"])
            if "critical_percent" in data:
                config.critical_percent = int(data["critical_percent"])
            if "auto_stop" in data:
                config.auto_stop = bool(data["auto_stop"])

            # Currency settings
            if "display_currency" in data:
                config.display_currency = data["display_currency"]
            if "currency_rates" in data:
                config.currency_rates.update(data["currency_rates"])
            if "display_currencies" in data:
                config.display_currencies = data["display_currencies"]

        except Exception as e:
            print(f"Warning: Could not load config file: {e}")

        return config

    def save(self, config_path: Path):
        """Save configuration to JSON file."""
        data = {
            "budget_context": self.budget_context,
            "budget_dev": self.budget_dev,
            "budget_review": self.budget_review,
            "warning_percent": self.warning_percent,
            "critical_percent": self.critical_percent,
            "auto_stop": self.auto_stop,
            "display_currency": self.display_currency,
            "currency_rates": self.currency_rates,
            "display_currencies": self.display_currencies,
        }

        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)

    def get_budget_for_phase(self, phase: str) -> float:
        """Get budget limit for a specific phase."""
        phase = phase.lower()
        if phase in ("context", "sm"):
            return self.budget_context
        elif phase in ("dev", "development", "implement"):
            return self.budget_dev
        elif phase in ("review", "qa"):
            return self.budget_review
        return self.budget_dev  # Default

    def get_thresholds(self) -> dict[str, float]:
        """Get budget thresholds as decimal values."""
        return {
            "warning": self.warning_percent / 100.0,
            "critical": self.critical_percent / 100.0,
            "stop": 1.0,
        }


# Global configuration instance
_config: Optional[CostConfig] = None


def get_config() -> CostConfig:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        # Try to load from file first, then overlay with env vars
        config_file = Path(__file__).parent.parent.parent / ".automation" / "costs" / "config.json"
        if config_file.exists():
            _config = CostConfig.from_file(config_file)
        else:
            _config = CostConfig.from_env()
    return _config


def set_config(config: CostConfig):
    """Set the global configuration instance."""
    global _config
    _config = config


def reset_config():
    """Reset the global configuration instance."""
    global _config
    _config = None


if __name__ == "__main__":
    # Demo/test
    config = get_config()

    print("Cost Configuration")
    print("=" * 40)
    print(f"Budget - Context: ${config.budget_context:.2f}")
    print(f"Budget - Dev:     ${config.budget_dev:.2f}")
    print(f"Budget - Review:  ${config.budget_review:.2f}")
    print()
    print(f"Warning at:  {config.warning_percent}%")
    print(f"Critical at: {config.critical_percent}%")
    print(f"Auto-stop:   {config.auto_stop}")
    print()
    print(f"Display Currency: {config.display_currency}")
    print(f"Display Currencies: {config.display_currencies}")
    print()
    print("Currency Rates:")
    for code, rate in config.currency_rates.items():
        print(f"  {code}: {rate}")
