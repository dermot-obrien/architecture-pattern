---
kind: pattern
id: AP-002
title: "AP-002 Event-driven ingestion"
description: "Ingests events from producers through a durable log, so consumers can replay them."
pattern_type: architecture-pattern
pattern_scope: capability-area
version: 0.3.0
status: proposed
created: 2026-02-02
last_modified: 2026-09-20
owner: Architecture team
portfolio:
  priority: medium
  target_quarter: "2027-Q1"
  committed: false
---

# AP-002 Event-driven ingestion

This paragraph is not the summary, because the description is.

## Context

Why the pattern exists and the forces it balances.

## Diagram

![Components](components.svg)

## Building Blocks

| ID | Name | Responsibility |
|---|---|---|
| 01 | Intake | Receives the request |
| 02 | Store | Keeps the record |

## Interfaces

| ID | From | To | Description |
|---|---|---|---|
| IF-01 | 01 | 02 | Writes the record |

## Scenarios

### S1 Main scenario

| Step | From | To | Interface | What happens |
|---|---|---|---|---|
| 1 | 01 | 02 | IF-01 | The record is written |

See also [the old gateway](../AP-004-old-gateway/index.md), [order intake](../AP-001-order-intake/index.md) and [its diagram](../AP-004-old-gateway/components.svg).
