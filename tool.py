import json as JSON
JSON.stringify=JSON.dumps
JSON.parse=JSON.loads

import sys
import re

"""
Markdown specs:

Anything above the first level-2 heading does nothing

# level-1 heading does nothing (for your eyes only)

## Display title of entry on level 2 headings
- category: game
- search-terms: lorem ipsum dolor

```
Unordered list directly following the heading defines metadata
After the list ends, the following text until the next heading (either level 1 or 2) are the content of the entry
Code block is optional, useful for bypassing Markdown syntax.
(When outputting to md, it's always code-block'd.)

headings HAVE TO BE `# text`, not `# text #` nor `text\n====`.
List can use `-`, `+` or `*`.
code blocks HAVE TO BE backticks, not indented. The 3 backticks have to be on their own line.
```


JSON and internal representation specs:
[
    {
        "type":"text",
        "content":"regular text in markdown that is not in an entry"
    },
    {
        "type":"h1",
        "content":"level-1 headings"
    },
    {
        "type":"entry",
        "title":"title goes here"
        "metadata":{
            "category":"game",
            "search-terms":"lorem ipsum dolor"
        },
        "content":"text goes here"
    }
]



Lua script specs

return {     -- `return`s a 2d array
    {
        "Entry title",
        "Search terms",
        "Category",
        "Content",
        "[optional] URL"
    }
}



Metadata specs:
category:
    one of the following, used by the game to determine what color to display:
    help, org, game, term, setup, pattern, command, english, name
search-terms:
    alias: search-term, search
    used by in-game search function
url:
    alias: web, website
    optional. Clickable in-game link
id:
    an ID for the entry that can be useful in some functionalities.
    Same entry across languages should have identical ID (cross-language reference/comparison)
    Different versions of the same entry should have identical ID (platform restriction)
    Completely different entries should have different ID
platform-restriction:
    one of the following:
    none, apple, non-apple
    Defaults to none.
    A pair of `apple` and `non-apple` versions with the same ID should appear together for the sake of Lua script generation
"""

metadata_aliases={
    "search-term":"search-terms",
    "search":"search-terms",
    "web":"url",
    "website":"url"
}

custom_characters_codepoint_to_name={983061: 'zChan.thinking', 983042: 'zChan.full', 983040: 'zChan.none', 983051: 'zChan.question', 983058: 'zChan.qualified', 983045: 'zChan.grinning', 983057: 'zChan.cracked', 983059: 'zChan.unqualified', 983050: 'zChan.fear', 983049: 'zChan.rage', 983062: 'zChan.spark', 983053: 'zChan.shocked', 983060: 'zChan.understand', 983047: 'zChan.tears', 983056: 'zChan.cry', 983043: 'zChan.happy', 983055: 'zChan.sweat_drop', 983054: 'zChan.ellipses', 983041: 'zChan.normal', 983052: 'zChan.angry', 983048: 'zChan.anxious', 983044: 'zChan.confused', 983046: 'zChan.frowning', 983588: 'mahjong.haru', 983597: 'mahjong.s5Red', 983625: 'mahjong.p5Comb1', 983633: 'mahjong.p9Comb2', 983609: 'mahjong.s1Base', 983596: 'mahjong.m5Red', 983612: 'mahjong.s5Comb', 983626: 'mahjong.p5Comb2', 983598: 'mahjong.p5Red', 983557: 'mahjong.m6', 983599: 'mahjong.m1Base', 983575: 'mahjong.p6', 983566: 'mahjong.s6', 983553: 'mahjong.m2', 983607: 'mahjong.m9Base', 983631: 'mahjong.p9Base', 983562: 'mahjong.s2', 983615: 'mahjong.s9Base', 983593: 'mahjong.ran', 983586: 'mahjong.hatsuAlt', 983618: 'mahjong.p2Comb', 983628: 'mahjong.p6Comb', 983617: 'mahjong.p2Base', 983554: 'mahjong.m3', 983567: 'mahjong.s7', 983563: 'mahjong.s3', 983572: 'mahjong.p3', 983576: 'mahjong.p7', 983558: 'mahjong.m7', 983614: 'mahjong.s7Comb', 983620: 'mahjong.p3Comb1', 983630: 'mahjong.p7Comb', 983605: 'mahjong.m7Base', 983608: 'mahjong.mComb', 983636: 'mahjong.s1jBase', 983635: 'mahjong.s1j', 983583: 'mahjong.chun', 983621: 'mahjong.p3Comb2', 983632: 'mahjong.p9Comb1', 983619: 'mahjong.p3Base', 983555: 'mahjong.m4', 983584: 'mahjong.hatsu', 983564: 'mahjong.s4', 983568: 'mahjong.s8', 983592: 'mahjong.ume', 983573: 'mahjong.p4', 983577: 'mahjong.p8', 983627: 'mahjong.p6Base', 983624: 'mahjong.p5Base', 983559: 'mahjong.m8', 983590: 'mahjong.aki', 983613: 'mahjong.s7Base', 983629: 'mahjong.p7Base', 983616: 'mahjong.s9Comb', 983594: 'mahjong.kiku', 983611: 'mahjong.s5Base', 983610: 'mahjong.s1Comb', 983606: 'mahjong.m8Base', 983637: 'mahjong.s1jComb', 983604: 'mahjong.m6Base', 983603: 'mahjong.m5Base', 983602: 'mahjong.m4Base', 983601: 'mahjong.m3Base', 983600: 'mahjong.m2Base', 983595: 'mahjong.take', 983591: 'mahjong.fuyu', 983623: 'mahjong.p4Comb', 983589: 'mahjong.natsu', 983587: 'mahjong.hakuAlt', 983571: 'mahjong.p2', 983582: 'mahjong.pe', 983556: 'mahjong.m5', 983622: 'mahjong.p4Base', 983634: 'mahjong.frameComb', 983574: 'mahjong.p5', 983581: 'mahjong.sha', 983552: 'mahjong.m1', 983565: 'mahjong.s5', 983560: 'mahjong.m9', 983579: 'mahjong.ton', 983580: 'mahjong.nan', 983578: 'mahjong.p9', 983561: 'mahjong.s1', 983585: 'mahjong.haku', 983570: 'mahjong.p1', 983569: 'mahjong.s9', 983314: 'key.windows', 983304: 'key.macFowardDel', 983333: 'key.macPgdnAlt', 983299: 'key.shift', 983315: 'key.alt', 983310: 'key.macPgup', 983329: 'key.isoAlt', 983331: 'key.macEndAlt', 983320: 'key.up', 983322: 'key.left', 983305: 'key.macEsc', 983328: 'key.isoCtrl', 983297: 'key.macOpt', 983313: 'key.space', 983302: 'key.backspace', 983319: 'key.esc', 983326: 'key.keyboard', 983309: 'key.macEnd', 983324: 'key.del', 983306: 'key.macTab', 983317: 'key.winMenu', 983318: 'key.tab', 983311: 'key.macPgdn', 983296: 'key.macCmd', 983323: 'key.right', 983325: 'key.enterText', 983330: 'key.macHomeAlt', 983303: 'key.clear', 983316: 'key.ctrl', 983312: 'key.macEnter', 983334: 'key.iecPower', 983332: 'key.macPgupAlt', 983298: 'key.macCtrl', 983327: 'key.macMediaEject', 983300: 'key.capsLock', 983321: 'key.down', 983308: 'key.macHome', 983307: 'key.fn', 983301: 'key.enter_or_return', 983130: 'mino.C', 983115: 'mino.F', 983116: 'mino.E', 983132: 'mino.O1', 983111: 'mino.Z5', 983107: 'mino.L', 983129: 'mino.I3', 983126: 'mino.N', 983131: 'mino.I2', 983127: 'mino.H', 983128: 'mino.I5', 983106: 'mino.J', 983110: 'mino.I', 983108: 'mino.T', 983105: 'mino.S', 983119: 'mino.V', 983118: 'mino.U', 983113: 'mino.P', 983109: 'mino.O', 983124: 'mino.R', 983112: 'mino.S5', 983117: 'mino.T5', 983123: 'mino.L5', 983122: 'mino.J5', 983114: 'mino.Q', 983121: 'mino.X', 983120: 'mino.W', 983104: 'mino.Z', 983125: 'mino.Y', 983425: 'controller.lt', 983459: 'controller.psMute', 983426: 'controller.rt', 983427: 'controller.lb', 983434: 'controller.joystickR', 983436: 'controller.jsLD', 983438: 'controller.jsLR', 983461: 'controller.psOption', 983432: 'controller.xboxB', 983428: 'controller.rb', 983430: 'controller.xboxY', 983433: 'controller.joystickL', 983447: 'controller.dpadD', 983424: 'controller.xbox', 983435: 'controller.jsLU', 983451: 'controller.xboxMenu', 983431: 'controller.xboxA', 983454: 'controller.ps', 983429: 'controller.xboxX', 983449: 'controller.dpadR', 983460: 'controller.psCreate', 983458: 'controller.psSquare', 983457: 'controller.psCross', 983453: 'controller.xboxConnect', 983455: 'controller.psTriangle', 983456: 'controller.psCircle', 983444: 'controller.jsRPress', 983452: 'controller.xboxShare', 983450: 'controller.xboxView', 983448: 'controller.dpadL', 983446: 'controller.dpadU', 983445: 'controller.dpad', 983437: 'controller.jsLL', 983441: 'controller.jsRL', 983443: 'controller.jsLPress', 983442: 'controller.jsRR', 983440: 'controller.jsRD', 983439: 'controller.jsRU', 983234: 'icon.rankS', 983182: 'icon.toDown', 983205: 'icon.nextFrame', 983183: 'icon.toLeft', 983186: 'icon.crossMark', 983212: 'icon.export', 983188: 'icon.infoMark', 983233: 'icon.speedFive', 983218: 'icon.saveTwo', 983209: 'icon.pound', 983174: 'icon.help', 983207: 'icon.dollar', 983226: 'icon.rankE', 983169: 'icon.music', 983191: 'icon.globe', 983239: 'icon.copy', 983172: 'icon.play_pause', 983189: 'icon.warnMark', 983180: 'icon.hollowLogo', 983197: 'icon.cross_thick', 983214: 'icon.trash', 983224: 'icon.rankC', 983206: 'icon.yen', 983216: 'icon.saveOne', 983178: 'icon.retry_spin', 983203: 'icon.play', 983195: 'icon.apple', 983173: 'icon.info', 983200: 'icon.num2InSpin', 983176: 'icon.volume_up', 983204: 'icon.pause', 983231: 'icon.speedOne', 983211: 'icon.onebag', 983215: 'icon.loadOne', 983168: 'icon.menu', 983238: 'icon.garbage', 983237: 'icon.bomb', 983171: 'icon.back', 983223: 'icon.rankB', 983187: 'icon.musicMark', 983229: 'icon.speedOneEights', 983190: 'icon.console', 983235: 'icon.bone', 983232: 'icon.speedTwo', 983193: 'icon.settings', 983196: 'icon.home', 983202: 'icon.num4InSpin', 983228: 'icon.rankZ', 983221: 'icon.rankU', 983175: 'icon.mute', 983227: 'icon.rankF', 983225: 'icon.rankD', 983236: 'icon.invis', 983222: 'icon.rankA', 983179: 'icon.filledLogo', 983220: 'icon.rankX', 983219: 'icon.zBook', 983217: 'icon.loadTwo', 983170: 'icon.language', 983198: 'icon.num0InSpin', 983192: 'icon.video_camera', 983181: 'icon.toUp', 983185: 'icon.checkMark', 983208: 'icon.euro', 983210: 'icon.bitcoin', 983230: 'icon.speedOneHalf', 983201: 'icon.num3InSpin', 983199: 'icon.num1InSpin', 983194: 'icon.mrz', 983213: 'icon.import', 983184: 'icon.toRight', 983177: 'icon.volume_down'}

