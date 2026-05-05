import MarkdownIt from 'markdown-it';
import DOMPurify from 'dompurify';

const md = new MarkdownIt({
  html: true,        // 允许 HTML 标签
  linkify: true,     // 自动转换链接
  typographer: true,
});

export function useMarkdown() {
  const render = (rawText) => {
    if (!rawText) return '';
    // 1. 将 Markdown 转为 HTML
    const html = md.render(rawText);
    // 2. 过滤危险标签（防止 XSS）
    return DOMPurify.sanitize(html);
  };

  return { render };
}