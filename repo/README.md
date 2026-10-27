# ClearSite: empty-alt image classification and accessibility checker

Code for the ClearSite paper. Contains (1) a rule-based accessibility checker with five checks,
(2) a Node.js harness that runs axe-core on the same pages, and (3) a pipeline that compares
models for one task: given an image with `alt=""`, is it **decorative** (correct) or **meaningful** (needs a text alternative)?

## Status (read first)
- Implemented and run: the pilot (6 self-written pages, `pilot/`): ClearSite checker vs axe-core.
- Implemented and run on hand-labeled data from 34 public websites (406 images): collection, feature extraction, and 5-model comparison (`src/`, `data/labeled.csv`, `results/`).
- The checked-in comparison uses website-grouped cross-validation and seed 0. See `results/model_comparison.json` for the recorded metrics.

## Requirements
- Python 3.13 (tested 3.13.16), `pip install -r requirements.txt` (scikit-learn 1.9.1, pandas 3.0.5, beautifulsoup4 4.15.0, matplotlib)
- Node.js 18+ for the pilot axe-core run: `npm install axe-core jsdom` (axe-core 4.13, jsdom)
- Hardware: any laptop; the whole pipeline runs in seconds on CPU. No GPU. No pretrained models; models are trained from scratch with fixed seeds.

## Reproduce the pilot (Checkpoint 2 results)
```
python src/checker.py pilot/pages/sample_page.html     # repeat for each page in pilot/pages
node src/run_axe.js                                     # writes pilot/results/axecore_*.json
```
Hand-review labels: `pilot/results/manual_review.md`. Note: axe-core's color-contrast rule cannot run under jsdom (no canvas), so contrast is not compared with axe-core.

## Reproduce the main experiment
1. Put public home-page URLs in `data/urls.txt` (one per line). Check each site's terms; only public pages. The checked-in URLs and labels document the completed experiment.
2. `python src/collect.py data/urls.txt`  (respects robots.txt, 3 s delay, logs to `data/collection_log.tsv`)
3. `python src/extract.py`  -> `data/candidates.csv`. Open it and fill the `label` column by hand with `decorative` or `meaningful`
   (criteria: https://www.w3.org/WAI/tutorials/images/decorative/). Save as `data/labeled.csv`.
   If possible have a second person label a sample and report agreement.
4. `python src/train_eval.py data/labeled.csv --seed 0`  -> `results/model_comparison.{csv,json}`

Evaluation: GroupKFold by website (no site appears in both train and test), positive class = meaningful,
metrics = precision, recall, F1 plus confusion counts. Models: ClearSite rule (flag all), axe-core behavior (flag none),
filename heuristic, logistic regression, random forest (class-balanced, 200 trees).

## Tests
`python -I tests/pipeline_check.py` builds synthetic pages in a temp folder and checks that the scripts run. Its numbers are meaningless.

## Data
The repository includes hand-labeled image features and experiment results. Raw HTML snapshots of third-party websites are not included; `data/raw/*.html` is ignored by Git. Collect public pages with step 2; do not redistribute scraped pages. Share labeled features and URLs only where licensing permits.

## AI assistance disclosure
Claude (Anthropic) was used to help write and debug the code in this repository and to polish this README. All results must come from running the code.

## Third-party software
axe-core (Deque Systems, MPL-2.0), jsdom, scikit-learn, pandas, BeautifulSoup.
