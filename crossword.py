# Programa desenvolvido para a disciplina de Inteligência Artificial que desenvolve um algoritmo que resolve caça-palavras.
# Bianca Zuchinali e Guilherme Specht
# Última atualização: 06/10/2024

import time
from collections import defaultdict
import sys
from typing import List, Tuple, Dict, Set

sys.setrecursionlimit(99999)  # Aumenta o limite de recursão para grids maiores

# Define uma classe TrieNode que será usada para cada nó na Trie
class TrieNode:
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = defaultdict(TrieNode)  # Dicionário de filhos que contém nós filhos
        self.is_end_of_word: bool = False  # Indica se este nó representa o final de uma palavra

# Define a classe Trie para armazenar e manipular palavras
class Trie:
    def __init__(self):
        self.root: TrieNode = TrieNode()  # Inicializa a raiz da Trie

    # Insere uma palavra na Trie
    def insert(self, word: str) -> None:
        node: TrieNode = self.root
        for char in word:
            node = node.children[char]  # Cria ou navega para o nó filho correspondente ao caractere
        node.is_end_of_word = True  # Marca o final da palavra

    # Busca palavras que combinam com um padrão, usando '?' como caractere curinga
    def search_with_pattern(self, pattern: str) -> List[str]:
        return self.search_with_pattern_recursive(self.root, pattern, 0, '')

    # Função recursiva para buscar palavras que se encaixam no padrão
    def search_with_pattern_recursive(self, node: TrieNode, pattern: str, index: int, current_word: str) -> List[str]:
        # Se alcançou o final do padrão, verifica se é uma palavra válida
        if index == len(pattern):
            if node.is_end_of_word:
                return [current_word]  # Retorna a palavra atual
            return []  # Retorna lista vazia se não for o final de uma palavra

        char = pattern[index]
        words: List[str] = []
        # Se o caractere é um curinga '?', tenta todas as opções possíveis nos nós filhos
        if char == '?':
            for child_char, child_node in node.children.items():
                words.extend(self.search_with_pattern_recursive(child_node, pattern, index + 1, current_word + child_char))
        # Se o caractere é específico, segue o caminho correspondente na Trie
        elif char in node.children:
            words.extend(self.search_with_pattern_recursive(node.children[char], pattern, index + 1, current_word + char))
        return words

# Carrega palavras de um arquivo e as insere na Trie
def load_words(file_path: str) -> Tuple[Trie, Dict[int, List[str]]]:
    trie: Trie = Trie()  # Inicializa a Trie
    with open(file_path, 'r', encoding='utf-8') as file:
        words: List[str] = sorted(file.read().splitlines())  # Lê e ordena as palavras
    for word in words:
        trie.insert(word)  # Insere cada palavra na Trie
    # Adiciona a criação do word_size_map aqui e retorna ambos
    word_size_map: Dict[int, List[str]] = preprocess_words_by_length(words)  # Mapeia palavras por tamanho
    return trie, word_size_map  # Retorna a Trie e o mapa de tamanho das palavras

# Pré-processa palavras por tamanho para otimizar busca por comprimento
def preprocess_words_by_length(words: List[str]) -> Dict[int, List[str]]:
    word_size_map: Dict[int, List[str]] = defaultdict(list)  # Mapeia o tamanho das palavras para uma lista de palavras daquele tamanho
    for word in words:
        word_size_map[len(word)].append(word)  # Agrupa palavras pelo tamanho
    return word_size_map  # Retorna o mapa

# Função para contar o número de vogais em uma palavra
def count_vowels(word: str) -> int:
    vowels: Set[str] = set('aeiouAEIOU')  # Conjunto de vogais
    return sum(1 for char in word if char in vowels)  # Conta o número de vogais na palavra

# Função para carregar o grid de um arquivo
def load_grid(file_path: str) -> List[List[str]]:
    # Lê o grid de um arquivo e retorna uma lista de listas (linhas do grid)
    with open(file_path, 'r') as file:
        return [list(line.strip()) for line in file.readlines()]

# Função para imprimir o grid
def print_grid(grid: List[List[str]]) -> None:
    # Itera sobre cada linha do grid e imprime
    for line in grid:
        print(''.join(line))
    print("\n")

# Função para verificar se o grid foi completamente preenchido
def is_grid_complete(grid: List[List[str]]) -> bool:
    # Verifica se ainda há '?' no grid (espaços não preenchidos)
    for row in grid:
        if '?' in row:
            return False
    return True  # Retorna True se não houver mais espaços a serem preenchidos

