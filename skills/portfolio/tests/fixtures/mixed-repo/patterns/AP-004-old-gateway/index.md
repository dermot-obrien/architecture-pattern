---
kind: pattern
id: AP-004
title: "AP-004 Old gateway"
pattern_type: architecture-pattern
pattern_scope: problem
version: 1.4.0
status: deprecated
created: 2023-02-02
last_modified: 2025-01-15
owner: Architecture team
portfolio:
  state: archive
  reason: "Agreed at the architecture review: replaced by AP-002"
  since: 2026-10-01
---

# AP-004 Old gateway

A single gateway in front of every service, kept for the record.

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

It fed [order intake](../AP-001-order-intake/index.md).
