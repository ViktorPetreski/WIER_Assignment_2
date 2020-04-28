from extractors import regex_extractor, xpath_extractor
from roadrunner import utils

if __name__ == '__main__':
    # regex_extractor.extract_contents("./WebPages/overstock.com/jewelry01.html")
    # regex_extractor.extract_contents("./WebPages/overstock.com/jewelry02.html")
    # xpath_extractor.extract_content("./WebPages/overstock.com/jewelry01.html")
    utils.run("./WebPages/overstock.com/jewelry01.html", "./WebPages/overstock.com/jewelry02.html")
