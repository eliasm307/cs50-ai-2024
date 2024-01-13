import csv
import sys
from typing import Dict, Set, TypedDict

from util import Node, StackFrontier, QueueFrontier


# Maps names to a set of corresponding person_ids
names: Dict[str, Set[str]] = {}


class PersonInfo(TypedDict):
    name: str
    birth: str
    movies: Set[str]


# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people: Dict[str, PersonInfo] = {}


class MovieInfo(TypedDict):
    title: str
    year: str
    stars: Set[str]


# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies: Dict[str, MovieInfo] = {}


def load_data(directory: str):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]['name']
            person2 = people[path[i + 1][1]]["name"]
            # type: ignore we are skipping the first segment without a movie_id, but type still has `None`
            movie = movies[path[i + 1][0]]["title"]  # type: ignore
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source_person_id: str, target_person_id: str) -> list[tuple[str | None, str]] | None:
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    # initial frontier with initial state
    frontier = QueueFrontier()
    frontier.add(Node(source_person_id))

    # initial empty visited set
    visited_person_ids: set[str] = set()

    while True:
        if frontier.empty():
            return None  # no link to target

        # get next node from frontier
        current_node = frontier.remove()

        # check if node is the goal
        if current_node.person_id == target_person_id:
            path: list[tuple[str | None, str]] = []
            while current_node.parent:  # Note this goes up to the source person but does not include them
                path.append((current_node.from_movie_id, current_node.person_id))
                current_node = current_node.parent

            path.reverse()  # show path from source to target
            return path

        # record node as visited
        visited_person_ids.add(current_node.person_id)

        # expand node and add neighbors to frontier
        for movie_id, related_person_id in neighbors_for_person(current_node.person_id):
            if not related_person_id in visited_person_ids:
                frontier.add(Node(related_person_id, current_node, movie_id))
                visited_person_ids.add(related_person_id)


def person_id_for_name(name: str) -> str | None:
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id: str) -> set[tuple[str, str]]:
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
