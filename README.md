# coding_socrates_web_scraping

# m3 coffee.py - Coffee Data Analysis

This Python script (`m3 coffee.py`) scrapes coffee product data from a website (website URL not provided), stores it in a MongoDB database, and then generates visualizations to analyze the collected data.

## Functionality:

The script performs the following tasks:

1. **Data Collection:**
   - **URL Gathering:** 
      - Iterates through 6 paginated pages of a website.
      - Extracts individual product URLs from each page and appends them to the `all_links` list.
   - **Product Data Scraping:**
      - For each URL in `all_links`, visits the product page and extracts relevant data fields.

2. **Data Storage:**
   - **MongoDB Integration:** Inserts the scraped product data into the `coffee_source_m3` collection in a MongoDB database.

3. **Data Visualization:**
   - **Top 10 Coffee Producing Countries:** Generates a histogram visualizing the top 10 countries based on the number of coffee products sourced from them.
   - **Price Distribution by Region:** Creates a graph (type not specified) illustrating the distribution of coffee prices across different geographical regions.

## Requirements:

- Python 3
- Libraries:
    - Requests (for making HTTP requests to the website)
    - BeautifulSoup (for parsing HTML content)
    - Pymongo (for interacting with MongoDB)
    - Matplotlib or Seaborn (for data visualization)

## How to Run:

1. **Configure MongoDB Connection:** Update the script with your MongoDB connection details.
2. **Execute the Script:** `python m3 coffee.py`

## Output:

- The script will populate the `coffee_source_m3` collection in your MongoDB database with the scraped coffee product data.
- Two visualizations will be generated:
    - A histogram showing the top 10 coffee-producing countries.
    - A graph displaying the price distribution of coffee by region.
