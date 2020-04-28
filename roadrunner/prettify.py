from bs4 import BeautifulSoup as bs
from extractors.regex_extractor import parse_file
import difflib
import re
from collections import Counter
import lxml.etree as et

# remove all attributes except some tags(only saving ['href','src'] attr)
def _remove_all_attrs_except_saving(soup):
    whitelist = []
    for tag in soup.find_all(True):
        if tag.name not in whitelist:
            tag.attrs = {}
        else:
            attrs = dict(tag.attrs)
            for attr in attrs:
                # if attr not in ['src', 'href']:
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


def ending_tag(tag):
    matcher = re.compile(r"</\w+\s*\S*>")
    return matcher.search(tag) is not None

def starting_tag(tag):
    matcher = re.compile(r"<\w+\s*\S*>")
    return matcher.search(tag) is not None


def check_tag(word):
    matcher = re.compile(r"</?\w+\s*\S*>")
    return True if matcher.search(word) is not None else False


def compare_base_of_tags(tag1, tag2, mode="both"):
    if mode == "both":
        return tag1.replace("/", "") == tag2.replace("/", "")
    elif mode == "end":
        return tag1 == re.sub(r"</?(w+)>", r"</\1>", tag2)
    elif mode == "start":
        return tag1 == re.sub(r"</?(w+)>", r"<\1>", tag2)
    elif mode == "terminal":
        return starting_tag(tag1) and ending_tag(tag2) and tag1 == tag2.replace("/", "")


def assess_next_lines(tag, page, index):
    counter = 1
    next_tag = page[index]
    potential_expressions = [page[index - 1]]
    while counter + index < len(page) and tag != next_tag:
        potential_expressions.append(next_tag)
        next_tag = page[index + counter]
        counter += 1
    potential_expressions.append(next_tag)
    return len(potential_expressions) > 1, counter if counter > 1 else 1, "({})?".format(
        " ".join(potential_expressions))


def find_closest_ending_tag(page, opening_tag, i):
    next_tag = page[i + 1]
    temp = i
    while i < len(page) and not compare_base_of_tags(opening_tag, next_tag, mode="end"):
        i += 1
        next_tag = page[i + 1]
    return i - 1 if i != temp else -1


def find_beginning_of_loop(page, tag, i):
    prev_tag = page[i - 1]
    temp = i
    while i > 0 and not compare_base_of_tags(tag, prev_tag, mode="start"):
        i -= 1
        prev_tag = page[i - 1]
    return i - 1 if i != temp else -5


def match_square(part, tag, i):
    closing_tag_id = find_closest_ending_tag(part, tag, i)
    beginning_tag_id = find_beginning_of_loop(part, tag, i)
    if closing_tag_id > 0 and beginning_tag_id > 0:
        internal_sample = part[i:closing_tag_id]
        internal_wrapper = part[beginning_tag_id:i]
        return internal_sample, internal_wrapper
    return None, None


def roadrunner(wrapper, sample, i, j, result):
    if i == len(wrapper) or j == len(sample):
        return result
    line_wrapper = wrapper[i]
    line_sample = sample[j]
    if line_sample == line_wrapper:
        result.append(line_wrapper)
        return roadrunner(wrapper, sample, i + 1, j + 1, result)
    elif not check_tag(line_wrapper) and not check_tag(line_sample):
        result.append("#text")
        return roadrunner(wrapper, sample, i + 1, j + 1, result)
    else:
        prev_wrapper_tag = wrapper[i - 1]
        prev_sample_tag = sample[j - 1]
        is_optional = False
        # loop detected in the wrapper
        if ending_tag(prev_wrapper_tag) and starting_tag(line_wrapper) and compare_base_of_tags(prev_wrapper_tag, line_wrapper):
            internal_sample, internal_wrapper = match_square(wrapper, line_wrapper, i)
            if internal_sample is not None:
                internal_result = roadrunner(internal_wrapper, internal_sample, 0, 0, [])
                if internal_result is not None:
                    result.extend(internal_result)
                    return roadrunner(wrapper, sample, i + 1, j, result)
                else:
                    is_optional = True
            else:
                is_optional = True
        elif ending_tag(prev_sample_tag) and starting_tag(line_sample) and compare_base_of_tags(prev_sample_tag, line_sample):
            internal_sample, internal_wrapper = match_square(sample, line_sample, j)
            if internal_sample is not None:
                internal_result = roadrunner(internal_wrapper, internal_sample, 0, 0, [])
                if internal_result is not None:
                    result.extend(internal_result)
                    return roadrunner(wrapper, sample, i, j + 1, result)
                else:
                    is_optional = True
            else:
                is_optional = True
        else:
            is_optional = True

        if is_optional:
            temp = sample[j - 5: j + 5]
            temp1 = wrapper[i - 5: i + 5]
            found_wrap, counter_wrap, res_wrap = assess_next_lines(sample[j], wrapper, i)
            found_samp, counter_samp, res_samp = assess_next_lines(wrapper[i], sample, j)
            if counter_samp < counter_wrap:
                result.append(res_samp)
                return roadrunner(wrapper, sample, i + counter_samp, j + 1, result)
            else:
                result.append(res_wrap)
                return roadrunner(wrapper, sample, i + 1, j + counter_wrap, result)


def run(wrapper, sample):
    wrapper = prettify(wrapper)
    # print(wrapper)
    sample = prettify(sample)
    res = "".join(roadrunner(wrapper, sample, 0, 0, []))
    soup = bs(res, features="lxml")  # make BeautifulSoup
    prettyHTML = soup.prettify()
    with open("res.html", "w") as file:
        file.write(prettyHTML)
