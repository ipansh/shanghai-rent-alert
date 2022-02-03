import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
import boto3
import re
import datetime
from datetime import datetime
import io
from io import StringIO

### access telegram token
with open('/Users/ilya/Desktop/keys/telegram_token.txt') as f:
    lines = f.readlines()

telegram_token = lines[0]

### permissions for telegram bot token
bot_url = "https://api.telegram.org/bot{}/".format(telegram_token)

def retrieve_main_df_from_bucket(bucket, file_name):
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket= bucket, Key= file_name) 
    main_df = pd.read_csv(obj['Body'])
    return main_df

def scrape_smartshanghai(main_df):
    day_df = pd.DataFrame()
    listing_list = []
    
    for page_number in range(1,2):
        url = 'https://www.smartshanghai.com/housing/apartments-rent/?page={}&bedrooms[0]=1&ownership_private=1&ownership_landlord=1&ownership_agency=1&view=list'.format(page_number)
        html = requests.get(url)
        soup = BeautifulSoup(html.text, "html.parser")
        
        for tag in soup('a'):
            if bool(re.match(r'https://www\.smartshanghai\.com/housing/apartments-rent/[0-9]', str(tag.get('href')))):
                listing_list.append(tag.get('href'))
                
    for listing_url in listing_list:
        detail_list = []
        
        listing_html = requests.get(listing_url)
        listing_soup = BeautifulSoup(listing_html.text, "html.parser")
        
        detail_list.append(listing_url)
        
        detail_list.append(listing_soup.find('span', {'class' : 'price'}).get_text())
        
        for div_tag in listing_soup.find_all('div', {'class' : 'details'}):
            div_tag_children = div_tag.findChildren()
            for another_tag in div_tag_children:
                if another_tag.find('div') is not None:
                    detail_list.append(another_tag.find('div').text.strip())
        
        day_df = day_df.append(pd.Series(detail_list), ignore_index=True)
        
    day_df.columns = ['url','price', 'type','type2','availability','comission','rooms','size',
                      'floor','furnished','direction','district','area','compound','distance']
                      
    day_df = day_df[['price','type','availability','size','floor','furnished','direction','district','url']]
    day_df.loc[:,'price'] = [int(price.replace(',','')) for price in day_df['price']]
    day_df.loc[:,'floor'] = day_df['floor'].astype('int')
    
    filtered_day_df = day_df[(day_df['price'] > 5000) & (day_df['price'] < 8000) & (day_df['floor'] > 2)]
 
    main_df = main_df.append(filtered_day_df).drop_duplicates(subset = ['url'])
    
    return main_df

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def send_message(text, chat_id):
    url = bot_url + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)
    
def update_bucket_file(main_df):
    main_df.loc[:,'notified'] = 1
    main_df.loc[:,'notify_date'] = datetime.now().date().strftime('%Y/%m/%d')

    csv_buffer = io.StringIO()
    main_df.to_csv(csv_buffer)
    s3_resource = boto3.resource('s3')
    
    return s3_resource.Object('kepler-data-10', 'main_df.csv').put(Body=csv_buffer.getvalue())

def lambda_handler(event, context):
    
    main_df = retrieve_main_df_from_bucket("kepler-data-10", "main_df.csv")
    main_df = scrape_smartshanghai(main_df)
    
    if len(main_df[main_df['notified'] != 1]) == 0:
        send_message("No new options available!", 33651759)
    else:
        for notified, send_listing_url, district, floor, price in zip(main_df['notified'], main_df['url'], main_df['district'], main_df['floor'], main_df['price']):
            if notified != 1:
                send_message("New option available!\nRent: {}\nDistrict: {}\nFloor: {}\nLink: {} ".format(price, district, floor, send_listing_url), 33651759)
        else:
            pass
        
    update_bucket_file(main_df)
    
    return print('Done!')