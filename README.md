# ProjectMu

ProjectMu 是一个用于通过简谱生成 .wav 格式音频文件的工具。

ProjectMu is a tool for generating audio files in .wav format from numbered musical notations.

## 使用方法

```
mu [NMNFILE] [-o WAVFILE] [-tN]
```

| 参数 | 作用 |
| --- | --- |
| `NMNFILE` | 从 NMNFILE 中读取乐谱文件 |
| `-o WAVFILE` | 输出到 WAVFILE 中（如缺省，则默认输出到 a.wav） |
| `-tN` | 设置输出音频文件音色（0，1，2，3，4 分别表示正弦波、方波、三角波、锯齿波、叠加的正弦波。缺省时默认生成正弦波） |

示例:

```
mu 'example/Bad Apple!!.nmn' -o 'Bad Apple!!.wav' -t1
```

## NMN 文件格式

### 示例

+ Lemon - 米津玄师

```
B 4/4 174
0 0 0 1^/2^/ |
3^ 1^/6/ , 2^ | 7 5/3/ , 7 | 6 5/1/ , 5 | 3 - - 2/3/ |
4 - 1^ [3:7/,/1^/] | 5 - 4 3./4// | 4# - 1^ [3:7/,/6/] | 5# - - 1^/2^/ |
3^ 1^/6/ , 2^ | 7 5/3/ , 7 | 6 5/1/ , 5 | 3 - - 2/3/ |
4 - 5 [3:4/,/5/] | 3 5 1^ 3^ | 2^ .2^/ 2^/1^/ ,/1^/ | 1^ - - - ||
```

+ Bad Apple!! - nomico

```
F# 4/4 137
6vv <<06vv5vv6vv>> 6vv <<06vv5vv6vv>> | 6vv <<06vv5vv6vv> 6vv<6vv1v> 2v<1v2v>> |
6vv <<06vv5vv6vv>> 6vv <<06vv5vv6vv>> | 6vv <<06vv5vv6vv> 2v<1v2v> 1v<6vv1v>> |&

~
<6v7v 12> 3 <65> | 3 6v <32 17v> | <6v7v 12> 3 <21> | <7v6v 7v1 7v6v 5#v7v> |
<6v7v 12> 3 <65> | 3 6v <32 17v> | <6v7v 12> 3 <21> | 7v 1 2 3 |&

~
<56 32> 3 <23> | <56 32> 3 <23> | <21 7v5v> 6v <5v6v> | <7v1 23> 6v <35> |
<56 32> 3 <23> | <56 32> 3 <23> | <21 7v5v> 6v <5v6v> | <7v1 23> 6v <35> |
<56 32> 3 <23> | <56 32> 3 <23> | <21 7v5v> 6v <5v6v> | <7v1 23> 6v <35> |
<56 32> 3 <23> | <56 32> 3 <67> | <1^7 65> 3 <23> | <21 7v5v> 6v |&

~
<35> |&

~
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

### 整体格式

| 符号 | 说明 |
| --- | --- |
| `F#` | 调式。用大写字母表示大调，小写字母表示小调，如 `C#` 表示升 C 大调，`bb` 表示降 b 小调。 |
| `4/4` | 节奏型。如 `4/4`, `6/8`, `1/2` ... |
| `174` | 每分钟节拍数（BPM） |
| `\|` | 小节线 |
| `\|&` | 用于表示该部分乐谱结束。（当乐曲的调号、节奏型、速度中途改变，或者乐曲中存在反复记号时使用） |
| `~` | 保持调号、节奏型、速度和上一部分相同。 |
| `\|\|` | 用于表示乐谱结束。 |
| `\|:` | 当乐谱中存在反复记号或各个部分并非按顺序排列时，用此符号表示乐谱结束。在该符号下一行需注明乐谱各部分在整首乐曲中的排列顺序。 |

### 音符格式

| 符号 | 说明 |
| --- | --- |
| `6` | 音符（La） |
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
| `[3:...]` | 三连音，同理， `[5:...]` 表示五连音 |

更多乐谱示例见[此处](example)。