# Coloca uma palavra no grid na posição especificada
def place_word(grid: List[List[str]], word: str, row: int, col: int, direction: str) -> None:
    # Coloca a palavra horizontalmente ou verticalmente no grid
    if direction == 'H':  # Direção horizontal
        for i in range(len(word)):
            grid[row][col + i] = word[i]  # Preenche o grid com cada letra da palavra
    elif direction == 'V':  # Direção vertical
        for i in range(len(word)):
            grid[row + i][col] = word[i]  # Preenche o grid com cada letra da palavra

# Remove uma palavra do grid, mas preserva letras de palavras que cruzam
def remove_word(grid: List[List[str]], word: str, row: int, col: int, direction: str, used_words: List[Tuple[str, int, int, str]]) -> None:
    # Remove a palavra horizontalmente ou verticalmente no grid, mas mantém letras que cruzam
    length: int = len(word)
    if direction == 'H':
        for i in range(length):
            if col + i < len(grid[0]) and grid[row][col + i] == word[i]:
                # Verifica se essa letra pertence a outra palavra cruzada
                if not any(w for w, r, c, d in used_words if d == 'V' and c == col + i and r <= row < r + len(w)):
                    grid[row][col + i] = '?'  # Substitui a letra por '?'
    elif direction == 'V':
        for i in range(length):
            if row + i < len(grid) and grid[row + i][col] == word[i]:
                # Verifica se essa letra pertence a outra palavra cruzada
                if not any(w for w, r, c, d in used_words if d == 'H' and r == row + i and c <= col < c + len(w)):
                    grid[row + i][col] = '?'  # Substitui a letra por '?'

# Verifica se uma palavra pode ser colocada no grid na posição e direção especificadas
def can_place_word(grid: List[List[str]], word: str, row: int, col: int, direction: str) -> bool:
    # Verifica se a palavra cabe no grid e se pode ser colocada na posição
    if direction == 'H':  # Verificação horizontal
        if col + len(word) > len(grid[0]):  # Verifica se a palavra cabe
            return False
        for i in range(len(word)):
            if grid[row][col + i] != '?' and grid[row][col + i] != word[i]:
                return False  # Verifica se há um conflito de letras
    elif direction == 'V':  # Verificação vertical
        if row + len(word) > len(grid):  # Verifica se a palavra cabe
            return False
        for i in range(len(word)):
            if grid[row + i][col] != '?' and grid[row + i][col] != word[i]:
                return False  # Verifica se há um conflito de letras
    return True  # Se todas as verificações passam, a palavra pode ser colocada

# Função para encontrar os espaços disponíveis no grid, priorizando interseções e palavras maiores
def find_free_spaces(grid: List[List[str]]) -> List[Tuple[int, int, int, str, int, int]]:
    free_spaces: List[Tuple[int, int, int, str, int, int]] = []

    # Detectar espaços horizontais
    for row in range(len(grid)):
        col = 0
        while col < len(grid[0]):
            if grid[row][col] != '.':  # Considera todos os caracteres exceto '.'
                start_col = col
                fixed_letters: int = 0  # Contador de letras fixas já presentes
                intersecoes: int = 0  # Contador de interseções
                while col < len(grid[0]) and grid[row][col] != '.':
                    if grid[row][col] != '?':  # Conta letras já fixas
                        fixed_letters += 1
                    if row > 0 and grid[row - 1][col] != '.' and grid[row - 1][col] != '?':
                        intersecoes += 1  # Incrementa se há interseções na linha superior
                    if row < len(grid) - 1 and grid[row + 1][col] != '.' and grid[row + 1][col] != '?':
                        intersecoes += 1  # Incrementa se há interseções na linha inferior
                    col += 1
                if col - start_col > 1:  # Apenas espaços com mais de 1 célula são considerados
                    free_spaces.append((row, start_col, col - start_col, 'H', fixed_letters, intersecoes))
            else:
                col += 1

    # Detectar espaços verticais
    for col in range(len(grid[0])):
        row = 0
        while row < len(grid):
            if grid[row][col] != '.':  # Considera todos os caracteres exceto '.'
                start_row = row
                fixed_letters = 0  # Contador de letras fixas já presentes
                intersecoes = 0  # Contador de interseções
                while row < len(grid) and grid[row][col] != '.':
                    if grid[row][col] != '?':  # Conta letras já fixas
                        fixed_letters += 1
                    if col > 0 and grid[row][col - 1] != '.' and grid[row][col - 1] != '?':
                        intersecoes += 1  # Incrementa se há interseções na coluna à esquerda
                    if col < len(grid[0]) - 1 and grid[row][col + 1] != '.' and grid[row][col + 1] != '?':
                        intersecoes += 1  # Incrementa se há interseções na coluna à direita
                    row += 1
                if row - start_row > 1:  # Apenas espaços com mais de 1 célula são considerados
                    free_spaces.append((start_row, col, row - start_row, 'V', fixed_letters, intersecoes))
            else:
                row += 1

    # Prioriza os espaços por interseções, depois comprimento e finalmente por letras fixas
    free_spaces.sort(key=lambda x: (-x[5], -x[2], -x[4]))  # Prioriza interseções, depois comprimento e letras fixas
    return free_spaces  # Retorna a lista de espaços livres

