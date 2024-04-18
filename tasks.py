# import html
import time
import requests
import logging
from pathlib import Path
from robocorp import storage
from datetime import datetime, timedelta
from datetime import datetime
from robocorp.tasks import task
# from RPA.Robocorp.WorkItems import WorkItems
from robocorp import vault
from robocorp.tasks import get_output_dir
# from RPA.Excel.Files import Files as Excel
from robocorp import excel
from RPA.Browser.Selenium import Selenium 
logger = logging.getLogger(__name__)
import re


def opening_the_news_Site():
    logger.info("Opening the news site.")
    browser = Selenium()
    
    # Define Chrome options to disable popup blocking
    options = [
        "--disable-popup-blocking",
        "--ignore-certificate-errors"
    ]
    secrets =vault.get_secret('alijazeersite') 

    # Open browser with specified options
    browser.open_available_browser(secrets["url"], browser_selection="Chrome", options=options)
    return browser


def search_the_phrase(browser, phrase):
    logger.info(f"Searching the phrase: {phrase}")
    try:
        browser.click_button('Allow all')

    except:
        pass
        # finding the serach icon and field
    locator1 = "//button[@aria-pressed='false']//*[name()='svg']"
    browser.wait_until_page_contains_element(locator1, timeout=10)
    browser.click_element(locator1)
    browser.input_text("//input[@placeholder='Search']",phrase)
    browser.click_button("//button[@aria-label='Search Al Jazeera']")
    try:
        locator2 = "//select[@id='search-sort-option']"
        browser.wait_until_element_is_visible(locator2, timeout=10)
        browser.click_element(locator2)
    except:
        print("No news associated with the search phrase")
        return
    dropdown_locator = "//select[@id='search-sort-option']/option[1]" 
    browser.click_element(dropdown_locator)


def retrive_data(browser, num_months_ago, search_phrase):

    logger.info(f"Retrieving data from {num_months_ago} months ago.")

    # Declearing varibale to return the date
    data ={}
    counter = 1
    # Handling the possible inputs
    if num_months_ago == 0:
        num_months_ago =1
    current_date = datetime.now()
    target_date = current_date - timedelta(days=num_months_ago * 30)  # Assuming each month has 30 days


    # print(len(search_list_selector))
    is_there_ShowMore = True

    articles_titiles = []
    browser.wait_until_element_is_visible("xpath://*[@id='main-content-area']/div[2]/div[2]", timeout=10)
    while is_there_ShowMore:
        
        # Search result section
        
        search_list_selector = browser.find_element("xpath=//*[@id='main-content-area']/div[2]/div[2]")
        articles = browser.find_elements("tag:article", parent=search_list_selector)
        button_locator = browser.find_elements("tag:button", parent=search_list_selector)
        
        for article in articles:
            excert = browser.find_element("tag:p",parent=article)
            time_of_post, description  = extract_before_ellipsis(excert.text)
            article_date = formated_article_date(time_of_post)
            if(article_date == None):
                continue
            try:
                # print(article_date, target_date,)
                if is_within_time_frame(article_date, target_date):

                    # Now 'article' is a single WebElement, which can be used as a parent

                    title= browser.find_element("tag:h3", parent=article)
                    if title.text not in articles_titiles:
                    
                        articles_titiles.append(title.text)
                        
                        # does the title or description contains money
                        # checking how many times the search keyword apears in title and description
                        no_of_search_phrase, contains = no_of_topic_and_money_amount(title.text, 
                                                                            description, search_phrase)

                        
                        image = browser.find_element(locator="tag:img", parent=article)
                        image_url = image.get_attribute('src')

                        picture_name = image_url.split("/")[-1]  # Extracting picture name from URL
                        output_path = Path(get_output_dir()) / picture_name

                        data[counter] = [counter,title.text, article_date, description, 
                                            picture_name, no_of_search_phrase, contains]
                        #update counter
                        counter+=1

                        print("Title now")
                        print(image_url)  # Or perform further actions with the image URL.
                        print(picture_name,"The name of the picuture")
                        print(output_path, "The output path of the picture")
                        # print(image.scr)
                        print(title.text) # This will print the text of the title within each article
                        print( time_of_post, article_date)

                        print(description)
                        print("ONe article ends here")
            except Exception as e:
                print(e, "Error now now")

        # time.sleep(2)
        try:
            ads_locator = browser.find_element("xpath=//button[@aria-label='Close Ad']")
            browser.click_button(ads_locator) 
        except Exception as e:
            print(e,"My massege> NO Adds Found")
            pass
        try: 
            # Scroll the element into view
            browser.scroll_element_into_view(button_locator)
            browser.wait_until_element_is_enabled(button_locator, timeout=10)

            browser.click_button(button_locator)
            time.sleep(5)
            print("Botton Clicked")
    
        except Exception as e: 
            print(e, "Error")
            is_there_ShowMore = False
    return data


