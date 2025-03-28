import importlib


def import_model(model_name: str):
    module = importlib.import_module('data_model_module')
    return getattr(module, model_name)
