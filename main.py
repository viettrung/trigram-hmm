from hmm import BrownCorpus
import time

s = time.time()

hmm = BrownCorpus()

sentence = "Ask jail deputies"

y = hmm.get_tag_sequence(sentence.split())

print(y)

e = time.time()

print('elapsed time:', e-s)
