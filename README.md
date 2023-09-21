# ProjectMu

ProjectMu 是一个用于通过简谱生成 .wav 格式音频文件的工具。

ProjectMu is a tool for generating audio files in .wav format from numbered musical notations.

## 使用方法

```
Description: Generate audio file from numeric music notation.
Usage: mu [-o OUTFILE] [-t<n>] FILE
Options:
  FILE        input file name
  -o OUTFILE  output file name (default: a.wav)
  -t0         timbre: sine wave (default)
  -t1         timbre: superimposed sine waves
  -t2         timbre: triangle wave
  -t3         timbre: sawtooth wave
  -t4         timbre: square wave
  -t5         timbre: plucked string
```

| 参数 | 作用 |
| --- | --- |
| `FILE` | 从 FILE 中读取乐谱文件 |
| `-o OUTFILE` | 输出到 OUTFILE 中（如缺省，则默认输出到 a.wav） |
| `-t<n>` | 设置输出音频文件音色（`n` = `0`，`1`，`2`，`3`，`4`, `5` 时分别表示正弦波、木管乐器、三角波、锯齿波、方波和拨弦乐器音色。缺省时默认生成正弦波） |

示例:

```
mu -o 'Bad Apple!!.wav' -t1 'example/Bad Apple!!.nmn'
```

## 简谱格式说明

### 示例

+ Lemon - 米津玄师

```
B 4/4 174
0 0 0 1^/2^/ |
3^ 1^/6/ , 2^ | 7 5/3/ , 7 | 6 5/1/ , 5 | 3 - - 2/3/ |
4 - 1^ [3:2]7/,/1^/! | 5 - 4 3./4// | 4# - 1^ [3:2]7/,/6/! | 5# - - 1^/2^/ |
3^ 1^/6/ , 2^ | 7 5/3/ , 7 | 6 5/1/ , 5 | 3 - - 2/3/ |
4 - 5 [3:2]4/,/5/! | 3 5 1^ 3^ | 2^ .2^/ 2^/1^/ ,/1^/ | 1^ - - - ||
```

+ Bad Apple!! - nomico

```
F# 4/4 137
6vv <<06vv5vv6vv>> 6vv <<06vv5vv6vv>> | 6vv <<06vv5vv6vv> 6vv<6vv1v> 2v<1v2v>> |
6vv <<06vv5vv6vv>> 6vv <<06vv5vv6vv>> | 6vv <<06vv5vv6vv> 2v<1v2v> 1v<6vv1v>> |~

<6v7v 12> 3 <65> | 3 6v <32 17v> | <6v7v 12> 3 <21> | <7v6v 7v1 7v6v 5#v7v> |
<6v7v 12> 3 <65> | 3 6v <32 17v> | <6v7v 12> 3 <21> | 7v 1 2 3 |~

<56 32> 3 <23> | <56 32> 3 <23> | <21 7v5v> 6v <5v6v> | <7v1 23> 6v <35> |
<56 32> 3 <23> | <56 32> 3 <23> | <21 7v5v> 6v <5v6v> | <7v1 23> 6v <35> |
<56 32> 3 <23> | <56 32> 3 <23> | <21 7v5v> 6v <5v6v> | <7v1 23> 6v <35> |
<56 32> 3 <23> | <56 32> 3 <67> | <1^7 65> 3 <23> | <21 7v5v> 6v |~

<35> |~

0 |&

G 4/4 137
<35> |
<56 32> 3 <23> | <56 32> 3 <23> | <21 7v5v> 6v <5v6v> | <7v1 23> 6v <35> |
<56 32> 3 <23> | <56 32> 3 <23> | <21 7v5v> 6v <5v6v> | <7v1 23> 6v <35> |
<56 32> 3 <23> | <56 32> 3 <23> | <21 7v5v> 6v <5v6v> | <7v1 23> 6v <35> |
<56 32> 3 <23> | <56 32> 3 <67> | <1^7 65> 3 <23> | <21 7v5v> 6v 0 |
<6v.6v/ ,6v 6v.6v/ ,6v> | <6v.6v/ ,6v 6v.6v/ ,6v> | <6v.6v/ ,6v 6v.6v/ ,6v> | <6v.6v/ ,6v 6v.6v/ ,0> |:

1 1 2 2 3 4 3 5 1 1 2 2 3 6
```

### 段落格式

| 符号 | 说明 |
| --- | --- |
| `F#` | 调式。`F#` 即 `1 = F#`（升 F 大调），又如，降 C 大调表示为 `Cb`。 |
| `4/4` | 节奏型。如 `4/4`, `6/8`, `1/2` ... |
| `174` | 每分钟节拍数（BPM） |
| `\|` | 小节线 |
| `\|&` | 用于表示该块乐谱结束，下一块需要重新设置调号、节奏型和速度。（用于当乐曲的调号、节奏型与速度中途改变时） |
| `\|~` | 用于表示该块乐谱结束，且下一块调号、节奏型、速度和当前节相同。（通常用于当乐曲中存在反复记号时） |
| `\|\|` | 用于表示乐谱结束。 |
| `\|:` | 当乐谱中存在反复记号（各个块的演奏顺序需要手动排列）时，用此符号表示乐谱结束。并在后面输入乐谱各个块在整首乐曲中的排列顺序。 |

### 音符格式

| 符号 | 说明 |
| --- | --- |
| `1` ~ `7` | 音符 |
| `0` | 休止符 |
| `,` | 用于替代延音线第一个以后的音符，表示延续前一个音符 |
| `#` | 升号（放置在音符后） |
| `b` | 降号（同上） |
| `=` | 还原号（同上） |
| `^` | 将当前音符升高八度 |
| `v` | 将当前音符降低八度 |
| `-` | 延长线，每加一条横线延长一个四分音符的长度 |
| `.` | 附点 |
| `/` | 用于表示下划线 |
| `<...>` | 在 `<` 和 `>` 之间的音符会统一额外添加下划线。例如， `<<1/2/> 2/>` 等价于 `1///2/// 2//`. |
| `[3:2]...!` | （由两拍分拆而来的）三连音，同理， `[5:4]...!` 表示（由四拍分拆而来的）五连音。由四拍、六拍分拆而来或由八拍结合合而来的七连音分别表示为 `[7:4]...!`，`[7:6]...!` 和 `[7:8]...!`，依此类推。 |

*注：除以上符号外的字符（如空格，括号，换行等）在乐谱中只起到方便阅读的作用，没有实际意义。*

更多乐谱示例见[此处](example)。
