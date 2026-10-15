"""Flask page that runs one simulated coffee-shop morning per page load."""

import base64
import io

import matplotlib

matplotlib.use("Agg")  # render to images without a display
import matplotlib.pyplot as plt
import numpy as np
from flask import Flask, render_template_string

from coffee import OPEN_MINUTES, simulate

app = Flask(__name__)

THEMES = {
    "light": {"surface": "#fcfcfb", "ink": "#0b0b0b", "muted": "#52514e", "grid": "#e4e3df", "series": "#2a78d6"},
    "dark": {"surface": "#1a1a19", "ink": "#f0efec", "muted": "#c3c2b7", "grid": "#3a3a37", "series": "#3987e5"},
}

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Coffee Shop Morning</title>
<style>
  :root { --surface: #fcfcfb; --ink: #0b0b0b; --muted: #52514e; --border: #e4e3df; }
  @media (prefers-color-scheme: dark) {
    :root { --surface: #1a1a19; --ink: #f0efec; --muted: #c3c2b7; --border: #3a3a37; }
  }
  body { margin: 0; padding: 32px 16px; background: var(--surface); color: var(--ink);
         font: 16px/1.5 system-ui, -apple-system, sans-serif; }
  main { max-width: 860px; margin: 0 auto; }
  h1 { font-size: 24px; margin: 0 0 4px; }
  .sub { color: var(--muted); margin: 0 0 24px; }
  .stats { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 24px; }
  .stat { flex: 1 1 180px; border: 1px solid var(--border); border-radius: 8px; padding: 16px; }
  .stat .label { color: var(--muted); font-size: 14px; }
  .stat .value { font-size: 32px; font-weight: 600; font-variant-numeric: tabular-nums; }
  img { width: 100%; height: auto; display: block; }
  a { color: inherit; }
</style>
</head>
<body>
<main>
  <h1>One morning at the coffee shop</h1>
  <p class="sub">7:00 to 11:00, one barista. A new morning is simulated every time you
    <a href="/">reload the page</a>.</p>
  <div class="stats">
    <div class="stat"><div class="label">Customers served</div><div class="value">{{ served }}</div></div>
    <div class="stat"><div class="label">Average wait</div><div class="value">{{ "%.1f"|format(avg_wait) }} min</div></div>
  </div>
  <picture>
    <source srcset="data:image/png;base64,{{ charts.dark }}" media="(prefers-color-scheme: dark)">
    <img src="data:image/png;base64,{{ charts.light }}"
         alt="Each customer's wait in minutes, by arrival time from 7:00 to 11:00">
  </picture>
</main>
</body>
</html>
"""


def wait_chart(arrivals, waits, theme):
    """Draw each customer's wait against their arrival time; return a base64 PNG."""
    c = THEMES[theme]
    fig, ax = plt.subplots(figsize=(8.6, 4), dpi=150)
    fig.patch.set_facecolor(c["surface"])
    ax.set_facecolor(c["surface"])

    ax.vlines(arrivals, 0, waits, color=c["series"], linewidth=1, alpha=0.5)
    ax.scatter(arrivals, waits, s=22, color=c["series"], edgecolors=c["surface"], linewidths=1, zorder=3)

    hours = np.arange(0, OPEN_MINUTES + 1, 30)
    ax.set_xticks(hours, [f"{7 + m // 60}:{m % 60:02d}" for m in hours])
    ax.set_xlim(0, OPEN_MINUTES)
    ax.set_ylim(0, max(waits.max() * 1.1, 1) if waits.size else 1)
    ax.set_xlabel("Arrival time", color=c["muted"])
    ax.set_ylabel("Wait (minutes)", color=c["muted"])
    ax.set_title("Each customer's wait", loc="left", color=c["ink"], fontsize=12, fontweight="bold")

    ax.grid(axis="y", color=c["grid"], linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(c["muted"])
    ax.tick_params(colors=c["muted"], length=0)

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=c["surface"])
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


@app.route("/")
def index():
    arrivals, waits = simulate(np.random.default_rng())
    return render_template_string(
        PAGE,
        served=waits.size,
        avg_wait=waits.mean() if waits.size else 0.0,
        charts={theme: wait_chart(arrivals, waits, theme) for theme in THEMES},
    )


if __name__ == "__main__":
    app.run(debug=True)
