#!/usr/bin/env python3

import unittest
import xl


_xml1_text = \
    """<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="http://www.docbook.org/xml/5.0/rng/docbook.rng"?>
<?xml-model href="http://www.docbook.org/xml/5.0/xsd/docbook.xsd"?>
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
    prolog = xl.Prolog(version="1.0", encoding="UTF-8")

    doctype = xl.DocType("""html 
  PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\"""")

    html = xl.Element("html", {"xmlns": "http://www.w3.org/1999/xhtml", "xml:lang": "en", "lang": "en"})
    head = xl.sub(html, "head", kids=[xl.Element("title", kids=["Virtual Library"])])
    _sf = xl.sub(head, "sf")
    body = xl.sub(html, "body")
    p = xl.sub(body, "p")
    p.kids.append("Moved to ")
    a = xl.sub(p, "a", attrs={"href": "http://example.org/"})
    a.kids.append("example.org")
    p.kids.append(".")
    _span = xl.sub(body, "span")

    xml = xl.Xml(prolog=prolog, doctype=doctype, root=html)
    xml.other_qmelements.append(xl.QMElement("xml-model", {"href": "http://www.docbook.org/xml/5.0/rng/docbook.rng"}))
    xml.other_qmelements.append(xl.QMElement("xml-model", {"href": "http://www.docbook.org/xml/5.0/xsd/docbook.xsd"}))
    return xml


class MyTestCase(unittest.TestCase):
    def test_something(self):
        xml1 = xl.parse(_xml1_text, do_strip=True, dont_do_tags=["p"])
        xml2 = get_xml2()
        print("####")
        print(xml1.to_str(do_pretty=False, dont_do_tags=["p"]))
        print("####")
        print(xml2.to_str(do_pretty=False, dont_do_tags=["p"]))
        print("####")
        self.assertEqual(xml1.to_str(), xml2.to_str())  # add assertion here


if __name__ == '__main__':
    unittest.main()