def save_data_to_Excel(workbook, data, sheet_name):
    worksheet = workbook.worksheet(sheet_name)
    for i in range(len(data)):
        worksheet.append_rows_to_worksheet(data[i], header=False)
     # Save the workbook
    # worksheet.save_workbook()

@task
def main():
    logger.info("Starting the main task.")

    browser_instance = opening_the_news_Site()

    # Define the path for the new Excel file in the output directory
    output_dir = Path(get_output_dir())
    excel_file_path = output_dir / "Articles.xlsx"
    
    # Create a new Excel workbook and add a worksheet with the name 'Sheet1'
    workbook = excel.create_workbook(fmt="xlsx", sheet_name="Sheet1")
    
    
    # Append a row with column headers
    sheet_name = "Sheet1"
    worksheet = workbook.worksheet(sheet_name)
    row_to_append = [
        ["No", "Title", "Date", "Description", "Picture Filename", "Count", "Contains Money"]
    ]
    
    # Append the row to the worksheet
    worksheet.append_rows_to_worksheet(row_to_append, header=False)
    

    # Retrieve the text content from the asset
    content = storage.get_text("parameters")

    # Split the content into lines
    topics_and_months = content.splitlines()
    
    for topic_and_month in topics_and_months:
        print(len(topic_and_month), "The length of topics and months")
        # Assuming each line is "search_phrase,number_of_months"
        search_phrase, number_of_months = topic_and_month.split(',') 
          
        # Convert number_of_months to an integer
        number_of_months = int(number_of_months.strip())
        search_phrase = search_phrase.strip()
        print(number_of_months, search_phrase, "zzzzzzzzzzzzz")
        # Create an output work item with this data as the payload
        # workitems.outputs.create(payload={"search_phrase": search_phrase, "number_of_months": number_of_months})

        
        search_the_phrase(browser_instance, search_phrase)
        data_retrieved =  retrive_data(browser_instance, number_of_months, search_phrase)

        save_data_to_Excel(workbook, data_retrieved, sheet_name)
        workbook.save(excel_file_path)

    workbook.save(excel_file_path)
    print("This is Selamu's output")
    
    # Close the browser
    # browser.close_all_browsers()



def extract_before_ellipsis(text):
    if len(text) <=0:
        return 
    # Split the text at '...'
    date_part = "No Date"
    description_part = ""
    try:
        parts = text.split(" ...")
        # Take the first part, before the '...'
        date_part = parts[0]
        description_part=parts[1]
    except:
        pass
    description_part.replace("Â","")

    return date_part, description_part
def formated_article_date(date_extracted):
    # cleaning the date part
    date_extracted = date_extracted.strip()

    # possible hours, minutes and seconds
    possible_hms = ["second", "seconds","min\xadutes","minute", "minutes", "hour","hours"]
    possible_days = ["day", "days"]
    possible_months_format_One =["January", "Feburary", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    possible_months_format_Two =["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    current_date = datetime.now()
    try:   
        if(date_extracted.split(" ")[1]) in possible_hms:
            date_object = current_date
            formatted_date = date_object.strftime("%Y%m%d")
            return formatted_date
        elif date_extracted.split(" ")[1] in possible_days:
            # Split the expression to extract the number of days
            num_days = int(date_extracted.split()[0])
            # Calculate the target date by subtracting the number of days from the current date
            date_object = current_date - timedelta(days=num_days)
            formatted_date = date_object.strftime("%Y%m%d")
            return formatted_date
        elif date_extracted.split(" ")[0] in possible_months_format_One:
            # Convert the date string to a datetime object
            date_object = datetime.strptime(date_extracted, "%B %d, %Y")
    
            # Format the datetime object to the desired format
            formatted_date = date_object.strftime("%Y%m%d")
    
            return formatted_date
        elif date_extracted.split(" ")[0] in possible_months_format_Two:
            # Convert the date string to a datetime object
            date_object = datetime.strptime(date_extracted, "%b %d, %Y")
            formatted_date= date_object.strftime("%Y%m%d")
            return formatted_date

    except Exception as e:
            return e, None
def is_within_time_frame(article_date, target_date):
    # Convert article date string to a datetime object
    try:
        article_datetime = datetime.strptime(article_date, "%Y%m%d")
    except Exception as e:
        return e, False
    # Check if the article date is within the time frame (since the target date)
    return article_datetime  >= target_date

def no_of_topic_and_money_amount(title, description, search_phrase):
    # Trying to find the number of times the title and description contains
    countT = title.split(" ").count(search_phrase)
    countD = description.split(" ").count(search_phrase)

    # Regex pattern to match various money formats
    pattern = r"\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\d+\s(?:dollars|USD)"
    
    # Find all matches in the text
    matchesT = re.findall(pattern, title)
    matchesD = re.findall(pattern, description)
    
    return matches
    return countT + countD,  bool(matchesT + matchesD)
