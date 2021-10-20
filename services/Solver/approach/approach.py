import abc


class Approach(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def generate_CEA(self, cols=None, rows=None):
        raise NotImplementedError('generate_CEA must be implemented!')

    @abc.abstractmethod
    def generate_CTA(self, cols=None):
        raise NotImplementedError('generate_CTA must be implemented!')

    @abc.abstractmethod
    def generate_CPA(self, cols1=None, cols2=None):
        raise NotImplementedError('generate_CTA must be implemented!')
