"""
@author: Mazen Osama
@date:  27-Dec-2022
@brief:
This is a simple script to download the HTML GNC C library manual because it does not exist in PDF form
Extraction of this was easy because the HTML links reference each other in a relative manner.

This is achieved using the BeautifulSoup module in python
"""
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm # for progress bars in the console
import os
import logging

urlBase="https://www.gnu.org/software/libc/manual/html_node/"
urlIndex = "https://www.gnu.org/software/libc/manual/html_node/index.html#SEC_Contents"
logging.basicConfig(filename='failures.log', filemode='w', level=logging.DEBUG)


out=str()

def extract_man(intro_links):
    print("extracting manual...")
    for link in tqdm(intro_links):
        html_file_name = link.attrs["href"]
        if not os.path.exists(html_file_name):
            fullurl = urlBase + html_file_name
            req = requests.get(fullurl)
            # specifiying the encoding as "utf-8" helps in parsing and writing some html outputs from websites tp prevent certain UnicodeError exceptions
            with open(html_file_name, "w", encoding="utf-8") as f:
                logging.debug(f"creating file -> {html_file_name}")
                try:
                    f.write(req.text)
                    logging.debug(f"file {html_file_name} written successfully!")
                except:
                   logging.error(f"failed to write file -> {html_file_name}") 
                   continue
        else:
            print(f"file {html_file_name} already downloaded!")
   


def filter_intro(intro_links):
    filtered_info = list()
    print("filtereing links....")
    for link in tqdm(intro_links):
        if "#" in str(link.attrs["href"]):
            continue
        elif "dir" in str(link.attrs["href"]):
            continue
        else:
            filtered_info.append(link)
    print("filtering done...!")
    return filtered_info

def retry_downloading(link):
    stat = True
    html_file_name=link.attrs["href"]
    fullurl = urlBase + html_file_name
    req = requests.get(fullurl)
    with open(html_file_name, "w", encoding="utf-8") as f:
        try:
            f.write(req.text)
        except Exception as e:
            stat = False
            logging.error(f"failed to write file -> {html_file_name}, with exception: {e}") 
    return stat

def check_downloaded_files(links):
    stat = True
    print("checking downlowded files...")
    for link in tqdm(links):
        html_file_name = link.attrs["href"]
        with open(html_file_name, "r") as file:
            contents = file.read()
            if contents == "":
                stat = False
                logging.error(f"file {html_file_name} was not written successfully!..retrying now.")
                stat = retry_downloading(link)
    return stat

def move_all_files():
    print("Moving all files to new folder...")
    os.mkdir("GNU-C-Library-Manual__HTML")
    filelist = os.listdir()
    filelist = [f for f in filelist if ".html" in f]
    for file in tqdm(filelist):
        os.rename(file,"GNU-C-Library-Manual__HTML/"+file)


def main():
    global out
    # pgIndex = requests.get(url=urlIndex)

    # with open("index.html", "w") as html:
    #     html.write(pgIndex.text)


    with open("index.html", "r") as html:
        html_file = html.read()

    soup = BeautifulSoup(str(html_file), 'lxml')

    links = soup.find_all("a")
    
    filtered_intro_list = filter_intro(links)
    extract_man(filtered_intro_list)
    stat = check_downloaded_files(filtered_intro_list)

    if not stat:
        print("some file were not downloaded correctly, please check failures.log file")
    else:
        # move all created files to a folder
        move_all_files()

    print(f"Done extracting GNC C library HTML manual from {urlBase}")
    print("Please Check failures.log file for any errors during extraction.")

#---------------------------------------------------------------------------------------
if __name__=="__main__":
    main()