import logging
import os

# Função gerada por IA
def setup_logger():
    # Verificar se o diretório 'files' existe, e criar se não existir
    log_directory = 'src/files'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)  # Criar o diretório 'files' se não existir

    # Criação do logger
    logger = logging.getLogger("crossword_solver")
    if not logger.hasHandlers():  # Evita configurar múltiplos manipuladores
        logger.setLevel(logging.DEBUG)
        
        # Criar manipuladores para arquivo e console
        file_handler = logging.FileHandler(os.path.join(log_directory, 'log.txt'), mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatação do log - sem timestamps para reduzir a duplicidade
        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Adicionar manipuladores ao logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger
