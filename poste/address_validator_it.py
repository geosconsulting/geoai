import re
from typing import List, Dict, Tuple

class ItalianAddressValidator:
    def __init__(self):
        # Define valid street types
        self.street_types = {'PIAZZA', 'VIA', 'CORSO', 'VIALE', 'VICOLO', 'LARGO', 'LUNGOMARE'}
        
        # Define province codes and their corresponding regions
        self.province_codes = {
            'AG': 'Agrigento', 'AL': 'Alessandria', 'AN': 'Ancona', 'AO': 'Aosta',
            'AR': 'Arezzo', 'AP': 'Ascoli Piceno', 'AT': 'Asti', 'AV': 'Avellino',
            'BA': 'Bari', 'BT': 'Barletta-Andria-Trani', 'BL': 'Belluno', 'BN': 'Benevento',
            'BG': 'Bergamo', 'BI': 'Biella', 'BO': 'Bologna', 'BZ': 'Bolzano',
            'BS': 'Brescia', 'BR': 'Brindisi', 'CA': 'Cagliari', 'CL': 'Caltanissetta',
            'CB': 'Campobasso', 'CE': 'Caserta', 'CT': 'Catania', 'CZ': 'Catanzaro',
            'CH': 'Chieti', 'CO': 'Como', 'CS': 'Cosenza', 'CR': 'Cremona',
            'KR': 'Crotone', 'CN': 'Cuneo', 'EN': 'Enna', 'FM': 'Fermo',
            'FE': 'Ferrara', 'FI': 'Firenze', 'FG': 'Foggia', 'FC': 'Forlì-Cesena',
            'FR': 'Frosinone', 'GE': 'Genova', 'GO': 'Gorizia', 'GR': 'Grosseto',
            'IM': 'Imperia', 'IS': 'Isernia', 'SP': 'La Spezia', 'AQ': "L'Aquila",
            'LT': 'Latina', 'LE': 'Lecce', 'LC': 'Lecco', 'LI': 'Livorno',
            'LO': 'Lodi', 'LU': 'Lucca', 'MC': 'Macerata', 'MN': 'Mantova',
            'MS': 'Massa-Carrara', 'MT': 'Matera', 'ME': 'Messina', 'MI': 'Milano',
            'MO': 'Modena', 'MB': 'Monza e Brianza', 'NA': 'Napoli', 'NO': 'Novara',
            'NU': 'Nuoro', 'OR': 'Oristano', 'PD': 'Padova', 'PA': 'Palermo',
            'PR': 'Parma', 'PV': 'Pavia', 'PG': 'Perugia', 'PU': 'Pesaro e Urbino',
            'PE': 'Pescara', 'PC': 'Piacenza', 'PI': 'Pisa', 'PT': 'Pistoia',
            'PN': 'Pordenone', 'PZ': 'Potenza', 'PO': 'Prato', 'RG': 'Ragusa',
            'RA': 'Ravenna', 'RC': 'Reggio Calabria', 'RE': 'Reggio Emilia',
            'RI': 'Rieti', 'RN': 'Rimini', 'RM': 'Roma', 'RO': 'Rovigo',
            'SA': 'Salerno', 'SS': 'Sassari', 'SV': 'Savona', 'SI': 'Siena',
            'SR': 'Siracusa', 'SO': 'Sondrio', 'SU': 'Sud Sardegna', 'TA': 'Taranto',
            'TE': 'Teramo', 'TR': 'Terni', 'TO': 'Torino', 'TP': 'Trapani',
            'TN': 'Trento', 'TV': 'Treviso', 'TS': 'Trieste', 'UD': 'Udine',
            'VA': 'Varese', 'VE': 'Venezia', 'VB': 'Verbano-Cusio-Ossola',
            'VC': 'Vercelli', 'VR': 'Verona', 'VV': 'Vibo Valentia',
            'VI': 'Vicenza', 'VT': 'Viterbo'
        }

    def validate_id(self, id_code: str) -> List[str]:
        """Validate the format of the ID code."""
        errors = []
        if not re.match(r'^[A-Z0-9]{10}$', id_code):
            errors.append(f"Invalid ID format: {id_code}. Should be 10 alphanumeric characters.")
        return errors

    def validate_street_address(self, address: str) -> List[str]:
        """Validate the street address format."""
        errors = []
        
        # Check if address starts with a valid street type
        if not any(address.startswith(street_type) for street_type in self.street_types):
            errors.append(f"Invalid street type in address: {address}")
        
        # Check if address contains a number
        if not re.search(r'\d', address):
            errors.append(f"Missing street number in address: {address}")
            
        # Check for common formatting issues
        if re.search(r'\s{2,}', address):
            errors.append(f"Multiple consecutive spaces found in address: {address}")
            
        return errors

    def validate_postal_code(self, postal_code: int, city: str) -> List[str]:
        """Validate the postal code format and basic rules."""
        errors = []
        
        # Convert to string for validation
        postal_str = str(postal_code)
        
        # Check length
        if len(postal_str) != 5:
            errors.append(f"Invalid postal code length for {city}: {postal_code}. Should be 5 digits.")
            
        # Check if numeric
        if not postal_str.isdigit():
            errors.append(f"Postal code contains non-numeric characters: {postal_code}")
            
        # Check for leading zeros
        if postal_str.startswith('0') and len(postal_str) < 5:
            errors.append(f"Postal code missing leading zeros: {postal_code}")
            
        return errors

    def validate_province(self, province: str, city: str) -> List[str]:
        """Validate the province code and its relationship with the city."""
        errors = []
        
        # Check if province code exists
        if province not in self.province_codes:
            errors.append(f"Invalid province code: {province}")
            
        # Future enhancement: Could add city-province relationship validation
        # Would require a complete database of Italian cities and their provinces
        
        return errors

    def validate_address(self, address_data: List[str]) -> Dict[str, List[str]]:
        """Validate all components of an address."""
        if len(address_data) != 5:
            return {"format_error": ["Address data must contain exactly 5 elements"]}
            
        id_code, street, postal_code, city, province = address_data
        
        errors = {
            "id": self.validate_id(id_code),
            "street": self.validate_street_address(street),
            "postal_code": self.validate_postal_code(int(postal_code), city),
            "province": self.validate_province(province, city)
        }
        
        return {k: v for k, v in errors.items() if v}  # Only return categories with errors

    def validate_addresses(addresses: List[List[str]]) -> Dict[int, Dict[str, List[str]]]:
        """
        Validate a list of addresses and return all found errors.
        
        Args:
            addresses: List of address lists, each containing [id, street, postal_code, city, province]
            
        Returns:
            Dictionary mapping address index to dictionary of errors by category
        """
        validator = ItalianAddressValidator()
        results = {}
        
        for idx, address in enumerate(addresses):
            errors = validator.validate_address(address)
            if errors:  # Only include addresses with errors
                results[idx] = errors
                
        return results