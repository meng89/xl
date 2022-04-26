#!/usr/bin/env python3

import unittest
import xl


_xml1_text = \
    """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html 
  PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
                        <title>Virtual Library</title>   
        <sf></sf>
    </head>
    <body>
        <p>Moved to <a href="http://example.org/">example.org</a>.</p>
        
           <span />
    </body>
                        
</html>
"""


def _xml2_fun():
    html = xl.E("html")
    _head = xl.sub(html, "head", kids=[xl.Element("title", kids=["Virtual Library"])])
    body = xl.sub(html, "body")
    p = xl.sub(body, "p")
    p.kids.append("Moved to ")
    a = xl.sub(p, "a", attrs={"href": "http://example.org/"})
    a.kids.append("example.org")
    p.kids.append(".")
    _span = xl.sub(body, "span")

    prolog = xl.Prolog(version="1.0", encoding="UTF-8")

    doctype = xl.DocType("""html 
  PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd""")

    xml = xl.Xl(prolog=prolog, doctype=doctype, root=html)




class MyTestCase(unittest.TestCase):
    def test_something(self):
        html = xl.sub()
        self.assertEqual(True, False)  # add assertion here



if __name__ == '__main__':
    xml = xl.parse(_xml_text1, do_strip=True)
    xml2 = xl.parse(xml.to_str())
    print(xml2.to_str(do_pretty=True, dont_do_tags=["title"]))

    # unittest.main()
