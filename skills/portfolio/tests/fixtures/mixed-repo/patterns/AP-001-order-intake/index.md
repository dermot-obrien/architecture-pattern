---
kind: pattern
id: AP-001
title: "AP-001 Order intake"
pattern_type: architecture-pattern
pattern_scope: problem
version: 1.0.0
status: active
created: 2026-01-10
last_modified: 2026-09-01
owner: Architecture team
portfolio:
  priority: high
  target_quarter: "2026-Q4"
  committed: true
---

# AP-001 Order intake

Takes an order from any channel and records it exactly once.

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
