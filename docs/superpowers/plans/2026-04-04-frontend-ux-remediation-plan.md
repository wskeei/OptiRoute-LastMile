# Frontend UX Remediation Plan

> Source: `frontend-ux-auditor-planner` audit on 2026-04-04. This plan follows the auditor's remediation format and prioritizes trust, usability, and task clarity before any visual restyling.

**Goal:** Turn the current frontend from a demo-style dashboard into a clearer, more trustworthy, and more operable delivery dispatch product experience.

**Architecture:** Keep the existing Vue 3 + Element Plus + Leaflet + ECharts structure, but execute UX work in ordered phases. Fix misleading controls and broken interaction promises first, then rework onboarding and task flow, then address information architecture, responsiveness, accessibility, and finally visual normalization.

**Tech Stack:** Vue 3, TypeScript, Vue Router, Pinia, Element Plus, Leaflet, ECharts, Vite

---

## Audit Baseline

### Product Context
- Product purpose: last-mile AI dispatch and route visualization
- Core user journey: login/register -> enter system -> reset demo data -> start AI dispatch -> inspect routes -> review monitor/history/analytics
- Primary CTA: `开始AI调度`
- Current product shape: demo-oriented operational dashboard, not production-grade UX

### Current Risk Summary
- `P0`: core dispatch controls over-promise real capability
- `P1`: several clickable surfaces do not produce meaningful results
- `P1`: first-run flow does not foreground the primary task
- `P1`: responsive behavior is largely absent
- `P1`: accessibility and persistent state feedback are weak
- `P1`: visual system has strong AI-template patterns that reduce product credibility

### Preconditions
- The repository currently has no `.impeccable.md` design context file.
- Large-scale visual redesign should not begin until behavioral truthfulness and task flow are corrected.
- Before implementation begins, confirm:
  - which algorithm parameters are truly controllable
  - which metrics are real versus estimated
  - whether post-login default navigation should be `/dashboard` or `/dispatch`
  - whether the product will continue to present itself as a demo system

## Priority Findings

### P0: Misleading Control Surface
- The settings and dispatch pages present algorithm configuration as if it materially controls backend behavior.
- Analytics presents estimated optimization outcomes in a way that can be read as factual system output.
- Main files:
  - `frontend/src/views/Settings.vue`
  - `frontend/src/views/SmartDispatch.vue`
  - `frontend/src/views/Analytics.vue`
  - `frontend/src/views/PackageFlow.vue`

### P1: Broken or Misleading Interaction Affordances
- History cards look navigable but do not open a detail experience.
- Sidebar collapse uses a clickable `div`.
- Dashboard feature cards use clickable `div` containers as primary navigation.
- Main files:
  - `frontend/src/views/RouteHistory.vue`
  - `frontend/src/App.vue`
  - `frontend/src/views/Dashboard.vue`

### P1: Weak Onboarding and Task Prioritization
- Root navigation and login redirect favor `dashboard`, while the real primary task is dispatch.
- The product does not clearly teach "reset demo data -> start dispatch -> inspect outcomes".
- Main files:
  - `frontend/src/router/index.ts`
  - `frontend/src/views/Dashboard.vue`
  - `frontend/src/views/SmartDispatch.vue`
  - `frontend/src/views/RealtimeMap.vue`
  - `frontend/src/views/Login.vue`
  - `frontend/src/views/Register.vue`

### P1: Responsive and Accessibility Gaps
- Layouts rely on fixed column counts, fixed card widths, and desktop-first composition.
- Auth forms rely heavily on placeholders instead of explicit labels and persistent guidance.
- Main files:
  - `frontend/src/App.vue`
  - `frontend/src/style.css`
  - `frontend/src/views/Dashboard.vue`
  - `frontend/src/views/Analytics.vue`
  - `frontend/src/views/Settings.vue`
  - `frontend/src/views/Login.vue`
  - `frontend/src/views/Register.vue`

### P1: Visual Credibility Problem
- The global visual language leans on repeated glass cards, blue-purple gradients, gradient headlines, and emoji-heavy headings.
- The result reads as a generic AI-generated dashboard rather than an intentional operations product.
- Main files:
  - `frontend/src/style.css`
  - `frontend/src/App.vue`
  - `frontend/src/views/Dashboard.vue`
  - `frontend/src/views/Login.vue`
  - `frontend/src/views/Register.vue`
  - repeated page-level `.glass-card` styles throughout `frontend/src/views/*.vue`

## Recommended Skill Order

1. `/teach-impeccable`
2. `/harden`
3. `/clarify`
4. `/onboard`
5. `/distill`
6. `/arrange`
7. `/adapt`
8. `/normalize`
9. `/polish`

## Remediation Plan

### Phase 1: Fix Trust and Capability Mismatch

**Priority:** P0

**Goal:** Make every core control and metric truthful, so users can understand what is real, what is estimated, and what is demo-only behavior.

**Key changes:**
- Remove or relabel controls that do not affect backend behavior.
- Distinguish demo configuration from real dispatch parameters.
- Mark estimated metrics as estimates, or remove them if they cannot be defended.
- Replace deceptive interaction hints with explicit behavior.

**Likely files / routes:**
- `frontend/src/views/SmartDispatch.vue`
- `frontend/src/views/Settings.vue`
- `frontend/src/views/Analytics.vue`
- `frontend/src/views/RouteHistory.vue`
- `frontend/src/views/PackageFlow.vue`

**Implementation focus:**
- Audit all algorithm-related labels, sliders, summaries, and alerts.
- Review all KPI copy that implies measured business value.
- Review package creation flow where randomized coordinates can be misread as normal operational data.

**Suggested workflow / skills:**
- `/harden`
- `/clarify`

