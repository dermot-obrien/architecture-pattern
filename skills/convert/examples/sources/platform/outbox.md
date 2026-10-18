# Transactional outbox

Publish an event exactly when the state change that caused it commits.

## Steps

1. The Business Service writes its state and the event to the Service Database.
2. The Outbox Relay polls the Service Database for new events.
3. The Outbox Relay publishes each event to the Event Broker.
