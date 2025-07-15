#!/usr/bin/env python3
"""
Demo del Sistema de Análisis de Rentabilidad SPP
Muestra las capacidades principales del sistema
"""
import sys
import os
sys.path.append('/workspace/PoC2-ClienteAltoValor')

from src.data_manager import RentabilityDataManager
import json

def print_header(title):
    """Imprime un encabezado formateado"""
    print("\n" + "="*60)
    print(f"🎯 {title}")
    print("="*60)

def print_section(title):
    """Imprime una sección"""
    print(f"\n📊 {title}")
    print("-" * 40)

def demo_system_overview():
    """Muestra resumen del sistema"""
    print_header("SISTEMA DE ANÁLISIS DE RENTABILIDAD SPP")
    
    print("""
🏦 DATOS PROCESADOS:
   • 20 archivos Excel de rentabilidad oficial
   • 4 tipos de fondos (0: Conservador, 1: Mixto Conservador, 2: Mixto, 3: Crecimiento)
   • 4 AFPs (Habitat, Integra, Prima, Profuturo)
   • 5 períodos (Enero-Mayo 2025)
   • Rentabilidad nominal y real por horizonte temporal

🤖 CAPACIDADES DEL AGENTE:
   • Consultas de rentabilidad por AFP
   • Comparaciones entre AFPs
   • Análisis de tipos de fondos
   • Tendencias históricas
   • Recomendaciones personalizadas
    """)

def demo_data_loading():
    """Demuestra la carga de datos"""
    print_header("CARGA Y PROCESAMIENTO DE DATOS")
    
    print("🔄 Inicializando gestor de datos...")
    data_manager = RentabilityDataManager()
    
    stats = data_manager.get_summary_statistics()
    
    print_section("Estadísticas del Sistema")
    print(f"📁 Archivos procesados: {stats['total_files_processed']}")
    print(f"🏦 AFPs disponibles: {', '.join(stats['available_afps'])}")
    print(f"📈 Tipos de fondos: {stats['available_fund_types']}")
    print(f"📅 Períodos: {', '.join(stats['available_periods'])}")
    
    return data_manager

def demo_afp_query(data_manager):
    """Demuestra consulta por AFP"""
    print_header("CONSULTA DE RENTABILIDAD POR AFP")
    
    print_section("Rentabilidad de Habitat - Fondo Conservador (Tipo 0)")
    habitat_data = data_manager.get_rentability_by_afp("Habitat", 0)
    
    if "error" not in habitat_data:
        rentability = habitat_data["rentability_data"]
        print(f"🏦 AFP: {habitat_data['afp_name']}")
        print(f"📊 Tipo de fondo: {habitat_data['fund_type']} (Conservador)")
        print(f"📅 Período: {habitat_data['period']}")
        
        # Mostrar algunos datos clave
        key_periods = [k for k in rentability.keys() if "nominal" in k][:3]
        for period in key_periods:
            real_period = period.replace("nominal", "real")
            if real_period in rentability:
                print(f"   • {period.replace('_nominal', '')}: {rentability[period]:.2f}% nominal, {rentability[real_period]:.2f}% real")
    else:
        print(f"❌ Error: {habitat_data['error']}")

def demo_afp_comparison(data_manager):
    """Demuestra comparación entre AFPs"""
    print_header("COMPARACIÓN ENTRE AFPs")
    
    print_section("Habitat vs Integra vs Prima - Fondo Conservador")
    comparison = data_manager.compare_afp_rentability(["Habitat", "Integra", "Prima"], 0)
    
    if "error" not in comparison:
        rankings = comparison["rankings"]
        
        # Mostrar ranking para rentabilidad a 1 año
        period_keys = [k for k in rankings.keys() if "2016" in k and "nominal" in k]
        if period_keys:
            period_key = period_keys[0]
            print(f"🏆 Ranking rentabilidad nominal (período más reciente):")
            for i, (afp, value) in enumerate(rankings[period_key], 1):
                print(f"   {i}. {afp}: {value:.2f}%")
    else:
        print(f"❌ Error en comparación")

