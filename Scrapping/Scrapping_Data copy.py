import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Fungsi untuk mengambil data dari halaman O*NET (untuk RIASEC dan Abilities)
def scrape_onet_category(url, category_name, is_abilities=False):
    data = []
    page = 1
    max_attempts = 50

    while True:
        page_url = f"{url}?p={page}" if page > 1 else url
        print(f"Scraping {category_name} - Page {page}: {page_url}")
        
        try:
            response = requests.get(page_url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break
        
        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table')
        table = None
        for t in tables:
            if t.find('tr') and len(t.find_all('tr')[0].find_all(['th', 'td'])) >= (3 if is_abilities else 4):
                table = t
                break
        
        if not table or not hasattr(table, 'find_all'):
            print(f"No valid table found for {category_name} at page {page}")
            break
        
        rows = table.find_all('tr')[1:]  # Lewati header
        if not rows:
            print(f"No rows found on page {page}")
            break
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= (3 if is_abilities else 4):
                job_code = cols[0].text.strip()
                job_title = cols[1].text.strip()
                
                if is_abilities:
                    ability_score = cols[2].text.strip() if len(cols) > 2 else None
                    data.append({
                        'O*NET-SOC Code': job_code,
                        'O*NET-SOC Title': job_title,
                        'Ability Score': ability_score
                    })
                else:
                    job_zone = cols[2].text.strip()
                    interest_areas = cols[3].text.strip().split(', ')
                    first_interest = interest_areas[0] if len(interest_areas) > 0 else None
                    second_interest = interest_areas[1] if len(interest_areas) > 1 else None
                    third_interest = interest_areas[2] if len(interest_areas) > 2 else None
                    shown_fewer = 'Yes' if 'Show fewer occupations' in cols[3].text else None
                    
                    data.append({
                        'O*NET-SOC Code': job_code,
                        'O*NET-SOC Title': job_title,
                        'Job Zone': job_zone,
                        'First Interest Area': first_interest,
                        'Second Interest Area': second_interest,
                        'Third Interest Area': third_interest,
                        'Shown in Fewer Occupations': shown_fewer
                    })
        
        page += 1
        time.sleep(1)
        
        if page > max_attempts:
            print(f"Reached max page limit ({max_attempts}) for {category_name}")
            break
    
    return pd.DataFrame(data)

# Fungsi untuk mengambil dataset pekerjaan
def scrape_onet_occupations(url):
    data = []
    page = 1
    max_attempts = 50
    
    while True:
        page_url = f"{url}&p={page}" if page > 1 else url
        print(f"Scraping Occupations - Page {page}: {page_url}")
        
        try:
            response = requests.get(page_url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break
        
        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table')
        table = None
        for t in tables:
            if t.find('tr') and len(t.find_all('tr')[0].find_all(['th', 'td'])) >= 3:
                table = t
                break
        
        if not table or not hasattr(table, 'find_all'):
            print(f"No valid table found for occupations at page {page}")
            break
        
        rows = table.find_all('tr')[1:]  # Lewati header
        if not rows:
            print(f"No rows found on page {page}")
            break
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                code = cols[0].text.strip()
                occupation = cols[1].text.strip()
                job_family = cols[2].text.strip()
                
                data.append({
                    'Code': code,
                    'Occupation': occupation,
                    'Job Family': job_family
                })
        
        page += 1
        time.sleep(1)
        
        if page > max_attempts:
            print(f"Reached max page limit ({max_attempts}) for occupations")
            break
    
    return pd.DataFrame(data)

# Fungsi untuk mengambil semua kategori abilities
def get_abilities_categories(base_url):
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching abilities categories: {e}")
        return {}
    
    soup = BeautifulSoup(response.content, 'html.parser')
    categories = {}
    links = soup.select('a[href*="/find/descriptor/result/1.B.1."]')
    for link in links:
        category_name = link.text.strip()
        category_url = 'https://www.onetonline.org' + link['href']
        categories[category_name] = category_url
    
    return categories

# Link dari dokumen
riasec_urls = {
    'Realistic': 'https://www.onetonline.org/explore/interests/Realistic/',
    'Investigative': 'https://www.onetonline.org/explore/interests/Investigative/',
    'Artistic': 'https://www.onetonline.org/explore/interests/Artistic/',
    'Social': 'https://www.onetonline.org/explore/interests/Social/',
    'Enterprising': 'https://www.onetonline.org/explore/interests/Enterprising/',
    'Conventional': 'https://www.onetonline.org/explore/interests/Conventional/'
}
occupation_url = 'https://www.onetonline.org/find/family?f=0&g=Go'
abilities_base_url = 'https://www.onetonline.org/find/descriptor/browse/1.B.1/'

# Scraping dataset RIASEC
riasec_dfs = []
for personality, url in riasec_urls.items():
    df = scrape_onet_category(url, personality, is_abilities=False)
    print(f"Collected {len(df)} rows for {personality}")
    riasec_dfs.append(df)

# Gabungkan semua dataset RIASEC
riasec_combined = pd.concat(riasec_dfs, ignore_index=True)
riasec_combined = riasec_combined.drop_duplicates()

# Scraping dataset pekerjaan
occupation_df = scrape_onet_occupations(occupation_url)
occupation_df = occupation_df.drop_duplicates()

# Scraping dataset abilities
abilities_categories = get_abilities_categories(abilities_base_url)
abilities_dfs = []
for category, url in abilities_categories.items():
    df = scrape_onet_category(url, f"Abilities: {category}", is_abilities=True)
    print(f"Collected {len(df)} rows for Abilities: {category}")
    if not df.empty:  # Hanya tambahkan DataFrame yang tidak kosong
        abilities_dfs.append(df)

# Gabungkan semua dataset abilities (jika ada)
if abilities_dfs:
    abilities_combined = pd.concat(abilities_dfs, ignore_index=True)
    abilities_combined = abilities_combined.drop_duplicates()
else:
    print("No abilities data collected.")
    abilities_combined = pd.DataFrame()

# Simpan ke CSV
riasec_combined.to_csv('riasec_dataset_full.csv', index=False)
occupation_df.to_csv('occupation_dataset_full.csv', index=False)
if not abilities_combined.empty:
    abilities_combined.to_csv('abilities_dataset_full.csv', index=False)

print(f"Dataset RIASEC berhasil disimpan: riasec_dataset_full.csv ({len(riasec_combined)} rows)")
print(f"Dataset Pekerjaan berhasil disimpan: occupation_dataset_full.csv ({len(occupation_df)} rows)")
if not abilities_combined.empty:
    print(f"Dataset Abilities berhasil disimpan: abilities_dataset_full.csv ({len(abilities_combined)} rows)")
else:
    print("No abilities dataset saved due to empty data.")