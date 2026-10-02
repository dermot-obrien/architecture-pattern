# Order intake

Orders arrive through the intake gateway, BB-001, which is this catalogue's own and is written bare. The same block written with this catalogue's code, ex:BB-001, links inside the site and is checked.

Authentication uses the operations platform's identity provider, ops:BB-024, which links to its stable identifier address. Events go to [the lab's message broker](lab:BB-007), which is registered one identifier at a time because the lab has no site.

Examples in code are never checked: `lab:BB-099`.
