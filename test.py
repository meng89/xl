#!/usr/bin/env python3
import xl


xmlfile = "/mnt/data/projects/xml-p5a/T/T01/T01n0001.xml"

s = open(xmlfile).read()

s = """ <a><!--CBETA todo type: a--><!--CBETA todo type: newmod--> </a>"""
s = """<a>&gt;</a>"""
xml = xl.parse(s, ignore_comment=True)

print("end")
print(xml.to_str())
