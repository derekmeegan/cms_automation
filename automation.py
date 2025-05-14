import os
import sys
import asyncio
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from browser_use import Agent, Controller
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext
from browser_use.agent.views import ActionResult

load_dotenv()

# --- Browser and Controller Setup ---
browser = Browser(
    config=BrowserConfig(
        headless=False, # Keep headless=False for debugging visibility
    )
)
controller = Controller()

class ElementActionParams(BaseModel):
    index: Optional[int] = Field(default=None, description="Index of the element from the agent's observation")
    selector: Optional[str] = Field(default=None, description="CSS selector for the target element")
    xpath: Optional[str] = Field(default=None, description="XPath selector for the target element")
    description: Optional[str] = Field(default=None, description="Optional description of the element for logging/clarity")

# --- Cleaned-up Custom Click Action using only Playwright Locator ---
@controller.registry.action(
    'Click Element',
    param_model=ElementActionParams,
)
async def click_element(params: ElementActionParams, browser: BrowserContext):
    """
    Clicks the element specified by its CSS selector or XPath using Playwright's
    locator() method. Temporarily highlights the element before clicking.
    """
    print("DEBUG: --- ENTERING click_element function ---")
    sys.stdout.flush()

    locator = None # Playwright Locator object
    location_method = ""
    element_description = params.description or ""

    try:
        # Get the underlying Playwright Page object
        print("DEBUG: Attempting to get current page...")
        sys.stdout.flush()
        page = await browser.get_current_page()
        print(f"DEBUG: Got page object: {type(page)}")
        sys.stdout.flush()

        # --- Locate Element using Playwright Locator (XPath or CSS) ---
        if params.xpath:
            location_method = f"XPath '{params.xpath}'"
            element_description = params.description or location_method
            print(f"DEBUG: Locating element using Playwright page.locator with {location_method}")
            sys.stdout.flush()
            locator = page.locator(params.xpath)
        elif params.selector:
            location_method = f"CSS Selector '{params.selector}'"
            element_description = params.description or location_method
            print(f"DEBUG: Locating element using Playwright page.locator with {location_method}")
            sys.stdout.flush()
            locator = page.locator(params.selector)
        else:
            # No valid selector provided
            raise ValueError('Either a CSS selector or an XPath must be provided')

        # --- Perform Actions using Playwright Locator ---
        print(f"DEBUG: Attempting action on element: {element_description}")
        sys.stdout.flush()

        # Check if the locator resolved to at least one element before proceeding
        # locator.count() might be useful, or just let actions fail if not found.
        # Playwright actions have built-in waits, so an explicit check isn't always needed.

        # Click using Playwright Locator method (handles waiting)
        print(f"DEBUG: Performing click via locator...")
        sys.stdout.flush()
        # You can add timeout to the click if needed: await locator.click(timeout=5000) # 5 seconds
        await locator.click()
        print(f"DEBUG: Click via locator completed.")
        sys.stdout.flush()

        # Optional: Short pause AFTER click if the page needs time to react visually
        await asyncio.sleep(0.5)

        # --- Return Success ---
        return ActionResult(
            extracted_content=f'🖱️ Successfully clicked element: {element_description}',
            include_in_memory=False # Usually best not to clutter memory with simple clicks
        )

    except Exception as e:
        # --- Error Handling ---
        error_detail = str(e)
        # Try to get a more specific description if the locator is known
        loc_info = f" using {location_method}" if location_method else ""
        err_msg = f'❌ Failed click action on element{loc_info}: {error_detail}'
        print(err_msg)
        sys.stdout.flush()
        # Re-raise the exception so the agent framework knows the action failed
        raise Exception(err_msg)
    finally:
        # No ElementHandle cleanup needed when using Locator
        print("DEBUG: --- EXITING click_element function (finally block) ---")
        sys.stdout.flush()

async def main():
    current_location = "Philadelphia"
    today = datetime.now().strftime("%m-%d-%Y")

    assignment_field_activator_xpath = "//div[contains(@class, 'formElement') and contains(@class, 'fieldFormElement') and .//div[@id='Assignment']]"
    assignment_dropdown_option_xpath = "//li[contains(@class, 'mru-item') and .//div[contains(@class, 'code-text') and normalize-space()='(9996610)'] and .//div[contains(@class, 'secondary-text') and contains(., '96410')]]" 
    duration_field_activator_xpath = "//div[contains(@class, 'formElement') and contains(@class, 'fieldFormElement') and .//div[@id='BaseHours']]"
    location_field_activator_xpath = "//div[contains(@class, 'formElement') and contains(@class, 'fieldFormElement') and .//div[@id='Location']]"
    duration_keypad_8_xpath = "//div[@id='durationPicker']//td[contains(@class, 'duration-picker-gray-background') and normalize-space()='8']"
    duration_keypad_done_xpath = "//td[@id='durationAllowNegativeSaveButton']"
    location_search_input_selector = "#search-control-input"
    location_dropdown_option_xpath = "//li[.//div[contains(@class, 'code-text') and normalize-space()='(PA87)']]"
    submit_button_xpath = "//button[@id='submit-btn']"

    agent = Agent(
        task = f"""
Objective: Input my time into the CMS tracker for my work. Today's date is {today}.

Starting URL: https://{os.getenv('username')}:{os.getenv('password')}@cmsotg.gtus.com/Expert_PROD/ApplicationServices/OnTheGoTime

Instructions:
1.  Navigate to the starting URL. Authentication is handled by the URL. Wait for the main time entry page to load.
2.  Verify the displayed date is correct for today ({today}). If not, adjust it.
3.  **Activate the Client/Assignment field:** Use the 'Click Element' action, providing the specific XPath `{assignment_field_activator_xpath}` in the `xpath` parameter. Click this specific field container to reveal the search input.
4.  **Input Client/Assignment Search Text:** Wait for the search input field to appear. Use the standard 'Input Text' action to type '9996610' into the input field identified by the CSS selector `#search-control-input` and placeholder of "Client / Assignment" and click enter and wait 2 seconds.
5.  **Select Client/Assignment Option:** Wait for the dropdown list of results to appear. Use the 'Click Element' action, providing the specific XPath `{assignment_dropdown_option_xpath}` in the `xpath` parameter, and set the description to 'Click dropdown option with code (9996610)'.
6.  **Activate Duration field:** Use the 'Click Element' action, providing the specific XPath `{duration_field_activator_xpath}` in the `xpath` parameter. Click this specific field container to reveal the duration input.
7.  **Input Duration '8' via Keypad:** Inside the duration picker popup: first, use the 'Click Element' action with XPath `{duration_keypad_8_xpath}` to click the '8' button. Second, use the 'Click Element' action with XPath `{duration_keypad_done_xpath}` to click the 'Done' button.
8.  **Activate Location field:** Use the 'Click Element' action, providing the specific XPath `{location_field_activator_xpath}` in the `xpath` parameter. Click this specific field container to reveal the location input.
9.  **Input and Select Location:** First, use the standard 'Input Text' action to type '{current_location}' into the location search input field (verify selector '{location_search_input_selector}'). Second, wait for the dropdown list and use the 'Click Element' action with XPath `{location_dropdown_option_xpath}` to select the 'PA Philadelphia - Philadelphia (PA87)' option.
10. **Submit:** Click the submit button with the 'Click Element' action, providing the specific XPath `{submit_button_xpath}` in the `xpath` parameter.
""",
        llm=ChatOpenAI(model="gpt-4.1-mini"),
        controller=controller,
        browser=browser,
    )
    result = await agent.run()



if __name__ == "__main__":
    asyncio.run(main())
