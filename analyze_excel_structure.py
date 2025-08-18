#!/usr/bin/env python3
"""
Script para analizar la estructura real de los archivos Excel
"""
import pandas as pd
import sys

def analyze_excel_structure(file_path):
    """Analiza la estructura de un archivo Excel"""
    print(f"Analizando archivo: {file_path}")
    print("=" * 80)
    
    try:
        # Leer el archivo Excel sin header
        df = pd.read_excel(file_path, header=None)
        
        print(f"Dimensiones del archivo: {df.shape[0]} filas x {df.shape[1]} columnas")
        print("\nPrimeras 15 filas del archivo:")
        print("-" * 80)
        
        # Mostrar las primeras 15 filas para entender la estructura
        for i in range(min(15, len(df))):
            row_data = []
            for j in range(min(10, len(df.columns))):  # Solo primeras 10 columnas
                cell_value = df.iloc[i, j]
                if pd.isna(cell_value):
                    row_data.append("NaN")
                else:
                    row_data.append(str(cell_value)[:20])  # Truncar a 20 caracteres
            print(f"Fila {i:2d}: {' | '.join(row_data)}")
        
        print("\n" + "=" * 80)
        print("ANÁLISIS DE ESTRUCTURA:")
        
        # Buscar patrones de rentabilidad
        print("\nBuscando patrones de 'rentabilidad':")
        for i in range(len(df)):
            for j in range(len(df.columns)):
                cell_value = str(df.iloc[i, j]).lower()
                if 'rentabilidad' in cell_value:
                    print(f"  Fila {i}, Col {j}: {df.iloc[i, j]}")
        
        # Buscar patrones de 'acumulada' y 'anualizada'
        print("\nBuscando patrones de 'acumulada' y 'anualizada':")
        for i in range(len(df)):
            for j in range(len(df.columns)):
                cell_value = str(df.iloc[i, j]).lower()
                if 'acumulada' in cell_value or 'anualizada' in cell_value:
                    print(f"  Fila {i}, Col {j}: {df.iloc[i, j]}")
        
        # Buscar nombres de AFPs
        print("\nBuscando nombres de AFPs:")
        afp_names = ['habitat', 'integra', 'prima', 'profuturo']
        for i in range(len(df)):
            for j in range(len(df.columns)):
                cell_value = str(df.iloc[i, j]).lower()
                for afp in afp_names:
                    if afp in cell_value:
                        print(f"  Fila {i}, Col {j}: {df.iloc[i, j]} (AFP: {afp.upper()})")
        
        # Buscar períodos (fechas)
        print("\nBuscando períodos/fechas:")
        for i in range(len(df)):
            for j in range(len(df.columns)):
                cell_value = str(df.iloc[i, j])
                if '/' in cell_value and any(char.isdigit() for char in cell_value):
                    print(f"  Fila {i}, Col {j}: {cell_value}")
        
        return df
        
    except Exception as e:
        print(f"Error analizando archivo: {e}")
        return None

def main():
    # Analizar archivo de fondo tipo 1
    file_path = "/workspace/PoC2-ClienteAltoValor/documents/Rentabilidad Acumulada y Anualizada del Fondo Tipo 1 por AFP/FP-1220-1-my2025.XLS"
    df = analyze_excel_structure(file_path)
    
    if df is not None:
        print("\n" + "=" * 80)
        print("ANÁLISIS ESPECÍFICO PARA PRIMA AFP:")
        print("=" * 80)
        
        # Buscar específicamente datos de Prima
        for i in range(len(df)):
            cell_value = str(df.iloc[i, 0]).lower()
            if 'prima' in cell_value:
                print(f"\nFila {i} (Prima AFP):")
                row_data = []
                for j in range(min(15, len(df.columns))):
                    cell_value = df.iloc[i, j]
                    if pd.isna(cell_value):
                        row_data.append("NaN")
                    else:
                        row_data.append(str(cell_value))
                print(f"  Datos: {row_data}")

if __name__ == "__main__":
    main()