custom_characters_name_to_codepoint={'zChan.thinking': 983061, 'zChan.full': 983042, 'zChan.none': 983040, 'zChan.question': 983051, 'zChan.qualified': 983058, 'zChan.grinning': 983045, 'zChan.cracked': 983057, 'zChan.unqualified': 983059, 'zChan.fear': 983050, 'zChan.rage': 983049, 'zChan.spark': 983062, 'zChan.shocked': 983053, 'zChan.understand': 983060, 'zChan.tears': 983047, 'zChan.cry': 983056, 'zChan.happy': 983043, 'zChan.sweat_drop': 983055, 'zChan.ellipses': 983054, 'zChan.normal': 983041, 'zChan.angry': 983052, 'zChan.anxious': 983048, 'zChan.confused': 983044, 'zChan.frowning': 983046, 'mahjong.haru': 983588, 'mahjong.s5Red': 983597, 'mahjong.p5Comb1': 983625, 'mahjong.p9Comb2': 983633, 'mahjong.s1Base': 983609, 'mahjong.m5Red': 983596, 'mahjong.s5Comb': 983612, 'mahjong.p5Comb2': 983626, 'mahjong.p5Red': 983598, 'mahjong.m6': 983557, 'mahjong.m1Base': 983599, 'mahjong.p6': 983575, 'mahjong.s6': 983566, 'mahjong.m2': 983553, 'mahjong.m9Base': 983607, 'mahjong.p9Base': 983631, 'mahjong.s2': 983562, 'mahjong.s9Base': 983615, 'mahjong.ran': 983593, 'mahjong.hatsuAlt': 983586, 'mahjong.p2Comb': 983618, 'mahjong.p6Comb': 983628, 'mahjong.p2Base': 983617, 'mahjong.m3': 983554, 'mahjong.s7': 983567, 'mahjong.s3': 983563, 'mahjong.p3': 983572, 'mahjong.p7': 983576, 'mahjong.m7': 983558, 'mahjong.s7Comb': 983614, 'mahjong.p3Comb1': 983620, 'mahjong.p7Comb': 983630, 'mahjong.m7Base': 983605, 'mahjong.mComb': 983608, 'mahjong.s1jBase': 983636, 'mahjong.s1j': 983635, 'mahjong.chun': 983583, 'mahjong.p3Comb2': 983621, 'mahjong.p9Comb1': 983632, 'mahjong.p3Base': 983619, 'mahjong.m4': 983555, 'mahjong.hatsu': 983584, 'mahjong.s4': 983564, 'mahjong.s8': 983568, 'mahjong.ume': 983592, 'mahjong.p4': 983573, 'mahjong.p8': 983577, 'mahjong.p6Base': 983627, 'mahjong.p5Base': 983624, 'mahjong.m8': 983559, 'mahjong.aki': 983590, 'mahjong.s7Base': 983613, 'mahjong.p7Base': 983629, 'mahjong.s9Comb': 983616, 'mahjong.kiku': 983594, 'mahjong.s5Base': 983611, 'mahjong.s1Comb': 983610, 'mahjong.m8Base': 983606, 'mahjong.s1jComb': 983637, 'mahjong.m6Base': 983604, 'mahjong.m5Base': 983603, 'mahjong.m4Base': 983602, 'mahjong.m3Base': 983601, 'mahjong.m2Base': 983600, 'mahjong.take': 983595, 'mahjong.fuyu': 983591, 'mahjong.p4Comb': 983623, 'mahjong.natsu': 983589, 'mahjong.hakuAlt': 983587, 'mahjong.p2': 983571, 'mahjong.pe': 983582, 'mahjong.m5': 983556, 'mahjong.p4Base': 983622, 'mahjong.frameComb': 983634, 'mahjong.p5': 983574, 'mahjong.sha': 983581, 'mahjong.m1': 983552, 'mahjong.s5': 983565, 'mahjong.m9': 983560, 'mahjong.ton': 983579, 'mahjong.nan': 983580, 'mahjong.p9': 983578, 'mahjong.s1': 983561, 'mahjong.haku': 983585, 'mahjong.p1': 983570, 'mahjong.s9': 983569, 'key.windows': 983314, 'key.macFowardDel': 983304, 'key.macPgdnAlt': 983333, 'key.shift': 983299, 'key.alt': 983315, 'key.macPgup': 983310, 'key.isoAlt': 983329, 'key.macEndAlt': 983331, 'key.up': 983320, 'key.left': 983322, 'key.macEsc': 983305, 'key.isoCtrl': 983328, 'key.macOpt': 983297, 'key.space': 983313, 'key.backspace': 983302, 'key.esc': 983319, 'key.keyboard': 983326, 'key.macEnd': 983309, 'key.del': 983324, 'key.macTab': 983306, 'key.winMenu': 983317, 'key.tab': 983318, 'key.macPgdn': 983311, 'key.macCmd': 983296, 'key.right': 983323, 'key.enterText': 983325, 'key.macHomeAlt': 983330, 'key.clear': 983303, 'key.ctrl': 983316, 'key.macEnter': 983312, 'key.iecPower': 983334, 'key.macPgupAlt': 983332, 'key.macCtrl': 983298, 'key.macMediaEject': 983327, 'key.capsLock': 983300, 'key.down': 983321, 'key.macHome': 983308, 'key.fn': 983307, 'key.enter_or_return': 983301, 'mino.C': 983130, 'mino.F': 983115, 'mino.E': 983116, 'mino.O1': 983132, 'mino.Z5': 983111, 'mino.L': 983107, 'mino.I3': 983129, 'mino.N': 983126, 'mino.I2': 983131, 'mino.H': 983127, 'mino.I5': 983128, 'mino.J': 983106, 'mino.I': 983110, 'mino.T': 983108, 'mino.S': 983105, 'mino.V': 983119, 'mino.U': 983118, 'mino.P': 983113, 'mino.O': 983109, 'mino.R': 983124, 'mino.S5': 983112, 'mino.T5': 983117, 'mino.L5': 983123, 'mino.J5': 983122, 'mino.Q': 983114, 'mino.X': 983121, 'mino.W': 983120, 'mino.Z': 983104, 'mino.Y': 983125, 'controller.lt': 983425, 'controller.psMute': 983459, 'controller.rt': 983426, 'controller.lb': 983427, 'controller.joystickR': 983434, 'controller.jsLD': 983436, 'controller.jsLR': 983438, 'controller.psOption': 983461, 'controller.xboxB': 983432, 'controller.rb': 983428, 'controller.xboxY': 983430, 'controller.joystickL': 983433, 'controller.dpadD': 983447, 'controller.xbox': 983424, 'controller.jsLU': 983435, 'controller.xboxMenu': 983451, 'controller.xboxA': 983431, 'controller.ps': 983454, 'controller.xboxX': 983429, 'controller.dpadR': 983449, 'controller.psCreate': 983460, 'controller.psSquare': 983458, 'controller.psCross': 983457, 'controller.xboxConnect': 983453, 'controller.psTriangle': 983455, 'controller.psCircle': 983456, 'controller.jsRPress': 983444, 'controller.xboxShare': 983452, 'controller.xboxView': 983450, 'controller.dpadL': 983448, 'controller.dpadU': 983446, 'controller.dpad': 983445, 'controller.jsLL': 983437, 'controller.jsRL': 983441, 'controller.jsLPress': 983443, 'controller.jsRR': 983442, 'controller.jsRD': 983440, 'controller.jsRU': 983439, 'icon.rankS': 983234, 'icon.toDown': 983182, 'icon.nextFrame': 983205, 'icon.toLeft': 983183, 'icon.crossMark': 983186, 'icon.export': 983212, 'icon.infoMark': 983188, 'icon.speedFive': 983233, 'icon.saveTwo': 983218, 'icon.pound': 983209, 'icon.help': 983174, 'icon.dollar': 983207, 'icon.rankE': 983226, 'icon.music': 983169, 'icon.globe': 983191, 'icon.copy': 983239, 'icon.play_pause': 983172, 'icon.warnMark': 983189, 'icon.hollowLogo': 983180, 'icon.cross_thick': 983197, 'icon.trash': 983214, 'icon.rankC': 983224, 'icon.yen': 983206, 'icon.saveOne': 983216, 'icon.retry_spin': 983178, 'icon.play': 983203, 'icon.apple': 983195, 'icon.info': 983173, 'icon.num2InSpin': 983200, 'icon.volume_up': 983176, 'icon.pause': 983204, 'icon.speedOne': 983231, 'icon.onebag': 983211, 'icon.loadOne': 983215, 'icon.menu': 983168, 'icon.garbage': 983238, 'icon.bomb': 983237, 'icon.back': 983171, 'icon.rankB': 983223, 'icon.musicMark': 983187, 'icon.speedOneEights': 983229, 'icon.console': 983190, 'icon.bone': 983235, 'icon.speedTwo': 983232, 'icon.settings': 983193, 'icon.home': 983196, 'icon.num4InSpin': 983202, 'icon.rankZ': 983228, 'icon.rankU': 983221, 'icon.mute': 983175, 'icon.rankF': 983227, 'icon.rankD': 983225, 'icon.invis': 983236, 'icon.rankA': 983222, 'icon.filledLogo': 983179, 'icon.rankX': 983220, 'icon.zBook': 983219, 'icon.loadTwo': 983217, 'icon.language': 983170, 'icon.num0InSpin': 983198, 'icon.video_camera': 983192, 'icon.toUp': 983181, 'icon.checkMark': 983185, 'icon.euro': 983208, 'icon.bitcoin': 983210, 'icon.speedOneHalf': 983230, 'icon.num3InSpin': 983201, 'icon.num1InSpin': 983199, 'icon.mrz': 983194, 'icon.import': 983213, 'icon.toRight': 983184, 'icon.volume_down': 983177}

