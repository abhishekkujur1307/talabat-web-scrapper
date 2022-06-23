from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import json


url = input('Enter restaurant link: ')

req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urlopen(req)
bs = BeautifulSoup(html.read(), 'lxml')

#Fetching the restaurant name
name = bs.find_all("div", {"class": "col-12 p-r-0"}, "a")
res_name = str(name[0].a['href'])
# Latitude and Longitude of Restaurant
latitude_longitude_data = json.loads(bs.find('script', type='application/ld+json').string)
latitude = float(latitude_longitude_data['geo']['latitude'])
longitude = float(latitude_longitude_data['geo']['longitude'])

#Creating a funtion to find the information of a restorent by just if's name
def info(q):
    u = 'https://www.talabat.com/'+str(q)

    req = Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req)

    bs = BeautifulSoup(html.read(), 'lxml')

    info = []

    # Adding restaurant_name
    for name in bs.find_all("h3", {"class": "f-22 f-m-16 color-primary"}):
        n = str(name.get_text())
        restaurant_name = n.replace(' delivers to you', '')
        info.append(restaurant_name)

    # Adding restaurant_logo
    img = bs.findAll(("img", {"class": "brand-logo"}))
    restaurant_logo = (img[1]['src'])
    info.append(restaurant_logo)

    # Adding latitude
    info.append(latitude)

    # Adding longitude
    info.append(longitude)

    # Adding cuisine_tags
    cuisines = bs.find_all("p", {"class": "mt-2 text-center f-14 f-400 cuisine-string white"})
    cuisines_tags_list = []
    for i in cuisines:
        cuisine = str(i.get_text())
        cuisines_tags_list.append(cuisine)
    info.append(cuisines_tags_list)


#    Returns
#    restaurant_name - str
#    restaurant_logo - str
#    latitude        - float
#    longitude       - float
#    cuisine_tags    - list
    return info


def restaurant_csv(restaurant_details):
    restaurant = {'restaurant_name': restaurant_details[0], 'restaurant_logo': restaurant_details[1], 'restaurant_latitude': restaurant_details[2], 'restaurant_longitude': restaurant_details[3], 'cuisine_tags':restaurant_details[4]}
    restaurant_df = pd.DataFrame(restaurant)
    # print(restaurant_df)
    restaurant_df_csv = str(restaurant_details[0]).replace(' ','_') + "_restaurant.csv"
    restaurant_df.to_csv(restaurant_df_csv, index=False)




def menu_info(u, restaurant_name):

# Using Selenium for fetching menu_details as beautiful_soup cannot do that
    driver = webdriver.Chrome()
    driver.implicitly_wait(15)
    driver.get(u)
    driver.implicitly_wait(15)
   
    
    html = driver.page_source
    driver.set_page_load_timeout(15)
    driver.quit()


    val = BeautifulSoup(html,'lxml')
    

    menu_item = val.find_all('div',{'class':'f-15'})
    item_descriptions = val.find_all('div', {'class','f-12 description'})
    item_prices = val.find_all('span', {'class','currency'})
    item_images = val.find_all('img')

    item_name_list = []
    item_description_list = []
    item_price_list = []
    item_image_list = []



    restaurant_details = []
    for item in menu_item:
        item_name = str(item.get_text())
        item_name_list.append(item_name)

    for desc in item_descriptions:
        item_description = str(desc.get_text())
        if(len(item_description) == 0):
            item_description = 'No description'
        item_description_list.append(item_description)

    for item_price in item_prices:
        item_price_val = item_price.get_text()
        item_price_list.append(float(item_price_val))
    
    length = len(item_name_list)
    for i in range(0,length):
        item_image_list.append(item_images[9+i]['src'])

    menu = {'item_name': item_name_list, 'item_description': item_description_list,'item_price(in AED)': item_price_list, 'item_image': item_image_list}
    menu_df = pd.DataFrame(menu)

    # Makes {restaurant_name}_menu_df.csv
    menu_df_csv = str(restaurant_name).replace(' ','_') + "_menu.csv"
    menu_df.to_csv(menu_df_csv, index=False)

#     Returns
#     item_name        - str
#     item_description - str
#     item_price       - float
#     item_image       - str
    return menu_df




if __name__ == '__main__':

    #Calling the info() function to fetch the restaurant information
    restaurant_details = info(res_name)
    restaurant_name = restaurant_details[0]
    restaurant_csv(restaurant_details)


    print('\nRestaurant details')
    # Prints restaurant_details
    print(restaurant_details)


    print('\nMenu details')
    # Prints menu_details
    print(menu_info(url, restaurant_name))
