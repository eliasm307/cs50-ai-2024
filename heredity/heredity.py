import csv
import itertools
from operator import ge
import sys
from typing import Any, Literal, TypedDict


class GeneralProbabilities(TypedDict):
    gene: dict[Literal[0, 1, 2], float]
    trait: dict[Literal[0, 1, 2], dict[bool, float]]
    mutation: float


PROBS: GeneralProbabilities = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


class GeneTraitProbabilities(TypedDict):
    gene: dict[Literal[0, 1, 2], float]
    trait: dict[Literal[True, False], float]


PersonToGeneTraitProbabilitiesMap = dict[str, GeneTraitProbabilities]


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")

    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities: PersonToGeneTraitProbabilitiesMap = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}: ")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}: ")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p: .4f}")


class PersonData(TypedDict):
    name: str
    mother: str | None
    father: str | None
    trait: bool | None


def load_data(filename) -> dict[str, PersonData]:
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


PeopleMap = dict[str, PersonData]


def has_parents(person: PersonData):
    return bool(person["father"]) and bool(person['mother'])


def joint_probability(people: PeopleMap, one_gene: set[str], two_genes: set[str], have_trait: set[str]):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    def get_gene_count(person: str):
        """
        Get the number of genes the person has
        """
        if person in one_gene:
            return 1

        elif person in two_genes:
            return 2

        return 0

    def get_probability_of_parent_passing_gene(parent: str):
        """
        Get the probability that the given parent will pass on a gene to their child

        - If a parent has two copies of the gene, then they will pass it on to the child
        - if a parent has one copy of the gene, then the gene is passed on to the child with probability 0.5
        - if a parent has no copies of the gene, then they will not pass it on to the child
        """
        gene_count = get_gene_count(parent)

        if gene_count == 2:
            # ie its normally definite that they pass it on,
            # but we remove the chance that it mutates into a dud
            return 1 - PROBS["mutation"]

        elif gene_count == 1:
            # assuming the chance of mutation equally affects the
            # probability of passing on or not passing on the gene
            return 0.5

        # ie its normally definite that they dont pass it on,
        # but we add the chance that it mutates into something
        return 0 + PROBS['mutation']

    p = 1  # neutral stating value
    for name, person in people.items():
        # get target gene count
        gene_count = get_gene_count(name)

        if has_parents(person):
            # use marginalisation to determine the probability of inheriting from parents
            # ie we sum the probabilities of all the conditions that result in the target outcome
            assert person['mother'] is not None
            assert person['father'] is not None
            p_mother = get_probability_of_parent_passing_gene(person['mother'])
            p_father = get_probability_of_parent_passing_gene(person['father'])
            p_not_mother = 1 - p_mother
            p_not_father = 1 - p_father
            if gene_count == 2:
                # this can only happen if we get it from both parents
                # ie P(Mother) and P(Father)
                p *= p_mother * p_father

            elif gene_count == 1:
                # this can happen if we get it from either parent ie
                # ie P(Mother)¬P(Father) + ¬P(Mother)P(Father)
                p *= (p_mother * p_not_father) + (p_not_mother * p_father)

            if gene_count == 0:
                # this can happen if we dont get it from both parents
                # ie ¬P(Mother)¬P(Father)
                p *= p_not_mother * p_not_father

        else:
            # include gene probability
            p *= PROBS["gene"][gene_count]

        # include trait probability
        p *= PROBS['trait'][gene_count][name in have_trait]

    return p


def update(probabilities: PersonToGeneTraitProbabilitiesMap, one_gene: set[str], two_genes: set[str], have_trait: set[str], p: float):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        # add p to gene
        if person in one_gene:
            probabilities[person]["gene"][1] += p

        elif person in two_genes:
            probabilities[person]["gene"][2] += p

        else:
            probabilities[person]["gene"][0] += p

        # add p to trait
        probabilities[person]["trait"][person in have_trait] += p


def normalise_map_probabilities(map: dict[Any, float]):
    total = sum(map.values())
    factor = 1 / total
    for key in map:
        map[key] *= factor


def normalize(probabilities: PersonToGeneTraitProbabilitiesMap):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        normalise_map_probabilities(probabilities[person]["gene"])
        normalise_map_probabilities(probabilities[person]["trait"])


if __name__ == "__main__":
    main()