def parse_pua_characters(s):
    # converts a PUA character to {{name}} or {{hex codepoint}}.
    def r(matchobj):
        codepoint=ord(matchobj.group(0))
        if codepoint in custom_characters_codepoint_to_name:
            return "{{"+custom_characters_codepoint_to_name[codepoint]+"}}"
        else:
            return "{{"+hex(codepoint)+"}}"
    s=re.sub(
        r"([\ue000-\uf8ff\U000F0000-\U000FFFFD\U00100000-\U0010FFFD])",
        r,
        s
    )
    return s


def read_json(fname):
    with open(fname, encoding="utf-8") as f:
        return JSON.parse(f.read())

def dump_json(data, fname):
    with open(fname, "w", encoding="utf-8") as f:
        f.write(JSON.stringify(data, indent=4, ensure_ascii=False))

def read_lua_json(fname):
    # Reads JSON converted from Lua internal representation. (I can't directly read Lua code.)
    with open(fname, encoding="utf-8") as f:
        data=JSON.parse(f.read())
    # expecting 2D array like in Lua representation
    output=[]
    for i in data:
        entry={
            "type":"entry",
            "title":i[0],
            "metadata":{
                "search-terms":i[1],
                "category":i[2]
            },
            "content":parse_pua_characters(i[3])
        }
        if len(i)>=5:
            entry["metadata"]["url"]=i[4]
        output.append(entry)
    return output

