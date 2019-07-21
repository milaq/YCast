import xml.etree.cElementTree as etree

XML_HEADER = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'


def get_init_token():
    return XML_HEADER + '<EncryptedToken>0000000000000000</EncryptedToken>'


def strip_https(url):
    if url.startswith('https://'):
        url = 'http://' + url[8:]
    return url


class Page:
    def __init__(self):
        self.items = []
        self.count = -1

    def add(self, item):
        self.items.append(item)

    def set_count(self, count):
        self.count = count

    def to_xml(self):
        xml = etree.Element('ListOfItems')
        etree.SubElement(xml, 'ItemCount').text = str(self.count)
        for item in self.items:
            item.append_to_xml(xml)
        return xml

    def to_string(self):
        return XML_HEADER + etree.tostring(self.to_xml()).decode('utf-8')


class Previous:
    def __init__(self, url):
        self.url = url

    def append_to_xml(self, xml):
        item = etree.SubElement(xml, 'Item')
        etree.SubElement(item, 'ItemType').text = 'Previous'
        etree.SubElement(item, 'UrlPrevious').text = self.url
        etree.SubElement(item, 'UrlPreviousBackUp').text = self.url
        return item


class Display:
    def __init__(self, text):
        self.text = text

    def append_to_xml(self, xml):
        item = etree.SubElement(xml, 'Item')
        etree.SubElement(item, 'ItemType').text = 'Display'
        etree.SubElement(item, 'Display').text = self.text
        return item


class Search:
    def __init__(self, caption, url):
        self.caption = caption
        self.url = url

    def append_to_xml(self, xml):
        item = etree.SubElement(xml, 'Item')
        etree.SubElement(item, 'ItemType').text = 'Search'
        etree.SubElement(item, 'SearchURL').text = self.url
        etree.SubElement(item, 'SearchURLBackUp').text = self.url
        etree.SubElement(item, 'SearchCaption').text = self.caption
        etree.SubElement(item, 'SearchTextbox').text = None
        etree.SubElement(item, 'SearchButtonGo').text = "Search"
        etree.SubElement(item, 'SearchButtonCancel').text = "Cancel"
        return item


class Directory:
    def __init__(self, title, destination):
        self.title = title
        self.destination = destination

    def append_to_xml(self, xml):
        item = etree.SubElement(xml, 'Item')
        etree.SubElement(item, 'ItemType').text = 'Dir'
        etree.SubElement(item, 'Title').text = self.title
        etree.SubElement(item, 'UrlDir').text = self.destination
        etree.SubElement(item, 'UrlDirBackUp').text = self.destination
        return item


class Station:
    def __init__(self, uid, name, description, url, logo, genre, location, mime, bitrate, bookmark):
        self.uid = uid
        self.name = name
        self.description = description
        self.url = strip_https(url)
        self.logo = logo
        self.genre = genre
        self.location = location
        self.mime = mime
        self.bitrate = bitrate
        self.bookmark = bookmark

    def append_to_xml(self, xml):
        item = etree.SubElement(xml, 'Item')
        etree.SubElement(item, 'ItemType').text = 'Station'
        etree.SubElement(item, 'StationId').text = self.uid
        etree.SubElement(item, 'StationName').text = self.name
        etree.SubElement(item, 'StationUrl').text = self.url
        etree.SubElement(item, 'StationDesc').text = self.description
        etree.SubElement(item, 'Logo').text = self.logo
        etree.SubElement(item, 'StationFormat').text = self.genre
        etree.SubElement(item, 'StationLocation').text = self.location
        etree.SubElement(item, 'StationBandwidth').text = self.bitrate
        etree.SubElement(item, 'StationMime').text = self.mime
        etree.SubElement(item, 'StationBookmark').text = self.bookmark
        return item
