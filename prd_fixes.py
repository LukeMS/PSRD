import re

def sub_asterisks(text, *args):
    if "*" in text:
        # add a leading space
        text = re.sub("( *)(?P<main>\*+)", " \g<main>", text)
        # remove space between asterisks
        text = text.replace("* *", "**")
        # escape them
        text = text.replace("*", "\*")
    return text


def remove_lines(text, *args):
    lines = [line for line in text.splitlines()]
    exclusions = []
    [exclusions.extend(list(range(rng[0] - 1, rng[1]))) for rng in args]
    lines = [line for i, line in enumerate(lines) if i not in exclusions]
    return "\n".join(lines)

def issue_warnings(text, halt_on_error=False, *args):
    lines = [line for line in text.splitlines()]

    # upc = Unexpected Paragraph Closings
    upc = re.compile(
        "(?P<text>.+</p>[^\n]+)", re.IGNORECASE)

    # ecm = Empty Cell at Middle
    ecm = re.compile(
        "(?P<text>.+</td><td>(</td>|</tr>).+)", re.IGNORECASE)

    # ehm = Empty Header at Middle
    ehm = re.compile(
        "(?P<text>.+</th><th>(</th>|</tr>).+)", re.IGNORECASE)

    # UnClosed Table
    uct = re.compile(
        "(?P<text>.+(</td>|</tr>)(<table>|<thead>|<tbody>).*)", re.IGNORECASE)

    #UnClosed Header
    uch_open = re.compile(
        ".*(<h\d>).*", re.IGNORECASE)
    uch_close = re.compile(
        ".*(</h\d>).*", re.IGNORECASE)

    # Double Header Table
    dbt = re.compile(
        "(?P<text>.+th +colspan.+)", re.IGNORECASE)

    # Rogue Cell in Paragraph
    rcp = re.compile(
        "^\s*(?P<text><p.+</?td>.+)", re.IGNORECASE)

    errors = 0

    for i, line in enumerate(lines):
        upc_search = upc.search(line)
        if upc_search and not re.search("<br */? *> *$", line):
            print("§§§ Unexpected paragraph closing at line (line {}): '{}".format(
                i + 1, upc_search.group("text")))
            errors += 1

        ehm_search = ehm.search(line)
        if ehm_search:
            print("§§§ Unexpected empty header cell not at row start (line {}): '{}".format(
                i + 1, ehm_search.group("text")))
            errors += 1

        ecm_search = ecm.search(line)
        if ecm_search:
            print("§§§ Unexpected empty cell not at row start (line {}): '{}".format(
                i + 1, ecm_search.group("text")))
            errors += 1

        uct_search = uct.search(line)
        if uct_search:
            print("§§§ Unclosed table (line {}): '{}".format(
                i + 1, uct_search.group("text")))
            errors += 1

        dbt_search = dbt.search(line)
        if dbt_search:
            print("§§§ Double Header (unpatched) Table (line {}): '{}".format(
                i + 1, dbt_search.group("text")))
            errors += 1

        rcp_search = rcp.search(line)
        if rcp_search:
            print("§§§ Rogue Cell in Paragraph (line {}): '{}".format(
                i + 1, rcp_search.group("text")))
            errors += 1

        uch_open_search = uch_open.search(line)
        uch_close_search = uch_close.search(line)
        if uch_open_search and not uch_close_search:
            print("§§§ Header missing closure (line {}): '{}".format(
                i + 1, line))
            errors += 1
    if halt_on_error and errors:
        raise ValueError("Errors were found while analyzing the file. This is happening because the 'halt_on_error' parameter was set to True.")
    return text

def remove_indentation(text, *args):
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(lines)

def remove_empty_lines(text, *args):
    lines = [line.strip() for line in text.splitlines() if line]
    return "\n".join(lines)

def fix_nonclosing_consecutive_tags(text, tag, *args):
    """Also fixes blank tags."""
    lines = [line for line in text.splitlines()]
    old_lines = [line for line in lines]
    open_t = "<{}>".format(tag)
    close_t = "</{}>".format(tag)
    blank_a = open_t + "\s*" + close_t
    blank_b = open_t + "\s*" + open_t
    sub_a = re.compile(blank_a, re.IGNORECASE)
    sub_b = re.compile(blank_b, re.IGNORECASE)
    _pat = "(?P<full>(?P<open_t>{})(?P<body>[^<]+)(?P<close_t>{}))".format(
        open_t, open_t)
    pat = re.compile(_pat, re.IGNORECASE)
    fixed = open_t + "{}" + close_t
    mod = []
    for i, line in enumerate(lines):
        while True:
            line = sub_a.sub("", line)
            line = sub_b.sub("", line)
            match = pat.search(line)
            if not match:
                break
            old = match.group('full')
            new = fixed.format(match.group('body'))
            # print("old: '{}'".format(old))
            # print("new: '{}'".format(new))
            line = line.replace(old, new)
            mod.append(i)
        lines[i] = line
    mod = sorted(list(set(mod)))
    """
    for i in mod:
        print(
            ("\n###### old line: \n'{}'"
             "\n###### new line: \n'{}'\n").format(
             old_lines[i],
             lines[i]))
    """

    return "\n".join(lines)



url = {
    "/creatureTypes.html": "/pathfinderRPG/prd/bestiary/creatureTypes.html",
    "/universalMonsterRules.html": "/pathfinderRPG/prd/bestiary/universalMonsterRules.html",

    "/pathfinderRPG/prd/bestiary5/deepMerfolk.html": "/pathfinderRPG/prd/bestiary5/merfolkDeep.html",

    "/pathfinderRPG/prd/bestiary5/muckdweller.html": "/pathfinderRPG/prd/bestiary5/muckdwellers.html",

    "/pathfinderRPG/advancedPlayersGuide/baseClasses/oracle.html": "/pathfinderRPG/prd/advancedPlayersGuide/baseClasses/oracle.html",

    "/pathfinderRPG/prd/mythicAdventures/mythicSpells/pathfinderRPG/mythicAdventures/mythicSpells/gaseousForm.html":
    "/pathfinderRPG/prd/mythicAdventures/mythicSpells/pathfinderRPG/mythicAdventures/mythicSpells/gaseousForm.html",

    "/pathfinderRPG/prd/occultAdventures/spells/synthesia.html":
    "/pathfinderRPG/prd/occultAdventures/spells/synesthesia.html",

    "/pathfinderRPG/prd/coreRulebook/spells/inflightLightWounds.html":
    "/pathfinderRPG/prd/coreRulebook/spells/inflictLightWounds.html",

    "/pathfinderRPG/prd/bestiary2/universalmonsterules.html":
    "/pathfinderRPG/prd/bestiary/universalMonsterRules.html",

    "/pathfinderRPG/prd/unchained/step6.html":
    "/pathfinderRPG/prd/unchained/monsters/step6.html",

    "/pathfinderRPG/prd/unchained/monster/step7.html":
    "/pathfinderRPG/prd/unchained/monsters/step7.html",

    "/pathfinderRPG/prd/monsterCodex/monsterCodex/duergar.html":
    "/pathfinderRPG/prd/monsterCodex/duergar.html",

    "/pathfinderRPG/prd/coreRulebook/bestiary/monsterFeats.html":
    "/pathfinderRPG/prd/bestiary/monsterFeats.html",

    "/pathfinderRPG/prd/unchained/skillsAndOptions/consolidatedSkills/perform.html":
    "/pathfinderRPG/prd/coreRulebook/skills/perform.html",

    "/pathfinderRPG/prd/coreRulebook/spells/bloodyClaws.html":
    "/pathfinderRPG/prd/advancedPlayersGuide/spells/bloodyClaws.html",

    "/pathfinderRPG/prd/monsterCodex/troglodtyes.html":
    "/pathfinderRPG/prd/monsterCodex/troglodytes.html"
}

url_with_anchor = {
    "/pathfinderRPG/prd/ultimateCampaign/characterBackground/storyFeats.html#accursed": "/pathfinderRPG/prd/ultimateCampaign/characterBackground/storyFeats.html#accursed-(story)",
    "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#evasion": "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#evasion-rogue",
    "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#bleeding-attack": "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#rogue-talents-bleeding-attack",
    "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#combat-trick": "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#rogue-talents-combat-trick",
    "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#fast-stealth": "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#rogue-talents-fast-stealth",
    "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#finesse-rogue": "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#rogue-talents-finesse-rogue",
    "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#rogue-crawl": "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#rogue-talents-rogue-crawl",
    "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#slow-reactions": "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#rogue-talents-slow-reactions",
    "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#surprise-attack": "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#rogue-talents-surprise-attack",
    "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#trap-spotter": "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#rogue-talents-trap-spotter",
    "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#weapon-training": "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#rogue-talents-weapon-training",
    "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#opportunist": "/pathfinderRPG/prd/coreRulebook/classes/rogue.html#advanced-talents-opportunist",
}

