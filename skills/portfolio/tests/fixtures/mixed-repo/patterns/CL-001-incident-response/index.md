---
kind: pattern
id: CL-001
title: "CL-001 Incident response"
pattern_type: collaboration
pattern_scope: domain
version: 0.2.0
status: draft
created: 2026-04-04
last_modified: 2026-10-01
owner: Operations
---

# CL-001 Incident response

How the on-call engineer, the incident lead and the service owner work together during an incident.

## Context

Why the pattern exists and the forces it balances.

## Diagram

![Components](components.svg)

## Participants

| ID | Name | Responsibility |
|---|---|---|
| 01 | Intake | Receives the request |
| 02 | Store | Keeps the record |

## Interactions

| ID | From | To | Description |
|---|---|---|---|
| IF-01 | 01 | 02 | Writes the record |

## Scenarios

### S1 Main scenario

| Step | From | To | Interface | What happens |
|---|---|---|---|---|
| 1 | 01 | 02 | IF-01 | The record is written |
