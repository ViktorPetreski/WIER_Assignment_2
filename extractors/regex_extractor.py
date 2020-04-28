import re
import json


def parse_file(file_name, encoding_type="iso-8859-1"):
    with open(file_name, "r", encoding=encoding_type) as file:
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


def extract_contents_rtvslo(file_name):
    content = parse_file(file_name, "utf-8")

    author_time_regex = re.compile(
        r"<div class=\"author-name\">(.*?)<\/div>\s*<\/div>\s*<div class=\"publish-meta\">\s*(.*?)\s*<br>",
        re.MULTILINE | re.DOTALL)
    author_time = re.findall(author_time_regex, content)
    author = author_time[0][0]
    published_time = author_time[0][1]

    title_regex = re.compile(r"<h1>(.*?)<\/h1>\s*<div class=\"subtitle\">", re.MULTILINE | re.DOTALL)
    title = re.findall(title_regex, content)

    subtitle_regex = re.compile(r"<div class=\"subtitle\">(.*?)<\/div>", re.MULTILINE | re.DOTALL)
    subtitle = re.findall(subtitle_regex, content)

    lead_regex = re.compile(r"<p class=\"lead\">(.*?)\s*<\/p>", re.MULTILINE | re.DOTALL)
    lead = re.findall(lead_regex, content)

    content_regex = re.compile(
        r"<figcaption itemprop=\"caption description\">\s*<span class=\"icon-photo\"><\/span>(.*?)\s*<\/figcaption>.*?\s*<p class=\"Body\"><\/p><p class=\"Body\">(.*?)\s*<p><\/p>\s*<div",
        re.MULTILINE | re.DOTALL)

    content_lst = re.findall(content_regex, content)
    img_caption = content_lst[0][0]

    content_lst_2 = re.sub(r"<br>|</?strong>", "\n", content_lst[0][1])
    content_final = re.sub(r"</?\w+.*?>", "", content_lst_2)

    # print(content_lst[0][0])
    # print(author, published_time, title, subtitle, lead)
    # print(content_final)

    final_dict = {
        "Author": author,
        "PublishedTime": published_time,
        "Title": title[0],
        "SubTitle": subtitle[0],
        "Lead": lead[0],
        "Content": "\n".join([img_caption, content_final])
    }

    for key, val in final_dict.items():
        print(key, ":", val)

    # print(json.dumps(final_dict, indent=4, ensure_ascii=False))

