# 题目仓库

## 支持题型

| 题型 | 支持| 含参生成 | 题库抽题 |
| --- | :-: | :-: | :-: |
| 单项选择题 | 是 | 是 | 是 |
| 判断题 | 是 | TODO | 是 |
| 文字填空题 | 是 | TODO | 是 |
| 多项选择 | 否 | TODO | TODO |

----

### 单项选择题
单项选择题选项标记模式形如：
```markdown
- 选项1
- 选项2
- 选项3
- 选项4
```
其中**第一个**选项（`选项1`）须为该题答案。

*注意：*
选项中不应加入`A`, `B`等标记，在生成题目时将打乱选项顺序并添加编号标记。

详细样例请参考`./selective`中的样例文件。

------

### 判断题
判断题选项标记模式形如：
```markdown
- 错误
- 正确
```
其中**第一个**s选项（`错误`）须为该题答案。

详细样例请参考`./judge`中的样例文件。

------

### 文字填空题
文字填空题标记模式形如：
```markdown
| type | value |
|---|---|
| %{Answer 1}% | `0xffff` |
| %{Answer 2}% | `0x0000`|
```
其中`%{Answer 1}% `与`%{Answer 2}% `将被替换为`<1>`与`<2>`待填空。

详细样例请参考`./text`中的样例文件。

------

## 含参生成
含参生成需要在题目中*定义参数*，*标记参数*。

样例：
```markdown
$ X = ['a', 'b']
$ Y = [1, 2, 3, 4]
$ Z = [ {'alph': 'a', 'num': 1}, {'alph': 'b', 'num': 2}]
在此处随机插入参数X中的某一项：%{X}%。
在此处随机插入参数Y中的某一项：%{Y+3}%。由于y中的候选项为int，可支持运算。
在此处随机插入参数Z中的某一组：%{Z['alph']}%与%{Z['num']}%。
```

*注意：*
在同一道题中随机的选项相同。
