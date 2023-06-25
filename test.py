import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Open the file and read the content
with open('test.html', 'r') as f:
    html_content = f.read()

# Parse the HTML content with Beautiful Soup
soup = BeautifulSoup(html_content, 'html.parser')

# Find all 'a' elements with class 'b-text_copy-3'
elements = soup.find_all('a', {'class': 'b-text_copy-3'})

# Loop over each element
for element in elements:
    url = element['href']
    print("URL:", url)
    print("Text:", element.get_text())
    
    # Check if the href value is a valid URL
    parsed_url = urlparse(url)
    if bool(parsed_url.netloc) and bool(parsed_url.scheme):
        # Send a GET request to the URL
        response = requests.get(url)

        # Parse the HTML content of the page with Beautiful Soup
        page_soup = BeautifulSoup(response.content, 'html.parser')

        # Find the elements with the classes you're interested in and print their text content
        for class_name in ["b-d-none b-d-block@md property-full-name",
                           "hover-border b-d-none b-d-block@lg b-d-inline@xl b-mb1",
                           "hover-border b-d-none b-d-block@lg b-d-inline@xl"]:
            target_element = page_soup.find(class_=class_name)
            if target_element:
                print(f"Text of '{class_name}':", target_element.get_text())
            else:
                print(f"Element with class '{class_name}' not found")
    else:
        print("Invalid URL, skipping...")
    print("---" * 20)