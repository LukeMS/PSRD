#!/usr/bin/env python
# -*- coding:utf-8 -*-

import bz2
import codecs
import copy
import hashlib as hash
import os
import pickle
import re
import shutil
import zlib

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Comment

import prd_fixes

PARSER = None

INDEX = "https://paizo.com/pathfinderRPG/prd/index.html"

OGL = "/pathfinderRPG/prd/openGameLicense.html"

HEADERS = [None, "#", "*", "=", "~", "+", "-"]

BULLETS = [None, "*", "+", "-", "•", "‣", "⁃"]

DEBUG = 0

# if True only offline files cached responses will be used
OFFLINE = False

# overwrites existing rst files (if non-existent or changed)
# OVERWRITE, HALT_ON_ERROR = "all", False
# OVERWRITE, HALT_ON_ERROR = "all", True
# OVERWRITE, HALT_ON_ERROR = True, False
# OVERWRITE, HALT_ON_ERROR = False, True
OVERWRITE, HALT_ON_ERROR = False, False

order = sorted

TRADEMARKS = {
    "Pathfinder RPG": "PRD"
}

VALID_SRC = [
    "advancedclassguide",
    "advancedplayersguide",
    "advancedraceguide",
    "bestiary",
    "bestiary2",
    "bestiary3",
    "bestiary4",
    "bestiary5",
    "corerulebook",
    "indices", # PRD indices are at /indices
    "gamemasteryguide",
    "monstercodex",
    "mythicadventures",
    "npccodex",
    "occultadventures",
    "technologyguide",
    "ultimatecampaign",
    "ultimatecombat",
    "ultimateequipment",
    "ultimatemagic",
    "unchained",
]

CORE_PAGES = [
    "gettingStarted",
    "races",
    "classes",
    "usingSkills",
    "skillDescriptions",
    "skills",
    "feats",
    "equipment",
    "additionalRules",
    "combat",
    "magic",
    "spellLists",
    "spellIndex",
    "spells",
    "prestigeClasses",
    "gamemastering",
    "environment",
    "nPCClasses",
    "creatingNPCs",
    "magicItems",
    "glossary",
]

DBGPRINT_LAST_END = "\n"

HASH_BLOCKSIZE = 65536

VALID_ANCHOR = re.compile("[a-z0-9_]+")


""" ###################
    Common utilities
""" ####################


def hash_file2(fname):
    sha = hash.sha256()
    with open(fname, 'rb') as f:
        file_buffer = f.read(HASH_BLOCKSIZE)
        while len(file_buffer) > 0:
            sha.update(file_buffer)
            file_buffer = f.read(HASH_BLOCKSIZE)
    return sha.hexdigest()

def hash_file(fname):
    with open(fname, 'rb') as f:
        return zlib.crc32(f.read())

def equal_file_hashes(f1, f2):
    return hash_file(f1) == hash_file(f2)

def parse_unicode_encode_error(e, txt):
    text = e.args[0]
    # print("parse_unicode_encode_error (pos: {})".format(e.args[2]))
    pos = e.args[2]
    print("parse_unicode_encode_error '{}'".format(txt[pos - 50: pos - 1]))

def save_dict(data, fname):
    """Save a dictionary data to a bz2-compressed pickle file."""
    bin_data = bz2.compress(pickle.dumps(data))
    with open(fname, "wb") as f:
        f.write(bin_data)


def load_dict(fname):
    """Load a dictionary from a bz2-compressed pickle file."""
    with open(fname, 'rb') as f:
        data = pickle.loads(bz2.decompress(f.read()))
    return data


def dbgprint(level, *args, **kwargs):
    global DBGPRINT_LAST_END
    head = DBGPRINT_LAST_END == "\n" and ">>>" or None

    if DEBUG >= level:
        fn = kwargs.pop("fn", None)
        if fn:
            if head:
                print(head, fn(*args), **kwargs)
            else:
                print(fn(*args), **kwargs)
        else:
            if head:
                print(head, *args, **kwargs)
            else:
                print(*args, **kwargs)
    DBGPRINT_LAST_END = kwargs.get("end", "\n")


def xassert(test, *args, **kwargs):
    if not test:
        dbgprint(0, "Assertion Error", *args, **kwargs)
        raise(AssertionError("Assertion Error"))


def shoehorn(s):
    """Remove accents (but also other things, like ß‘’“”)."""
    import unicodedata as ud
    return ud.normalize('NFKD', s).encode(
        'ascii', 'ignore').decode('utf-8', 'ignore')


class RequestsInterface:

    cache_file = "cache/reqint.bz2p"

    def __init__(self):
        if os.path.isfile(self.cache_file):
            dbgprint(0, "using cached version of '{}'",
                     self.cache_file,
                     fn=str.format)
            self.cache = load_dict(self.cache_file)
        else:
            self.cache = {}
        import requests as _requests
        RequestsInterface._requests = _requests
        RequestsInterface.req_count = 0
        RequestsInterface.exceptions = RequestsInterfaceExceptions(
            _requests)

    def close(self):
        save_dict(self.cache, self.cache_file)

    def get(self, url, *args):
        if url in self.cache:
            r = self.cache[url]
            r.raise_for_status()
            return r

        if OFFLINE:
            raise self.exceptions.PageNotFoundOrOfflineError(
                "Currently offline, url: " + url)
        else:
            self.req_count += 1
            dbgprint(1, "<requesting '{}'>", url, fn=str.format)
            r = RequestsInterface._requests.get(url, *args)
            self.cache[url] = r
            r.raise_for_status()
            return r


def local_html_path(url):
    url = url.replace("/pathfinderRPG/prd/", "").replace(".html", "")
    if url.startswith("/"):
        url = url.replace("/", "")
    local = "html/" + url.replace("/", ".")
    return local.lower()


def test_get_page(url, dbg=1):
    try:
        # before anything, check locally
        local = local_html_path(url)
        assert(not local.endswith("."))
        if os.path.isfile(local):
            dbgprint(dbg, " and found '{}' locally¹", local,
                     fn=str.format)
            return True
        else:
            dbgprint(dbg, " but couldn't find '{}' locally, ", local,
                     fn=str.format, end = " ")

        # now try to retrieve it
        get_page(url)
        dbgprint(dbg, "and retrieved online version, ", end=" ")
        if os.path.isfile(local):
            dbgprint(dbg, "and found it locally²")
            return True

        dbgprint(dbg, "but couldn't find '{}' locally", local,
                 fn=str.format)
        return False
    except AssertionError as e:
        dbgprint(0, "\nDebug information : url: '{}'", url, fn=str.format)
        raise e

    except (requests.exceptions.HTTPError,
            requests.exceptions.PageNotFoundOrOfflineError
    ) as e:
        dbgprint(dbg,
                 "but couldn't retrieve online page ({}).",
                 e,
                 fn=str.format)
        return False
    except InvalidLinkError as e:
        dbgprint(dbg,
                 "but the link isn't valid ({}).",
                 e,
                 fn=str.format)
        return False

def _stdref_core_page(_ref, anchor, ref, dbg, current=None):
    current = current or PARSER.current
    # core single page
    if "/" not in ref:
        alt_url = "/pathfinderRPG/prd/coreRulebook/" + ref
        alt_url = alt_url.replace("//", "/")
        dbgprint(dbg,
            "'core single page' (guess: '{}', _ref: '{}' -> ref: '{}')",
            alt_url, _ref, ref,
            fn=str.format, end=" ")
        if test_get_page(alt_url):
            return alt_url, alt_url + anchor
    # core subpage
    else:
        alt_url = ref.replace("pathfinderRPG/prd", "").split("/")
        alt_url = "/".join([v for v in alt_url if v])
        alt_url = ("/pathfinderRPG/prd/coreRulebook/" + alt_url).replace(
            "//", "/")
        dbgprint(dbg,
            "'core subpage' (guess: '{}', _ref: '{}' -> ref: '{}')",
            alt_url, _ref, ref,
            fn=str.format, end=" ")
        if test_get_page(alt_url):
            return alt_url, alt_url + anchor

    return None, None


