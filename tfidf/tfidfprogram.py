import math
from pathlib import Path
from typing import List, Dict

import MeCab

from switcher import ProgramSwitcher
from wikipedia.dump import WikiPediaDumpStream
from dataclasses import dataclass


@dataclass
class Term:
    text: str
    term_type: str
    
    def __eq__(self, other):
        if not isinstance(other, Term):
            return False
        return self.text == other.text and self.term_type == other.term_type
    
    def __hash__(self):
        return (self.text + self.term_type).__hash__()


def read_text_files(text_folder_path: Path) -> List[str]:
    texts = []
    for text_file_path in text_folder_path.glob('*.txt'):
        with text_file_path.open('r', encoding='utf-8') as text_file:
            texts.append(text_file.read())
    return texts


class TFIDFDocument:
    
    def __init__(self, text: str):
        self.text = text
        self._dl = self._calc_dl()
        self._tfs = self._calc_tfs()
    
    def _calc_tfs(self) -> Dict[Term, float]:
        mecab = MeCab.Tagger('-Ochasen')
        mecab_parse = mecab.parse(self.text)
        mecab_parse_split_by_term = mecab_parse.split('\n')[:-2]
        term_counts: Dict[Term, int] = {}
        for term_mecab in mecab_parse_split_by_term:
            term_mecab_data = term_mecab.split('\t')
            term = Term(term_mecab_data[0], term_mecab_data[3].split('-')[0])
            term_count = term_counts.get(term, 0)
            term_counts[term] = term_count + 1
    
        
        return {t: float(count) / float(self.dl) for t, count in term_counts.items()}
    
    def _calc_dl(self) -> int:
        mecab = MeCab.Tagger('-Ochasen')
        mecab_parse = mecab.parse(self.text)
        mecab_parse_split_by_term = mecab_parse.split('\n')[:-2]
        return len(mecab_parse_split_by_term)
    
    def tf(self, term: Term, default=None):
        return self._tfs.get(term, default)

    @property
    def dl(self):
        return self._dl

class TFIDFProgram(ProgramSwitcher):
    
    def __init__(self):
        self.documents: List[TFIDFDocument] = []
    
    def run(self):
        texts = read_text_files(Path('./files/amazon-review-texts/'))
        for text in texts:
            tfidf_doc = TFIDFDocument(text)
            self.documents.append(tfidf_doc)
        
        for doc in self.documents:
            tfidf_list: List = []
            for term in doc._tfs.keys():
                tfidf_list.append([term, self.tfidf(doc, term)])
            print(list(reversed(sorted(tfidf_list, key=lambda i: i[1])))[:5])
    
    def tfidf(self, doc: TFIDFDocument, term: Term):
        return doc.tf(term) * self.idf(term)
    
    def idf(self, term: Term):
        df_t = 0
        for doc in self.documents:
            if doc.tf(term, None) is not None:
                df_t += 1
        return math.log2(len(self.documents) / (df_t + 1))


class OkapiBM25Program(ProgramSwitcher):
    def __init__(self):
        self.documents: List[TFIDFDocument] = []
    
    def run(self):
        texts = read_text_files(Path('./files/amazon-review-texts/'))
        for text in texts:
            tfidf_doc = TFIDFDocument(text)
            self.documents.append(tfidf_doc)
        
        for doc in self.documents:
            tfidf_list: List = []
            for term in doc._tfs.keys():
                tfidf_list.append([term, self.score(doc, term)])
            print(list(reversed(sorted(tfidf_list, key=lambda i: i[1])))[:5])
    
    def score(self, doc: TFIDFDocument, term: Term):
        k_1 = 1.2
        b = 0.75
        avg_dl = self.avg_dl()
        return self.idf(term) * ((doc.tf(term) * (k_1 + 1)) / (doc.tf(term) + k_1 * (1 - b + b*(doc.dl / avg_dl))))

    def idf(self, term: Term):
        df_t = 0
        for doc in self.documents:
            if doc.tf(term, None) is not None:
                df_t += 1
        return math.log2((len(self.documents) - df_t + 0.5) / (df_t + 0.5))
    
    def avg_dl(self):
        n = len(self.documents)
        sum = 0
        for doc in self.documents:
            sum += doc.dl
        return sum / n