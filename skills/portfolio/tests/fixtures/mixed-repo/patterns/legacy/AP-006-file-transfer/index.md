---
sidebar_label: File transfer
status: Approved
pattern_type: architecture-pattern
version: "0.4"
last_modified: 2026-02-02
author: "An architect"
---

# AP-006 Managed file transfer

Moves files between organisations with receipts and retries.

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
