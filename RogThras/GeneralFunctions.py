import itertools

#-------------------------------------------------------------------------------
def shortest_hitting_set(lists):
    # Remove empty lists: if any list is empty, there's no valid hitting set
    lists = [set(lst) for lst in lists if lst]

    # Get the universe of elements
    universe = set().union(*lists)

    # Try all combinations of elements, starting from size 1
    for r in range(1, len(universe)+1):
        for subset in itertools.combinations(universe, r):
            # Check if this subset intersects all input sets
            if all(any(x in s for x in subset) for s in lists):
                return list(subset)  # Found the smallest valid subset

    return None
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    lists = [
        ['a', 'b', 'c'],
        ['b', 'c'],
        ['a', 'd'],
        ['c', 'e', 'f'],
        ['a','g'],
        ]
    result = shortest_hitting_set(lists)
    print("Shortest list that hits all input lists:", result)







