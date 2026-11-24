"""Verify the exact live URL contract against the preserved project archive."""
import argparse
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
import tarfile

ROOT = 'https://eentost.github.io/'
ARCHIVE = Path(__file__).resolve().parents[1] / '.deploy' / 'site.tar.gz'


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refresh, self.canonical, self.links, self.scripts = [], [], [], []
        self.robots = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta':
            if attrs.get('http-equiv', '').lower() == 'refresh':
                self.refresh.append(attrs.get('content'))
            if attrs.get('name', '').lower() == 'robots':
                self.robots.append(attrs.get('content', ''))
            if 'adsense' in attrs.get('name', '').lower():
                raise ValueError('unexpected AdSense markup in redirect')
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical.append(attrs.get('href'))
        if tag == 'a':
            self.links.append(attrs.get('href'))
        if tag == 'script':
            self.scripts.append(attrs)


def old_html_paths():
    with tarfile.open(ARCHIVE) as source:
        return {
            PurePosixPath(item.name).as_posix()
            for item in source.getmembers()
            if item.isfile() and item.name.endswith('.html')
            and PurePosixPath(item.name).name != '404.html'
        }


def verify(site):
    old_pages = old_html_paths()
    assert len(old_pages) == 20, f'unexpected baseline page count: {len(old_pages)}'
    actual = {path.relative_to(site).as_posix() for path in site.rglob('*') if path.is_file()}
    expected = old_pages | {'robots.txt', '404.html'}
    assert actual == expected, f'unexpected artifact paths: {sorted(actual ^ expected)}'
    for relative in sorted(old_pages):
        target = ROOT if relative == 'index.html' else ROOT + relative
        raw = (site / relative).read_text()
        page = Page()
        page.feed(raw)
        assert page.refresh == [f'0; url={target}'], f'{relative}: missing or incorrect instant refresh'
        assert page.canonical == [target], f'{relative}: missing or incorrect canonical target'
        assert page.links == [target], f'{relative}: missing or incorrect fallback link'
        assert not page.scripts, f'{relative}: script present'
        assert not any('noindex' in tag.lower() for tag in page.robots), f'{relative}: noindex hides redirect'
        assert 'pagead' not in raw and '/greenroom-guide/' not in raw, f'{relative}: obsolete URLs or ads'
    robots = (site / 'robots.txt').read_text()
    assert robots == 'User-agent: *\nAllow: /\n', 'obsolete sitemap or crawler restriction'
    not_found = Page()
    not_found.feed((site / '404.html').read_text())
    assert not_found.links == [ROOT, ROOT + 'sitemap.xml'], 'invalid 404 fallback links'
    assert not not_found.refresh and not not_found.canonical and not not_found.scripts, '404 must not redirect or run scripts'
    assert not_found.robots == ['noindex,follow'], '404 should not be indexed'
    print(f'Verified {len(old_pages)} one-to-one redirect files (21 URLs with the home alias), custom 404, and no legacy sitemap or ad code.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('site', type=Path)
    verify(parser.parse_args().site)
