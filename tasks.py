import re
import time
import requests
import logging
from pathlib import Path
from robocorp import vault
from robocorp import excel
from robocorp import storage
from datetime import datetime
from robocorp.tasks import task
from datetime import datetime, timedelta
from robocorp.tasks import get_output_dir
from RPA.Browser.Selenium import Selenium 

logger = logging.getLogger(__name__)


#@task
#oppening the site aljazeera.com
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
    browser.open_available_browser(secrets["url"], 
                                        browser_selection="Chrome", 
                                        options=options)
    return browser

#searching for the phrase of the news
# @task
def search_the_phrase(browser, phrase):

    logger.info(f"Searching the phrase: {phrase}")
    # if the site contains collecting cookies 
    try:
        browser.click_button('Allow all')

    except:
        pass
    
    # finding the serach icon and field
    locator1 = "//button[@aria-pressed='false']//*[name()='svg']"
    browser.wait_until_page_contains_element(locator1, timeout=10)
    browser.click_element(locator1)
    # inserting the search phrase in the input field
    browser.input_text("//input[@placeholder='Search']",phrase)
    browser.click_button("//button[@aria-label='Search Al Jazeera']")

    # Trying to find it there is a realated articles with the search phrase
    try:
        locator2 = "//select[@id='search-sort-option']"
        browser.wait_until_element_is_visible(locator2, timeout=10)
        browser.click_element(locator2)
    except:
        return "No news associated with the search phrase"

    # sort by time
    dropdown_locator = "//select[@id='search-sort-option']/option[1]" 
    browser.click_element(dropdown_locator)


def retrive_data(browser, num_months_ago, search_phrase):

    logger.info(f"Retrieving data from {num_months_ago} months ago.")

    # Declearing varibale to return the date
    data =[]
    counter = 1
    # Handling the possible inputs
    if num_months_ago == 0:
        num_months_ago =1
    # To compare the date
    current_date = datetime.now()
    target_date = current_date - timedelta(days=num_months_ago * 30)  # Assuming each month has 30 days)

    # to store articles for extraction
    articles_titiles = []

    browser.wait_until_element_is_visible("xpath://*[@id='main-content-area']/div[2]/div[2]", timeout=10)
    
    # to handle paggination
    is_there_ShowMore = True
    
    while is_there_ShowMore:
        
        # Search result section
        search_list_selector = browser.find_element("xpath=//*[@id='main-content-area']/div[2]/div[2]")
        articles = browser.find_elements("tag:article", parent=search_list_selector)
        # the show more button
        button_locator = browser.find_elements("tag:button", parent=search_list_selector)
        
        # for each articles 
        for article in articles:
            # getting excert section
            excert = browser.find_element("tag:p",parent=article)

            # getting time and description of the post from excert
            time_of_post, description  = extract_before_ellipsis(excert.text)
            article_date = formated_article_date(time_of_post)

            # check if the artices does contains date
            if(article_date == None):
                continue
            try:

                # checking the article date is in the time period of the input
                if is_within_time_frame(article_date, target_date):

                    title= browser.find_element("tag:h3", parent=article)
                    if title.text not in articles_titiles:
                        articles_titiles.append(title.text)
                        
                        # does the title or description contains money
                        # checking how many times the search keyword apears in title and description
                        no_of_search_phrase, contains = no_of_topic_and_money_amount(title.text, 
                                                                                      description, 
                                                                                      search_phrase)
                        # finding the imgae of each article
                        image = browser.find_element(locator="tag:img", parent=article)
                        image_url = image.get_attribute('src')

                        picture_name = image_url.split("/")[-1]  # Extracting picture name from URL
                        output_path = Path(get_output_dir()) / picture_name

                        data.append([counter,title.text, article_date, description, 
                                            picture_name, no_of_search_phrase, contains])
                        #update counter
                        counter+=1

            except Exception as e:
                print(e)
        # try to locate and close the ads section
        try:
            ads_locator = browser.find_element("xpath=//button[@aria-label='Close Ad']")
            browser.click_button(ads_locator) 

        except Exception as e:
            pass
        
        # Trying to find if there is more article
        try: 
            # Scroll the element into view the show more button
            browser.scroll_element_into_view(button_locator)
            browser.wait_until_element_is_enabled(button_locator, timeout=10)


            browser.click_button(button_locator)
            time.sleep(5)
            print("Botton Clicked")
    
        except Exception as e: 
            is_there_ShowMore = False
            pass

    return data