**Verification:**
- No primary UI control implies backend control unless the backend actually honors it.
- No KPI can be mistaken for a measured metric if it is only estimated.
- No major clickable surface ends in `console.log` or no-op behavior.
- A reviewer can answer "where does this value come from?" for every headline metric.

### Phase 2: Rebuild First-Run and Core Task Flow

**Priority:** P1

**Goal:** Make the first successful dispatch understandable without prior project knowledge.

**Key changes:**
- Re-evaluate the default post-login landing page.
- Shift the UX center of gravity from dashboard browsing to dispatch completion.
- Add explicit next-step guidance for empty states, first-run states, and no-history states.
- Clarify the sequence between resetting demo data, dispatching, and reviewing outcomes.

**Likely files / routes:**
- `frontend/src/router/index.ts`
- `frontend/src/views/Dashboard.vue`
- `frontend/src/views/SmartDispatch.vue`
- `frontend/src/views/RealtimeMap.vue`
- `frontend/src/views/Login.vue`
- `frontend/src/views/Register.vue`

**Implementation focus:**
- Decide whether `/dispatch` becomes the primary landing route.
- Convert dashboard from promotional overview to task-oriented launch surface, or reduce its prominence.
- Add page-level instructional content where the system currently relies on toasts.

**Suggested workflow / skills:**
- `/onboard`
- `/distill`

**Verification:**
- A new user can complete the first dispatch flow within 30 seconds without external explanation.
- Empty and no-history states point to a concrete next action.
- The primary CTA and the primary route are aligned.

### Phase 3: Rework Information Architecture and Page Responsibilities

**Priority:** P1

**Goal:** Reduce navigation noise and make each page's purpose distinct and defensible.

**Key changes:**
- Reassess the current eight-item sidebar structure.
- Clarify or consolidate overlapping roles among dashboard, analytics, history, and monitor pages.
- Make the dispatch page the operational center, with analysis pages positioned as secondary.

**Likely files / routes:**
- `frontend/src/App.vue`
- `frontend/src/views/Dashboard.vue`
- `frontend/src/views/Analytics.vue`
- `frontend/src/views/RouteHistory.vue`
- `frontend/src/views/RealtimeMap.vue`

**Implementation focus:**
- Reorder navigation by operational priority.
- Remove or merge page content that repeats the same metrics in slightly different card layouts.
- Define one sentence of purpose for each page before visual changes begin.

**Suggested workflow / skills:**
- `/arrange`
- `/distill`

**Verification:**
- The sidebar foregrounds core operations over secondary analysis.
- Each page has a non-overlapping role.
- Repeated KPI blocks and duplicate chart storytelling are reduced.

### Phase 4: Add Responsive Behavior, Accessibility, and Persistent Feedback

**Priority:** P1

**Goal:** Upgrade the frontend from desktop demo composition to product-grade usability across screen sizes and input modes.

**Key changes:**
- Add responsive breakpoints and restructure dense grid layouts.
- Replace clickable `div` controls with semantic interactive elements where needed.
- Add explicit labels and more durable guidance in forms and task panels.
- Replace toast-only error reporting with inline, persistent state communication where appropriate.

**Likely files / routes:**
- `frontend/src/App.vue`
- `frontend/src/style.css`
- `frontend/src/views/*.vue`

**Implementation focus:**
- Dashboard, analytics, settings, auth, and dispatch layouts need first attention.
- Dialog widths and overlay panels need mobile-safe behavior.
- Keyboard navigation and focus behavior need verification on navigation and auth flows.

**Suggested workflow / skills:**
- `/adapt`
- `/harden`

**Verification:**
- No horizontal scrolling at 375px viewport width for core pages.
- Login, navigation, and dispatch initiation are keyboard operable.
- Auth forms no longer rely on placeholder text as the only field cue.
- Error, loading, and empty states remain visible long enough to guide recovery.

### Phase 5: Normalize the Visual System and Remove AI-Slop Signals

**Priority:** P1 after Phases 1-4

**Goal:** Build a more credible, restrained, and operationally appropriate visual language after usability issues are corrected.

**Key changes:**
- Reduce gratuitous gradients, glassmorphism, gradient text, and emoji-led hierarchy.
- Consolidate repeated card and button styling into a smaller tokenized system.
- Make visual emphasis serve task importance rather than decoration.

**Likely files / routes:**
- `frontend/src/style.css`
- `frontend/src/App.vue`
- page-level scoped styles under `frontend/src/views/*.vue`

**Implementation focus:**
- Eliminate duplicated `.glass-card` variants and align surfaces with one system.
- Rework the auth pages, dashboard hero, and highlighted KPI blocks first.
- Keep the product feeling modern without reading as a generic AI showcase.

**Suggested workflow / skills:**
- `/normalize`
- `/polish`

**Verification:**
- Repeated page-level visual patterns are consolidated.
- Emoji are no longer carrying core hierarchy by default.
- Primary emphasis is reserved for dispatch-critical actions and states.
- The interface reads as an operations product rather than a stylized demo.

## Delivery Order

1. Phase 1 must be completed before any broad restyling.
2. Phase 2 should begin immediately after Phase 1, because task flow is the next-largest UX risk.
3. Phase 3 should run before or alongside Phase 4 only where page responsibilities are already stable.
4. Phase 5 should be the final pass.

## Definition of Done

- Core controls and KPIs no longer misrepresent system capability.
- The first successful dispatch path is obvious and teachable.
- Primary navigation reflects operational priority.
- Core pages work at mobile width and support keyboard-first interaction.
- Visual design is more restrained and internally consistent.

## Execution Notes

- Do not start with gradients, shadows, or animation polish.
- Do not preserve misleading controls merely because they are visually impressive.
- If the product remains a demo, the UI should say so plainly.
- Re-run a UX audit after each major phase to confirm the score improves for the right reasons.
