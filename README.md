# techmino-dictionary-converter

This repository contains a Python script used to convert the ZDictionary for Techmino between different formats.

## Quick help

```
python tool.py [flags] infile outfile
```

Input and output file formats are implied by the extension names of the file names (`.json`, `.lua` or `.md`, case insensitive).

You can also use flags to manually specify a input or output file format.

A `.json` input file is assumed to be in the verbose representation (i.e. the internal representation of this Python script) format. To specify a JSON format that matches the in-game format, use the `--read-lua-json` flag.

List of flags:

```
-h, --help       : display help message.
--read-json      : assume infile is verbose representation JSON.
--read-lua-json  : assume infile is in-game representation JSON.
--read-md        : assume infile is markdown.
--dump-json      : output verbose representation JSON.
--dump-lua       : output Lua script.
--dump-md        : output markdown.
```

## Format specifications

### Markdown

A compatible Markdown file follows the format of the following example:

```
Text above any headings are considered comments.

# So are level-1 headings

and any text between a level-1 heading and the next level-2 heading.

## Level-2 headings are titles of dictionary entries.
- metadata-key: metadata are in unordered list directly under the level-2 heading

` ` `
and code block contains the body text of the entry. (backticks separated to avoid screwing format in this document)
` ` `
```

Having text under a level-2 heading but not in a list or in a code block, or having an un-closed code block, are undefined behaviors - the code aren't programmed to handle these situations.

Headings have to be `# text` format, not `# text #` nor `text\n====`.

The three backticks for a code block must be on their own line.

Lists can use `-`, `+` or `*`.

### Verbose JSON representation

Verbose JSON format follows the following example:

```json
[
  {
    "type":"text",
    "content":"regular text that is not an entry is stored here"
  },
  {
    "type":"h1",
    "content":"level-1 headings are stored here"
  },
  {
    "type":"entry",
    "title":"dictionary entries are stored here",
    "metadata":{
      "metadata-key":"metadata value",
    }
    "content":"body text here"
  }
]
```

### In-game representation format

The in-game format is a 2D array like this: (below is Lua table syntax)

```lua
{
  {
    "Entry title",
    "Search terms metadata",
    "Category metadata",
    "Body text",
    "[optional] URL metadata"
  }
}
```

The script does not directly read Lua source code; please convert to JSON and use the `--read-lua-json` flag to read data from the game.

When converting to Lua script, comment texts, level-1 headings and extra metadata are exported to Lua comments.

## Metadata fields

At this moment, User670, the author of this Python script, has identified and/or defined the following metadata fields. You can add more metadata fields to fit your application's needs.

Only Markdown format can use key aliases, and they are converted to the original key name when reading a markdown file. Reading JSON will not make such conversion.

### `search-terms` (required, Techmino)

Alias: `search-term`

Used in-game for the search functionality.

### `category` (required, Techmino)

One of the following: `help`, `org`, `game`, `term`, `setup`, `pattern`, `command`, `english`, `name`

Used by the game to determine display color.

### `url` (Techmino)

Aliases: `web`, `website`

A URL related to the entry. The game has a button in the dictionary interface to jump to this URL.

### `id` (User670)

An identifier for the entry.

Currently, this field is required when the metadata `platform-restriction` is used; a pair of entries with the same ID and different `platform-restriction` is needed to generate platform-dependent entries when exporting to Lua script.

Additionally, it is recommended that corresponding entries across language to use the same ID, so that tools that cross-reference across languages can be made.

### `platform-restriction` (User670)

If present, one of the following: `apple` or `non-apple`.

If a pair of entries with the same ID and opposite `platform-restriction` are present, then when exporting to Lua script, a conditional would be added to make the `apple` entry appear on iOS and MacOS devices, and `non-apple` entry on other devices.

## Other formatting notes

### Line continuation in markdown

In the code blocks in markdown format, you can use backslash at the end of a line to indicate a line continuation. For example, this code block

```
some text \
goes here
```

would be parsed into `"content":"some text goes here"`, on one line.

You would need to beware of whitespaces for languages where that matters. A continuation line will have its leading whitespaces stripped, so you might need a space before the backslash on the previous line:

```
    some text\
    goes here
```

would be parsed into `"content":"    some textgoes here"`.

When outputting markdown, line continuations will not be added.

### Unicode PUA characters

In Markdown and Verbose JSON representations, Unicode Private Use Area characters can be written as `{{code}}`, where `code` is either a hexadecimal Unicode code point (with the `0x` prefix), eg. `{{0xF0001}}`, or a name defined in Techmino's [`parts/char.lua`](https://github.com/26F-Studio/Techmino/blob/main/parts/char.lua), eg. `{{zChan.normal}}`.

When reading in-game representation JSON, literal PUA characters will be converted to this representation.

When dumping to Lua, named PUA characters would be converted to Lua string concatenation (`..CHAR.zChan.normal..`), and code point ones would be converted to literal characters.

### `[Tt]etris` and `[Pp]atreon`

The words "Tetris" and "Patreon" are not censored by this script.
