import configparser

def loadConfig(path='./config.cfg'):
    # load config file
    try:
        config = configparser.ConfigParser()
        with open(path) as f:
            config.read_file(f)
    except IOError:
        raise ValueError("Missing configuration file.")

    # inheri global config
    if "global" in config:
        for section in config:
            for key in config["global"]:
                if key not in section:
                    config[section][key] = config["global"][key]
    # done
    return config