patches = {
    True: [
        (str.replace,
         "/pathfinderRPG/prd/coreRulebook/bestiary/",
         "/pathfinderRPG/prd/bestiary/"
         ),

        (str.replace,
         "/pathfinderRPG/prd/coreRulebookmagicItems/",
         "/pathfinderRPG/prd/coreRulebook/magicItems/"
         ),

        (str.replace,
         '<td style="white-space: normal;"></td>',
         '<td></td>'
         ),

        (str.replace,
         "</td><td></td><td>",
         "</td><td>&mdash;</td><td>"
         ),

        (str.replace,
         "<thead><th>",
         "<thead><tr><th>"
         ),

        (str.replace,
         "</p><p",
         "</p>\n<p"
         ),

        (str.replace,
         "<p></p>",
         ""
         ),

        (sub_asterisks, None, None),

        (str.replace,
         'http://paizo.com/pathfinderRPG/prd/',
         '/pathfinderRPG/prd/'),

        (str.replace,
         'https://paizo.com/pathfinderRPG/prd/',
         '/pathfinderRPG/prd/'),

        # (issue_warnings, True, None)
    ],


###############################
# ADVANCEDCLASSGUIDE.CLASSES.ARCANIST
###############################
    "advancedclassguide.classes.arcanist": [
        (str.replace,
         '#energy-shield-exploit',
         '#energy-shield')
    ],
###############################
# end of ADVANCEDCLASSGUIDE.CLASSES.ARCANIST
###############################


###############################
# ADVANCEDCLASSGUIDE.CLASSES.BLOODRAGER
###############################
    "advancedclassguide.classes.bloodrager": [
        (str.replace,
         """<a href="/pathfinderRPG/prd/coreRulebook/spells/bearSEndurance.html#bear-s-endurance"><a href="/pathfinderRPG/prd/coreRulebook/spells/bearSEndurance.html#bear-s-endurance"><em>bear's endurance</em></a></a>""",
         """<a href="/pathfinderRPG/prd/coreRulebook/spells/bearSEndurance.html#bear-s-endurance">bear's endurance</a>""")
    ],
###############################
# end of ADVANCEDCLASSGUIDE.CLASSES.BLOODRAGER
###############################


###############################
# ADVANCEDCLASSGUIDE.CLASSES.SHAMAN
###############################
    "advancedclassguide.classes.shaman": [
        (str.replace,
         '<a href="#spirit-animals">',
         '<a href="#spirit-animal">'),
        (str.replace,
         '<a href="/pathfinderRPG/prd/coreRulebook/spells/restoration.html#lesser-restoration">',
         '<a href="/pathfinderRPG/prd/coreRulebook/spells/restoration.html#restoration-lesser">'),
    ],
###############################
# end of ADVANCEDCLASSGUIDE.CLASSES.SHAMAN
###############################


###############################
# ADVANCEDCLASSGUIDE.CLASSES.SKALD
###############################
    "advancedclassguide.classes.skald": [
        (str.replace,
         '<p id="strong-kenning"><strong>Spell Kenning (Su)</strong>',
         '<p id="spell-kenning"><strong>Spell Kenning (Su)</strong>'),
        (str.replace,
         '<a href="http://paizo.com/pathfinderRPG/prd/coreRulebook/classes/barbarian.html#superstition">superstition</a>',
         '<a href="http://paizo.com/pathfinderRPG/prd/coreRulebook/classes/barbarian.html#rage-powers-superstition">superstition</a>'),
        (str.replace,
         '<a href="http://paizo.com/pathfinderRPG/prd/coreRulebook/classes/barbarian.html#renewed-vigor">renewed vigor</a>',
         '<a href="http://paizo.com/pathfinderRPG/prd/coreRulebook/classes/barbarian.html#rage-powers-renewed-vigor">renewed vigor</a>'),
    ],
###############################
# end of ADVANCEDCLASSGUIDE.CLASSES.SKALD
###############################


###############################
# ADVANCEDCLASSGUIDE.FEATS
###############################
    "advancedclassguide.feats": [
        (remove_indentation, None, None),
        (str.replace,
         \
         """<tr>
<th>Panache Feats</th>
<th>Prerequisites</th>
<th>Benefits</th>
</tr>""",
        """</tbody><thead>
<tr>
<th>Panache Feats</th>
<th>Prerequisites</th>
<th>Benefits</th>
</tr>
</thead><tbody>"""),
        (str.replace,
         """
<tr>
<th>Style Feats</th>
<th>Prerequisites</th>
<th>Benefits</th>
</tr>""",
         """</tbody><thead>
<tr>
<th>Style Feats</th>
<th>Prerequisites</th>
<th>Benefits</th>
</tr>
</thead><tbody>"""),
        (str.replace,
         """
<tr>
<th>Teamwork Feats</th>
<th>Prerequisites</th>
<th>Benefit</th>
</tr>""",
         """</tbody><thead>
<tr>
<th>Teamwork Feats</th>
<th>Prerequisites</th>
<th>Benefit</th>
</tr>
</thead><tbody>"""),
        (str.replace,
         '</t>', '</td>')
    ],
###############################
# end of ADVANCEDCLASSGUIDE.FEATS
###############################


###############################
# ADVANCEDPLAYERSGUIDE.ADVANCEDGEAR
###############################
    "advancedplayersguide.advancedgear": [
        (str.replace,
         """<thead><tr id="armor-cost-bonus-dex-bonus-check-penalty-failure-chance-30-ft.-20-ft.-weight1"><th rowspan="2">Armor</th><th rowspan="2">Cost</th><th rowspan="2">Armor/Shield Bonus</th><th rowspan="2">Maximum Dex Bonus</th><th rowspan="2">Armor Check Penalty</th><th rowspan="2">Arcane Spell Failure Chance</th><th colspan="2">Speed</th><th rowspan="2">Weight<sup>1</sup></th></tr>
<tr><th>30 ft.</th><th>20 ft.</th></thead>""",
         """<thead>
  <tr id="armor-cost-bonus-dex-bonus-check-penalty-failure-chance-30-ft.-20-ft.-weight1">
    <th rowspan="2">Armor</th>
    <th rowspan="2">Cost</th>
    <th rowspan="2">Armor/Shield Bonus</th>
    <th rowspan="2">Maximum Dex Bonus</th>
    <th rowspan="2">Armor Check Penalty</th>
    <th rowspan="2">Arcane Spell Failure Chance</th>
    <th rowspan="2">Speed 30 ft.</th>
    <th rowspan="2">Speed 20 ft.</th>
    <th rowspan="2">Weight<sup>1</sup></th>
  </tr>
</thead>""")
    ],
###############################
# end of ADVANCEDPLAYERSGUIDE.ADVANCEDGEAR
###############################


###############################
# ADVANCEDPLAYERSGUIDE.ADVANCEDNEWRULES
###############################
    "advancedplayersguide.advancednewrules": [
        (
            str.replace,
            '<p><a href = "#basic-traits"><strong>Basic Traits</strong>',
            '<p><a href = "#basic-traits"><strong>Basic Traits</strong></a>'
        ),
        (str.replace,
         '<p><a href = "#campaign-traits"><strong>Campaign Traits</strong>',
         '<p><a href = "#campaign-traits"><strong>Campaign Traits</strong></a>'
        ),
        (str.replace,
         '<p><a href = "#race-traits"><strong>Race Traits</strong>',
         '<p><a href = "#race-traits"><strong>Race Traits</strong></a>'
        ),
        (str.replace,
         '<p><a href = "#regional-traits"><strong>Regional Traits</strong>',
         '<p><a href = "#regional-traits"><strong>Regional Traits</strong></a>'
        ),
        (str.replace,
         '<p><a href = "#religion-traits"><strong>Religion Traits</strong>',
         '<p><a href = "#religion-traits"><strong>Religion Traits</strong></a>'
        ),
    ],
###############################
# end of ADVANCEDPLAYERSGUIDE.ADVANCEDNEWRULES
###############################


###############################
# ADVANCEDPLAYERSGUIDE.CORECLASSES.ROGUE
###############################
    "advancedplayersguide.coreclasses.rogue": [
        (str.replace,
         '<p id="powerful-sneak**"><i>Powerful Sneak** (Ex)</i>',
         '<p id="powerful-sneak"><i>Powerful Sneak** (Ex)</i>'),
        (str.replace,
         '<p id="deadly-sneak**"><i>Deadly Sneak** (Ex)</i>',
         '<p id="deadly-sneak"><i>Deadly Sneak** (Ex)</i>'),
    ],
###############################
# end of ADVANCEDPLAYERSGUIDE.CORECLASSES.ROGUE
###############################


###############################
# ADVANCEDRACEGUIDE.FEATUREDRACES.OREADS
###############################
    "advancedraceguide.featuredraces.oreads": [
        (str.replace,
         '<p><span class="body-copy-char">Strong abjuration; CL 12th; <a href="/pathfinderRPG/prd/coreRulebook/feats.html#craft-magic-arms-and-armor" >Craft Magic Arms and Armor</a>, <span class="body-copy-char italics">shield other<span class="body-copy-char">; Price +2 bonus.</p>',
         '<p>Strong abjuration; CL 12th; <a href="/pathfinderRPG/prd/coreRulebook/feats.html#craft-magic-arms-and-armor" >Craft Magic Arms and Armor</a>, shield other; Price +2 bonus.</p>'),
        (str.replace,
         '<p><span class="body-copy-char">Moderate abjuration; CL 8th; <a href="/pathfinderRPG/prd/coreRulebook/feats.html#craft-magic-arms-and-armor" >Craft Magic Arms and Armor</a>, <span class="body-copy-char italics">shield other<span class="body-copy-char">; Price +1 bonus.</p>',
         '<p>Moderate abjuration; CL 8th; <a href="/pathfinderRPG/prd/coreRulebook/feats.html#craft-magic-arms-and-armor" >Craft Magic Arms and Armor</a>, shield other; Price +1 bonus.</p>'),
    ],
###############################
# end of ADVANCEDRACEGUIDE.FEATUREDRACES.OREADS
###############################


###############################
# ADVANCEDRACEGUIDE.RACEBUILDER.EXAMPLERACES
###############################
    "advancedraceguide.racebuilder.exampleraces": [
        (str.replace,
         '<h3><b>Total</b> <span class="stat-block-rp">15 rp</span></p>',
         '<h3><b>Total</b> <span class="stat-block-rp">15 rp</span></h3>')
    ],
###############################
# end of ADVANCEDRACEGUIDE.RACEBUILDER.EXAMPLERACES
###############################


###############################
# ADVANCEDPLAYERSGUIDE.PRESTIGECLASSES.MASTERCHYMIST
###############################
    "advancedplayersguide.prestigeclasses.masterchymist": [
        (str.replace,
         '<tr><td>10th</td><td>+10</td><td>+5</td><td>+5</td><td>+3</td><td><a href="#advanced-mutagen" >Advanced mutagen</a>, <a href="#mutate" >mutate</a> 5/day</td><td>+1 level of alchemist</td><td>&mdash;</td></tr>',
         '<tr><td>10th</td><td>+10</td><td>+5</td><td>+5</td><td>+3</td><td><a href="#advanced-mutagen" >Advanced mutagen</a>, <a href="#mutate" >mutate</a> 5/day</td><td>+1 level of alchemist</td></tr>')
    ],
###############################
# end of ADVANCEDPLAYERSGUIDE.PRESTIGECLASSES.MASTERCHYMIST
###############################


###############################
# BESTIARY.DRAGON
###############################
    "bestiary.dragon": [
        (str.replace,
         '<thead><tr><th rowspan="2">Size</th><th rowspan="2">Fly Speed (maneuverability)</th><th rowspan="2">1 Bite</th><th rowspan="2">2 Claws</th><th rowspan="2">2 Wings</th><th rowspan="2">1 Tail Slap</th><th rowspan="2">1 Crush</th><th rowspan="2">1 Tail Sweep</th><th colspan="2">Breath Weapon</th></tr><tr><th>Line</th><th>Cone</th></tr></thead>',
         '<thead><tr><th rowspan="2">Size</th><th rowspan="2">Fly Speed<br>(maneuverability)</th><th rowspan="2">1 Bite</th><th rowspan="2">2 Claws</th><th rowspan="2">2 Wings</th><th rowspan="2">1 Tail Slap</th><th rowspan="2">1 Crush</th><th rowspan="2">1 Tail Sweep</th><th>Breath / Line</th><th>Breath / Cone</th></tr></thead>')
    ],
###############################
# end of BESTIARY.DRAGON
###############################


###############################
# BESTIARY.ELEMENTAL
###############################
    "bestiary.elemental": [
        (str.replace,
         '</th><tr></thead>',
         '</th></tr></thead>')
    ],
###############################
# end of BESTIARY.ELEMENTAL
###############################


###############################
# BESTIARY.MONSTERCREATION
###############################
    "bestiary.monstercreation": [
        (str.replace,
         '<th colspan="2">Average Damage</th><th rowspan="2">Primary Ability DC</th><th rowspan="2">Secondary Ability DC</th><th rowspan="2">Good Save</th><th rowspan="2">Poor Save</th></tr><tr><th>High</th><th>Low</th></tr></thead>',
         '<th rowspan="2">Avg. Dmg. High</th><th rowspan="2">Avg. Dmg. Low</th><th rowspan="2">Primary Ability DC</th><th rowspan="2">Secondary Ability DC</th><th rowspan="2">Good Save</th><th rowspan="2">Poor Save</th></tr></tr></thead>'),
        (str.replace,
         '<th rowspan="2">Creature Type</th><th colspan="21">Challenge Rating</th><tr>',
         '<th rowspan="2">Creature Type / Challenge Rating</th>'),
        (str.replace,
         '</td><td></td><td></td><td></td><td><h1',
         '<h1'),
        (str.replace,
         '</td><td></td><td></td><td></td><td><h2',
         '<h2'),
        (str.replace,
         '</td><td></td><td></td><td></td><td><p',
         '<p'),
        (str.replace,
         '</td><td></td><td></td><td></td><td><div',
         '<div'),
        (str.replace,
         '</td><td></td><td></td><td></td><td><table',
         '<table'),
        (str.replace,
         '</td><td></td><td></td><td></td><td>\n',
         '\n'),
        (str.replace,
         'See Table: </td><td> by CR for a list',
         'See Table: by CR for a list'),
    ],
###############################
# end of BESTIARY.MONSTERCREATION
###############################


###############################
# BESTIARY.UNIVERSALMONSTERRULES
###############################
    "bestiary.universalmonsterrules": [
        (remove_indentation, None, None),

        (str.replace,
         """<thead>
<tr><th rowspan="2">Natural Attack</th><th colspan="9"><center>Base Damage by Size*</center></th><th rowspan="2">Damage Type</th><th rowspan="2">Attack Type</th></tr>
<tr><th>Fine</th><th>Dim.</th><th>Tiny</th><th>Small</th><th>Medium</th><th>Large</th><th>Huge</th><th>Garg.</th><th>Col.</th></tr>
</thead>""",
         """<thead>
<tr><th>Natural Attack / Base Dmg. by Size*</th><th>Fine</th><th>Dim.</th><th>Tiny</th><th>Small</th><th>Medium</th><th>Large</th><th>Huge</th><th>Garg.</th><th>Col.</th><th>Damage Type</th><th>Attack Type</th></tr>
</thead>"""),
    ],
###############################
# end of BESTIARY.UNIVERSALMONSTERRULES
###############################


###############################
# BESTIARY2.PROTEAN
###############################
    "bestiary2.protean": [
        (str.replace,
         '<a href="/pathfinderRPG/prd/bestiary2/#protean,-voidworm">',
         '<a href="#protean,-voidworm">'),
        (str.replace,
         '<a href="/pathfinderRPG/prd/bestiary2/#protean,-naunet">',
         '<a href="#protean,-naunet">'),
        (str.replace,
         '<a href="/pathfinderRPG/prd/bestiary2/#protean,-imentesh">',
         '<a href="#protean,-imentesh">'),
        (str.replace,
         '<a href="/pathfinderRPG/prd/bestiary2/#protean,-keketar">',
         '<a href="#protean,-keketar">'),
        (str.replace,
         '<a href="/pathfinderRPG/prd/bestiary2/#protean,-keketar">',
         '<a href="#protean,-keketar">'),
    ],
###############################
# end of BESTIARY2.PROTEAN
###############################


###############################
# BESTIARY3.DRAGON
###############################
    "bestiary3.dragon": [
        (str.replace,
         '<thead><tr><th rowspan="2">Size</th><th rowspan="2">Fly Speed<br />(maneuverability)</th><th rowspan="2">1 Bite</th><th rowspan="2">2 Claws</th><th rowspan="2">Gore</th><th rowspan="2">1 Tail Slap</th><th rowspan="2">1 Crush</th><th rowspan="2">1 Tail Sweep</th><th colspan="2">Breath Weapon</th></tr><tr><th>Line</th><th>Cone</th></tr></thead>',
         '<thead><tr><th rowspan="2">Size</th><th rowspan="2">Fly Speed<br>(maneuverability)</th><th rowspan="2">1 Bite</th><th rowspan="2">2 Claws</th><th rowspan="2">Gore</th><th rowspan="2">1 Tail Slap</th><th rowspan="2">1 Crush</th><th rowspan="2">1 Tail Sweep</th><th>Breath / Line</th><th>Breath / Cone</th></tr></thead>')
    ],
###############################
# end of BESTIARY3.DRAGON
###############################


###############################
# BESTIARY3.FEYCREATURE
###############################
    "bestiary3.feycreature": [
        (str.replace,
         '<center><table><tr><td>1&ndash;2</td><td><i><a href="/pathfinderRPG/prd/coreRulebook/spells/dancingLights.html',
         '<center><table><tr><th>HD</th><th>Abilities</th></tr><tr><td>1&ndash;2</td><td><i><a href="/pathfinderRPG/prd/coreRulebook/spells/dancingLights.html')
    ],
###############################
# end of BESTIARY3.FEYCREATURE
###############################


###############################
# BESTIARY3.FLAILSNAIL
###############################
    "bestiary3.flailsnail": [
        (str.replace,
         '<center><table><tr><td>1&ndash;3</td><td>Spell misfires',
         '<center><table><tr><th>d10 roll</th><th>Effect</th></tr><tr><td>1&ndash;3</td><td>Spell misfires')
    ],
###############################
# end of BESTIARY3.FLAILSNAIL
###############################


###############################
# BESTIARY4.EMPYREALLORD
###############################
    "bestiary4.empyreallord": [
        (str.replace,
         """<li><b>Mythic</b>: An empyreal lord functions as a 10th mythic rank creature, including the mythic power ability (10/day, surge +1d12). It may expend uses of mythic power to use the mythic versions of any spell-like ability denoted with an asterisk (*) just as if the ability were a mythic spell.</p>
<li>Use of the following spell-like abilities at will&mdash;<i><a href="/pathfinderRPG/prd/coreRulebook/spells/demand.html#demand" >demand</a></i>, <i><a href="/pathfinderRPG/prd/coreRulebook/spells/discernLocation.html#discern-location" >discern location</a></i>, <i><a href="/pathfinderRPG/prd/coreRulebook/spells/fabricate.html#fabricate" >fabricate</a></i>, and <i><a href="/pathfinderRPG/prd/coreRulebook/spells/majorCreation.html#major-creation" >major creation</a></i>.</p>
<li>Use of the following spell-like abilities once per day&mdash;<i><a href="/pathfinderRPG/prd/coreRulebook/spells/dimensionalLock.html#dimensional-lock" >dimensional lock</a></i>*, <i><a href="/pathfinderRPG/prd/coreRulebook/spells/miracle.html#miracle" >miracle</a> </i>(limited to physical effects that manipulate the realm or to effects that are relevant to the empyreal lord's areas of concern), <i><a href="/pathfinderRPG/prd/coreRulebook/spells/powerWordStun.html#power-word-stun" >power word stun</a></i>*.</p>
<li><b>Heightened Awareness (Ex)</b>: An empyreal lord gains a +10 insight bonus on <a href="/pathfinderRPG/prd/coreRulebook/skills/perception.html#perception" >Perception</a> and Initiative checks.</p>""",

         """<ul><li><b>Mythic</b>: An empyreal lord functions as a 10th mythic rank creature, including the mythic power ability (10/day, surge +1d12). It may expend uses of mythic power to use the mythic versions of any spell-like ability denoted with an asterisk (*) just as if the ability were a mythic spell.</li>
<li>Use of the following spell-like abilities at will&mdash;<i><a href="/pathfinderRPG/prd/coreRulebook/spells/demand.html#demand" >demand</a></i>, <i><a href="/pathfinderRPG/prd/coreRulebook/spells/discernLocation.html#discern-location" >discern location</a></i>, <i><a href="/pathfinderRPG/prd/coreRulebook/spells/fabricate.html#fabricate" >fabricate</a></i>, and <i><a href="/pathfinderRPG/prd/coreRulebook/spells/majorCreation.html#major-creation" >major creation</a></i>.</li>
<li>Use of the following spell-like abilities once per day&mdash;<i><a href="/pathfinderRPG/prd/coreRulebook/spells/dimensionalLock.html#dimensional-lock" >dimensional lock</a></i>*, <i><a href="/pathfinderRPG/prd/coreRulebook/spells/miracle.html#miracle" >miracle</a> </i>(limited to physical effects that manipulate the realm or to effects that are relevant to the empyreal lord's areas of concern), <i><a href="/pathfinderRPG/prd/coreRulebook/spells/powerWordStun.html#power-word-stun" >power word stun</a></i>*.</li>
<li><b>Heightened Awareness (Ex)</b>: An empyreal lord gains a +10 insight bonus on <a href="/pathfinderRPG/prd/coreRulebook/skills/perception.html#perception" >Perception</a> and Initiative checks.</li></ul>""")
    ],
###############################
# end of BESTIARY4.EMPYREALLORD
###############################


###############################
# BESTIARY4.GOLEM
###############################
    "bestiary4.golem": [
        (str.replace,
         """<li>Cure spells affect it as if it were a living creature, but only cure the minimum amount of damage.</p>
<li>Spells and effects that specifically affect blood (such as <i><a href="/pathfinderRPG/prd/ultimateMagic/spells/boilingBlood.html#boiling-blood" >boiling blood</a></i>) affect it normally.</p>""",

         """<ul><li>Cure spells affect it as if it were a living creature, but only cure the minimum amount of damage.</li>
<li>Spells and effects that specifically affect blood (such as <i><a href="/pathfinderRPG/prd/ultimateMagic/spells/boilingBlood.html#boiling-blood" >boiling blood</a></i>) affect it normally.</li></ul>"""),

(str.replace,
         """<li>Any spell with the water descriptor heals a coral golem 1d6 points of damage per level of the caster (maximum 10d6).</p>
<li><i><a href="/pathfinderRPG/prd/coreRulebook/spells/transmuteRockToMud.html#transmute-rock-to-mud" >Transmute rock to mud</a></i> slows a coral golem (as the <i><a href="/pathfinderRPG/prd/coreRulebook/spells/slow.html#slow" >slow</a></i> spell) for 1d6 rounds (no save).<span class="char-style-override-53"></p>
<li><i><a href="/pathfinderRPG/prd/coreRulebook/spells/transmuteMudToRock.html#transmute-mud-to-rock" >Transmute mud to rock</a></i> increases the golem's bleed damage to 2d6 for 3 rounds.<span class="char-style-override-53"></p>
<li><i><a href="/pathfinderRPG/prd/coreRulebook/spells/softenEarthAndStone.html#soften-earth-and-stone" >Soften earth and stone</a></i> causes a coral golem to lose its damage reduction for 3 rounds.</p>""",

         """<ul>
<li>Any spell with the water descriptor heals a coral golem 1d6 points of damage per level of the caster (maximum 10d6).</li>
<li><i><a href="/pathfinderRPG/prd/coreRulebook/spells/transmuteRockToMud.html#transmute-rock-to-mud" >Transmute rock to mud</a></i> slows a coral golem (as the <i><a href="/pathfinderRPG/prd/coreRulebook/spells/slow.html#slow" >slow</a></i> spell) for 1d6 rounds (no save).</li>
<li><i><a href="/pathfinderRPG/prd/coreRulebook/spells/transmuteMudToRock.html#transmute-mud-to-rock" >Transmute mud to rock</a></i> increases the golem's bleed damage to 2d6 for 3 rounds.</li>
<li><i><a href="/pathfinderRPG/prd/coreRulebook/spells/softenEarthAndStone.html#soften-earth-and-stone" >Soften earth and stone</a></i> causes a coral golem to lose its damage reduction for 3 rounds.</li>
</ul>"""),
    (str.replace,
     """<li>A <i><a href="/pathfinderRPG/prd/coreRulebook/spells/shatter.html#shatter" >shatter</a></i> spell causes a junk golem to discorporate and dazes it for 1 round.</p>
<li>A <i><a href="/pathfinderRPG/prd/coreRulebook/spells/grease.html#grease" >grease</a></i> spell affects the junk golem as if it were <i><a href="/pathfinderRPG/prd/coreRulebook/spells/haste.html#haste" >haste</a></i> for 1d6 rounds and ends any <i><a href="/pathfinderRPG/prd/coreRulebook/spells/slow.html#slow" >slow</a></i> effect on it.</p>
<li>An <i><a href="/pathfinderRPG/prd/coreRulebook/spells/arcaneLock.html#arcane-lock" >arcane lock</a></i> or <i><a href="/pathfinderRPG/prd/coreRulebook/spells/holdPortal.html#hold-portal" >hold portal</a></i> spell affects the junk golem as if it were a <i><a href="/pathfinderRPG/prd/coreRulebook/spells/slow.html#slow" >slow</a></i> spell for 1d6 rounds and breaks any <i><a href="/pathfinderRPG/prd/coreRulebook/spells/haste.html#haste" >haste</a></i> effect on it.</p>
<li>A <i><a href="/pathfinderRPG/prd/coreRulebook/spells/woodShape.html#wood-shape" >wood shape</a></i> or <i><a href="/pathfinderRPG/prd/coreRulebook/spells/rustingGrasp.html#rusting-grasp" >rusting grasp</a></i> spell deals 2d6 points of damage to a junk golem.</p>""",
"""<ul>
<li>A <i><a href="/pathfinderRPG/prd/coreRulebook/spells/shatter.html#shatter" >shatter</a></i> spell causes a junk golem to discorporate and dazes it for 1 round.</li>
<li>A <i><a href="/pathfinderRPG/prd/coreRulebook/spells/grease.html#grease" >grease</a></i> spell affects the junk golem as if it were <i><a href="/pathfinderRPG/prd/coreRulebook/spells/haste.html#haste" >haste</a></i> for 1d6 rounds and ends any <i><a href="/pathfinderRPG/prd/coreRulebook/spells/slow.html#slow" >slow</a></i> effect on it.</li>
<li>An <i><a href="/pathfinderRPG/prd/coreRulebook/spells/arcaneLock.html#arcane-lock" >arcane lock</a></i> or <i><a href="/pathfinderRPG/prd/coreRulebook/spells/holdPortal.html#hold-portal" >hold portal</a></i> spell affects the junk golem as if it were a <i><a href="/pathfinderRPG/prd/coreRulebook/spells/slow.html#slow" >slow</a></i> spell for 1d6 rounds and breaks any <i><a href="/pathfinderRPG/prd/coreRulebook/spells/haste.html#haste" >haste</a></i> effect on it.</li>
<li>A <i><a href="/pathfinderRPG/prd/coreRulebook/spells/woodShape.html#wood-shape" >wood shape</a></i> or <i><a href="/pathfinderRPG/prd/coreRulebook/spells/rustingGrasp.html#rusting-grasp" >rusting grasp</a></i> spell deals 2d6 points of damage to a junk golem.</li>
</ul>"""
    ),

    (str.replace,
     """<li>A magical attack that deals fire damage slows a wax golem (as the <i><a href="/pathfinderRPG/prd/coreRulebook/spells/slow.html#slow" >slow</a></i> spell) for 2d6 rounds (no save). In addition, for 3 rounds after taking fire damage, every time a wax golem uses its slam attack, it deals an additional 1d4 points of fire damage due to its molten wax.</p>
<li>A magical attack that deals cold damage breaks any <i><a href="/pathfinderRPG/prd/coreRulebook/spells/slow.html#slow" >slow</a></i> effect on the golem and heals 1 point of damage for each 3 points of damage the attack would otherwise deal. If the amount of healing would cause the golem to exceed its full normal hit points, it gains any excess as temporary hit points. A wax golem gains no saving throw against cold effects.</p>""",
     """<ul>
<li>A magical attack that deals fire damage slows a wax golem (as the <i><a href="/pathfinderRPG/prd/coreRulebook/spells/slow.html#slow" >slow</a></i> spell) for 2d6 rounds (no save). In addition, for 3 rounds after taking fire damage, every time a wax golem uses its slam attack, it deals an additional 1d4 points of fire damage due to its molten wax.</li>
<li>A magical attack that deals cold damage breaks any <i><a href="/pathfinderRPG/prd/coreRulebook/spells/slow.html#slow" >slow</a></i> effect on the golem and heals 1 point of damage for each 3 points of damage the attack would otherwise deal. If the amount of healing would cause the golem to exceed its full normal hit points, it gains any excess as temporary hit points. A wax golem gains no saving throw against cold effects.</li>
</ul>"""
    ),


        (str.replace,
         """<h2 id="construction">Construction</h2>
<p>A blood golem's body must be constructed from the fresh blood of approximately 20 Medium creatures and alchemical fluids worth at least 500 gp.</p>""",
         """<h2 id="golem-blood-construction">Construction</h2>
<p>A blood golem's body must be constructed from the fresh blood of approximately 20 Medium creatures and alchemical fluids worth at least 500 gp.</p>"""),
        (str.replace,
         """<h2 id="construction">Construction</h2>
<p>A coral golem's body is made of a healthy colony of living coral weighing at least 1,000 pounds, infused with rare organic substances and minerals worth 3,500 gp.</p>""",
         """<h2 id="golem-coral-construction">Construction</h2>
<p>A coral golem's body is made of a healthy colony of living coral weighing at least 1,000 pounds, infused with rare organic substances and minerals worth 3,500 gp.</p>"""),
        (str.replace,
         """<h2 id="construction">Construction</h2>
<p>A junk golem's body is made up of 250 pounds of assorted rubbish with 200 gp of spare metal and copper wire.</p>""",
         """<h2 id="golem-junk-construction">Construction</h2>
<p>A junk golem's body is made up of 250 pounds of assorted rubbish with 200 gp of spare metal and copper wire.</p>"""),
        (str.replace,
         """<h2 id="construction">Construction</h2>
<p>The construction of a wax golem requires a block of solid wax that weights at least 1,000 pounds.</p>""",
         """<h2 id="golem-wax-construction">Construction</h2>
<p>The construction of a wax golem requires a block of solid wax that weights at least 1,000 pounds.</p>"""),
        ],
###############################
# end of BESTIARY4.GOLEM
###############################


###############################
# BESTIARY4.SOULBOUNDMANNEQUIN
###############################
    "bestiary4.soulboundmannequin": [
        (str.replace,
         """<li><i>Chaotic Neutral:</i> <i><a href="/pathfinderRPG/prd/coreRulebook/spells/confusion.html#confusion" >confusion</a></i> (DC 13)</p>
<li><i>Lawful Neutral</i>: <i><a href="/pathfinderRPG/prd/coreRulebook/spells/fear.html#fear" >fear</a></i> (DC 13)</p>
<li><i>Neutral</i>: <i><a href="/pathfinderRPG/prd/coreRulebook/spells/holdMonster.html#hold-monster" >hold monster</a></i> (DC 13)</p>
<li><i>Neutral Evil</i>: <i><a href="/pathfinderRPG/prd/coreRulebook/spells/enervation.html#enervation" >enervation</a></i></p>
<li><i>Neutral Good</i>:<i> <a href="/pathfinderRPG/prd/coreRulebook/spells/invisibility.html#invisibility-greater" >greater invisibility</a></i></p>""",
         """<ul><li><i>Chaotic Neutral:</i> <i><a href="/pathfinderRPG/prd/coreRulebook/spells/confusion.html#confusion" >confusion</a></i> (DC 13)</li>
<li><i>Lawful Neutral</i>: <i><a href="/pathfinderRPG/prd/coreRulebook/spells/fear.html#fear" >fear</a></i> (DC 13)</li>
<li><i>Neutral</i>: <i><a href="/pathfinderRPG/prd/coreRulebook/spells/holdMonster.html#hold-monster" >hold monster</a></i> (DC 13)</li>
<li><i>Neutral Evil</i>: <i><a href="/pathfinderRPG/prd/coreRulebook/spells/enervation.html#enervation" >enervation</a></i></li>
<li><i>Neutral Good</i>:<i> <a href="/pathfinderRPG/prd/coreRulebook/spells/invisibility.html#invisibility-greater" >greater invisibility</a></i></li></ul>""")
    ],
###############################
# end of BESTIARY4.SOULBOUNDMANNEQUIN
###############################


###############################
# BESTIARY5.ANGELS
###############################
    "bestiary5.angels": [
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/spells/command.html#command-greater"><a href = "/pathfinderRPG/prd/coreRulebook/spells/command.html#greater-command"><em>greater command</em></a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/spells/command.html#command-greater">greater command</a>""")
    ],
###############################
# end of BESTIARY5.ANGELS
###############################


###############################
# BESTIARY5.APKALLU
###############################
    "bestiary5.apkallu": [
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/spells/command.html#command-greater"><a href = "/pathfinderRPG/prd/coreRulebook/spells/command.html#greater-command"><em>greater command</em></a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/spells/command.html#command-greater">greater command</a>""")
    ],
###############################
# end of BESTIARY5.APKALLU
###############################

###############################
# BESTIARY5.GIANTS
###############################
    "bestiary5.giants": [
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#rapid-reload"><a href = "/pathfinderRPG/prd/ultimateCombat/ultimateCombatFeats.html#rapid-reload">Rapid Reload</a></a>""",
         """<a href = "/pathfinderRPG/prd/ultimateCombat/ultimateCombatFeats.html#rapid-reload">Rapid Reload</a>""")
    ],