def read_markdown(fname):
    # Okay I'm not markdown expert so, uh, bear with me
    def line_recognizer(line):
        if line=="":
            return "empty", ""
        if line.startswith("# "):
            return "h1", line[2:].strip()
        if line.startswith("## "):
            return "h2", line[3:].strip()
        if line.startswith("- ") or line.startswith("+ ") or line.startswith("* "):
            return "ul", line[2:].strip()
        if line=="```":
            return "backticks",""
        return "text", line
    
    def metadata_parser(line):
        a=line.split(":")
        return a[0].strip(), ":".join(a[1:]).strip()
    
    def is_truthy(v):
        return v.lower() in ["true","yes","1"]
    
    def is_falsy(v):
        return v.lower() in ["false","no","0"]
    
    def text_array_strip(v):
        while len(v)!=0 and v[0].strip()=="":
            v=v[1:]
        while len(v)!=0 and v[-1].strip()=="":
            v=v[:-1]
        return v
    
    def text_array_join(a, joiner=""):
        # strip empty lines around the text
        a=text_array_strip(a)
        # Is it now empty?
        if len(a)==0: return ""
        # strip end-of-text linebreaks on the last segment
        a[-1]=a[-1].rstrip()
        # deal with line continuation
        i=0
        while i<len(a):
            if a[i].endswith("\\\n"):
                if i+1<len(a):
                    a[i]=a[i][:-2]+a[i+1].lstrip()
                    del(a[i+1])
                    i-=1
            i+=1
        # finally, join the text
        return joiner.join(a)
    
    output=[]
    
    current={"type":"begin"}
    
    is_in_backticks=False
    
    with open(fname, encoding="utf-8") as f:
        for line in f.readlines():
            #line=line.strip()
            ltype, ltext = line_recognizer(line.strip())
            
            # h1, h2 ends last element forceably
            # an h1 element lasts only a single line
            # at the start, new element has to be started, but no last element to push
            if ltype=="h1" or ltype=="h2" or\
              current["type"]=="h1" or\
              current["type"]=="begin":
                # put current elements into output, and start afresh
                if current["type"]!="begin":
                    if current["type"]=="text" or current["type"]=="entry":
                        current["content"]=text_array_join(current["content"])
                    output.append(current)
                # h1 starts h1, h2 starts entry, everything else starts text
                if ltype=="h1":
                    current={
                        "type":"h1",
                        "content":ltext
                    }
                elif ltype=="h2":
                    current={
                        "type":"entry",
                        "title":ltext,
                        "metadata":{},
                        "content":[]
                    }
                else:
                    current={
                        "type":"text",
                        "content":[ltext]
                    }
            # If current element is text, anything here is added verbatim
            if current["type"]=="text":
                current["content"].append(line)
            
            if current["type"]=="entry":
                if ltype=="backticks":
                    is_in_backticks=not is_in_backticks
                    continue
                
                if is_in_backticks:
                    current["content"].append(line)
                
                elif ltype=="ul":
                    k, v = metadata_parser(ltext)
                    if k in metadata_aliases:
                        k=metadata_aliases[k]
                    current["metadata"][k]=v
                
                elif ltype=="empty" or ltype=="text":
                    current["content"].append(line)
        # end of for line loop
        # dump whatever into output
        if current["type"]=="text" or current["type"]=="entry":
            current["content"]=text_array_join(current["content"])
        output.append(current)
    return output

