from typing import Literal
from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

Person = Literal["A", "B", "C"]
Role = Literal["Knight", "Knave"]

people: list[Person] = ["A", "B", "C"]
roles: list[Role] = ["Knight", "Knave"]


def create_person_is_role_symbol(person: Person, role: Role):
    return Symbol(person + " is a " + role)


def add_general_facts(knowledge: And, available_people: list[Person]):
    knight_symbols = []
    knave_symbols = []

    # people can only have one role
    for person in available_people:
        personIsKnight = create_person_is_role_symbol(person, "Knight")
        personIsKnave = create_person_is_role_symbol(person, "Knave")
        # people can be either role
        knowledge.add(Or(personIsKnight, personIsKnave))
        # people cannot be both roles
        knowledge.add(Not(And(personIsKnight, personIsKnave)))
        knight_symbols.append(personIsKnight)
        knave_symbols.append(personIsKnave)

    all_are_knaves = And(*knave_symbols)
    some_are_knaves = Or(*knave_symbols)
    none_are_knaves = And(*map(lambda s: Not(s), knave_symbols))
    all_are_knights = And(*knight_symbols)
    some_are_knights = Or(*knight_symbols)
    none_are_knights = And(*map(lambda s: Not(s), knight_symbols))

    # if all are one role then none are the other role, and vice versa
    knowledge.add(Biconditional(all_are_knaves, none_are_knights))
    knowledge.add(Biconditional(all_are_knights, none_are_knaves))

    # if some are one role then some are the other role, and vice versa
    knowledge.add(Implication(some_are_knights, some_are_knaves))


def add_claim_by_person(knowledge: And, claim: And | Or | Implication | Not, person: Person):
    personIsKnight = create_person_is_role_symbol(person, "Knight")
    personIsKnave = create_person_is_role_symbol(person, "Knave")
    # If person is telling the truth then they are a knight
    knowledge.add(Implication(claim, personIsKnight))
    # If person is lying then they are a knave
    knowledge.add(Implication(Not(claim), personIsKnave))


# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And()

add_general_facts(knowledge0, available_people=["A"])
add_claim_by_person(
    knowledge=knowledge0,
    person='A',
    claim=And(AKnight, AKnave),  # "I am both a knight and a knave."
)

# Puzzle 1
# A says "We are both knaves."
AClaim = And(AKnave, BKnave)
# B says nothing.
knowledge1 = And()

add_general_facts(knowledge1, ["A", "B"])
add_claim_by_person(
    knowledge=knowledge1,
    person='A',
    claim=And(AKnave, BKnave),  # "We are both knaves."
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And()

add_general_facts(knowledge2, ["A", "B"])
a_b_are_same_kind_claim = Or(
    And(AKnave, BKnave),
    And(AKnight, BKnight)
)
add_claim_by_person(
    knowledge=knowledge2,
    person='A',
    #  "We are the same kind."
    claim=a_b_are_same_kind_claim,
)
add_claim_by_person(
    knowledge=knowledge2,
    person='B',
    #  "We are of different kinds."
    claim=Not(a_b_are_same_kind_claim),
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # TODO
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
