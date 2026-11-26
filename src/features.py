"""Definisi set fitur dan aturan R0."""
import re

# R0: URL dianggap sah bila persis mengikuti templat https://www.<host>/ (tanpa path, query, fragmen)
TEMPLATE_RE = re.compile(r"^https://www\.[^/?#]+/?$")
