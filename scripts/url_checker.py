import pandas as pd
import requests
from tqdm import tqdm

GITHUB_BASE = "https://raw.githubusercontent.com/dig-Eds-cat/digEds_cat/refs/heads/main/"
EDITIONS = f"{GITHUB_BASE}/digEds_cat.csv"

print(f"fetching {EDITIONS}")
df = pd.read_csv(EDITIONS)

data = df[["id", "URL"]].to_dict('records')

print("checking URLs")
for x in tqdm(data):
    try:
        r = requests.get(x["URL"], headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})  # noqa:
        x["status"] = r.status_code
        x["error"] = ""
    except Exception as e:
        x["status"] = 404
        x["error"] = e

results_df = pd.DataFrame(data)
print("saving result as result.csv")
results_df.to_csv("result.csv", index=False)
print("done")
