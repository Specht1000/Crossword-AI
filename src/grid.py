from typing import List, Tuple, Dict
from logger_config import setup_logger
from utils import priority_removal_criteria, find_intersections
from trie import Trie

logger = setup_logger()

# Função para carregar o grid de um arquivo
def load_grid(file_path: str) -> List[List[str]]:
    with open(file_path, 'r') as file:
        return [list(line.strip()) for line in file.readlines()]

# Defina uma variável global para armazenar o último grid impresso
last_printed_grid = ""
def print_grid(grid: List[List[str]]) -> None:
    global last_printed_grid
    # Constrói o grid como uma string para comparação
    current_grid = '\n'.join(''.join(line) for line in grid)
    
    # Só imprime o grid se ele for diferente do último grid impresso
    if current_grid != last_printed_grid:
        last_printed_grid = current_grid  # Atualiza o último grid impresso
        logger.info(current_grid)  # Imprime o grid no log


# Função para verificar se o grid foi completamente preenchido
def is_grid_complete(grid: List[List[str]]) -> bool:
    for row in grid:
        if '?' in row:
            return False
    return True

def validate_all_words_in_grid(grid: List[List[str]], words_trie: Trie) -> bool:
    # Captura todas as palavras horizontais e verticais do grid
    all_words = get_all_words_from_grid(grid)
    invalid_words = []  # Lista para armazenar palavras inválidas
    
    # Verifica cada palavra, se não estiver na Trie, adiciona à lista de inválidas
    for word, row, col, direction in all_words:
        if not words_trie.search_with_pattern(word):
            invalid_words.append((word, row, col, direction))  # Adiciona a palavra inválida com sua posição e direção
    
    # Se houver palavras inválidas, as imprime
    if invalid_words:
        for word, row, col, direction in invalid_words:
            logger.info(f"Palavra inválida encontrada: {word} na direção {direction} na posição ({row}, {col})")
        return False  # Retorna False se houver palavras inválidas
    
    return True  # Todas as palavras são válidas

# Função para capturar todas as palavras horizontais e verticais no grid
def get_all_words_from_grid(grid: List[List[str]]) -> List[Tuple[str, int, int, str]]:
    words_found = []

    # Captura palavras horizontais
    for row in range(len(grid)):
        col = 0
        while col < len(grid[0]):
            if grid[row][col] != '.':
                start_col = col
                while col < len(grid[0]) and grid[row][col] != '.':
                    col += 1
                word = ''.join(grid[row][start_col:col])  # Extrai a palavra horizontal
                if len(word) > 1:  # Apenas considera palavras com duas ou mais letras
                    words_found.append((word, row, start_col, 'H'))
            else:
                col += 1

    # Captura palavras verticais
    for col in range(len(grid[0])):
        row = 0
        while row < len(grid):
            if grid[row][col] != '.':
                start_row = row
                while row < len(grid) and grid[row][col] != '.':
                    row += 1
                word = ''.join(grid[i][col] for i in range(start_row, row))  # Extrai a palavra vertical
                if len(word) > 1:  # Apenas considera palavras com duas ou mais letras
                    words_found.append((word, start_row, col, 'V'))
            else:
                row += 1

    return words_found  # Retorna todas as palavras encontradas

# Função para detectar palavras que interceptam o espaço (horizontal ou vertical)
def find_intersecting_words(grid: List[List[str]], row: int, col: int, direction: str, used_words: List[Tuple[str, int, int, str]]) -> List[Tuple[str, int, int, str]]:
    intersecting_words: List[Tuple[str, int, int, str]] = []

    if direction == 'H':  # Verifica interceptação horizontal
        for i in range(len(grid[0])):
            if grid[row][i] != '.' and grid[row][i] != '?':
                for word, wr, wc, wd in used_words:
                    if wd == 'V' and wc == i and wr <= row < wr + len(word):
                        intersecting_words.append((word, wr, wc, wd))

    elif direction == 'V':  # Verifica interceptação vertical
        for i in range(len(grid)):
            if grid[i][col] != '.' and grid[i][col] != '?':
                for word, wr, wc, wd in used_words:
                    if wd == 'H' and wr == i and wc <= col < wc + len(word):
                        intersecting_words.append((word, wr, wc, wd))

    return intersecting_words  # Retorna as palavras que interceptam

