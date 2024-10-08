import time
from trie import load_words
from grid import load_grid
from solver import fill_grid_max
from logger_config import setup_logger

def main() -> None:
    start_time = time.time()

    logger = setup_logger()  # Configura o logger
    logger.info('Construindo a árvore Trie!')

    words_trie, word_size_map = load_words('src/files/lista_palavras.txt')  # Carrega palavras na Trie
    grid = load_grid('grids/grid-0.txt')  # Carrega o grid

    logger.info("Preenchendo o grid ao máximo antes do backtracking...")

    if fill_grid_max(grid, words_trie, word_size_map):  # Tenta preencher o grid ao máximo
        with open('src/files/resultado.txt', 'w') as file:  # Se bem sucedido, salva o resultado
            for line in grid:
                file.write(''.join(line) + '\n')
        logger.info(f"Grid preenchido com sucesso em {time.time() - start_time:.2f} segundos")
    else:
        logger.info("Não foi possível preencher o grid ao máximo.")


if __name__ == "__main__":
    main()
