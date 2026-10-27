# Manual review of every ClearSite finding (ground truth labeling)

Reviewed by hand before computing precision/recall, per Checkpoint 1 feedback.

| Page | Rule | Element | ClearSite | axe-core (same rule category) | Manual verdict |
|---|---|---|---|---|---|
| clean_page_1 | - | - | 0 findings | 0 findings | Correct (no issues present) |
| clean_page_2 | - | - | 0 findings | 0 findings | Correct (no issues present) |
| context_case | img-empty-alt | divider-line.png | flagged | not flagged (alt="" accepted by default) | **False positive** -- genuinely decorative divider graphic |
| context_case | img-empty-alt | house-1.jpg | flagged | not flagged (alt="" accepted by default) | **True positive** -- real listing photo, needs a real description; axe missed this |
| issues_page_2 | low-contrast-text | #aaaaaa on #f5f5f5 (2.13:1) | flagged | not run (jsdom can't render contrast) | True positive (confirmed by WCAG math) |
| issues_page_2 | low-contrast-text | #777777 on #ffffff (4.48:1) | flagged | not run | True positive, but borderline -- 0.02 under threshold |
| issues_page_2 | non-descriptive-link | "Read more" | flagged | not flagged (axe only checks a link has *some* accessible name) | True positive, context-dependent judgment call |
| issues_page_2 | input-missing-label | #newsletter_email | flagged | flagged | True positive (both tools agree) |
| issues_page_3 | heading-skip | h1 -> h4 | flagged | flagged | True positive (both tools agree) |
| issues_page_3 | non-descriptive-link | "here" | flagged | not flagged | True positive, context-dependent judgment call |
| sample_page | img-missing-alt | logo.png | flagged | flagged | True positive (both tools agree) |
| sample_page | img-empty-alt | hero-banner.jpg | flagged | not flagged | True positive (judgment call -- banner reads as meaningful, not decorative) |
| sample_page | heading-skip | h1 -> h3 | flagged | flagged | True positive (both tools agree) |
| sample_page | low-contrast-text | #999999 on #ffffff (2.85:1) | flagged | not run | True positive (confirmed by WCAG math) |
| sample_page | non-descriptive-link | "Click here" | flagged | not flagged | True positive, context-dependent judgment call |
| sample_page | input-missing-label | #email (has placeholder="Email") | flagged | **not flagged** (axe accepts a placeholder as an accessible name) | True positive per WCAG technique F62 (placeholder-only labels fail), but a real methodological disagreement with axe's default ruleset |
| sample_page | input-missing-label | #business_name | flagged | flagged | True positive (both tools agree) |

**Totals:** 15 ClearSite findings across 6 pages -> 14 true positives, 1 false positive.
Precision = 14/15 = 0.93. Recall = 14/14 = 1.00 (no confirmed issue in the 5 checked
categories was missed on this test set).
