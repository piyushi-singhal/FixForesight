# Problem Statement

## The Industrial Maintenance Problem

Unplanned equipment downtime in industrial operations results in:

- **Lost production** — a single unplanned stoppage can cost thousands to hundreds of thousands of dollars per hour in heavy industry.
- **Safety risks** — mechanical failures, particularly bearing failures or thermal runaway, present direct worker safety hazards.
- **Reactive maintenance cycles** — without predictive insight, teams respond to failures after the fact, leading to emergency part sourcing, overtime labour, and cascading failures.

Traditional **scheduled maintenance** (time-based) is inefficient: it replaces parts that are still healthy while missing actual wear-based degradation that occurs between intervals.

---

## The Gap FixForesight Addresses

| Current State | With FixForesight |
|---|---|
| Maintenance scheduled by calendar | Maintenance triggered by data-driven failure risk |
| No early warning of impending failure | Failure probability computed per machine in real time |
| Technicians respond after breakdown | Technicians receive prescriptive work orders before failure |
| No historical search of incident data | Solr-indexed incident search across entire history |
| Manual status tracking via spreadsheets | Digital work-order lifecycle: open → in_progress → completed |

---

## Dataset Motivation

The **AI4I 2020 Predictive Maintenance Dataset** (10,000 records, UCI ML Repository) was chosen because it:

- Contains realistic industrial sensor readings (air temp, process temp, rotational speed, torque, tool wear).
- Labels five distinct failure types (heat dissipation, power loss, overstrain, tool wear, random).
- Has realistic class imbalance (~3.4% failure rate), reflecting real industrial conditions.
- Is publicly available and reproducible.

---

## Related Documents

- [Project Overview](project-overview.md)
- [Objectives](objectives.md)
