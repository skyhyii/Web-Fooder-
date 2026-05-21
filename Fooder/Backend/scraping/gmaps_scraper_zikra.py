from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from database.db_zikra import SessionLocal
from database.models_zikra import Restaurant, Review


class GoogleMapsScraper:

    def scrape_restaurants(self, keyword, city):

        search_query = f"{keyword} {city}"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto("https://www.google.com/maps")

            page.wait_for_timeout(5000)

            page.locator('input#searchboxinput').fill(search_query)
            page.keyboard.press('Enter')

            page.wait_for_timeout(10000)

            html = page.content()

            browser.close()

        soup = BeautifulSoup(html, 'html.parser')

        results = []

        cards = soup.find_all('div', class_='Nv2PK')

        for card in cards[:5]:
            try:
                name = card.find('div', class_='qBF1Pd').text
                rating = card.find('span', class_='MW4etd').text

                results.append({
                    'name': name,
                    'rating': rating
                })

            except:
                continue

        return results


    def save_to_database(self, restaurants, city):

        session = SessionLocal()

        for item in restaurants:

            existing = session.query(Restaurant).filter_by(
                restaurant_name=item['name'],
                city=city
            ).first()

            if existing:
                continue

            restaurant = Restaurant(
                restaurant_name=item['name'],
                rating=float(item['rating']),
                city=city
            )

            session.add(restaurant)

        session.commit()
        session.close()