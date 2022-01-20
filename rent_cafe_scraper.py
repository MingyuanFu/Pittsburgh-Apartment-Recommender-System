from bs4 import BeautifulSoup
import requests
import pandas as pd


def truncate_zipcode(zipcode):
    if '-' in str(zipcode):
        zipcode = int(zipcode.split('-')[0])
    else:
        zipcode = int(zipcode)
    return zipcode


def truncate_price(price):
    price = str(price)
    if '-' in price:
        price = float([i[1:].strip() for i in price.split('-')][0])
    elif price != '0':
        price = float(price.replace('$', ''))
    else:
        price = 0
    return int(price)


def house_scraper(filepath='rentcafe_result.csv'):
    housings = []
    for i in range(10):

        page = requests.get("https://www.rentcafe.com/apartments-for-rent/us/pa/allegheny-county/?page=" + str(i))
        soup = BeautifulSoup(page.content, 'html.parser')
        housing_list = soup.find(id="results")
        housing_items = housing_list.find_all("div", class_="item-information")

        for house in housing_items:
            title = house.find("h2", class_="building-name")['title'].replace(',', ' ')
            coordinate = house.find("div", itemprop="geo").find_all('meta')
            latitude, longitude = coordinate[0]['content'], coordinate[1]['content']
            street_address = house.find("span", itemprop="streetAddress").text.replace(',', ' ')
            zipcode = house.find("span", itemprop="postalCode").text
            try:
                price = house.find("div", class_="price").find('span').text.replace(',', '')
            except:
                price = 0
            try:
                bed_info = house.find("li", class_="data-beds").text
            except:
                bed_info = 0
            try:
                bath_info = house.find("li", class_="data-baths").text
            except:
                bath_info = 0
            try:
                amenities = house.find("div", class_="amenities").find_all('li')
                amenity_list = []
                for amen in amenities:
                    amenity_list.append(amen['title'])
                amenity_info = "+".join(amenity_list)
            except:
                amenity_info = 0

            house_info = [title, latitude, longitude, street_address, zipcode, price, bed_info, bath_info,
                          amenity_info]
            housings.append(house_info)
    df = pd.DataFrame(housings, columns=['title', 'latitude', 'longitude', 'street_address'
        , 'zipcode', 'price', 'bed_info', 'bath_info', 'amenity_info'])
    df.to_csv(filepath, index=False)
    df['zipcode'] = df['zipcode'].apply(lambda x: truncate_zipcode(x))
    df['price'] = df['price'].apply(lambda x: truncate_price(x))

    return df
