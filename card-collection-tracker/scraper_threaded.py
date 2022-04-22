from typing import Type
import requests
import re
from queue import Queue
from bs4 import BeautifulSoup
import time
import multiprocessing
import json
import concurrent.futures
def search(set_name, sets):
    for set in sets:
        if set['name'] == set_name:
            return set


def extract_checklists(set_link):
    sid = re.search('(\/)([0-9])+(\/)',set_link.attrs['href']) # get sid in the form '/[sid here]/'
        
    set_url = "https://www.tcdb.com" + set_link.attrs['href']
    print(set_url)
    set_page =  requests.get(set_url)
    soup = BeautifulSoup(set_page.content,"html.parser")
    data = {"checklist": []}
    
    #check for "included sets" 
    included_sets = soup(text=lambda t: "Included Sets:" in t)
    if len(included_sets) != 0:
        #get checklist of each set
        #basically call extract_sets
        included_sets_links = soup.select("a[href^='/ViewSet.cfm']")
        data["checklist"] = "Collection w/ included sets"
        #todo
    else:
        #goto checklist page
        checklist_url = "https://www.tcdb.com/PrintChecklist.cfm/sid" + sid.group(0)
        checklist_page = requests.get(checklist_url)
        soup = BeautifulSoup(checklist_page.content,features="lxml")
        checklist_rows = soup.select('font')
        title = soup.find('title')
        set_name = title.string
        if len(checklist_rows) > 1:
            checklist = [card.string for card in checklist_rows if not card.string.isspace()]
            checklist.pop(0) #pop the useleses match
            data["checklist"].append({"name": set_name, "cards": []})
            print(set_name)
            for card_data in checklist:
                data_list = card_data.split(" ",1)
                #data["checklist"][0]["cards"].append({"id": data_list[0], "name": data_list[1]})
                data["checklist"][data["checklist"].index(search(set_name,data["checklist"]))]["cards"].append({"id": data_list[0], "name": data_list[1]})
                print("Card ID:", data_list[0], "\nCard Name:", data_list[1],"\n")
            return data

def extract_sets(year_link, lock):
    #is_included - boolean to determine the type of scrape we want to do
    time.sleep(1)
    year_set_url = "https://www.tcdb.com" + year_link.attrs['href']
    print("Scraping for the year: ", year_link.string)
    data = {"year": year_link.string, "sets": []}
    year_set_page = requests.get(year_set_url)
    soup = BeautifulSoup(year_set_page.content, "html.parser")
    year_set_links = soup.select("a[href^='/ViewSet.cfm']")

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for set_link in year_set_links:
            futures.append(executor.submit(extract_checklists, (set_link)))
        for future in concurrent.futures.as_completed(futures):
            try:
                #file_data = json.load(file)
                #file_data.update(future.result())
                #json.dump(file_data, file)
                #json.dump(future. manner that doesn't hurt her feelings when he explains that the director of the film wasn't sure about her capabilities as an actress... He 
                data["sets"].append(future.result())
            except TypeError:
                print("Type Error exception")
    return data
def extract_years(soup, lock):
    file = open("card_data.json", "w")
    time.sleep(1)
    year_links = soup.select("a[href^='/ViewAll.cfm/sp/Baseball/year/']")
    year_links.sort(reverse=True, key = lambda x: int(x.string)) #sort links by year so we do them in order

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        data = {"data": []}
        for year_link in year_links:
            if(int(year_link.string) >= 20):
                futures.append(executor.submit(extract_sets,(year_link), (lock)))
        for future in concurrent.futures.as_completed(futures):
            try:
                #file_data = json.load(file)
                #file_data.update(future.result())
                #json.dump(file_data, file)
                #json.dump(future.result(), file, indent=2)
                #json_data = json.dumps(future.result(), indent=2)
                #file.write(json_data)
                data["data"].append(future.result())
                #json.dump(data, file, indent=2)
            except TypeError:
                print("Type Error exception")
        json.dump(data, file, indent=2)
        file.close()

#source trading card db
url = "https://www.tcdb.com/ViewAll.cfm/sp/Baseball?MODE=Years"
page = requests.get(url)

soup = BeautifulSoup(page.content,"html.parser")
m = multiprocessing.Manager()
lock = m.Lock()
start = time.time()
extract_years(soup, lock)
end = time.time()

print("Total time ", (end-start))
