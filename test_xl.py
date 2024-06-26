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
        <p>Moved to <a href="http://example.org/">example.org</a>.<!--这是xml注释--></p>
        
           <span/>
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
    # p.kids.append(xl.Comment("这是xml注释"))
    _span = xl.sub(body, "span")

    xml = xl.Xml(prolog=prolog, doctype=doctype, root=html)
    xml.kids.insert(1, xl.QMElement("xml-model", {"href": "http://www.docbook.org/xml/5.0/rng/docbook.rng"}))
    xml.kids.insert(2, xl.QMElement("xml-model", {"href": "http://www.docbook.org/xml/5.0/xsd/docbook.xsd"}))
    return xml


class MyTestCase(unittest.TestCase):
    def test_something(self):
        xml1 = xl.parse(_xml1_text, do_strip=True, dont_do_tags=["p"])
        xml2 = get_xml2()
        print()
        print("########/BEGING")
        print("########/xml1:")
        xml1_str = xml1.to_str(do_pretty=True, dont_do_tags=["p"])
        print(xml1_str)
        print("########/xml2:")
        xml2_str = xml2.to_str(do_pretty=True, dont_do_tags=["p"])
        print(xml2_str)
        print("########/END")
        self.assertEqual(xml1_str, xml2_str)


xml3_text = """ <a class="class1" id="id1">text<c/></a> """


class MyTestCase2(unittest.TestCase):
    def test_something(self):
        xml3 = xl.parse(xml3_text, do_strip=True)
        root2 = xl.parse_e(xml3_text)
        xml4 = xl.Xml(root=root2)
        print()
        print("########/BEGING")
        print("########/xml3:")
        print(xml3.to_str(self_closing=False))
        print("########/xml4:")
        print(xml4.to_str(self_closing=False))
        print("########/END")
        self.assertEqual(xml3.to_str(self_closing=False), xml4.to_str(self_closing=False))


class MytestCase3(unittest.TestCase):
    def test_api(self):
        xml3 = xl.parse(xml3_text, do_strip=True)
        for x in xml3.root.kids:
            if isinstance(x, xl.Element):
                print(repr(x.tag))

        print("here", xml3.prolog, xml3.root, xml3.doctype)

        self.assertEqual(len(xml3.root.find_kids("c")), 1)


if __name__ == '__main__':
    unittest.main()
