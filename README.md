# CMS Time Entry Automation

This Python script automates the process of entering work hours into the CMS tracker web application. It leverages Playwright-based browser automation and a custom agent framework to interact with the time entry form, filling out all required fields and submitting the entry for a given date.

## What the Script Does

- **Automated Time Entry:**  
  The script opens the CMS OnTheGoTime web application, authenticates using credentials from environment variables, and navigates to the time entry page.

- **Field Interactions:**  
  It programmatically:
  1. Verifies and sets the correct date for the entry.
  2. Activates the Client/Assignment field and searches for a specific assignment code.
  3. Selects the correct assignment from the dropdown.
  4. Activates and fills in the Duration field using a keypad interface.
  5. Activates the Location field, searches for the specified location, and selects it from the dropdown.
  6. Clicks the submit button to finalize the entry.

- **Custom Actions:**  
  The script uses a custom "Click Element" action that interacts with page elements via XPath or CSS selectors, with debugging output for transparency.

- **Configuration:**  
  - Credentials (`username`, `password`) are loaded from a `.env` file.
  - The script is designed for debugging (browser runs in non-headless mode).
  - The automation steps and selectors are clearly defined and can be adjusted as needed.

## How to Use

1. **Install Dependencies:**  
   Ensure all required packages in `requirements.txt` are installed.

2. **Set Up Environment Variables:**  
   Create a `.env` file in the project directory with your CMS credentials:
   ```
   username=YOUR_USERNAME
   password=YOUR_PASSWORD
   ```

3. **Run the Script:**  
   Execute the script:
   ```
   python automation.py
   ```

   The browser will open and the automation will proceed to fill and submit the time entry form for the specified date.
