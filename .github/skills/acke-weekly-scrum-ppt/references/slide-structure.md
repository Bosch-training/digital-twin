# Slide structure

Fixed order produced by `scripts/build_deck.py`. Tables paginate at 8 rows per slide with a `(n/m)` title suffix.

| # | Slide | Content | Icon |
|---|---|---|---|
| 1 | Title | white logo, "Weekly Scrum Status Report", team, sprint, week range + ISO week, prepared by | none |
| 2 | Executive Summary | RAG chip + reason, 1-6 bullets, KPI cards (progress %, points done/committed, items done, items blocked) | goal |
| 3 | Sprint Goal & Burndown | goal text, committed points, line chart (ideal vs actual) | goal |
| 4+ | Completed | table: ID, Item, Owner, Points | done |
| next | In Progress | table: ID, Item, Owner, Points, Progress % | progress |
| next | Blockers & Risks | up to 3 blocker cards (owner + ask) and 3 risk cards (severity + mitigation) | blocked |
| next | Velocity | clustered columns committed vs completed per sprint, average velocity, commitment reliability | velocity |
| next | Next Week Plan | table: #, Planned work, Owner | next |
| last | Closing | white logo, "Thank you", contact | none |

## Limits (enforced by scripts)
- Max 6 summary bullets, ~12 words each (warning above 12, validate_deck warns above 14).
- Item / risk titles <= 70 chars; asks and mitigations <= 110 chars.
- More than 3 blockers or risks: extras go to speaker notes (validate_status warns).
- Each item's optional `detail` goes to speaker notes, never on the slide.

## Computed values (do not supply in JSON)
- Progress % = sum(completed points) / `committed_points`; if `committed_points` is missing or 0, falls back to completed + in-progress points.
- Ideal burndown = straight line from committed points on the first label to 0 on the last.
- Average velocity = mean of `velocity[].completed`; reliability = sum completed / sum committed.
