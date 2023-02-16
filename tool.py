import json as JSON
JSON.stringify=JSON.dumps
JSON.parse=JSON.loads

import sys

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
            "content":i[3]
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
                if ltype=="ul":
                    k, v = metadata_parser(ltext)
                    if k in metadata_aliases:
                        k=metadata_aliases[k]
                    current["metadata"][k]=v
                if ltype=="backticks":
                    pass
                    # does nothing - now we're enforcing code blocks so that display isn't screwed up
                
                    #if "render-as-code-block" not in current["metadata"]:
                    #    current["metadata"]["render-as-code-block"]="true"
                    #if is_truthy(current["metadata"]["render-as-code-block"])==False:
                    #    current["content"].append("```")
                if ltype=="empty" or ltype=="text":
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
(not implemented): output Lua script.
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
        pass
        #dump_lua(data, outfile)
    if outfile_format=="md":
        dump_markdown(data, outfile)
