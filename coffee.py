"""Simulate one morning (7:00-11:00) at a coffee shop with a single barista."""

import numpy as np

OPEN_MINUTES = 4 * 60      # 7:00 to 11:00
MEAN_INTERARRIVAL = 3.0    # about one customer every three minutes
MIN_SERVICE, MAX_SERVICE = 1.0, 4.0


def simulate(rng):
    """Return each customer's arrival time and wait, in minutes after opening."""
    # Draw more gaps than we could plausibly need, then keep arrivals before closing.
    gaps = rng.exponential(MEAN_INTERARRIVAL, size=int(OPEN_MINUTES / MEAN_INTERARRIVAL * 3))
    arrivals = np.cumsum(gaps)
    arrivals = arrivals[arrivals < OPEN_MINUTES]
    service = rng.uniform(MIN_SERVICE, MAX_SERVICE, size=arrivals.size)

    waits = np.empty(arrivals.size)
    barista_free_at = 0.0
    for i, (arrival, duration) in enumerate(zip(arrivals, service)):
        start = max(arrival, barista_free_at)
        waits[i] = start - arrival
        barista_free_at = start + duration
    return arrivals, waits


def main():
    _, waits = simulate(np.random.default_rng())
    print(f"Customers served: {waits.size}")
    print(f"Average wait: {waits.mean() if waits.size else 0.0:.2f} minutes")


if __name__ == "__main__":
    main()