###############################
# end of BESTIARY5.GIANTS
###############################


###############################
# BESTIARY5.DRAGONSESOTERIC
###############################
    "bestiary5.dragonsesoteric": [
        (remove_indentation, None, None),

        (str.replace,
         '<table id = "esoteric-dragon-age-categories">',
         '<table id = "table-esoteric-dragon-age-categories">'),

        (str.replace,
         """<thead>
<tr>
<th colspan = "8">&nbsp;</th>
<th colspan = "2">Breath Weapon</th>
</tr>
<tr>
<th>Size</th>
<th>Fly Speed (maneuverability)</th>
<th>1 Bite</th>
<th>2 Claws</th>
<th>2 Wings</th>
<th>1 Tail Slap</th>
<th>1 Crush</th>
<th>1 Tail Sweep</th>
<th>Cone</th>
<th>Line</th>
</tr>
</thead>""",

         """<thead>
<tr>
    <th>Size</th>
    <th>Fly Speed<br>(maneuverability)</th>
    <th>1 Bite</th>
    <th>2 Claws</th>
    <th>2 Wings</th>
    <th>1 Tail Slap</th>
    <th>1 Crush</th>
    <th>1 Tail Sweep</th>
    <th>Breath / Cone</th>
    <th>Breath / Line</th>
</tr>
</thead>"""),

        (str.replace,
         """<tbody>
<tr><td>Tiny</td><td>100 ft. (average)</td>1d4</td><td>1d3</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>30 ft.</td><td>15 ft.</td></tr>
<tr><td>Small</td><td>150 ft. (average)</td>1d6</td><td>1d4</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>40 ft.</td><td>20 ft.</td></tr>
<tr><td>Medium</td><td>150 ft. (average)</td>1d8</td><td>1d6</td><td>1d4</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>60 ft.</td><td>30 ft.</td></tr>
<tr><td>Large</td><td>200 ft. (poor)</td>2d6</td><td>1d8</td><td>1d6</td><td>1d8</td><td>&mdash;</td><td>&mdash;</td><td>80 ft.</td><td>40 ft.</td></tr>
<tr><td>Huge</td><td>200 ft. (poor)</td>2d8</td><td>2d6</td><td>1d8</td><td>2d6</td><td>2d8</td><td>&mdash;</td><td>100 ft.</td><td>50 ft.</td></tr>
<tr><td>Gargantuan</td><td>250 ft. (clumsy)</td>4d6</td><td>2d8</td><td>2d6</td><td>2d8</td><td>4d6</td><td>2d6</td><td>120 ft.</td><td>60 ft.</td></tr>
<tr><td>Colossal</td><td>250 ft. (clumsy)</td>4d8</td><td>4d6</td><td>2d8</td><td>4d6</td><td>4d8</td><td>2d8</td><td>140 ft.</td><td>70 ft.</td></tr>
</tbody>""",

         """<tbody>
    <tr><td>Tiny</td><td>100 ft. (average)</td><td>1d4</td><td>1d3</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>30 ft.</td><td>15 ft.</td></tr>
    <tr><td>Small</td><td>150 ft. (average)</td><td>1d6</td><td>1d4</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>40 ft.</td><td>20 ft.</td></tr>
    <tr><td>Medium</td><td>150 ft. (average)</td><td>1d8</td><td>1d6</td><td>1d4</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>60 ft.</td><td>30 ft.</td></tr>
    <tr><td>Large</td><td>200 ft. (poor)</td><td>2d6</td><td>1d8</td><td>1d6</td><td>1d8</td><td>&mdash;</td><td>&mdash;</td><td>80 ft.</td><td>40 ft.</td></tr>
    <tr><td>Huge</td><td>200 ft. (poor)</td><td>2d8</td><td>2d6</td><td>1d8</td><td>2d6</td><td>2d8</td><td>&mdash;</td><td>100 ft.</td><td>50 ft.</td></tr>
    <tr><td>Gargantuan</td><td>250 ft. (clumsy)</td><td>4d6</td><td>2d8</td><td>2d6</td><td>2d8</td><td>4d6</td><td>2d6</td><td>120 ft.</td><td>60 ft.</td></tr>
    <tr><td>Colossal</td><td>250 ft. (clumsy)</td><td>4d8</td><td>4d6</td><td>2d8</td><td>4d6</td><td>4d8</td><td>2d8</td><td>140 ft.</td><td>70 ft.</td></tr>
</tbody>""")
    ],
###############################
# end of BESTIARY5.DRAGONSESOTERIC
###############################


###############################
# BESTIARY5.MUMMYLORD
###############################
    "bestiary5.mummylord": [
        (str.replace,
         ' (<em>Pathfinder RPG Bestiary <em>302)',
         ''),
        (fix_nonclosing_consecutive_tags, 'em', None)
    ],
###############################
# end of BESTIARY5.MUMMYLORD
###############################


###############################
# BESTIARY5.MUTANT
###############################
    "bestiary5.mutant": [
        (fix_nonclosing_consecutive_tags, 'em', None)
    ],
###############################
# end of BESTIARY5.MUTANT
###############################


###############################
# BESTIARY5.TAXIDERMICCREATURE
###############################
    "bestiary5.taxidermiccreature": [
        (str.replace, "<stro\nng>", "<strong>")
    ],
###############################
# end of BESTIARY5.TAXIDERMICCREATURE
###############################


###############################
# CORERULEBOOK.CLASSES
###############################
    "corerulebook.classes": [(
        str.replace,
        """<thead><tr><th rowspan="2">Character Level</th><th colspan="3">Experience Point Total</th><th rowspan="2">Feats</th><th rowspan="2">Ability Score</th></tr>
<tr><th>Slow</th><th>Medium</th><th>Fast</th></tr></thead>""",
        """<thead><tr><th rowspan="2">Character Level</th><th>XP<br>Slow</th><th>XP<br>Medium</th><th>XP<br>Fast</th><th rowspan="2">Feats</th><th rowspan="2">Ability Score</th></tr></thead>""")
    ],
###############################
# end of CORERULEBOOK.CLASSES
###############################



###############################
# CORERULEBOOK.CLASSES.MONK
###############################
    "corerulebook.classes.monk": [(
        str.replace,
        """<wbr>""",
        """""")
    ],
###############################
# end of CORERULEBOOK.CLASSES.MONK
###############################



###############################
# CORERULEBOOK.ADDITIONALRULES
###############################
    "corerulebook.additionalrules": [

    (remove_indentation, None, None),
    (
        str.replace,
        '<tr><th colspan="5">One Round (Tactical)*</th></tr>',
        '<tr><td colspan="5"><i>One Round (Tactical)*</i></td></tr>'
    ),
    (
        str.replace,
        '<tr><th colspan="5">One Minute (Local)  </th></tr>',
        '<tr><td colspan="5"><i>One Minute (Local)</i></td></tr>'
    ),
    (
        str.replace,
        '<tr><th colspan="5">One Hour (Overland)  </th></tr>',
        '<tr><td colspan="5"><i>One Hour (Overland)</i></td></tr>'
    ),
    (
        str.replace,
        '<tr><th colspan="5">One Day (Overland)  </th></tr>',
        '<tr><td colspan="5"><i>One Day (Overland)</i></td></tr>'
    ),
    (
        str.replace,
        """<tr><th colspan="3">Mount (carrying load)</th></tr>""",
        """<tr><td colspan="3"><i>Mount (carrying load)</i></td></tr>"""
    ),
    (
        str.replace,
        """<tr><th colspan="3">Ship</th></tr>""",
        """<tr><td colspan="3"><i>Ship</i></td></tr>"""
    ),
    (
        str.replace,
        """<thead><tr><th rowspan="2">Load</th><th rowspan="2">Max Dex</th><th rowspan="2">Check Penalty</th><th colspan="2">Speed</th><th rowspan="2">Run</th></tr>
<tr><th>(30 ft.)</th><th>(20 ft.)</th></tr></thead>""",
        """<thead><tr><th rowspan="2">Load</th><th rowspan="2">Max Dex</th><th rowspan="2">Check Penalty</th><th>Speed (30 ft.)</th><th>Speed (20 ft.)</th><th rowspan="2">Run</th></tr></thead>"""),
    (
        str.replace,
        """<table>
<tr>
<td>&nbsp;</td>
<td><b>Lawful</b></td>
<td><b>Neutral</b></td>
<td><b>Chaotic</b></td>
</tr>
<tr>
<td><b>Good</b></td>
<td>Lawful Good</td>
<td>Neutral Good</td>
<td>Chaotic Good</td>
</tr>
<tr>
<td><b>Neutral</b></td>
<td>Lawful Neutral</td>
<td>Neutral</td>
<td>Chaotic Neutral</td>
</tr>
<tr>
<td><b>Evil</b></td>
<td>Lawful Evil</td>
<td>Neutral Evil</td>
<td>Chaotic Evil</td>
</tr>
</table>""",
        """<table stub_columns=1>
    <tr>
        <th>&nbsp;</th>
        <th>Lawful</th>
        <th>Neutral</th>
        <th>Chaotic</th>
    </tr>
    <tr>
        <td>Good</td>
        <td>Lawful Good</td>
        <td>Neutral Good</td>
        <td>Chaotic Good</td>
    </tr>
    <tr>
        <td>Neutral</td>
        <td>Lawful Neutral</td>
        <td>Neutral</td>
        <td>Chaotic Neutral</td>
    </tr>
    <tr>
        <td>Evil</td>
        <td>Lawful Evil</td>
        <td>Neutral Evil</td>
        <td>Chaotic Evil</td>
    </tr>
</table>""")
    ],