# saving to excel
# @task
def save_data_to_Excel(workbook, data, sheet_name):
    
    worksheet = workbook.worksheet(sheet_name)

    # if there is articles save it inside the worksheet
    try:
        for i in range(len(data)):
            row_to_append = [data[i]]
            worksheet.append_rows_to_worksheet(row_to_append, header=False)
        # Save the workbook
        # worksheet.save_workbook()
    except Exception as e:
        pass 
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

    # splitting it to search phrase and number of months
    search_phrase, number_of_months = content.split(',') 
        
    # Convert number_of_months to an integer
    number_of_months = int(number_of_months.strip())

    # Performing cleaning the phrase
    search_phrase = search_phrase.strip()
    
    # Create an output work item with this data as the payload
    # workitems.outputs.create(payload={"search_phrase": search_phrase, 
    #                                         "number_of_months": number_of_months})
    
    # Sending search phrase to the search method
    search_the_phrase(browser_instance, search_phrase)

    # Processing data
    data_retrieved =  retrive_data(browser_instance, number_of_months, search_phrase)

    # Saving Data
    save_data_to_Excel(workbook, data_retrieved, sheet_name)
    workbook.save(excel_file_path)

    # Saving the workbook
    workbook.save(excel_file_path)
    
    # Close the browser
    browser_instance.close_all_browsers()


# getting the date and description from the excert of the article
def extract_before_ellipsis(text):
    
    # checking if the text contains the excert
    if len(text) <=0:
        return 

    # Split the text at '...'
    date_part = ""
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

# formating the article's date
def formated_article_date(date_extracted):

    # cleaning the date part
    date_extracted = date_extracted.strip()

    # Defining possible hours, minutes and seconds 
    possible_hms = ["second", "seconds","min\xadutes", 
                        "minute", "minutes", "hour","hours"]

    possible_days = ["day", "days"]

    possible_months_format_One =["January", "Feburary", "March", "April", 
                                    "May", "June", "July", "August", "September", 
                                    "October", "November", "December"]

    possible_months_format_Two =["Jan", "Feb", "Mar", "Apr",
                                    "May", "Jun", "Jul", "Aug", 
                                    "Sep", "Oct", "Nov", "Dec"]
   
    current_date = datetime.now()
   
    # Formatting the date to make it more easy to compare and returning the article times
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

# comparing if the article time is with in the date of given period of time
def is_within_time_frame(article_date, target_date):

    # Convert article date string to a datetime object
    try:
        article_datetime = datetime.strptime(article_date, "%Y%m%d")
    except Exception as e:
        return e, False
    
    # Check if the article date is within the time frame (since the target date)
    return article_datetime  >= target_date

# checking if the topics and description contains money 
# and how many times the title and description contains the search phrase
def no_of_topic_and_money_amount(title, description, search_phrase):

    # Trying to find the number of times the title and description contains
    countT = title.split(" ").count(search_phrase)
    countD = description.split(" ").count(search_phrase)

    # Regex pattern to match various money formats
    pattern = r"\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\d+\s(?:dollars|USD)"
    
    # Find all matches in the text
    matchesT = re.findall(pattern, title)
    matchesD = re.findall(pattern, description)

    # returning the number of times money appears and if there is search phrase in both
    return countT + countD,  bool(matchesT + matchesD)
