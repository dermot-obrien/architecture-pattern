# Submit a claim

As a claimant I want to submit a claim online, with my evidence, so that I am paid quickly and know where my claim stands. The goal is a decision within five working days.

## Actors

- Claimant: the policy holder making the claim
- Claims Handler: reviews the claim and decides it

## Main flow

1. The Claimant submits the claim and evidence through the Claims Portal.
2. The Claims Portal sends the claim to the Claims Service.
3. The Claims Service checks the cover with the Policy Register.
4. The Claims Service stores the evidence in the Document Store.
5. The Claims Service assigns the claim to a Claims Handler for review.

## Out of scope

Payment of an approved claim, which is another use case.
