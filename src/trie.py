from collections import defaultdict
from typing import List, Tuple, Dict

class TrieNode:
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = defaultdict(TrieNode)
        self.is_end_of_word: bool = False

class Trie:
    def __init__(self):
        self.root: TrieNode = TrieNode()

    def insert(self, word: str) -> None:
        node: TrieNode = self.root
        for char in word:
            node = node.children[char]
        node.is_end_of_word = True

    def search_with_pattern(self, pattern: str) -> List[str]:
        return self.search_with_pattern_recursive(self.root, pattern, 0, '')

    def search_with_pattern_recursive(self, node: TrieNode, pattern: str, index: int, current_word: str) -> List[str]:
        if index == len(pattern):
            if node.is_end_of_word:
                return [current_word]
            return []
        char = pattern[index]
        words: List[str] = []
        if char == '?':
            for child_char, child_node in node.children.items():
                words.extend(self.search_with_pattern_recursive(child_node, pattern, index + 1, current_word + child_char))
        elif char in node.children:
            words.extend(self.search_with_pattern_recursive(node.children[char], pattern, index + 1, current_word + char))
        return words

def load_words(file_path: str) -> Tuple[Trie, Dict[int, List[str]]]:
    trie = Trie()
    with open(file_path, 'r', encoding='utf-8') as file:
        words = sorted(file.read().splitlines())
    for word in words:
        trie.insert(word)
    word_size_map = preprocess_words_by_length(words)
    return trie, word_size_map

def preprocess_words_by_length(words: List[str]) -> Dict[int, List[str]]:
    word_size_map: Dict[int, List[str]] = defaultdict(list)
    for word in words:
        word_size_map[len(word)].append(word)
    return word_size_map