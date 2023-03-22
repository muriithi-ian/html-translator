import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from googletrans import Translator
from tqdm import tqdm
import time


translator = Translator(service_urls=['translate.google.com'])

# Function to recursively get all HTML files in a directory
def get_html_files(directory):
    html_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

# Function to translate a text string from English to Hindi
def translate_text(text):
    # Split the text into chunks of at most 5000 characters (googletrans API limit)
    chunks = [text[i:i+5000] for i in range(0, len(text), 5000)]
    # Translate each chunk to Hindi
    if chunks:
        try:
            translated_chunks = [translator.translate(
                chunk, dest='hi', src='en').text for chunk in chunks]
        except Exception as e:
            print(f"Translation failed with error: {e}")
            translated_chunks = [chunk for chunk in chunks]
    else:
        translated_chunks = []

    # Join the translated chunks back into a single string
    translated_text = ''.join(translated_chunks)
    # Return the translated text
    return translated_text

# Function to modify the HTML file
def modify_html_file(file):
    with open(file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    # Get the body tag
    body_tag = soup.body
    # Get all tags under the body tag
    tags = body_tag.find_all()
    for tag in tags:
        if tag.name not in ['script', 'style']:
            # translate text to new text
            if tag.string:
                try:
                    translated_text = translate_text(tag.string)
                except Exception as e:
                    print(f"Translation failed with error: {e}")
                    translated_text = tag.string
                tag.string.replace_with(translated_text)

    with open(file, 'w', encoding='utf-8') as f:
        f.write(str(soup))


# Main function to call other functions
def main(directory):
    # Directory containing HTML files
    # Get all HTML files in directory
    html_files = get_html_files(directory)
    # Process each HTML file using a thread pool with progress bar
    with ThreadPoolExecutor(max_workers=4) as executor, tqdm(total=len(html_files)) as progress:
        futures = [executor.submit(modify_html_file, file) for file in html_files]
        for future in as_completed(futures):
            try:
                result = future.result()
            except Exception as exc:
                print(f"Error occurred: {exc}")
                result = None
            if result:
                progress.update(1)
    print("Translation attempt complete. Check the HTML files for errors.")


if __name__ == '__main__':
    start_time = time.time()
    main('/home/saint/del/www.classcentral.com')
    end_time = time.time()

    print(f"Total time: {end_time - start_time} seconds")
