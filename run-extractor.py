from extractors import regex_extractor, xpath_extractor
from roadrunner.utils import *

if __name__ == '__main__':
    # regex_extractor.extract_contents("./WebPages/overstock.com/jewelry01.html")
    # regex_extractor.extract_contents("./WebPages/overstock.com/jewelry02.html")
    # xpath_extractor.extract_content("./WebPages/overstock.com/jewelry01.html")
    # prettify.run("./WebPages/overstock.com/jewelry01.html", "./WebPages/overstock.com/jewelry02.html")
    regex_extractor.extract_contents_rtvslo(
        "./WebPages/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html")
