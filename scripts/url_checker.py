import asyncio
import os
import pandas as pd
import aiohttp
from typing import List, Dict

GITHUB_BASE = "https://raw.githubusercontent.com/dig-Eds-cat/digEds_cat/refs/heads/main"
EDITIONS = f"{GITHUB_BASE}/digEds_cat.csv"
MAX_RETRIES = 3
RETRY_DELAY = 1

html_dir = "html"
os.makedirs(html_dir, exist_ok=True)


async def check_url(session: aiohttp.ClientSession, url_data: Dict) -> Dict:
    """Check a single URL and return the result with retries."""
    for attempt in range(MAX_RETRIES):
        try:
            start_time = asyncio.get_event_loop().time()
            async with session.get(
                url_data["URL"],
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"  # noqa:
                },
                timeout=aiohttp.ClientTimeout(total=15),  # 15 seconds timeout
            ) as response:
                end_time = asyncio.get_event_loop().time()
                content = await response.text()

                # Save content to file
                filename = f"{html_dir}/{url_data['id']}.html"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)

                # Get file size in KB
                file_size = os.path.getsize(filename) / 1024  # Convert bytes to KB

                url_data["status"] = response.status
                url_data["error"] = ""
                url_data["response_time"] = round(end_time - start_time, 3)
                url_data["content_size"] = round(
                    file_size, 2
                )  # KB with 2 decimal places
                return url_data
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"try to fetch {url_data['URL']}")
                await asyncio.sleep(RETRY_DELAY)
                continue
            url_data["status"] = 404
            url_data["error"] = str(e)
            url_data["response_time"] = -1
            url_data["content_size"] = -1
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
