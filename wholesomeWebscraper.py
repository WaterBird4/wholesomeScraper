
# ———————— retrieve data

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

# To use safari you have to enable remote control in settings
#driver = webdriver.Safari()

driver = webdriver.Chrome()
url = “https://www.wholesome.co/shop/flower/“
driver.get(url)

elem = driver.find_element(By.CLASS_NAME, ‘button’)
elem.send_keys(Keys.RETURN)

products = driver.find_elements(By.CLASS_NAME, “productListItem”)

assert len(products) > 0

product_dict = {}
count = 0
For val in products:
	new_url = val.find_element(By.TAG_NAME, ‘a’).get_attribute(‘href’)
	product_dict[count] = new_url
	count += 1


def build_data_table(driver):
	data_table = driver.find_element(By.CLASS_NAME, “pdpAttributesTable”)
	rows = data_table.find_elements(By.TAG_NAME, “tr”)
	assert len(rows) > 0
	data_dict = {}
	for val in range(0, len(rows)):
		data_key = rows[val].find_element(By.TAG_NAME, ’th’).text
		data_value = rows[val].find_element(By.TAG_NAME, ‘td’).text
		data_dict[data_key] = data_value
	return data_dict


product_data_dict = {}
for val in product_dict.keys():
	goto_page = product_dict.get(val)
	driver.get(goto_page)
	wait = WebDriverWait(driver, 10)
	data_dict = build_data_table(driver)
	product_data_dict[val] = [goto_page, data_dict]
	wait = WebDriverWait(driver, 10)

# ———— save data to a file
from datetime import datetime

filename = 'product_data_' + datetime.today().strftime('%m_%d_%Y')+ '.txt'

with open(filename, ‘w’) as f:
	for k in product_data_dict.keys():
		f.write(str(k) + “|” + str(product_data_dict.get(k)) + ‘,\n’)


# ———————— pivot data
import pandas as pd


df = pd.DataFrame.from_dict(product_data_dict, orient='index')
column_names = [‘url’, ‘data_dict’]
df.columns = column_names


column_names = ['Strain Type', 'THCa', 'Total THC', 'CBDa', 'Total CBD', 'Total CBC', 'Total CBG', 'Lot Expiration']
initial_values = [0, 1, 2, 3, 4, 5, 6, 7]
all_data = pd.DataFrame(data=[column_names, initial_values])
all_data.column_names = column_names

for k in product_data_dict.keys():
	temp = pd.DataFrame.from_dict(product_data_dict.get(k)[1], orient='index’).transpose()
	all_data = all_data.append(temp)

all_data = pd.DataFrame()
for val in range(0, len(product_data_dict.keys())):
	temp = pd.DataFrame.from_dict(df.loc[val][‘data_dict’], orient=‘index’).transpose()
	all_data = all_data.append(temp, ignore_index=True)
	

for val in range(0, len(product_data_dict.keys())):
	url = df.loc[val][‘url’]
	all_data.at[val, ‘url’] = url



