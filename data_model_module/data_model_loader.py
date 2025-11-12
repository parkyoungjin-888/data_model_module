import importlib


def get_data_model(file_name: str, model_name: str, project_model_list: list[str]):
    module = importlib.import_module(f'data_model_module.data_model.{file_name}')
    data_model = getattr(module, model_name)
    project_model_dict = {project_model: getattr(module, project_model) for project_model in project_model_list}
    return data_model, project_model_dict
