import abc

from tfidf.tfidfprogram import TFIDFProgram, OkapiBM25Program


def main():
    ps = TFIDFProgram()
    ps.run()
    print('=' * 100)
    ps = OkapiBM25Program()
    ps.run()
    
    


if __name__ == '__main__':
    main()
