import re
import json


def parse_file(file_name):
    with open(file_name, "r", encoding="iso-8859-1") as file:
        content = file.read()

    return content


def extract_contents(file_name):
    content = parse_file(file_name)

    title_extractor = re.compile(
        r"<td\s*valign=\"top\">\s*<a href=\"http://www\.overstock\.com/cgi-bin/d2\.cgi\?PAGE=PROFRAME&amp;PROD_ID=\d+\"><b>(\d{,2}-[K|k][T|t]\.?\s*(?:\S*\s*){,6}\(?\d*\.?\d*\s\S*\)?)</b></a>",
        re.MULTILINE | re.DOTALL)
    # the_tr = title_extractor.search(content)
    titles = re.findall(title_extractor, content)
    price_extractor = re.compile(r"nowrap=\"nowrap\">(?:\S*\s*){,2}([$€]\s*[0-9.,]+)\s*(\(\d{,2}%\))?")
    prices = price_extractor.findall(content)
    content_extractor = re.compile(r"valign=\"top\"><span\s*class=\"\w+\">(.*?)<br>", re.DOTALL | re.MULTILINE)
    contents = content_extractor.findall(content)

    prices_list = []
    c = 0
    while c < len(prices):
        prices_list.append((prices[c][0], prices[c + 1][0], prices[c + 2][0], prices[c + 2][1]))
        c += 3
    product = zip(titles, contents, prices_list)
    results = []
    for title, content, price in product:
        prod_dict = {
            "title": title,
            "content": content.replace("\n", " "),
            "list_price": price[0],
            "price": price[1],
            "saving": price[2],
            "saving_percent": price[3]
        }
        results.append(prod_dict)
    print(len(results))
    print(json.dumps(results, indent=4))
