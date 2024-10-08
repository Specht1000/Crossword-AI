from typing import Set, List, Tuple
from logger_config import setup_logger

logger = setup_logger()

def count_vowels(word: str) -> int:
    vowels: Set[str] = set('aeiouAEIOU')
    return sum(1 for char in word if char in vowels)

def priority_removal_criteria(word: str) -> int:
    score: int = 0
    special_chars: Set[str] = set('&#$+!@*()-_/')
    numbers: Set[str] = set('0123456789')
    for char in word:
        if char in special_chars:
            score -= 30
        elif char in numbers:
            score -= 20
        else:
            score += 1
    return score

# Ordena as palavras correspondentes por prioridade (mais vogais primeiro e menos caracteres especiais)
def prioritize_words(matching_words: List[str]) -> List[str]:
    # Ordena as palavras com base em dois critérios:
    # 1. Maior número de vogais (quanto mais vogais, mais alta a prioridade)
    # 2. Menos caracteres especiais ou números (quanto menos, maior a prioridade)
    return sorted(matching_words, key=lambda word: (count_vowels(word), priority_removal_criteria(word)), reverse=True)

# Função para encontrar o número de interseções de uma palavra no grid
def find_intersections(word: str, row: int, col: int, direction: str, used_words: List[Tuple[str, int, int, str]]) -> int:
    intersections: int = 0
    length: int = len(word)
    
    if direction == 'H':  # Verifica interseções para palavras horizontais
        for i in range(length):
            if any(w for w, wr, wc, wd in used_words if wd == 'V' and wc == col + i and wr <= row < wr + len(w)):
                intersections += 1
                
    elif direction == 'V':  # Verifica interseções para palavras verticais
        for i in range(length):
            if any(w for w, wr, wc, wd in used_words if wd == 'H' and wr == row + i and wc <= col < wc + len(w)):
                intersections += 1

    return intersections  # Retorna o número de interseções