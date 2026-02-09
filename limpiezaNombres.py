import pandas as pd
from thefuzz import process
import sys

# --- CONFIGURACIÓN ---
FILE_PARTIDOS = "data/2024.xlsx"
FILE_RANKING = "data/Ranking_ATP_2024.xlsx"
UMBRAL_SUGERENCIA = 50  # Solo te sugerirá si la similitud es mayor a esto

def main():
    print("📂 Cargando archivos...")
    try:
        df_partidos = pd.read_excel(FILE_PARTIDOS)
        df_ranking = pd.read_excel(FILE_RANKING)
    except FileNotFoundError:
        print("❌ Error: No encuentro los archivos excel en la carpeta data/")
        return

    # 1. Definimos quién es el MASTER y quién es el SUCIO
    
    # MASTER: Los nombres que aparecen en los partidos (Winner y Loser)
    # Usamos set para eliminar duplicados y unimos ambas columnas
    nombres_master = set(df_partidos['Winner'].dropna().unique()) | set(df_partidos['Loser'].dropna().unique())
    
    # A CORREGIR: Los nombres del Ranking
    columna_ranking = 'Player' if 'Player' in df_ranking.columns else 'Jugador'
    nombres_a_corregir = df_ranking[columna_ranking].dropna().unique().tolist()
    
    print(f"📊 MASTER (Partidos): {len(nombres_master)} jugadores únicos.")
    print(f"🎯 A CORREGIR (Ranking): {len(nombres_a_corregir)} jugadores.")
    print("-" * 60)
    print("🚀 INICIANDO PROCESO DE VALIDACIÓN MANUAL")
    print("   Objetivo: Cambiar nombre de RANKING para que coincida con PARTIDOS.")
    print("   NOTA: Si el jugador del ranking NO jugó partidos, rechaza el cambio ('n').")
    print("-" * 60)

    cambios = {} # Diccionario {Nombre_Ranking_Original : Nombre_Partidos_Master}

    # 2. Iteramos sobre los nombres del RANKING
    for i, nombre_sucio in enumerate(nombres_a_corregir):
        
        # Si el nombre del ranking YA EXISTE en los partidos, está perfecto. Saltamos.
        if nombre_sucio in nombres_master:
            continue

        # Buscamos el nombre más parecido dentro de la lista de PARTIDOS
        # Esto busca "Cuál de los que jugaron se parece a este del ranking"
        match_result = process.extractOne(nombre_sucio, nombres_master)
        
        # Si no encuentra nada (lista vacía) o falla
        if match_result is None:
            continue
            
        mejor_match, puntaje = match_result

        # Si el puntaje es muy bajo, avisamos
        if puntaje < UMBRAL_SUGERENCIA:
            # Opcional: Descomentar si quieres revisar casos muy difíciles, 
            # pero dado que el ranking es enorme, mejor saltar los irrelevantes.
            # print(f"⚠️  Baja similitud: Ranking '{nombre_sucio}' vs Partidos '{mejor_match}' ({puntaje}%)")
            continue 

        # PREGUNTA AL USUARIO
        print(f"\n[{i}/{len(nombres_a_corregir)}] Ranking: '{nombre_sucio}'  --->  Partidos: '{mejor_match}' (Score: {puntaje}%)")
        respuesta = input("   [Enter = Sí] / [n = No] / [Escribe manual]: ").strip()

        if respuesta == "" or respuesta.lower() == 'y':
            # Aceptamos el cambio: En el ranking pondremos el nombre del partido
            cambios[nombre_sucio] = mejor_match
            print("   ✅ Cambio aceptado.")
        
        elif respuesta.lower() == 'n':
            print("   ❌ Cambio rechazado.")
        
        else:
            # Cambio manual
            cambios[nombre_sucio] = respuesta
            print(f"   ✏️  Guardado cambio manual: {respuesta}")

    # 3. Aplicamos los cambios SOLAMENTE AL RANKING
    print("\n" + "="*60)
    print(f"🔄 Aplicando {len(cambios)} correcciones al DataFrame de Ranking...")
    
    if cambios:
        df_ranking[columna_ranking] = df_ranking[columna_ranking].replace(cambios)

   # 4. Guardamos en EXCEL (Más compatible y fácil de leer)
    print("💾 Guardando archivos en formato EXCEL...")
    
    # Cambia .to_parquet por .to_excel
    df_partidos.to_excel("data/partidos_clean.xlsx", index=False)
    df_ranking.to_excel("data/ranking_clean.xlsx", index=False)

    print("✅ ¡LISTO! Archivos .xlsx creados.")

if __name__ == "__main__":
    main()