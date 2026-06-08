from html import escape

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse


router = APIRouter(include_in_schema=False)


def _openapi_url(request: Request) -> str:
    root_path = request.scope.get("root_path", "")
    return f"{root_path}/openapi.json"


def _render(template: str, *, title: str, openapi_url: str) -> HTMLResponse:
    html = (
        template.replace("__TITLE__", escape(title))
        .replace("__OPENAPI_URL__", escape(openapi_url, quote=True))
    )
    return HTMLResponse(html)


@router.get("/docs")
async def swagger_docs(request: Request) -> HTMLResponse:
    return _render(
        _SWAGGER_HTML,
        title="AtlasCore Auth API - Swagger",
        openapi_url=_openapi_url(request),
    )


@router.get("/redoc")
async def redoc_docs(request: Request) -> HTMLResponse:
    return _render(
        _REDOC_HTML,
        title="AtlasCore Auth API - ReDoc",
        openapi_url=_openapi_url(request),
    )


_SWAGGER_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>__TITLE__</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    <style>
      :root {
        color-scheme: dark;
        --background: #0b1019;
        --surface: #121b2b;
        --surface-soft: #172235;
        --surface-raised: #1b2840;
        --code-bg: #0f1726;
        --border: #314158;
        --text: #e6edf7;
        --muted: #a9b6c8;
        --accent: #58c4dc;
        --green: #56d364;
        --blue: #58a6ff;
        --orange: #f2cc60;
        --red: #ff7b72;
        --purple: #d2a8ff;
      }

      body {
        margin: 0;
        background: var(--background);
        -webkit-font-smoothing: antialiased;
        text-rendering: optimizeLegibility;
      }

      .swagger-ui * {
        text-shadow: none !important;
        -webkit-text-stroke: 0 transparent;
      }

      .swagger-ui,
      .swagger-ui .info .title,
      .swagger-ui .opblock-tag,
      .swagger-ui .parameter__name,
      .swagger-ui table thead tr td,
      .swagger-ui table thead tr th,
      .swagger-ui .response-col_status,
      .swagger-ui .response-col_links,
      .swagger-ui .response-col_description,
      .swagger-ui .model-title,
      .swagger-ui .model,
      .swagger-ui .prop-format,
      .swagger-ui .prop-type,
      .swagger-ui .tab li,
      .swagger-ui label,
      .swagger-ui p {
        color: var(--text);
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }

      .swagger-ui .scheme-container,
      .swagger-ui .topbar {
        background: var(--surface);
        border-bottom: 1px solid var(--border);
        box-shadow: none;
      }

      .swagger-ui .topbar .download-url-wrapper,
      .swagger-ui .topbar .link {
        display: none;
      }

      .swagger-ui .wrapper {
        max-width: 1260px;
      }

      .swagger-ui .info {
        margin: 32px 0 24px;
      }

      .swagger-ui .info .title {
        font-size: 2.4rem;
        letter-spacing: 0;
      }

      .swagger-ui .info .description,
      .swagger-ui .info li,
      .swagger-ui .opblock-description-wrapper p,
      .swagger-ui .response-col_description__inner div,
      .swagger-ui .markdown p {
        color: var(--muted);
      }

      .swagger-ui .filter .operation-filter-input,
      .swagger-ui input,
      .swagger-ui select,
      .swagger-ui textarea {
        border: 1px solid var(--border);
        border-radius: 8px;
        background: var(--code-bg);
        color: var(--text);
      }

      .swagger-ui .filter .operation-filter-input {
        margin: 0 0 22px;
        padding: 10px 12px;
      }

      .swagger-ui .opblock-tag {
        border-bottom: 1px solid var(--border);
        font-size: 1.08rem;
        letter-spacing: 0;
      }

      .swagger-ui .opblock {
        border-color: var(--border);
        border-radius: 8px;
        background: var(--surface);
        box-shadow: none;
      }

      .swagger-ui .opblock .opblock-summary {
        border-color: var(--border);
      }

      .swagger-ui .opblock .opblock-summary-method {
        min-width: 72px;
        border-radius: 6px;
        text-shadow: none;
      }

      .swagger-ui .opblock.opblock-get {
        border-color: rgba(88, 166, 255, 0.45);
        background: rgba(88, 166, 255, 0.08);
      }

      .swagger-ui .opblock.opblock-post {
        border-color: rgba(86, 211, 100, 0.45);
        background: rgba(86, 211, 100, 0.08);
      }

      .swagger-ui .opblock.opblock-patch,
      .swagger-ui .opblock.opblock-put {
        border-color: rgba(210, 168, 255, 0.45);
        background: rgba(210, 168, 255, 0.08);
      }

      .swagger-ui .opblock.opblock-delete {
        border-color: rgba(255, 123, 114, 0.45);
        background: rgba(255, 123, 114, 0.08);
      }

      .swagger-ui .opblock .opblock-summary-description,
      .swagger-ui .opblock .opblock-summary-path,
      .swagger-ui .opblock .opblock-summary-path__deprecated {
        color: var(--text);
      }

      .swagger-ui .opblock-body,
      .swagger-ui .opblock-section-header,
      .swagger-ui .responses-inner,
      .swagger-ui .model-box,
      .swagger-ui section.models {
        background: var(--surface);
        border-color: var(--border);
        box-shadow: none;
      }

      .swagger-ui section.models {
        border-radius: 8px;
      }

      .swagger-ui .btn,
      .swagger-ui .btn.authorize,
      .swagger-ui .execute-wrapper .btn {
        border-color: var(--accent);
        border-radius: 8px;
        background: #143448;
        color: #ecfeff;
        box-shadow: none;
      }

      .swagger-ui .responses-inner h4,
      .swagger-ui .responses-inner h5,
      .swagger-ui .response-col_description__inner,
      .swagger-ui .response-col_description__inner p,
      .swagger-ui .response-col_description__inner span,
      .swagger-ui .response-control-media-type__title,
      .swagger-ui .content-type-wrapper,
      .swagger-ui .copy-to-clipboard,
      .swagger-ui .download-contents,
      .swagger-ui .tab li button {
        color: var(--text);
      }

      .swagger-ui .tab li button {
        border-radius: 6px;
        background: var(--surface-raised);
        box-shadow: none;
      }

      .swagger-ui .tab li button.tablinks.active {
        background: #e4ebf5;
        color: #1f9d55;
      }

      .swagger-ui .responses-table,
      .swagger-ui .responses-wrapper,
      .swagger-ui .responses-inner {
        background: var(--surface);
      }

      .swagger-ui .highlight-code,
      .swagger-ui .highlight-code > .microlight,
      .swagger-ui .microlight,
      .swagger-ui .body-param__example,
      .swagger-ui .example {
        border-radius: 8px;
        background: var(--code-bg) !important;
        color: var(--text) !important;
      }

      .swagger-ui .highlight-code {
        border: 1px solid var(--border);
        overflow: hidden;
      }

      .swagger-ui .highlight-code > .microlight,
      .swagger-ui .microlight {
        padding: 18px 20px;
        line-height: 1.65;
      }

      .swagger-ui .microlight *,
      .swagger-ui .highlight-code *,
      .swagger-ui pre *,
      .swagger-ui code * {
        background: transparent !important;
        background-color: transparent !important;
        border: 0 !important;
        box-shadow: none !important;
        outline: 0 !important;
        text-shadow: none !important;
        -webkit-text-stroke: 0 transparent !important;
      }

      .swagger-ui code,
      .swagger-ui pre,
      .swagger-ui .highlight-code code,
      .swagger-ui .highlight-code pre {
        background: var(--code-bg);
        color: var(--text);
        font-weight: 500;
      }

      .swagger-ui .microlight .token.string,
      .swagger-ui .microlight .token.number,
      .swagger-ui .microlight .token.boolean {
        color: #85e89d !important;
      }
    </style>
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
    <script>
      window.ui = SwaggerUIBundle({
        url: "__OPENAPI_URL__",
        dom_id: "#swagger-ui",
        deepLinking: true,
        displayRequestDuration: true,
        docExpansion: "none",
        defaultModelsExpandDepth: -1,
        filter: true,
        persistAuthorization: true,
        tryItOutEnabled: true,
        tagsSorter: "alpha",
        operationsSorter: "method",
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIStandalonePreset
        ],
        layout: "StandaloneLayout"
      });
    </script>
  </body>
