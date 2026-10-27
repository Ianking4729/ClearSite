# ClearSite

ClearSite is a research project on classifying images with empty `alt` text as either decorative or meaningful, and on checking web accessibility. The paper source is in [`main.tex`](main.tex); the code and experiment data are in [`repo/`](repo/).

## Start here

See [`repo/README.md`](repo/README.md) for prerequisites, the pilot, the main experiment workflow, evaluation details, and data notes.

To reproduce the model comparison from the code directory:

```powershell
cd repo
python src/train_eval.py data/labeled.csv --seed 0
```

The experiment expects hand-labeled data in `repo/data/labeled.csv`. See the detailed README before collecting pages or interpreting results.
