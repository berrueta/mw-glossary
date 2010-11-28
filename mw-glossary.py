#
# (c) Diego Berrueta, 2010
#
# See the README
#

import client # http://sourceforge.net/apps/mediawiki/mwclient/index.php?title=Main_Page
import sys
from string import maketrans, translate
import re
import getopt

###########################################################

def populate_glos(host, path, catName, username = None, password = None, domain = None):
    site = client.Site(host, do_init=False, path=path)

    if (username is not None and password is not None):
        if (domain is not None):
            site.login(username,password,domain=domain)
        else:
            site.login(username,password)
    site.site_init()

    cat = site.Categories[catName]
    glos = {}
    for page in cat:
        if (page.namespace == 0):
            print "Retrieving", page.name
            allDef = page.edit()
            filteredParas = filter(lambda p : len(p) > 0 and p[0].isalpha(), allDef.splitlines())
            if (len(filteredParas) > 0):
                firstPara = filteredParas[0]
                glos[str(page.name)] = str(firstPara)
            else:
                print "Ignoring unusable definition for", page.name
        else:
            print "Discarding page", page.name, "in namespace", page.namespace
    return glos

###########################################################

def output_html_glossary(glos, out = sys.stdout):
    out.write("<html><body><dl>")
    items = glos.items()
    items.sort()
    for k,v in items:
        out.write("<dt>%s</dt><dd>%s</dd>" % (k, to_html(v)))
    out.write("</dl></body></html>")

def to_html(s):
    s = re.sub("\[\[((.*)\|)?([^\]]*)\]\]","<u>\\3</u>", s)  # remove [[Internal|Links]]
    s = re.sub("\[([^\] ]*) ([^\]]*)\]","<a href=\"\\1\">\\2</a>", s)    # change [http://example.org External links] 
    s = re.sub("'''([^']*)'''", "<b>\\1</b>", s)  # change '''bold'''
    s = re.sub("''([^']*)''", "<i>\\1</i>", s)  # change ''italics''
    return s    

###########################################################

def output_latex_glossary(glos, out = sys.stdout):
    out.write("\\makeglossary\n\n")
    items = glos.items()
    items.sort()
    for k,v in items:
        latexKey = "glo:%s" % translate(k.lower(), maketrans(" ", "-"), ".")
        out.write("\\storeglosentry{%s}{name={%s},description={%s}}\n\n" % (latexKey, k, to_latex(v)))


def to_latex(s):
    s = re.sub("\[\[((.*)\|)?([^\]]*)\]\]","\\\\underline{\\3}", s)  # change [[Internal|Links]]
    s = re.sub("\[([^\] ]*) ([^\]]*)\]","\\2", s)    # change [http://example.org External links] 
    s = re.sub("'''([^']*)'''", "\\\\textbf{\\1}", s)  # change '''bold'''
    s = re.sub("''([^']*)''", "\\\\textit{\\1}", s)  # remove ''italics''
    s = re.sub("\"([^\"]*)\"", "``\\1''", s)    # change "quotes"
    return s
    
###########################################################

def usage():
    print """
    --help            : show this usage instructions
    --output filename : write the output to the designated file
    --user username   : wiki username
    --pass password   : wiki password
    --domain domain   : wiki authentication domain
    --host hostname   : wiki hostname (e.g., "wikipedia.org")
    --path path       : wiki path (e.g., "/w/")
    --category cat    : wiki category (e.g., "Glossary")
    --latex | --html  : selects the output format
    """

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho", ["help", "output=", "user=", "pass=", "domain=", "host=", "path=", "category=", "latex", "html"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    output = sys.stdout
    username = None
    password = None
    domain = None
    host = None
    path = "/w/"
    category = "Glossary"
    output_func = output_latex_glossary
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-o", "--output"):
            output = open(a, "wt")
        elif o == "--user":
            username = a
        elif o == "--pass":
            password = a
        elif o == "--domain":
            domain = a
        elif o == "--host":
            host = a
        elif o == "--path":
            path = a
        elif o == "--category":
            category = a
        elif o == "--latex":
            output_func = output_latex_glossary
        elif o == "--html":
            output_func = output_html_glossary
        else:
            assert False, "unhandled option"
    if host is None:
        usage()
    else:
        glos = populate_glos(host, path, category, username = username, password = password, domain = domain)
        output_func(glos, output)
    