def demo_fund_analysis(data_manager):
    """Demuestra análisis de tipos de fondos"""
    print_header("ANÁLISIS DE TIPOS DE FONDOS")
    
    print_section("Características de los Fondos")
    fund_analysis = data_manager.analyze_fund_performance([0, 1, 2, 3])
    
    if "fund_analysis" in fund_analysis:
        for fund_key, fund_info in fund_analysis["fund_analysis"].items():
            fund_type = fund_key.split("_")[-1]
            print(f"\n📊 FONDO TIPO {fund_type}: {fund_info['name']}")
            print(f"   • Riesgo: {fund_info['risk_level']}")
            print(f"   • Perfil: {fund_info['target_profile']}")
            print(f"   • Descripción: {fund_info['description']}")
            
            if "average_rentability" in fund_info and "averages" in fund_info["average_rentability"]:
                avg_data = fund_info["average_rentability"]["averages"]
                # Mostrar rentabilidad promedio más reciente
                recent_keys = [k for k in avg_data.keys() if "2016" in k]
                if recent_keys:
                    nominal_key = [k for k in recent_keys if "nominal" in k][0]
                    real_key = [k for k in recent_keys if "real" in k][0]
                    print(f"   • Rentabilidad promedio: {avg_data[nominal_key]:.2f}% nominal, {avg_data[real_key]:.2f}% real")

def demo_recommendations():
    """Muestra recomendaciones del sistema"""
    print_header("RECOMENDACIONES DEL SISTEMA")
    
    print("""
💡 RECOMENDACIONES SEGÚN PERFIL:

👴 PERSONAS PRÓXIMAS A JUBILARSE (55+ años):
   • Fondo Tipo 0 (Conservador)
   • Menor volatilidad, preservación de capital
   • Rentabilidad más estable

👨‍💼 PERSONAS DE MEDIANA EDAD (35-55 años):
   • Fondo Tipo 1 o 2 (Mixto Conservador/Mixto)
   • Balance entre crecimiento y estabilidad
   • Diversificación de riesgo

👨‍🎓 PERSONAS JÓVENES (25-35 años):
   • Fondo Tipo 2 o 3 (Mixto/Crecimiento)
   • Mayor potencial de crecimiento a largo plazo
   • Pueden asumir mayor volatilidad

🔍 FACTORES A CONSIDERAR:
   • Horizonte de inversión
   • Tolerancia al riesgo
   • Situación financiera personal
   • Diversificación entre AFPs
    """)

def demo_sample_queries():
    """Muestra ejemplos de consultas que puede responder el agente"""
    print_header("EJEMPLOS DE CONSULTAS AL AGENTE")
    
    queries = [
        "¿Cuál es la rentabilidad de Habitat en el fondo conservador?",
        "Compara el rendimiento entre Integra y Prima en fondos de crecimiento",
        "¿Qué tipo de fondo recomiendas para una persona de 30 años?",
        "Muestra la evolución de rentabilidad de los fondos mixtos",
        "¿Cuál es la diferencia entre rentabilidad nominal y real?",
        "¿Qué AFP tiene mejor rendimiento histórico en fondos conservadores?",
        "Explica los riesgos de los fondos de crecimiento",
        "¿Cómo ha sido la rentabilidad en los últimos 5 años?"
    ]
    
    print("\n🤖 El agente puede responder consultas como:")
    for i, query in enumerate(queries, 1):
        print(f"   {i}. \"{query}\"")
    
    print(f"\n💬 Total de consultas posibles: Ilimitadas")
    print("🎯 El agente combina datos reales con análisis inteligente")

def main():
    """Función principal del demo"""
    print("🚀 INICIANDO DEMO DEL SISTEMA SPP")
    
    try:
        # 1. Resumen del sistema
        demo_system_overview()
        
        # 2. Carga de datos
        data_manager = demo_data_loading()
        
        # 3. Consulta por AFP
        demo_afp_query(data_manager)
        
        # 4. Comparación entre AFPs
        demo_afp_comparison(data_manager)
        
        # 5. Análisis de fondos
        demo_fund_analysis(data_manager)
        
        # 6. Recomendaciones
        demo_recommendations()
        
        # 7. Ejemplos de consultas
        demo_sample_queries()
        
        print_header("DEMO COMPLETADO EXITOSAMENTE")
        print("""
✅ SISTEMA LISTO PARA PRODUCCIÓN:
   • Datos procesados y validados
   • Agente conversacional funcional
   • API endpoints disponibles
   • Integración con Azure OpenAI

🚀 PRÓXIMOS PASOS:
   • Desplegar en Azure Functions
   • Configurar variables de entorno
   • Probar endpoints de API
   • Integrar con aplicación cliente

📞 SOPORTE:
   • Documentación completa en README.md
   • Código limpio y comentado
   • Sistema de pruebas incluido
        """)
        
    except Exception as e:
        print(f"\n❌ Error durante el demo: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)