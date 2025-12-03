import nodriver
import time
import asyncio
import json
import re
import csv
import datetime

base_url = "https://indeed.com"

page_loading_state = "Page Loading State"
cloudflare_state = "Cloudflare State"
easy_search_state = "Easy Search State"
rich_search_state = "Rich Search State"
search_done_state = "Search Done State"

page_delay = 5
action_delay = 3
turnstile_delay = 10

COOKIE_FILE = ".session.dat"

def insert_data_to_csv(job_data):
    headers = ['jobTitle', 'companyName']
    with open('job_list.csv', 'a', newline='\n') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writerow(job_data)

def find_data_from_csv(job_detail) -> bool:
    with open('job_list.csv', mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if row != []:
                if job_detail['jobTitle'] == row[0] and job_detail['companyName'] == row[1]:
                    return True
    return False

def make_job_description(job_description, job_detail):
    date = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
    companyName = job_detail['companyName']
    jobTitle = job_detail['jobTitle']
    companyName = companyName.replace("/", "")
    jobTitle = jobTitle.replace("/", "")
    with open(f"./job_descriptions/{companyName}_{jobTitle}_{date}", "w+") as f:
        f.write(job_description)

async def load_cookies(browser):
    try:
        await browser.cookies.load(COOKIE_FILE)
        print("Cookies loaded.")
        return True
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Failed to load cookies: {e}")
    except FileNotFoundError:
        print("Cookie file does not exist.")

    return False


async def save_cookies(browser):
    try:
        await browser.cookies.save(COOKIE_FILE)
        print("Cookies saved.")
    except Exception as e:
        print(f"Failed to save cookies: {e}")

async def load_document(page):
    await page.evaluate(
        expression = """
            new Promise((resolve) => {
                if (document.readyState === 'complete') {
                    resolve();
                } else {
                    document.addEventListener('readystatechange', () => {
                        if (document.readyState === 'complete') {
                            resolve();
                        }
                    });
                }
            });
        """,
        await_promise = True
    )

async def handle_cloudflare_state(page):
    # wait for 10 second until turnstile appear
    print("Cloudflare loading...")
    await asyncio.sleep(turnstile_delay)

    # get turnstile component
    print("Getting cloudflare callenge box...")
    content = await page.select("div.main-content")

    # get turnstile location
    print("Calculating location...")
    location = await content.get_position()

    # click mouse
    print("Clicking check box...")
    await page.mouse_click(location.x + 25, location.y + 30)

async def handle_easy_search(page):
    print("Easy search is performing...")

    print("Typing keyword...")
    keyword_bar = await page.query_selector("input[name='q']")
    if keyword_bar:
        await keyword_bar.click()
        await keyword_bar.send_keys("ai ml engineer")
    
    await asyncio.sleep(action_delay)
    
    print("Typing location...")
    # click on location bar
    location_bar = await page.query_selector("input[name='l']")
    if location_bar:
        await location_bar.click()
        await location_bar.clear_input()
        await location_bar.send_keys("remote")
    
    await asyncio.sleep(action_delay)
    
    print("Clicking enter button...")
    # submit the search
    search_button = await page.query_selector("button[type='submit']")
    if search_button:
        await search_button.click()

async def handle_rich_search(page):
    print("Choosing remote option")
    remote_filter = await page.query_selector("button[id='remote_filter_button']")
    if remote_filter:
        await remote_filter.click()
    
    await asyncio.sleep(action_delay)

    # select remote option
    remote_option = await page.query_selector("a[aria-label='Remote']")
    if remote_option:
        await remote_option.click()

    # click on time filter
    print("Choosing time option")
    time_filter = await page.query_selector("button[id='fromAge_filter_button']")
    if time_filter:
        await time_filter.click()
    
    await asyncio.sleep(action_delay)

    time_option = await page.query_selector("a[aria-label='Last 24 hours']")
    if time_option:
        await time_option.click()

async def main():
    #start the browser
    browser = await nodriver.start()

    if not await load_cookies(browser):
        print("Logged in with cloudflare")
    else:
        print("Logged in with cookies.")

    #navigate to a page
    page = await browser.get(base_url)

    # maximize the browser
    await page.maximize()

    # event loop
    exit_state = False
    
    while not exit_state:
        # delay for page loading
        await asyncio.sleep(page_delay)

        # initiate state
        state = page_loading_state

        # check current state
        if await page.find_element_by_text("Additional Verification Required"):
            state = cloudflare_state
        
        if await page.find_element_by_text("Your next job starts here"):
            state = easy_search_state
        
        if await page.query_selector("button[id='remote_filter_button']") or await page.query_selector("button[id='fromAge_filter_button']"):
            state = rich_search_state
        
        if await page.query_selector("button[id='remote_option_remote']") and await page.query_selector("button[id='fromAge_option_fromAge']"):
            state = search_done_state
            
        await load_document(page)
        # event loop by state
        match state:
            
            case "Page Loading State":
                print("Page Loading State...")
                await asyncio.sleep(page_delay)

            case "Cloudflare State":
                await handle_cloudflare_state(page)
            
            case "Easy Search State":
                await save_cookies(browser)
                # click on the search bar to start easy search
                await handle_easy_search(page)
                
            case "Rich Search State":
                # click on remote filter
                await handle_rich_search(page)
                
            case "Search Done State":
                # get job list
                print("Search Done State")
                cards = await page.select_all("div[data-testid='slider_container']")
                for card in cards:
                    if not card.parent.attributes.__contains__("aria-hidden"):
                        link = await card.query_selector("a[data-jk]")
                        if link:
                            await link.click()
                        
                        await asyncio.sleep(page_delay)

                        job_title = await page.query_selector("h2[data-testid='jobsearch-JobInfoHeader-title']>span")
                        company_name = await page.query_selector("div[data-testid='inlineHeader-companyName']>span")
                        job_description_group = await page.query_selector("div[id='jobDescriptionText']")
                        job_description = job_description_group.text_all

                        job_detail = {
                           'jobTitle' : job_title.text,
                           'companyName' : company_name.text_all,
                        #    'url' : url,
                        }

                        print(job_detail)

                        if not find_data_from_csv(job_detail):
                           insert_data_to_csv(job_detail)
                           make_job_description(job_description, job_detail)
                
                await asyncio.sleep(action_delay)

                next_button = await page.query_selector("a[data-testid='pagination-page-next'")
                if next_button:
                    await next_button.click()
                else :
                    exit_state = True

if __name__ == '__main__':

    nodriver.loop().run_until_complete(main())