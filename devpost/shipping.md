# WorkCheck shipping record

Status: in progress. Reviewed 21 October 2026. The learner explicitly confirmed the PoC ready within its documented scope and authorized 6-ship. They confirmed the exact event URL below. The public repository is published and anonymously verified. No demo-video link is confirmed. No Devpost entry has been submitted by the agent.

## Confirmed event and current requirements

Event: [Build With AI: Basics](https://learn-ai-basics.devpost.com/). Deadline: **26 October 2026, 5:00pm EDT**, which is **23:00 Europe/Bucharest** that day (timezone conversion checked with Python zoneinfo). The [event overview](https://learn-ai-basics.devpost.com/) requires a new Skill-Pack project with scope.md, prd.md and spec.md in the public repository.

The [official rules](https://learn-ai-basics.devpost.com/rules) specify:

- Build during September 22–October 26, 2026; disclose incorporated pre-existing work.
- Public GitHub, GitLab or Bitbucket repository, runnable sources/instructions and an open-source licence.
- Functioning-device demonstration under three minutes, publicly visible on YouTube or Vimeo.
- Features/functionality description; English materials or English translations.
- Age-of-majority and other eligibility conditions; the entrant must check their own eligibility.
- Multiple entries may be submitted if unique and substantially different. This alone does not certify another project's eligibility.

For licensing, the rule uses "should" for open-source licensing; treat the licence as an explicit preparation item rather than inventing a separate eligibility guarantee. A public GitHub repository remains the chosen route from the saved plan, even though the live rules allow other providers.

The [organizer's form update](https://learn-ai-basics.devpost.com/updates/46821-two-new-questions-on-the-submission-form) confirms a required Skill Pack usage explanation and age-of-majority checkbox, and directs entrants to put the public repository in **Try it out**. The [submission management page](https://devpost.com/submit-to/30447-build-with-ai-basics/manage/submissions) shows a registration/login gate in unauthenticated access. **The complete signed-in form and all field lengths were not inspected.** Ask the learner to paste the actual prompts/limits rather than assuming generic Devpost fields.

The installed workflow also requires the learner's exit survey. Its exact signed-in questions and completion are not accessible here. Personal reflections and survey answers remain entirely the learner's. Deployment is not required by the installed shipping workflow; no hosting or paid services are proposed.

## Readiness evidence carried forward and rechecked

Application snapshot: 0726ff73b32da3f741d02a12169b174981f2ab17. Final-report/docs checkpoint: 9cefc8e3d715df10e66358904941f06220a0349e. Prior fresh full run: 181 tests passed; prior complete cold offline browser flow passed. See [validation.md](validation.md) and [coverage.md](coverage.md).

At 6-ship entry, the documented running server's health returned ok. Three ordinary-notation/mathematical regression tests passed (0.684 seconds). Two relevant UI regressions passed (25.238 seconds), covering concept/example/practice order, independent reveals, edit invalidation, both-topic behavior, Cancel and confirmed reset. These two UI tests used the existing nonlocal socket guard and made no nonlocal attempts. `pip check` reported no broken requirements. No runtime code changed during this shipping preparation.

Photo recognition and automatic practice grading remain **deferred**. Do not present planned full engineering-mathematics coverage as implemented or claim measured learning improvements.

## Public repository preparation

Audit baseline: 9cefc8e, 7 commits and 44 tracked files. Targeted scan inspected 133 history objects; no configured credential-pattern findings or private-profile/environment-file history paths were found. The planning files are tracked. The learner profile and environment files are ignored and were never tracked in the inspected history. Manually reviewed source/docs for project relevance; code-author identity is the explicit WorkCheck build-agent identity, not an invented learner identity. Evidence: ignored local artifact `.workcheck/public-repository-audit.json`.

This combines a targeted scanner with manual review; it is not a guarantee against every possible secret. Recheck intended new files and final history immediately before pushing. Preserve the planning docs, coverage, setup, technical evidence and app map. Keep `.agents/`, `.claude/`, `agent/`, `skills-lock.json`, `.venv/`, `.workcheck/`, the learner profile, local drafts and credentials out of publication. The first four currently remain unrelated untracked workspace material; never blanket-stage them.

**MIT licence approved and applied.** The learner approved the proposed licence, including `Copyright (c) 2026 WorkCheck contributors`. See the root [LICENSE](../LICENSE). Third-party packages retain their own licences.

**Publication explicitly authorized:** account `Deatheater10-creator`, public repository `WorkCheck`, audited code and included Git history. Public repository created under the verified authorized account and the audited history pushed normally to `master`. Authentication used Git Credential Manager; credentials were not printed or stored in project files or remote URLs.

Fresh pre-publication audit: all eight reachable commits, 47 historical paths, 119 unique file versions and eight commit metadata objects checked. No configured secret-pattern findings or private paths were found. This adds complete per-commit path checks and metadata scanning to the earlier manual review. Evidence remains local in `.workcheck/final-history-audit.json`; repeat after the publication-preparation commit.

The authorized technical sequence is:

1. Apply the approved root licence; audit and commit the final public files.
2. Create an empty public `WorkCheck` repository under the confirmed account. Avoid auto-generating competing README/licence commits in GitHub. If an existing repository is supplied, inspect it first rather than overwriting history.
3. Add its confirmed URL as origin and push the local `master` branch normally. Never force-push or paste access tokens into chat. Use the account's normal browser/credential-manager authentication.
4. Check the URL without authentication. Verify README setup, dependency lock, app sources, tests, licence and the three planning documents are accessible. Record the verified URL in this file and spec.md.

Publication verified without authentication on 21 October 2026: public visibility, MIT licence, README, pinned dependencies, application source, tests and scope/PRD/spec accessible. Remote commit matched local `b5808a650a4b6d9c17b5d321d54bd5247a149966`. The final pre-push audit checked nine commits, 48 historical paths, 123 unique file versions and nine metadata objects with no configured findings or private paths. Publication records are committed separately and checked again before pushing.

## Demo and submission materials

- [demo-plan.md](demo-plan.md): screen actions, exact test inputs, suggested pacing and recording mechanics; no scripted narration.
- [submission-evidence.md](submission-evidence.md): factual evidence and boundaries to consult while the learner writes; not a submission draft.
- [readiness.md](readiness.md), [code-walkthrough.md](code-walkthrough.md), [app-map.html](app-map.html): technical support material, not learner reflections.

## Remaining steps

- [x] Correct event identified and confirmed by learner.
- [x] Explicit final PoC readiness recorded; build/learning-wrap-up prerequisites complete.
- [x] Public rules, overview and organizer update checked; signed-in form limitation recorded.
- [x] Relevant maths/UI regressions and documented running server checked.
- [x] Existing tracked history and publication boundaries audited locally.
- [x] Concrete demo plan and factual writing aids prepared.
- [x] GitHub owner, proposed copyright-holder line, MIT licence and explicit public-publishing authorization.
- [x] Final audited public files committed and public repository URL verified anonymously.
- [ ] Learner records and uploads the demo; public video URL verified.
- [ ] Learner provides the actual signed-in field prompts/limits and writes their answers, including Skill Pack usage.
- [ ] Learner completes eligibility confirmations, personal reflections and exit survey.
- [ ] Learner reviews the completed entry and explicitly authorizes submission or submits it themselves.

Public repository URL: [https://github.com/Deatheater10-creator/WorkCheck](https://github.com/Deatheater10-creator/WorkCheck).

Public video URL: not yet available.

Submission status: not submitted; do not mark completion until the learner confirms it.
