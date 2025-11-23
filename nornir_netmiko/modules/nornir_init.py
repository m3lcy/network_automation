from nornir import InitNornir

def init_nornir():
    return InitNornir(config_file = "config.yaml")