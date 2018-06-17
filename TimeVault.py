# A music, activity, and weather diary.
# The GUI is mostly superfluous.

import requests  # internet connection
from bs4 import BeautifulSoup  # scraping html information
import json  # bs4 helper
import time  # recording the date
import sqlite3  # table entries
import pandas as pd  # printing an attractive table
import tabulate as tab  # printing an attractive table

# kivy GUI imports
import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout


# Weather
def get_weather():
    # Enter your city coords
    html = requests.get("https://weather.com/en-CA/weather/today/l/cd81ca7148657b33cf62a3e49a47ed674be8b06e8a66ea1d91c9326b9ac0d784")
    soup = BeautifulSoup(html.content, "html.parser")

    weatherTEMP = soup.find("div", class_="today_nowcard-temp").span.get_text()
    weatherFEELS = soup.find("span", classname="deg-feels").get_text()

    # print("City weather:\n" + weatherTEMP + " feels like " + weatherFEELS + "\n")
    return weatherTEMP # + ", feels like " + weatherFEELS


# Print db table
def print_db_table(conn):
    df = pd.read_sql("SELECT * FROM Personal", conn)
    print(tab.tabulate(df, headers=["Date", "Artist", "Track", "Event", "Weather"],
                            tablefmt='grid',
                            showindex=False) )

# SQL table processes
def main(artist, track, event):

    # Table entry data:
    date = time.strftime("%b %d, %Y")
    weather = get_weather()

    print(date, artist, track, event, weather)

    # Table entry process:
    conn = sqlite3.connect('Personal.db')
    c = conn.cursor()

    # If table hasn't already been created, create one:
    c.execute("CREATE TABLE IF NOT EXISTS Personal (date, Artist, Track, Event, Weather)")

    # Save new scraped data if it's a new day:
    try:
        c.execute('CREATE UNIQUE INDEX IF NOT EXISTS MyUniqueIndexName ON Personal (date)')
        c.execute('INSERT INTO Personal VALUES (?,?,?,?,?)', (date, artist, track, event, weather))
    except sqlite3.IntegrityError:
        print("Daily entry already in table.")

    # Print db table:
    print_db_table(conn)

    # Save and exit:
    conn.commit()
    conn.close()


class MyApp(App):
    
    # button click function
    def buttonClicked(self,btn):
        artist = self.txt0.text
        track = self.txt1.text
        event = self.txt2.text

        if btn.text == 'Enter':
            btn.text = "Place in Table"
            main(str(artist), str(track), str(event))
        elif btn.text == 'Place in Table':
            btn.text = 'Entry Successful'

    # layout
    def build(self):
        layout = BoxLayout(orientation='vertical')

        root = FloatLayout()

        # label variables
        x = 1.
        y = .4

        self.lbl0 = Label(text="Artist of the day:", bold='true', font_size=18, size_hint=(x, y))
        layout.add_widget(self.lbl0)
        self.txt0 = TextInput(text='', multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.txt0)

        self.lbl1 = Label(text="Track of the day:", bold='true', font_size=18, size_hint=(x, y))
        layout.add_widget(self.lbl1)
        self.txt1 = TextInput(text='', multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.txt1)

        self.lbl2 = Label(text="Activity of the day:", bold='true', font_size=18, size_hint=(x, y))
        layout.add_widget(self.lbl2)
        self.txt2 = TextInput(text='', multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.txt2)

        btn1 = Button(text="Enter")
        btn1.bind(on_press=self.buttonClicked)

        layout.add_widget(btn1)
        root.add_widget(layout)

        return root



# run app
if __name__ == "__main__":
    Config.set('graphics', 'width', '300')
    Config.set('graphics', 'height', '400')
    MyApp().run()
