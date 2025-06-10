<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9"
  exclude-result-prefixes="sitemap">
  
  <xsl:output method="html" encoding="UTF-8" indent="yes" omit-xml-declaration="yes"/>
  
  <xsl:template match="/">
    <html lang="zh-CN">
      <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>站点地图索引 - 每日 AI 小故事</title>
        <style>
          :root {
            --primary: #4361ee;
            --secondary: #3f37c9;
            --light: #f8f9fa;
            --dark: #212529;
            --gray: #6c757d;
          }
          * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
          }
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: var(--dark);
            background-color: #f5f7ff;
            padding: 2rem 1rem;
          }
          .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            overflow: hidden;
          }
          header {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 2rem;
            text-align: center;
          }
          h1 {
            font-weight: 600;
            font-size: 2.25rem;
            margin-bottom: 0.5rem;
          }
          .subtitle {
            opacity: 0.9;
            font-weight: 300;
            font-size: 1.1rem;
          }
          .info-bar {
            background-color: #eef2ff;
            padding: 1rem;
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
            color: var(--gray);
            border-bottom: 1px solid #dee2e6;
          }
          table {
            width: 100%;
            border-collapse: collapse;
          }
          thead {
            background-color: #edf2ff;
          }
          th {
            padding: 1.25rem 1.5rem;
            text-align: left;
            font-weight: 600;
            color: var(--secondary);
            border-bottom: 2px solid #dee2e6;
          }
          td {
            padding: 1.25rem 1.5rem;
            border-bottom: 1px solid #e9ecef;
          }
          tr:hover {
            background-color: #f8f9ff;
          }
          .url-cell {
            max-width: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
          .url-cell a {
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
          }
          .url-cell a:hover {
            text-decoration: underline;
            color: var(--secondary);
          }
          footer {
            text-align: center;
            padding: 1.5rem;
            color: var(--gray);
            font-size: 0.9rem;
            border-top: 1px solid #e9ecef;
          }
          @media (max-width: 768px) {
            .info-bar { flex-direction: column; gap: 0.5rem; text-align: center; }
            th, td { padding: 0.75rem; }
            h1 { font-size: 1.75rem; }
          }
        </style>
      </head>
      <body>
        <div class="container">
          <header>
            <h1>每日 AI 小故事 · 站点地图</h1>
            <div class="subtitle">内容索引与更新记录</div>
          </header>
          
          <div class="info-bar">
            <div>总链接数: <xsl:value-of select="count(sitemap:urlset/sitemap:url)"/></div>
            <div>最后更新: 
              <!-- XSLT 1.0兼容的时间格式化 -->
              <xsl:variable name="latest" select="(sitemap:urlset/sitemap:url/sitemap:lastmod)[last()]"/>
              <xsl:value-of select="concat(
                substring($latest, 1, 10), 
                ' ', 
                substring($latest, 12, 5)
              )"/>
            </div>
          </div>
          
          <table>
            <thead>
              <tr>
                <th width="70%">页面地址</th>
                <th width="30%">最后更新时间</th>
              </tr>
            </thead>
            <tbody>
              <xsl:for-each select="sitemap:urlset/sitemap:url">
                <xsl:sort select="sitemap:lastmod" order="descending"/>
                <tr>
                  <td class="url-cell">
                    <a href="{sitemap:loc}" target="_blank" rel="noopener noreferrer">
                      <xsl:value-of select="sitemap:loc"/>
                    </a>
                  </td>
                  <td>
                    <!-- XSLT 1.0兼容的时间格式化 -->
                    <xsl:value-of select="concat(
                      substring(sitemap:lastmod, 1, 10), 
                      ' ', 
                      substring(sitemap:lastmod, 12, 5)
                    )"/>
                  </td>
                </tr>
              </xsl:for-each>
            </tbody>
          </table>
          
          <footer>
            <div>© 2025 每日 AI 小故事 · 自动生成</div>
          </footer>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>