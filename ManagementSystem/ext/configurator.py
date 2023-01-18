import configparser


class SystemVariables:
    def __init__(self, header='DEFAULT', path='system_variables.ini'):
        self.system_variables = configparser.ConfigParser()
        self.__header = header
        self.__path = path
        self.load_variables()

    def __getitem__(self, key):
        return self.system_variables.get(self.__header, key)

    def load_variables(self):
        self.system_variables.read(self.__path)

    def update_variable(self, key, value):
        self.system_variables.set(self.__header, key, value)

    def write_variables(self):
        with open(self.__path, 'w') as configfile:
            self.system_variables.write(configfile)
