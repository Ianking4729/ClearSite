"""Compare models on hand-labeled empty-alt images, splitting BY SITE (no site in both train and test).
Positive class = 'meaningful' (the image NEEDS a text alternative; ClearSite should flag it).

Models (same folds, same metrics):
  1. clearsite_rule  : flags every empty-alt image as meaningful (current ClearSite rule)
  2. axecore_rule    : flags none (axe-core accepts alt="" by default)
  3. filename_heuristic : meaningful unless filename has a decorative word / svg / ico
  4. logistic_regression
  5. random_forest
Usage: python src/train_eval.py data/labeled.csv [--seed 0]
"""
import sys, json, numpy as np, pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix

NUM = ["name_decor_words", "name_content_words", "has_width_height", "area", "aspect_ratio",
       "in_link", "link_has_text", "aria_hidden", "role_presentation", "text_len_nearby",
       "is_svg_or_icon_ext", "has_title", "has_figcaption"]

def load(path):
    df = pd.read_csv(path)
    df = df[df["label"].isin(["decorative", "meaningful"])].copy()
    df["y"] = (df["label"] == "meaningful").astype(int)
    tags = pd.get_dummies(df["parent_tag"], prefix="parent")
    X = pd.concat([df[NUM].astype(float), tags.astype(float)], axis=1)
    return df, X

def metrics(y, p):
    pr, rc, f1, _ = precision_recall_fscore_support(y, p, average="binary", zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y, p, labels=[0, 1]).ravel()
    return dict(precision=pr, recall=rc, f1=f1, tp=int(tp), fp=int(fp), fn=int(fn), tn=int(tn))

def main(path, seed=0):
    df, X = load(path)
    n_sites = df["site"].nunique()
    k = min(5, n_sites)
    if k < 2:
        sys.exit("Need labeled images from at least 2 sites.")
    gkf = GroupKFold(n_splits=k)
    names = ["clearsite_rule", "axecore_rule", "filename_heuristic", "logistic_regression", "random_forest"]
    preds = {n: np.zeros(len(df), dtype=int) for n in names}
    for tr, te in gkf.split(X, df["y"], groups=df["site"]):
        preds["clearsite_rule"][te] = 1
        preds["axecore_rule"][te] = 0
        h = ((df.iloc[te]["name_decor_words"] == 0) & (df.iloc[te]["is_svg_or_icon_ext"] == 0)).astype(int)
        preds["filename_heuristic"][te] = h.values
        lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced", random_state=seed))
        lr.fit(X.iloc[tr], df["y"].iloc[tr]); preds["logistic_regression"][te] = lr.predict(X.iloc[te])
        rf = RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=seed)
        rf.fit(X.iloc[tr], df["y"].iloc[tr]); preds["random_forest"][te] = rf.predict(X.iloc[te])
    res = {n: metrics(df["y"], p) for n, p in preds.items()}
    out = {"n_images": int(len(df)), "n_sites": int(n_sites), "n_meaningful": int(df["y"].sum()),
           "folds": k, "seed": seed, "results": res}
    print(json.dumps(out, indent=2))
    pd.DataFrame(res).T.round(3).to_csv("results/model_comparison.csv")
    json.dump(out, open("results/model_comparison.json", "w"), indent=2)
    return out

if __name__ == "__main__":
    seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 0
    main(sys.argv[1], seed)
