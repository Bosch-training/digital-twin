# Status data schema (`status.json`)

Validated by `scripts/validate_status.py`. Unknown keys (e.g. `_comment`) are ignored. See `assets/sample-status.json` for a full example.

## Top level
| Field | Type | Required | Notes |
|---|---|---|---|
| `team` | string | yes | shown on title and footer |
| `sprint` | number or string | yes | |
| `week_start`, `week_end` | `YYYY-MM-DD` | yes | end >= start; ISO week label derives from start |
| `rag` | `green` / `amber` / `red` | yes | |
| `rag_reason` | string | yes | one line |
| `goal` | string | yes | <= 160 chars |
| `committed_points` | number | no | defaults to done + in-progress points |
| `summary` | string[] | yes | 1-6 bullets |
| `notes` | string | no | speaker notes for the summary slide |
| `prepared_by`, `contact` | string | no | title / closing slides |

## Lists (use `[]` when empty)
| Field | Item fields |
|---|---|
| `completed` | `id`, `title`, `owner`, `points` (number), optional `detail` |
| `in_progress` | same as completed plus `percent` (0-100) |
| `blocked` | `id`, `title`, `owner`, `ask`, optional `detail` |
| `risks` | `risk`, `severity` (`low`/`medium`/`high`), `mitigation`, optional `owner` |
| `next_week` | `title`, `owner` |
| `velocity` | `sprint`, `committed`, `completed` (>= 1 entry, oldest first, last 5-6 sprints) |

## Burndown (required)
```json
"burndown": {"labels": ["D1", "D2", "..."], "remaining": [40, 38, 35]}
```
`labels` covers the whole sprint (>= 2); `remaining` has one value per elapsed day and may be shorter than `labels`.
