from re import split
import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""


"""
NOTES:
- "JP" non-terminals are joining phrases e.g. "in the", "at his", "the", "of" etc
- "JP" non-terminals should only be used at the sentence level or in between symbols to avoid accepting multiple "Det"'s in a row
  e.g. "Holmes sat in the the armchair." ("the" repeated). Generally "NP"s can optionally have a "JP" prefix


EXAMPLES:

Text: She never said a word until we were at the door here.
Symbols: N Adv V Det N Conj N V P Det N Adv
Sentence structure: (NP VP NP) Conj (NP VP Det NP)
    = S Conj S

Text: holmes sat in the red armchair and he chuckled
Symbols: N V P Det Adj N Conj N V
Sentence structure: (NP VP Det NP) Conj (NP VP)
    = S Conj S

Text: holmes chuckled to himself
Symbols: N V P N
Sentence structure: NP VP JP NP

Text: holmes sat down and lit his pipe
Symbols: N V Adv Conj V Det N
Sentence structure: (NP VP) Conj VP NP
    = S Conj VP NP

Text: i had a country walk on thursday and came home in a dreadful mess
Symbols: N V Det Adj N P N Conj V N P Det Adj N
Sentence structure: (NP VP Det NP) Conj VP JP NP
    = S Conj VP JP NP
"""
NONTERMINALS = """
S -> NP VP | NP JP NP | NP VP JP NP
S -> JP NP VP | JP NP VP JP NP | NP VP JP NP
S -> S Conj VP NP | S Conj S | JP S | S Conj VP JP NP
NP -> N | NP Adv | NP JP NP | Adj NP
VP -> V | Adv VP | VP Adv | VP NP
JP -> P | Det | P Det
"""


# CFG = Context Free Grammar
grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def get_token_symbols(token: str):
    return [p.lhs().symbol() for p in grammar.productions(None, token)]


# This is for printing details about sentences to aid in coming up with a rule to cover the structure
def print_sentence_debug(tokens: list[str]):
    print("Chart:", parser.chart_parse(tokens).pretty_format())
    print("\nText:", *tokens)
    all_symbols = []
    for token in tokens:
        token_symbols = get_token_symbols(token)
        all_symbols += token_symbols
        print(
            *token_symbols,
            " - ",
            token,
        )

    print("\nSymbols:", *all_symbols)


def main():
    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return

    if not trees:
        print("Could not parse sentence.")
        # print_sentence_debug(s)  # NOTE: Un-comment this to see more details of un-parseable sentences
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def contains_some_alpha_chars(word: str):
    return any(c.isalpha() for c in word.strip())


def preprocess(sentence: str):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    return [
        word
        for word in nltk.word_tokenize(sentence.lower())
        if contains_some_alpha_chars(word)
    ]


def is_np_tree(tree: nltk.Tree) -> bool:
    return tree.label() == "NP"


def is_np_chunk(tree: nltk.Tree) -> bool:
    """
    An "NP chunk" (Noun Phrase chunk) is an NP Tree tree that does not itself contain any other
    NP Tree as subtrees.
    """
    if not is_np_tree(tree):
        return False

    for subtree in tree.subtrees():
        if tree == subtree:
            continue  # NOTE: subtrees includes the root tree, so we ignore it

        if is_np_tree(subtree):
            return False  # NP tree contains NP subtrees

    return True  # NP tree does not contain NP subtrees


def np_chunk(tree: nltk.Tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    np_chunks = [
        np_subtree
        for np_subtree in tree.subtrees(is_np_tree)
        if is_np_chunk(np_subtree)
    ]

    return np_chunks


if __name__ == "__main__":
    main()
