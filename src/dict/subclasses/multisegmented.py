class multisegmented_module:
    def __init__(self):
        self.multisegmented = {}

    def add_multisegmented(self, ids, stable_list, interchangeable):
        if ids not in self.multisegmented:
            self.multisegmented[ids] = [stable_list, interchangeable]

            if interchangeable is not None:
                tmp = list(ids)
                tmp[interchangeable[0]-1],tmp[interchangeable[1]-1] = tmp[interchangeable[1]-1],tmp[interchangeable[0]-1]
                other_ids = tuple(tmp)
                self.multisegmented[other_ids] = [stable_list, interchangeable]

    def is_multisegmented(self, ids):
        return ids in self.multisegmented.keys()

    def get_multitsegmented_info(self, ids):
        return self.multisegmented.get(ids)