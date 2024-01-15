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


def add_general_facts_for_people(knowledge: And, available_people: list[Person]):
    for person in available_people:
        personIsKnight = create_person_is_role_symbol(person, "Knight")
        personIsKnave = create_person_is_role_symbol(person, "Knave")
        # people can be either role
        knowledge.add(Or(personIsKnight, personIsKnave))
        # people cannot be both roles
        knowledge.add(Not(And(personIsKnight, personIsKnave)))


def add_claim_by_person(knowledge: And, claim: And | Or | Implication, person: Person):
    personIsKnight = create_person_is_role_symbol(person, "Knight")
    personIsKnave = create_person_is_role_symbol(person, "Knave")
    # If person is telling the truth then they are a knight
    knowledge.add(Implication(claim, personIsKnight))
    # If person is lying then they are a knave
    knowledge.add(Implication(Not(claim), personIsKnave))


# Puzzle 0
# A says "I am both a knight and a knave."
claim_by_a = And(AKnight, AKnave)
knowledge0 = And()
add_general_facts_for_people(knowledge0, ["A"])
add_claim_by_person(
    knowledge=knowledge0,
    claim=claim_by_a,
    person='A'
)

# Puzzle 1
# A says "We are both knaves."
AClaim = And(AKnave, BKnave)
# B says nothing.
knowledge1 = And(
    # If A is telling the truth then they are a knight
    Implication(AClaim, AKnight),
    # If A is lying then they are a knave
    Implication(Not(AClaim), AKnave),
    # If they are both not knaves then one of them is a knight
    Implication(Not(And(AKnave, BKnave)), Or(AKnight, BKnight))
)

add_general_facts_for_people(knowledge1, ["A", "B"])

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # Implication(
    #     Or(And(AKnave, BKnave), And(AK))
    # )
)

add_general_facts_for_people(knowledge2, ["A", "B"])

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
