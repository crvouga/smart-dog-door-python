def view_html_root(children: str, title: str) -> str:
    return f"""
<html>
    <head>
        <title>{title}</title>
        <link
            rel="stylesheet"
            href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"
        >
    </head>
    <body>
        <main class="container">
            {children}
        </main>
    </body>
</html>"""
