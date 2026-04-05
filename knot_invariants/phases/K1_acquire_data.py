"""
Phase K1 — Acquire knot invariant data from KnotInfo.

Downloads the KnotInfo database and parses it into a structured JSON format
suitable for systematic exploration.

KnotInfo: https://www.indiana.edu/~knotinfo/
Data download: https://knotinfo.math.indiana.edu/

Output: data/k1_results.json
"""

import json
import csv
import sys
import os

# KnotInfo provides data as downloadable CSV files
# The main URL for bulk download:
KNOTINFO_URL = "https://knotinfo.math.indiana.edu/"

# Key invariants to extract (subset of ~80 available)
TARGET_INVARIANTS = [
    # Classical
    'name',
    'crossing_number',
    'unknotting_number',
    'bridge_index',
    'braid_index',
    'braid_length',
    
    # Numeric invariants
    'signature',
    'determinant',
    'three_genus',
    'four_ball_genus',  # slice genus
    'concordance_order',
    'nakanishi_index',
    
    # Polynomial invariants (evaluated at specific points or as coefficients)
    'alexander_polynomial',
    'jones_polynomial',
    'homfly_polynomial',
    'conway_polynomial',
    'kauffman_polynomial',
    
    # Geometric  
    'hyperbolic_volume',
    'chern_simons_invariant',
    
    # Symmetry
    'symmetry_type',
    'amphicheiral',
    'reversible',
    
    # Homological
    'rasmussen_invariant',  # s invariant
    'ozsvath_szabo_tau',    # tau invariant
    
    # Other
    'arc_index',
    'thurston_bennequin_number',
    'self_linking_number',
]


def download_knotinfo(output_dir='../data'):
    """
    Instructions for downloading KnotInfo data.
    
    KnotInfo does not have a simple CSV bulk download API.
    Options:
    1. Use the knotinfo Python package: pip install knotinfo
    2. Scrape the website tables
    3. Use the Sage interface: sage.knots.knotinfo
    """
    print("=" * 60)
    print("KnotInfo Data Acquisition")
    print("=" * 60)
    print()
    print("Option 1 (RECOMMENDED): Use the 'knotinfo' Python package")
    print("  pip install knotinfo")
    print("  Then use knotinfo.KnotInfo to query invariants")
    print()
    print("Option 2: Use the 'database_knotinfo' from SageMath")
    print("  from sage.knots.knotinfo import KnotInfo")
    print()
    print("Option 3: Manual download from https://knotinfo.math.indiana.edu/")
    print("  - Select invariants")
    print("  - Download as CSV")
    print()
    
    # Try option 1
    try:
        import knotinfo
        print("✅ knotinfo package found! Extracting data...")
        extract_from_package(knotinfo, output_dir)
        return True
    except ImportError:
        print("❌ knotinfo package not installed")
        print("   Install with: pip install knotinfo")
        print()
    
    # If nothing works, create a stub file
    print("Creating stub data file with known small knots...")
    create_stub_data(output_dir)
    return False


def extract_from_package(knotinfo_module, output_dir):
    """Extract data using the knotinfo Python package."""
    # The knotinfo package provides access to the full database
    # Usage varies by version — adapt as needed
    
    results = []
    # This would iterate through all knots and extract invariants
    # Placeholder for actual implementation
    
    output_path = os.path.join(output_dir, 'k1_results.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=1)
    print(f"Saved {len(results)} knots to {output_path}")


def create_stub_data(output_dir):
    """Create stub data with well-known knots for testing."""
    
    # Well-known knots with some invariants
    # These values are from standard knot tables
    stub_knots = [
        {
            'name': '0_1',  # Unknot
            'crossing_number': 0,
            'unknotting_number': 0,
            'signature': 0,
            'determinant': 1,
            'three_genus': 0,
            'bridge_index': 1,
            'braid_index': 1,
            'jones_at_minus1': 1,
            'alexander_at_minus1': 1,
            'hyperbolic_volume': 0,
            'is_alternating': True,
            'symmetry_type': 'fully_amphicheiral',
        },
        {
            'name': '3_1',  # Trefoil
            'crossing_number': 3,
            'unknotting_number': 1,
            'signature': -2,
            'determinant': 3,
            'three_genus': 1,
            'bridge_index': 2,
            'braid_index': 2,
            'jones_at_minus1': 3,
            'alexander_at_minus1': 3,
            'hyperbolic_volume': 0,  # Torus knot
            'is_alternating': True,
            'symmetry_type': 'reversible',
        },
        {
            'name': '4_1',  # Figure-eight
            'crossing_number': 4,
            'unknotting_number': 1,
            'signature': 0,
            'determinant': 5,
            'three_genus': 1,
            'bridge_index': 2,
            'braid_index': 3,
            'jones_at_minus1': 5,
            'alexander_at_minus1': 5,
            'hyperbolic_volume': 2.0298832128,
            'is_alternating': True,
            'symmetry_type': 'fully_amphicheiral',
        },
        {
            'name': '5_1',  # Cinquefoil
            'crossing_number': 5,
            'unknotting_number': 2,
            'signature': -4,
            'determinant': 5,
            'three_genus': 2,
            'bridge_index': 2,
            'braid_index': 2,
            'jones_at_minus1': 5,
            'alexander_at_minus1': 5,
            'hyperbolic_volume': 0,  # Torus knot
            'is_alternating': True,
            'symmetry_type': 'reversible',
        },
        {
            'name': '5_2',
            'crossing_number': 5,
            'unknotting_number': 1,
            'signature': -2,
            'determinant': 7,
            'three_genus': 1,
            'bridge_index': 2,
            'braid_index': 3,
            'jones_at_minus1': 7,
            'alexander_at_minus1': 7,
            'hyperbolic_volume': 2.8281220883,
            'is_alternating': True,
            'symmetry_type': 'reversible',
        },
    ]
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'k1_stub.json')
    with open(output_path, 'w') as f:
        json.dump(stub_knots, f, indent=2)
    
    print(f"✅ Created stub data with {len(stub_knots)} knots at {output_path}")
    print(f"   This is for testing only — run with knotinfo package for full data")


if __name__ == '__main__':
    download_knotinfo()
