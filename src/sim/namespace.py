class Namespace:
    """A Namespace represents a naming heirachy, starting with an
    empty root. For example DNS is a namespace heirachy:
    .com.example.www where the root namespace is actualy the implicit
    empty namespace before the first '.' character. Each subsequent
    level fo the namespace divides the namespace in to logical
    heirachical steps. Each level of the namespace may contain a single
    item that is attached at that level: Eg: .car.engine.fuelInjector may
    contain a single Python Object attached to it."""


    def __init__(self, name=''):
        self.name = name
        self.children = {}
        self.item = None

    def tokenize_path(self, path):
        if path == '':
            return '', ''

        tokens = path.split('.')

        subpath = tokens.pop(0)
        remainder = ".".join(tokens)

        return subpath, remainder

    def insert(self, path, item):
        """Inserts an item at the specific Namespace. Path may be a
        namespace in the form org.suborg.division. A Path may contain
        one item."""

        if path == '':
            self.item = item
            return

        subpath, remainder = self.tokenize_path(path)

        if subpath not in self.children:
            self.children[subpath] = Namespace(subpath)

        self.children[subpath].insert(remainder, item)

    def get(self, path):
        """Returns item in the given namespace or None. Returns a list
        as this may be a partial match of an entire namespace subtree."""

        if path == '':
            return self.get_all()

        subpath, remainder = self.tokenize_path(path)

        return self.children[subpath].get(remainder)

    def get_all(self):
        """Returns all items within the namespace regardless of path."""

        items = []
        if self.item != None:
            items.append(self.item)

        for c in self.children.values():
            child_items = c.get_all()
            items.extend(child_items)

        return items

    def __next_item(self):
        for c in self.children.values():
            yield from c.__next_item()

        if self.item != None:
            yield self.item


    def iterator(self):
        """Child first traversal of namespace tree."""

        yield from self.__next_item()
