import json

def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False

def has_kvp_method(o):
    method = getattr(o, 'to_kvp', None)
    if method == None:
        return False

    if callable(method):
        return True

    return False

class Namespace:
    """A Namespace represents a naming heirachy, starting with an
    empty root. For example DNS is a namespace heirachy:
    .com.example.www where the root namespace is actualy the implicit
    empty namespace before the first '.' character. Each subsequent
    level fo the namespace divides the namespace in to logical
    heirachical steps. Each level of the namespace may contain a single
    item that is attached at that level: Eg: .car.engine.fuelInjector may
    contain a single Python Object attached to it."""


    def __init__(self, name='', parent=None):
        self.name = name
        self.parent = parent
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
            self.children[subpath] = Namespace(subpath, self)

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
            yield self


    def iterator(self):
        """Child first traversal of namespace tree."""

        yield from self.__next_item()

    def to_kvp_item(self):
        form = {}
        form['path'] = self.canonical_path()
        if is_jsonable(self.item):
            form['item'] = self.item
        elif has_kvp_method(self.item):
            form['item'] = self.item.to_kvp();
        else:
            form['item'] = '<not-serializable>'

        return form;

    def to_kvp(self):
        ns_list = []
        iterator = self.iterator()
        for i in iterator:
            ns_list.append(i.to_kvp_item())

        return ns_list;

    def canonical_path(self):
        path = self.name
        parent = self.parent
        while parent != None:
            path = "{0}.{1}".format(parent.name, path)
            parent = parent.parent

        return path.lstrip('.')
