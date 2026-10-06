# Spec: <Feature name>

**Status:** Draft | Reviewed | Implemented
**Author:** <your name>  **Date:** <YYYY-MM-DD>

> Write this yourself. The spec describes **what** the feature does and **why**. It says nothing
> about how it's built: no class names, no libraries. That goes in `plan.md`.

## 1. Problem
<!-- One or two sentences: who has what problem? -->

## 2. User stories
> 📖 **Book:** [§3.4.1 Guidelines for Effective User Stories](https://www.swebook.org/chapters/03-user-requirements/index.html#341-guidelines-for-effective-user-stories) (INVEST: Independent, Negotiable, Valuable, Estimable, Small, Testable)

<!-- As a <role>, I want <capability>, so that <benefit>. Keep them small and independent.
     Number each user story (US-#): US-1, US-2, ... -->
- **US-1:** As a …, I want …, so that …
- **US-2:** …

## 3. Acceptance criteria
> 📖 **Book:** [§3.4.1 Given / When / Then](https://www.swebook.org/chapters/03-user-requirements/index.html#given--when--then-writing-acceptance-criteria-as-scenarios); error and edge cases: [§10.4 black-box testing](https://www.swebook.org/chapters/10-testing/index.html#104-input-coverage-i-black-box-testing)

<!-- AC = acceptance criterion: one testable condition the feature must meet to count as done.
     Number them AC-1, AC-2, ... and tag the user story each one serves (US-#).
     Given/When/Then. These become your Behave scenarios and tests. Include error cases. -->

**AC-1 (US-1): <short name>**
- Given …
- When …
- Then …

**AC-2 (US-1): <error or edge case>**
- Given …
- When …
- Then …

## 4. Data
<!-- What information the feature stores or shows, and the rules for it (required? unique? range?). -->
| Thing | Information | Rules |
|---|---|---|
|  |  |  |

## 5. API / UI behavior
<!-- What the user or API client can do, and what they get back. Include error responses. -->
| Action | Input | Success result | Failure result |
|---|---|---|---|
|  |  |  |  |

## 6. Out of scope
> 📖 **Book:** the "Won't have" of [§4.4.1 MoSCoW](https://www.swebook.org/chapters/04-requirements-analysis/index.html#441-must-should-could-wont-moscow-prioritization) (Must/Should/Could/Won't have)

<!-- What this feature deliberately does NOT do. This stops scope creep (including from the AI). -->
-

## 7. Open questions
<!-- Anything unclear. Resolve these before planning. -->
- [ ]
