"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Generateur de sitemap
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
class SitemapGenerator:
    def __init__(self, base_url):
        self.base_url = base_url
        self.sitemap_urls = []

    def add_url(self, url, lastmod=None, changefreq='monthly', priority=None):
        url_entry = {'loc': url}
        if lastmod:
            url_entry['lastmod'] = lastmod
        if changefreq:
            url_entry['changefreq'] = changefreq
        if priority:
            url_entry['priority'] = priority
        self.sitemap_urls.append(url_entry)

    def generate_sitemap_xml(self):
        from xml.etree.ElementTree import Element, SubElement, tostring
        sitemap = Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
        for url in self.sitemap_urls:
            url_element = SubElement(sitemap, 'url')
            for key, value in url.items():
                SubElement(url_element, key).text = value
        return tostring(sitemap, encoding='utf-8', method='xml').decode('utf-8')
