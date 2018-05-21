# A script to record data describing the current day.
# Current recorded values: Date, weather, CAD to USD.

import requests # internet connection
from bs4 import BeautifulSoup # scraping html information
import json # bs4 helper
import time # recording the date
import sqlite3 # table entries
import pandas as pd # printing an attractive table
import tabulate as tab # printing an attractive table


# CAD Dollar
def getCADtoUSD():
	html = requests.get("https://www.bankofcanada.ca/")
	soup = BeautifulSoup(html.content, "html.parser")
	cad_html = soup.get_text()
	cad_var = cad_html[cad_html.index("titlesHomepageChart"):cad_html.index("subTitlesHomepageChart")]
	cad_json = cad_var.replace("titlesHomepageChart = ", "").replace(";", "")
	cad_json = json.loads(cad_json)
	# print("Currency:\n" + cad_json['USD'] + "\n")
	#cad = cad_json['USD'].replace("1 CAD = ", "").replace(" USD", "")
	return cad_json['USD']


# Weather
def getWeather():
	# enter your city coords
	html = requests.get("https://weather.com/en-CA/weather/today/l/cd81ca7148657b33cf62a3e49a47ed674be8b06e8a66ea1d91c9326b9ac0d784")
	soup = BeautifulSoup(html.content, "html.parser")

	weatherTEMP = soup.find("div", class_="today_nowcard-temp").get_text()
	weatherFEELS = soup.find("span", classname="deg-feels").get_text()

	# print("City weather:\n" + weatherTEMP + " feels like " + weatherFEELS + "\n")
	return weatherTEMP + ", feels like " + weatherFEELS


# Table entry date:
cad = getCADtoUSD()
date = time.strftime("%b %d, %Y")
weather = getWeather()



# Table entry process:
conn = sqlite3.connect('TimeVault.db')
c = conn.cursor()


# if table hasn't already been created, create one:
c.execute("CREATE TABLE IF NOT EXISTS TimeVault (Date, Weather, CADtoUSD)")


# Save new scraped data if it's a new day:
try:
	c.execute('CREATE UNIQUE INDEX IF NOT EXISTS MyUniqueIndexName ON TimeVault (date)')
	c.execute('INSERT INTO TimeVault VALUES (?,?,?)', (date, weather, cad))
except sqlite3.IntegrityError:
	print("Daily entry already in table.")


# print new table:
df = pd.read_sql("SELECT * FROM TimeVault", conn)
# print new table:
print(tab.tabulate(df, headers=["Date", "Weather", "CAD to USD"], tablefmt='grid', showindex=False))


conn.commit()
conn.close()

