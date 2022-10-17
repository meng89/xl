#!/usr/bin/env python3

import xl

doctype = xl.DocType("html")
html = xl.Element("html")
body = xl.sub(html, "body")
p = xl.sub(body, "p")
p.kids.append("Hello World!")

xml = xl.Xml(doctype=doctype, root=html)
print(xml.to_str())

