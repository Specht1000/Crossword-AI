from typing import List, Dict, Tuple, Set
from grid import *
from utils import *
from trie import Trie
from logger_config import setup_logger

logger = setup_logger()

def solve(grid: List[List[str]], words_trie: Trie, word_size_map: Dict[int, List[str]], 
          used_words: List[Tuple[str, int, int, str]] = [], 
          attempt_count: Dict[Tuple[int, int, str], int] = {}, 
          depth: int = 0, max_depth: int = 99999, 
          tried_words: Dict[Tuple[int, int, str], Set[str]] = {}, 
          removed_words: List[str] = [], retry_limit: int = 10, removal_attempts: Dict[str, int] = {}) -> bool:

    # Verifica se o grid está completamente preenchido
    if is_grid_complete(grid):
        # Verifica se todas as palavras formadas no grid são válidas
        if validate_all_words_in_grid(grid, words_trie):
            logger.info("O jogo foi concluído com sucesso!")  # Mensagem de sucesso
            print_grid(grid)  # Imprime o grid final
            # Listar todas as palavras utilizadas
            logger.info("\nPalavras utilizadas no grid:")
            for word, row, col, direction in used_words:
                logger.info(f"Palavra: {word} | Posição: ({row}, {col}) | Direção: {direction}")
            return True
        else:
            # Se palavras inválidas forem detectadas, remove as que cruzam a palavra inválida
            logger.info("Grid completo, mas com palavras inválidas. Iniciando backtracking para corrigir...")
            for word, row, col, direction in get_all_words_from_grid(grid):
                if not words_trie.search_with_pattern(word):
                    logger.info(f"Palavra inválida detectada: {word} na posição ({row}, {col}) na direção {direction}.")
                    # Remover todas as palavras que cruzam essa palavra inválida
                    remove_intersecting_words_for_invalid(grid, word, row, col, direction, used_words, words_trie)

                    # Agora tentar encontrar uma nova palavra para substituir o espaço onde estava a palavra inválida
                    logger.info(f"Tentando preencher o espaço onde estava '{word}' na posição ({row}, {col}) na direção {direction}.")
                    
                    # Obter o tamanho máximo e as letras existentes naquele espaço
                    max_length, existing_letters = find_max_word_length_and_existing_letters(grid, row, col, direction)
                    pattern: str = create_pattern_from_existing_letters(max_length, existing_letters)
                    
                    # Encontrar novas palavras que podem ser colocadas naquele espaço
                    matching_words = words_trie.search_with_pattern(pattern)
                    matching_words = [w for w in matching_words if len(w) == max_length and w not in removed_words]
                    
                    if matching_words:
                        matching_words = prioritize_words(matching_words)
                        new_word = matching_words[0]  # Escolher a nova palavra a ser colocada
                        place_word(grid, new_word, row, col, direction)
                        logger.info(f"Nova palavra '{new_word}' colocada na posição ({row}, {col}) na direção {direction}.")
                        used_words.append((new_word, row, col, direction))
                        print_grid(grid)
                    else:
                        logger.info(f"Não foi possível encontrar uma nova palavra para substituir '{word}'. Continuando backtracking...")
                    return solve(grid, words_trie, word_size_map, used_words, attempt_count, depth, max_depth, tried_words, removed_words, retry_limit)

    # Encontra todos os espaços livres disponíveis no grid, priorizando interseções
    free_spaces: List[Tuple[int, int, int, str, int, int]] = find_free_spaces(grid)

    # Itera sobre cada espaço livre encontrado
    for row, col, length, direction, fixed_letters, intersecoes in free_spaces:
        max_length, existing_letters = find_max_word_length_and_existing_letters(grid, row, col, direction)
        pattern: str = create_pattern_from_existing_letters(max_length, existing_letters)
        matching_words: List[str] = [word for word in words_trie.search_with_pattern(pattern) if len(word) == max_length and word not in removed_words]
        matching_words = prioritize_words(matching_words)

        # Controle de tentativas e colocação de palavras
        if (row, col, direction) not in tried_words:
            tried_words[(row, col, direction)] = set()

        if (row, col, direction) not in attempt_count:
            attempt_count[(row, col, direction)] = 0

        if attempt_count[(row, col, direction)] >= 10:
            logger.info(f"Tentativas esgotadas para o espaço ({row}, {col}) na direção {direction}. Tentando outro espaço.")
            continue  # Passa para o próximo espaço disponível

        for word in matching_words:
            if word in tried_words[(row, col, direction)]:
                continue

            if word not in [w[0] for w in used_words] and can_place_word(grid, word, row, col, direction):
                # Apenas uma vez log e impressão
                place_word(grid, word, row, col, direction)
                used_words.append((word, row, col, direction))
                print_grid(grid)  # Imprime o grid após colocar a palavra

                attempt_count[(row, col, direction)] = 0

                if solve(grid, words_trie, word_size_map, used_words, attempt_count, depth + 1, max_depth, tried_words, removed_words, retry_limit):
                    return True

                logger.info(f"Backtracking: removendo palavra '{word}' da posição ({row}, {col}) na direção {direction}.")
                remove_word(grid, word, row, col, direction, used_words)  # Remoção também ocorre uma vez
                used_words.pop()
                removed_words.append(word)
                attempt_count[(row, col, direction)] += 1
                tried_words[(row, col, direction)].add(word)
        
        # Se o espaço não puder ser preenchido, tenta remover palavras bloqueantes
        if not matching_words or attempt_count[(row, col, direction)] >= retry_limit:
            if is_grid_complete(grid):
                # Validação adicional para garantir que o grid está quase completo
                logger.info("O grid está quase completo, validando antes de remover palavras.")
                if validate_all_words_in_grid(grid, words_trie):
                    return True
            if remove_blocking_words(grid, row, col, direction, used_words, removed_words, removal_attempts):
                attempt_count[(row, col, direction)] = 0
                if solve(grid, words_trie, word_size_map, used_words, attempt_count, depth + 1, max_depth, tried_words, removed_words, retry_limit):
                    return True

    return False

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
                        print_grid(grid)  # Imprime o grid com a palavra colocada
                        used_words.append((word, row, col, direction))  # Adiciona a palavra à lista de usadas
                        space_filled = True  # Marca que um espaço foi preenchido
                        break  # Sai do loop para tentar preencher o próximo espaço

        # Se nenhum espaço puder ser preenchido, inicia o processo de backtracking
        if not space_filled:
            logger.info("Nenhuma palavra pode ser preenchida mais. Iniciando backtracking.")
            # Chama a função de resolução (backtracking) para tentar resolver o grid
            return solve(grid, words_trie, word_size_map, used_words=used_words)

        # Atualiza os espaços livres após a inserção de uma palavra
        free_spaces = find_free_spaces(grid)

    # Quando todos os espaços possíveis forem preenchidos, inicia o backtracking para completar o grid
    logger.info("Preenchimento máximo concluído, iniciando backtracking para completar o grid.")
    return solve(grid, words_trie, word_size_map, used_words=used_words)
