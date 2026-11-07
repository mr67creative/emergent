# MeanTime — Product Requirements & Build Notes

## Original problem statement
Build **MeanTime**, a next-generation platform that turns dead AI waiting time (while ChatGPT, Claude, Gemini, DeepSeek, or Grok is thinking) into verified micro-advertising revenue, bite-sized Daily Insights, and physical rewards.

User supplied detailed visual-first requirements:
- Dark #09090B background, #121216 elevated cards, subtle borders, emerald #10B981 plus cyan/amber, Inter and JetBrains Mono.
- No green status capsules, badge clutter, long explanatory UI paragraphs, or long stacked data-entry forms. Prefer visual gauges, maps, heatmaps, inline editing, tactile tiles, sliders and title tooltips.
- `/`: interactive electric conduit from prompt to earning vault, 5-second charge, $0.011 per verified view, ad/insight switch; interactive 55/45 revenue slider, merch preview, three role entrances.
- Shared exact two-row AdBox: headline row, description plus CTA row, floating close button, 2px charging line; no timers, tags, snooze or status pills.
- `/dashboard`: balance, time, payout, referral metrics; dotted land-masked map, 7x24 or 52-week heatmap, interests radar with declared/discovered controls.
- `/insights`: topic and reading-time filters, bookmark/upvote, complete reading to tune discovered interests, one-click reset; brand contribution and separate organic-reach funnel.
- `/rewards`: Duolingo-style winding SVG path, stickers100, boost250, tee500, hoodie1000, desk mat/keycap2500; clickable milestone drawer, product preview, reserve meter, shipping stepper.
- `/advertiser`: editable 2-pane canvas, 5 AI hosts, A/B/C creatives, character rings, topic tiles, CPVV slider .010–.050, budget and forecast.
- `/advertiser/analytics`: geographic filter, temporal heatmap, interest performance, variant confidence.
- `/admin`: J/K approve/reject, arrows navigate, in-context ad/insight preview, Laya risk gauge and sub-meters, reserve liquidity.
- Everything prepopulated and immediately interactive; React, lucide-react, recharts, SVG map/path/conduit.

## Explicit user decisions
- **Interactive simulation**. No real payments, advertising network, AI calls, physical fulfillment or live risk scanning.
- **In-app simulator only**. User said: “Please make sure that this not added in the navbar, it should be inside the user's profile dropdown or similar.” Simulator link exists only in profile dropdown.
- Use the supplied visual guidelines directly; no design-agent reinterpretation.

## Architecture decisions
- React19 / React Router7 frontend; FastAPI backend; MongoDB via existing MONGO_URL. Protected environment variables untouched.
- Client uses REACT_APP_BACKEND_URL exclusively for API routing.
- Server-created random private simulation token in localStorage, supplied as X-Demo-Token. Each browser receives a private sandbox; all session/campaign/submission queries are scoped to that token. These are sandbox roles, not real production admin authorization.
- Mongo collections: sessions (profile, active charge), campaigns, submissions. Unique session-token and owner/id indexes. Mongo response projections exclude BSON `_id`; response state uses Pydantic.
- Integer thousandths of dollars for balances; 5% overclock bonus uses integer micro-unit carry and caps eligible ad earnings at $30.
- Server timestamps enforce the 5-second minimum, charge ID is consumed atomically, duplicate completion blocked. Browser dismiss/hidden-tab/navigation cancels viewing. This is a simulator, not production anti-fraud verification.
- Atomic withdrawal minimum $5. Atomic insight-read predicate prevents duplicate discovered increments.
- Static illustrative geographic, temporal, CTR, organic-reach and risk datasets, clearly labeled sample/simulation. Persisted interactions and business actions are backed by MongoDB.
- Reusable AdBox, rings/segments/gauge, real land-masked dotted map (7,531 points), chart components, shared header/footer and profile dropdown.
- Three generated, hosted merchandise product images: stickers, engineer tee, stealth hoodie. Other milestone previews use appropriate product icons.
- Shadcn/Radix dropdowns, sheets/dialogs, Sonner notifications; custom SVG electrical conduit and winding rewards path.