###############################
# end of CORERULEBOOK.ADDITIONALRULES
###############################


###############################
# CORERULEBOOK.CREATINGNPCS
###############################
    "corerulebook.creatingnpcs": [
        (str.replace,
         '<thead><tr><th rowspan="2">Ability Score</th><th colspan="2">Melee NPC</th><th colspan="2">Ranged NPC</th><th colspan="2">Divine NPC</th><th colspan="2">Arcane NPC</th><th colspan="2">Skill NPC</th></tr><tr><th>Basic</th><th>Heroic</th><th>Basic</th><th>Heroic</th><th>Basic</th><th>Heroic</th><th>Basic</th><th>Heroic</th><th>Basic</th><th>Heroic</th></tr></thead>',
         '<thead><tr><th>Ability Score</th><th>Melee<br>Basic</th><th>Melee<br>Heroic</th><th>Ranged<br>Basic</th><th>Ranged<br>Heroic</th><th>Divine<br>Basic</th><th>Divine<br>Heroic</th><th>Arcane<br>Basic</th><th>Arcane<br>Heroic</th><th>Skill<br>Basic</th><th>Skill<br>Heroic</th></tr></thead>'),
        (str.replace,
         '<thead><tr><th colspan="2">PC Skill Class Selections*</th><th colspan="2">NPC Skill Class Selections*</th></tr></thead>',
         '<thead><tr><th>PC classes*</th><th>Skills</th><th>NPC classes*</th><th>Skills</th></tr></thead>'),
        (str.replace,
         """<tr><td>Monk</td><td>4 + Int Mod</td><td></td><td></td></tr>
<tr><td>Paladin</td><td>2 + Int Mod</td><td></td><td></td></tr>
<tr><td>Ranger</td><td>6 + Int Mod</td><td></td><td></td></tr>
<tr><td>Rogue</td><td>8 + Int Mod</td><td></td><td></td></tr>
<tr><td>Sorcerer</td><td>2 + Int Mod</td><td></td><td></td></tr>
<tr><td>Wizard</td><td>2 + Int Mod</td><td></td><td></td></tr>""",
         """<tr><td>Monk</td><td>4 + Int Mod</td><td>&mdash;</td><td>&mdash;</td></tr>
<tr><td>Paladin</td><td>2 + Int Mod</td><td>&mdash;</td><td>&mdash;</td></tr>
<tr><td>Ranger</td><td>6 + Int Mod</td><td>&mdash;</td><td>&mdash;</td></tr>
<tr><td>Rogue</td><td>8 + Int Mod</td><td>&mdash;</td><td>&mdash;</td></tr>
<tr><td>Sorcerer</td><td>2 + Int Mod</td><td>&mdash;</td><td>&mdash;</td></tr>
<tr><td>Wizard</td><td>2 + Int Mod</td><td>&mdash;</td><td>&mdash;</td></tr>""")
    ],
###############################
# end of CORERULEBOOK.CREATINGNPCS
###############################


###############################
# CORERULEBOOK.ENVIRONMENT
###############################
    "corerulebook.environment": [
        (str.replace,
         """<thead><tr><th rowspan="2">Door Type</th><th rowspan="2">Typical Thickness</th><th rowspan="2">Hardness</th><th rowspan="2">Hit Points</th><th colspan="2">break DC</th></tr>
<tr><th>Stuck</th><th>Locked</th></tr></thead>""",
         """<thead><tr><th rowspan="2">Door Type</th><th rowspan="2">Typical Thickness</th><th rowspan="2">Hardness</th><th rowspan="2">Hit Points</th><th>break DC<br>Stuck</th><th>break DC<br>Locked</th></tr></thead>"""),

        (str.replace,
         """<thead><tr><th rowspan="2"></th><th colspan="3">Category of Forest </th></tr>
<tr><th>Sparse</th><th>Medium</th><th>Dense</th></tr></thead>""",

         """<caption>Table: Category of Forest</caption><thead><tr><th>Terrain</th><th>Sparse</th><th>Medium</th><th>Dense</th></tr></thead>"""),

        (str.replace,
         """<thead><tr><th rowspan="2"></th><th colspan="2">Marsh Category</th></tr>
<tr><th>Moor</th><th>Swamp</th></tr></thead>""",

         """<caption>Table: Marsh Category</caption>
<tr><th>Terrain</th><th>Moor</th><th>Swamp</th></tr></thead>"""),

        (str.replace,
         """<thead><tr><th rowspan="2"></th><th colspan="2">Hills Category</th></tr>
<tr><th>Gentle Hills</th><th>Rugged Hills</th></tr></thead>""",

         """<caption>Table: Hills Category</caption><thead>
<tr><th>Terrain</th><th>Gentle Hills</th><th>Rugged Hills</th></tr></thead>"""),

        (str.replace,
         """<thead><tr><th rowspan="2"></th><th colspan="3">Mountain Category</th></tr>
<tr><th>Alpine Meadow</th><th>Rugged</th><th>Forbidding</th></tr></thead>""",

         """<caption>Table: Mountain Category</caption><thead>
<tr><th>Terrain</th><th>Alpine Meadow</th><th>Rugged</th><th>Forbidding</th></tr></thead>"""),

        (str.replace,
         """<thead><tr><th rowspan="2"></th><th colspan="3">Desert Category</th></tr>
<tr><th>Tundra</th><th>Rocky</th><th>Sandy</th></tr></thead>""",

         """<caption>Table: Desert Category</caption>
<thead><tr><th>Terrain</th><th>Tundra</th><th>Rocky</th><th>Sandy</th></tr></thead>"""),

        (str.replace,
         """<thead>
<tr><th /><th>Farm</th><th>Grassland</th><th>Battlefield</b></th></tr></thead>""",

         """<caption>Table: Plains Category</caption>
<thead>
<tr><th>Terrain</th><th>Farm</th><th>Grassland</th><th>Battlefield</b></th></tr></thead>"""),

        (str.replace,
         """<thead><tr><th rowspan="2">Condition</th><th colspan="2">Attack/Damage</th><th rowspan="2">Movement</th><th rowspan="2">Off Balance?<sup>1</sup></th></tr>
<tr><th>Slashing or Bludgeoning</th><th>Piercing</th></tr></thead>""",

         """<thead><tr><th>Condition</th><th>Attack/Dmg.<br>Slashing or Bludgeoning</th><th>Attack/Dmg.<br>Piercing</th><th>Movement</th><th>Off Balance?<sup>1</sup></th></tr></thead>"""),

        (str.replace,
         """<thead><tr><th rowspan="2">Condition</th><th colspan="2">Attack/Damage</th><th rowspan="2">Movement</th><th rowspan="2">Off Balance?<sup>1</sup></th></tr>
<tr><th>Slashing or Bludgeoning</th><th>Piercing</th></tr></thead>""",

         """<thead><tr><th>Condition</th><th>Attack/Dmg.<br>Slashing or Bludgeoning</th><th>Attack/Dmg.<br>Piercing</th><th>Movement</th><th>Off Balance?<sup>1</sup></th></tr></thead>"""),
        (str.replace,
         'Blown Away Size<sup3</sup>',
         'Blown Away Size<sup>3</sup>'),
    ],
###############################
# end of CORERULEBOOK.ENVIRONMENT
###############################


###############################
# CORERULEBOOK.EQUIPMENT
###############################
    "corerulebook.equipment": [
        (remove_indentation, None, None ),

        (str.replace,
         """<thead><tr><td colspan="9"><i>Ranged Weapons</i></td></tr></thead>""",
         """<tr><td colspan="9"><i>Ranged Weapons</i></td></tr>"""),

        (str.replace,
         """<thead>
<tr><th rowspan="2">Armor</th><th rowspan="2">Cost</th><th rowspan="2">Armor/Shield Bonus</th><th rowspan="2">Maximum <a href="gettingStarted.html#dexterity">Dex</a> Bonus</th><th rowspan="2">Armor Check Penalty</th><th rowspan="2">Arcane Spell Failure Chance</th><th colspan="2">Speed</th><th rowspan="2">Weight<sup>1</sup></th></tr>
<tr><th>30 ft.</th><th>20 ft.</th></tr>
</thead>""",
         """<thead>
<tr><th>Armor</th><th>Cost</th><th>Armor/Shield Bonus</th><th>Maximum <a href="gettingStarted.html#dexterity">Dex</a> Bonus</th><th>Armor Check Penalty</th><th>Arcane Spell Failure Chance</th><th>Weight<sup>1</sup></th><th>Speed<br>Speed<br>30 ft.</th><th>20 ft.</th></tr>
</thead>"""),

        (str.replace,
         """<thead>
<tr><th rowspan="2">Size</th><th colspan="2">Humanoid</th><th colspan="2">Nonhumanoid</th></tr>
<tr><th>Cost</th><th>Weight</th><th>Cost</th><th>Weight</th></tr>
</thead>""",
         """<thead>
<tr><th>Size</th><th>Humanoid<br>Cost</th><th>Humanoid<br>Weight</th><th>Non-humanoid<br>Cost</th><th>Non-humanoid<br>Weight</th></tr>
</thead>"""),

        (str.replace,
         """<tr><th>Item</th><th>Cost</th><th>Weight</b></th></tr>""",
         """<tr><th>Item</th><th>Cost</th><th>Weight</th></tr>"""),

        (str.replace,
         """</th></tr>
<tr><th>Item</th><th>Cost</th><th>Weight</th></tr>
</thead>""",
         """</th><th>Cost</th><th>Weight</th></tr>
            </thead>"""),

        (str.replace,
         """</th></tr>
<tr><th>Service</th><th colspan="2">Cost</th></tr>
</thead>""",
         """</th><th colspan="2">Cost</th><th>Weight</th></tr>
            </thead>"""),
        (str.replace,
         """</thead>
</tbody>
<tr><td>Coach cab</td>""",
         """</thead>
            <tbody>
                <tr><td>Coach cab</td>"""),

        (str.replace,
         """<thead>
                <tr><th colspan="3"><i><b>Spellcasting and Services</b></i></th></tr>
                <tr><th>Service</th><th colspan="2">Cost</th></tr>
            </thead>
            </tbody>
                <tr><td>Coach cab</td><td colspan="2">3 cp per mile</td></tr>
                <tr><td>Hireling, trained</td><td colspan="2">3 sp per day</td></tr>
                <tr><td>Hireling, untrained</td><td colspan="2">1 sp per day</td></tr>
                <tr><td>Messenger</td><td colspan="2">2 cp per mile</td></tr>
                <tr><td>Road or gate toll</td><td colspan="2">1 cp</td></tr>
                <tr><td>Ship's passage</td><td colspan="2">1 sp per mile</td></tr>
                <tr><td>Spellcasting</td><td colspan="2">Caster level &times; spell level &times; 10 gp<sup>3</sup></td></tr>
            </tbody>""",
         """<thead>
                <tr><th><i><b>Spellcasting and Services</b></i></th><th>Service</th><th colspan="2">Cost</th><th>Weight</th></tr>
            </thead>
            </tbody>
                <tr><td>Coach cab</td><td colspan="2">3 cp per mile</td></tr>
                <tr><td>Hireling, trained</td><td colspan="2">3 sp per day</td></tr>
                <tr><td>Hireling, untrained</td><td colspan="2">1 sp per day</td></tr>
                <tr><td>Messenger</td><td colspan="2">2 cp per mile</td></tr>
                <tr><td>Road or gate toll</td><td colspan="2">1 cp</td></tr>
                <tr><td>Ship's passage</td><td colspan="2">1 sp per mile</td></tr>
                <tr><td>Spellcasting</td><td colspan="2">Caster level &times; spell level &times; 10 gp<sup>3</sup></td></tr>
            </tbody>"""),

        (str.replace,
         """<thead>
<tr><th rowspan="2">Barding</th><th colspan="3">Modifier</th></tr>
<tr><th>(40 ft.)</th><th>(50 ft.)</th><th>(60 ft.)</th></tr>
</thead>""",
         """<thead>
<tr><th rowspan="2">Barding / Modifier</th><th>(40 ft.)</th><th>(50 ft.)</th><th>(60 ft.)</th></tr>
</thead>"""),
    ],
###############################
# end of CORERULEBOOK.EQUIPMENT
###############################


###############################
# CORERULEBOOK.FEATS
###############################
    "corerulebook.feats": [
        (str.replace,
         """<thead><tr><th rowspan="2">Leadership Score</th><th rowspan="2">Cohort Level</th><th colspan="6">Number of Followers by Level</th></tr><tr><th>1st</th><th>2nd</th><th>3rd</th><th>4th</th><th>5th</th><th>6th</th></tr></thead>""",
        """<thead><tr><th>Leadership Score</th><th>Cohort Level</th><th>1st Level<br> Followers</th><th>2nd Level<br> Followers</th><th>3rd Level<br> Followers</th><th>4th Level<br> Followers</th><th>5th Level<br> Followers</th><th>6th Level<br> Followers</th></tr></thead>"""
            )
    ],
###############################
# end of CORERULEBOOK.FEATS
###############################


###############################
# CORERULEBOOK.GAMEMASTERING
###############################
    "corerulebook.gamemastering": [
        (str.replace,
         """<thead><tr><th rowspan="2">CR</th><th rowspan="2">Total XP</th><th colspan="3">Individual XP</th></tr>
<tr><th>1-3</th><th>4-5</th><th>6+</th></tr></thead>""",
        """<thead><tr><th rowspan="2">CR</th><th rowspan="2">Total XP</th><th>Ind. XP<br>1-3</th><th>Ind. XP<br>4-5</th><th>Ind. XP<br>6+</th></tr></thead>"""
            ),
        (str.replace,
         """<thead><tr><th rowspan="2">Average Party Level</th><th colspan="3">Treasure per Encounter</th></tr>
<tr><th>Slow</th><th>Medium</th><th>Fast</th></tr></thead>""",
        """<thead><tr><th rowspan="2">Average Party Level / Treasure</th><th>Slow</th><th>Medium</th><th>Fast</th></tr></thead>"""
            ),
    ],
###############################
# end of CORERULEBOOK.GAMEMASTERING
###############################


###############################
# CORERULEBOOK.MAGICITEMS.WONDROUSITEMS
###############################
    "corerulebook.magicitems.wondrousitems": [
        (str.replace,
         """<thead><tr><th colspan="2">Gray Bag</th><th colspan="2">Rust Bag</th><th colspan="2">Tan Bag</th></tr><tr><th>d%</th><th>Animal</th><th>d%</th><th>Animal</th><th>d%</th><th>Animal</th></tr></thead>""",
        """<thead><tr><th>Gray Bag<br>d%</th><th>Animal</th><th>Rust Bag<br>d%</th><th>Animal</th><th>Tan Bag<br>d%</th><th>Animal</th></tr></thead>"""
            ),
        (str.replace,
         '<tr><td>13</td><td><i><a href="#robe-of-bones">Robe of blending</a> </i></td><td>8,400 gp</td></tr>',
        '<tr><td>13</td><td><i><a href="#robe-of-blending">Robe of blending</a> </i></td><td>8,400 gp</td></tr>'
            ),
        (str.replace,
        '<p id="robe-of-bones" class="stat-block-title"><b>Robe of Blending</b></p>',
         '<p id="robe-of-blending" class="stat-block-title"><b>Robe of Blending</b></p>'
         ),

    ],
###############################
# end of CORERULEBOOK.MAGICITEMS.WONDROUSITEMS
###############################


###############################
# CORERULEBOOK.SKILLS.DISABLEDEVICE
###############################
    "corerulebook.skills.disabledevice": [
        (str.replace,
         """<p><table>
<thead><tr><th>Device""",
        """<table>
<thead><tr><th>Device"""
            )
    ],
###############################
# end of CORERULEBOOK.SKILLS.DISABLEDEVICE
###############################


###############################
# CORERULEBOOK.SPELLS.DETECTEVIL
###############################
    "corerulebook.spells.detectevil": [
        (str.replace,
         """<caption>Detect Chaos/Evil/Good/Law</caption>
<thead><tr><th rowspan="2">Creature/Object</th><th colspan="5">Aura Power</th></tr>
<tr><th>None</th><th>Faint</th><th>Moderate</th><th>Strong</th><th>Overwhelming</th></tr></thead>""",
        """<caption>Detect Chaos/Evil/Good/Law: Aura Power per Creature/Object</caption>
<thead><tr><th rowspan="2">Creature/Object</th><th>None</th><th>Faint</th><th>Moderate</th><th>Strong</th><th>Overwhelming</th></tr></thead>"""
            )
    ],
###############################
# end of CORERULEBOOK.SPELLS.DETECTEVIL
###############################


