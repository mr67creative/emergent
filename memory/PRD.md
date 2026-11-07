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
- Integer thousandths of dollars for balances. Overclock was removed at the user's request in the 2026-11-07 refresh; historical earnings remain intact. New verified ad charges always credit11mills.
- Server timestamps enforce the 5-second minimum, charge ID is consumed atomically, duplicate completion blocked. Browser dismiss/hidden-tab/navigation cancels viewing. This is a simulator, not production anti-fraud verification.
- Atomic withdrawal minimum $5. Atomic insight-read predicate prevents duplicate discovered increments.
- Static illustrative geographic, temporal, CTR, organic-reach and risk datasets, clearly labeled sample/simulation. Persisted interactions and business actions are backed by MongoDB.
- Reusable AdBox, rings/segments/gauge, real land-masked dotted map (7,531 points), chart components, shared header/footer and profile dropdown.
- Four generated, hosted merchandise product images: stickers, engineer tee, stealth hoodie, desk mat with artisan keycap. Website brand monogram was reconstructed from merchandise and prepared as transparent PNG.
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
The refreshed simulation is ready for use. Optional next improvement: campaign-specific performance inside the extension preview.

## Refresh request — 2026-11-07
Exact user request:
> I want this very Herosection to be much more stronger rather than a AI slop, something like wavvy thunder effect but beautifully executed, remove translation based animation and hover effects, generate image for Desk mat and keycap, remove earning overclock, add payout, referrals, add the extension Ad box to be shown for Advertisement creation as well as some part of app, Add extension popup UI and make it accessible through profile dropdown menu item, User dashboard doesnot need World map, Advertisor's World map must be scrollable, zoomable, and instead of 7 points, each pixels or cluster should be hoverable, Navbar should be reimagined, The logo you added on Merch should also be in the website.

Clarified decision: **$1 vault credit** for each referral after the existing **$3.90 verified ad revenue** threshold. Simulation scope retained; extension means an interactive in-app popup/placement preview, not an installed browser extension.

### Refresh implemented
- Replaced straight conduit with full-width Canvas electrical waves:24 layered organic strands, glow, emerald/cyan detail, charging-responsive intensity. No translated interface entrance/hover movement; decorative hover effects disabled. Canvas is nonblank/static for reduced-motion users and rendering pauses when hidden/offscreen.
- New navbar, personal/advertiser workspace selector, mobile route navigation, profile dropdown, matching merchandise monogram across website/popup/vault/favicon.
- Generated desk mat/keycap studio artwork; used in milestone drawer and preview teaser.
- Removed250-view overclock milestone and bonus logic. Existing stored bonus earnings are preserved; old boost claim hidden in state, cannot be newly claimed. Remaining physical milestones100/500/1000/2500.
- Added `/payouts`: available balance, demo bank/wallet destination, amount presets/custom amount, minimum$5/overdraft validation, confirmation, persistent payout history and CSV export. Dashboard quick withdrawal remains.
- Added `/referrals`: private invite code/link, labeled sample members, progress meters, simulated activity, qualification and exact-once$1 credits. A fresh browser joining via ref code creates a real sandbox referral record; its completed ad simulations add20mills verified gross ad revenue to inviter's corresponding record. No real messages or money transfers.
- Added `/extension` via profile dropdown, with browser chrome, compact popup, vault/stats, power switch, ad/insight mode and per-site controls. Settings persist and affect simulator. Popup shows latest saved creative; simulator serves approved creative.
- Shared `ExtensionAdFrame` preserves exact minimal2-row `AdBox`, adds external extension attribution, and appears in composer, simulator, extension UI and dashboard feed preview.
- Removed user-dashboard world map; replaced with earnings timeline. Added payout/referral access and corrected tee milestone02.
- Advertiser map now has7,531 individually inspectable land pixels in158 geographic clusters using actual country GeoJSON. Regional labels, sample per-pixel views/clicks/CPVV/platform, wheel/button/key zoom100–500%, native overflow scrollbars, drag pan, region select/focus, click-filter and reset. CSV and KPI period filters align. Coastal boundary pixels are honestly labeled coastal clusters.
- All-region spend now sums regional views×regionalCPVV (not flat CPVV).7-day$3014.80 and30-day$12059.21 verified against the sample dataset.
- Added backward-compatible feature defaults to existing sandbox profiles without resetting balances, creatives or history. New referral-code index; same private owner scoping.

### Refresh verification
- `/app/test_reports/iteration_2.json`:20/20 API tests passed. Studio/admin/insight/reward workflows regressed successfully.
- Initial responsive run31/33 passed; only simulator at390/360 overflowed. Fixed canvas bounds and main horizontal clipping. Post-fix browser mobile frames verify390→390 and360→360 document widths.
- Corrected weighted spend and tee milestone mismatch; browser assertions pass for7/30days, region reset and milestone02.
- Header logo transparent corners verified; new desk artwork and all product images loaded. Popup controls/settings persistence, referral link/credit, withdrawals/export, individual pixel hover/click, zoom/wheel/drag/arrow-key pan verified.
- Canvas pixel sampling confirms rendered electrical strands and changing frames; reduced-motion retains nonblank still frame. Tested hover positions unchanged and CSS motion countzero.
- Final optimized frontend build passed: `/app/test_reports/refresh-build-final.log`.
- Tester changed test scripts/reports only, not application sources. Old bonus test intentionally replaced with removal/history-preservation regression.
- Local rerun wrapper lacked Playwright; equivalent remaining responsive checks were executed in existing browser tooling, not reported as an application failure.
- No known blocking issue in requested simulation flows. External ad serving, extension installation, real payouts, real shipping and geographic telemetry remain outside the confirmed scope.