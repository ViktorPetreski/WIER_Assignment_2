from bs4 import BeautifulSoup as bs
from extractors.regex_extractor import parse_file
import difflib
import re
from collections import Counter


# remove all attributes except some tags(only saving ['href','src'] attr)
def _remove_all_attrs_except_saving(soup):
    whitelist = ['a', 'img']
    for tag in soup.find_all(True):
        if tag.name not in whitelist:
            tag.attrs = {}
        else:
            attrs = dict(tag.attrs)
            for attr in attrs:
                if attr not in ['src', 'href']:
                    del tag.attrs[attr]
    return soup


def prettify(file_name):
    content = parse_file(file_name)
    soup = bs(content, features="lxml")  # make BeautifulSoup
    soup = _remove_all_attrs_except_saving(soup)
    [script.extract() for script in soup(["script", "style", "meta", "link", "map"])]
    pretty_html = soup.prettify().splitlines(1)  # prettify the html
    sentence = ''
    combined_sentences = []
    for line in pretty_html:
        if not check_tag(line):
            sentence = "{} {}".format(sentence, line.replace("\n", ""))
        else:
            if len(sentence) > 1:
                combined_sentences.append(sentence)
                sentence = ''
            combined_sentences.append(line)
    stripped_html = [re.sub(r"(src|href)\s*=\s*\"\S+\"", r"\1='#link'", line.strip()) for line in combined_sentences]
    return stripped_html

def check_tag(word):
    matcher = re.compile(r"</?\w+\s*\S*>")
    return True if matcher.search(word) is not None else False


def assess_next_lines(line, page, index):
    counter = 0
    potential_expressions = []
    result = []
    while counter < 10:
        if line != page[index + counter]:
            potential_expressions.append(page[index + counter])
            counter += 1
        else:
            for key, value in Counter(potential_expressions):
                if value > 1:
                    result.append("({})*".format(key))
                else:
                    result.append(key)
    return len(result) > 0, counter, result

def run(wrapper, sample):
    wrapper = prettify(wrapper)
    # print(wrapper)
    sample = prettify(sample)
    diffInstance = difflib.Differ()
    # diffList = list(diffInstance.compare(wrapper, sample))
    print("-" * 50)
    # for line in diffList:
    #     if line[0] == '-':
    #         print(line)
    i = j = 0
    line_wrapper = wrapper[i]
    line_sample = sample[j]
    result = []
    while line_wrapper != "</html>" or line_sample != "</html>":
        if line_sample == line_wrapper:
            result.append(line_wrapper)
        else:
            # TODO: add iterator checking first
            if check_tag(line_wrapper):
                found, counter, res = assess_next_lines(line_wrapper, sample, j)
                j += counter - 1
                if not found:
                    found, counter, res = assess_next_lines(line_sample, wrapper, i)
                    i += counter - 1
                if not found:
                    print("!" * 50, i, j)
                    print(check_tag(line_sample))
                result.extend(res)
            else:
                if check_tag(line_sample):
                    print("!" * 20, i, j)
                else:
                    result.append("#text")
        i += 1
        j += 1
