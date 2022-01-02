from pathlib import Path

import MeCab

from switcher import ProgramSwitcher
from wikipedia.dump import WikiPediaDumpStream


class TFIDF(ProgramSwitcher):
    def run(self):
        mecab = MeCab.Tagger('-Ochasen')
        print(mecab.parse("私は行く。"))
