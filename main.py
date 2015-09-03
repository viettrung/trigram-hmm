from hmm import BrownCorpus
import time

s = time.time()

hmm = BrownCorpus()

# sentence = "Hello world. My name is luu."

# y = hmm.get_tag_sequence(sentence.split())
hmm.test_tag_sequence('test','test_result')
hmm.test_accuracy('test_result');

# print(y)

e = time.time()

print('elapsed time:', e-s)
