import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Fungsi untuk mengambil data dari halaman O*NET
def scrape_onet_personality(url, personality):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Inisialisasi list untuk menyimpan data
    data = []
    
    # Temukan tabel di halaman
    table = soup.find('table')
    if table:
        rows = table.find_all('tr')[1:]  # Lewati header
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:
                job_code = cols[0].text.strip()
                job_title = cols[1].text.strip()
                job_zone = cols[2].text.strip()
                
                # Ambil interest areas
                interest_areas = cols[3].text.strip().split(', ')
                first_interest = interest_areas[0] if len(interest_areas) > 0 else None
                second_interest = interest_areas[1] if len(interest_areas) > 1 else None
                third_interest = interest_areas[2] if len(interest_areas) > 2 else None
                
                # Cek apakah ditampilkan di "Fewer Occupations"
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
    
    return pd.DataFrame(data)

# Fungsi untuk mengambil dataset pekerjaan
def scrape_onet_occupations(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    data = []
    table = soup.find('table')
    if table:
        rows = table.find_all('tr')[1:]  # Lewati header
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
    
    return pd.DataFrame(data)

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

# Scraping dataset RIASEC
riasec_dfs = []
for personality, url in riasec_urls.items():
    df = scrape_onet_personality(url, personality)
    riasec_dfs.append(df)

# Gabungkan semua dataset RIASEC
riasec_combined = pd.concat(riasec_dfs, ignore_index=True)

# Scraping dataset pekerjaan
occupation_df = scrape_onet_occupations(occupation_url)

# Simpan ke CSV
riasec_combined.to_csv('riasec_dataset.csv', index=False)
occupation_df.to_csv('occupation_dataset.csv', index=False)

print("Dataset berhasil disimpan: riasec_dataset.csv dan occupation_dataset.csv")