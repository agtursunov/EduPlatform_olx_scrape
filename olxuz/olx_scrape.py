import requests
from bs4 import BeautifulSoup
import csv

url = "https://www.olx.uz"

def get_soup(url):
    response = requests.get(url)
    print(f"Status code: {response.status_code}")
    return BeautifulSoup(response.text, "html.parser")

def get_categories(soup):
    categories = soup.find_all("a", class_="css-1gw3rcq")
    next_categories = soup.find_all("a", class_="css-1a53ivj")
    categories.extend(next_categories)
    
    results = []
    for cat in categories:
        name = cat.get_text(strip=True)
        link = cat.get("href")
        if link and name:
            if not link.startswith("http"):
                link = url + link
            results.append((name, link))
    print(f"found categories: {len(results)}")
    return results

def save_categories_to_csv(categories, filename="olx_categories.csv"):
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Категория", "Ссылка"])
        writer.writerows(categories)

def get_ads(soup):
    texts = soup.find_all("a", class_="css-1tqlkj0")
    prices = soup.find_all("p", class_="css-1vhm4ri")
    locations = soup.find_all("p",class_ ="css-1pzx3wn")
    dates = soup.find_all("p", class_="css-1uf1vew")
    ads = []
    for i in range(len(texts)):
        title_tag = texts[i]
        title = title_tag.get_text(strip=True)

        href = title_tag.get("href")
        if href:
            link = href if href.startswith("http") else url + href
        else:
            link = 'None'

        price = 'None'
        price_tag = prices[i].find("span", {"data-testid": "ad-price"})
        str_price = price_tag.get_text(strip=True)
        price = str_price if len(str_price) > 0 else 'None'

        date_tag = dates[i]
        date = date_tag.get_text(strip=True)
        
        location_tag = locations[i]
        location = location_tag.get_text(strip=True)

        ads.append((title, price, link, location, date))  
    print(f"found titles: {len(texts)}")
    print(f"found prices: {len(prices)}")
    return ads

def save_ads_to_csv(ads, filename="vip_ads.csv"):
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Объявление", "Цена", "Ссылка"])
        writer.writerows(ads)

def main():
    soup =  get_soup(url)

    categories = get_categories(soup)
    save_categories_to_csv(categories)

    ads = get_ads(soup)
    save_ads_to_csv(ads)

if __name__ == "__main__":
    main()