def place_word(grid: List[List[str]], word: str, row: int, col: int, direction: str) -> None:
    # Verifica se a palavra pode ser colocada e faz a impressão apenas uma vez
    logger.info(f"\nColocando palavra '{word}' na posição ({row}, {col}) na direção {direction}.")
    
    if direction == 'H':  # Direção horizontal
        for i in range(len(word)):
            grid[row][col + i] = word[i]  # Preenche o grid com cada letra da palavra
    elif direction == 'V':  # Direção vertical
        for i in range(len(word)):
            grid[row + i][col] = word[i]  # Preenche o grid com cada letra da palavra

    print_grid(grid)  # Apenas uma impressão do grid após colocar a palavra

def remove_word(grid: List[List[str]], word: str, row: int, col: int, direction: str, used_words: List[Tuple[str, int, int, str]]) -> None:
    logger.info(f"\nRemovendo palavra '{word}' da posição ({row}, {col}) na direção {direction}.")
    length: int = len(word)
    if direction == 'H':
        for i in range(length):
            if col + i < len(grid[0]) and grid[row][col + i] == word[i]:
                if not any(w for w, r, c, d in used_words if d == 'V' and c == col + i and r <= row < r + len(w)):
                    grid[row][col + i] = '?'  # Substitui a letra por '?'
    elif direction == 'V':
        for i in range(length):
            if row + i < len(grid) and grid[row + i][col] == word[i]:
                if not any(w for w, r, c, d in used_words if d == 'H' and r == row + i and c <= col < c + len(w)):
                    grid[row + i][col] = '?'  # Substitui a letra por '?'
    # Imprime o grid após a palavra ser removida
    print_grid(grid)  # A impressão acontece após a remoção

# Função para remover palavras que cruzam uma palavra inválida
def remove_intersecting_words_for_invalid(grid: List[List[str]], word: str, row: int, col: int, direction: str, used_words: List[Tuple[str, int, int, str]], words_trie: Trie) -> None:
    intersecting_words = find_intersecting_words(grid, row, col, direction, used_words)
    
    # Remover todas as palavras que interceptam a palavra inválida
    for intersect_word, wr, wc, wd in intersecting_words:
        logger.info(f"Removendo palavra interceptada: {intersect_word} na posição ({wr}, {wc}) na direção {wd}.")
        remove_word_if_exists(grid, intersect_word, wr, wc, wd, used_words)

    # Após remover as palavras cruzadas, remova a palavra inválida do grid
    remove_word_if_exists(grid, word, row, col, direction, used_words)

# Remove uma palavra do grid e da lista de palavras usadas, se estiver presente
def remove_word_if_exists(grid: List[List[str]], word: str, row: int, col: int, direction: str, used_words: List[Tuple[str, int, int, str]]) -> None:
    if (word, row, col, direction) in used_words:
        remove_word(grid, word, row, col, direction, used_words)
        used_words.remove((word, row, col, direction))
    else:
        logger.info(f"Tentativa de remover palavra '{word}' falhou: não encontrada em used_words.")

# Adicionando limite de remoções para evitar loops infinitos
MAX_REMOVALS = 5  # Limite de tentativas de remoção por palavra
def remove_blocking_words(grid: List[List[str]], row: int, col: int, direction: str, used_words: List[Tuple[str, int, int, str]], removed_words: List[str], removal_attempts: Dict[str, int]) -> bool:
    intersecting_words: List[Tuple[str, int, int, str]] = find_intersecting_words(grid, row, col, direction, used_words)

    if intersecting_words:  # Se encontrar palavras que interceptam
        logger.info(f"Verificando palavras que interceptam o espaço ({row}, {col}) na direção {direction}.")

        # Ordena as palavras pela prioridade de remoção
        intersecting_words.sort(key=lambda x: (priority_removal_criteria(x[0]), len(x[0]), -find_intersections(x[0], x[1], x[2], x[3], used_words)))

        for word_to_remove in intersecting_words:
            # Se já atingiu o limite de tentativas de remoção, não remove mais essa palavra
            if removal_attempts.get(word_to_remove[0], 0) >= MAX_REMOVALS:
                continue

            logger.info(f"Removendo palavra menos prioritária '{word_to_remove[0]}' que está na posição ({word_to_remove[1]}, {word_to_remove[2]}) na direção {word_to_remove[3]}.")

            # Remove a palavra do grid
            remove_word(grid, word_to_remove[0], word_to_remove[1], word_to_remove[2], word_to_remove[3], used_words)
            used_words.remove(word_to_remove)  # Remove da lista de palavras usadas
            removed_words.append(word_to_remove[0])  # Adiciona à lista de removidas
            removal_attempts[word_to_remove[0]] = removal_attempts.get(word_to_remove[0], 0) + 1  # Incrementa a contagem de tentativas de remoção
            logger.info(f"Palavra '{word_to_remove[0]}' removida {removal_attempts[word_to_remove[0]]} vezes.")

            print_grid(grid)  # Imprime o grid após a remoção
            return True

    return False  # Se não houver palavras a remover, retorna False

