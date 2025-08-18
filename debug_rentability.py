#!/usr/bin/env python3
"""
Script de debug para analizar el problema de rentabilidad anualizada
"""
import pandas as pd
import json
import re
import os
from typing import Dict, List, Any, Optional

def analyze_excel_structure(file_path: str):
    """Analiza la estructura de un archivo Excel"""
    print(f"\n=== ANALIZANDO: {file_path} ===")
    
    df = pd.read_excel(file_path, header=None)
    print(f"Dimensiones: {df.shape}")
    
    # Mostrar las primeras filas relevantes
    print("\nFila 4 (períodos):")
    for col in range(min(10, df.shape[1])):
        if col % 2 == 1:  # Solo columnas impares que contienen períodos
            cell_value = str(df.iloc[4, col]) if col < df.shape[1] else "N/A"
            print(f"  Col {col}: {cell_value}")
    
    print("\nFila 5 (etiquetas de años):")
    for col in range(min(10, df.shape[1])):
        if col % 2 == 1:  # Solo columnas impares
            cell_value = str(df.iloc[5, col]) if col < df.shape[1] else "N/A"
            print(f"  Col {col}: {cell_value}")
    
    print("\nFila 6 (Nominal/Real):")
    for col in range(min(10, df.shape[1])):
        cell_value = str(df.iloc[6, col]) if col < df.shape[1] else "N/A"
        print(f"  Col {col}: {cell_value}")
    
    print("\nDatos de AFPs (filas 7-10):")
    for row in range(7, min(11, df.shape[0])):
        afp_name = str(df.iloc[row, 0])
        print(f"  Fila {row}: {afp_name}")
        # Mostrar algunos valores de rentabilidad
        for col in range(1, min(6, df.shape[1])):
            value = df.iloc[row, col]
            print(f"    Col {col}: {value}")

def extract_periods_from_excel(file_path: str):
    """Extrae períodos específicamente como lo hace el código actual"""
    df = pd.read_excel(file_path, header=None)
    
    periods = []
    period_labels = []
    
    # Buscar en la fila 4 los períodos - estructura real del Excel
    for col in range(1, df.shape[1], 2):  # Cada 2 columnas (nominal y real)
        if col < df.shape[1]:
            period_cell = str(df.iloc[4, col])
            if "/" in period_cell and any(char.isdigit() for char in period_cell):
                periods.append(period_cell.strip())
                
                # Extraer la etiqueta del período de la fila 5
                if col < df.shape[1]:
                    label_cell = str(df.iloc[5, col])
                    if "año" in label_cell:
                        period_labels.append(label_cell.strip())
    
    return periods, period_labels

def extract_afp_data(file_path: str, afp_name: str):
    """Extrae datos de una AFP específica"""
    df = pd.read_excel(file_path, header=None)
    
    periods, period_labels = extract_periods_from_excel(file_path)
    
    afp_names = ["Habitat", "Integra", "Prima", "Profuturo"]
    
    for idx in range(7, min(11, len(df))):
        afp_name_cell = str(df.iloc[idx, 0])
        
        if afp_name.lower() in afp_name_cell.lower():
            afp_data = {"afp_name": afp_name, "rentability_data": {}}
            
            # Extraer datos de rentabilidad por período
            col_idx = 1
            for i, period in enumerate(periods):
                if col_idx < df.shape[1]:
                    # RENTABILIDAD NOMINAL
                    nominal_val = df.iloc[idx, col_idx]
                    if pd.notna(nominal_val) and str(nominal_val).upper() not in ['N.A.', 'NA', 'N/A']:
                        try:
                            nominal_float = float(nominal_val)
                            period_key = f"period_{i+1}_nominal"
                            afp_data["rentability_data"][period_key] = nominal_float
                            afp_data["rentability_data"][f"{period}_nominal"] = nominal_float
                            
                            if i < len(period_labels):
                                label_key = f"{period_labels[i]}_nominal"
                                afp_data["rentability_data"][label_key] = nominal_float
                        except:
                            pass
                    
                    # RENTABILIDAD REAL
                    if col_idx + 1 < df.shape[1]:
                        real_val = df.iloc[idx, col_idx + 1]
                        if pd.notna(real_val) and str(real_val).upper() not in ['N.A.', 'NA', 'N/A']:
                            try:
                                real_float = float(real_val)
                                period_key = f"period_{i+1}_real"
                                afp_data["rentability_data"][period_key] = real_float
                                afp_data["rentability_data"][f"{period}_real"] = real_float
                                
                                if i < len(period_labels):
                                    label_key = f"{period_labels[i]}_real"
                                    afp_data["rentability_data"][label_key] = real_float
                            except:
                                pass
                    
                    col_idx += 2
            
            return afp_data
    
    return None

def main():
    # Analizar archivos de diferentes fondos
    files_to_analyze = [
        "/workspace/PoC2-ClienteAltoValor/documents/Rentabilidad Acumulada y Anualizada del Fondo Tipo 1 por AFP/FP-1220-1-my2025.XLS",
        "/workspace/PoC2-ClienteAltoValor/documents/Rentabilidad Acumulada y Anualizada del Fondo Tipo 2 por AFP/FP-1360-my2025.XLS"
    ]
    
    for file_path in files_to_analyze:
        if os.path.exists(file_path):
            analyze_excel_structure(file_path)
            
            periods, period_labels = extract_periods_from_excel(file_path)
            print(f"\nPeríodos extraídos: {periods}")
            print(f"Etiquetas extraídas: {period_labels}")
            
            # Extraer datos de Prima AFP
            prima_data = extract_afp_data(file_path, "Prima")
            if prima_data:
                print(f"\nDatos de Prima AFP:")
                print(f"Claves disponibles: {list(prima_data['rentability_data'].keys())}")
                
                # Buscar datos de 5 años (mayo 2020 a mayo 2025)
                print(f"\nBuscando datos de 5 años (mayo 2020 a mayo 2025):")
                for key, value in prima_data['rentability_data'].items():
                    if "5" in key or "2020" in key:
                        print(f"  {key}: {value}")
            
            print("\n" + "="*80)

if __name__ == "__main__":
    main()