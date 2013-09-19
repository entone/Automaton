import re
import unidecode

def slugify(st):
    st = unidecode.unidecode(unicode(st)).lower()
    return re.sub(r'\W+','-',st)