def dump_markdown(data, fname):
    def is_truthy(v):
        return v.lower() in ["true","yes","1"]
    
    def is_falsy(v):
        return v.lower() in ["false","no","0"]
    
    with open(fname, "w", encoding="utf-8") as f:
        for i in data:
            if i["type"]=="h1":
                f.write("# "+i["content"]+"\n")
            if i["type"]=="text":
                f.write(i["content"]+"\n")
            if i["type"]=="entry":
                f.write("## "+i["title"]+"\n")
                for j in i["metadata"]:
                    f.write("- "+j+": "+i["metadata"][j]+"\n")
                f.write("\n")
                #if "render-as-code-block" in i["metadata"] and is_truthy(i["metadata"]["render-as-code-block"]):
                if True:
                    f.write("```\n")
                    f.write(i["content"]+"\n")
                    f.write("```\n")
                else:
                    f.write(i["content"].replace("\n","<br />"))
                f.write("\n")

def dump_lua(data, fname):
    # okay it's getting messy
    def text_escape(n):
        # escape characters
        n=n.replace("\\","\\\\").replace("\n","\\n").replace("\t","\\t").replace("\"","\\\"")
        # convert {{}} back to ZFramework representation
        def r(matchobj):
            glyph=matchobj.group(1)
            if glyph in custom_characters_name_to_codepoint:
                return '"..CHAR.{}.."'.format(glyph)
            else:
                return chr(int(glyph[2:],16))
        n=re.sub(
            "{{([^}]+)}}",
            r,
            n
        )
        return n
    
    def entry_to_lua(e):
        t="    {"
        t+='\"'+text_escape(e["title"])+'\",\n'
        t+="        "
        t+='\"'+text_escape(e["metadata"]["search-terms"])+'\",\n'
        t+="        "
        t+='\"'+text_escape(e["metadata"]["category"])+'\",\n'
        t+="        "
        t+='\"'+text_escape(e["content"])+'\",'
        if "url" in e["metadata"]:
            t+="\n"
            t+="        "
            t+='\"'+text_escape(e["metadata"]["url"])+'\",'
        for i in e["metadata"]:
            if i not in ["search-terms","category","url"]:
                t+="\n        -- {}: {}".format(i,e["metadata"][i])
        t+="\n    }"
        return t
    already_added_platform_restriction_ids=[]
    
    t="-- Automatically generated by a Python script, from a markdown source file.\n"
    t+="-- The script can be found here: https://github.com/user670/techmino-dictionary-converter/blob/master/tool.py \n"
    t+="return {\n"
    for i in data:
        if i["type"]=="text":
            if i["content"].strip()=="": continue
            for line in i["content"].split("\n"):
                t+="    -- "+line+"\n"
            continue
        if i["type"]=="h1":
            t+="    -- # "+i["content"]+"\n"
            continue
        if i["metadata"].get("id") in already_added_platform_restriction_ids:
            continue
        if "platform-restriction" in i["metadata"] and i["metadata"]["platform-restriction"]!="none":
            if "id" not in i["metadata"]:
                # lacks an ID, cannot do platform restriction
                t+=entry_to_lua(i)
                t+=",\n"
                continue
            apple=None
            nonapple=None
            for j in data:
                if j["type"]!="entry": continue
                if "id" not in j["metadata"]:
                    continue
                if j["metadata"]["id"]!=i["metadata"]["id"]:
                    continue
                if "platform-restriction" in j["metadata"]:
                    if j["metadata"]["platform-restriction"]=="apple":
                        apple=j
                    if j["metadata"]["platform-restriction"]=="non-apple":
                        nonapple=j
            if apple==None or nonapple==None:
                # there isn't a pair of platform-restricted duplicates
                # add as normal
                t+=entry_to_lua(i)
                t+=",\n"
            else:
                t+="FNNS and "
                t+=entry_to_lua(apple)
                t+=" or "
                t+=entry_to_lua(nonapple)
                t+=",\n"
                already_added_platform_restriction_ids.append(i["metadata"]["id"])
            continue
        t+=entry_to_lua(i)
        t+=",\n"
    t+="}"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(t)
            


