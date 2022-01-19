from wordle_bot import WordleBot

def main():
    wordle_bot = WordleBot(word_list="wordlists/wordlist_5char.txt")
    wordle_bot.play()

if __name__  == "__main__":
    main()