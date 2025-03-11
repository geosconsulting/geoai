from typing import List
from pydantic import BaseModel, constr, conint

class Address(BaseModel):
    id_code: constr(min_length=10, max_length=10)  # Fixed length fiscal code
    street: constr(min_length=5)  # Street cannot be empty
    # postal_code: constr(min_length=5)  # Exactly 5 digits as string (preserves leading zeros)
    postal_code: conint(ge=10000, le=99999)  # Assuming valid Italian postal codes
    city: constr(min_length=4)  # City cannot be empty
    province: constr(min_length=2, max_length=2)  # Province code is always 2 characters

class AddressList(BaseModel):
    addresses: List[Address]


addresses = [
        ['F0LC1F2J25', 'PIAZZA VITTORIA 16', 88900, 'CROTONE', 'KR'],
        ['B0BA4B2OG1', 'PIAZZA CARDINALE PANICO 4', 73039, 'TRICASE', 'LE'],
        ['F19O6F37FE', 'PIAZZA DEGLI ALPINI 7A', 31030, 'BORSO DEL GRAPPA', 'TV'],
        ['F1B41F39U1', 'PIAZZA DEL FONTANILE 14', 31, 'ARTENA', 'RM'],
        ['F1LCPF3TNS', 'PIAZZA BENIAMINO CHIATTO 2', 87100, 'COSENZA', 'CS'],
        ['F1KJ7F3SBW', 'PIAZZA FISAC 2', 22100, 'COMO', 'CO'],
        ['J0YC6J3JA2', 'PIAZZA GIACOMO LEOPARDI 12', 60012, 'TRECASTELLI', 'AN']
    ]

# Convert your list to proper format
address_data = {"addresses": [
    {
        "id_code": code,
        "street": street,
        "postal_code": postal,
        "city": city,
        "province": province
    } for code, street, postal, city, province in addresses
]}

# Validate the data
validated_addresses = AddressList(**address_data)