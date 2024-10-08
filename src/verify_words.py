def verify_word(file_path: str, searched_word: str) -> bool:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                words = line.split()
                if searched_word in words:
                    print(f"A palavra '{searched_word}' está na lista.")
                    return True
        print(f"A palavra '{searched_word}' não está na lista.")
        return False
    except FileNotFoundError:
        print("file não encontrado.")
        return False

file_path = 'src/files/lista_palavras.txt'
searched_word = "MAI"
verify_word(file_path, searched_word)