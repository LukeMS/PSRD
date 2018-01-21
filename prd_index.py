import codecs
import os

from bs4 import BeautifulSoup

import prd

TABLE = {}
SOUP = BeautifulSoup("", "lxml")
BULLETS = ["", "*", "+", "-", "•", "‣", "⁃"]

TEMPLATE = """

PFRPG Reference Document
#########################

The PFRPG is released under the `Open Game License`_, meaning the core rules that drive the PFRPG system are available to anyone to use for free under the terms of the OGL.

This compendium of rules, charts, and tables contains all of the open rules in the system, and is provided for the use of the community of gamers and publishers working with the system.

Table of contents
#################

{}

.. toctree::
   :hidden:

{}

Open Game License
##################

.. include:: opengamelicense.rst

"""

def fancy_part(part):
    part = part.strip()
    part = part.replace(part[0], part[0].upper(), 1)

    res = "".join([(c.isupper() and " " or "") + c for c in part]).strip()
    return res

def fancy_name(text):
    split = text.split("/")
    return [fancy_part(part) for part in split]

def set_recursive_dict_entry(v, *keys):
    entry = TABLE
    for i, k in enumerate(keys):
        """
        dbg = "{}/{} (key: '{}' / keys: '{}'".format(
            i + 1, len(keys), k, keys)
        print(dbg)
        """
        entry.setdefault(k, {"_children": {}, "_level": i})
        # last one
        if i == len(keys) - 1:
            entry[k]["_url"] = v
        else:
            entry = entry[k]["_children"]

def create_dict(urls):
    for url in sorted(urls):
        text = url.replace("/pathfinderRPG/prd/", "").replace(
            ".html", "").strip()
        level = text.count("/")
        fancy_list = fancy_name(text)
        set_recursive_dict_entry(url, *fancy_list)

def dict_to_lines(table, lines = None):
    # create list for first recursion
    lines = lines or []
    keys = sorted(list(table.keys()))
    for k in keys:
        v = table[k]
        if type(v) == dict:
            url = v.pop("_url", None)
            if url:
                text = prd._parse_href_local(url, k)
            else:
                text = k
            level = v["_level"]
            text = (("  " * (level)) + "{} ".format(BULLETS[level + 1]) +
                    text)
            if level == 0:
                text = ".. rst-class:: top\n\n" + text
            lines.append(text)
            dict_to_lines(v["_children"], lines)
    return "\n\n".join(lines)

def create_index(urls):
    lines = []
    for url in sorted(urls):
        text = url.replace("/pathfinderRPG/prd/", "").replace(
            ".html", "").strip()
        level = text.count("/")
        fancy_list = fancy_name(text)
        rst_file = url.replace("/pathfinderRPG/prd/", "").replace(
            "/", ".").replace(".html", ".rst").lower()
        index_name = "   " + fancy_list[-1] + " ({}) <{}>".format(
            "\\".join(fancy_list[:-1]),
            rst_file
        )
        lines.append(index_name)
    return "\n\n".join(sorted(lines))

def create_rst(urls):
    create_dict(urls)
    toc = (dict_to_lines(TABLE))

    index = create_index(urls)

    rst = TEMPLATE.format(toc, index)

    with open("index.rst", "w", encoding='utf-8') as f:
        f.write(rst)


def main():
    with open(os.path.join("html", "urls.txt"), "r", encoding='utf-8') as f:
        urls = f.read().splitlines()
        urls.remove("/pathfinderRPG/prd/openGameLicense.html")
    """
    from pprint import pprint
    pprint(TABLE, indent = 2)
    """
    create_rst(urls)

if __name__ == '__main__':
    # main()
    pass
