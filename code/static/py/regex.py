import re

# Pattern for ID (numeric, optionally with leading zeros)
ID_PATTERN = r'^\d+$'

# Pattern for Name (letters, spaces, hyphens)
NAME_PATTERN = r'^[a-zA-Z\s\-]+$'

# Pattern for Address (letters, numbers, spaces, commas, periods)
ADDRESS_PATTERN = r'^[a-zA-Z0-9\s,\.]+$'

# Pattern for Number (phone number format, adjust as needed)
NUMBER_PATTERN = r'^\+?(\d{1,4}[\s-])?(\d{1,4}[\s-])?\d+$'

# Pattern for Neighborhood (letters, spaces)
BAIRRO_PATTERN = r'^[a-zA-Z\s]+$'

# Pattern for Complement (letters, numbers, spaces, optional)
COMPLEMENT_PATTERN = r'^[a-zA-Z0-9\s]*$'

# Pattern for Municipality (letters, spaces)
MUNICIPIO_PATTERN = r'^[a-zA-Z\s]+$'

# Pattern for Observation (alphanumeric and punctuation)
OBSERVACAO_PATTERN = r'^[a-zA-Z0-9\s,.!?-]*$'

# Pattern for Telefones (comma-separated phone numbers)
TELEFONES_PATTERN = r'^(\+?\d+[\s-]?)+$'

def validate_input(pattern, input_value):
    """ Validate the input value against the provided regex pattern. """
    return re.match(pattern, input_value) is not None

def validate_id(id):
    return validate_input(ID_PATTERN, id)

def validate_name(name):
    return validate_input(NAME_PATTERN, name)

def validate_address(address):
    return validate_input(ADDRESS_PATTERN, address)

def validate_number(number):
    return validate_input(NUMBER_PATTERN, number)

def validate_bairro(bairro):
    return validate_input(BAIRRO_PATTERN, bairro)

def validate_complement(complement):
    return validate_input(COMPLEMENT_PATTERN, complement)

def validate_municipio(municipio):
    return validate_input(MUNICIPIO_PATTERN, municipio)

def validate_observacao(observacao):
    return validate_input(OBSERVACAO_PATTERN, observacao)

def validate_telefones(telefones):
    # Split by comma and validate each phone number
    phone_numbers = telefones.split(',')
    return all(validate_input(NUMBER_PATTERN, phone_number.strip()) for phone_number in phone_numbers)
