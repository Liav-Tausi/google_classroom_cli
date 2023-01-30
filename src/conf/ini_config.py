import configparser


def get_config(filename: str, section: str) -> dict:
    db_config: dict = dict()

    parser = configparser.ConfigParser()
    parser.read(filename)
    if parser.has_section(section):
        parameters = parser.items(section)
        for param in parameters:
            db_config[param[0]] = param[1]
    else:
        raise Exception()
    return db_config
