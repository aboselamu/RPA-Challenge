# import html
import time
from datetime import datetime, timedelta
from datetime import datetime
from robocorp.tasks import task
# from robocorp.workitems import WorkItems
from robocorp import vault
from robocorp.tasks import get_output_dir

from RPA.Browser.Selenium import Selenium 

# from RPA.Excel.Files import Files as Excel
# import re

@task
def main():
    browser = Selenium()
    
    # Define Chrome options to disable popup blocking
    options = [
        "--disable-popup-blocking",
        "--ignore-certificate-errors"
    ]
    
    secrets =vault.get_secret('aljazeersite') 

    # Open browser with specified options
    browser.open_available_browser(secrets["url"], browser_selection="Chrome", options=options)

    # Initialize work items and browser
    # work_items = WorkItems()

    
    # browser = Selenium(auto_close = False)
    # Define browser options
    # options = {
    #     "args": [
    #         "--disable-popup-blocking",
    #         "--ignore-certificate-errors",
    #         "--start-maximized"
    #     ]
    # }

    # Open the browser with the specified options
    # browser.open_available_browser('https://example.com', options=options)

    
    # excel = Excel()
    
    # # Open the Excel file to store data
    # excel.create_workbook("news_data.xlsx")
    # excel.rename_worksheet("Sheet", "Data")
    # excel.append_row(["Title", "Date", "Description", "Picture Filename", "Count", "Contains Money"])
    
    # # Process each input work item
    # for item in work_items.inputs:
    #     search_phrase = item.payload["search_phrase"]
    #     news_category = item.payload["news_category"]
    #     number_of_months = item.payload["number_of_months"]
        
        # Implement web scraping logic here
    # browser.open_available_browser(secrets["url"])
    # browser.open_available_browser(secrets['url'],maximized=True)
    try:
        browser.click_button('Allow all')

    except:
        pass
        # Perform search, navigate, and extract data
    # site-header__search-trigger
    locator1 = "//button[@aria-pressed='false']//*[name()='svg']"
    browser.wait_until_page_contains_element(locator1, timeout=10)
    browser.click_element(locator1)
    browser.input_text("//input[@placeholder='Search']",'Business',)
    browser.click_button("//button[@aria-label='Search Al Jazeera']")
    # browser.click_element("//select[@id='search-sort-option']")
    try:
        locator2 = "//select[@id='search-sort-option']"
        browser.wait_until_element_is_visible(locator2, timeout=10)
        browser.click_element(locator2)
    except:
        print("No news associated with the search phrase")
        return
    dropdown_locator = "//select[@id='search-sort-option']/option[1]" 
    browser.click_element(dropdown_locator)
    # browser.wait_until_element_is_visible("xpath://*[@id='main-content-area']/div[2]/div[2]", timeout=10)
    # # Search result section
    # search_list_selector = browser.find_element("xpath=//*[@id='main-content-area']/div[2]/div[2]")
    # Use a relative XPath from the context of 'search_list_selector'
    # articles = browser.find_elements("xpath=//*[@id='main-content-area']/div[2]/div[2]/article[1]")
    
    num_months_ago = 2
    current_date = datetime.now()
    target_date = current_date - timedelta(days=num_months_ago * 30)  # Assuming each month has 30 days

    browser.wait_until_element_is_visible("xpath://*[@id='main-content-area']/div[2]/div[2]", timeout=10)
    search_list_selector = browser.find_element("xpath=//*[@id='main-content-area']/div[2]/div[2]")
    # print(len(search_list_selector))
    is_there_ShowMore = True
    while is_there_ShowMore:
        
        # Search result section
        
        articles = browser.find_elements("tag:article", parent=search_list_selector)
        button_locator = browser.find_elements("tag:button", parent=search_list_selector)
        
        # # articles = search_list_selector.find_elements("xpath:.//[article")
        # //*[@id="main-content-area"]/div[2]/div[2]/article[10]
        # //*[@id="main-content-area"]/div[2]/div[2]/button
        # //button[@class='show-more-button grid-full-width']
        # button = browser.find_element("xpath=//span[@aria-hidden='true'][normalize-space()='Show more']")
        for article in articles:
            # getting information 
            excert = browser.find_element("tag:p",parent=article)
            time_of_post, description  = extract_before_ellipsis(excert.text)
            article_date = formated_article_date(time_of_post)
            print(article_date, target_date,)
            if is_within_time_frame(article_date, target_date):
                # Now 'article' is a single WebElement, which can be used as a parent
                title= browser.find_element("tag:h3", parent=article)
                print("Title now")
                print(title.text) # This will print the text of the title within each article
                print( time_of_post, article_date)
                print(description)
                print("ONe article ends here")
        time.sleep(5)
        try:
            ads_locator = browser.find_element("xpath=//button[@aria-label='Close Ad']")
            browser.click_button(ads_locator) 
        except Exception as e:
            print(e,"My massege> NO Adds Found")
        try: 
        
        #  button = browser.find_element("tag:button", parent=search_list_selector)
            # Scroll the element into view
            browser.scroll_element_into_view(button_locator)
            browser.wait_until_element_is_enabled(button_locator, timeout=10)

            browser.click_button(button_locator)
            time.sleep(20)
            print("Botton Clicked")
    
        except Exception as e: 
            print(e, "Error")
            is_there_ShowMore = False

        # print(type("Â"), test_mes[3:5], test_mes[4],len(test_mes))
    # titles_xpath = "//*[@id='main-content-area']/div[2]/div[2]/article/div[2]/div[1]/h3"
    
    # titles = browser.find_elements(titles_xpath)    
    # for title in  titles:
    #     # Decode HTML entities in the title text
    #     decoded_title = html.unescape(title.text)
    #     # Further clean the title text if necessary
    #     clean_title = decoded_title.replace("&shy;", "")
    #     print("KOMan " + clean_title)
        
    print(str(len(articles))+ " > This is Selamu's output")
        # For each news item extracted, process and store data in Excel
        # Example row to append:
        # excel.append_row([title, date, description, picture_filename, count, contains_money])
        
    # Save and close the Excel workbook
    # excel.save("output/news_data.xlsx")
    # excel.close()
    
    # Close the browser
    browser.close_all_browsers()



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
    current_date = datetime.now()
    try:   
        if(date_extracted.split(" ")[1]) in possible_hms:
            date_object = current_date
        elif date_extracted.split(" ")[1] in possible_days:
            # Split the expression to extract the number of days
            num_days = int(date_extracted.split()[0])
            # Calculate the target date by subtracting the number of days from the current date
            date_object = current_date - timedelta(days=num_days)
        else:
            # Convert the date string to a datetime object
            date_object = datetime.strptime(date_extracted, "%B %d, %Y")
            # Format the datetime object to the desired format
    except Exception as e:
        return  
    formatted_date = date_object.strftime("%Y%m%d")

    return formatted_date

def is_within_time_frame(article_date, target_date):
    # Convert article date string to a datetime object
    article_datetime = datetime.strptime(article_date, "%Y%m%d")
    # Check if the article date is within the time frame (since the target date)
    return article_datetime  >= target_date



# def get_previous_month_date(date_string, num_months):
#     # Convert the date string to a datetime object
#     date_object = datetime.strptime(date_string, "%Y%m%d")
    
#     # Calculate the number of days to subtract based on the number of months
#     days_to_subtract = num_months * 30
    
#     # Subtract the timedelta to get the previous month's date
#     previous_month_date = date_object - timedelta(days=days_to_subtract)
    
#     return previous_month_date


if __name__ == "__main__":
    main()
