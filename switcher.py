import abc


class ProgramSwitcher(metaclass=abc.ABCMeta):
    def run(self):
        raise NotImplementedError()