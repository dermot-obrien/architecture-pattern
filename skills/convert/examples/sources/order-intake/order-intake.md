# Order intake

A customer's order is taken from any sales channel, checked and priced once, paid for, recorded and announced to the rest of the business. The pattern keeps pricing and validation in one place so that every channel gives the same answer.

## Building blocks

| Component | Responsibility |
|---|---|
| Sales Channel | Collects the order from the customer, on the web or on a phone |
| Order API | The single entry point for orders from every channel |
| Order Service | Validates, prices and owns the order through its life |
| Payment Gateway | Authorises the payment with the payment provider |
| Order Store | Holds every order and its state |
| Event Broker | Carries business events to whoever subscribes |
| Notification Service | Tells the customer what happened |

## Flow

1. The Sales Channel submits the order to the Order API.
2. The Order API asks the Order Service to create the order.
3. The Order Service asks the Payment Gateway to authorise the payment.
4. The Order Service writes the order to the Order Store.
5. The Order Service publishes an order placed event to the Event Broker.
6. The Event Broker delivers the event to the Notification Service.

## Constraints

Payment details never reach the Order Store. Orders are idempotent on the channel's own reference.
