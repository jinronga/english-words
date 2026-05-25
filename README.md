# 英语单词整理

本项目整理人教版小学、初中、高中英语单词表，并补充四级、六级英语词汇，方便按学段、教材册次与考试分类复习。

## 内容概览

- 教材词表来源：`https://english.mikigo.site/`
- 四级、六级词库来源：`https://github.com/KyleBing/english-vocabulary`
- 音标来源：有道词典（英式 / 美式）
- 词组音标说明：词组缺少直出音标时，按组成词音标拼接供参考
- 例句说明：每个词条在表格中保留 1 条英文例句和中文翻译，表格后 `## 更多例句` 中再提供 3 条英文例句及对应中文翻译
- 四级、六级说明：当前保留单词、中文释义、例句与例句翻译，音标暂以 `-` 占位

| 学段 | 目录 | 文件数量 | 词条数量 | 例句数量 |
| --- | --- | ---: | ---: | ---: |
| 小学 | `小学/` | 8 | 849 | 3396 |
| 初中 | `初中/` | 5 | 2317 | 9268 |
| 高中 | `高中/` | 9 | 3207 | 12828 |
| 四级 | `四级/` | 1 | 7508 | 30032 |
| 六级 | `六级/` | 1 | 5651 | 22604 |
| 合计 | - | 24 | 19532 | 78128 |

## 目录结构

```text
.
├── 小学/
│   ├── 三年级/
│   ├── 四年级/
│   ├── 五年级/
│   └── 六年级/
├── 初中/
│   ├── 七年级/
│   ├── 八年级/
│   └── 九年级/
├── 高中/
│   ├── 必修/
│   └── 选修/
├── 四级/
├── 六级/
└── scripts/
```

## 快速导航

- [GitHub Pages 首页](https://jinronga.github.io/english-words/)
- [小学单词整理](小学/)
- [初中单词整理](初中/)
- [高中单词整理](高中/)
- [四级单词整理](四级/)
- [六级单词整理](六级/)

## 文件格式

每个词表文件包含两部分：

1. 单词表：序号、单词、英式音标、美式音标、中文翻译、例句、例句翻译
2. 更多例句：按词条编号列出每个单词的 3 条补充例句，并在每条英文下面给出中文翻译

四级、六级词表暂不含真实音标，音标列以 `-` 占位，其余列与教材词表保持一致。

## 维护脚本

`scripts/add_example_sentences.py` 用于批量补齐或重建例句内容：

```bash
python3 scripts/add_example_sentences.py
```

脚本可重复运行，会重建 `## 更多例句` 区块，不会重复追加旧内容。

`scripts/example_translations.json` 是英文例句到中文译文的缓存文件，脚本会优先使用该缓存生成中文翻译。

`scripts/generate_cet_vocab.py` 用于从公开 CET4 / CET6 JSON 词库重新生成四级、六级 Markdown 文件：

```bash
python3 scripts/generate_cet_vocab.py
```

## GitHub Pages 发布

本仓库已补充 GitHub Pages 配置和词典式首页界面：

- `_config.yml`：Jekyll 站点配置，并启用 Markdown 相对链接转换
- `_layouts/default.html`：自定义站点布局，包含顶部导航、主题切换和页面类型标记
- `index.md`：学习入口首页，先按小学、初中、高中、四级、六级进入分类页
- `assets/css/style.scss`：实现简约入口卡片、学习卡片、表格和移动端响应式样式
- `assets/js/home.js`：实现黑白主题、分类页入口增强、词表页学习模式和本地学习进度

发布方式：

1. 进入 GitHub 仓库 `Settings` → `Pages`
2. `Build and deployment` 选择 `Deploy from a branch`
3. `Branch` 选择 `main`，目录选择 `/root`
4. 保存后等待 GitHub Pages 构建完成

项目发布后的访问地址应为：

```text
https://jinronga.github.io/english-words/
```

GitHub Pages 只发布静态内容，`scripts/` 里的 Python 脚本不会在网页端运行；需要更新词表时，先在本地运行脚本并提交生成后的 Markdown 文件。
