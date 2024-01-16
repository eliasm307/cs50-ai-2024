import itertools
import random
import re


RowColumn = tuple[int, int]


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells: set[RowColumn], mine_count: int):
        self.local_cells = set(cells)
        self.mine_count = mine_count

    def __eq__(self, other: 'Sentence'):
        return self.local_cells == other.local_cells and self.mine_count == other.mine_count

    def __str__(self):
        return f"( {self.local_cells} = {self.mine_count} )"


    def known_mines(self) -> set[RowColumn]:
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        if self.mine_count == len(self.local_cells):
            print("[Sentence] All cells are mines:", self)
            return self.local_cells.copy() # all are mines

        return set()


    def known_safes(self) -> set[RowColumn]:
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        if self.mine_count == 0:
            print("[Sentence] All cells are safe:", self)
            return self.local_cells.copy() # no mines so all are safe

        return set()


    def mark_mine(self, cell: RowColumn):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        if cell not in self.local_cells:
            return

        print("[Sentence] Marking mine:", cell, "removing from: ", self)
        # if cell is mine then we can remove it from the sentence
        # and reduce the mine count
        self.local_cells.remove(cell)
        if self.mine_count > 0:
            self.mine_count -= 1

        print("[Sentence] After marking mine:", self)


    def mark_safe(self, cell: RowColumn):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        if cell not in self.local_cells:
            return

        print("[Sentence] Marking safe:", cell, "removing from: ", self)
        # if cell is safe then we can remove it from the sentence
        self.local_cells.remove(cell)
        print("[Sentence] After marking safe:", self)


    def is_subset_of(self, s: 'Sentence'):
        return self.local_cells.issubset(s.local_cells)


    def resolve_with(self, sub_sentence: 'Sentence') -> 'Sentence | None':
        remaining_cells = self.local_cells.symmetric_difference(sub_sentence.local_cells)
        remaining_mine_count = max(0, self.mine_count - sub_sentence.mine_count)

        s = Sentence(
            cells=remaining_cells,
            mine_count=remaining_mine_count
        )

        if s.is_redundant():
            return

        return s


    def is_redundant(self):
        return len(self.local_cells) == 0


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made: set[RowColumn] = set()

        # Keep track of which cells can still be clicked on
        self.available_moves: set[RowColumn] = set()

        # Keep track of cells known to be safe or mines
        self.mines: set[RowColumn] = set()
        self.safes: set[RowColumn] = set()

        # List of sentences about the game known to be true
        self.knowledge: list[Sentence] = []

        # Load list of cells that we are still unsure of (ie all of them initially)
        self.unknown_cells: set[RowColumn] = set()
        self.mine_counts: dict[RowColumn, int] = dict()

        for row_index in range(height):
            for col_index in range(width):
                cell = (row_index, col_index)
                self.unknown_cells.add(cell)
                self.available_moves.add(cell)


    def mark_mine(self, cell: RowColumn):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """

        if cell not in self.mines:
            # if we already know the cell is a mine then we dont need to do anything
            self.mines.add(cell)
            self.unknown_cells.remove(cell)

        self.available_moves.remove(cell)
        print("Marking mine:", cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)


    def mark_safe(self, cell: RowColumn):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """

        if cell not in self.safes:
            # if we already know the cell is safe then we dont need to do anything
            self.safes.add(cell)
            self.unknown_cells.remove(cell)

        print("Marking safe:", cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)


    def mark_revealed(self, cell: RowColumn, mine_count: int):
        if cell in self.available_moves:
            self.available_moves.remove(cell)

        self.moves_made.add(cell)
        self.mark_safe(cell)
        self.mine_counts[cell] = mine_count


    def add_knowledge(self, cell: RowColumn, count: int):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        print("")
        neighbours = self.get_unknown_neighbours(cell)
        print("Adding knowledge:", cell, "has mines", count, "and neighbours", neighbours, "...")
        self.mark_revealed(cell, count)
        s = Sentence(neighbours, count)
        print("Adding sentence to knowledge:", s)
        self.knowledge.append(s)
        self.print_board()

        has_new_info = True # ie we just added a safe and a sentence

        while has_new_info: # keep checking until we have exhausted all inferences
            self.remove_redundant_sentences()
            safes_added = self.infer_and_mark_safes()
            mines_added = self.infer_and_mark_mines()
            sentences_added = self.infer_and_add_sentences()
            has_new_info = mines_added or safes_added or sentences_added

        print("After adding knowledge:", cell, "has mines", count)
        self.print_board()


    def infer_and_add_sentences(self):
        """
        Reviews existing clauses to see if any can be resolved to new clauses
        """
        new_sentences: list[Sentence] = []
        duplicates: list[Sentence] = []

        for left_index in range(len(self.knowledge)):
            for right_index in range(left_index + 1, len(self.knowledge)):
                s1 = self.knowledge[left_index]
                s2 = self.knowledge[right_index]
                if s1 == s2:
                    duplicates.append(s1)
                    continue

                new_sentence = self.try_resolving_sentences(s1, s2)
                if new_sentence:
                    new_sentences.append(new_sentence)

        has_changes = False

        for sentence in duplicates:
            self.knowledge.remove(sentence)

        # add sentences if they dont already exist
        for sentence in new_sentences:
            if not self.knowledge_includes_similar_sentence(sentence):
                has_changes = True
                self.knowledge.append(sentence)
            else:
                print("Skipping redundant existing sentence:", sentence)

        return has_changes


    def remove_redundant_sentences(self):
        """
        Removes any sentences that are redundant
        """
        for sentence in self.knowledge:
            if sentence.is_redundant():
                self.knowledge.remove(sentence)


    def knowledge_includes_similar_sentence(self, new_sentence: Sentence):
        for existing_sentence in self.knowledge:
            if existing_sentence == new_sentence:
                return True  # found an existing matching sentence

        return False  # sentence is unique


    def try_resolving_sentences(self, s1: Sentence, s2: Sentence) -> Sentence | None:
        if s1 == s2:
            return None

        if s1.is_redundant() or s2.is_redundant():
            return

        if s1.is_subset_of(s2):
            s = s2.resolve_with(s1)
            if s:
                print("Inferred new sentence:", s, "from removing", s1, "from", s2)
            return s

        elif s2.is_subset_of(s1):
            s =  s1.resolve_with(s2)
            if s:
                print("Inferred new sentence:", s, "from removing", s2, "from", s1)
            return s

    def infer_and_mark_mines(self):
        has_changes = False
        for sentence in self.knowledge:
            new_mines = sentence.known_mines()
            has_changes = has_changes or len(new_mines) > 0
            if len(new_mines):
                print("Inferred mines:", new_mines)

            for mine in new_mines:
                self.mark_mine(mine)

        return has_changes


    def infer_and_mark_safes(self):
        has_changes = False
        for sentence in self.knowledge:
            new_safes = sentence.known_safes()
            has_changes = has_changes or len(new_safes) > 0
            if len(new_safes):
                print("Inferred safes:", new_safes)

            for safe in new_safes:
                self.mark_safe(safe)

        return has_changes


    def get_unknown_neighbours(self, source_cell: RowColumn):
        neighbours: set[RowColumn] = set()
        x, y = source_cell

        # Loop over all cells within one row and column and ignore invalid coordinates
        for row_index in range(max(0, x - 1), min(self.height, x + 2)):
            for col_index in range(max(0, y - 1), min(self.width, y + 2)):
                current_cell = (row_index, col_index)

                # Ignore the cell itself
                if current_cell == source_cell:
                    continue

                # ignore cells with known states
                if current_cell not in self.unknown_cells:
                    continue


                neighbours.add(current_cell)

        return neighbours

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for move in self.safes:
            if move in self.available_moves:
                print("Found safe move:", move)
                return move


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        return next(iter(self.available_moves))


    def print_row_divider(self):
        print("     " + "-----" * self.width)


    def print_board(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        print("")
        print("     ", end="")
        for col in range(self.width):
            print("  " + str(col) + "  ", end="")

        print("")

        for row in range(self.height):
            self.print_row_divider()
            for col in range(-1, self.width):
                if(col == -1):
                    print("  " + str(row) + " ", end="")
                    continue

                cell = (row, col)
                if cell in self.moves_made:

                    print("| " + self.get_number_emoji(self.mine_counts[cell]) + "  ", end="")

                elif cell in self.mines:
                    print("| 💣 ", end="")

                elif cell in self.safes:
                    print("| 🛟 ", end="")

                else:
                    print("| ❔ ", end="")

            print("|")

        self.print_row_divider()
        print("")

    def get_number_emoji(self, n: int):
        return {
            0: "0️⃣",
            1: "1️⃣",
            2: "2️⃣",
            3: "3️⃣",
            4: "4️⃣",
            5: "5️⃣",
            6: "6️⃣",
            7: "7️⃣",
            8: "8️⃣",
            9: "9️⃣",
        }[n]