def _stdref_current_folder(_ref, anchor, ref, dbg, current=None):
    current = current or PARSER.current
    base = current.replace("/pathfinderRPG/prd/", "").split("/")
    base = [v for v in base if v][:-1]
    if len(base) == 0:
        return None, None
    base_str = "/".join(base)
    is_valid_src = base[0].lower() in VALID_SRC
    dbgprint(
        dbg,
        "(§ _stdref_current_folder ("
        "(base_str: '{}', "
        "is_valid_src: '{}'"
        ")",
        base_str,
        is_valid_src,
        fn=str.format,
        end=" ")
    if is_valid_src and base[0].lower() != "indices":
        alt_url = base_str + "/" + ref
        alt_url = alt_url.replace("//", "/")
        if not alt_url.startswith("/pathfinderRPG/prd/"):
            alt_url = "/pathfinderRPG/prd/" + alt_url
        alt_url = alt_url.replace("//", "/")
        dbgprint(dbg,
            "'current folder' (guess: '{}', _ref: '{}' -> ref: '{}')",
             alt_url, _ref, ref,
             fn=str.format, end=" ")
        if test_get_page(alt_url):
            return alt_url, alt_url + anchor

    return None, None


def _standard_ref(_ref, anchor, ref, current=None):
    dbg = 1
    current = current or PARSER.current
    # optimal case
    if ref.startswith("/pathfinderRPG/prd"):
        dbgprint(dbg,
            "'optimal case' (ref: '{}', _ref: '{}')",
             ref, _ref,
             fn=str.format, end=" ")
        try:
            check_link(ref)
        except InvalidLinkError as e:
            # just checking it, no need to raise
            dbgprint(dbg, ", but the link is invalid.")
        else:
            if test_get_page(ref, dbg):
                return ref, anchor and "#".join([ref, anchor]) or ref

    # second best just needs the prefix
    if (ref.startswith("/") and
        "pathfinderRPG" not in ref and
        [v for v in ref.split("/") if v][0].lower() in VALID_SRC
    ):
        try:
            alt_url = ("/pathfinderRPG/prd/" + ref).replace("//", "/")
            check_link(alt_url)
            return alt_url, anchor and "#".join([alt_url, anchor]) or alt_url
        except InvalidLinkError as e:
            # just checking it, no need to raise
            pass

    # local anchor
    if not ref and _ref.startswith("#"):
        dbgprint(dbg, "'local anchor' current '{}' _ref '{}", current, _ref,
                 fn=str.format)
        return current, current + _ref


    # raise an error because we wont' handle external links here
    if ref.startswith("http") or ref.startswith("www") or ".com/" in ref:
        err = string.format("ref: {}, current: {}".format(ref, current))
        raise ExternalLinkError(err)

    # should be a root / core relative path
    # someone below will handle it if we just replace the relative path
    if ref.startswith(".."):
        count = ref.count("..")
        pat = "/".join([".." for i in range(count)])
        rel = ref.replace(pat, "")
        base = current.replace("/pathfinderRPG/prd/", "").split("/")[:-1]
        base = [v for v in base if v][:(count * -1)]

        # is it a core page?
        if len(base) == 0:
            dbgprint(dbg, "('{}'[] >> '?')", pat, fn=str.format, end=" ")
            ret_url, ret_anchor = _stdref_core_page(_ref, anchor, rel, dbg)
            if ret_url:
                return ret_url, ret_anchor and "#".join([ret_url, ret_anchor]) or ret_url
        else:
            base.append("fake_page.html")
            rel_cur = "/".join(base)
            dbgprint(dbg, "('{}'[] >> '{}')", pat, rel_cur,
                     fn=str.format, end=" ")
            ret_url, ret_anchor = _stdref_current_folder(
                _ref, anchor, rel, dbg, current=rel_cur)
            if ret_url:
                return ret_url, ret_anchor and "#".join([ret_url, ret_anchor]) or ret_url

    if ".." in ref:
        splitted = current.replace("/pathfinderRPG/prd", "")
        if splitted.startswith("/"):
            splitted.replace("/", "", 1)

        splitted = splitted.split("/")
        if splitted[-1].endswith(".html"):
            splitted.pop()
        dbgprint(dbg, "current level: {}, double_dots count {}",
                 len(splitted), ref.count(".."),
                 fn = str.format)
        double_dots = "/".join(splitted).count("..")
        clean = [x for x in splitted if x != ".."]
        # should be a root / core path
        # someone below will handle it if we just replace the relative path
        if double_dots == len(splitted):
            ref = ref.replace("../", "")
        # maybe we could find this relative path
        # elif ouble_dots < len(splitted):
        else:
            # splitted = splitted[:double_dots * -1]
            err = ("""relative paths ("..") not implemented. """
                   """ref: "{}", current: "{}" """.format(
                        ref, current))
            raise NotImplementedError(err)

    if ref.startswith("./"):
        test_cur = current.replace(".html", "").replace("/", ".").split(
            ".")
        if len(test_cur) > 1:
            test_cur = test_cur[:-1]
            test_ref = ref.replace("./", "").replace("/", ".").split(
                ".")
            guess = ".".join(test_cur + test_ref).replace(".html", "")
            html = guess.replace(".", "/") + ".html".replace("//", "/")
            dbgprint(dbg,
                     "Guess for ref starting with '.' ('{}'->{}) = '{}'",
                     ref, guess, html,
                     fn=str.format, end=" ")
            if test_get_page(html, dbg):
                return html, anchor and "#".join([html, anchor]) or html

    if ref.startswith("."):
        ref = ref.replace(".", "", 1)


    if ref.startswith("pathfinderRPG/prd/"):
        test = ref.replace("pathfinderRPG/prd/", "").split("/")
        print("test[0]", test[0])

        """
        example:
            was pathfinderRPG/prd/feats.html
            is now feats.html
        """
        if len(test) == 1:
            file_base = test[0].replace(".html", "")
            dbgprint(dbg, "file_base", file_base)
            if file_base in CORE_PAGES:
                alt_url = "/pathfinderRPG/prd/coreRulebook/" + test[0]
                if test_get_page(alt_url, dbg):
                    return alt_url, anchor and "#".join([alt_url, anchor]) or alt_url

            err = "Invalid ref: '{}' (_ref: '{}')".format(ref, _ref)
            raise ValueError(err)

        # skills/perception.html
        elif len(test) == 2:
            file_base = test[0]
            dbgprint(dbg, "file_base", file_base)
            if file_base.lower() in VALID_SRC:
                alt_url = "/" + ref
                if test_get_page(alt_url, dbg):
                    return alt_url, anchor and "#".join([alt_url, anchor]) or alt_url

            elif file_base in CORE_PAGES:
                ref = "/pathfinderRPG/prd/coreRulebook/" + "/".join(test)
                return ref, anchor and "#".join([ref, anchor]) or ref

            else:
                err = "Invalid ref: '{}'' (_ref: '{}'')".format(ref, _ref)
                raise ValueError(err)

        elif test[0] not in VALID_SRC:
            err = "Invalid href: {} (processed: {})".format(_ref, ref)
            raise ValueError(err)
        else:
            ref = "/" + ref
            return ref, anchor and "#".join([ref, anchor]) or ref

    # dangling page
    if "/" not in ref and len(ref.split("/")) == 1:
        base = current.replace("/pathfinderRPG/prd/", "").split("/")[:-1]
        base = "/".join(base)
        path = os.path.join(base, ref).replace("\\", "/")
        alt_url = ("/pathfinderRPG/prd/" + path).replace("//", "/")
        dbgprint(dbg,
            "'dangling page' "
            "(guess: '{}', _ref: '{}' -> ref: '{}', base '{}'')",
            alt_url, _ref, ref, base,
            fn=str.format, end=" ")
        if test_get_page(alt_url, dbg):
            return alt_url, anchor and "#".join([alt_url, anchor]) or alt_url

    # local subpage of parent
    ret_url, ret_anchor = _stdref_current_folder(_ref, anchor, ref, dbg)
    if ret_url:
        return ret_url, ret_anchor and "#".join([ret_url, ret_anchor]) or ret_url

    # is it a core page, after all?
    ret_url, ret_anchor = _stdref_core_page(_ref, anchor, ref, dbg)
    if ret_url:
        return ret_url, ret_anchor and "#".join([ret_url, ret_anchor]) or ret_url

    if _ref.startswith("<a href"):
        e = HtmlFormatError(_ref)
        e._original_msg = _ref
        raise e

    # a common error is to use /pathfinderRPG/ instead of /pathfinderRPG/prd/
    if "prd" not in ref:
        alt_url = ref.replace("/pathfinderRPG/", "/pathfinderRPG/prd/")
        dbgprint(dbg,
            "'missing /prd/' "
            "(guess: '{}', _ref: '{}' -> ref: '{}')",
            alt_url, _ref, ref,
            fn=str.format, end=" ")
        if test_get_page(alt_url, dbg):
            return alt_url, anchor and "#".join([alt_url, anchor]) or alt_url


    # manual fixes for typos and really broken things
    if "#" in _ref:
        alt_url, alt_anchor = _ref.split("#")
    else:
        alt_url, alt_anchor = _ref, ""
    alt_url = prd_fixes.url.get(alt_url, None)
    if alt_url is not None:
        dbgprint(dbg,
            "'patched url' "
            "(guess: '{}', _ref: '{}' -> ref: '{}'')",
            alt_url, _ref, ref,
            fn=str.format, end=" ")
        if test_get_page(alt_url, dbg):
            return alt_url, alt_anchor and "#".join([alt_url, alt_anchor]) or alt_url


    err = "href: '{}' (processed: '{}'), current: '{}'".format(
        _ref, ref, current)



    raise NotImplementedError("Shouldn't reach end. " + err)


