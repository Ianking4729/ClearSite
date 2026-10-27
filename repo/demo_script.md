# ClearSite Demo Script (Under 3 Minutes)

**Target:** about 2:40-2:55 at a steady pace. Bracketed text is an on-screen cue, not narration. Run both commands once before recording, then clear the terminal with `cls`. Record in your own voice; no camera is needed.

## Before Recording

In PowerShell, from `C:\Users\Yan\Downloads\ClearSite_Repo\repo`, verify both commands:

```powershell
python src/checker.py pilot/pages/context_case.html
python src/train_eval.py data/labeled.csv --seed 0
```

Both commands have been verified from this folder. To show the results CSV in PowerShell, use:

```powershell
type results\model_comparison.csv
```

## Narration and Screen Cues

### 1. Problem (0:00-0:20)

[Show `pilot/pages/context_case.html`; point to the divider, then the house photo.]

“Some images have an empty alt on purpose because they are decoration. Others are empty by mistake. Scanners can’t tell the difference from the attribute alone. My project tests whether lightweight methods can help.”

### 2. Checker and Pilot (0:20-0:55)

[Run `python src/checker.py pilot/pages/context_case.html`; point at both warnings. Briefly show `pilot/results/manual_review.md`.]

“ClearSite flags both images. The divider is decorative, so that warning is a false alarm. The house photo is meaningful and needs a description. axe-core flags neither: it avoids the divider warning, but misses the house photo. This pilot uses six pages I wrote myself, so it demonstrates behavior rather than representing the web.”

### 3. Data and Method (0:55-1:25)

[Show `data/candidates.csv`, then scroll through a few images in `data/label_sheet.html`.]

“I found candidate sites by searching Google Maps across business and organization categories. This is a convenience sample. I collected 406 empty-alt images from 34 sites and labeled each by hand: 358 meaningful and 48 decorative. The models use HTML clues, not image pixels. I compare five methods with five-fold validation grouped by website, so each test site is held out from training.”

### 4. Results (1:25-2:25)

[Run `python src/train_eval.py data/labeled.csv --seed 0`, then `type results\model_comparison.csv`.]

“Flagging every image has the best F1, 0.937, and catches all meaningful images. But it also flags all 48 decorative images. That high F1 is largely because 88 percent of this dataset is meaningful.

“The filename heuristic is close, with F1 0.933. The random forest has the highest precision, 0.940. It correctly clears 30 decorative images, but misses 75 meaningful ones. Its F1 is 0.859. The trade-off is fewer false alarms versus more missed barriers. Since a missed accessibility barrier can be serious, I would use the forest to prioritize warnings, not silently suppress them.”

### 5. Limits and Close (2:25-2:55)

[Keep the CSV visible.]

“This is a small convenience sample, with one labeler, one seed, only 48 decorative examples, and HTML-only features. There is no browser extension yet. Next I would add more sites, measure agreement with a second labeler, add visual features, and test the tool with developers. Predictions should support human review, not replace it.”

## After Recording (not spoken)

Upload as an unlisted video, test that its link opens while logged out, then replace the supplemental-links TODO in `main.tex` with a descriptive video link before creating the submitted PDF.
