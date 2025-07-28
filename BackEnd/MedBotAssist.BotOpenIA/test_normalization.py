#!/usr/bin/env python3
"""
Script de prueba para validar la normalización de texto en búsquedas.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.database_service import normalize_text_for_search

def test_normalization():
    """Pruebas de normalización de texto"""
    
    print("🧪 Pruebas de normalización de texto para búsquedas")
    print("=" * 60)
    
    test_cases = [
        # (texto_original, texto_normalizado_esperado)
        ("Sánchez García", "sanchez garcia"),
        ("José María", "jose maria"),
        ("PÉREZ", "perez"),
        ("Ángel Rodríguez", "angel rodriguez"),
        ("María José Hernández", "maria jose hernandez"),
        ("GONZÁLEZ LÓPEZ", "gonzalez lopez"),
        ("   Espacio   Extra   ", "espacio extra"),
        ("Niño con ñ", "nino con n"),
        ("Múltiples   espacios", "multiples espacios"),
        ("", ""),  # texto vacío
    ]
    
    all_passed = True
    
    for i, (original, expected) in enumerate(test_cases, 1):
        result = normalize_text_for_search(original)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        if result != expected:
            all_passed = False
        
        print(f"{i:2d}. {status} '{original}' -> '{result}'")
        if result != expected:
            print(f"     Esperado: '{expected}'")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ Todas las pruebas pasaron correctamente!")
    else:
        print("❌ Algunas pruebas fallaron.")
    
    return all_passed

def test_search_examples():
    """Ejemplos de cómo funcionará la búsqueda"""
    
    print("\n🔍 Ejemplos de búsquedas que ahora funcionarán:")
    print("=" * 60)
    
    examples = [
        ("Usuario busca: 'sanchez'", "Encontrará: 'Sánchez García'"),
        ("Usuario busca: 'jose maria'", "Encontrará: 'José María Rodríguez'"),
        ("Usuario busca: 'PEREZ'", "Encontrará: 'Pérez López'"),
        ("Usuario busca: 'angel'", "Encontrará: 'Ángel Hernández'"),
        ("Usuario busca: 'gonzalez'", "Encontrará: 'González Martínez'"),
    ]
    
    for search, result in examples:
        print(f"• {search}")
        print(f"  → {result}")
        print()

if __name__ == "__main__":
    success = test_normalization()
    test_search_examples()
    
    if success:
        print("🎉 La normalización está lista para usar!")
    else:
        print("⚠️  Revisar la implementación de normalización.")