# Função para verificar se uma palavra pode ser colocada no grid
def can_place_word(grid: List[List[str]], word: str, row: int, col: int, direction: str) -> bool:
    if direction == 'H':  # Direção horizontal
        if col + len(word) > len(grid[0]):  # A palavra cabe no grid horizontalmente?
            return False
        for i in range(len(word)):
            if grid[row][col + i] != '?' and grid[row][col + i] != word[i]:
                return False  # Conflito de letras
    elif direction == 'V':  # Direção vertical
        if row + len(word) > len(grid):  # A palavra cabe no grid verticalmente?
            return False
        for i in range(len(word)):
            if grid[row + i][col] != '?' and grid[row + i][col] != word[i]:
                return False  # Conflito de letras
    return True

# Função para encontrar espaços livres no grid
def find_free_spaces(grid: List[List[str]]) -> List[Tuple[int, int, int, str, int, int]]:
    free_spaces: List[Tuple[int, int, int, str, int, int]] = []

    # Detectar espaços horizontais
    for row in range(len(grid)):
        col = 0
        while col < len(grid[0]):
            if grid[row][col] != '.':  # Considera todos os caracteres exceto '.'
                start_col = col
                fixed_letters: int = 0  # Contador de letras fixas
                intersecoes: int = 0  # Contador de interseções
                while col < len(grid[0]) and grid[row][col] != '.':
                    if grid[row][col] != '?':  # Conta letras já fixas
                        fixed_letters += 1
                    if row > 0 and grid[row - 1][col] != '.' and grid[row - 1][col] != '?':
                        intersecoes += 1  # Incrementa se há interseções acima
                    if row < len(grid) - 1 and grid[row + 1][col] != '.' and grid[row + 1][col] != '?':
                        intersecoes += 1  # Incrementa se há interseções abaixo
                    col += 1
                if col - start_col > 1:
                    free_spaces.append((row, start_col, col - start_col, 'H', fixed_letters, intersecoes))
            else:
                col += 1

    # Detectar espaços verticais
    for col in range(len(grid[0])):
        row = 0
        while row < len(grid):
            if grid[row][col] != '.':
                start_row = row
                fixed_letters = 0
                intersecoes = 0
                while row < len(grid) and grid[row][col] != '.':
                    if grid[row][col] != '?':
                        fixed_letters += 1
                    if col > 0 and grid[row][col - 1] != '.' and grid[row][col - 1] != '?':
                        intersecoes += 1
                    if col < len(grid[0]) - 1 and grid[row][col + 1] != '.' and grid[row][col + 1] != '?':
                        intersecoes += 1
                    row += 1
                if row - start_row > 1:
                    free_spaces.append((start_row, col, row - start_row, 'V', fixed_letters, intersecoes))
            else:
                row += 1

    # Ordena por interseções, depois comprimento, depois letras fixas
    free_spaces.sort(key=lambda x: (-x[5], -x[2], -x[4]))
    return free_spaces

# Função para encontrar o comprimento máximo possível e as letras existentes para uma palavra
def find_max_word_length_and_existing_letters(grid: List[List[str]], row: int, col: int, direction: str) -> Tuple[int, Dict[int, str]]:
    max_length: int = 0
    existing_letters: Dict[int, str] = {}

    if direction == 'H':  # Direção horizontal
        while col + max_length < len(grid[0]) and grid[row][col + max_length] != '.':
            if grid[row][col + max_length] != '?':  # Captura letras já presentes
                existing_letters[max_length] = grid[row][col + max_length]
            max_length += 1
    elif direction == 'V':  # Direção vertical
        while row + max_length < len(grid) and grid[row + max_length][col] != '.':
            if grid[row + max_length][col] != '?':
                existing_letters[max_length] = grid[row + max_length][col]
            max_length += 1

    return max_length, existing_letters

# Função para criar um padrão de caracteres a partir das letras existentes
def create_pattern_from_existing_letters(max_length: int, existing_letters: Dict[int, str]) -> str:
    pattern: List[str] = ['?'] * max_length
    for position, letter in existing_letters.items():
        pattern[position] = letter
    return ''.join(pattern)