def standard_ref(_ref, current=None):
    current = current or PARSER.current

    ref = anchor = ""
    if "#" in _ref:
        anchor_split = _ref.split("#")
        ref = anchor_split[0]
        anchor = anchor_split[1]
    else:
        ref = _ref

    ref = ref.strip()

    if ref.startswith("bestiary/"):
        ref = "/pathfinderRPG/prd/" + ref
    elif ref.startswith("/prd/spells"):
        ref = "/pathfinderRPG" + ref.replace("/prd/", "/prd/coreRulebook/")
    elif ref.startswith("/pathfinder/prd"):
        ref = ref.replace("/pathfinder/prd", "/pathfinderRPG/prd")
    elif ref.startswith("https://paizo.com"):
        ref = ref.replace("https://paizo.com", "")
    elif ref.startswith("/prd/"):
        ref = ref.replace("/prd/", "/pathfinderRPG/prd/")

    if not ref and anchor:
        retval, _ = _standard_ref(_ref, anchor, ref)
    else:
        if ref not in PARSER.cache_test:
            std_ref, anchor_ref = _standard_ref(_ref, anchor, ref)
            try:
                check_link(std_ref)
            except InvalidLinkError as e:
                err_msg = (
                    "Invalid link "
                    "(std_ref: '{}', ref: '{}', _ref: '{}', current: '{}'".format(
                        std_ref, ref, _ref, current))
                e.change_custom_msg(err_msg)
                raise e
            try:
                assert(anchor_ref.count("#") <= 1 and
                       anchor_ref.startswith(std_ref) and
                       "/#" not in anchor_ref
                )
            except AssertionError as e:
                    dbgprint(0, "Debug information (Invalid link): std_ref: "
                             "'{}', anchor_ref: '{}', ref: '{}'",
                             std_ref, anchor_ref, ref, fn=str.format)
                    raise e

            PARSER.cache_test[ref] = std_ref

        retval = PARSER.cache_test[ref]

    std_anchor = anchor

    if std_anchor:
        std_anchor = standard_anchor_ref(anchor)

        try:
            assert(VALID_ANCHOR.match(std_anchor))
        except AssertionError as e:
                dbgprint(0, "Debug information (Invalid link): retval: "
                         "'{}', std_anchor: '{}', ref: '{}', _ref: '{}",
                         retval, std_anchor, ref, _ref, fn=str.format)
                raise e


    return retval, std_anchor and "#".join([retval, std_anchor]) or retval


def skip_link(url, ignore_locals=True):
    lower = url.lower()
    if (
        not url or
        lower == "/pathfinderrpg" or
        lower == "updates.html" or
        lower == '/pathfinderrpg/prd' or
        # do not retrieve local links for 'get_links'
        (ignore_locals and lower.startswith("#")) or
        lower.startswith("/pathfindersociety") or
        lower.startswith("/paizocon") or
        lower.startswith("/store") or
        lower.startswith("/pathfinderrpg/products") or
        lower.startswith("/products") or
        lower.startswith("/pathfinderrpg/resources") or
        "threads/rzs2soys" in lower or
        "messageboards" in lower
    ):
        return True
    return False


def _get_links(url=INDEX, recursive=1):
    xassert(url)
    text = get_page(url)
    soup = get_soup(text)

    links = []
    for ref in soup.findAll('a', href=True):
        href = ref['href']
        if skip_link(href):
            continue
        try:
            std, _ = standard_ref(href, url)
            if not std:
                err = ("Null 'standard_ref' return value "
                       "(href: {}, url: {})".format(href, url))
                raise ValueError(err)
            xassert(std)
            links.append(std)
        except ValueError as e:
            dbgprint(0, "href: '{}', current: '{}'", href, url,
                     fn=str.format)
            raise e
        except HtmlFormatError as e:
            msg = e._original_msg
            err = str.format(
                "Invalid href formatting. "
                "url: '{}', ref: '{}', parent: \n'{}'".format(
                    msg, ref, ref.parent)
            )
            raise HtmlFormatError(err)

    data = set(links)
    if recursive <= 2:
        recursive_sets = [
            _get_links(url, recursive + 1)
            for url in order(list(data))
            if url not in LINK_PAGES_DONE]
        data = data.union(*recursive_sets)
    LINK_PAGES_DONE[url] = True
    return data


def get_links():
    cache_path = os.path.join("html", "urls.txt")
    if os.path.isfile(cache_path):
        with open(cache_path, "r") as f:
            dbgprint(0, "using cached version of '{}'",
                     cache_path,
                     fn=str.format)
            links = f.read().splitlines()
            return links
    else:
        links = _get_links()
        links = list(links)
        for i, link in enumerate(links):
            fix = prd_fixes.url.get(alt_url, None)
            if fix is not None:
                links[i] = fix
        links = set(links)
        with open(cache_path, "w") as f:
            string =  "\n".join(links)
            dbgprint(0, "caching new version of '{}'",
                     cache_path, fn=str.format)
            f.write(string)
        return links


def check_link(link):
    if ("#" in link or "//" in link or ".." in link or
        link.startswith(".") or not "/" in link
    ):
        err_msg = "invalid link: " + link
        e = InvalidLinkError(err_msg)
        e._original_msg = err_msg
        raise e

def check_links(links):
    for link in links:
        check_link(link)
    dbgprint(1, "'check_links': ok")


def get_prd_name(url):
    url = url.split("/pathfinderRPG/prd/")[-1].replace(".html", "").replace(
        "/", ".").lower()

    return url


