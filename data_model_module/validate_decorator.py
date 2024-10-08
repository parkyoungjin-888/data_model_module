from functools import wraps
from pydantic import ValidationError


def validate_input(model):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                validated_data = model(**kwargs).model_dump()
            except ValidationError as e:
                return {'validation error': e.errors()}
            return func(data=validated_data, *args)
        return wrapper
    return decorator


def validate_output(model):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if result is None:
                return None
            try:
                validated_data = model(**result)
            except ValidationError as e:
                return {'validation error': e.errors()}
            return validated_data.model_dump()
        return wrapper
    return decorator
