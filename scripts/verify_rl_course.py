"""Check the course manuscript, runnable-code synchronization, and static links."""
from pathlib import Path
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import ast
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/courses/rl'


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids, self.links, self.lessons = [], [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if tag in ('a', 'link', 'script', 'img'):
            url = a.get('href' if tag in ('a', 'link') else 'src')
            if url:
                self.links.append(url)
        if tag == 'section' and a.get('class') == 'rl-lesson':
            self.lessons.append(a.get('data-lesson'))


def verify():
    counts = {'lessons': 0, 'formulas': 0, 'diagrams': 0, 'chinese_characters': 0}
    for n in range(1, 66):
        source = ASSETS / 'chapters' / f'lesson-{n:02d}.htmlfrag'
        text = source.read_text(encoding='utf-8')
        assert len(re.findall(r'<h2\b', text)) == 1, source
        assert len(re.findall(r'<h3\b', text)) == 11, source
        assert '<svg' in text and '<details' in text, source
        assert not re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', text), source
        prose = re.sub(r'<pre\b.*?</pre>', '', text, flags=re.S)
        assert prose.count(r'\[') == prose.count(r'\]'), ('display math', source)
        assert prose.count(r'\(') == prose.count(r'\)'), ('inline math', source)
        assert r'\tag{' in prose, source
        scripts = [unescape(c).strip() for c in re.findall(r'<pre[^>]*>\s*<code[^>]*>(.*?)</code>\s*</pre>', text, re.S)]
        python = (ASSETS / 'examples' / f'lesson_{n:02d}.py').read_text(encoding='utf-8').strip()
        assert python in scripts, ('download differs from displayed code', source)
        ast.parse(python)
        counts['lessons'] += 1
        counts['formulas'] += prose.count(r'\tag{')
        counts['diagrams'] += text.count('<svg')
        counts['chinese_characters'] += len(re.findall(r'[\u4e00-\u9fff]', re.sub('<[^>]+>', '', prose)))
    for script in (ASSETS / 'examples').glob('*.py'):
        ast.parse(script.read_text(encoding='utf-8'))

    files = [p for folder in ['', 'en', 'posts', 'courses', 'en/posts', 'en/courses'] for p in (ROOT / folder).glob('*.html')]
    pages = {p.resolve(): Page(p.read_text(encoding='utf-8')) for p in files}
    for path, page in pages.items():
        assert len(page.ids) == len(set(page.ids)), ('duplicate IDs', path)
        for url in page.links:
            u = urlsplit(url)
            if u.scheme or u.netloc:
                continue
            target = (ROOT / unquote(u.path.lstrip('/'))) if u.path.startswith('/') else (path.parent / unquote(u.path)).resolve() if u.path else path
            if target.is_dir():
                target /= 'index.html'
            assert target.exists(), ('broken local link', path, url)
            if u.fragment and target in pages:
                assert unquote(u.fragment) in pages[target].ids, ('broken anchor', path, url)
    course = pages[(ROOT / 'courses/robot-reinforcement-learning.html').resolve()]
    assert course.lessons == [str(n) for n in range(1, 66)], 'Nested or missing reader sections'
    with zipfile.ZipFile(ASSETS / 'rl-experiments.zip') as package:
        assert len([p for p in package.namelist() if re.search(r'lesson_\d\d\.py$', p)]) == 65
        assert 'rl-experiments/rl_policy_common.py' in package.namelist()
        assert 'rl-experiments/rl_continuous_common.py' in package.namelist()
        assert not any('authoring' in p for p in package.namelist())
    print('PASS:', counts, ';', len(pages), 'site pages, local links, code synchronization and experiment archive')


if __name__ == '__main__':
    verify()