def get_page(url):
    html = get_prd_name(url)
    if ".." in url or (url != INDEX and url != OGL and
                        html.split(".")[0] not in VALID_SRC):
        raise InvalidLinkError(
            "url ('{}') refers to a invalid source ('{}')".format(
            url, html))

    cache_path = os.path.join("html", html).lower().replace("\\", "/")

    url = "https://paizo.com" + url

    if os.path.isfile(cache_path):
        with codecs.open(cache_path, "r", "utf-8") as f:
            dbgprint(1, "using cached version '{}' for {}",
                     cache_path, url,
                     fn=str.format)
            text = f.read()
    else:
        r = requests.get(url)
        text = r.text
        error = False
        with codecs.open(cache_path, "w", "utf-8") as f:
            dbgprint(1, "caching new version of '{}' ({})",
                     url, html,
                     fn=str.format)
            try:
                f.write(text)
            except UnicodeEncodeError as e:
                error = e
        if error:
            os.remove(cache_path)
            raise(error)

    key = cache_path.split("/")[-1]
    patches = prd_fixes.patches.get(key, None) or []
    if patches:
        dbgprint(0, "'{}': applying {} patch(es)", key, len(patches),
                 fn=str.format)
    patches.extend(prd_fixes.patches.get(True, None))
    for patch in patches:
        text = patch[0](text, *(patch[1:]))

    with codecs.open("html/patched.tmp", "w", "utf-8") as f:
        f.write(text)
    return text
""" ###################
    end of Common utilities
""" ####################


""" ###################
    Custom exceptions
""" ####################
class CustomError(Exception):

    def change_custom_msg(self, msg):
        args = list(self.args)
        args[0] = msg
        self.args = tuple(args)

    def get_custom_msg(self):
        return self.args[0]

class ExternalLinkError(CustomError):
    pass

class InvalidLinkError(CustomError):
    pass

class ManualBreakError(CustomError):
    pass

class HtmlFormatError(CustomError):
    pass

class PageNotFoundOrOfflineError(CustomError):
    pass

class RequestsInterfaceExceptions:

    def __init__(self, requests):
        self.HTTPError = requests.exceptions.HTTPError
        self.PageNotFoundOrOfflineError = PageNotFoundOrOfflineError
""" ###################
    end of Custom exceptions
""" ####################


""" ###################
    html2rst parsing utilities
""" ####################
def has_parent_named(item, names):
    parent = item.parent
    level = 0
    while True:
        if parent.name.lower() in names:
            level += 1
        parent = getattr(parent, "parent", None)
        if not parent:
            return parent, level

def parse_list(ulist, order=False):
    # TODO: climb up to the root and figure this list level
    parent, level = has_parent_named(ulist, ("ul", "ol"))
    level = level + 1

    lst = ["\n"]

    _id = ulist.get("id", None)
    if _id:
        anchor = rst_anchor(_id)
        lst.extend([anchor, ""])


    if ulist.find("ul"):
        raise NotImplementedError("Nested list:\n" + ulist.parent)

    if ulist.get("title", None):
        lst.append("**{}**\n".format(ulist["title"]))

    lis = ulist.find_all("li")

    for i, li in enumerate(lis):
        parse_soup_member(li)
        bullet = BULLETS[level]
        start = order and "# " or "{} ".format(BULLETS[level])
        text = flatten(li).replace("\n", " ")
        lst.append((("  " * (level - 1)) + start) + text + "\n")

    lst.append("\n")

    return "\n".join(lst)

def process_subdivided_tables(soup ):
    theads = [thead.extract() for thead in soup.find_all("thead")]
    tbodys = [tbody.extract() for tbody in soup.find_all("tbody")]

    tables = []
    caption = soup.find("caption")
    caption = caption and caption.extract() or caption
    tfoots = [tfoot.extract() for tfoot in soup.find_all("tfoot")]
    for i, (thead, tbody) in enumerate(zip(theads, tbodys)):
        new_t = PARSER.soup.new_tag("table")
        if i == 0 and caption:
            new_t.append(caption)
        new_t.append(thead.extract())
        new_t.append(tbody.extract())
        if i == len(theads) - 1 and tfoots:
            [new_t.append(tfoot) for tfoot in tfoots]

        tables.append(new_t)

    soup.name = "div"
    div = soup
    try:
        assert(len_tags(div) == 0)
    except AssertionError as e:
        dbgprint(0, "\n\nDebug information: \ndiv '{}', \nnew tables:\n'{}'",
                         div, tables, fn=str.format)
        raise e

    dbgprint(0, "'process_subdivided_tables' ({})...", len(tables),
             end=" ", fn=str.format)

    for new_t in tables:
        div.append(new_t)

    return div


def fix_bad_subdivisions(table):
    dbg = 2
    if not dbg:
        dbgprint(dbg, "'fix_bad_subdivisions'...")
    else:
        dbgprint(dbg, "'fix_bad_subdivisions'...", end=" ")
    theads = []
    tbodys = []
    tfoots = []
    trs = []

    # dbgprint(0, "table:\n{}", table.prettify(), fn=str.format)

    while table.find("tr"):
        tr = table.find("tr")
        dbgprint(dbg, "tr:\n{}", tr, fn=str.format)

        parent = tr and tr.parent
        if tr and parent.name == "tfoot":
            tfoots.append(parent.extract())
            continue

        if tr and parent.name == "tbody":
            tbodys.append(parent.extract())
            dbgprint(dbg, "extracted tbody:", tbodys[-1])
            continue

        if tr and parent.name == "thead":
            theads.append(parent.extract())
            dbgprint(dbg, "extracted thead:", theads[-1])
            tr = None

        if tr and tr.find("th"):
            thead = PARSER.soup.new_tag("thead")
            thead.append(tr.extract())
            theads.append(thead)
            dbgprint(dbg, "new thead:", theads[-1])
        elif tr and tr.find("td"):
            trs.append(tr.extract())
            continue

        # last item or new section, join the trs
        if (not tr or (tr and tr.find("th"))) and trs:
            tbody = PARSER.soup.new_tag("tbody")
            [tbody.append(tr) for tr in trs]
            tbodys.append(tbody)
            dbgprint(dbg, "new tbody:", tbodys[-1])
            trs = []
            continue

    dbgprint(0, "theads (#{}):", len(theads), end=" ", fn=str.format)
    dbgprint(0, "tbodys (#{}):", len(tbodys), end=" ", fn=str.format)

    for i, (thead, tbody) in enumerate(zip(theads, tbodys)):
        table.append(thead)
        table.append(tbody)

    dbgprint(dbg, "theads {}, tbodys {}:\n", theads, tbodys, fn=str.format)


def process_progression_tables(table):
    dbgprint(0, "'process_progression_tables'...", end = " ")
    theads = table.find_all("thead")

    trs = table.find("thead").find_all("tr")
    if len(trs) == 1:
        return
    assert(len(trs) == 2)

    progression_table = False
    for row, tr in enumerate(trs):
        for th in tr.find_all("th"):
            colspan = int(th.get("colspan", 0))
            if len_tags(th) > 0:
                parse_soup_member(th)
            lower = flatten(th)
            if not lower:
                th.decompose()
                continue
            lower = lower.lower()
            # print(lower)
            spells = colspan > 2 and (
                "per day" in lower or
                lower == "average party level" or
                lower == "spells known"
            )
            if spells:
                progression_table = True
                assert(row == 0)
                th.decompose()
            elif progression_table and row == 1:
                tmp = th.extract()
                trs[0].append(tmp)

    if progression_table:
        trs[1].decompose()
    else:
        raise NotImplementedError("\nMultiple headers: \n{}".format(table))

