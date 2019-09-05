from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time

def get_data():    

    urls = [
            'https://www.linkedin.com/jobs/search?keywords=Data%20Science&location=S%C3%A3o%20Paulo%20e%20Regi%C3%A3o&trk=guest_job_search_jobs-search-bar_search-submit&redirect=false&position=1&pageNum=0'
            ]

    list_ids = []
    list_company = []
    list_title = []
    list_date = []
    list_location = []
    
    for url in urls:       
        
        url_parsed = url
        
        url_parsed = url_parsed.format('0', '1', '0')
       
        print('--->')
        print(url_parsed)
        
        # LOCAL
        path_to_chromedriver = 'your_path_to/chromedriver.exe'  # change path as needed                
        chromeOptions = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images":2}
        chromeOptions.add_experimental_option("prefs",prefs)
        chromeOptions.add_argument('--disable-logging')
        chromeOptions.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(executable_path = path_to_chromedriver, chrome_options=chromeOptions)                    
        
        driver.get(url_parsed)
        
        keep_clicking = True
        counter = 0
        while keep_clicking == True:
            time.sleep(5)
            try:
                driver.find_element_by_css_selector('button.see-more-jobs').click()
            except WebDriverException:
                pass
            
            except NoSuchElementException:
                keep_clicking = False
                
            counter = counter + 1
            
            # !IMPORTANTE -> Limita o número de cliques que serão dados
            # no botão de Ver mais Jobs.
            if counter >= 50:
                keep_clicking = False
        
        try:
            html = driver.page_source
            driver.close()
            driver.quit()
        except WebDriverException:
            continue
        
        soup = BeautifulSoup(html, "html5lib")

        section_to_select = 'li'
        class_of_section = 'result-card'
        
        list_jobs = soup.findAll(section_to_select,attrs={"class": class_of_section})   
        
        if list_jobs == None:
            section_to_select = 'li'
            class_of_section = 'jobs-search-result-item'
            
            list_jobs = soup.findAll(section_to_select,attrs={"class": class_of_section})        

        for job in list_jobs:
            data_id = job.get('data-id')
            
            if data_id in list_ids:
                continue

            print(job.h4.text)
            
            try:
                company = job.h4.text
                title = job.h3.text
                date = job.time.get('datetime')                
                location = job.find("span", class_="job-result-card__location").text

                list_ids.append(data_id)
                list_company.append(company)
                list_title.append(title)
                list_date.append(date)
                list_location.append(location)

            except AttributeError:
                pass

    df = pd.DataFrame({'id': list_ids, 'company': list_company, 'title': list_title, 'date': list_date, 'location': list_location})

    return df

def main():
    
    df = get_data()
    df.to_csv('my-scraped-jobs.csv', index=False)

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)
    
if __name__ == '__main__':
    main()