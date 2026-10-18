---
kind: use-case
id: UC-001
title: "UC-001 Track an order"
version: 0.1.0
status: draft
created: 2026-05-05
last_modified: 2026-09-09
owner: Product team
primary_actor: "Customer"
supports_outcome: OC-001
success_criteria: ["The customer sees the order's current step"]
portfolio:
  priority: low
---

# UC-001 Track an order

A customer sees where their order is, from intake to delivery.

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
