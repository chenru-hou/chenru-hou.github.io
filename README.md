# 个人科研主页

简洁、响应式的静态学术主页，包含 Home、Publications、Blog 和博客文章详情页。所有内容保存在仓库中，无需数据库或付费服务。初始姓名、机构、研究方向与论文均为明确的占位内容。

## 修改内容

- `content/profile.json`：姓名、简介、单位、研究方向、联系方式、外部链接、近况。email 为空时不显示邮箱。
- `content/publications.json`：复制一个条目即可增加论文；按年份自动倒序。`links` 示例：`[{"label":"DOI","url":"https://doi.org/你的DOI"},{"label":"Code","url":"https://github.com/你的项目"}]`。
- `content/posts/*.md`：每个文件为一篇博客。复制示例文章，修改头部 title、date、tag、summary 与正文即可。文件名使用小写英文字母、数字和连字符，例如 `2026-12-01-reading-notes.md`。日期格式 YYYY-MM-DD。当前支持段落、标题、无序列表、粗体、行内代码和 http(s) 链接，HTML 会自动转义。空列表也能正常显示。
- `assets/style.css`：颜色、字体和布局；替换照片可修改 `scripts/build.py` 中的 portrait 模板，并将图片放入 assets。

## 本地预览

仅需 Python 3，无第三方依赖：

```sh
python3 scripts/build.py
python3 -m http.server 8000 --directory dist
```

打开 http://localhost:8000 。每次修改内容后重新执行构建。

## GitHub Pages 公开部署

代码提交到 `main` 后，`.github/workflows/pages.yml` 自动构建并发布。首次使用时进入仓库 Settings → Pages → Build and deployment，选择 **GitHub Actions**（需要仓库管理员权限）。如首次工作流因 Pages 未启用而失败，完成该设置后在 Actions 中重新运行。

预期网址（部署成功后才可访问）：https://chenru-hou.github.io/website/

此站点使用相对链接，同时支持仓库子路径和自定义域名。没有后端、登录或在线编辑器；日常更新可直接使用 GitHub 网页编辑文件并提交，工作流随后发布更新。