# Encontra o comprimento máximo possível e as letras existentes para uma palavra em uma posição
def find_max_word_length_and_existing_letters(grid: List[List[str]], row: int, col: int, direction: str) -> Tuple[int, Dict[int, str]]:
    max_length: int = 0
    existing_letters: Dict[int, str] = {}

    if direction == 'H':  # Verifica horizontalmente
        while col + max_length < len(grid[0]) and grid[row][col + max_length] != '.':
            if grid[row][col + max_length] != '?':  # Coleta as letras já presentes
                existing_letters[max_length] = grid[row][col + max_length]
            max_length += 1

    elif direction == 'V':  # Verifica verticalmente
        while row + max_length < len(grid) and grid[row + max_length][col] != '.':
            if grid[row + max_length][col] != '?':  # Coleta as letras já presentes
                existing_letters[max_length] = grid[row + max_length][col]
            max_length += 1

    return max_length, existing_letters  # Retorna o comprimento máximo e as letras existentes

# Cria um padrão de caracteres para busca com base nas letras existentes
def create_pattern_from_existing_letters(max_length: int, existing_letters: Dict[int, str]) -> str:
    pattern: List[str] = ['?'] * max_length  # Inicia o padrão com '?'
    for position, letter in existing_letters.items():
        pattern[position] = letter  # Substitui pelos caracteres já conhecidos
    return ''.join(pattern)  # Retorna o padrão como string

# Função para definir a prioridade de inserção/remocao com base em caracteres especiais, números e letras
def priority_removal_criteria(word: str) -> int:
    score: int = 0
    special_chars: Set[str] = set('&#$+!@*()-_/')  # Conjunto de caracteres especiais
    numbers: Set[str] = set('0123456789')  # Conjunto de números

    # Penaliza pontuação para caracteres especiais e números
    for char in word:
        if char in special_chars:
            score -= 30  # Cada caractere especial reduz 30 pontos
        elif char in numbers:
            score -= 20  # Cada número reduz 20 pontos
        else:
            score += 1   # Letras comuns adicionam 1 ponto

    return score  # Retorna a pontuação

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

# Função que remove palavras menos prioritárias que bloqueiam o progresso
def remove_blocking_words(grid: List[List[str]], row: int, col: int, direction: str, used_words: List[Tuple[str, int, int, str]], removed_words: List[str]) -> bool:
    intersecting_words: List[Tuple[str, int, int, str]] = find_intersecting_words(grid, row, col, direction, used_words)

    if intersecting_words:  # Se encontrar palavras que interceptam
        print(f"Verificando palavras que interceptam o espaço ({row}, {col}) na direção {direction}.")

        # Ordena as palavras pela prioridade de remoção, mas agora as menos prioritárias (menor pontuação) são removidas
        intersecting_words.sort(key=lambda x: (priority_removal_criteria(x[0]), len(x[0]), -find_intersections(x[0], x[1], x[2], x[3], used_words)))

        # Remove a primeira palavra com menor prioridade de permanência
        word_to_remove = intersecting_words[0]
        print(f"Removendo palavra menos prioritária '{word_to_remove[0]}' que está na posição ({word_to_remove[1]}, {word_to_remove[2]}) na direção {word_to_remove[3]}.")

        # Remove a palavra do grid
        remove_word(grid, word_to_remove[0], word_to_remove[1], word_to_remove[2], word_to_remove[3], used_words)
        used_words.remove(word_to_remove)  # Remove da lista de palavras usadas
        removed_words.append(word_to_remove[0])  # Adiciona à lista de removidas
        print_grid(grid)  # Imprime o grid após a remoção
        return True
    else:
        return False  # Se não houver palavras a remover, retorna False