###############################
# CORERULEBOOK.SPELLS.DETECTMAGIC
###############################
    "corerulebook.spells.detectmagic": [
        (str.replace,
         """<table><caption>Detect Magic</caption>
<thead><tr><th rowspan="2">Spell or Object</th><th colspan="4">Aura Power</th></tr>
<tr><th>Faint</th><th>Moderate</th><th>Strong</th><th>Overwhelming</th></tr></thead>""",
        """<table><caption>Detect Magic: Aura Power per Spell or Object</caption>
<thead><tr><th rowspan="2">Spell or Object</th><th>Faint</th><th>Moderate</th><th>Strong</th><th>Overwhelming</th></tr></thead>"""
            )
    ],
###############################
# end of CORERULEBOOK.SPELLS.DETECTMAGIC
###############################


###############################
# CORERULEBOOK.SPELLS.PERMANENCY
###############################
    "corerulebook.spells.permanency": [
        (str.replace,
         """<table><th>Spell</th><th>Minimum Caster Level</th><th>GP Cost</th></tr>""",
        """<table><tr><th>Spell</th><th>Minimum Caster Level</th><th>GP Cost</th></tr>"""
            )
    ],
###############################
# end of CORERULEBOOK.SPELLS.PERMANENCY
###############################


###############################
# CORERULEBOOK.SPELLS.POLYMORPHANYOBJECT
###############################
    "corerulebook.spells.polymorphanyobject": [
        (str.replace,
         """</tfoot>
<table><br />
<thead>""",
        """</tfoot>
</table><br><table>
<thead>"""
            )
    ],
###############################
# end of CORERULEBOOK.SPELLS.POLYMORPHANYOBJECT
###############################


###############################
# CORERULEBOOK.SPELLS.PRISMATICSPRAY
###############################
    "corerulebook.spells.prismaticspray": [
        (str.replace,
         """<thead><tr><th>1d8</th><th>Color of Beam</th><th></th></tr></thead>""",
         """<thead><tr><th>1d8</th><th>Color of Beam</th><th>Effect</th></tr></thead>"""
            )
    ],
###############################
# end of CORERULEBOOK.SPELLS.PRISMATICSPRAY
###############################


###############################
# INDICES.BESTIARY
###############################
    "indices.bestiary": [
        (str.replace,
         '<a href="/pathfinderRPG/prd/bestiary/devil.html#devil-imp"></a>Devil, Imp',
         '<a href="/pathfinderRPG/prd/bestiary/devil.html#devil-imp">Devil, Imp</a>')
    ],
###############################
# end of INDICES.BESTIARY
###############################

###############################
# INDICES.FEATS
###############################
    "indices.feats": [
        (str.replace,
         # rogue td generated a col that exceeded table's col numbers
         """<tr class = "link-book-oa"><td><a href = "/pathfinderRPG/prd/occultAdventures/feats.html#lucid-dreamer">Lucid Dreamer</a></td><td>Cha 13, Knowledge (planes) 3 ranks</td><td>Gain greater control during dreams</td><td></td></tr>""",
         """<tr class = "link-book-oa"><td><a href = "/pathfinderRPG/prd/occultAdventures/feats.html#lucid-dreamer">Lucid Dreamer</a></td><td>Cha 13, Knowledge (planes) 3 ranks</td><td>Gain greater control during dreams</td></tr>"""),
        (str.replace,
         # rogue p
         """<td><p id="dispel-magic"><i><a href = "/pathfinderRPG/prd/coreRulebook/spells/dispelMagic.html#dispel-magic">Dispel magic</a>""",
         """<td><i><a href = "/pathfinderRPG/prd/coreRulebook/spells/dispelMagic.html#dispel-magic">Dispel magic</a>""")
    ],
###############################
# end of INDICES.FEATS
###############################


###############################
# INDICES.SPELLLISTS
###############################
    "indices.spelllists": [
        (remove_indentation, None, None ),
        (str.replace,
         """<table id = "spelllist" summary = "Spell List" cellspacing = "0">
<thead>
<tr><th>Level</th><th>Spell Name</th><th>School</th><th>Description</th></tr>
</thead>
<tbody>""",
         """<table id = "spelllist" summary = "Spell List" cellspacing = "0">
<thead>
<tr><th>Spell Name</th><th>School</th><th>Description</th></tr>
</thead>
<tbody>"""
            ),
        (fix_nonclosing_consecutive_tags, 'td', None)
    ],
###############################
# end of INDICES.SPELLLISTS
###############################


###############################
# MONSTERCODEX.BOGGARDS
###############################
    "monstercodex.boggards": [(
        str.replace,
        """<h1 id = "monster-codex-example-boggards">Example Boggards</h2>""",
        """<h1 id = "monster-codex-example-boggards">Example Boggards</h1>"""),
        (str.replace,
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightning-reflexes"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightnin-reflexes">Lightning Reflexes</a></a>""",
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightning-reflexes">Lightning Reflexes</a>"""),

        (str.replace,
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a></a>""",
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a>"""),
    ],
###############################
# end of MONSTERCODEX.BOGGARDS
###############################


###############################
# MONSTERCODEX.BUGBEARS
###############################
    "monstercodex.bugbears": [(
        str.replace,
        """<h1>Example Bugbears</h2>""",
        """<h1>Example Bugbears</h1>"""),
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a>"""),
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#spell-focus"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#spell-focus">Spell Focus</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#spell-focus">Spell Focus</a>"""),
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#weapon-finesse"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#weapon-finesse">Weapon Finesse</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#weapon-finesse">Weapon Finesse</a>"""),
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-reflexes"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-reflexes">Combat Reflexes</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-reflexes">Combat Reflexes</a>"""),
        (str.replace,
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightning-reflexes"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightnin-reflexes">Lightning Reflexes</a></a>""",
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightning-reflexes">Lightning Reflexes</a>"""),
        (str.replace,
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#dazzling-display"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#dazzling-display">Dazzling Display</a></a>""",
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#dazzling-display">Dazzling Display</a>"""),
    ],
###############################
# end of MONSTERCODEX.BUGBEARS
###############################


###############################
# MONSTERCODEX.FIREGIANTS
###############################
    "monstercodex.firegiants": [
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a>"""),
    ],
###############################
# end of MONSTERCODEX.FIREGIANTS
###############################


###############################
# MONSTERCODEX.FROSTGIANTS
###############################
    "monstercodex.frostgiants": [
        (str.replace,
         """<a href = "pathfinderRPG/prd/feats.html#craft-magic-arms-and-armor"><a href = "pathfinderRPG/prd/feats.html#craft-magic-arms-and-armor">Craft Magic Arms and Armor</a></a>""",
         """<a href = "pathfinderRPG/prd/feats.html#craft-magic-arms-and-armor">Craft Magic Arms and Armor</a>"""),
    ],
###############################
# end of MONSTERCODEX.FROSTGIANTS
###############################


###############################
# MONSTERCODEX.GNOLLS
###############################
    "monstercodex.gnolls": [
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a>"""),
        (str.replace,
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightning-reflexes"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightnin-reflexes">Lightning Reflexes</a></a>""",
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightning-reflexes">Lightning Reflexes</a>"""),
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#spell-focus"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#spell-focus">Spell Focus</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#spell-focus">Spell Focus</a>"""),
    ],
###############################
# end of MONSTERCODEX.GNOLLS
###############################


###############################
# MONSTERCODEX.GOBLINS
###############################
    "monstercodex.goblins": [
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#weapon-finesse"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#weapon-finesse">Weapon Finesse</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#weapon-finesse">Weapon Finesse</a>"""),
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-reflexes"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-reflexes">Combat Reflexes</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-reflexes">Combat Reflexes</a>"""),
    ],
###############################
# end of MONSTERCODEX.GOBLINS
###############################


###############################
# MONSTERCODEX.HOBGOBLINS
###############################
    "monstercodex.hobgoblins": [
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-reflexes"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-reflexes">Combat Reflexes</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-reflexes">Combat Reflexes</a>"""),
    ],
###############################
# end of MONSTERCODEX.HOBGOBLINS
###############################


###############################
# MONSTERCODEX.KOBOLDS
###############################
    "monstercodex.kobolds": [(
        str.replace,
        """<p class = "stat-block-1"></p>""",
        """""")
    ],
###############################
# end of MONSTERCODEX.KOBOLDS
###############################


###############################
# MONSTERCODEX.LIZARDFOLK
###############################
    "monstercodex.lizardfolk": [
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a>"""),
    ],
###############################
# end of MONSTERCODEX.LIZARDFOLK
###############################


###############################
# MONSTERCODEX.OGRES
###############################
    "monstercodex.ogres": [
        (str.replace,
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightning-reflexes"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightnin-reflexes">Lightning Reflexes</a></a>""",
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightning-reflexes">Lightning Reflexes</a>"""),
    ],
###############################
# end of MONSTERCODEX.OGRES
###############################


###############################
# MONSTERCODEX.ORCS
###############################
    "monstercodex.orcs": [
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a>"""),
    ],
###############################
# end of MONSTERCODEX.ORCS
###############################


###############################
# MONSTERCODEX.RATFOLK
###############################
    "monstercodex.ratfolk": [
        (str.replace,
         """<p class = "stat-block-1"></p>""",
         """"""),
        (str.replace,
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightning-reflexes"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightnin-reflexes">Lightning Reflexes</a></a>""",
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightning-reflexes">Lightning Reflexes</a>"""),
        (str.replace,
         """<p id = "riding-rat" class = "stat-block-title">Riding Rats (3) <span class = "stat-block-cr">CR &mdash;</span></p>""",
         """<p id = "riding-rats" class = "stat-block-title">Riding Rats (3) <span class = "stat-block-cr">CR &mdash;</span></p>"""),
        (str.replace,
         '<p class = "stat-block-2"></p>',
         '')

    ],
###############################
# end of MONSTERCODEX.RATFOLK
###############################

###############################
# MONSTERCODEX.SAHUAGIN
###############################
    "monstercodex.sahuagin": [
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a>"""),
        (str.replace,
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightning-reflexes"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightnin-reflexes">Lightning Reflexes</a></a>""",
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightning-reflexes">Lightning Reflexes</a>"""),
    ],
###############################
# end of MONSTERCODEX.SAHUAGIN
###############################


###############################
# MONSTERCODEX.SERPENTFOLK
###############################
    "monstercodex.serpentfolk": [
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a>"""),
        (str.replace,
         """<a href = "pathfinderRPG/prd/feats.html#craft-magic-arms-and-armor"><a href = "pathfinderRPG/prd/feats.html#craft-magic-arms-and-armor">Craft Magic Arms and Armor</a></a>""",
         """<a href = "pathfinderRPG/prd/feats.html#craft-magic-arms-and-armor">Craft Magic Arms and Armor</a>"""),
    ],
###############################
# end of MONSTERCODEX.SERPENTFOLK
###############################


###############################
# MONSTERCODEX.TROGLODYTES
###############################
    "monstercodex.troglodytes": [
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a>"""),
        (str.replace,
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightning-reflexes"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightnin-reflexes">Lightning Reflexes</a></a>""",
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightning-reflexes">Lightning Reflexes</a>"""),
    ],
###############################
# end of MONSTERCODEX.TROGLODYTES
###############################


###############################
# MONSTERCODEX.TROLLS
###############################
    "monstercodex.trolls": [
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a>"""),
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#spell-focus"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#spell-focus">Spell Focus</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#spell-focus">Spell Focus</a>"""),
        (str.replace,
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightning-reflexes"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightnin-reflexes">Lightning Reflexes</a></a>""",
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightning-reflexes">Lightning Reflexes</a>"""),
        (str.replace,
        '<h3 id = "troll-fury">Troll Fury (Druid)</h3>',
        '<h3>Troll Fury (Druid)</h3>'),
    ],
###############################
# end of MONSTERCODEX.TROLLS
###############################


