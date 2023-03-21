# ———————— retrieve data

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

# To use safari you have to enable remote control in settings
#driver = webdriver.Safari()

driver = webdriver.Chrome()
url = "https://www.wholesome.co/shop/flower/"
driver.get(url)

#THERE IS AN AGE CHECK THAT HAPPENS THIS CLICKS THE BUTTON TO CONTINUE TO THE SITE
elem = driver.find_element(By.CLASS_NAME, 'button')
elem.send_keys(Keys.RETURN)


products = driver.find_elements(By.CLASS_NAME, "productListItem")

# CHECK YOU HAVE AT LEAST 1 PRODUCT IN YOUR LIST OF PRODUCTS
assert len(products) > 0

# CREATE DICTIONARY OF PRODUCT URLS
product_dict = {}
count = 0
for val in products:
	new_url = val.find_element(By.TAG_NAME, 'a').get_attribute('href')
	#product_name = new_url.rsplit('/')[-1]
	#temp_data = [product_name, new_url]
	product_dict[count] = new_url
	count += 1
# CHECK ALL PRODUCTS HAVE URLS
# assert len(product_dict.values()) == len(products)
# DO WE WANT IT TO FAIL IF ONE PRODUCT DOESN'T HAVE A URL OR WORK SO LONG AS WE HAVE AT LEAST 1 URL?
assert len(product_dict.values()) > 0

def build_data_table(driver):
	data_table = driver.find_element(By.CLASS_NAME, "pdpAttributesTable")
	rows = data_table.find_elements(By.TAG_NAME, "tr")
	# CHECK YOU HAVE DATA TO BUILD THE DICTIONARY WITH
	assert len(rows) > 0
	data_dict = {}
	for val in range(0, len(rows)):
		data_key = rows[val].find_element(By.TAG_NAME, "th").text
		data_value = rows[val].find_element(By.TAG_NAME, "td").text
		data_dict[data_key] = data_value
	return data_dict

# RETRIEVE DATA FOR EACH PRODUCT AND BUILD DICTIONARY
product_data_dict = {}
for val in product_dict.keys():
	goto_page = product_dict.get(val)
	driver.get(goto_page)
	wait = WebDriverWait(driver, 5)
	data_dict = build_data_table(driver)
	product_data_dict[val] = [goto_page, data_dict]
	wait = WebDriverWait(driver, 5)

# ———————— pivot data
import pandas as pd


df = pd.DataFrame.from_dict(product_data_dict, orient='index')
all_data = pd.DataFrame()
for val in range(0, len(product_data_dict.keys())):
	temp = pd.DataFrame.from_dict(df.loc[val][1], orient="index").transpose()
	temp["product_name"] = product_data_dict.get(val)[0].rsplit('/')[-1]
	all_data = all_data.append(temp, ignore_index=True)

all_data.reset_index(inplace=True, drop=True)

# ———— save data to a file
from datetime import datetime

filename = "product_data_" + datetime.today().strftime("%m_%d_%Y")+ ".txt"
with open(filename, "w") as f:
	all_data.to_csv(f, index=False)