def parse_std_table(table):
    dbgprint(0, "'parse_std_table'...", end = " ")

    parent, level = has_parent_named(table, ["blockquote"])
    indent = (3 + level) * " "

    lines = ["\n"]

    table_title = ""
    if table.caption and table.caption.string:
        table_title = " " + table.caption.string.strip()

    foot_lines = []
    tfoots = table.find_all("tfoot")
    tfoot_count = sum([1 for tfoot in tfoots
                       for td in tfoot.find_all("td")])

    tr_count = len(table.find_all("tr"))
    td_count = len(table.find_all("td"))
    th_count = len(table.find_all("th"))


    if tfoot_count == 0 and tr_count == 1:
        replacement = None
        if td_count == 1 and th_count == 0:
            replacement = table.find("td")
        elif td_count == 0 and th_count == 1:
            replacement = table.find("th")

        if replacement:
            dbgprint(0, "replacing one-lined table with blockquote")
            parse_soup_member(replacement)
            replacement = replacement.extract()
            inner_p = PARSER.soup.new_tag("p")
            inner_p.string = flatten(replacement)

            if table_title:
                title = table.caption
                title.name = "b"
                inner_p.string = ": " + inner_p.string.strip()
                inner_p.string.insert_before(title.extract())

            holder_block = PARSER.soup.new_tag("blockquote")
            holder_block.append(inner_p)
            table.insert_after(holder_block)

            return ""

    lines.append(      "\n{}.. list-table::{}\n".format(level * " ",
                                                        table_title))
    lines.append(      "{}:header-rows: 1\n".format(indent))
    stub_cols = table.get("stub_columns", None)
    if stub_cols:
        lines.append(  "{}:stub-columns: {}\n".format(indent, int(stub_cols)))
    if table.parent.name == "center":
        lines.append(  "{}:align: center\n".format(indent))
    elif table.parent.name == "right":
        lines.append(  "{}:align: right\n".format(indent))
    lines.append(      "{}:class: contrast-reading-table\n".format(indent))
    lines.append(      "{}:widths: auto\n\n".format(indent))

    foot_lines = []
    for tfoot in tfoots:
        # dbgprint(0, "tfoot was: '{}'", tfoot, fn=str.format)
        if tfoot.find("tr"):
            for tr in tfoot.find_all("tr"):
                for td in tr.find_all("td"):
                    parse_soup_member(td)
                    foot_lines.append(flatten(td))
        else:
            for td in tfoot.find_all("td"):
                parse_soup_member(td)
                foot_lines.append(flatten(td))
        tfoot.decompose()

    footer = None
    if tfoot_count:
        final_foots = ["\n**Notes:**\n"]
        for foot in foot_lines:
            foot = foot.replace("\n", " ")
            foot = foot.strip()
            if foot.startswith("\* "):
                foot = foot[3:]
            if not foot or foot == " ":
                continue
            foot = foot.replace("  ", " ").strip()
            if not foot.startswith("*"):
                foot = "* " + foot
            foot = foot + "\n"
            final_foots.append(foot)
        footer = ("\n".join(foot for foot in final_foots) +
                  "\n")

    head_count = 0
    row_count = 0
    blank_cell = PARSER.soup.new_tag("td")
    blank_cell.string = "\ "
    head_entries = []
    for tr in table.find_all("tr"):
        # TODO: |br|, :br: not working inside a table cell
        for br in table.find_all("br"):
            br.replace_with(" ")
        # header
        if tr.find("th"):
            head_entries = entries = tr.find_all("th")
            # allow a table without a title for the first column
            if (head_count == 0 and entries[0].string is None and
                    len_tags(entries[0]) == 0):
                entries[0] = blank_cell
            head_count += len(entries)
        # body
        elif tr.find("td"):
            real_entries = tr.find_all("td")
            entries = []
            for entry in real_entries:
                tmp = [entry]
                colspan = int(entry.get("colspan", 1))
                if colspan > 1:
                    if not len_tags(entry) and not entry.string:
                        tmp = [blank_cell]
                    blanks = [blank_cell for i in range(colspan - 1)]
                    tmp.extend(blanks)
                entries.extend(tmp)
            try:
                assert(len(entries) == head_count or (
                       len(entries) == 1 and head_count == 0))
            except AssertionError as e:
                dbgprint(0,
                    "\n\nDebug information: "
                    "len(entries): {}, head_count: {}, head_entries: '{}'"
                    "\nentries: \n'{}' \ntable: \n'{}'",
                    len(entries), head_count, head_entries, entries, table,
                    fn=str.format)
                raise e

            row_count += len(entries)

        [parse_soup_member(entry) for entry in entries
         if not isinstance(entry, (NavigableString, Comment))]
        for i, entry in enumerate(entries):
            try:
                v = flatten(entry)
                assert(v)
                entries[i] = v
            except AssertionError as e:
                dbgprint(0,
                         "\n\nDebug information: entry: '{}' entries '{}', table: \n'{}'",
                         entry, entries, table, fn=str.format)
                raise e
            except NotImplementedError as e:
                dbgprint(0,
                         "\n\nDebug information: entries '{}', table: \n'{}'",
                         entries, table, fn=str.format)
                raise e

        try:
            row = ('{}* - '.format(indent) +
                   ('\n{}  - '.format(indent)).join(entries) + "\n")
        except TypeError as e:
            dbgprint(0,
                     "\n\nDebug information: entries '{}', table: \n'{}'",
                     entries, table, fn=str.format)
            raise e

        lines.append(row)

    if footer:
        lines.append(footer)

    text = "\n" + "".join(lines) + "\n"
    # allow single-lined tables
    if ((row_count == 0 or (row_count != 1 and head_count == 0)) and
        get_prd_name(PARSER.current).lower() not in prd_fixes.exceptions.tables) :

        dbgprint(
                0,
                "\n\nDebug information: table: '{}'"
                "\nprevious_siblings '{}', \nnext_siblings '{}'",
                table,
                [str(v) for v in table.previous_siblings][:2],
                [str(v) for v in table.next_siblings][:2],
                fn=str.format)

        err = ("Null table (len_tags(table) {}), th: {}, td: {}"
               "\n##### Text:\n{}\n##### Soup: {}"
               ).format(len_tags(table), head_count, row_count, text, table,
                        fn=str.format)
        raise HtmlFormatError(err)
    elif get_prd_name(PARSER.current).lower() in prd_fixes.exceptions.tables:
        if head_count == 1 and row_count == 0:
            text = text.replace(':header-rows: 1', ':header-rows: 0')
    return text


def parse_table(table):
    _id = table.get("id", None)
    if _id:
        anchor = rst_anchor(_id)
        del table['id']
        table.insert_before(anchor)

    theads = table.find_all("thead")
    loose_th_rows = sum([1 for tr in table.find_all("tr")
                         if tr.find("th") and
                         tr.parent.name in ("table", "tbody")])
    tbodies = table.find_all("tbody")
    thead_rows = table.find("thead") and table.find("thead").find_all("tr") or []

    dbgprint(0, "\n'parse_table' len(theads): {}, len(tbodies): {}, "
            "loose_th_rows: {}",
        len(theads), len(tbodies), loose_th_rows, fn=str.format, end = " ")
    if len(thead_rows) == 2:
        process_progression_tables(table)
    elif len(theads) == 0 and loose_th_rows == 0:
        pass
    elif len(theads) > 1 and len(theads) == len(tbodies):
        return process_subdivided_tables(table)
    else:
        dbgprint(0, "loose_th_rows: {}", loose_th_rows,
                 fn=str.format, end=" ")
        if (loose_th_rows > 1 or (len(theads) > 1 and len(tbodies) == 0) or
            (len(theads) >= 1 and loose_th_rows >= 1 and len(tbodies) == 0)
        ):
            fix_bad_subdivisions(table)
            return process_subdivided_tables(table)

    # it should be a standard table
    return parse_std_table(table)

def parse_blockquote(soup):
    while soup.find("p"):
        p = soup.find("p")
        text = parse_paragraph(p, indent=1)
        if text:
            p.replace_with(text)
        else:
            p.decompose()
    return "\n".join(["", flatten(soup), ""])

def split_paragraphs(item):
    string = str(item)
    string = string.replace("<br/>", "</p><p>")
    new_soup = BeautifulSoup(string, "lxml")
    ps = [p.extract() for p in new_soup.find_all("p")]
    _class = item.get("class", None)
    if _class:
        for p in ps:
            dbgprint(0, "setting inherited class for paragraph "
                     "'{}' to '{}'",
                     p, _class, fn=str.format)
            p['class'] = _class
    _id = item.get("id", None)
    if _id:
        ps[0]["id"] = _id
    [item.insert_after(p) for p in reversed(ps)]

