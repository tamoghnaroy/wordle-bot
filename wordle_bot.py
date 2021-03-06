import random
import pprint
import os, sys

TGREEN = '\033[32m'
TYELLOW = '\033[33m'
TBLACK = '\033[30m'
TRED = '\033[31m'
null_char = '\033[m'


class WordleBot(object):
    def __init__(self, word_list, num_chars=5, num_attempts=6, verbose=False):
        self._num_attempts = num_attempts
        self._solved = False
        self._num_chars = num_chars
        self._word_list = []
        self._position_db = {}
        self._verbose = verbose

        with open(word_list, "r") as fp:
            count = 0
            for line in fp:
                cur_word = line.rstrip("\n")
                if len(cur_word) == num_chars:
                    self._word_list.append(cur_word)
                    
                    for i, c in enumerate(cur_word):
                        cur_key = c + str(i)
                        # Update Position db
                        if cur_key not in self._position_db:
                            self._position_db[cur_key] = [count]
                        else:
                            self._position_db[cur_key].append(count)
                    count += 1
        
        self._key_prefix = [str(i) for i in range(num_chars)]
    

    def char_to_dict(self, input_string):
        ret_dict = {}
        for i, c in enumerate(input_string):
            if c not in ret_dict:
                ret_dict[c] = [i]
            else:
                ret_dict[c].append(i)
        return ret_dict
    

    def pretty_print_feedback(self, guess, feedback):
        output_str = ""
        for i, c in enumerate(guess):
            f = feedback[i]
            if f == "g":
                output_str += TGREEN + c.upper() + null_char
            elif f == "y":
                output_str += TYELLOW + c.upper() + null_char
            elif f == "b": 
                output_str += TRED + c.upper() + null_char

        return output_str



    def compare(self, target, query):
        feedback_list = [None] * self._num_chars
        matches = set()

        for i, c in enumerate(query):
            target_char = target[i]
            if c == target_char:
                feedback_list[i] = "g"
                matches.add(c)
            elif c not in target:
                feedback_list[i] = "b"

        for i, item in enumerate(feedback_list):
            if item is None:
                c = query[i]
                if c in matches:
                    feedback_list[i] = "b"
                else:
                    feedback_list[i] = "y"
                    matches.add(c)
            
        feedback = "".join(feedback_list)

        return feedback


    def get_indices(self, key):
        if key in self._position_db:
            return set(self._position_db[key])
        else:
            return set()

    def print_search_space(self):
        output_list = []
        for i in self._search_space:
            output_list.append(self._word_list[i])
        pprint.pprint(output_list)


    def prune(self, feedback, guess):
        visited = set()
        ## Guess wasn't correct. Let's remove this index
        try:
            cur_index = self._word_list.index(guess)
            self._search_space  = self._search_space - set({cur_index})
        except ValueError:
            pass

        for i, c in enumerate(feedback):
            cur_char = guess[i]
            if c == "g":
                cur_key = cur_char + str(i)
                cur_indices = self.get_indices(cur_key)
                self._search_space = self._search_space.intersection(cur_indices)
            elif c == "b" and cur_char not in visited:
                for prefix in self._key_prefix:
                    cur_key = cur_char + prefix
                    cur_indices = self.get_indices(cur_key)
                    self._search_space = self._search_space - cur_indices
            elif c == "b" and cur_char in visited:
                cur_key = cur_char + str(i) 
                cur_indices = self.get_indices(cur_key)
                self._search_space = self._search_space - cur_indices       
            elif c == "y":
                current_search_space = set()
                for prefix in self._key_prefix:
                    cur_key = cur_char + prefix
                    cur_indices = self.get_indices(cur_key)
                    if prefix == str(i):
                        self._search_space = self._search_space - cur_indices
                    else:
                        current_search_space = current_search_space.union(cur_indices)
                self._search_space = self._search_space.intersection(current_search_space)
            visited.add(guess[i])

        return self._search_space


    def run(self, target, initial_guess=None):
        target = target.lower()
        if initial_guess is None:
            initial_guess = random.choice(self._word_list)
        
        self._initial_guess = initial_guess
        self._search_space = set(range(0, len(self._word_list)))

        cur_iter = 0
        current_guess = initial_guess

        while not self._solved and cur_iter < self._num_attempts:                
            current_feedback = self.compare(target, current_guess)
            if self._verbose:
                print(f"-----------Iteration:{cur_iter + 1}-----------")
                print(f"Current Guess {current_guess} ({current_feedback})")
            cur_iter += 1
            if current_feedback == "g" * self._num_chars:
                # print("Solved!")
                break
            self._search_space = self.prune(current_feedback, current_guess)
            if self._verbose:
                print(f"Current Search Space:{len(self._search_space)}({len(self._word_list)})")
                if len(self._search_space) < 6:
                    self.print_search_space()
                print("-" * 50)
                
            current_index = random.sample(self._search_space, 1)[0]
            current_guess = self._word_list[current_index]
        
        self._total_iter = cur_iter

    
    def play(self):

        cur_iter = 0
        target = random.choice(self._word_list)
        print("Enter a 5 letter word")

        while cur_iter < self._num_attempts:
            current_guess = input(f"{cur_iter + 1}/{self._num_attempts} ")

            if len(current_guess) !=5:
                continue
            current_feedback = self.compare(target, current_guess)
            pretty_string = self.pretty_print_feedback(current_guess, current_feedback)
            print(f"{cur_iter + 1}/{self._num_attempts}: {pretty_string}")

            if current_feedback == "g" * self._num_chars:
                print("Solved!")
                break
        
            cur_iter += 1
        
        print(f"Tough Luck. The word was: {target.upper()}")








