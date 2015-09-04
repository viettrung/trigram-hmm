import os
import re
import time

BROWN_CORPUS_DIR = 'brown'
DICTIONARY_DIR = 'dictionary'
TEST_DIR = 'test'

WORD = 'word'
WORD_TAG = 'word_tag'
UNIGRAM = 'unigram'
BIGRAM = 'bigram'
TRIGRAM = 'trigram'

FILE_TEST_TAG_ORIGIN = 'test_tag_origin'
FILE_TEST = 'test'


class BrownCorpus:
    word_dict = {}
    word_tag_dict = {}
    unigram_tag_dict = {}
    bigram_tag_dict = {}
    trigram_tag_dict = {}
    distinct_tags = []

    test = ''
    test_tag = ''

    def __init__(self):

        if os.path.isdir(DICTIONARY_DIR):
            self.word_dict = get_trained_data(WORD)
            self.word_tag_dict = get_trained_data(WORD_TAG)
            self.unigram_tag_dict = get_trained_data(UNIGRAM)
            self.bigram_tag_dict = get_trained_data(BIGRAM)
            self.trigram_tag_dict = get_trained_data(TRIGRAM)
        else:
            list_of_filename = os.listdir(BROWN_CORPUS_DIR)
            count_file = 0
            for filename in list_of_filename:
                if re.match('c[a-r]\d{2}', filename) is not None:
                    count_file += 1
                    with open(BROWN_CORPUS_DIR + "/" + filename) as corpus_file:
                        lines = corpus_file.readlines()
                        for line in lines:
                            if line.strip():
                                line += " STOP/STOP"
                                penult_tag = ''
                                last_tag = ''
                                for word_tag in line.split():
                                    word, tag = word_tag.rsplit('/', 1)

                                    if count_file <= 490:

                                        if word in self.word_dict:
                                            self.word_dict[word] += 1
                                        else:
                                            self.word_dict[word] = 1

                                        if (word, tag) in self.word_tag_dict:
                                            self.word_tag_dict[word, tag] += 1
                                        else:
                                            self.word_tag_dict[word, tag] = 1

                                        if tag in self.unigram_tag_dict:
                                            self.unigram_tag_dict[tag] += 1
                                        else:
                                            self.unigram_tag_dict[tag] = 1

                                        if (last_tag, tag) in self.bigram_tag_dict:
                                            self.bigram_tag_dict[last_tag, tag] += 1
                                        else:
                                            self.bigram_tag_dict[last_tag, tag] = 1

                                        if (penult_tag, last_tag, tag) in self.trigram_tag_dict:
                                            self.trigram_tag_dict[penult_tag, last_tag, tag] += 1
                                        else:
                                            self.trigram_tag_dict[penult_tag, last_tag, tag] = 1

                                        penult_tag = last_tag
                                        last_tag = tag

                                    elif len(line.split()) > 2 and len(line.split()) <= 11:
                                        self.test += word + '\n'
                                        if word != 'STOP':
                                            self.test_tag += word + '\t' + tag + '\n'

                                    else:
                                        break

                        corpus_file.close()

            os.makedirs(DICTIONARY_DIR)
            save_trained_data(self.word_dict, WORD)
            save_trained_data(self.word_tag_dict, WORD_TAG)
            save_trained_data(self.unigram_tag_dict, UNIGRAM)
            save_trained_data(self.bigram_tag_dict, BIGRAM)
            save_trained_data(self.trigram_tag_dict, TRIGRAM)

            os.makedirs(TEST_DIR)
            save_test_data(self.test, FILE_TEST)
            save_test_data(self.test_tag, FILE_TEST_TAG_ORIGIN)

        self.process_low_frequency_word()
        self.distinct_tags = set(self.unigram_tag_dict.keys())

    def process_low_frequency_word(self):
        new = {}
        # change words with freq <5 into unknown words "<unkown>"
        for (word, tag) in self.word_tag_dict:
            new[word, tag] = self.word_tag_dict[word, tag]
            if self.word_tag_dict[word, tag] < 5:
                if ('<unkown>', tag) not in new:
                    new['<unkown>', tag] = 0
                new['<unkown>', tag] += self.word_tag_dict[word, tag]
        self.word_tag_dict = new

    def get_e(self, word, tag):
        if (word, tag) in self.word_tag_dict:
            return float(self.word_tag_dict[word, tag]) / self.unigram_tag_dict[tag]
        else:
            return 0.0

    def get_q(self, penult_tag, last_tag, current_tag):
        if (penult_tag, last_tag, current_tag) in self.trigram_tag_dict:
            return float(self.trigram_tag_dict[penult_tag, last_tag, current_tag]) / self.bigram_tag_dict[last_tag, current_tag]
        else:
            return 0.0

    def get_word(self, sentence, k):
        if k < 0:
            return ''
        else:
            return sentence[k]

    def get_tag_sequence(self, sentence):
        print('start tagging...')
        pi = {}
        pi[0, '', ''] = 1
        bp = {}
        n = len(sentence)
        y = {}
        for k in range(1, n + 1):
            word = self.get_word(sentence, k - 1)
            if word not in self.word_dict:
                word = '<unkown>'
            for u in self.get_tags(k - 1):
                for v in self.get_tags(k):
                    pi[k, u, v], bp[k, u, v] = max([(pi[k - 1, w, u] * self.get_q(w, u, v) * self.get_e(word, v), w) for w in self.get_tags(k - 2)])

        prob, y[n - 1], y[n] = max([(pi[n, u, v] * self.get_q(u, v, 'STOP'), u, v) for u in self.distinct_tags for v in self.distinct_tags])

        for k in range(n - 2, 0, -1):
            y[k] = bp[k + 2, y[k + 1], y[k + 2]]

        return y

    def get_tags(self, k):
        if k in [0, -1]:
            return set([''])
        else:
            return self.distinct_tags

    def test_accuracy(self, test_result):
        correct = 0
        n = 0
        fkey = open(TEST_DIR + '/' + FILE_TEST_TAG_ORIGIN, 'r')
        for line in open(TEST_DIR + '/' + test_result, 'r'):
            n += 1
            if line == fkey.readline():
                correct += 1
        fkey.close()
        print('tag accuracy: ', float(correct) / n)

    def test_tag_sequence(self, testFileName, outFileName):
        start_time = time.time()

        sentence = []
        fout = open(TEST_DIR + '/' + outFileName, 'w')

        for line in open(TEST_DIR + '/' + testFileName, 'r'):
            line = line.strip()
            if line == 'STOP':
                if sentence:
                    # sentence.append(line)
                    print(sentence)
                    path = self.get_tag_sequence(sentence)
                    print(path)
                    for i in range(len(sentence)):
                        fout.write(sentence[i] + '\t' + path[i + 1] + '\n')
                    sentence = []
            else:
                sentence.append(line)

        finish_time = time.time()
        fout.close()
        print('time to execute test_tag_sequence method:', finish_time - start_time)


def save_trained_data(data, filename):
    file_path = DICTIONARY_DIR + '/' + filename
    file = open(file_path, 'w')
    file.write(str(data))
    file.close()


def save_test_data(data, filename):
    file_path = TEST_DIR + '/' + filename
    file = open(file_path, 'w')
    file.write(str(data))
    file.close()


def get_trained_data(filename):
    file_path = DICTIONARY_DIR + '/' + filename
    file = open(file_path, 'r')
    file_content = file.read()
    file.close()
    return eval(file_content)
