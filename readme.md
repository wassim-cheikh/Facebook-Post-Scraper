# Facebook Post Scraping Bot

## Overview

The Facebook Posts Scraping Bot is a Python script written in python 3.11.4, designed for scraping posts from Facebook pages and groups based on specified keywords. The script utilizes the SeleniumBase library to automate the process. The scraped data is saved in JSON format, and two files are generated after each successful execution: one in the data folder containing the scraped posts data, and the other in the traces folder containing the execution trace.

## Dependencies

- **SeleniumBase**: 4.20.3
- Make sure to install the necessary dependencies using the provided `requirements.txt` file: pip install -r requirements.txt

## Configuration

The configuration file `constants.py` is used to set the necessary parameters for the script. Here are the key parameters:

- **email**: Facebook email for authentication.
- **password**: Facebook password for authentication.
- **urls**: List of URLs for Facebook pages and groups to be scraped.
- **posts_number**: Number of posts to be treated during each execution.
- **scrolling_timeout**: The maximum time for gathering posts or exceeding when reaching the specified post number.
- **catch**: List of keywords. Posts containing any of these words will be saved separately after execution.
- **ignore**: List of keywords. Posts containing any of these words will be saved separately after execution.
- **comments_number**: Number of comments to be scraped for each post.
- **headless**: If set to True, the automated browser runs in headless mode (no UI).
- **check_trace**: If set to True, the script looks for previous traces of the page or group and eliminates treated posts from the current execution.
- **use_same_words**: If `check_trace` is True, eliminates treated posts only if the keywords used are the same for the current execution.

## Functioning

The script will iterate over the specified Facebook URLs, scrape posts, classify them based on keywords, and save the results in the data and traces folders.

## Output

- **Data Files**: Saved in the `data` folder, these files contain the following information for each scraped post:
- Author
- URL
- Date
- Content
- Number of Reactions
- Number of Comments
- Reactions
- Comments

- **Traces Files**: Saved in the `traces` folder, these files provide information about each execution:
- Date and Time
- Pages or Groups URLs
- Treated Posts
- Keywords Used in the Execution