###############################
# MONSTERCODEX.VAMPIRES
###############################
    "monstercodex.vampires": [
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#weapon-finesse"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#weapon-finesse">Weapon Finesse</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#weapon-finesse">Weapon Finesse</a>"""),
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-casting">Combat Casting</a>"""),
        (str.replace,
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightning-reflexes"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightnin-reflexes">Lightning Reflexes</a></a>""",
        """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#lightning-reflexes">Lightning Reflexes</a>"""),
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#spell-focus"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#spell-focus">Spell Focus</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#spell-focus">Spell Focus</a>"""),
        (str.replace,
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-reflexes"><a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-reflexes">Combat Reflexes</a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/feats.html#combat-reflexes">Combat Reflexes</a>"""),
    ],
###############################
# end of MONSTERCODEX.VAMPIRES
###############################




###############################
# MYTHICADVENTURES.MYTHICFEATS
###############################
    "mythicadventures.mythicfeats": [(
        str.replace,
        """<h1 id = "monster-codex-example-boggards">Example Boggards</h2>""",
        """<h1 id = "monster-codex-example-boggards">Example Boggards</h1>""")
    ],
###############################
# end of MYTHICADVENTURES.MYTHICFEATS
###############################


###############################
# MYTHICADVENTURES.MYTHICGAME
###############################
    "mythicadventures.mythicgame": [
    (str.replace,
     """<thead><tr><th></th><th></th><th colspan="3">Individual XP</th></tr>
<tr><th>CR</th><th>Total XP</th><th>1-3</th><th>4-5</th><th>6+</th></tr></thead>""",
     """<thead><tr><th>CR</th><th>Total XP</th><th>Ind. XP<br>1-3</th><th>Ind. XP<br>4-5</th><th>Ind. XP<br>6+</th></tr></thead>"""),
     (str.replace,
      """<thead><tr><th></th><th colspan="3">Treasure per Encounter</th></tr>
<tr><th>CR</th><th>Slow</th><th>Medium</th><th>Fast</th></tr></thead>""",
      """<thead><tr><th>CR / Treasure per Encounter</th><th>Slow</th><th>Medium</th><th>Fast</th></tr></thead>"""),
    ],
###############################
# end of MYTHICADVENTURES.MYTHICGAME
###############################


###############################
# MYTHICADVENTURES.MYTHICITEMS.MAGICITEMS
###############################
    "mythicadventures.mythicitems.magicitems": [
        (str.replace,
         """Varies</p>; <b>CL 17""",
         """Varies; <b>CL</b> 17"""),
        (str.replace,
         """Varies</p>; +1 bonus/+2 Reflex</b>""",
         """Varies; <b>+1 bonus/+2 Reflex</b>"""),
    ],
###############################
# end of MYTHICADVENTURES.MYTHICITEMS.MAGICITEMS
###############################


###############################
# MYTHICADVENTURES.MYTHICMONSTERS.MINOTAUR
###############################
    "mythicadventures.mythicmonsters.minotaur": [
        (str.replace,
         """<a href="/pathfinderRPG/prd/coreRulebook/feats.html#improved-bull-rush"><a href="/pathfinderRPG/prd/coreRulebook/feats.html#improved-bull-rush">Improved Bull Rush</a></a>""",
         """<a href="/pathfinderRPG/prd/coreRulebook/feats.html#improved-bull-rush">Improved Bull Rush</a>""")
    ],
###############################
# end of MYTHICADVENTURES.MYTHICMONSTERS.MINOTAUR
###############################



###############################
# NPCCODEX.APPENDIX
###############################
    "npccodex.appendix": [
        (str.replace,
         '<a href="/pathfinderRPG/prd/npcCodex/core/wizard.html#cruel-conjurer">cruel conjurer (human conjurer 15)<br />',
         '<a href="/pathfinderRPG/prd/npcCodex/core/wizard.html#cruel-conjurer">cruel conjurer</a> (human conjurer 15)<br />')
    ],
###############################
# end of NPCCODEX.APPENDIX
###############################



###############################
# OCCULTADVENTURES.CLASSES.MESMERIST
###############################
    "occultadventures.classes.mesmerist": [(
        str.replace,
        """<tr><td>20th</td><td>+15/+10/+5</td><td>+6</td><td>+12</td><td>+12</td><td>Mesmerist trick, rule minds</td><td>5</td><td>5</td><td>5</td><td>5</td><td>5</td></tr>""",
        """<tr><td>20th</td><td>+15/+10/+5</td><td>+6</td><td>+12</td><td>+12</td><td>Mesmerist trick, rule minds</td><td>5</td><td>5</td><td>5</td><td>5</td><td>5</td><td>5</td></tr>""")
    ],
###############################
# end of OCCULTADVENTURES.CLASSES.MESMERIST
###############################



###############################
# OCCULTADVENTURES.CLASSES.PSYCHIC
###############################
    "occultadventures.classes.psychic": [
        (
            str.replace,
            "<caption>d% Damage Reduction</caption>",
            "<tr><th>d%</th><th>Damage Reduction</th></tr>"
        ),
        (
            str.replace,
            "<tr><td>1&ndash;35 DR 5/bludgeoning</td></tr>",
            "<tr><td>1&ndash;35</td><td>DR 5/bludgeoning</td></tr>"
        ),
        (
            str.replace,
            "<tr><td>36&ndash;60 DR 5/cold iron</td></tr>",
            "<tr><td>36&ndash;60</td><td>DR 5/cold iron</td></tr>"
        ),
        (
            str.replace,
            "<tr><td>61&ndash;100 DR 5/magic</td></tr></table>",
            "<tr><td>61&ndash;100</td><td>DR 5/magic</td></tr></table>"
        ),
        (
            str.replace,
            "<i>ARG </i>",
            ", "
        )
    ],
###############################
# end of OCCULTADVENTURES.CLASSES.PSYCHIC
###############################

###############################
# OCCULTADVENTURES.FEATS
###############################
    "occultadventures.feats": [
        (str.replace,
         '</td><td></td>',
         '</td>'
        ),
    ],
###############################
# end of OCCULTADVENTURES.FEATS
###############################


###############################
# OCCULTADVENTURES.OCCULTGAME
###############################
    "occultadventures.occultgame": [
        (str.replace,
         '<h3>Incorporating the Occult</h3>',
         '<h2>Incorporating the Occult</h2>')
    ],
###############################
# end of OCCULTADVENTURES.OCCULTGAME
###############################


###############################
# OCCULTADVENTURES.OCCULTREWARDS
###############################
    "occultadventures.occultrewards": [
        (str.replace,
         '<thead><tr><th>Lesser Major Rods</th><th>Price</th></tr></thead>',
         '</tbody><thead><tr><th>Lesser Major Rods</th><th>Price</th></tr></thead><tbody>'
        ),
        (str.replace,
         '<thead><tr><th>Greater Major Rods</th><th>Price</th></tr></thead>',
         '</tbody><thead><tr><th>Greater Major Rods</th><th>Price</th></tr></thead><tbody>'
        ),
        (str.replace,
         '</th><th></tr>',
         '</th></tr>'
        ),
    ],
###############################
# end of OCCULTADVENTURES.OCCULTREWARDS
###############################



###############################
# OCCULTADVENTURES.OCCULTRULES
###############################
    "occultadventures.occultrules": [
        (
            str.replace,
            """<tr><td>Suspend affliction</td><td>Affliction's save DC</td></tr>\n<table>""",
            """<tr><td>Suspend affliction</td><td>Affliction's save DC</td></tr>"""
        ),
        (
            str.replace,
            """</td></tr></tfoot>
<table>
<p><b>""",
            """</td></tr></tfoot>
</table>
<p><b>"""
        ),
        (
            str.replace,
"""<table><caption>Modifying Occult Rituals</caption>
<thead><tr><th>Casting Time</th><th>Check DC Modifier or Modification</th></tr></thead>
<tbody><tr><td>Casting time is restricted (such as "only during a full moon")</td><td>-4</td></tr>
<tr><td>Casting time is severely restricted (such as "only during a lunar eclipse")</td><td>-8</td></tr>
<thead><tr><th>Focus and Material Components</th><th></th></tr></thead>
<tbody><tr><td>Expensive material component (500 gp)</td><td>-1</td></tr>
<tr><td>Expensive material component (5,000 gp)</td><td>-2</td></tr>
<tr><td>Expensive material component (25,000 gp)</td><td>-4</td></tr>
<tr><td>Expensive focus (5,000 gp)</td><td>-1</td></tr>
<tr><td>Expensive focus (25,000 gp)</td><td>-2</td></tr></tbody>
<thead><tr><th>Range</th><th></th></tr></thead>
<tbody><tr><td>Greater range than normal</td><td>+1 to +6</td></tr>
<tr><td>Shorter range than normal</td><td>-1 to -4</td></tr></tbody>
<thead><tr><th>Area</th><th></th></tr></thead>
<tbody><tr><td>Larger area than normal</td><td>+1 to +6</td></tr>
<tr><td>Smaller area than normal</td><td>-1 to -4</td></tr></tbody>
<thead><tr><th>Target</th><th></th></tr></thead>
<tbody><tr><td>Unwilling target must be helpless</td><td>-2</td></tr>
<tr><td>Limited targets (by HD, creature type, and so on)</td><td>-3</td></tr>
<tr><td>Single target to multiple targets</td><td>4</td></tr></tbody>
<thead><tr><th>Duration</th><th></th></tr></thead>
<tbody><tr><td>Greater duration than normal</td><td>+1 to +6</td></tr>
<tr><td>Shorter duration than normal</td><td>-1 to -4</td></tr>
<tr><td>One year or more</td><td>casting time in increments of 1 hour/level instead of 10 minutes/level</td></tr></tbody>
<thead><tr><th>Backlash</th><th></th></tr></thead>
<tbody><tr><td>Per 2d6 points of damage</td><td>-1</td></tr>
<tr><td>Caster is exhausted</td><td>-2</td></tr>
<tr><td>Per temporary negative level caster gains</td><td>-2</td></tr>
<tr><td>Per permanent negative level caster gains</td><td>-4</td></tr>
<tr><td>Caster reduced to -1 hp</td><td>-3</td></tr>
<tr><td>Caster infected with disease</td><td>-4</td></tr>
<tr><td>Caster suffers curse effects</td><td>-4</td></tr>
<tr><td>Backlash affects secondary casters too</td><td>-1</td></tr></tbody></table>""",

"""
<table>
    <caption>Modifying Occult Rituals</caption>
    <tr>
        <th>Casting Time</th>
        <th>Check DC Modifier or Modification</th>
    </tr>

    <tr>
        <td>Casting time is restricted (such as "only during a full moon")</td>
        <td>-4</td>
    </tr>
    <tr>
        <td>Casting time is severely restricted (such as "only during a lunar eclipse")</td>
        <td>-8</td>
    </tr>
</table>

<table>
        <tr>
            <th>Focus and Material Components</th>
            <th>Check DC Modifier or Modification</th>
        </tr>

        <tr>
            <td>Expensive material component (500 gp)</td>
            <td>-1</td>
        </tr>
        <tr>
            <td>Expensive material component (5,000 gp)</td>
            <td>-2</td>
        </tr>
        <tr>
            <td>Expensive material component (25,000 gp)</td>
            <td>-4</td>
        </tr>
        <tr>
            <td>Expensive focus (5,000 gp)</td>
            <td>-1</td>
        </tr>
        <tr>
            <td>Expensive focus (25,000 gp)</td>
            <td>-2</td>
        </tr>
</table>

<table>
        <tr>
            <th>Range</th>
            <th>Check DC Modifier or Modification</th>
        </tr>

        <tr>
            <td>Greater range than normal</td>
            <td>+1 to +6</td>
        </tr>
        <tr>
            <td>Shorter range than normal</td>
            <td>-1 to -4</td>
        </tr>
</table>

<table>
        <tr>
            <th>Area</th>
            <th>Check DC Modifier or Modification</th>
        </tr>

        <tr>
            <td>Larger area than normal</td>
            <td>+1 to +6</td>
        </tr>
        <tr>
            <td>Smaller area than normal</td>
            <td>-1 to -4</td>
        </tr>
</table>

<table>
        <tr>
            <th>Target</th>
            <th>Check DC Modifier or Modification</th>
        </tr>

        <tr>
            <td>Unwilling target must be helpless</td>
            <td>-2</td>
        </tr>
        <tr>
            <td>Limited targets (by HD, creature type, and so on)</td>
            <td>-3</td>
        </tr>
        <tr>
            <td>Single target to multiple targets</td>
            <td>4</td>
        </tr>
</table>

<table>
    <tr>
        <th>Duration</th>
        <th>Check DC Modifier or Modification</th>
    </tr>

    <tr>
        <td>Greater duration than normal</td>
        <td>+1 to +6</td>
    </tr>
    <tr>
        <td>Shorter duration than normal</td>
        <td>-1 to -4</td>
    </tr>
    <tr>
        <td>One year or more</td>
        <td>casting time in increments of 1 hour/level instead of 10 minutes/level</td>
    </tr>
</table>

<table>
    <tr>
        <th>Backlash</th>
        <th>Check DC Modifier or Modification</th>
    </tr>

    <tr>
        <td>Per 2d6 points of damage</td>
        <td>-1</td>
    </tr>
    <tr>
        <td>Caster is exhausted</td>
        <td>-2</td>
    </tr>
    <tr>
        <td>Per temporary negative level caster gains</td>
        <td>-2</td>
    </tr>
    <tr>
        <td>Per permanent negative level caster gains</td>
        <td>-4</td>
    </tr>
    <tr>
        <td>Caster reduced to -1 hp</td>
        <td>-3</td>
    </tr>
    <tr>
        <td>Caster infected with disease</td>
        <td>-4</td>
    </tr>
    <tr>
        <td>Caster suffers curse effects</td>
        <td>-4</td>
    </tr>
    <tr>
        <td>Backlash affects secondary casters too</td>
        <td>-1</td>
    </tr>
</table>""",
        )
    ],
###############################
# end of OCCULTADVENTURES.OCCULTRULES
###############################


###############################
# OPENGAMELICENSE
###############################
    "opengamelicense": [
        (str.replace,
         '<i>Tome of Horrors, Revised</b></i>',
         '<i>Tome of Horrors, Revised</i></b>'),
        (str.replace,
         '</b></p>',
         '</p>'),

    ],
###############################
# end of OPENGAMELICENSE
###############################


###############################
# TECHNOLOGYGUIDE.ARMOR
###############################
    "technologyguide.armor": [
        (remove_indentation, None, None),

        (str.replace,
         """<tr><th colspan = "11">Medium Armor</th></tr>
</thead>
<tbody>
<tr><td>Panic suit</td>""",
        """<tr>
<th>Medium Armor</th><th>Price</th><th>Armor/Shield Bonus</th><th>Max. Dex Bonus</th><th>Armor Check Penalty</th><th>Arcane Spell Failure Chance</th><th>Speed (30 ft.)</th><th>Speed (20 ft.)</th><th>Weight</th><th>Capacity</th><th>Usage</th>
</tr></thead>
<tbody>
    <tr><td>Panic suit</td>"""
         ),

        (str.replace,
         """<tr><th colspan = "11">Heavy Armor</th></tr>
</thead>
<tbody>
<tr><td>Spacesuit</td>""",
        """<tr>
<th>Heavy Armor</th><th>Price</th><th>Armor/Shield Bonus</th><th>Max. Dex Bonus</th><th>Armor Check Penalty</th><th>Arcane Spell Failure Chance</th><th>Speed (30 ft.)</th><th>Speed (20 ft.)</th><th>Weight</th><th>Capacity</th><th>Usage</th>
</tr></thead>
<tbody>
        <tr><td>Spacesuit</td>"""
         ),

        (str.replace,
         """<tr><th colspan = "11">Shields</th></tr>
</thead>
<tbody>
<tr><td>Hard light shield</td>""",
        """<tr><th>Shields</th><th>Price</th><th>Armor/Shield Bonus</th><th>Max. Dex Bonus</th><th>Armor Check Penalty</th><th>Arcane Spell Failure Chance</th><th>Speed (30 ft.)</th><th>Speed (20 ft.)</th><th>Weight</th><th>Capacity</th><th>Usage</th>
</tr></thead>
    <tbody>
        <tr><td>Hard light shield</td>"""
         ),
    ],
###############################
# end of TECHNOLOGYGUIDE.ARMOR
###############################



###############################
# TECHNOLOGYGUIDE.CYBERTECH
###############################
    "technologyguide.cybertech": [
        (str.replace,
         """<tr><th colspan = "5">Body Slot Cybertech</th></tr>""",
         """<tr><th>Body Slot Cybertech</th><th>Price</th><th>Weight</th><th>Implant</th><th>Install</th></tr>"""),
        (str.replace,
         """<tr><th colspan = "5">Brain Slot Cybertech</th></tr>""",
         """<tr><th>Brain Slot Cybertech</th><th>Price</th><th>Weight</th><th>Implant</th><th>Install</th></tr>"""),
        (str.replace,
         """<tr><th colspan = "5">Ears Slot Cybertech</th></tr>""",
         """<tr><th>Ears Slot Cybertech</th><th>Price</th><th>Weight</th><th>Implant</th><th>Install</th></tr>"""),
        (str.replace,
         """<tr><th colspan = "5">Eyes Slot Cybertech</th></tr>""",
         """<tr><th>Eyes Slot Cybertech</th><th>Price</th><th>Weight</th><th>Implant</th><th>Install</th></tr>"""),
        (str.replace,
         """<tr><th colspan = "5">Head Slot Cybertech</th></tr>""",
         """<tr><th>Head Slot Cybertech</th><th>Price</th><th>Weight</th><th>Implant</th><th>Install</th></tr>"""),
        (str.replace,
         """<tr><th colspan = "5">Legs Slot Cybertech</th></tr>""",
         """<tr><th>Legs Slot Cybertech</th><th>Price</th><th>Weight</th><th>Implant</th><th>Install</th></tr>"""),
        (str.replace,
         """<tr><th colspan = "5">Slotless Cybertech</th></tr>""",
         """<tr><th>Slotless Cybertech</th><th>Price</th><th>Weight</th><th>Implant</th><th>Install</th></tr>"""),
    ],
###############################
# end of TECHNOLOGYGUIDE.CYBERTECH
###############################



###############################
# TECHNOLOGYGUIDE.GEAR
###############################
    "technologyguide.gear": [
        (str.replace,
         '<tr><th colspan = "3">Batteries and Power</th></tr>',
         '<tr><th>Batteries and Power</th><th>Price</th><th>Weight</th></tr>'),

        (str.replace,
         '<tr><th colspan = "3">Grenades and Explosives</th></tr>',
         '<tr><th>Grenades and Explosives</th><th>Price</th><th>Weight</th></tr>'),

        (str.replace,
         '<tr><th colspan = "3">Implants, Medical Devices, and Nanotech</th></tr>',
         '<tr><th>Implants, Medical Devices, and Nanotech</th><th>Price</th><th>Weight</th></tr>'),

        (str.replace,
         '<tr><th colspan = "3">Other Tools and Accessories</th></tr>',
         '<tr><th>Other Tools and Accessories</th><th>Price</th><th>Weight</th></tr>'),
    ],
###############################
# end of TECHNOLOGYGUIDE.GEAR
###############################



###############################
# TECHNOLOGYGUIDE.HAZARDS
###############################
    "technologyguide.hazards": [
        (str.replace,
         '<li>When</td><td>an item ',
         '<li>When an item ')
    ],
###############################
# end of TECHNOLOGYGUIDE.HAZARDS
###############################



###############################
# TECHNOLOGYGUIDE.WEAPONS
###############################
    "technologyguide.weapons": [
        (
            str.replace,
            '<tr><th colspan = "11">Exotic Weapons</th></tr>',
            '<tr><th>Exotic Weapons</th><th>Price</th><th>Dmg (S)</th><th>Dmg (M)</th><th>Critical</th><th>Range</th><th>Capacity</th><th>Usage</th><th>Weight</th><th>Type<sup>1</sup></th><th>Special</th></tr>'
        ),
        (
            str.replace,
            '<tr><th colspan = "11">One-Handed Ranged Weapons (Firearms)</th></tr>',
            '<tr><th>One-Handed Ranged Weapons (Firearms)</th><th>Price</th><th>Dmg (S)</th><th>Dmg (M)</th><th>Critical</th><th>Range</th><th>Capacity</th><th>Usage</th><th>Weight</th><th>Type<sup>1</sup></th><th>Special</th></tr>'
        ),
        (
            str.replace,
            '<tr><th colspan = "11">Two-Handed Ranged Weapons (Firearms)</th></tr>',
            '<tr><th>Two-Handed Ranged Weapons (Firearms)</th><th>Price</th><th>Dmg (S)</th><th>Dmg (M)</th><th>Critical</th><th>Range</th><th>Capacity</th><th>Usage</th><th>Weight</th><th>Type<sup>1</sup></th><th>Special</th></tr>'
        ),
        (
            str.replace,
            '<tr><th colspan = "11">Two-Handed Ranged Weapons (Heavy Weaponry)</th></tr>',
            '<tr><th>Two-Handed Ranged Weapons (Heavy Weaponry)</th><th>Price</th><th>Dmg (S)</th><th>Dmg (M)</th><th>Critical</th><th>Range</th><th>Capacity</th><th>Usage</th><th>Weight</th><th>Type<sup>1</sup></th><th>Special</th></tr>'
        ),
    ],
###############################
# end of TECHNOLOGYGUIDE.WEAPONS
###############################


###############################
# ULTIMATECAMPAIGN.CAMPAIGNSYSTEMS.CONTACTS
###############################
    "ultimatecampaign.campaignsystems.contacts": [
        (
            str.replace,
            '<thead><tr><th colspan="2">NPC Trust (Score)</th><a href="/pathfinderRPG/prd/coreRulebook/skills/diplomacy.html#diplomacy" >Diplomacy</a> DC*</th></tr></thead>',
            '<thead><tr><th>NPC Trust (Score)</th><th><a href="/pathfinderRPG/prd/coreRulebook/skills/diplomacy.html#diplomacy" >Diplomacy</a> DC*</th></tr></thead>'
        )
    ],
###############################
# end of ULTIMATECAMPAIGN.CAMPAIGNSYSTEMS.CONTACTS
###############################



###############################
# ULTIMATECAMPAIGN.DOWNTIME.DOWNTIMEEVENTS
###############################
    "ultimatecampaign.downtime.downtimeevents": [
        (
            str.replace,
            '<tr><td>99&mdash;100</td><td>Roll twice</td></tr><table>',
            '<tr><td>99&mdash;100</td><td>Roll twice</td></tr></table>'
        )
    ],
###############################
# end of ULTIMATECAMPAIGN.DOWNTIME.DOWNTIMEEVENTS
###############################


###############################
# ULTIMATECOMBAT.CLASSARCHETYPES.FIGHTER
###############################
    "ultimatecombat.classarchetypes.fighter": [
        (str.replace,
         """<a href="/pathfinderRPG/prd/ultimateCombat/combat/gladiatorWeapons.html#table-gladiator-weapons"><a href="/pathfinderRPG/prd/ultimateCombat/combat/gladiatorWeapons.html#table-gladiator-weapons">pata</a>""",
         """<a href="/pathfinderRPG/prd/ultimateCombat/combat/gladiatorWeapons.html#table-gladiator-weapons">pata</a>""")
    ],
###############################
# end of ULTIMATECOMBAT.CLASSARCHETYPES.FIGHTER
###############################

###############################
# ULTIMATECOMBAT.COMBAT.EASTERNARMORANDWEAPONS
###############################
    "ultimatecombat.combat.easternarmorandweapons": [
        (
            str.replace,
            '<thead><tr><th>Armor</th><th>Cost</th><th>Armor<br>Bonus</th><th>Maximum<br>Dex Bonus</th><th>Armor<br>Check Penalty</th><th>Arcane Spell<br>Failure</th><th colspan="2">Speed<br><div style="float:left;">30ft</div><div style="float:right;">20ft</div></th><th>Weight</th></tr></thead>',
            '<thead><tr><th>Armor</th><th>Cost</th><th>Armor<br>Bonus</th><th>Maximum<br>Dex Bonus</th><th>Armor<br>Check Penalty</th><th>Arcane Spell<br>Failure</th><th>Speed<br>30ft</th><th>Speed<br>20ft</th><th>Weight</th></tr></thead>'
        )
    ],
###############################
# end of ULTIMATECOMBAT.COMBAT.EASTERNARMORANDWEAPONS
###############################


###############################
# ULTIMATECOMBAT.COMBAT.FIREARMS
###############################
    "ultimatecombat.combat.firearms": [
        (
            str.replace,
            '<thead><tr><th>Item</th><th>Cost</th><th>Weight</th></tr><thead>',
            '<thead><tr><th>Item</th><th>Cost</th><th>Weight</th></tr></thead>'
        )
    ],
###############################
# end of ULTIMATECOMBAT.COMBAT.FIREARMS
###############################


###############################
# ULTIMATECOMBAT.COMBAT.SIEGEENGINES
###############################
    "ultimatecombat.combat.siegeengines": [
        (remove_indentation, None, None),

        (str.replace,
         """<thead><tr><th></th><th></th><th colspan="4">Hit Points</th></tr>
<tr><th rowspan="2">Material</th><th>Hardness</th><th>Large</th><th>Huge</th><th>Colossal</th><th>Gargantuan</th></tr></thead>""",
         """<thead><tr><th>Material</th><th>Hardness</th><th>Hit Points<br>Large</th><th>Hit Points<br>Huge</th><th>Hit Points<br>Colossal</th><th>Hit Points<br>Gargantuan</th></tr></thead>"""
        ),
        (str.replace,
         """<thead>
<tr><th></th><th></th><th></th><th colspan="4">Hit Points</th></tr>
<tr><th>Material</th><th>Break DC<sup>1</sup></th><th>Hardness</th><th>Large</th><th>Huge</th><th>Colossal</th><th>Gargantuan</th></tr>
</thead>""",
         """<thead><tr><th>Material</th><th>Break DC<sup>1</sup></th><th>Hardness</th><th>Hit Points<br>Large</th><th>Hit Points<br>Huge</th><th>Hit Points<br>Colossal</th><th>Hit Points<br>Gargantuan</th></tr></thead>"""
        ),
    ],
###############################
# end of ULTIMATECOMBAT.COMBAT.SIEGEENGINES
###############################



###############################
# ULTIMATECOMBAT.VARIANTS.PIECEMEALARMOR
###############################
    "ultimatecombat.variants.piecemealarmor": [
        (
            str.replace,
            """<th colspan="2">Speed<br><div style="float:left">30 ft.</div><div style="float:right">20 ft.</div></th>""",
            """<th>Speed<br>30 ft.<th>Speed<br>20 ft.</th></th>"""
        )
    ],
###############################
# end of ULTIMATECOMBAT.VARIANTS.PIECEMEALARMOR
###############################



###############################
# ULTIMATEEQUIPMENT.APPENDIX
###############################
    "ultimateequipment.appendix": [
        (remove_lines, (15, 337), (2701, 2707), (2713, 2725)),

        (remove_indentation, None, None),

        (remove_empty_lines, None, None),

        (str.replace,
         """</table></td><td></td><td>
</td><td></td><td>
<table""",
         """</table>
<table"""),

        (str.replace,
         '<caption>Random Armor or Shield</td></tr>',
         '<caption>Random Armor or Shield</caption>'),

        (str.replace,
         '<i><a href',
         '<a href'),

        (str.replace,
         '<td></i>',
         '<td>'),

        (str.replace,
         '</a></i>',
         '</a>'),

        (str.replace,
         '<i>',
         ''),
        (str.replace,
         '</i>',
         ''),

        (str.replace,
         """<td><a href="/pathfinderRPG/prd/coreRulebook/spells/catSGrace.html#cat-s-grace-mass" >Cat's <a href="/pathfinderRPG/prd/advancedPlayersGuide/spells/grace.html#grace" >grace</a>, mass</a></td>""",
         """<td><a href="/pathfinderRPG/prd/coreRulebook/spells/catSGrace.html#cat-s-grace-mass" >Cat's grace, mass</a></td>"""),

        (str.replace,
         """<td><a href="/pathfinderRPG/prd/coreRulebook/spells/globeOfInvulnerability.html#globe-of-invulnerability-lesser" >Globe of <a href="/pathfinderRPG/prd/coreRulebook/magicItems/armor.html#armor-invulnerability" >invulnerability</a>, lesser</a></td>""",
         """<td><a href="/pathfinderRPG/prd/coreRulebook/spells/globeOfInvulnerability.html#globe-of-invulnerability-lesser" >Globe of invulnerability, lesser</a></td>"""),

        (str.replace,
         """<td><a href="/pathfinderRPG/prd/coreRulebook/spells/planarBinding.html#planar-binding-greater" >Planar <a href="/pathfinderRPG/prd/coreRulebook/spells/binding.html#binding" >binding</a>, greater</a></td>""",
         """<td><a href="/pathfinderRPG/prd/coreRulebook/spells/planarBinding.html#planar-binding-greater" >Planar binding, greater</a></td>"""),

        (str.replace,
         """<a href="/pathfinderRPG/prd/coreRulebook/spells/foxSCunning.html#fox-s-cunning-mass" >Fox's <a href="/pathfinderRPG/prd/advancedPlayersGuide/magicItems/weapons.html#cunning" >cunning</a>, mass</a>""",
         """<a href="/pathfinderRPG/prd/coreRulebook/spells/foxSCunning.html#fox-s-cunning-mass" >Fox's cunning, mass</a>"""),

        (str.replace,
         """<a href="/pathfinderRPG/prd/coreRulebook/spells/planarBinding.html#planar-binding-lesser" >Planar <a href="/pathfinderRPG/prd/coreRulebook/spells/binding.html#binding" >binding</a>, lesser</a>""",
         """<a href="/pathfinderRPG/prd/coreRulebook/spells/planarBinding.html#planar-binding-lesser" >Planar binding, lesser</a>"""),
        (str.replace,
         '<td colspan="3">*Can dispel permanent negative levels.</tr></td>',
         '<td colspan="3">*Can dispel permanent negative levels.</td></tr>'),

        (str.replace,
         """</table>
</td><td>""",
         """</table>\n"""),

        (str.replace,
         """</td></tr>
</td><td></td><td><tr>""",
         """</td></tr>
<tr>"""),

        (str.replace,
         """</td></tr>
<table""",
         """</td></tr></table>
<table"""),

        (str.replace,
         """</td></tr>
<div class = "table"><table""",
         """</td></tr></table>
<div class = "table"><table"""),

        (str.replace,
         """<caption>0-Level Divine Scrolls</td></tr>
<thead>""",
         """<caption>0-Level Divine Scrolls</caption>
<thead>"""),
    ],
###############################
# end of ULTIMATEEQUIPMENT.APPENDIX
###############################


###############################
# ULTIMATEEQUIPMENT.GEAR.ALCHEMICALWEAPONS
###############################
    "ultimateequipment.gear.alchemicalweapons": [
        (str.replace,
         '<thead><tr><th colspan="8"><span style="float: left;">One-handed Melee Weapons</span></th></tr></thead>',
         '<thead><tr><th>One-handed Melee Weapons</th><th>Price</th><th>Dmg</th><th>Critical</th><th>Range</th><th>Weight</th><th>Type</th><th>Special</th></tr></thead>'),
        (str.replace,
         '<thead><tr><th colspan="8"><span style="float: left;">Ranged Weapons</span></th></tr></thead>',
         '<thead><tr><th>Ranged Weapons</th><th>Price</th><th>Dmg</th><th>Critical</th><th>Range</th><th>Weight</th><th>Type</th><th>Special</th></tr></thead>'),
    ],
###############################
# end of ULTIMATEEQUIPMENT.GEAR.ALCHEMICALWEAPONS
###############################


###############################
# ULTIMATEEQUIPMENT.WONDROUSITEMS.BODY
###############################
    "ultimateequipment.wondrousitems.body": [
        (str.replace,
         '<tr><td>61&ndash;75</td><td><i>Eidolon anchoring harness</td><td></i>6,000 gp</td></tr>',
         '<tr><td>61&ndash;75</td><td><i>Eidolon anchoring harness</i></td><td>6,000 gp</td></tr>'),
        (str.replace,
         '<tr><td>77&ndash;100</td><td><i>Robe of scintillating colors</i></td><td>27,000 gp</p>',
         '<tr><td>77&ndash;100</td><td><i>Robe of scintillating colors</i></td><td>27,000 gp</td></tr>')
    ],
###############################
# end of ULTIMATEEQUIPMENT.WONDROUSITEMS.BODY
###############################


###############################
# ULTIMATEEQUIPMENT.WONDROUSITEMS.FEET
###############################
    "ultimateequipment.wondrousitems.feet": [
        (str.replace,
         '<span class="stat-block-1-char "',
         '<span class="stat-block-1-char"'
        ),
        (str.replace,
         '<p class="stat-block-1"><b>+1 enhancement bonus</b> 2,000 gp; <b>+2 enhancement bonus</b> 8,000 gp</p>; <b>+3 enhancement bonus</b> 18,000 gp; <b>+4 enhancement bonus</b> 32,000 gp; <b>+5 enhancement bonus</b> 50,000 gp</p>',
         '<p class="stat-block-1"><b>+1 enhancement bonus</b> 2,000 gp; <b>+2 enhancement bonus</b> 8,000 gp; <b>+3 enhancement bonus</b> 18,000 gp; <b>+4 enhancement bonus</b> 32,000 gp; <b>+5 enhancement bonus</b> 50,000 gp.</p>'
        ),
    ],
###############################
# end of ULTIMATEEQUIPMENT.WONDROUSITEMS.FEET
###############################


###############################
# ULTIMATEEQUIPMENT.ARMSANDARMOR.ARMOR
###############################
    "ultimateequipment.armsandarmor.armor": [
        (str.replace,
         """<thead><tr><th>Size</th><th colspan="2">Humanoid<br /><span style="float: left;">Price</span>&nbsp;<span style="float: right;">Weight</span></th><th colspan="2">Non-Humanoid<br /><span style="float: left;">Price</span>&nbsp;<span style="float: right;">Weight</span></th></tr></thead>""",
         """<thead>
<tr><th>Size</th><th>Humanoid<br>Price</th><th>Humanoid<br>Weight</th><th>Nonhumanoid<br>Price</th><th>Nonhumanoid<br>Weight</th></tr>
</thead>"""),
        (str.replace,
            """<th>Price</th><th>Armor/Shield<br />Bonus</th><th>Max<br />Dex Bonus</th><th>Armor<br />Check Penalty</th><th>Arcane Spell<br />Failure Chance</th><th colspan="2">Speed<br /><span style="float: left;">30 ft.</span>&nbsp;<span style="float: right;">20 ft.</span></th><th>Weight<sup>1</sup></th></tr></thead>""",
            """<th>Price</th><th>Armor/Shield<br>Bonus</th><th>Max<br>Dex Bonus</th><th>Armor<br>Check Penalty</th><th>Arcane Spell<br>Failure Chance</th><th>Speed<br>30 ft.</th><th >Speed<br>20 ft.</th><th>Weight<sup>1</sup></th></tr></thead>""")
    ],
###############################
# end of ULTIMATEEQUIPMENT.ARMSANDARMOR.ARMOR
###############################

###############################
# ULTIMATEEQUIPMENT.ARMSANDARMOR.WEAPONS
###############################
    "ultimateequipment.armsandarmor.weapons": [
        (str.replace,
         '<thead><tr><th colspan="9">Light Melee Weapons</th></tr></thead>',
         '<thead><tr><th>Light Melee Weapons</th><th>Price</th><th>Dmg (S)</th><th>Dmg (M)</th><th>Critical</th><th>Range</td><th>Weight</th><th>Type</th><th>Special</th></tr></thead>'),
        (str.replace,
         '<thead><tr><th colspan="9">One-Handed Melee Weapons</th></tr><thead>',
         '<thead><tr><th>One-Handed Melee Weapons</th><th>Price</th><th>Dmg (S)</th><th>Dmg (M)</th><th>Critical</th><th>Range</td><th>Weight</th><th>Type</th><th>Special</th></tr></thead>'),
        (str.replace,
         '<thead><tr><th colspan="9">Two-Handed Melee Weapons</th></tr></thead>',
         '<thead><tr><th>Two-Handed Melee Weapons</th><th>Price</th><th>Dmg (S)</th><th>Dmg (M)</th><th>Critical</th><th>Range</td><th>Weight</th><th>Type</th><th>Special</th></tr></thead>'),
        (str.replace,
         '<thead><tr><th colspan="9">Ranged Weapons</th></tr></thead>',
         '<thead><tr><th>Ranged Weapons</th><th>Price</th><th>Dmg (S)</th><th>Dmg (M)</th><th>Critical</th><th>Range</td><th>Weight</th><th>Type</th><th>Special</th></tr></thead>'),
        (str.replace,
         '<thead><tr><th colspan="9"><span style="float: left;">One-Handed Melee Weapons</span></td></tr></thead>',
         '<thead><tr><th>One-Handed Melee Weapons</th><th>Price</th><th>Dmg (S)</th><th>Dmg (M)</th><th>Critical</th><th>Range</td><th>Weight</th><th>Type</th><th>Special</th></tr></thead>'),
        (str.replace,
         '<thead><tr><th colspan="9"><span style="float: left;">Two-Handed Melee Weapons</span></td></tr></thead>',
         '<thead><tr><th>Two-Handed Melee Weapons</th><th>Price</th><th>Dmg (S)</th><th>Dmg (M)</th><th>Critical</th><th>Range</td><th>Weight</th><th>Type</th><th>Special</th></tr></thead>'),
        (str.replace,
         '<thead><tr><th colspan="9"><span style="float: left;">Ranged Weapons</span></td></tr></thead>',
         '<thead><tr><th>Ranged Weapons</th><th>Price</th><th>Dmg (S)</th><th>Dmg (M)</th><th>Critical</th><th>Range</td><th>Weight</th><th>Type</th><th>Special</th></tr></thead>'),
        (str.replace,
         '<thead><tr><th colspan="11"><span style="float: left;">Two-Handed Ranged Weapons (Early Firearms)</span></th></tr></thead>',
         '<thead><tr><th>Two-Handed Ranged Weapons (Early Firearms)</th><th>Price</th><th>Dmg (S)</th><th>Dmg (M)</th><th>Critical</th><th>Range</th><th>Misfire</th><th>Capacity</th><th>Weight</th><th>Type</th><th>Special</th></tr></thead>'),
        (str.replace,
         '<thead><tr><th colspan="11"><span style="float: left;">One-Handed Ranged Weapons (Advanced Firearms)</span></th></tr></thead>',
         '<thead><tr><th>One-Handed Ranged Weapons (Advanced Firearms)</th><th>Price</th><th>Dmg (S)</th><th>Dmg (M)</th><th>Critical</th><th>Range</th><th>Misfire</th><th>Capacity</th><th>Weight</th><th>Type</th><th>Special</th></tr></thead>'),
    ],
###############################
# end of ULTIMATEEQUIPMENT.ARMSANDARMOR.WEAPONS
###############################



###############################
# ULTIMATEEQUIPMENT.ARTIFACTSANDOTHERS.ARTIFACTS
###############################
    "ultimateequipment.artifactsandothers.artifacts": [
        (str.replace,
         """<table id="table-1" class="basic-table">
<p""",
         """<p""")
    ],
###############################
# end of ULTIMATEEQUIPMENT.ARTIFACTSANDOTHERS.ARTIFACTS
###############################


###############################
# ULTIMATEEQUIPMENT.ARTIFACTSANDOTHERS.CURSEDITEMS
###############################
    "ultimateequipment.artifactsandothers.curseditems": [
        (str.replace,
         """<p><i>Dependent</i>: The item only functions in certain situations. To determine the situation, select or roll on the following table.</p>
</blockquote>""",
         """<p><i>Dependent</i>: The item only functions in certain situations. To determine the situation, select or roll on the following table.</p>
<blockquote>"""),
        (str.replace,
         """<blockquote>
<p><i>Uncontrolled</i>: An uncontrolled item occasionally activates at random times. Roll d% every day. On a result of 01&ndash;05, the item activates at some random point during that day. </p>""",
         """</blockquote>
<p><i>Uncontrolled</i>: An uncontrolled item occasionally activates at random times. Roll d% every day. On a result of 01&ndash;05, the item activates at some random point during that day. </p>""")
    ],
###############################
# end of ULTIMATEEQUIPMENT.ARTIFACTSANDOTHERS.CURSEDITEMS
###############################


###############################
# ULTIMATEEQUIPMENT.RINGSRODSSTAVES.RINGS
###############################
    "ultimateequipment.ringsrodsstaves.rings": [
        (str.replace,
         """<p class="stat-block"><b>Ring of Elemental Command (Water)</b></p>
<li>""",
         """<p class="stat-block"><b>Ring of Elemental Command (Water)</b></p>
<ul>
<li>""")
    ],
###############################
# end of ULTIMATEEQUIPMENT.RINGSRODSSTAVES.RINGS
###############################


###############################
# ULTIMATEEQUIPMENT.WONDROUSITEMS.SLOTLESS
###############################
    "ultimateequipment.wondrousitems.slotless": [
        (str.replace,
         """<thead><tr><th colspan="2">Gray Bag<br /><span style="float: left;">d%</span> <span class="float: right;">Animal</span></th><th colspan="2">Rust Bag<br /><span style="float: left;">d%</span> <span class="float: right;">Animal</span></th><th colspan="2">Tan Bag<br /><span style="float: left;">d%</span> <span class="float: right;">Animal</span></th></tr></thead>""",
         """<thead><tr><th>Gray Bag<br>d%</th><th>Animal</th><th>Rust Bag<br>d%</th><th>Animal</th><th>Tan Bag<br>d%</th><th>Animal</th></tr></thead>"""),
        (str.replace,
         '<tr><td>11<i></td><td>Ioun stone (scarlet and blue sphere)</i></td><td>8,000 gp</td></tr>',
         '<tr><td>11</td><td>Ioun stone (scarlet and blue sphere)</td><td>8,000 gp</td></tr>'),
        (str.replace,
         '<tr><td>18&ndash;19<i></td><td>Bag of tricks (rust)</i></td><td>8,500 gp</td></tr>',
         '<tr><td>18&ndash;19</td><td>Bag of tricks (rust)</td><td>8,500 gp</td></tr>'),
         (str.replace,
         '<tr><td>84&ndash;87<i></td><td>Drums of haste</i></td><td>45,000 gp</td></tr>',
         '<tr><td>84&ndash;87</td><td>Drums of haste</td><td>45,000 gp</td></tr>'),
    ],
###############################
# end of ULTIMATEEQUIPMENT.WONDROUSITEMS.SLOTLESS
###############################


###############################
# ULTIMATEMAGIC.MAGIC.BUILDINGANDMODIFYINGCONSTRUCTS
###############################
    "ultimatemagic.magic.buildingandmodifyingconstructs": [
        (str.replace,
         '<p class="body-copy" />',
         '')
    ],
###############################
# end of ULTIMATEMAGIC.MAGIC.BUILDINGANDMODIFYINGCONSTRUCTS
###############################




###############################
# UNCHAINED.CLASSES.INDEX
###############################
    "unchained.classes.index": [
        (remove_indentation, None, None),

        (str.replace,
         """<thead>
<th>""",
         """<thead>
<tr>
<th>"""),

        (str.replace,
         """</th>
</thead>""",
         """</th>
</tr>
</thead>"""),

        (str.replace,
         '"><td></td>',
         '"><td>\ </td>'),
    ],
###############################
# end of UNCHAINED.CLASSES.INDEX
###############################


###############################
# UNCHAINED.CLASSES.SUMMONER
###############################
    "unchained.classes.summoner": [
        (remove_indentation, None, None),
        (str.replace,
         '<a href="#summon-monster"><em>summon monster</a> I</em>',
         '<a href="#summon-monster">Summon monster I</a>'),
        (str.replace,
         '<a href="#summon-monster"><em>Summon monster</a> II</em>',
         '<a href="#summon-monster">Summon monster II</a>'),
         (str.replace,
         '<a href="#summon-monster"><em>Summon monster</a> III</em>',
         '<a href="#summon-monster">Summon monster III</a>'),
        (str.replace,
         '<a href="#summon-monster"><em>Summon monster</a> IV</em>',
         '<a href="#summon-monster">Summon monster IV</a>'),
        (str.replace,
         '<a href="#summon-monster"><em>Summon monster</a> V</em>',
         '<a href="#summon-monster">Summon monster V</a>'),
        (str.replace,
         '<a href="#summon-monster"><em>Summon monster</a> VI</em>',
         '<a href="#summon-monster">Summon monster VI</a>'),
        (str.replace,
         '<a href="#summon-monster"><em>Summon monster</a> VII</em>',
         '<a href="#summon-monster">Summon monster VII</a>'),
        (str.replace,
         '<a href="#summon-monster"><em>Summon monster</a> VIII</em>',
         '<a href="#summon-monster">Summon monster VIII</a>'),
        (str.replace,
         '<a href="#summon-monster"><em>Summon monster</a> IX</em>',
         '<a href="#summon-monster">Summon monster IX</a>'),
        (str.replace,
         '<th colspan="6">&nbsp;</th>',
         ''),
        (str.replace,
         """<thead>
<th>""",
         """<thead>
<tr>
<th>"""),

        (str.replace,
         """</th>
</thead>""",
         """</th>
</tr>
</thead>"""),
    ],
###############################
# end of UNCHAINED.CLASSES.SUMMONER
###############################

###############################
# UNCHAINED.GAMEPLAY.ALIGNMENT
###############################
    "unchained.gameplay.alignment": [
        (str.replace,
         '</td>>',
         '</td>')
    ],
###############################
# end of UNCHAINED.GAMEPLAY.ALIGNMENT
###############################

###############################
# UNCHAINED.GAMEPLAY.REPLACINGITERATIVEATTACKS
###############################
    "unchained.gameplay.replacingiterativeattacks": [
        (
            str.replace,
            '<a href="maximum-hits">Table: Maximum Hits</a>',
            '<a href="/pathfinderRPG/prd/unchained/gameplay/replacingIterativeAttacks.html#maximum-hits">Table: Maximum Hits</a>'
        ),
    ],
###############################
# end of UNCHAINED.GAMEPLAY.REPLACINGITERATIVEATTACKS
###############################

###############################
# UNCHAINED.MAGIC.ESOTERICMATERIALCOMPONENTS
###############################
    "unchained.magic.esotericmaterialcomponents": [
        (remove_indentation, None, None),

        (str.replace,
         """<caption>Esoteric Material Component Costs</caption>
<thead>
<tr>
<th>&nbsp;</th>
<th colspan="10">Spell Level</th>
</tr>
<tr>
<th>CL</th><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th><th>7</th><th>8</th><th>9</th>
</tr>
</thead>""",
         """<caption>Esoteric Material Component Costs</caption>
<thead>
<tr>
    <th>CL / Spell Level</th><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th><th>7</th><th>8</th><th>9</th>
</tr>
</thead>""")
    ],
###############################
# end of UNCHAINED.MAGIC.ESOTERICMATERIALCOMPONENTS
###############################



###############################
# UNCHAINED.MAGIC.INNATEITEMBONUSES
###############################
    "unchained.magic.innateitembonuses": [
        (str.replace,
         '<tr><td></td><td>+2 to all three</td></tr>',
         '<tr><td>\ </td><td colspan="2">+2 to all three</td></tr>'),
        (str.replace,
         '<tr><td></td><td>one and +2 to two others</td></tr>',
         '<tr><td>\ </td><td colspan="2">one and +2 to two others</td></tr>'),
        (str.replace,
         '<tr><td></td><td>+4 to two scores</td></tr>',
         '<tr><td>\ </td><td colspan="2">+4 to two scores</td></tr>'),
        (str.replace,
         '<tr><td></td><td>another, or +4 to all three</td></tr>',
         '<tr><td>\ </td><td colspan="2">another, or +4 to all three</td></tr>'),
        (str.replace,
         '<tr><td></td><td>one and +4 to two others</td></tr>',
         '<tr><td>\ </td><td colspan="2">one and +4 to two others</td></tr>'),
        (str.replace,
         '<tr><td>40,000&ndash;63,999 gp</td><td>Any choice above, </td><td>+40,000 gp</td></tr>',
         '<tr><td>40,000&ndash;63,999 gp</td><td>Any choice above, or</td><td>+40,000 gp</td></tr>'),
        (str.replace,
         '<tr><td></td><td>or +4 to two scores</td></tr>',
         '<tr><td>\ </td><td colspan="2">+4 to two scores</td></tr>'),
    ],
###############################
# end of UNCHAINED.MAGIC.INNATEITEMBONUSES
###############################


###############################
# UNCHAINED.MAGIC.SCALINGITEMS
###############################
    "unchained.magic.scalingitems": [
        (remove_indentation, None, None),

        (str.replace,
         '<p class="item-description paraoverride-17">â¢</td><td>',
         '<p class="item-description paraoverride-17">â¢'),

        (str.replace,
         '<p class = "stat-block">â¢</td><td>',
         '<p class = "stat-block">â¢'),

        (str.replace,
         '<tr>Level</th><th>Bauble (5%)</th><th>Prize (15%)</th><th>Wonder (30%)</th></tr>',
         '<tr><th>Level</th><th>Bauble (5%)</th><th>Prize (15%)</th><th>Wonder (30%)</th></tr>'),

        (str.replace,
         """<thead>
<tr><th>&nbsp;</th><th colspan="10">Spell Level</th></tr>
<tr><th>CL</th><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th><th>7</th><th>8</th><th>9</th></tr>
</thead>""",
         """<thead>
        <tr><th>CL / Spell Level</th><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th><th>7</th><th>8</th><th>9</th></tr>
    </thead>""")
    ],
###############################
# end of UNCHAINED.MAGIC.SCALINGITEMS
###############################


###############################
# UNCHAINED.MAGIC.SIMPLIFIEDSPELLCASTING
###############################
    "unchained.magic.simplifiedspellcasting": [
        (remove_indentation, None, None),

        (str.replace,
         """<caption>Magus or Warpriest</caption>
<thead>
<tr><th>&nbsp;</th><th colspan="8" style="text-align: center;">Spells per Day</th></tr>""",
         """<caption>Magus or Warpriest: Spells per Day</caption>
<thead>"""),

        (str.replace,
         """<caption>Cleric, Druid, Shaman, Witch, or Wizard</caption>
<thead>
<tr><th>&nbsp;</th><th colspan="11" style="text-align: center;">Spells per Day</th></tr>""",
         """<caption>Cleric, Druid, Shaman, Witch, or Wizard: Spells per Day</caption>
<thead>"""),
    ],
###############################
# end of UNCHAINED.MAGIC.SIMPLIFIEDSPELLCASTING
###############################


###############################
# DESCRIPTION
###############################
    "unchained.monsters.step1": [
        (remove_indentation, None, None),

        (str.replace,
         """<thead>
<tr>
<th colspan = "2">&nbsp;</th>
<th colspan = "3">Saving Throws</th>
<th colspan = "2">&nbsp;</th>
<th rowspan = "2">Ability<br />DC</th>
<th rowspan = "2">Spell<br />DC</th>
<th rowspan = "2">Ability<br />Modifiers</th>
<th colspan = "2">Skills</th>
<th>&nbsp;</th>
</tr>
<tr><th>CR</th><th>AC</th><th>Fort</th><th>Ref</th><th>Will</th><th>CMD</th><th>hp</th><th>Master</th><th>Good</th><th>Options</th></tr>
</thead>""",
         """<thead>
<tr><th>CR</th><th>AC</th><th>Save<br>Fort.</th><th>Save<br>.Ref</th><th>Save<br>Will</th><th>CMD</th><th>hp</th><th>Ability<br>DC</th><th>Spell<br>DC</th><th>Ability<br>Modifiers</th><th>Skills<br>Master</th><th>Skills<br>Good</th><th>Options</th></tr>
</thead>"""),

        (str.replace,
         """<thead>
<tr><th>&nbsp;</th><th colspan = "2">Weapon Attacks</th><th colspan = "2">Natural Attacks</th></tr>
<tr><th>CR</th><th>High (Damage)</th><th>Low (Damage)</th><th>Two (Damage)</th><th>Three (Damage)</th></tr>
</thead>""",
         """<thead>
<tr><th>CR</th><th>Weapon Attacks<br>High (Damage)</th><th>Weapon Attacks<br>Low (Damage)</th><th>Natural Attacks<br>Two (Damage)</th><th>Natural AttacksThree (Damage)</th></tr>
</thead>""")
    ],
###############################
# end of DESCRIPTION
###############################


###############################
# UNCHAINED.MONSTERS.STEP6
###############################
    "unchained.monsters.step6": [
        (remove_indentation, None, None),

        (str.replace,
         '<a href="/pathfinderRPG/prd/bestiary/universalMonsterRules.html#fortification">fortification</strong> universal monster rule.</td>',
         '<a href="/pathfinderRPG/prd/bestiary/universalMonsterRules.html#fortification">fortification universal monster rule</a>.</td>'),
        (str.replace,
         """<em></em>""",
         """"""),
        (str.replace,
         """<td><em></td>""",
         """<td></td>"""),
        (str.replace,
         """<td></em></td>""",
         """<td></td>"""),
        (str.replace,
         """</tr>
<tr><td></td><td></td></tr>
<tr>""",
         """</tr>
<tr>"""),
        (str.replace,
         """</tr>
<tr><td></td><td></td><td></td></tr>
<tr>""",
         """</tr>
<tr>"""),

         (str.replace,
         """<a href="/pathfinderRPG/prd/coreRulebook/spells/command.html#command-greater"><a href="/pathfinderRPG/prd/coreRulebook/spells/command.html#greater-command"><em>greater command</em></a></a>""",
         """<a href = "/pathfinderRPG/prd/coreRulebook/spells/command.html#command-greater">greater command</a>""")
    ],
###############################
# end of UNCHAINED.MONSTERS.STEP6
###############################


###############################
# UNCHAINED.MONSTERS.STEP8
###############################
    "unchained.monsters.step8": [
        (str.replace,
         """<tr><td></td><td><a""",
         """<tr><td>\ </td><td><a"""),
    ],
###############################
# end of UNCHAINED.MONSTERS.STEP8
###############################

###############################
# UNCHAINED.SKILLSANDOPTIONS.BACKGROUNDSKILLS
###############################
    "unchained.skillsandoptions.backgroundskills": [
        (str.replace,
         '<p><strong>Step 3</strong>:</td><td>',
         '<p><strong>Step 3</strong>:')
    ],
###############################
# end of UNCHAINED.SKILLSANDOPTIONS.BACKGROUNDSKILLS
###############################

###############################
# UNCHAINED.SKILLSANDOPTIONS.GROUPEDSKILLS
###############################
    "unchained.skillsandoptions.groupedskills": [
        (remove_indentation, None, None),

        (str.replace,
         """<thead>
<tr>
<th rowspan = "2">Character Level</th>
<th rowspan = "2">Skill Specialities<sup>1</sup></th>
<th colspan = "4">Groups</th>
</tr>
<tr>
<th>2 + Int<sup>2</sup></th>
<th>4 + Int<sup>3</sup></th>
<th>6 + Int<sup>4</sup></th>
<th>8 + Int<sup>5</sup></th>
</tr>
</thead>""",
         """<thead>
<tr>
<th rowspan = "2">Character Level</th>
<th rowspan = "2">Skill Specialities<sup>1</sup></th>
<th>Group<br>2 + Int<sup>2</sup></th>
<th>Group<br>4 + Int<sup>3</sup></th>
<th>Group<br>6 + Int<sup>4</sup></th>
<th>Group<br>8 + Int<sup>5</sup></th>
</tr>
</thead>""")
    ],
###############################
# end of UNCHAINED.SKILLSANDOPTIONS.GROUPEDSKILLS
###############################



###############################
# UNCHAINED.SKILLSANDOPTIONS.SKILLUNLOCKS
###############################
    "unchained.skillsandoptions.skillunlocks": [
        (str.replace,
         '<p><strong>5 Ranks</strong>: You gain a swim speed of 10 feet, but only in water with a <a href="/pathfinderRPG/prd/coreRulebook/skills/swim.html#swim">Swim</a> DC of 15 or lower.</td><td></p>',
         '<p><strong>5 Ranks</strong>: You gain a swim speed of 10 feet, but only in water with a <a href="/pathfinderRPG/prd/coreRulebook/skills/swim.html#swim">Swim</a> DC of 15 or lower.</p>')
    ],
###############################
# end of UNCHAINED.SKILLSANDOPTIONS.SKILLUNLOCKS
###############################
}

class exceptions():
    tables = (
        "bestiary.animalcompanions",
        "bestiary.lycanthrope",
        "bestiary.variantmonsterindex",
        "corerulebook.classes.ranger"
    )

if __name__ == '__main__':
    import prd
    prd.main()
