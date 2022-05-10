# ProjectMu

ProjectMu 是一个用于通过简谱生成 .wav 格式音频文件的工具。

ProjectMu is a tool for generating audio files in .wav format from numbered musical notations.

## 使用方法

`mu [NMNFILE] [-o WAVFILE] [-tN]`

| 参数 | 作用 |
| --- | --- |
| `NMNFILE` | 从 NMNFILE 中读取乐谱文件（如缺省，则默认从标准输入中读取） |
| `-o WAVFILE` | 输出到 WAVFILE 中（如缺省，则默认输出到 a.wav） |
| `-tN` | 设置输出音频文件音色（0，1，2，3，4 分别表示正弦波、方波、三角波、锯齿波、叠加的正弦波。默认输出音色是正弦波） |

示例:

`mu 'example/Bad Apple!!.nmn' -o 'Bad Apple!!.wav' -t1`

## NMN 文件格式

### 整体格式

```
调号 节奏型 速度
x x x x | x x x x | x x x x |
x x x x | x x x x | x x x x |&

调号 节奏型 速度
x x x x | x x x x | x x x x |
x x x x | x x x x | x x x x |&

~
x x x x | x x x x | x x x x |:

1 3 2 3
```

| 符号 | 说明 |
| --- | --- |
| 调号 | 大写字母表示大调，小写字母表示小调，如 `C#` 表示升 C 大调，`bb` 表示降 b 小调。 |
| 节奏型 | 如 `4/4`, `6/8`, `1/2` ... |
| 速度 | 每分钟节拍数（BPM） |
| `\|` | 小节线 |
| `\|&` | 用于表示该部分乐谱结束。（如果乐曲的调号、节奏型、速度中途改变，或者乐曲中有反复记号等，可以将乐曲分为多个部分进行整理） |
| `\|:` | 用于表示乐谱结束。在该符号后需要有各部分乐谱在整首乐曲中的排列顺序。如果整首乐曲只有一个部分或者各部分已经按顺序排列，则可以直接用 `||` 代替该符号。 |
| `~` | 保持调号、节奏型、速度和前一部分相同。 |

### 音符格式

```
6vb .1/ , <36=> | 6b - 0 0 |
```
```
4# - 1^ [3:7/,/6/] | 5# - - 1^/2^/ |
```

| 符号 | 说明 |
| --- | --- |
| `6` | 音符（La） |
| `0` | 休止符 |
| `,` | 用于替代沿音线，表示延续上一个音符 |
| `^` | 将前面的音符升高八度 |
| `v` | 将前面的音符降低八度 |
| `#` | 升号（放置在音符后） |
| `b` | 降号（同上） |
| `=` | 还原号（同上） |
| `-` | 延长线，每加一条横线延长一个四分音符的长度 |
| `.` | 附点 |
| `/` | 用于表示下划线 |
| `<...>` | 在 `<` 和 `>` 之间的音符会统一额外添加下划线。例如， `<<1/2/> 2/>` 等价于 `1///2/// 2//`. |
| `[3:...]` | 三连音，同理 `[5:...]` 表示五连音 |

更多乐谱示例请查看[这里](example)。
