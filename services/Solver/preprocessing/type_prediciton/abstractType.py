import abc

class Type(object, metaclass=abc.ABCMeta):
    def get_type(self, input_str):
        raise NotImplementedError('get_type must be implemented!')
