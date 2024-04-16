import html
from robocorp.tasks import task
# from robocorp.workitems import WorkItems
from robocorp import browser, vault
from robocorp.tasks import get_output_dir

from RPA.Browser.Selenium import Selenium 

# from RPA.Excel.Files import Files as Excel
# import re

@task
def main():
    # Initialize work items and browser
    # work_items = WorkItems()
    browser = Selenium(auto_close = False)
    secrets =vault.get_secret('aljazeersite')
    # browser.configure(
    #    browser_engine="chromium", 
    #    screenshot="only-on-failure",
    #    headless= False,

    #    )
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
        # Example: browser.goto("https://www.aljazeera.com/")
    browser.open_available_browser(secrets['url'],maximized=True)
    try:
        browser.click_button('Allow all')

    except:
        pass
        # Perform search, navigate, and extract data
    # browser.click_element()
    # browser.wait_for_element("/html/body/div[1]/div/div[1]/div[1]/div/header/div[4]/div[2]/button/svg", timeout=10)
    # site-header__search-trigger
    locator1 = "//button[@aria-pressed='false']//*[name()='svg']"
    browser.wait_until_page_contains_element(locator1, timeout=10)
    browser.click_element(locator1)
    browser.input_text("//input[@placeholder='Search']",'Business',)
    browser.click_button("//button[@aria-label='Search Al Jazeera']")
    # browser.click_element("//select[@id='search-sort-option']")
    locator2 = "//select[@id='search-sort-option']"
    browser.wait_until_element_is_visible(locator2, timeout=10)
    browser.click_element(locator2)
    dropdown_locator = "//select[@id='search-sort-option']/option[1]" 
    browser.click_element(dropdown_locator)
    browser.wait_until_element_is_visible("xpath://*[@id='main-content-area']/div[2]/div[2]", timeout=10)
    # Search result section
    search_list_selector = browser.find_element("xpath=//*[@id='main-content-area']/div[2]/div[2]")
    # Use a relative XPath from the context of 'search_list_selector'
    articles = browser.find_elements("tag:article", parent=search_list_selector)
    # articles = search_list_selector.find_elements("xpath:.//[article")
    for article in articles:
        # 
        # Now 'article' is a single WebElement, which can be used as a parent
        title= browser.find_element("tag:h3", parent=article)
        # title = article.find_element(".//div[2]/div[1]/h3")
        excert = browser.find_element("tag:p",parent=article)
        time_of_post, description  = extract_before_ellipsis(excert.text)
        print("Title now")
        print(title.text) # This will print the text of the title within each article
        print( time_of_post)
        print(description)
        # Tes Â­la.."
        test_mes = "TesÂ­la.."
        t = test_mes.replace("t­","k")
        print(t.replace("Ã‚Â­"," "))

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
    
# /html/body/div[1]/div/div[3]/div/div/div/div/main/div[2]/div[2]
# //*[@id="main-content-area"]/div[2]/div[2]
# //*[@id="main-content-area"]/div[2]/div[2]





    
    # //*[@id="root"]/div/div[1]/div[1]/div/header/div[4]/div[2]/button/svg
    # <button type="button" class="no-styles-button" aria-pressed="false"><span class="screen-reader-text">Click here to search</span><svg class="icon icon--search icon--grey icon--24 " viewBox="0 0 20 20" version="1.1" aria-hidden="true"><title>search</title><path class="icon-main-color" d="M3.4 11.56a5.77 5.77 0 1 1 8.16 0 5.78 5.78 0 0 1-8.16 0zM20 18.82l-6.68-6.68a7.48 7.48 0 1 0-1.18 1.18L18.82 20 20 18.82z"></path></svg></button>
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
# def date_format(val):
#     possible_dates = {0:["seconds ago", "minutes ago","hours ago","days ago"]}

if __name__ == "__main__":
    main()
