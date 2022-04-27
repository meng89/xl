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


def get_xml2():
    html = xl.E("html", {"xmlns": "http://www.w3.org/1999/xhtml", "xml:lang": "en", "lang": "en"})
    head = xl.sub(html, "head", kids=[xl.Element("title", kids=["Virtual Library"])])
    _sf = xl.sub(head, "sf")
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
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\"""")

    xml = xl.Xl(prolog=prolog, doctype=doctype, root=html)
    return xml


class MyTestCase(unittest.TestCase):
    def test_something(self):
        xml1 = xl.parse(_xml1_text, do_strip=True, dont_do_tags=["p"])
        xml2 = get_xml2()

        self.assertEqual(xml1.to_str(), xml2.to_str())  # add assertion here


if __name__ == '__main__':
    unittest.main()