</html>
"""


_REDOC_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>__TITLE__</title>
    <style>
      :root {
        color-scheme: dark;
      }

      body {
        margin: 0;
        background: #0b1019;
      }

      redoc,
      #redoc-container {
        min-height: 100vh;
        display: block;
      }

      .redoc-loading {
        padding: 32px;
        color: #e7edf6;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }

      .redoc-loading p {
        color: #9aa8bd;
      }

      .api-content div[role="tabpanel"],
      .api-content pre,
      .api-content pre code {
        background-color: #182232 !important;
      }

      .api-content pre {
        border: 1px solid #2f3f59 !important;
        border-radius: 8px !important;
        box-shadow: none !important;
      }

      .api-content label,
      .api-content select {
        max-width: 100%;
      }

      .api-content label + div,
      .api-content [data-section-id] div[style*="background"] {
        box-sizing: border-box;
      }
    </style>
  </head>
  <body>
    <div id="redoc-container">
      <div class="redoc-loading">
        <strong>Loading AtlasCore ReDoc...</strong>
        <p>If this message stays visible, the ReDoc CDN script did not load.</p>
      </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/redoc@2.1.5/bundles/redoc.standalone.js"></script>
    <script>
      if (window.Redoc) {
        Redoc.init(
          "__OPENAPI_URL__",
          {
            expandResponses: "200,201",
            hideDownloadButton: false,
            nativeScrollbars: true,
            pathInMiddlePanel: true,
            theme: {
              colors: {
                primary: { main: "#58c4dc" },
                text: { primary: "#e7edf6", secondary: "#9aa8bd" },
                border: { dark: "#2a3850", light: "#2a3850" },
                responses: {
                  success: { color: "#56d364" },
                  error: { color: "#ff7b72" },
                  redirect: { color: "#d2a8ff" },
                  info: { color: "#58a6ff" }
                },
                http: {
                  get: "#58a6ff",
                  post: "#56d364",
                  put: "#f2cc60",
                  patch: "#d2a8ff",
                  delete: "#ff7b72"
                }
              },
              codeBlock: {
                backgroundColor: "#182232",
                tokens: {
                  property: "#d7e2f2",
                  string: "#9be9a8",
                  number: "#f2cc60",
                  boolean: "#f2cc60",
                  punctuation: "#a9b6c8"
                }
              },
              rightPanel: {
                backgroundColor: "#121b2b",
                textColor: "#e6edf7",
                width: "38%"
              },
              sidebar: { backgroundColor: "#121b2b", textColor: "#e6edf7" },
              typography: {
                fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
                code: {
                  fontFamily: "SFMono-Regular, Consolas, Liberation Mono, monospace",
                  backgroundColor: "#1b2840",
                  color: "#e6edf7"
                }
              }
            }
          },
          document.getElementById("redoc-container")
        );
      }
    </script>
  </body>
</html>
"""
