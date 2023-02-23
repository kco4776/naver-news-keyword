from soynlp.word import WordExtractor
from soynlp.noun import LRNounExtractor_v2
from soynlp.tokenizer import LTokenizer
from soykeyword.proportion import CorpusbasedKeywordExtractor


def extraction(trg, ref):
    total = trg + ref
    trg_idx = list(range(len(trg)))

    ext = WordExtractor()
    ext.train(total)
    words = ext.extract()

    noun_ext = LRNounExtractor_v2()
    noun_ext.train(total)
    nouns = noun_ext.extract()

    noun_scores = {noun: score.score for noun, score in nouns.items()}
    cohesion_score = {word: score.cohesion_forward for word, score in words.items()}
    combined_scores = {noun: score + cohesion_score.get(noun, 0)
                       for noun, score in noun_scores.items()}
    combined_scores.update(
        {subword: cohesion for subword, cohesion in cohesion_score.items()
         if not (subword in combined_scores)}
    )

    tokenizer = LTokenizer(scores=combined_scores)

    crp_ext = CorpusbasedKeywordExtractor(
        tokenize=lambda x: [tok for tok in tokenizer.tokenize(x)
                            if tok in nouns and len(tok) > 1]
    )
    crp_ext.train(total)
    keywords = crp_ext.extract_from_docs(trg_idx)
    return keywords
