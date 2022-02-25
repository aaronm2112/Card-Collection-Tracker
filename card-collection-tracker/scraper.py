
import requests
import re
from bs4 import BeautifulSoup
import nltk
nltk.download('words')
nltk.download('maxent_ne_chunker')
from nltk import word_tokenize, pos_tag, ne_chunk


#source trading card db
url = "https://www.tcdb.com/ViewAll.cfm/sp/Baseball?MODE=Years"
page = requests.get(url)

soup = BeautifulSoup(page.content,"html.parser")

year_links = soup.select("a[href^='/ViewAll.cfm/sp/Baseball/year/']")
#year_links = soup.find_all("a", href="/ViewAll.cfm/sp/Baseball/year/")

for link in year_links:
    #get all sets for this year
    #REQUEST set page for a year
    year_set_url = "https://www.tcdb.com" + link.attrs['href']
    year_set_page =  requests.get(year_set_url)
    soup = BeautifulSoup(year_set_page.content,"html.parser")
    year_set_links = soup.select("a[href^='/ViewSet.cfm']")

    #iterate through sets in a given year
    for set_link in year_set_links:
        #request each set within a year
        #get set id (sid)
        sid = re.search('(\/)([0-9])+(\/)',set_link.attrs['href'])
        
        set_url = "https://www.tcdb.com" + set_link.attrs['href']
        print(set_url)
        set_page =  requests.get(set_url)
        soup = BeautifulSoup(set_page.content,"html.parser")
        
        #check for "included sets" 
        included_sets = soup(text=lambda t: "Included Sets:" in t)

        if len(included_sets) != 0:
            #get checklist of each set
            for set in included_sets:
                print("Included")
        else:
            #goto checklist page
            checklist_url = "https://www.tcdb.com/PrintChecklist.cfm/sid" + sid.group(0)
            checklist_page = requests.get(checklist_url)
            soup = BeautifulSoup(checklist_page.content,features="lxml")
            checklist_rows = soup.select('font')
            title = soup.find('title')
            set_name = title.string
            print(checklist_url,set_name)
            print(str(type(checklist_rows)))
            if len(checklist_rows) > 1:
                checklist = [card.string for card in checklist_rows if not card.string.isspace()]
                checklist.pop(0) #pop the useleses match
            else:
                print("Unable to obtain checklist for sid", sid)  


            for card_data in checklist:
                #tokens = word_tokenize(card_data)
                #pos_tags = pos_tag(tokens)
                #print(pos_tags)
                #named_entities = ne_chunk(pos_tags)
                #if hasattr(named_entities, "label"):
                    #print(named_entities.label())
                data_list = card_data.split(" ",1)
                print("Card ID:", data_list[0], "\nCard Name:", data_list[1],"\n")




#todo: check if set contains other sets
#https://www.tcdb.com/PrintChecklistPDF.cfm/sid/231617
#sets are at /ViewSet.cfm ...
#cards are at /ViewCard.cfm ...
#people are at /Person.cfm ...

