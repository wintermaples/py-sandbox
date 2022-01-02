import bz2
from collections import deque
from pathlib import Path
from dataclasses import dataclass
from typing import List, IO
from xml.etree import ElementTree


@dataclass
class WikiPediaDumpIndex:
    id: int
    block_start: int
    block_end: int
    title: str
    
    def __str__(self) -> str:
        return ':'.join([str(self.id), str(self.block_start), str(self.block_end), self.title])


class WikiPediaDumpIndexSearcher():
    def __init__(self, index_file_path: Path, dump_file_path: Path):
        self.index_file_path = index_file_path
        self.dump_file_path = dump_file_path
    
    def search(self, page_title: str) -> List[WikiPediaDumpIndex]:
        raise NotImplementedError()


class WikiPediaDumpStream():
    def __init__(self, index_file_path: Path, dump_file_path: Path):
        self.index_file_path = index_file_path
        self.dump_file_path = dump_file_path
        self.dump_indexes: deque[WikiPediaDumpIndex] = deque()
    
    def read_indexes(self):
        with open(self.index_file_path, 'r', encoding='utf-8') as index_file:
            # block_endを指定するための変数
            indexes_in_block: List[WikiPediaDumpIndex] = []
            prev_block_start = None
            #####
            while line := index_file.readline():
                line_data = line.split(':')
                dump_index = WikiPediaDumpIndex(int(line_data[1]), int(line_data[0]), -1,
                                                line_data[2][:-1])  # titleの最後の文字に改行があるので削除している
                self.dump_indexes.append(dump_index)
                
                # block_endを指定するための処理
                # print(f'{prev_block_start}::{dump_index.block_start}')
                if prev_block_start != dump_index.block_start:
                    for index in indexes_in_block:
                        index.block_end = dump_index.block_start
                    indexes_in_block.clear()
                prev_block_start = dump_index.block_start
                indexes_in_block.append(dump_index)
            
            # 最後のindexes_in_blockのblock_endはファイルサイズにする
            for index in indexes_in_block:
                index.block_end = self.dump_file_path.stat().st_size
    
    def next(self):
        if len(self.dump_indexes) == 0:
            raise 'Dump indexes is empty.'
        
        file_block = None
        index = self.dump_indexes.popleft()
        with open(self.dump_file_path, 'rb') as dump_file:
            dump_file.seek(index.block_start)
            file_block = dump_file.read(index.block_end - index.block_start)
        
        if not file_block:
            return
        
        data = bz2.decompress(file_block)
        data_xml = data.decode(encoding='utf-8')
        
        root = ElementTree.fromstring(f"<root>{data_xml}</root>")
        page = root.find(f"page/[id='{index.id}']")
        
        if not page:
            raise f'Page(ID: {index.id}) is not found.'
        print(ElementTree.ElementTree(page).write("hoge.xml", encoding='utf-8'))
        return data_xml
    
    def skip(self, n):
        for i in range(n):
            self.dump_indexes.popleft()
