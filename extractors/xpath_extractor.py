from lxml import html
import json, re
from .regex_extractor import parse_file


def extract_content(file_name):
    tree = html.fromstring(parse_file(file_name))
    titles = tree.xpath('//table[2]/tbody/tr/td[5]//td[2]/a/b/text()')
    contents = tree.xpath('//table[2]/tbody/tr/td[5]//td[2]/span[@class="normal"]/text()')
    prices = tree.xpath('//s/text() | //span[@class="bigred"]/b/text() |  //span[@class="littleorange"]/text()')
    c = 0
    prices_tuples = []
    while c < len(prices):
        savings = prices[c + 2]
        split_savings_matcher = re.compile(r"([$€]\s*[0-9.,]+)\s*(\([0-9.,]+%\))")
        savings = split_savings_matcher.search(savings)
        prices_tuples.append((prices[c], prices[c+1], savings.group(1), savings.group(2)))
        c += 3
    product = zip(titles, contents, prices_tuples)
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
    print(json.dumps(results, indent=4))
