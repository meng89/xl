#!/usr/bin/env python3

import xl

xml_string = """<!DOCTYPE html>
<html><body><p>Hello World!</p></body></html>"""

xml = xl.parse(xml_string)
html = xml.root
body = html.kids[0]
p = body.kids[0]
print(p.kids[0])
