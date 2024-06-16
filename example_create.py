#!/usr/bin/env python3

import xl

doctype = xl.DocType()
html = xl.Element("html")
body = html.ekid("body")
p = body.ekid("p")
p.skid("Hello World!")

xml = xl.Xml(doctype=doctype, root=html)
print(xml.to_str(do_pretty=True, dont_do_tags=["p"]))
