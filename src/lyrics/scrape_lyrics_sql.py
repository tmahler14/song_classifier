"""
Scrape the lyrics for the datamining project
	- Given an artist name and song name, scrape the lyrics
@author - Tim
"""

#-------------------------
# Libs
#-------------------------

# External libs
import os, sys, time
import re
from bs4 import BeautifulSoup
import requests, json
import pandas as pd
import csv
import pymysql.cursors
#import mysql_util

#-------------------------
# Globals
#-------------------------
headers = {'Accept-Encoding': 'identity'}
azheaders = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }

#-------------------------
# Functions
#-------------------------

# Parse the lyrcis to remove [] phrases and crap
def parse_lyrics(lyrics):
	lyrics = re.sub(r"\[.*\]", "", lyrics).lstrip()	# Remove the brackets from the lyrics and preliminary spaces
	#print lyrics
	return lyrics

# Build genius url
def build_genius_url(artist_name, song_name):
	artist_name = re.sub('[^0-9a-zA-Z\w\s]+', '', artist_name)
	song_name = re.sub('[^0-9a-zA-Z\w\s]+', '', song_name)
	return "https://genius.com/"+artist_name.title().replace(" ", "-")+"-"+song_name.replace(" ", "-")+"-lyrics"

# Scrape genius for lyrics
def scrape_genius_lyrics(artist_name, song_name):
	song_url = build_genius_url(artist_name, song_name)
	#print "Song URL = %s\n"%(song_url)
	html = requests.get(song_url, headers=headers)

	# most_recent_list
	doc = BeautifulSoup(html.text, 'html.parser')
	lyrics_div = doc.find_all('lyrics', {"class" : "lyrics"})
	if lyrics_div and len(lyrics_div) > 0:
		lyrics = lyrics_div[0].text
		lyrics = re.sub(r"\[.*\]", "", lyrics).lstrip()	# Remove the brackets from the lyrics and preliminary spaces
		#print lyrics
		return lyrics
	else:
		# print "ERROR: Lyrics on genius not found!"
		
		return None

def build_az_lryics(artist_name, song_name):
	artist_name = re.sub('[^0-9a-zA-Z\w\s]+', '', artist_name)
	song_name = re.sub('[^0-9a-zA-Z\w\s]+', '', song_name)

	return "http://www.azlyrics.com/lyrics/"+artist_name.replace(" ", "")+"/"+song_name.replace(" ", "")+".html"

# Scrape genius for lyrics
def scrape_az_lyrics(artist_name, song_name):
	song_url = build_az_lryics(artist_name, song_name)
	#print "Song URL = %s\n"%(song_url)

	html = requests.get(song_url, headers=azheaders)

	# most_recent_list
	doc = BeautifulSoup(html.text, 'html.parser')
	lyrics_divs = doc.find_all('div')

	idx = 0
	for i, d in enumerate(lyrics_divs):
		if d.get("class") and len(d.get("class")) > 0 and "ringtone" in d.get("class"):
			idx = i
			break

	if idx:
		lyrics_div = lyrics_divs[idx+1]
		return lyrics_div.text
	else:
		return None

# Build metro url
def build_metro_url(artist_name, song_name):
	return "http://www.metrolyrics.com/"+song_name.replace(" ", "-")+"-lyrics-"+artist_name.replace(" ", "-")+".html"


# Scrape metro lyrics
def scrape_metro_lyrics(artist_name, song_name):
	song_url = build_metro_url(artist_name, song_name)
	#print "Song URL = %s\n"%(song_url)

	html = requests.get(song_url, headers=azheaders)
	doc = BeautifulSoup(html.text, 'html.parser')

	lyrics_div = doc.find("div", {"id" : "lyrics-body-text"})

	if lyrics_div:
		return parse_lyrics(lyrics_div.text)
	else:
		#print "LYRICS NOT FOUND"
		return None


# Main function
def main():
	print "Scraping lyrics"

	# establish connection to sql server
	connection = pymysql.connect(host='127.0.0.1',user='root',password='root',db='songs')
	cursor = connection.cursor()

	# select all song IDS
	query = "SELECT songID FROM songs" 
	cursor.execute(query)
	songlist = cursor.fetchall()

	successes = 0

	missing = open('./missing_lyrics.txt', 'w')


	for myRow in songlist:
		#print myRow
		# 1.) Get song lyrics
		query = "SELECT artist, title FROM songs WHERE songID = \'%s\' ;" % myRow[0]
		cursor.execute(query)
		result_set = cursor.fetchall()

		# result_set = mysql_util.execute_query(query)

		for row in result_set:
			# print row[0], row[1]
			song_lyrics = scrape_genius_lyrics(row[0].lower(), row[1].lower())

			if song_lyrics == None:
				song_lyrics = scrape_az_lyrics(row[0].lower(), row[1].lower())

			if song_lyrics == None:
				try:
					song_lyrics = scrape_metro_lyrics(row[0].lower(), row[1].lower())
				except:
					continue

			if song_lyrics != None:
				successes += 1
				#print genius_song_lyrics.encode('utf-8')

				target = open('./lyrics/'+myRow[0]+'.lyrics', 'w')
				target.write(song_lyrics.encode('utf-8'))
				target.close()

			else:
				missing.write(myRow[0].encode('utf-8')+", "+row[0]+', '+row[1]+"\n")


	#cursor.close()
#	sys.exit()

	print "Finished sraping lyrics. Lyrics found for " + str(float(successes)/float(10000))*100 + " percent of songs."

	cursor.close()
	missing.close()



if __name__=="__main__":
    main()