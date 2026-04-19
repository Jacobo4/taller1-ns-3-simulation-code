import subprocess
import re
import csv
import time
import os


def ejecutar_experimento():
    print("======================================================")
    print(" INICIANDO EXPERIMENTACIÓN: AUDITORÍA DE CLÚSTERES")
    print("======================================================\n")

    tiempo_simulacion = 60.0

    # Utilizamos las velocidades que te dieron la tabla exitosa
    velocidades = [
        # --- ZONA 1: Alta Resolución en la Ventana de Estabilidad y Caída del PDR ---
        # Queremos ver milímetro a milímetro cómo el PDR pasa del 100% al 25% (0.05 a 0.40 m/s)
        0.05,
        0.08,
        0.10,
        0.12,
        0.14,
        0.16,
        0.18,
        0.20,
        0.22,
        0.24,
        0.26,
        0.28,
        0.30,
        0.32,
        0.34,
        0.36,
        0.38,
        0.40,
        0.45,
        0.50,
        # --- ZONA 2: Transición (Caída final del PDR) ---
        0.55,
        0.60,
        0.65,
        0.70,
        0.80,
        0.90,
        1.00,
        1.10,
        1.20,
        # --- ZONA 3: Alta Resolución en el Efecto Elástico (Caos de Latencia y AODV) ---
        # Aquí buscamos atrapar exactamente en qué decimal ocurren los picos de latencia (1.30 a 3.00 m/s)
        1.30,
        1.40,
        1.50,
        1.60,
        1.70,
        1.80,
        1.90,
        2.00,
        2.10,
        2.20,
        2.30,
        2.40,
        2.60,
        2.80,
        3.00,
        # --- ZONA 4: La Cola Larga (Ruptura Total) ---
        # Pasos muy amplios solo para demostrar que la red no resucita mágicamente
        3.50,
        4.00,
        4.50,
        5.00,
        6.00,
        7.00,
        8.00,
        9.00,
        10.00,
        12.00,
    ]

    resultados_globales = []
    resultados_clusteres = []  # Nueva lista para la tabla de carga

    ruta_trazas = "results/trazas_manet.tr"

    for velocidad in velocidades:
        print(f"[*] Ejecutando escenario con Macro-velocidad = {velocidad} m/s...")

        comando = f'../../ns3 run "scratch/taller1-ns-3-simulation-code/main.cc --simTime={tiempo_simulacion} --macroSpeed={velocidad}"'

        inicio_tiempo = time.time()
        proceso = subprocess.run(
            comando,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        fin_tiempo = time.time()

        salida_consola = proceso.stdout
        tiempo_ejecucion = round(fin_tiempo - inicio_tiempo, 2)

        if tiempo_ejecucion < 0.5:
            print(f"    [!] ERROR CRÍTICO: El simulador no arrancó. Abortando.")
            return

        # 1. Extracción de Datos Generales
        pdr_match = re.search(
            r"Packet Delivery Ratio \(PDR\):\s+([\d\.]+)%", salida_consola
        )
        delay_match = re.search(
            r"Latencia Promedio \(Delay\):\s+([\d\.]+)\s+ms", salida_consola
        )

        pdr = float(pdr_match.group(1)) if pdr_match else 0.0
        delay = float(delay_match.group(1)) if delay_match else 0.0

        # Variables de recolección
        paquetes_udp = 0
        paquetes_aodv = 0
        aodv_a = 0
        aodv_b = 0
        aodv_c = 0

        if os.path.exists(ruta_trazas):
            # Tráfico General
            cmd_udp = (
                f'grep "^t" {ruta_trazas} | grep -i "udp" | grep -v -i "aodv" | wc -l'
            )
            paquetes_udp = int(
                subprocess.run(
                    cmd_udp, shell=True, capture_output=True, text=True
                ).stdout.strip()
                or 0
            )

            cmd_aodv = f'grep "^t" {ruta_trazas} | grep -i "aodv" | wc -l'
            paquetes_aodv = int(
                subprocess.run(
                    cmd_aodv, shell=True, capture_output=True, text=True
                ).stdout.strip()
                or 0
            )

            # 2. AUDITORÍA POR CLÚSTER (Expresiones Regulares por Rango de Nodos)
            # Clúster A (Nodos 0 al 4)
            cmd_a = f'grep "^t" {ruta_trazas} | grep -i "aodv" | grep -E "/NodeList/[0-4]/" | wc -l'
            aodv_a = int(
                subprocess.run(
                    cmd_a, shell=True, capture_output=True, text=True
                ).stdout.strip()
                or 0
            )

            # Clúster B (Nodos 5 al 9) - EL PUENTE
            cmd_b = f'grep "^t" {ruta_trazas} | grep -i "aodv" | grep -E "/NodeList/[5-9]/" | wc -l'
            aodv_b = int(
                subprocess.run(
                    cmd_b, shell=True, capture_output=True, text=True
                ).stdout.strip()
                or 0
            )

            # Clúster C (Nodos 10 al 14)
            cmd_c = f'grep "^t" {ruta_trazas} | grep -i "aodv" | grep -E "/NodeList/1[0-4]/" | wc -l'
            aodv_c = int(
                subprocess.run(
                    cmd_c, shell=True, capture_output=True, text=True
                ).stdout.strip()
                or 0
            )

        distancia_final = 30.0 + (2 * velocidad * tiempo_simulacion)

        print(
            f"    -> Fin en {tiempo_ejecucion}s | PDR: {pdr}% | AODV Total: {paquetes_aodv} [A:{aodv_a} | B:{aodv_b} | C:{aodv_c}]"
        )

        # Guardar en Tabla Principal
        resultados_globales.append(
            {
                "Velocidad_m_s": velocidad,
                "Distancia_Final_m": distancia_final,
                "PDR_Porcentaje": pdr,
                "Latencia_ms": delay,
                "Paquetes_Datos_UDP": paquetes_udp,
                "Paquetes_Control_AODV_Total": paquetes_aodv,
            }
        )

        # Guardar en Tabla de Carga de Clústeres
        resultados_clusteres.append(
            {
                "Velocidad_m_s": velocidad,
                "Distancia_Final_m": distancia_final,
                "AODV_Cluster_A_Origen": aodv_a,
                "AODV_Cluster_B_Puente": aodv_b,
                "AODV_Cluster_C_Destino": aodv_c,
            }
        )

    # Exportar Tabla Principal
    csv_principal = "results/resultados_simulacion.csv"
    with open(csv_principal, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=resultados_globales[0].keys())
        writer.writeheader()
        writer.writerows(resultados_globales)

    # Exportar Tabla de Clústeres
    csv_clusteres = "results/resultados_carga_clusteres.csv"
    with open(csv_clusteres, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=resultados_clusteres[0].keys())
        writer.writeheader()
        writer.writerows(resultados_clusteres)

    print(f"\n[+] Experimentación finalizada.")
    print(f"    1. Tabla General guardada en: {csv_principal}")
    print(f"    2. Tabla de Carga guardada en: {csv_clusteres}")


if __name__ == "__main__":
    ejecutar_experimento()
