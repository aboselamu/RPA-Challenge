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
    browser.click_element("/html/body/div[1]/div/div[1]/div[1]/div/header/div[4]/div[2]/button/svg")
    
    # //*[@id="root"]/div/div[1]/div[1]/div/header/div[4]/div[2]/button/svg
    # <button type="button" class="no-styles-button" aria-pressed="false"><span class="screen-reader-text">Click here to search</span><svg class="icon icon--search icon--grey icon--24 " viewBox="0 0 20 20" version="1.1" aria-hidden="true"><title>search</title><path class="icon-main-color" d="M3.4 11.56a5.77 5.77 0 1 1 8.16 0 5.78 5.78 0 0 1-8.16 0zM20 18.82l-6.68-6.68a7.48 7.48 0 1 0-1.18 1.18L18.82 20 20 18.82z"></path></svg></button>
        # For each news item extracted, process and store data in Excel
        # Example row to append:
        # excel.append_row([title, date, description, picture_filename, count, contains_money])
        
    # Save and close the Excel workbook
    # excel.save("output/news_data.xlsx")
    # excel.close()
    
    # Close the browser
    browser.close()

if __name__ == "__main__":
    main()
