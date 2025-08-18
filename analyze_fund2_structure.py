#!/usr/bin/env python3
"""
Script para analizar la estructura del archivo de fondo tipo 2
"""
import pandas as pd

def analyze_fund2_structure():
    """Analiza la estructura del archivo de fondo tipo 2"""
    file_path = "/workspace/PoC2-ClienteAltoValor/documents/Rentabilidad Acumulada y Anualizada del Fondo Tipo 2 por AFP/FP-1360-my2025.XLS"
    
    print(f"Analizando archivo: {file_path}")
    print("=" * 80)
    
    try:
        df = pd.read_excel(file_path, header=None)
        
        print(f"Dimensiones del archivo: {df.shape[0]} filas x {df.shape[1]} columnas")
        
        # Buscar secciones de rentabilidad
        print("\nBuscando secciones de rentabilidad:")
        for i in range(min(30, len(df))):
            cell_value = str(df.iloc[i, 0]).lower()
            if 'rentabilidad' in cell_value:
                print(f"  Fila {i}: {df.iloc[i, 0]}")
        
        # Buscar AFPs en ambas secciones
        print("\nBuscando AFPs:")
        afp_names = ['habitat', 'integra', 'prima', 'profuturo']
        for i in range(len(df)):
            cell_value = str(df.iloc[i, 0]).lower()
            for afp in afp_names:
                if afp in cell_value:
                    print(f"  Fila {i}: {df.iloc[i, 0]} (AFP: {afp.upper()})")
                    # Mostrar algunos datos de esa fila
                    row_data = []
                    for j in range(min(10, len(df.columns))):
                        cell_val = df.iloc[i, j]
                        if pd.isna(cell_val):
                            row_data.append("NaN")
                        else:
                            row_data.append(str(cell_val)[:15])
                    print(f"    Datos: {row_data}")
        
        # Buscar específicamente la sección anualizada
        print("\nBuscando sección anualizada:")
        anualizada_found = False
        for i in range(len(df)):
            cell_value = str(df.iloc[i, 0]).lower()
            if 'anualizada' in cell_value:
                print(f"  Fila {i}: {df.iloc[i, 0]}")
                anualizada_found = True
                
                # Mostrar las siguientes 10 filas para ver los datos
                print(f"  Siguientes filas después de anualizada:")
                for j in range(i+1, min(i+11, len(df))):
                    row_data = []
                    for k in range(min(8, len(df.columns))):
                        cell_val = df.iloc[j, k]
                        if pd.isna(cell_val):
                            row_data.append("NaN")
                        else:
                            row_data.append(str(cell_val)[:12])
                    print(f"    Fila {j}: {row_data}")
                break
        
        if not anualizada_found:
            print("  ❌ No se encontró sección anualizada")
        
    except Exception as e:
        print(f"Error analizando archivo: {e}")

if __name__ == "__main__":
    analyze_fund2_structure()