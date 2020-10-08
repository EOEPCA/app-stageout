"""ellip_atom main script containing the Atom class"""

import lxml.etree as etree

namespaces = dict()

namespaces['opt'] = 'http://www.opengis.net/opt/2.1'
namespaces['om']  = 'http://www.opengis.net/om/2.0'
namespaces['gml'] = 'http://www.opengis.net/gml/3.2'
namespaces['eop'] = 'http://www.opengis.net/eop/2.1'
namespaces['sar'] = 'http://www.opengis.net/sar/2.1'
namespaces['ssp'] = 'http://www.opengis.net/ssp/2.1'
namespaces['owc'] = 'http://www.opengis.net/owc/1.0'
namespaces['atom'] = 'http://www.w3.org/2005/Atom'
namespaces['terradue'] = 'http://www.terradue.com'

class Atom(object):
    """class Atom"""

    tree = None
    root = None
    entry = None

    def __init__(self, root):
        self.root = root
        self.tree = root
        self.links = self.root.xpath('/a:feed/a:entry/a:link', namespaces={'a':'http://www.w3.org/2005/Atom'})
        entries = self.root.xpath('/a:feed/a:entry', namespaces={'a':'http://www.w3.org/2005/Atom'})
        if entries:
            self.entry = entries[0]

    @staticmethod
    def from_template(template=None):
        """Create an atom with 1 entry from template"""#

        if template is None:
            template = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title type="text"></title>
    <summary type="html"></summary>
    <link rel="enclosure" type="application/octet-stream" href=""/>
    <date xmlns="http://purl.org/dc/elements/1.1/"></date>
    <published></published>
    <identifier xmlns="http://purl.org/dc/elements/1.1/"></identifier>
  </entry>