## Personas
1. User: monetize simulated waiting, track earnings/interests, read insights, claim milestones.
2. Advertiser: create/save variants, choose audience and bid, submit for review, inspect sample paid analytics, contribute organic insights.
3. Reviewer: judge the actual creative, inspect simulated risk signals, approve/reject quickly.

## Implemented — 2026-11-07
- All eight requested routes, plus profile-only `/simulator`, responsive layouts and branded metadata.
- Landing charge experience and ad/insight modes, working proof-block slider, rewards and role entries.
- Five host choices in studio and simulator. Prompts never leave the simulator for an AI provider.
- Dashboard earnings/payout, activity chart, country hover, heatmap, interest declarations/discovery/reset, reward progress and withdrawal history.
- Insight deck: six substantial editable sample technical insights, topic/time/bookmark filters, saved bookmarks/upvotes/reads/source clicks.
- Brand contribution flow -> admin review -> approved insight visible in explore, with source link and organic-reach sample funnel.
- S-curve milestones, product preview drawer, lock enforcement, claim and simulated dispatch/delivery, overclock activation.
- Inline A/B/C composer, text limits, targeting, daily budget, bid forecast, URL validation, persistent draft CRUD, pending review status.
- Advertiser sample analytics: click-to-filter map, KPIs, time filter, CSV export, interest bars, verification rings and confidence meters. Amber heat cells indicate exhausted daily budgets.
- Admin keyboard deck, all/ad/insight filters, correct queue transitions, high-risk approval blocked in both UI and server.
- Zero-balance fallback fixed; displayed earned totals and notifications consume actual credited amount including bonuses.
- Discovered radar supports additional read topics (Systems, Math, Startups); fixed chart initialization sizing and Tailwind ring-class shadow collision.
- Corrected inherited styling of instrumented dynamic spans so bid and forecast numbers retain their intended font size.
- Server validation trims and rejects blank creative content, uses explicit target whitelist, scopes private data, enforces locked milestones.

## Verification — 2026-11-07
- Testing agent report: `/app/test_reports/iteration_1.json`.
- 15/15 API regression tests passed, then rerun after fixes: 15/15 pass (`verification/backend-results.xml`).
- Browser tested all major workflows: ad credit/cancel, withdrawal, bookmarks/reads, contribution approval, reward shipping, studio CRUD, review keyboard commands, geographic CSV export.
- 24/24 route/viewport combinations passed at1920x800,390x844,360x780; no horizontal overflow or broken product imagery reported.
- Post-fix screenshots verified zero balances on home/simulator, two boosted charges totaling$0.023 (indicator and actual vault), reset HTTP200 and visibly empty discovered interests.
- Build passes (`/app/test_reports/verification/build.log`).
- No blocking known issues in chosen simulation scope. No actual external financial, ad-serving, AI, shipping or risk-scanning integration exists, intentionally.

## Prioritized backlog
### P0 — none within the chosen simulation scope
### P1 — optional next refinements
- Add a multi-view long-reasoning simulator mode with verified ad rotation.
- Expand the knowledge deck and sample milestone product previews.
- Make creative sample analytics respond to the selected saved campaign (currently clearly labeled illustrative dataset).
### P2 — only with explicit future scope approval
- Real browser extension and platform-specific wait detection.
- Real identity/role access, brand verification, advertiser budget funding and payment/withdrawal providers.
- Real ad inventory, event aggregation, anti-fraud signals and editorial scoring.
- Real merchandise catalog, shipping address collection and fulfillment/tracking integrations.

## Next action
The complete simulation is ready for use. A useful optional enhancement is long-reasoning ad rotation to demonstrate multiple verified charges in one AI wait.