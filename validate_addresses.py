import sys
import os
from poste.address_validator_it import ItalianAddressValidator as iav


# Example usage:
if __name__ == "__main__":
    # Your sample data
    addresses = [
        ['F0LC1F2J25', 'PIAZZA VITTORIA 16', 88900, 'CROTONE', 'KR'],
        ['B0BA4B2OG1', 'PIAZZA CARDINALE PANICO 4', 73039, 'TRICASE', 'LE'],
        ['F19O6F37FE', 'PIAZZA DEGLI ALPINI 7A', 31030, 'BORSO DEL GRAPPA', 'TV'],
        ['F1B41F39U1', 'PIAZZA DEL FONTANILE 14', 31, 'ARTENA', 'RM'],
        ['F1LCPF3TNS', 'PIAZZA BENIAMINO CHIATTO 2', 87100, 'COSENZA', 'CS'],
        ['F1KJ7F3SBW', 'PIAZZA FISAC 2', 22100, 'COMO', 'CO'],
        ['J0YC6J3JA2', 'PIAZZA GIACOMO LEOPARDI 12', 60012, 'TRECASTELLI', 'AN']
    ]

    results = iav.validate_addresses(addresses)

    # Print results
    if results:
        print("Found the following issues:")
        for idx, errors in results.items():
            print(f"\nAddress {idx + 1}: {addresses[idx]}")
            for category, issues in errors.items():
                print(f"  {category.upper()}:")
                for issue in issues:
                    print(f"    - {issue}")
    else:
        print("No issues found in the addresses.")
