from selenium import webdriver
#from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd
import numpy as np
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re



def scroll_page(driver):
#scroll to bottom

	SCROLL_PAUSE_TIME = 1

	# Get scroll height
	last_height = driver.execute_script("return document.body.scrollHeight")

	while True:
	    


		#workplace denotes the end of page with this dot image
	    end_of_page_dot = driver.find_elements_by_css_selector(".sx_e80168")
	    end_of_page_box = driver.find_elements_by_css_selector(".groupsStreamMemberBoxNames")

	    
	    if len(end_of_page_box) != 0:
	    	print end_of_page_box[0].text
	    else:
	    	pass

	    if len(end_of_page_dot) == 0 and len(end_of_page_box) == 0:
	    	
	    	# Scroll down to bottom
		    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

		    # Wait to load page
		    time.sleep(SCROLL_PAUSE_TIME)
	    	
	    else:
	    	print "end of page found!"
	    	break  
	    	

	    # Calculate new scroll height and compare with last scroll height
	   	# new_height = driver.execute_script("return document.body.scrollHeight")
		# if new_height == last_height:
	 #        break
	 #    last_height = new_height


def ParseStats(overall_stats):
#parser for "Comments", "shares", "Seenby", "views"

	
	post_stats = []

	for a in overall_stats:
			stat_content = a.text
			post_stats.append(stat_content)

	post_stats = [x.replace(' ', '') for x in post_stats]


	r1 = re.compile("([a-zA-Z]+)([0-9]+)")
	r2 = re.compile("([0-9]+)([a-zA-Z]+)")

	stat_dict = {"Comments": 0, "Seenby" : 0, "shares" : 0, "views" : 0 }


	for element in post_stats:
		try:
			var1 = r1.match(element)
			stat_list = list(var1.groups())

			stat_dict[stat_list[0]] = stat_list[1]

		except:
			var2 = r2.match(element)
			stat_list = list(var2.groups())
			stat_list[0], stat_list[1] = stat_list[1], stat_list[0]
			
			stat_dict[stat_list[0]] = stat_list[1]

	return stat_dict

#***************************************************************************************#
#***************************************************************************************#


option1 = webdriver.ChromeOptions()
option1.add_argument("--disable-notifications")
option1.add_argument("--ignore-certificate-errors")
option1.add_argument("--ignore-ssl-errors") #seems to occur after substantial scrolling


driver = webdriver.Chrome(chrome_options=option1)
#driver.get("https://gsk-workplace.facebook.com")
	


#login in process
#alex revill -> driver.get("https://gsk-workplace.facebook.com/profile.php?id=100027063322444")
#joe touey -> https://gsk-workplace.facebook.com/profile.php?id=100020921048090

#driver.get("https://gsk-workplace.facebook.com/profile.php?id=100020921048090")
#driver.get("https://gsk-workplace.facebook.com/groups/GAandDTechopen/")
#tech flp ->driver.get("https://gsk-workplace.facebook.com/groups/423104564839039/")
#CH Tech -> https://gsk-workplace.facebook.com/groups/1176034962538553/
#PH Tech -> https://gsk-workplace.facebook.com/groups/PharmaTechGSK/
#R&D Tech -> https://gsk-workplace.facebook.com/groups/2136274126658395/

driver.get("https://gsk-workplace.facebook.com/groups/2136274126658395/")
try:
	login_button = driver.find_element_by_xpath("//button[text()='Log In']")
	login_button.click()
except:
	login_button = driver.find_element_by_xpath("//button[text()='Log in']")
	login_button.click()


#one possibe way to get all post is to first call javascript to scroll down
#driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#call custom function scroll_page instead
scroll_page(driver)	

#empties
post_content_text = []
post_like_status = []
overall_stats = []
data = {}
data_aggregate = []
stat_content = []


#search for all post containers
post_body = driver.find_elements_by_css_selector("._5pcr")

#get_posts = post_body.find_elements_by_css_selector("._5pbx")  
print "\n\n\n"
print "Number of posts found = %r" % len(post_body)


#click all post contents before extracting text
for i in driver.find_elements_by_css_selector("a.see_more_link"):
    driver.execute_script("arguments[0].click();", i)
    


for content in range(len(post_body)):
	
	try:

		post_content = post_body[content].find_element_by_css_selector("._5pbx")

		post_content = post_content.text
		data["Post Content"] = post_content

	except:

		#in the scenario that it is a shared content
		try:
			post_content = post_body[content].find_element_by_css_selector("._5pco")
			post_content = post_content.text
			data["Post Content"] = post_content
		except:
			data["Post Content"] = np.nan

	#name/to group/ date/ time
	try: 
		header = post_body[content].find_element_by_css_selector("div.s_fam0bjoh_.l_fam0be1m2.clearfix")
	
	#get date & time value
		date_time = header.find_element_by_css_selector("._5ptz").get_attribute("title")
		date_time_list = [x.strip() for x in date_time.split(',')]
		data["Time"] = date_time_list[1]
		data["Date"] = date_time_list[0]

	except:
		data["Time"] = np.nan
		data["Date"] = np.nan

	#get posted_by _5vra
	try:
		posted_by = header.find_element_by_css_selector("._5vra")
		data["Posted By"] = posted_by.text

	except:
		data["Posted By"] = np.nan


	bs4_this = BeautifulSoup(post_body[content].get_attribute('outerHTML'), 'html.parser')

	try:
		#getnumber of likes 
		

		hidden_tag = bs4_this.find('span', {'class' : '_1g5v'})

		total_likes = hidden_tag.string
		#total_likes = header.find_element_by_xpath("//a[@class='_2x4v']")
		
		data["Number of Likes"] = total_likes

	except:
		data["Number of Likes"] = np.nan


	try:
		#Get number of Comments, Shares, Seen by, views
		temp = post_body[content].find_elements_by_css_selector("._ipo")
		#find the elements within this object
		overall_stats = temp[0].find_elements_by_css_selector("._36_q")
		

		# moved to ParseStats
		# for a in overall_stats:
		# 	stat_content = a.text
		# 	print stat_content + "\n\n\n"
		# 	post_stats.append(stat_content)

		#call parser for "Comments", "shares", "Seenby", "views"
		post_stats_parsed = ParseStats(overall_stats)

		data["Comments"] = post_stats_parsed["Comments"]
		data["Shares"] = post_stats_parsed["shares"]
		data["Seen by"] = post_stats_parsed["Seenby"]
		data["Views"] = post_stats_parsed["views"]

	except:
		data["Comments"] = np.nan
		data["Shares"] = np.nan
		data["Seen by"] = np.nan
		data["Views"] = np.nan



	#put everything together
	data_aggregate.append(data.copy())
	

print data_aggregate

df = pd.DataFrame(data_aggregate)

#Mon/Tues/Wed/Thu/Fri/Sat/Sun
# temp = pd.DataFrame()
# temp['Date'] = pd.to_datetime(df['Date'])
# df['Day'] = temp['Date'].dt.day_name()



df.to_csv('gsk_CH_Tech.csv', encoding='utf-8')