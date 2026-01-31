# - 工具：Markdown 渲染與消毒
# - 說明：將 Markdown 轉為 HTML，並使用 Bleach 做消毒以防 XSS
# - 註解：依憲法規範使用繁體中文註解，函式與變數採駝峰式命名

from typing import List

try:
    import markdown
    import bleach
except Exception:
    # 如果套件尚未安裝，讓開發者在執行時安裝；此處不會中止 import
    markdown = None
    bleach = None


def render_markdown(markdownText: str) -> str:
    """將 Markdown 轉為安全的 HTML。

    參數：
    - `markdownText`: 原始 Markdown 文字

    回傳：
    - 經過消毒的 HTML 字串
    """
    # 若未安裝相依套件，直接回傳原始（非理想），呼叫端會處理例外
    if markdown is None or bleach is None:
        raise RuntimeError('請安裝 markdown 與 bleach 套件以啟用 markdown 渲染')

    # 使用 CommonMark 風格的擴充功能集合（視需求可調整）
    extensions: List[str] = [
        'extra',
        'codehilite',
        'toc',
    ]

    # 先將 Markdown 轉為未消毒的 HTML
    unsafeHtml = markdown.markdown(markdownText or '', extensions=extensions, output_format='html5')

    # Bleach 允許的 tags & attributes（可視安全需求收斂）
    allowedTags = list(bleach.sanitizer.ALLOWED_TAGS) + [
        'p', 'pre', 'code', 'img', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'thead', 'tbody', 'tr', 'th', 'td'
    ]
    allowedAttributes = {
        **bleach.sanitizer.ALLOWED_ATTRIBUTES,
        'img': ['src', 'alt', 'title'],
        'a': ['href', 'title', 'rel'],
        'th': ['colspan', 'rowspan'],
    }

    # 清理 HTML 並自動將連結轉為安全連結
    cleaned = bleach.clean(unsafeHtml, tags=allowedTags, attributes=allowedAttributes)
    linked = bleach.linkify(cleaned)

    return linked
