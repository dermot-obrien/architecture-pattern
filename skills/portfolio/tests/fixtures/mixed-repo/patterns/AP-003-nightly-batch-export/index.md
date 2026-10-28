---
kind: pattern
id: AP-003
title: "AP-003 Nightly batch export"
pattern_type: architecture-pattern
pattern_scope: problem
version: 2.1.0
status: deprecated
superseded_by: [AP-002]
created: 2024-01-01
last_modified: 2025-06-30
owner: Architecture team
---

# AP-003 Nightly batch export

Exports the day's records to downstream systems in one nightly file.

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
