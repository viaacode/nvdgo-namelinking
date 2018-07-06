from argparse import ArgumentParser
from pythonmodules.ner.gmbner import *
import logging
from pythonmodules.profiling import timeit
import pickle
from nltk import pos_tag, word_tokenize

if __name__ == '__main__':
    # from random import sample
    parser = ArgumentParser(description='Train and test NER')
    parser.add_argument('--train', action='store_true', help='Train a tagger')
    parser.add_argument('--test', help='Test the tagger with TEST known examples (default 500)', default=500)
    parser.add_argument('--test-mediahaven', action='store_true', help='Tag MediaHaven newspaper OCR-text')
    parser.add_argument('--profile', action='store_true', help='Output run times of some key operations')
    parser.add_argument(dest='pickle', help='Filename of pickle file')
    args = parser.parse_args()
    if not args.profile:
        logging.getLogger('pythonmodules.profiling').setLevel(logging.ERROR)

    class Samples:
        def __init__(self):
            self.data = None

        def init(self):
            reader = read_gmb()
            data = list(reader)
            self.data = (data[:int(len(data) * 0.1)], data[int(len(data) * 0.1):])

        def training(self):
            if self.data is None:
                self.init()
            return self.data[1]

        def test(self, amount=500):
            if self.data is None:
                # optim: no need to read all the data if we only using test
                reader = read_gmb()
                return [next(reader) for i in range(amount)]
            return self.data[0][:amount]

    samples = Samples()
    if args.train:
        with timeit('Creating NamedEntityChunker'):
            chunker = NamedEntityChunker(samples.training())
        pickle.dump(chunker, open(args.pickle, 'wb'))
    else:
        with timeit('Pickle load'):
            chunker = pickle.load(open(args.pickle, 'rb'))

    if args.test_mediahaven:
        with timeit('NER Tagging'):
            from pythonmodules.mediahaven import MediaHaven

            # from pythonmodules.config import Config
            mh = MediaHaven()
            item = mh.one('+(workflow:GMS) +(archiveStatus:on_tape)')
            print(chunker.parse(pos_tag(word_tokenize(item['description']))))

    if args.test:
        with timeit('Testing accuracy'):
            testsamples = samples.test(int(args.test))
            score = chunker.evaluate(
                [conlltags2tree([(w, t, iob) for (w, t), iob in iobs]) for iobs in testsamples]
            )
            print("Test accuracy = %.2f%% (tested using %d samples)" % (score.accuracy() * 100, len(testsamples)))