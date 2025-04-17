import asyncio
from pathlib import Path
import pandas as pd
from playwright.async_api import async_playwright
import time
import requests
import zipfile

BOT_TOKEN = '7257895245:AAFSp_G4-3y_TcatCMCO61ZVMTLAdu0BX8M'
CHAT_ID = '-1002526959615'

EXCEL_PATH = r"C:\1 SHARE MARKET 2025\extra\Histy_tel\1 Lacks Project - 20k.xlsx"
RESET_AFTER = 20
CONCURRENCY = 5
semaphore = asyncio.Semaphore(CONCURRENCY)

async def download_csv(slno: int, link: str, context, download_dir: Path):
    async with semaphore:
        try:
            page = await context.new_page()
            await page.goto(link, timeout=30000)
            await page.wait_for_timeout(2000)

            download_button = await page.wait_for_selector(
                '//html/body/div[2]/div/div[7]/div/div/div/div[1]/div[2]/a',
                timeout=10000
            )

            async with page.expect_download(timeout=20000) as download_info:
                await download_button.click()

            download = await download_info.value
            file_path = download_dir / f"{slno}_{download.suggested_filename}"
            await download.save_as(file_path)

            print(f"[SLNO: {slno}] Downloaded: {file_path.name}")
            await page.close()

        except Exception as e:
            print(f"[SLNO: {slno}] Failed: {link} | Reason: {str(e)}")

def zip_and_send_to_telegram(folder_path: Path, batch_number: int):
    zip_name = f"Batch_{batch_number}.zip"
    zip_path = folder_path.parent / zip_name

    # Zip the folder
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in folder_path.rglob("*"):
            zipf.write(file, arcname=file.relative_to(folder_path))

    print(f"Zipped: {zip_path}")

    # Send to Telegram
    with open(zip_path, 'rb') as f:
        response = requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendDocument',
            data={'chat_id': CHAT_ID},
            files={'document': (zip_name, f)}
        )
    print(f"Telegram upload status: {response.status_code}")

async def process_batch(batch_data, batch_number):
    download_dir = Path(f"Download_Batch_{batch_number}")
    download_dir.mkdir(exist_ok=True)

    print(f"\n[Batch {batch_number}] Starting download of {len(batch_data)} links...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=True)

        tasks = [download_csv(slno, link, context, download_dir) for slno, link in batch_data]
        await asyncio.gather(*tasks)

        await context.close()
        await browser.close()

    print(f"[Batch {batch_number}] Download complete. Sending zip to Telegram...\n")
    zip_and_send_to_telegram(download_dir, batch_number)
    time.sleep(10)

async def main():
    df = pd.read_excel(EXCEL_PATH)
    data = df.iloc[:, [0, 1]].values.tolist()

    batches = [data[i:i + RESET_AFTER] for i in range(0, len(data), RESET_AFTER)]

    for batch_number, batch_data in enumerate(batches, start=1):
        await process_batch(batch_data, batch_number)

if __name__ == "__main__":
    asyncio.run(main())
