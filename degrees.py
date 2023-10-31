import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}
# names = {'kisha morales': {'11077519'}}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}
# people = {'11077519': {'name': 'Kisha Morales', 'birth': '', 'movies': set()}}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}
# movies = {'11171390': {'title': 'Kakol-zari', 'year': '1972', 'stars': {'7885560', '5095201', '1164771', '1028434', '1289559'}}}



def load_data(directory):
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
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    Shorthest paths between person with id source and person with id target

    Assuming there is a path from the source to the target, your function should return a list,
    where each list item is the next (movie_id, person_id) pair in the path from the source to the target. 
    Each pair should be a tuple of two strings.

    For example, if the return value of shortest_path were [(1, 2), (3, 4)], 
    that would mean that the source starred in movie 1 with person 2, 
    person 2 starred in movie 3 with person 4, and person 4 is the target.

    If there are multiple paths of minimum length from the source to the target, 
    your function can return any of them.
    If there is no possible path between two actors, your function should return None.
    
    You may call the neighbors_for_person function, which accepts a person's id as input, and returns a set of (movie_id, person_id) pairs for all people who starred in a movie with a given person.

    If no possible path, returns None.
    """

    searchedItems = set()
    frontier = QueueFrontier()
    initialState = source

    frontier.add(Node(state=initialState,parent=None,action=None))

    while not frontier.empty():
        node = frontier.remove()
        if frontier.contains_state(target):
            solution = []
            
            for node in frontier.frontier:
                if node.state == target:
                    print(f'target:{node.state}')
                    while node.parent is not None:
                        pair = (node.action,node.state) 
                        solution.append(pair)          
                        node = node.parent
                    solution.reverse()
                    break
            
            return solution
        else:
            moviesWhereStatePlayed = people.get(node.state)['movies']
            for movie in moviesWhereStatePlayed:
                peopleWhoPlayedInMovies = movies.get(movie)['stars']
                for person in peopleWhoPlayedInMovies:
                    newnode = Node(state=person,parent=node,action=movie)
                    if newnode.state not in searchedItems:
                        frontier.add(newnode)
            searchedItems.add(node.state)

    raise NotImplementedError


def person_id_for_name(name):
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


def neighbors_for_person(person_id):
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