def parse_paragraph(soup, indent=0):
    """
    if soup.find("br"):
        split_paragraphs(soup)
        return ""
    """

    over_pats = [
        ("stat-block-cr",           ),
    ]

    for override in reversed(soup.find_all("span")):
        _class = tuple(override.get("class", None))
        if _class in over_pats:
            dbgprint(1, "### override", override)
            parse_soup_member(override)
            override.replace_with(flatten(override))

    exclusions = [
        "td", # rogue tds inside paragraphs, go figure...
        "big"
    ]

    for exclusion in exclusions:
        for item in reversed(soup.find_all(exclusion)):
            parse_soup_member(item)
            text = flatten(item)
            item.replace_with(text)

    try:
        text = flatten(soup)
        text = "\n\n".join(
            [((" " * indent) + line) for line in text.splitlines()]
        )
        """
        if "\n" in text:
            dbgprint(0, "has newline", text)
        """
    except (TypeError, AttributeError) as e:
        dbgprint(0, "\n\nDebug information: paragraph \n'{}'",
            soup, fn=str.format)
        raise e

    _id = soup.get("id", None)
    if _id:
        anchor = rst_anchor(_id)
        return "\n".join(["", anchor, "", text])

    return text

def rst_page_anchor():
    ref_base = PARSER.current.replace("/pathfinderRPG/prd/", "").replace("/", ".").replace(".html", "").lower().split("#")[0]
    return "\n.. _`{}`:\n".format(ref_base)

def standard_anchor_ref(anchor):
    anchor = anchor.lower().replace(" ", "_").replace("-", "_").replace(",", "").replace("'", "").replace("__", "_")
    anchor = list(anchor.strip())
    if anchor[0] == "_":
        anchor = anchor[1:]
    if anchor[-1] == "_":
        anchor = anchor[:-1]
    anchor = "".join(anchor)
    return anchor

def rst_anchor(title_text, target=None):
    ref_base = PARSER.current.replace("/pathfinderRPG/prd/", "").replace("/", ".").replace(".html", "").lower().split("#")[0]
    clean_text = standard_anchor_ref(title_text)
    label = "#".join([ref_base, clean_text])

    # build an alias
    if target is None:
        return "\n.. _`{}`:".format(label)
    else:
        clean_target = standard_anchor_ref(target)
        clean_target = "#".join([ref_base, clean_target])
        """
        print("rst_anchor label '{}' clean_target '{}'".format(
            label, clean_target))
        """
        if label != clean_target:
            res = "\n.. _`{}`: `{}`_".format(label, clean_target)
            return res
        else:
            return ""
"""
def post_process_headers():

    pat = re.compile("^{% *"
                       "[level=(?P<level>\d+)]"
                       "[length=(?P<length>\d+)]"
                       " *%}$")
    table = {}
    for i, line in enumerate(lines):
        if line.startswith("{%") and line.endswith("%}"):
            match = pat.match(line)
            if match:
                level = match.group("level")
                length = match.group("length")
                table.setdefault(level, [])
                table[level].append({
                    "line_number": i,
                    "length": length
                })

    for i, level_data in enumerate(sorted(list(table.keys()))):
        for t in level_data:
            length = t["length"]
            line_number = t["line_number"]
            lines[line_number] = HEADERS[i + 1] *



def get_header_placeholder(level, length):

    return "{%" + "[level={}][length={}]".format(level, length) + "%}"

"""

def parse_header(title, i):
    symbol = HEADERS[i]

    lines = []

    html_id = title.get("id", None)

    # cleanup header
    for tag in ["a", "strong", "b", "em", "span"]:
        for each in reversed(title.find_all(tag)):
            try:
                each.replace_with(flatten(each))
            except ValueError as e:
                dbgprint(0, "\n\nDebug information: item '{}' parent: \n{}",
                    each, each.parent, fn=str.format)
                raise e

    text = flatten(title)
    if not text:
        return None
    else:
        text = text.replace("\t", " ").replace("  ", " ").strip()
    try:
        underline = symbol * (len(text) + 1)
    except TypeError as e:

        dbgprint(0, "TypeError for title level {} \n{}",
                 i, title.parent, fn=str.format)
        raise e

    # get the title-based anchor
    rst_ref = rst_anchor(text)

    # if there was an id, we also anchor from it (towards the title-based one)
    if html_id:
        # print("html_id", html_id, "text", text)
        anchor = rst_anchor(html_id, target=text)
        lines.extend([anchor, ""])
    lines.extend([rst_ref, "", text, underline])

    return "\n".join(lines)


def _parse_href_local(ref, text):
    ref = ref.replace("/pathfinderRPG/prd/", "").replace("/", ".").replace(
        ".html", "").lower()
    if "*" in text:
        text = text.replace("\ *", "").replace("*", "")
    return ":ref:`{} <{}>`\ ".format(text.replace("\ ``*``", ""), ref)


def parse_href(href):
    """
    #`Python <https://www.python.org/>`_

    <a href="/pathfinderRPG/prd/advancedPlayersGuide/baseClasses/summoner.html#summon-monster-i">

    data = {link['href']
            for link in soup.findAll('a', attrs={'href': re_str})}
    """

    anchor_ref = None
    try:
        ref = href['href']
    except KeyError as e:
        return href.string
    if skip_link(ref, ignore_locals=False):
        return href.string

    if ref in prd_fixes.url_with_anchor:
        _ref = ref
        ref = prd_fixes.url_with_anchor[ref]
        # print(_ref, ">>", ref)

    ref = ref.replace("-", "_").replace("#_", "#")

    try:
        _, anchor_ref = standard_ref(ref)
    except (NotImplementedError) as e:
        """
        Even if a local anchor is not considered a standard page referenc (for
        link-scrapper-related functions), when parsing html -> rst we should
        consider it.
        """
        if ref.startswith("#"):
            _, anchor_ref = standard_ref(PARSER.current + ref)
        else:
            raise e
    finally:
        if anchor_ref is None:
            dbgprint(0, "\n\nDebug information: href: '{}'", href, fn=str.format)

    try:
        err = "Anchor not set"
        assert(anchor_ref)
        err = "Invalid ref"
        assert(not anchor_ref.endswith("#"))
        assert("/#" not in anchor_ref)
    except AssertionError as e:
        dbgprint(0, "\n\nDebug information ({}): "
                 "href: '{}' >> anchor_ref: '{}'",
                 err, href, anchor_ref, fn=str.format)

    # dbgprint(0, "anchor_ref", anchor_ref)
    text = flatten(href)
    try:
        retval = _parse_href_local(anchor_ref, text)
    except AttributeError as e:
        dbgprint(0, "\n\nDebug information: "
                 "href: '{}' >> anchor_ref: '{}', text '{}",
                 href, anchor_ref, text, fn=str.format)
        raise e

    return retval


def len_tags(soup):
    return len([c for c in soup.descendants if c.name])


def flatten(soup):
    if isinstance(soup, (NavigableString, Comment)):
        return soup

    tags = len_tags(soup)
    # some tags were not parsed/replaced
    if tags > 0:
        err = "# contents {}, # tags {}, file: {}, text:\n{}".format(
            len(soup.contents),
            tags,
            PARSER.current,
            soup.prettify()
            )
        raise NotImplementedError(err)
    # plain strings should be joined
    elif len(soup.contents) > 1:
        string = "".join([c.string for c in soup.descendants])
        return string
    # single string
    else:
        return soup.string


def correct_html_symbols(rst):
    return rst

def parse_bestiary_stat_block_title(subtitle):
    cr_text = None
    text = None
    cr = subtitle.find("span", {"class": "stat-block-cr"})
    if cr:
        cr_text = "\n**{}** ".format(flatten(cr).strip())
        cr.decompose()

    text = parse_header(subtitle, 3)

    lines = [v for v in (text, cr_text) if v]

    rst_title = "\n".join(lines)

    subtitle.replace_with(rst_title)


