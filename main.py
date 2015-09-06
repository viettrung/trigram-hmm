from hmm import BrownCorpus
import re
import time


def get_user_input():
    return re.sub(r"([\.,?])", r" \1 ", input("\033[95mEnter your sentence ('stop' to exit): \033[0m"))

start_time = time.time()

hmm = BrownCorpus()

end_time = time.time()
print('(time to initialize BrownCorpus: %s)' % (end_time - start_time))

user_input = get_user_input()
while user_input != 'stop':
    start_time = time.time()
    sentence = user_input.split()

    y = hmm.get_tag_sequence(sentence)

    end_time = time.time()
    
    if y == '':
        print("Please input text and retry")
    else:
        print("==> The best tag sequence is:", y)
        print('(time to tag this sentence: %s)' % (end_time - start_time))

    user_input = get_user_input()


