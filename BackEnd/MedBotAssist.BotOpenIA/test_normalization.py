#!/usr/bin/env python3
"""
Test script to validate text normalization in searches.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.database_service import normalize_text_for_search

def test_normalization():
    """Text normalization tests"""
    
    print("🧪 Text normalization tests for searches")
    print("=" * 60)
    
    test_cases = [
        # (original_text, expected_normalized_text)
        ("Sánchez García", "sanchez garcia"),
        ("José María", "jose maria"),
        ("PÉREZ", "perez"),
        ("Ángel Rodríguez", "angel rodriguez"),
        ("María José Hernández", "maria jose hernandez"),
        ("GONZÁLEZ LÓPEZ", "gonzalez lopez"),
        ("   Extra   Space   ", "extra space"),
        ("Niño con ñ", "nino con n"),
        ("Multiple   spaces", "multiple spaces"),
        ("", ""),  # empty text
    ]
    
    all_passed = True
    
    for i, (original, expected) in enumerate(test_cases, 1):
        result = normalize_text_for_search(original)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        if result != expected:
            all_passed = False
        
        print(f"{i:2d}. {status} '{original}' -> '{result}'")
        if result != expected:
            print(f"     Expected: '{expected}'")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed correctly!")
    else:
        print("❌ Some tests failed.")
    
    return all_passed

def test_search_examples():
    """Examples of how searches will work"""
    
    print("\n🔍 Examples of searches that will now work:")
    print("=" * 60)
    
    examples = [
        ("User searches: 'sanchez'", "Will find: 'Sánchez García'"),
        ("User searches: 'jose maria'", "Will find: 'José María Rodríguez'"),
        ("User searches: 'PEREZ'", "Will find: 'Pérez López'"),
        ("User searches: 'angel'", "Will find: 'Ángel Hernández'"),
        ("User searches: 'gonzalez'", "Will find: 'González Martínez'"),
    ]
    
    for search, result in examples:
        print(f"• {search}")
        print(f"  → {result}")
        print()

if __name__ == "__main__":
    success = test_normalization()
    test_search_examples()
    
    if success:
        print("🎉 Normalization is ready to use!")
    else:
        print("⚠️  Need to review normalization implementation.")