def parse_bestiary_entry(soup):
    dbgprint(1, 'parse_bestiary_entry')
    def not_h1(tag):
        return tag.name != "h1"

    headers = soup.find_all("h1", {'class': 'monster-header'})
    for header in headers:
        header.replace_with(parse_header(header, 2))

    #<p class="stat-block-title"><b>Cheetah <span class="stat-block-cr">CR 2</span></b></p>
    subtitles = soup.find_all("p", {'class': 'stat-block-title'})
    for subtitle in subtitles:
        parse_bestiary_stat_block_title(subtitle)

    #<p class="stat-block-breaker">Defense</p>
    breakers = soup.find_all("p", {'class': 'stat-block-breaker'})
    for breaker in breakers:
        b = breaker.find("b")
        if b:
            b.replace_with(b.string)
        breaker.replace_with(parse_header(breaker, 3))

    while soup.find("p", {'class': "stat-block-2"}):
        item = list(reversed(soup.find_all("p", {'class': "stat-block-2"})))[-1]
        parse_soup_member(item)
        item.replace_with(parse_paragraph(item, indent=1))

def parse_format(fmt, str_mask, name=None):
    fmt.name = name or fmt.name
    if len_tags(fmt) > 0:
        href = fmt.find("a", {"href": True})
        parse_soup_member(fmt)
        if href:
            fmt.replace_with(flatten(fmt))
            return

    parent = fmt.parent
    string = flatten(fmt)
    if string == " ":
        fmt.replace_with(" ")
        return
    elif not string:
        fmt.decompose()
        return
    try:
        parent.name
    except AttributeError as e:
        dbgprint(
                0,
                "\n\nDebug information: fmt: '{}'"
                "\nprevious_siblings '{}', \nnext_siblings '{}'",
                fmt,
                [str(v) for v in fmt.previous_siblings][:2],
                [str(v) for v in fmt.next_siblings][:2],
                fn=str.format)
        raise e
    if parent.name.lower() in ("a", "b", "strong", "i", "em") or not string:
        new_text = string
    else:
        new_text = str_mask.format(string.strip())
    fmt.replace_with(new_text or "")

def parse_bold(b):
    parse_format(b, "\ **{}**\ ")

def parse_italic(i):
    parse_format(i, "\ *{}*\ ")

def parse_soup_member(soup):
    check_for_and_parse_bestiary_entries(soup)
    parse_all_tables(soup)
    parse_all_ulists(soup)
    parse_all_olists(soup)
    parse_all_titles(soup)
    parse_all_italics(soup)
    parse_all_superscripts(soup)
    parse_all_linebreaks(soup)
    parse_all_bolds(soup)
    parse_all_hrefs(soup)
    parse_all_blockquotes(soup)
    parse_all_paragraphs(soup)
    parse_ignored(soup)

def check_for_and_parse_bestiary_entries(soup):
    #bestiary entries need special treatment
    try:
        if (soup.find_all("h1", {'class': 'monster-header'}) or
            soup.find_all("p", {'class': 'stat-block-title'})
        ):
            parse_bestiary_entry(soup)
    except AttributeError as e:
        dbgprint(0, "\n\nDebug information: '{}'".format(soup))
        raise e

def parse_all_tables(soup):
    iterations = 0
    # while is required because new tables are created from subdivisions
    while soup.find("table"):
        table = soup.find("table")
        table.replace_with(parse_table(table))
        iterations += 1
        if iterations > 100:
            err = "Stuck on the loop, table: \n{}".format(table)
            raise NotImplementedError(err)
        if not soup.find("table"):
            dbgprint(0, "done parsing tables")

def parse_all_ulists(soup):
    ulists = soup.find_all("ul")
    for ulist in reversed(ulists):
        ulist.replace_with(parse_list(ulist))

def parse_all_olists(soup):
    olists = soup.find_all("ol")
    for olist in reversed(olists):
        olist.replace_with(parse_list(olist, order=True))

def parse_all_titles(soup):
    for i in range(1, 6 + 1):
        tag = "h%d" % i
        titles = soup.find_all(tag)
        for title in titles:
            text = parse_header(title, i)
            if text is None:
                title.decompose()
            else:
                title.replace_with(text)

def parse_all_italics(soup):
    italics = soup.find_all("i")
    italics.extend(soup.find_all("em"))
    for italic in reversed(italics):
        parse_italic(italic)

def parse_all_superscripts(soup):
    # superscript
    sups = soup.find_all("sup")
    for sup in sups:
        left = right = ""
        string = sup.string
        if not string:
            sup.decompose()
            continue

        if string.startswith(" "):
            left = " "
        if string.endswith(" "):
            right = " "
        if string.strip():
            sup.replace_with(
                left +
                "\ :sup:`{}`\ ".format(string.strip()) +
                right)
        else:
            sup.replace_with(
                left +
                right)

def parse_all_linebreaks(soup):
    for linebreak in soup.find_all('br'):
        linebreak.replace_with("\n")

def parse_all_bolds(soup):
    bolds = soup.find_all("b")
    bolds.extend(soup.find_all("strong"))
    for bold in reversed(bolds):
        parse_bold(bold)

def parse_all_hrefs(soup):
    for href in soup.find_all("a"):
        # if it has a nested buggy href
        if href.find("a", {"href": True}):
            parent_ref = href.get("href", None)
            nested = href.find("a", {"href": True})
            nested_ref = nested.get("href", None)
            # if they have the same target
            if not href.string and nested.string and parent_ref == nested_ref:
                href.replace_with(nested)
                continue
        if len_tags(href) > 0:
            parse_soup_member(href)

        has_url = href.get("href", False)
        if not has_url:
            if href.string:
                href.replace_with(href.string)
            else:
                href.decompose()
            continue
        try:
            href.replace_with(parse_href(href))
        except ValueError as e:
            dbgprint(
                    0,
                    "\n\nDebug information: href: '{}'"
                    "\nprevious_siblings '{}', \nnext_siblings '{}'",
                    href,
                    [str(v) for v in href.previous_siblings][:2],
                    [str(v) for v in href.next_siblings][:2],
                    fn=str.format)
            raise e

def parse_all_blockquotes(soup):
    for nested in reversed(soup.find_all("blockquote")):
        replace = parse_blockquote(nested)
        if replace is not None:
            nested.replace_with(replace)
        else:
            nested.decompose()

def parse_all_paragraphs(soup):
    # while is required because new paragraphs are created from subdivisions
    while soup.find("p"):
        nested = list(reversed(soup.find_all("p")))[-1]
        try:
            replace = parse_paragraph(nested)
        except TypeError as e:
            print(nested.previ)
            dbgprint(0, "\n\nDebug information: \nprevious_siblings '{}', \nnext_siblings '{}'",
                [str(v) for v in nested.previous_siblings][:2],
                [str(v) for v in nested.next_siblings][:2],
                fn=str.format)
            raise e

        if replace is not None:
            nested.replace_with(replace)
        else:
            nested.decompose()

def parse_ignored(soup):
    ignored_tags = ["center", "big", "nobr", "span", "div"]
    for tag in ignored_tags:
        for nested in reversed(soup.find_all(tag)):
            if len_tags(nested) > 0:
                parse_soup_member(nested)
            flat = flatten(nested)
            if flat:
                nested.replace_with(flat)
            else:
                nested.decompose()

def get_soup(text):
    return BeautifulSoup(text, "lxml")

def create_index():
    if not os.path.isfile("index.rst"):
        import prd_index
        prd_index.main()
    # should preserve mod time so that we don't trigger Sphinx without changes
    shutil.copy2("index.rst", "rst/index.rst")

def remove_comments(soup):
    comments = soup.find_all(string=lambda text:isinstance(text,Comment))
    for c in comments:
        c.extract()

