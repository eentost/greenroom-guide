"""Build the retired Greenroom project URL redirects without third-party dependencies."""
import argparse
from html import escape
from pathlib import Path

ROOT = 'https://eentost.github.io/'
PUBLISHED_PAGES = (
    'index.html',
    'about.html',
    'contact.html',
    'editorial-policy.html',
    'privacy.html',
    'sources.html',
    'terms.html',
    'guides/balcony-herbs.html',
    'guides/basil.html',
    'guides/light-guide.html',
    'guides/pests.html',
    'guides/plant-log.html',
    'guides/pot-drainage.html',
    'guides/potting-mix.html',
    'guides/repotting.html',
    'guides/small-space.html',
    'guides/start-here.html',
    'guides/watering.html',
    'guides/winter-care.html',
    'guides/yellow-leaves.html',
)


def build(site):
    site.mkdir(parents=True)
    for relative in PUBLISHED_PAGES:
        target = escape(ROOT if relative == 'index.html' else ROOT + relative, quote=True)
        output = site / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>초록한칸 페이지가 이동했습니다</title>
  <meta http-equiv="refresh" content="0; url={target}">
  <link rel="canonical" href="{target}">
</head>
<body>
  <main>
    <h1>초록한칸 페이지가 이동했습니다</h1>
    <p>자동으로 이동하지 않으면 <a href="{target}">이전과 같은 글의 새 주소로 이동</a>하세요.</p>
  </main>
</body>
</html>
""", encoding='utf-8')
    (site / 'robots.txt').write_text('User-agent: *\nAllow: /\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('site', type=Path, help='new directory for the redirect artifact')
    build(parser.parse_args().site)
