## Context

Several products keep balances that disagree, because each overwrites its own copy of the current state [R1]. An event-sourced ledger stores every change as an immutable event and derives the current state by replaying them [W1], so every balance can be traced to the events that made it.

The forces are auditability against the cost of replay. Replay grows with the stream, and a periodic snapshot bounds it [W3].

## Building Blocks

| ID | Name | Responsibility |
|---|---|---|
| 01 | Command handler | Validates a change and records it as an event |
| 02 | Ledger | Appends events and never changes one |
| 03 | Projector | Derives balances from the ledger [W2] |
| 04 | Balance view | Serves the derived balances |

## Interfaces

| ID | From | To | Description |
|---|---|---|---|
| IF-01 | 01 | 02 | Appends an event |
| IF-02 | 02 | 03 | Delivers new events in order |
| IF-03 | 03 | 04 | Updates a balance |

## Scenarios

### S1 Record a payment

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Command handler | 02 Ledger | Appends a payment event | IF-01 |
| 2 | 02 Ledger | 03 Projector | Delivers the event | IF-02 |
| 3 | 03 Projector | 04 Balance view | Updates the balance | IF-03 |
