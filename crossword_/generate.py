from copy import deepcopy
from itertools import combinations
import sys
from typing import Any

from crossword import Crossword, Variable


"""
A dictionary mapping variables to their corresponding words
"""
Assignment = dict[Variable, str]

"""
Variables that are related ie they have letters that overlap
in the crossword grid
"""
Arc = tuple[Variable, Variable]


class CrosswordCreator:
    def __init__(self, crossword: Crossword):
        """
        Create new CSP crossword generate.
        """

        self.crossword = crossword

        """
        A dictionary that maps variables to a set of possible words
        the variable might take on as a value
        """
        self.domains = {
            var: self.crossword.words.copy() for var in self.crossword.variables
        }

    def letter_grid(self, assignment: Assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment: Assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment: Assignment, filename: str):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont

        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters: Any = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size, self.crossword.height * cell_size),
            "black",
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                rect: Any = [
                    (j * cell_size + cell_border, i * cell_size + cell_border),
                    (
                        (j + 1) * cell_size - cell_border,
                        (i + 1) * cell_size - cell_border,
                    ),
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (
                                rect[0][0] + ((interior_size - w) / 2),
                                rect[0][1] + ((interior_size - h) / 2) - 10,
                            ),
                            letters[i][j],
                            fill="black",
                            font=font,
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable, words in self.domains.items():
            for word in words.copy():
                if len(word) != variable.length:
                    words.remove(word)

    def revise(self, x: Variable, y: Variable):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[(x, y)]
        if not overlap:
            return False

        revised = False
        overlap_x, overlap_y = overlap
        for word_x in self.domains[x].copy():
            x_has_matching_y_word = False
            for word_y in self.domains[y]:
                if word_x[overlap_x] == word_y[overlap_y]:
                    x_has_matching_y_word = True
                    break  # match found, no need to continue

            if not x_has_matching_y_word:
                self.domains[x].remove(word_x)
                revised = True

        return revised

    def ac3(self, arcs: list[Arc] | None = None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if arcs is None:
            arcs = self.get_all_arcs()
        else:
            arcs = arcs.copy()  # avoid mutating the input

        while len(arcs) > 0:
            x, y = arcs.pop()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False  # inconsistency found, cannot solve problem

                # enqueue arcs from x to check for consistency after revision
                for neighbour in self.crossword.neighbors(x):
                    if neighbour != y:  # dont include y as we have just considered it
                        # NOTE: neighbour must be first for it to get revised
                        arcs.append((neighbour, x))

        # all possible revisions completed without inconsistencies,
        # ie solution found
        return True

    def get_all_arcs(self):
        """
        Gets all variable-to-variable arcs/relationships on the crossword
        """
        arcs: list[Arc] = []

        # NOTE: this must include all combinations, even equivalent ones e.g. (x, y) and (y, x)
        # as the revision of arcs happens only for the first element so need 2 tuples to cover both elements
        for x in self.crossword.variables:
            for y in self.crossword.variables:
                if x == y:
                    continue  # we are only looking at arcs between different variables

                arc = self.crossword.overlaps[(x, y)]
                if arc:
                    arcs.append((x, y))

        return arcs

    def assignment_complete(self, assignment: Assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable not in assignment:
                return False

        return True  # all variables assigned a value

    def consistent(self, assignment: Assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.

        An assignment is consistent if it satisfies all of the constraints of the problem:
        that is to say, all values are distinct, every value is the correct length,
        and there are no conflicts between neighboring variables.
        """
        unique_words: set[str] = set()
        for x, word_x in assignment.items():
            if word_x in unique_words:
                return False  # duplicated word

            unique_words.add(word_x)

            if len(word_x) != x.length:
                return False  # word length is incorrect

            # check there are no conflicts between neighboring/overlapping variables
            for y in self.crossword.neighbors(x):
                if y not in assignment:
                    continue  # neighbour not yet assigned, ignore

                word_y = assignment[y]
                overlap_x, overlap_y = self.get_definite_overlap(x, y)
                if word_x[overlap_x] != word_y[overlap_y]:
                    return False  # overlap conflict

        return True  # all overlaps are valid

    def order_domain_values(self, var: Variable, assignment: Assignment) -> list[str]:
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # This is a list of tuples where the first tuple is
        # the count of neighbours a word rules out and the second is the word
        output: list[tuple[int, str]] = []
        neighbours = [
            v
            for v in self.crossword.neighbors(var)
            if v
            not in assignment  # already assigned neighbours should not be counted as they wont be ruled out
        ]

        # count how many neighboring words each domain word would eliminate
        for word_var in self.domains[var]:
            eliminated_count = 0
            for neighbour in neighbours:
                overlap_var, overlap_neighbour = self.get_definite_overlap(
                    var, neighbour
                )

                for word_neighbour in self.domains[neighbour]:
                    if word_var[overlap_var] != word_neighbour[overlap_neighbour]:
                        eliminated_count += 1

            output.append((eliminated_count, word_var))

        # sort words ascending by their neighbour elimination count
        return [word for (_, word) in sorted(output)]

    def get_definite_overlap(self, x: Variable, y: Variable) -> tuple[int, int]:
        """
        Gets the overlap between two variables where it is known an overlap exists
        """
        overlap = self.crossword.overlaps[(x, y)]
        if not overlap:
            raise Exception(str(x) + " should overlap " + str(y))

        return overlap

    def select_unassigned_variable(self, assignment: Assignment) -> Variable:
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        remaining_counts = [
            (len(self.domains[v]), v)
            for v in self.crossword.variables
            if v not in assignment
        ]
        remaining_counts.sort(key=lambda x: x[0])

        min_count = remaining_counts[0][0]
        vars_with_min_count = [
            v for (count, v) in remaining_counts if count == min_count
        ]

        if len(vars_with_min_count) == 1:
            return vars_with_min_count[0]

        # we have multiple variables with minimum remaining values,
        # so return the one with largest degree (ie has the most neighbours)
        max_degree: tuple[int, Variable] = (0, vars_with_min_count[0])
        for v in vars_with_min_count:
            degree = len(self.crossword.neighbors(v))
            if degree > max_degree[0]:
                max_degree = (degree, v)

        return max_degree[1]

    def backtrack(self, assignment: Assignment) -> Assignment | None:
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        v = self.select_unassigned_variable(assignment)
        for word in self.order_domain_values(v, assignment):
            # try assigning word
            new_assignment = assignment.copy()
            new_assignment[v] = word

            # check if the assignment is generally valid, otherwise skip it
            if self.consistent(new_assignment):
                # check arc consistency
                original_domains = self.domains
                self.domains = deepcopy(self.domains)
                self.domains[v] = {word}
                if not self.ac3():
                    continue

                # continue along this path to a solution
                solution = self.backtrack(new_assignment)
                if solution:
                    return solution  # solution found

                # solution not found on this path, restore state for next path
                # (assignment isn't mutated so doesn't need restoring)
                self.domains = original_domains

        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
