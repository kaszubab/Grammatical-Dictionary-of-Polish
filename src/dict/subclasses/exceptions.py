class Error(Exception):
     pass


class Relationship_exists(Error):
    pass

class Relationship_not_found(Error):
    pass

class Relationship_duplicated(Error):
    pass

