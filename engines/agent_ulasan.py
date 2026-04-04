import time
import sys
import csv
from playwright.sync_api import sync_playwright

def scrape_ulasan(url, output_filename):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()
        
        print(f"==> Membuka halaman produk... ")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(4)
        
        page.evaluate("window.scrollBy(0, 500)")
        time.sleep(1)
        
        tab_ulasan = page.locator("button[data-testid='review']")
        if tab_ulasan.count() > 0:
            tab_ulasan.first.click()
            time.sleep(3)
        else:
            try:
                page.locator("text=Ulasan").first.click()
                time.sleep(3)
            except:
                pass
                
        hasil_crawling = []
        review_id = 1
        
        for halaman in range(1, 1000):
            print(f"==> Mengambil ulasan halaman {halaman}...")
            for i in range(4):
                page.evaluate("window.scrollBy(0, 500)")
                time.sleep(1.5)
            
            reviews = page.locator("article")
            if reviews.count() == 0:
                break
                
            extracted_data = page.evaluate('''() => {
                let results = [];
                let articles = document.querySelectorAll("article");
                
                for(let art of articles) {
                    let textContent = art.innerText.trim();
                    let lines = textContent.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                    
                    if (lines.length < 2 || textContent.includes("pembeli merasa puas") || (textContent.includes("rating") && textContent.includes("ulasan") && lines.length > 5 && lines[0].includes("."))) {
                        continue;
                    }
                    
                    let goldStars = 0;
                    let svgs = art.querySelectorAll('svg');
                    for (let svg of svgs) {
                        let html = svg.outerHTML.toLowerCase();
                        if (html.includes('#ffd45f') || html.includes('yn300') || html.includes('color-star-active')) {
                            goldStars++;
                        }
                    }
                    
                    if (goldStars === 0) {
                        let ratingLabel = art.querySelector('[aria-label*="bintang"]');
                        if (ratingLabel) {
                            let match = ratingLabel.getAttribute('aria-label').match(/\\d+/);
                            if (match) goldStars = parseInt(match[0]);
                        }
                    }
                    
                    if (goldStars > 5) goldStars = 5;
                    
                    let waktu = lines[0];
                    let username = lines[1];
                    let varian = "-";
                    
                    let indexUlasan = 2;
                    if (lines.length > 2 && lines[2].includes("Varian:")) {
                        varian = lines[2].replace("Varian: ", "");
                        indexUlasan = 3;
                    }
                    
                    let review_lines = [];
                    for (let j = indexUlasan; j < lines.length; j++) {
                        let l = lines[j];
                        if (l.includes("orang terbantu") || l === "Membantu" || l === "Lihat Balasan" || l.includes("Laporkan")) {
                            break;
                        }
                        review_lines.push(l);
                    }
                    
                    results.push({
                        waktu: waktu,
                        username: username,
                        varian: varian,
                        rating: goldStars,
                        review: review_lines.join(" ").trim()
                    });
                }
                return results;
            }''')
            
            for item in extracted_data:
                item["id"] = review_id
                hasil_crawling.append(item)
                review_id += 1
                
            next_button = page.locator('button[aria-label="Laman berikutnya"]')
            if next_button.count() > 0 and not next_button.first.is_disabled():
                next_button.first.click()
                time.sleep(5)
            else:
                next_button_alt = page.locator('button[aria-label="Halaman berikutnya"]')
                if next_button_alt.count() > 0 and not next_button_alt.first.is_disabled():
                    next_button_alt.first.click()
                    time.sleep(5)
                else:
                    break
                    
        if hasil_crawling:
            with open(output_filename, "w", encoding="utf-8", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["id", "waktu", "username", "varian", "rating", "review"])
                writer.writeheader()
                writer.writerows(hasil_crawling)
            print(f"[OK] File disimpan di: {output_filename}")
        else:
             print("[ERROR] Gagal mengekstrak data.")

        browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: py agent_ulasan.py <url> <output_file>")
        sys.exit(1)
    scrape_ulasan(sys.argv[1], sys.argv[2])
