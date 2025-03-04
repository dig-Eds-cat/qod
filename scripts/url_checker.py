import asyncio
import pandas as pd
import aiohttp
from typing import List, Dict

GITHUB_BASE = (
    "https://raw.githubusercontent.com/dig-Eds-cat/digEds_cat/refs/heads/main/"
)
EDITIONS = f"{GITHUB_BASE}/digEds_cat.csv"
MAX_RETRIES = 3
RETRY_DELAY = 1


async def check_url(session: aiohttp.ClientSession, url_data: Dict) -> Dict:
    """Check a single URL and return the result with retries."""
    for attempt in range(MAX_RETRIES):
        try:
            async with session.get(
                url_data["URL"],
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"  # noqa:
                },
                timeout=aiohttp.ClientTimeout(total=15)  # 15 seconds timeout
            ) as response:
                url_data["status"] = response.status
                url_data["error"] = ""
                return url_data
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
                continue
            url_data["status"] = 404
            url_data["error"] = str(e)
    return url_data


async def check_urls(data: List[Dict]) -> List[Dict]:
    """Check all URLs concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [check_url(session, url_data) for url_data in data]
        return await asyncio.gather(*tasks)


async def main():
    print(f"fetching {EDITIONS}")
    df = pd.read_csv(EDITIONS)
    data = df[["id", "URL"]].to_dict("records")

    results = await check_urls(data)

    results_df = pd.DataFrame(results)
    print("saving result as result.csv")
    results_df.to_csv("result.csv", index=False)
    print("done")


if __name__ == "__main__":
    asyncio.run(main())
