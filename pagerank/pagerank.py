import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000

"""
dictionary mapping a page name to a set of all pages linked to by that page
"""
Corpus = dict[str, set[str]]

PageRankMap = dict[str, float]

ProbabilityMap = dict[str, float]


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")

    corpus = crawl(sys.argv[1])

    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]: .4f}")

    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]: .4f}")


def crawl(directory) -> Corpus:
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue

        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus: Corpus, page: str, damping_factor: float) -> ProbabilityMap:
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    output: ProbabilityMap = {}
    links = corpus[page]

    # if a page has no links, we can pretend it has links to
    # all pages in the corpus, including itself.
    if len(links) == 0:
        p = 1 / len(corpus)
        for possible_page in corpus:
            output[possible_page] = p

        return output

    # With probability 1 - damping_factor, the random surfer should
    # randomly choose one of all pages in the corpus with equal probability.
    p = (1 - damping_factor) / len(corpus)
    for possible_page in corpus:
        output[possible_page] = p

    # With probability damping_factor, the random surfer should
    # randomly choose one of the links from page with equal probability.
    p = damping_factor / len(links)
    for link in links:
        output[link] += p

    return output


def sample_pagerank(corpus: Corpus, damping_factor: float, n: int) -> PageRankMap:
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # setup map to track how many times each page was visited
    visits: dict[str, int] = {}
    for possible_page in corpus:
        visits[possible_page] = 0

    # get first page randomly
    page = random.choice(list(corpus.keys()))
    visits[page] += 1  # mark it as visited once

    # generate samples
    for i in range(n - 1):
        # get transition model for current page
        model = transition_model(corpus, page, damping_factor)

        # transition to next page based on probabilities in model
        page = random.choices(
            population=list(model.keys()),
            weights=list(model.values()),
            k=1
        )[0]

        # record page transition
        visits[page] += 1

    # normalise visits to probabilities ie the PageRank
    ranks: PageRankMap = {}
    for page in corpus:
        ranks[page] = visits[page] / n

    print("iteration sample: ", sum(ranks.values()))
    return ranks


def iterate_pagerank(corpus: Corpus, damping_factor: float) -> PageRankMap:
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    ALL_PAGES_COUNT = len(corpus)
    ALL_PAGES = corpus.keys()

    ranks: PageRankMap = {}

    # create corpus of backlinks
    target_to_sources: Corpus = {}

    # assign initial uniform probabilities
    equal_probability = 1 / ALL_PAGES_COUNT
    for source in corpus:
        ranks[source] = equal_probability
        target_to_sources[source] = set()

        # A page that has no links at all should be interpreted as
        # having one link for every page in the corpus (including itself).
        if len(corpus[source]) == 0:
            corpus[source] = set(ALL_PAGES)

    # populate backward corpus (should be after the target_to_sources map is populated)
    for source in corpus:
        for target in corpus[source]:
            target_to_sources[target].add(source)

    MAX_EPOCH_DELTA_THRESHOLD = 0.001
    RANDOM_PAGE_PROBABILITY = (1 - damping_factor) / ALL_PAGES_COUNT
    while True:
        # start with positive assumption and see if it is maintained for full epoch
        epoch_delta_within_threshold = True

        # go through all pages per epoch
        for page in corpus:
            old_rank = ranks[page]
            new_rank = 0

            # get links to the page
            sources = target_to_sources[page]

            # get value of sum of probabilities that links would link to current page
            for source in sources:
                # NOTE: because we injected links where there were none, this should not be empty
                source_links_count = len(corpus[source])

                # PR(i) / NumLinks(i)
                new_rank += ranks[source] / source_links_count

            # scale backward link probabilities by scaling factor
            new_rank *= damping_factor

            # add fixed random page probability
            new_rank += RANDOM_PAGE_PROBABILITY

            ranks[page] = new_rank

            # check delta and update epoch maximum
            delta = abs(new_rank - old_rank)
            epoch_delta_within_threshold = epoch_delta_within_threshold and delta < MAX_EPOCH_DELTA_THRESHOLD

        if epoch_delta_within_threshold:
            break

    return ranks


if __name__ == "__main__":
    main()