# Função principal de resolução com backtracking, priorizando interseções
def solve(grid: List[List[str]], words_trie: Trie, word_size_map: Dict[int, List[str]], used_words: List[Tuple[str, int, int, str]] = [], attempt_count: Dict[Tuple[int, int, str], int] = {}, depth: int = 0, max_depth: int = 99999, tried_words: Dict[Tuple[int, int, str], Set[str]] = {}, removed_words: List[str] = [], retry_limit: int = 100) -> bool:
    # Verifica se atingiu a profundidade máxima de recursão
    if depth > max_depth:
        print("Profundidade máxima de recursão atingida, fazendo backtracking...")
        return False

    # Verifica se o grid está completamente preenchido
    if is_grid_complete(grid):
        print("O jogo foi concluído com sucesso!")  # Mensagem de sucesso
        print_grid(grid)  # Imprime o grid final
        return True

    # Encontra todos os espaços livres disponíveis no grid, priorizando interseções
    free_spaces: List[Tuple[int, int, int, str, int, int]] = find_free_spaces(grid)

    # Itera sobre cada espaço livre encontrado
    for row, col, length, direction, fixed_letters, intersecoes in free_spaces:
        # Para o espaço atual, determina o comprimento máximo possível e as letras existentes
        max_length, existing_letters = find_max_word_length_and_existing_letters(grid, row, col, direction)
        # Cria um padrão com base nas letras já existentes no grid ('?' para espaços vazios)
        pattern: str = create_pattern_from_existing_letters(max_length, existing_letters)

        # Busca todas as palavras que correspondem ao padrão e têm o comprimento correto
        matching_words: List[str] = [word for word in words_trie.search_with_pattern(pattern) if len(word) == max_length and word not in removed_words]

        # Inicializa a lista de palavras já tentadas para este espaço, se necessário
        if (row, col, direction) not in tried_words:
            tried_words[(row, col, direction)] = set()

        # Inicializa o contador de tentativas para o espaço atual
        if (row, col, direction) not in attempt_count:
            attempt_count[(row, col, direction)] = 0

        # Itera sobre cada palavra que corresponde ao padrão
        for word in matching_words:
            # Verifica se a palavra já foi tentada nessa posição
            if word in tried_words[(row, col, direction)]:
                continue  # Se a palavra já foi tentada, pula para a próxima

            # Verifica se a palavra já não foi usada anteriormente
            if word not in [w[0] for w in used_words]:
                # Verifica se a palavra pode ser colocada no grid no espaço atual
                if can_place_word(grid, word, row, col, direction):
                    # Coloca a palavra no grid
                    place_word(grid, word, row, col, direction)
                    print(f"Colocando palavra '{word}' na posição ({row}, {col}) na direção {direction}.")
                    print_grid(grid)  # Imprime o grid após colocar a palavra
                    used_words.append((word, row, col, direction))  # Adiciona a palavra à lista de usadas
                    attempt_count[(row, col, direction)] = 0  # Reseta o contador de tentativas

                    # Faz a chamada recursiva para tentar preencher o restante do grid
                    if solve(grid, words_trie, word_size_map, used_words, attempt_count, depth + 1, max_depth, tried_words, removed_words, retry_limit):
                        return True  # Se a solução for encontrada, retorna True

                    # Se a inserção não funcionar, remove a palavra (backtracking)
                    print(f"Backtracking: removendo palavra '{word}' da posição ({row}, {col}) na direção {direction}.")
                    remove_word(grid, word, row, col, direction, used_words)  # Remove a palavra
                    print_grid(grid)  # Imprime o grid após a remoção
                    used_words.pop()  # Remove a palavra da lista de usadas
                    removed_words.append(word)  # Adiciona a palavra à lista de removidas
                    attempt_count[(row, col, direction)] += 1  # Incrementa o contador de tentativas

                    # Adiciona a palavra à lista de palavras tentadas para essa posição
                    tried_words[(row, col, direction)].add(word)

        # Se não houver palavras correspondentes ou o limite de tentativas for atingido, tenta remover palavras bloqueadoras
        if not matching_words or attempt_count[(row, col, direction)] >= retry_limit:
            # Remove palavras que estão bloqueando a inserção de novas palavras
            if remove_blocking_words(grid, row, col, direction, used_words, removed_words):
                # Reseta o contador de tentativas após a remoção
                attempt_count[(row, col, direction)] = 0
                # Tenta novamente preencher o grid após remover a palavra bloqueadora
                if solve(grid, words_trie, word_size_map, used_words, attempt_count, depth + 1, max_depth, tried_words, removed_words, retry_limit):
                    return True  # Retorna True se conseguir preencher o grid após a remoção

    return False  # Se não conseguir preencher nenhum espaço, retorna False (backtracking)

