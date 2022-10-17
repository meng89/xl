# xl mean "XML without mire"　无坑 XML

# Installtion　安装
## pip 
```shell
pip install xl@git+https://github.com/meng89/xl#egg=xl
```
## requirements.txt
```requirements.txt
xl@git+https://github.com/meng89/xl#egg=xl
```

# Usage　使用
## Create an XML file　写 XML：
```python
import xl

doctype = xl.DocType("html")
html = xl.Element("html")
body = xl.sub(html, "body")
p = xl.sub(body, "p")
p.kids.append("Hello World!")

xml = xl.Xml(doctype=doctype, root=html)
print(xml.to_str())

```

## Read an XML file　读 XML：
```python
import xl

xml_string = """<!DOCTYPE html>
<html><body><p>Hello World!</p></body></html>"""

xml = xl.parse(xml_string)
html = xml.root
body = html.kids[0]
p = body.kids[0]
print(p.kids[0])
```

# This software is licensed under the MIT license