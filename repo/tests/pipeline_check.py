"""PIPELINE SMOKE TEST ONLY. Builds synthetic pages in a temp dir to confirm the scripts run end to end.
Its numbers are meaningless and must NEVER appear in the paper."""
import os, sys, random, tempfile, pathlib, subprocess
root = pathlib.Path(__file__).resolve().parent.parent
random.seed(1)
tmp = pathlib.Path(tempfile.mkdtemp()); (tmp / "data/raw").mkdir(parents=True); (tmp / "results").mkdir()
for s in range(8):
    imgs = []
    for i in range(12):
        decor = random.random() < 0.5
        name = random.choice(["divider", "spacer", "arrow"]) if decor else random.choice(["team", "photo", "product"])
        imgs.append(f'<a href="/x"><img src="/img/{name}{i}.jpg" alt="" width="{random.randint(5,40) if decor else random.randint(200,600)}" height="{random.randint(5,40) if decor else random.randint(150,500)}"></a>')
    (tmp / f"data/raw/site{s}.html").write_text("<html><body>" + "".join(imgs) + "</body></html>")
sys.path.insert(0, str(root / "src"))
os.chdir(tmp)
import extract, pandas as pd
extract.main("data/raw", "data/candidates.csv")
df = pd.read_csv("data/candidates.csv")
df["label"] = ["decorative" if d == 1 else "meaningful" for d in df["name_decor_words"]]
df.to_csv("data/labeled.csv", index=False)
import train_eval
print("PIPELINE SMOKE TEST (synthetic data, numbers meaningless)")
r = train_eval.main("data/labeled.csv", 0)
assert set(r["results"]) == {"clearsite_rule", "axecore_rule", "filename_heuristic", "logistic_regression", "random_forest"}
print("OK: pipeline runs end to end")