</feed>"""
        parser = etree.XMLParser(recover=True, encoding='utf-8', remove_blank_text=True)    
        tree = etree.fromstring(template, parser)
        return Atom(tree)


    def set_identifier(self, identifier):
        """Set first atom entry identifier"""

        el_identifier = self.root.xpath('/a:feed/a:entry/d:identifier',
                                        namespaces={'a':'http://www.w3.org/2005/Atom',
                                                    'd':'http://purl.org/dc/elements/1.1/'})

        el_identifier[0].text = identifier

    def get_identifier(self):
        """Get first atom entry identifier"""

        el_identifier = self.root.xpath('/a:feed/a:entry/d:identifier',
                                        namespaces={'a':'http://www.w3.org/2005/Atom',
                                                    'd':'http://purl.org/dc/elements/1.1/'})

        if not el_identifier:
            return None

        return el_identifier[0].text

    def get_total_results(self):
        """get OS total results in feed"""

        total_results = self.root.xpath('/a:feed/os:totalResults',
                                        namespaces={'a':'http://www.w3.org/2005/Atom',
                                                    'os':'http://a9.com/-/spec/opensearch/1.1/'})

        if not total_results:
            return None

        return int(total_results[0].text)

    def set_title(self, text):
        """Set first atom entry title text"""

        el_title = self.root.xpath('/a:feed/a:entry/a:title',
                                   namespaces={'a':'http://www.w3.org/2005/Atom'})

        el_title[0].text = text

    def get_title(self, create=False):
        """get title text"""

        titles = self.root.xpath('/a:feed/a:entry/a:title',
                                 namespaces={'a':'http://www.w3.org/2005/Atom'})

        if not titles:
            if create:
                titles = [etree.SubElement(self.entry, "{http://www.w3.org/2005/Atom}title")]
                return titles[0]
            return None

        return titles[0].text

    def set_summary(self, text):
        """set summary text"""

        summaries = self.root.xpath('/a:feed/a:entry/a:summary',
                                    namespaces={'a':'http://www.w3.org/2005/Atom'})

        if not summaries:
            summary = self.get_summary(create=True)
        else:
            summary = summaries[0]

        summary.text = text

    def get_summary(self, create=False):
        """get summary text"""

        summaries = self.root.xpath('/a:feed/a:entry/a:summary',
                                    namespaces={'a':'http://www.w3.org/2005/Atom'})

        if not summaries:
            if create:
                summaries = [etree.SubElement(self.entry, "{http://www.w3.org/2005/Atom}summary")]

                return summaries[0].text

            return None

        return summaries[0].text

    def get_links(self, rel_type):
        """get links"""

        return self.root.xpath('/a:feed/a:entry/a:link[@rel = "{0}"]'.format(rel_type),
                               namespaces={'a':'http://www.w3.org/2005/Atom'})

    def set_enclosure_link(self, href, title, mime_type="application/octet-stream"):
        """get enclosure link"""

        el_enclosure_link = self.root.xpath('/a:feed/a:entry/a:link[@rel="enclosure" and (@href="" or @href="{0}")]'.format(href),
                                            namespaces={'a':'http://www.w3.org/2005/Atom'})

        if el_enclosure_link:
            link = el_enclosure_link[0]
            link.attrib['href'] = href
        else:
            link = self.add_enclosure_link(href, title, mime_type)

    def add_enclosure_link(self, href, title, mime_type="application/octet-stream"):
        """add results link"""

        xml_string = '<link rel="enclosure" type="%s" title="%s" href="%s"/>' % (mime_type, title, href.replace('&', '&amp;'))

        link = etree.fromstring(xml_string)
        self.entry.append(link)

        return link

    def add_extension(self, xml_ext):
        """add extension"""

        el_entry = self.root.xpath('/a:feed/a:entry/b:identifier',
                                   namespaces={'a':'http://www.w3.org/2005/Atom',
                                               'b':'http://purl.org/dc/elements/1.1/'})

        el_entry[0].addnext(xml_ext)

    def add_link(self, href, rel, title=None, link_type=None):
        """add link"""

        link = etree.SubElement(self.root.xpath('/a:feed/a:entry',
                                                namespaces={'a':'http://www.w3.org/2005/Atom'})[0],
                                "{http://www.w3.org/2005/Atom}link")

        link.attrib['href'] = href
        link.attrib['rel'] = rel

        if title:
            link.attrib['title'] = title
        if link_type:
            link.attrib['type'] = link_type

    def remove_link(self, rel, link_title=None, link_type=None, link_url=None):
        """remove link"""

        links = self.get_links(rel)
        link_filter = None
        value = None

        if link_title:
            link_filter = 'title'
            value = link_title
        elif link_type:
            link_filter = 'type'
            value = link_type
        elif link_url:
            link_filter = 'url'
            value = link_url
        else:
            raise Exception("Required parameter link_title, link_type or link_url")

        for link in links:
            if link.attrib[link_filter] == value:
                link.getparent().remove(link)


    def get_offering_elements(self, offering_code):
        """get offering elements"""

        return self.root.xpath('/a:feed/a:entry/b:offering[@code="{0}"]'.format(offering_code),
                               namespaces={'a':'http://www.w3.org/2005/Atom',
                                           'b':'http://www.opengis.net/owc/1.0'})

    @staticmethod
    def get_operation_elements(offering_element, operation_code=None):
        """get operation elements"""

        xpath = 'b:operation'
        if operation_code:
            xpath += '[@code="{0}"]'.format(operation_code)
        return offering_element.xpath(xpath, namespaces={'b':'http://www.opengis.net/owc/1.0'})

    def add_offering(self, offering):
        """add offering"""

        self.root.xpath('/a:feed/a:entry',
                        namespaces={'a':'http://www.w3.org/2005/Atom'})[0].append(offering)

    def add_offerings(self, offerings):
        """add offerings"""

        for offering in offerings:
            self.add_offering(offering)
            
            
    def set_offering(self, offering):
            
        if self.get_offering_elements(offering.attrib['code']):

            self.get_offering_elements(offering.attrib['code'])[0].getparent().remove(self.get_offering_elements(offering.attrib['code'])[0])
            
        self.root.xpath('/a:feed/a:entry',
                        namespaces={'a':'http://www.w3.org/2005/Atom'})[0].append(offering)


    def set_dctspatial(self, wkt):
        """set summary"""

        spatials = self.root.xpath('/a:feed/a:entry/c:spatial',
                                   namespaces={'a':'http://www.w3.org/2005/Atom',
                                               'c':'http://purl.org/dc/terms/'})
        if not spatials:
            el_spatial = self.get_dctspatial(True)
        else:
            el_spatial = spatials[0]

        el_spatial.text = wkt

    def get_dctspatial(self, create=False):
        """get or create summary"""

        spatials = self.root.xpath('/a:feed/a:entry/c:spatial',
                                   namespaces={'a':'http://www.w3.org/2005/Atom',
                                               'c':'http://purl.org/dc/terms/'})

        if not spatials:
            if create:
                spatials = [etree.SubElement(self.entry, "{http://purl.org/dc/terms/}spatial")]

                return spatials[0]

            return None

        return spatials[0].text

    def set_dcdate(self, date):
        """set dcdate"""

        el_dates = self.root.xpath('/a:feed/a:entry/d:date',
                                   namespaces={'a':'http://www.w3.org/2005/Atom',
                                               'd':'http://purl.org/dc/elements/1.1/'})

        if not el_dates:
            dcdate = self.get_dcdate(True)
        else:
            dcdate = el_dates[0]

        dcdate.text = date

    def get_dcdate(self, create=False):
        """get or create dcdate"""

        el_dates = self.root.xpath('/a:feed/a:entry/d:date',
                                   namespaces={'a':'http://www.w3.org/2005/Atom',
                                               'd':'http://purl.org/dc/elements/1.1/'})

        if not el_dates:
            if create:
                el_dates = [etree.SubElement(self.entry, "{http://purl.org/dc/elements/1.1/}date")]

                return el_dates[0]

            return None

        return el_dates[0].text

    def set_published(self, published):
        """set published"""

        el_published = self.root.xpath('/a:feed/a:entry/a:published',
                                       namespaces={'a':'http://www.w3.org/2005/Atom'})
        el_published[0].text = published

    def set_category(self, term, label=None, scheme=None):
        """get categories"""

        categories = self.get_categories(term, scheme)

        if not categories:
            categories = [etree.SubElement(self.entry, "{http://www.w3.org/2005/Atom}category")]

        categories[0].attrib['term'] = term
        if label != None:
            categories[0].attrib['label'] = label
        if scheme != None:
            categories[0].attrib['scheme'] = scheme

    def get_categories(self, term, scheme=None):
        """get categories"""

        cat_filter = '@term="{0}"'.format(term)
        if scheme != None:
            cat_filter = '{0} and @scheme="{1}"'.format(cat_filter, scheme)

        return self.root.xpath('/a:feed/a:entry/a:category[{0}]'.format(cat_filter),
                               namespaces={'a':'http://www.w3.org/2005/Atom'})

    def get_category_by_scheme(self, scheme):
        """get category by scheme"""

        categories = self.root.xpath('/a:feed/a:entry/a:category[@scheme="{0}"]'.format(scheme),
                                     namespaces={'a':'http://www.w3.org/2005/Atom'})
        if not categories:
            return None

        return categories[0]

    def remove_category(self, term, scheme=None):
        """get and remove category"""

        for category in self.get_categories(term, scheme):
            category.getparent().remove(category)

    def remove_category_by_scheme(self, scheme):
        """remove categoriy by scheme"""

        cat_filter = '@scheme="{0}"'.format(scheme)

        categories = self.root.xpath('/a:feed/a:entry/a:category[{0}]'.format(cat_filter),
                                     namespaces={'a':'http://www.w3.org/2005/Atom'})
        for category in categories:
            category.getparent().remove(category)

    def set_generator(self, uri, version, text):
        """get or create generator"""

        el_generator = self.root.xpath('/a:feed/a:entry/a:generator',
                                       namespaces={'a':'http://www.w3.org/2005/Atom'})

        if not el_generator:
            el_generator = [etree.SubElement(self.root.xpath('/a:feed/a:entry',
                                                             namespaces={'a':'http://www.w3.org/2005/Atom'})[0],
                                             "{http://www.w3.org/2005/Atom}generator")]

        el_generator[0].attrib['uri'] = uri
        el_generator[0].attrib['version'] = version
        el_generator[0].text = text

    @staticmethod
    def get_latest_offering_date(offering):
        """get latest offering date"""

        date = offering.xpath('b:operation[not(../b:operation/dc:date > dc:date)]/dc:date',
                              namespaces={'b':'http://www.opengis.net/owc/1.0',
                                          'dc':'http://purl.org/dc/elements/1.1/'})
        if date:
            return date[0].text
        return None

    def append_summary_html(self, text):
        """Append atom summary with text"""

        html_summary = self.get_summary(True)
        html_summary += "<p>%s</p>" % text

        self.set_summary(html_summary)

    def to_string(self, pretty_print=True):
        """convert to string"""

        return etree.tostring(self.tree, pretty_print=pretty_print).decode()

    def clear_enclosures(self):
        """clear enclosures"""

        links = self.get_links("enclosure")
        for link in links:
            link.getparent().remove(link)

    def get_extensions(self, name, namespace):
        """get extensions"""

        return self.root.xpath('/a:feed/a:entry/e:{0}'.format(name),
                               namespaces={'a':'http://www.w3.org/2005/Atom',
                                           'e':namespace})

    def get_wps_request_output(self):
        """get the output of the WPSExecute request"""

        return self.root.xpath('/a:feed/a:entry/b:offering/b:operation[@code="Execute"]\
        /b:request/c:Execute/c:ResponseForm/c:ResponseDocument/c:Output/e:Identifier',
                               namespaces={'a':'http://www.w3.org/2005/Atom',
                                           'b':'http://www.opengis.net/owc/1.0',
                                           'c':'http://www.opengis.net/wps/1.0.0',
                                           'dc':'http://purl.org/dc/elements/1.1/',
                                           'e':'http://www.opengis.net/ows/1.1'})[0].text

       
    def get_styleset(self):
    
        return self.get_offering_elements('http://www.terradue.com/spec/owc/1.0/req/atom/datacontext')[0].xpath('owc:styleSet', namespaces=namespaces)
    
    def get_collections(self):
    
        return self.get_offering_elements('http://www.terradue.com/spec/owc/1.0/req/atom/opensearch')[0].xpath('owc:operation', namespaces=namespaces)


