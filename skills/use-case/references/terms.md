<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Use case terms and their sources

The skill's terms follow the formal definitions below, so that a use case written with it reads the same way to someone trained in UML, the Unified Process or Cockburn's method. Definitions are paraphrased; the sources give the exact wording.

## Definitions

| Term | Meaning in this skill | Source |
|---|---|---|
| Use case | A set of behaviours a subject performs that gives one or more actors an observable result of value. The whole document | UML 2.5.1, clause 18; Jacobson 1992 |
| Actor | A role played by a person or system outside the subject that interacts with it. A participant of kind `actor` | UML 2.5.1, clause 18 |
| Subject | The system the use case describes. Its parts are participants of kind `solution` | UML 2.5.1, clause 18 |
| Scenario | One specific sequence of actions and interactions through a use case: an instance of it. `S1`, `S2` and so on | Booch, Rumbaugh and Jacobson 2005; Kruchten 2003 |
| Main success scenario | The scenario in which the goal is reached in the most direct way. Always `S1`. The Unified Process calls it the basic flow | Cockburn 2001; Kruchten 2003 |
| Extension, alternative flow | A path that departs from the main success scenario under a condition and either rejoins it or ends. `S2` onwards when it changes who acts; otherwise a line of prose | Cockburn 2001; Kruchten 2003 |
| Formality | How much of the description is written: brief, casual or fully dressed. Independent of endorsement | Cockburn 2001 |
| Goal level | Summary, user goal or subfunction. Most use cases worth a document are at user-goal level | Cockburn 2001 |
| Use-case story, slice | A story is one way through a use case; a slice is one or more stories delivered together, which is how a use case is planned and built incrementally | Jacobson, Spence and Bittner 2011 |
| Local use case | One identified within a container, such as an epic, for that container's own scoping or proving. This skill's term, not a standard one | This skill |
| Endorsed use case | One the organisation has accepted, with a registered identifier. This skill's term, not a standard one | This skill |

## The relationship that matters

A use case has scenarios. A scenario is never a smaller use case, and writing an informal use case does not make it a scenario: it makes it a brief or casual use case, which this skill keeps local until it is endorsed. Every source above agrees on that direction.

The same word appears in the `pattern` skill, where a scenario is a straight-line flow across a pattern's components. That is the same idea one level down: a path through a design rather than through a use case.

## Sources

- Object Management Group. *OMG Unified Modeling Language (OMG UML), Version 2.5.1*. formal/17-12-05, December 2017. Clause 18, Use Cases. https://www.omg.org/spec/UML/2.5.1
- Jacobson, I., Christerson, M., Jonsson, P. and Övergaard, G. *Object-Oriented Software Engineering: A Use Case Driven Approach*. Addison-Wesley, 1992. The origin of use cases.
- Jacobson, I., Booch, G. and Rumbaugh, J. *The Unified Software Development Process*. Addison-Wesley, 1999.
- Booch, G., Rumbaugh, J. and Jacobson, I. *The Unified Modeling Language User Guide*, second edition. Addison-Wesley, 2005. Use cases and their scenarios.
- Kruchten, P. *The Rational Unified Process: An Introduction*, third edition. Addison-Wesley, 2003. Flows of events: the basic flow and alternative flows.
- Cockburn, A. *Writing Effective Use Cases*. Addison-Wesley, 2001. Main success scenario, extensions, goal levels and formality.
- Jacobson, I., Spence, I. and Bittner, K. *Use-Case 2.0: The Guide to Succeeding with Use Cases*. Ivar Jacobson International, 2011. Use-case stories and slices.
