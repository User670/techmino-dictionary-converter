# techmino-dictionary-converter

本仓库包含一个 Python 脚本，用来转换不同格式的小Z词典。

## 快速帮助

```
python tool.py [flags] infile outfile
```

脚本会根据扩展名推测输入和输出格式。(`.json`，`.lua` 或 `.md`，不区分大小写。)

您也可以使用 flags 手动指定一个输入或输出格式。

扩展名为 `.json` 的输入文件会被假设为详细格式（Python 脚本内部储存格式）。要指定匹配游戏内部格式的 JSON 文件格式，请使用 `--read-lua-json` flag。

可用的 flags 如下：

```
-h, --help       : 显示帮助信息。
--read-json      : 假设输入文件是详细格式的 JSON。
--read-lua-json  : 假设输入文件是游戏内格式的 JSON。
--read-md        : 假设输入文件是 markdown。
--dump-json      : 输出详细格式的 JSON。
--dump-lua       : 输出 Lua 脚本。
--dump-md        : 输出 markdown。
```

## 格式标准

### Markdown

兼容的 Markdown 文件格式类似下面的例子：

```
在标题之上的文本是注释……

# 一级标题也是……

一级标题和下一个二级标题之间的文本也是。

## 二级标题是词典词条的标题。
- metadata-key: 元数据以无序列表的形式紧随二级标题之后。

` ` `
代码块包含词条正文。
` ` `
```

在二级标题下但是既不是无序列表，又不是代码块的文本术语未定义行为——脚本的代码没有处理这些情况的逻辑。

标题必须是 `# text` 格式，不可以是 `# text #` 或者 `text\n====`

代码块必须用三个反引号，不可以用缩进4个空格。三个反引号必须自成一行。

无序列表可以用 `-`, `+` 或 `*`。

### 详细 JSON 格式

详细 JSON 格式的例子如下：

```json
[
  {
    "type":"text",
    "content":"不属于词条的一般文本这样表示"
  },
  {
    "type":"h1",
    "content":"一级标题这样表示"
  },
  {
    "type":"entry",
    "title":"词条标题在此",
    "metadata":{
      "metadata-key":"metadata value",
    }
    "content":"词条正文在此"
  }
]
```

### 游戏内格式

游戏内表示小Z词典的格式是一个2维数组，例子如下：（下面是 Lua table 的语法）

```lua
{
  {
    "词条标题",
    "搜索关键字 (search-terms) 元数据",
    "分类 (category) 元数据",
    "正文",
    "[可选] 网址 (URL) 元数据"
  }
}
```

脚本不能直接读取 Lua 源代码。要读取游戏内的数据，请先转换为 JSON，然后使用 `--read-lua-json` flag。

导出 Lua 脚本时，注释文本、一级标题和额外元数据会导出为 Lua 注释。

## 元数据

目前 User670（本 Python 脚本的作者）识别或定义了以下的元数据项目。您可以按您的应用的需求自行添加元数据。

元数据名称别称只能在 Markdown 格式中使用；读取 Markdown 文件时会自动转换成正确的元数据名称。读取 JSON 文件不会做如此的转换。

### 搜索关键字 `search-terms` (必填，Techmino)

别称：`search-term`

游戏内用于搜索功能。

### 分类 `category` (必填，Techmino)

以下值中的一个：`help`, `org`, `game`, `term`, `setup`, `pattern`, `command`, `english`, `name`

游戏内用来决定显示颜色。

### 网址 `url` (Techmino)

别称：`web`, `website`

和词条相关的一个网址。游戏内有一个按钮可以跳转到该网址。

### `id` (User670)

词条的一个识别符。

目前，如果使用了 `platform-restriction`，则该元数据必填。一对 `id` 相同，`platform-restriction` 相异的词条会在导出 Lua 脚本的时候生成平台受限的词条。

此外，建议在不同语言的对应词条使用相同的 `id`，方便带有跨语言对照的工具开发。

### 平台限制 `platform-restriction` (User670)

如果存在，则应为以下两个值中的一个：`apple` or `non-apple`

如果两个词条有相同的 `id` 和不同的 `platform-restriction`，那么导出成 Lua 脚本的时候会添加一个条件判断，使得 `apple` 的词条显示在 iOS 和 MacOS 的设备上，`non-apple` 的词条显示在其他设备上。

## 其他格式注意事项

### Markdown格式中的换行

在 markdown 格式的代码块里，您可以在一行末尾使用反斜杠（`\`）表示行接续。例如，下面的代码块

```
some text \
goes here
```

会被理解为一行文字， `"content":"some text goes here"`。

对于带有空格的语言，您需要注意空格字符。接续行开头的空白字符会被去掉，这意味着您可能需要在前一行的反斜杠前添加空格。例如，

```
    some text\
    goes here
```

会被解析成 `"content":"    some textgoes here"`。

导出 markdown 的时候，行接续不会自动添加。

### Unicode 私用区字符

在 markdown 和详细 JSON 格式中，Unicode 私用区字符可以被表示为 `{{code}}`，其中 `code` 可以是16进制 Unicode 码点（带 `0x` 前缀)，例如 `{{0xF0001}}`，或者在 Techmino 的 [`parts/char.lua`](https://github.com/26F-Studio/Techmino/blob/main/parts/char.lua) 定义的名称，例如 `{{zChan.normal}}`。

读取游戏内格式 JSON 时，字面的私用区字符会被转换为这种格式。

导出成 Lua 时，用名称表示的私用区字符会被转化成 Lua 字符串拼接 (`..CHAR.zChan.normal..`)，用码点表示的会被转化成字面字符。

### `[Tt]etris` 和 `[Pp]atreon`

"Tetris" 和 "Patreon" 这两个词在这个脚本中未被和谐。
