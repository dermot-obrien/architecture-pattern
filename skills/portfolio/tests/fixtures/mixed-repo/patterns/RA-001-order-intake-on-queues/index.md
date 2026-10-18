---
kind: pattern
id: RA-001
title: "RA-001 Order intake on queues"
pattern_type: reference-architecture
pattern_scope: platform
implements: [AP-001]
version: 1.0.0
status: accepted
created: 2026-03-03
last_modified: 2026-08-08
owner: Platform team
portfolio:
  priority: high
  committed: true
---

# RA-001 Order intake on queues

Order intake built on a managed queue and a relational store.

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