if __name__=="__main__":

    help_text="""python {} [flags] infile outfile

Infile and outfile format are automatically determined by extension name (.json, .md, .lua).
Specifically, .json input is assumed to be verbose representation. To read JSON dumped from
in-game representation, use --read-lua-json flag.
Flags can be used to manually specify formats.

Flags:
-h, --help       : display this message.
--read-json      : assume infile is verbose representation JSON.
--read-lua-json  : assume infile is in-game representation JSON.
--read-md        : assume infile is markdown.
--dump-json      : output verbose representation JSON.
--dump-lua       : output Lua script.
--dump-md        : output markdown.
"""
    
    if "-h" in sys.argv or "--help" in sys.argv:
        print(help_text.format(sys.argv[0]))
        sys.exit()
    
    state="read-infile"
    infile=""
    outfile=""
    infile_format=""
    infile_force_format=False
    outfile_format=""
    outfile_force_format=False
    
    
    for i in sys.argv[1:]:
        if i=="--read-json":
            infile_format="json"
            infile_force_format=True
        elif i=="--read-lua-json":
            infile_format="lua-json"
            infile_force_format=True
        elif i=="--read-md":
            infile_format="md"
            infile_force_format=True
        elif i=="--dump-json":
            outfile_format="json"
            outfile_force_format=True
        elif i=="--dump-lua":
            outfile_format="lua"
            outfile_force_format=True
        elif i=="--dump-md":
            outfile_format="lua"
            outfile_force_format=True
        else:
            if state=="read-infile":
                infile=i
                if infile_force_format==False:
                    ext=i.split(".")[-1].lower()
                    if ext in ["json","md"]: infile_format=ext
                state="read-outfile"
            elif state=="read-outfile":
                outfile=i
                if outfile_force_format==False:
                    ext=i.split(".")[-1].lower()
                    if ext in ["json","md","lua"]: outfile_format=ext
                state="end"
    
    if infile=="":
        print("You did not specify an input file.")
        sys.exit()
    if outfile=="":
        print("You did not specify an output file.")
        sys.exit()
    if infile_format not in ["json","lua-json","md"]:
        print("You did not specify an input file format, and the format cannot be inferred from file extension.")
        sys.exit()
    if outfile_format not in ["json","lua","md"]:
        print("You did not specify an output file format, and the format cannot be inferred from file extension.")
        sys.exit()
    
    if infile_format=="json":
        data=read_json(infile)
    if infile_format=="lua-json":
        data=read_lua_json(infile)
    if infile_format=="md":
        data=read_markdown(infile)
    
    if outfile_format=="json":
        dump_json(data, outfile)
    if outfile_format=="lua":
        dump_lua(data, outfile)
    if outfile_format=="md":
        dump_markdown(data, outfile)
