def get_variable_name(variable, local_vars):
    return [name for name, value in local_vars.items() if value is variable]