class Html2Rst(object):

    def __init__(self):
        self.cache_test = {}

    def _parse_rst(self, html):
        self.soup = soup = BeautifulSoup(html, "lxml")
        remove_comments(soup)

        soup = soup.find("div", {"class": "body-content"})
        soup = soup.find("div", {"class": "body"})

        # it would be good to sort from the higher to the lowest level tags
        ids = [
            ("div",     {"class": "nav-menu"},                      None),
            ("link",    None,                                       None),
            ("div",     {"class": "footer"},                        None),
            ("div",     {"class": "header"},                        None),
            ("div",     {"id": "menu-bestiary"},                    None),
            ("div",     {"id": "menu-feats"},                       None),
            ("div",     {"id": "menu-spelllist"},                   None),
            ("script",  None,                                       None),
            ("p",       {"class": "shortcut-bar"},                 "input"),
            ("table",   {"id": "spell-areas"},                      "img"),
            ("table",   {"id": "figure-chases"},                    "img"),
            ("div",     {"id": "figure-tactical-movement"},         "img"),
            ("div",     {"id": "attacks-of-opportunity-diagram"},   "img"),
            ("div",     {"id": "figure-cover"},                     "img"),
            ("div",     {"id": "figure-flanking"},                  "img"),
            ("div",     {"id": "spell-areas"},                      "img")
       ]
        for (tag, tag_id, field) in ids:
            if tag_id is None:
                exclusions = reversed(soup.find_all(tag))
            else:
                exclusions = reversed(soup.find_all(tag, tag_id))

            for exclusion in exclusions:
                if field is None or exclusion.find(field):
                    #annihilate_soup(exclusion)
                    exclusion.decompose()

        #<span class="char-style-override-25">×</span>
        over_pats = [
            ("_5yl5",                       ),
            ("CharOverride-4",              ),
            ("CharOverride-5",              ),
            ("charoverride-10",             ),
            ("charoverride-11",             ),
            ("charoverride-14",             ),
            ("charoverride-15",             ),
            ("charoverride-17",             ),
            ("charoverride-22",             ),
            ("charoverride-23",             ),
            ("char-style-override-8",       ),
            ("char-style-override-9",       ),
            ("char-style-override-10",      ),
            ("char-style-override-11",      ),
            ("char-style-override-12",      ),
            ("char-style-override-14",      ),
            ("hyperlink",                   "char-style-override-14"),
            ("char-style-override-15",      ),
            ("hyperlink",                   "char-style-override-15"),
            ("char-style-override-16",      ),
            ("hyperlink",                   "char-style-override-18"),
            ("char-style-override-20",      ),
            ("Stat-Block-Breaker-Char",     "char-style-override-20"),
            ("char-style-override-23",      ),
            ("hyperlink",                   "char-style-override-23"),
            ("char-style-override-24",      ),
            ("char-style-override-25",      ),
            ("char-style-override-27",      ),
            ("char-style-override-29",      ),
            ("char-style-override-30",      ),
            ("char-style-override-31",      ),
            ("char-style-override-33",      ),
            ("char-style-override-34",      ),
            ("hyperlink",                   "char-style-override-34"),
            ("char-style-override-37",      ),
            ("hyperlink",                   "char-style-override-39"),
            ("char-style-override-38",      ),
            ("char-style-override-39",      ),
            ("char-style-override-40",      ),
            ("char-style-override-41",      ),
            ("char-style-override-45",      ),
            ("char-style-override-47",      ),
            ("char-style-override-51",      ),
            ("char-style-override-51",      ),
            ("char-style-override-69",      ),
            ("char-style-override-79",      ),
            ("char-style-override-86",      ),
            ("char-style-override-87",      ),
            ("char-style-override-92",      ),
            ("char-style-override-93",      ),
            ("body-copy-indent-char",       ),
            ("body-copy-char",              ),
            ("body-copy-char",              "italics"),
            ("hyperlink-1",                 ),
            ("superscript0",                ),
            ("stat-block-rp",               ),
            ("stat-block-1-char",           ),
            ("stat-block-1-char",           "italics"),
            ("comment-reference",           ),
            ("grame",                       ),
            ("stat-description-char",       ),
            ("nowrap",                      )
        ]

        for override in reversed(soup.find_all("span")):
            _class = override.get("class", None)
            if not _class:
                continue
            _class = tuple(_class)
            if _class in over_pats:
                dbgprint(1, "### override", override)
                try:
                    parse_soup_member(override)
                    flat = flatten(override)
                    if not flat:
                        override.decompose()
                    else:
                        override.replace_with(flat)
                except ValueError as e:
                    dbgprint(
                        0,
                        "\n\nDebug information: "
                        "override: '{}', len_tags: {}",
                        override, len_tags(override),
                        fn=str.format)
                    raise e

        parse_soup_member(soup)

        rst = [rst_page_anchor(), ""]
        if "opengamelicense" not in PARSER.current.lower():
            rst.extend([".. contents:: \ ", ""])

        for child in soup.descendants:
            try:
                assert(isinstance(child, (NavigableString, Comment)))
            except AssertionError as e:
                dbgprint(0, "\n\nDebug information: "
                    "child : {} ({}), "
                    "\nprevious_siblings '{}', \nnext_siblings '{}'",
                    child, type(child),
                    [str(v) for v in child.previous_siblings][:4],
                    [str(v) for v in child.next_siblings][:4],
                    fn=str.format)
                raise e
            for old, new in TRADEMARKS.items():
                text = child.replace(old, new)
            rst.append(text)

        rst = "\n".join(rst)
        rst = rst.splitlines()

        previous_refs = {}
        repeated_refs = []
        for i, line in enumerate(rst):
            # if a anchor to a line
            if line.startswith('.. _') and line.endswith('`:'):
                if line in previous_refs:
                    repeated_refs.append(i)
                else:
                    previous_refs[line] = True
            elif not line.startswith('..') and line.endswith(r"\ "):
                line = line[:-2]
                pass

            rst[i] = line

        for repeated in reversed(repeated_refs):
            rst.pop(repeated)

        rst = "\n".join(rst)
        rst = correct_html_symbols(rst)
        """
        """
        while "\n\n\n" in rst:
            rst = rst.replace("\n\n\n", "\n\n")

        return rst

    def parse(self, link):
        rst_path = os.path.join("rst", get_prd_name(link) + ".rst")
        if not OVERWRITE and os.path.isfile(rst_path):
            return
        dbgprint(0, "******", rst_path, "******")
        html = get_page(link)
        self.current = link
        self.current_rst = rst_path
        # raise ManualBreakError()
        rst = self._parse_rst(html)
        # raise ManualBreakError(rst)
        # raise ManualBreakError(rst_path)
        dbgprint(1, rst)
        dbgprint(1, "******", rst_path, "******\n")

        try:
            with open("rst.tmp", "w", encoding='utf-8') as f:
                f.write(rst)
            if (OVERWRITE == "all" or not os.path.isfile(rst_path) or
                not equal_file_hashes("rst.tmp", rst_path)
            ):
                dbgprint(0, "caching new version of '{}'",
                         rst_path,
                         fn=str.format)
                shutil.copy2("rst.tmp", rst_path)
            else:
                dbgprint(0, "no changes were made to '{}'",
                         rst_path,
                         fn=str.format)
        except UnicodeEncodeError as e:
            dbgprint(0, rst)
            dbgprint(0, "removing uncompleted file '{}'",
                     rst_path,
                     fn=str.format)
            err = parse_unicode_encode_error(e, rst)
            dbgprint(0, "buggy", str(rst[46449 - 1:46449 + 30]))
            os.remove(rst_path)
            dbgprint(0, link)
            raise e
        except Exception as e:
            dbgprint(0, rst)
            dbgprint(0, "removing uncompleted file '{}'",
                     rst_path,
                     fn=str.format)
            os.remove(rst_path)
            dbgprint(0, link)
            raise e
        # raise ManualBreakError(rst)
        # raise ManualBreakError(rst_path)

    def parse_all(self):
        global requests
        requests = RequestsInterface()
        try:
            links = get_links()
            check_links(links)

            """
            links = [
                "/pathfinderRPG/prd/bestiary4/golem.html"
            ]
            """

            for link in order(list(links)):
                try:
                    self.parse(link)
                except Exception as e:
                    if HALT_ON_ERROR:
                        dbgprint(0, "current:", self.current)
                        raise e
                    elif os.path.isfile(self.current_rst):
                        dbgprint(0, "removing previous version of failed build: '{}'", self.current_rst, fn=str.format)
                        os.remove(self.current_rst)

        finally:
            requests.close()



def main():
    global PARSER
    PARSER = Html2Rst()
    PARSER.parse_all()
    create_index()


if __name__ == '__main__':
    main()
