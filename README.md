# 个人科研主页

简洁、响应式的静态学术主页，包含 Home、Publications、Blog 和博客文章详情页。所有内容保存在仓库中，无需数据库或付费服务。个人资料与论文信息依据用户提供的简历及主页文档整理。未提供 DOI、全文链接或真实博客文章，因此没有添加这些内容。

## 修改内容

- `content/profile.json`：姓名、简介、单位、研究方向、联系方式、外部链接、近况。email 为空时不显示邮箱。
- `content/publications.json`：复制一个条目即可增加论文；按年份自动倒序。`links` 示例：`[{"label":"DOI","url":"https://doi.org/你的DOI"},{"label":"Code","url":"https://github.com/你的项目"}]`。
- `content/posts/*.md`：每个文件为一篇博客。新建文件，在正文前添加由 `---` 包围的头部，逐行填写 `title: 标题`、`date: 2026-11-02`、`tag: 随笔`、`summary: 简介`，然后编写正文。文件名使用小写英文字母、数字和连字符，例如 `2026-12-01-reading-notes.md`。日期格式 YYYY-MM-DD。当前支持段落、标题、无序列表、粗体、行内代码和 http(s) 链接，HTML 会自动转义。空列表也能正常显示。
- `assets/style.css`：颜色、字体和布局。

## 本地预览

仅需 Python 3，无第三方依赖：

```sh
python3 scripts/build.py
python3 -m http.server 8000 --directory dist
```

打开 http://localhost:8000 。每次修改内容后重新执行构建。

## GitHub 同步与构建

代码提交到 `main` 后，`.github/workflows/pages.yml` 仅检查网站能否成功构建，不会发布或部署网站。

日常更新可直接使用 GitHub 网页编辑 `content/profile.json`（包括教育、研究经历、会议、教学和 Methods）及 `content/publications.json`。论文条目的 `homepage: true` 控制是否显示在主页。

需要单文件私有预览时，运行 `python3 scripts/preview.py`，生成 `private-preview.html` 和 `website-preview.zip`。这些预览文件无需上传到仓库。