# Função para preencher o grid ao máximo antes do backtracking, priorizando palavras com mais interseções e maior comprimento
def fill_grid_max(grid: List[List[str]], words_trie: Trie, word_size_map: Dict[int, List[str]], used_words: List[Tuple[str, int, int, str]] = []) -> bool:
    # Encontra todos os espaços livres no grid
    free_spaces: List[Tuple[int, int, int, str, int, int]] = find_free_spaces(grid)

    # Continua tentando preencher enquanto houver espaços livres
    while free_spaces:
        # Ordena os espaços com base na quantidade de interseções (mais interseções primeiro)
        free_spaces.sort(key=lambda x: (-x[5], -x[2]))  # Prioriza interseções e tamanho

        space_filled: bool = False  # Flag para indicar se algum espaço foi preenchido

        # Itera sobre cada espaço livre encontrado
        for row, col, length, direction, fixed_letters, intersecoes in free_spaces:  
            # Para o espaço atual, calcula o comprimento máximo possível e as letras já presentes
            max_length, existing_letters = find_max_word_length_and_existing_letters(grid, row, col, direction)
            # Cria um padrão com base nas letras já presentes no grid
            pattern: str = create_pattern_from_existing_letters(max_length, existing_letters)
            # Encontra palavras que se encaixam no padrão e têm o comprimento correto
            matching_words: List[str] = [
                word for word in words_trie.search_with_pattern(pattern)
                if len(word) == max_length and word not in [w[0] for w in used_words]
            ]

            # Ordena as palavras correspondentes por prioridade (mais vogais primeiro)
            matching_words.sort(key=lambda word: (count_vowels(word), priority_removal_criteria(word)), reverse=True)

            # Tenta inserir as palavras correspondentes no grid
            if matching_words:
                for word in matching_words:
                    # Verifica se a palavra pode ser colocada na posição e direção especificadas
                    if can_place_word(grid, word, row, col, direction):
                        # Coloca a palavra no grid
                        place_word(grid, word, row, col, direction)
                        print(f"Preenchendo palavra '{word}' na posição ({row}, {col}) na direção {direction}.")
                        print_grid(grid)  # Imprime o grid com a palavra colocada
                        used_words.append((word, row, col, direction))  # Adiciona a palavra à lista de usadas
                        space_filled = True  # Marca que um espaço foi preenchido
                        break  # Sai do loop para tentar preencher o próximo espaço

        # Se nenhum espaço puder ser preenchido, inicia o processo de backtracking
        if not space_filled:
            print("Nenhuma palavra pode ser preenchida mais. Iniciando backtracking.")
            # Chama a função de resolução (backtracking) para tentar resolver o grid
            return solve(grid, words_trie, word_size_map, used_words=used_words)

        # Atualiza os espaços livres após a inserção de uma palavra
        free_spaces = find_free_spaces(grid)

    # Quando todos os espaços possíveis forem preenchidos, inicia o backtracking para completar o grid
    print("Preenchimento máximo concluído, iniciando backtracking para completar o grid.")
    return solve(grid, words_trie, word_size_map, used_words=used_words)

# Função principal para carregar o grid e as palavras e resolver o puzzle
def main() -> None:
    start_time = time.time()

    print('Construindo a árvore Trie!')
    words_trie, word_size_map = load_words('lista_palavras.txt')  # Carrega palavras na Trie
    grid = load_grid('grids/grid-6.txt')  # Carrega o grid

    print("Preenchendo o grid ao máximo antes do backtracking...")

    if fill_grid_max(grid, words_trie, word_size_map):  # Tenta preencher o grid ao máximo
        with open('resultado.txt', 'w') as file:  # Se bem sucedido, salva o resultado
            for line in grid:
                file.write(''.join(line) + '\n')
        print(f"Grid preenchido com sucesso em {time.time() - start_time:.2f} segundos")
    else:
        print("Não foi possível preencher o grid ao máximo.")

if __name__ == "__main__":
    main()  # Executa o programa principal
