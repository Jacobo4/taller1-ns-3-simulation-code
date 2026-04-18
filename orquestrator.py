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
        # 1. Zona de Estabilidad (10 puntos, saltos de 0.2 m/s)
        0.1,
        0.3,
        0.5,
        0.7,
        0.9,
        1.1,
        1.3,
        1.5,
        1.7,
        1.9,
        # 2. El Ojo del Huracán - Alta Precisión (31 puntos, saltos de 0.05 m/s)
        2.00,
        2.05,
        2.10,
        2.15,
        2.20,
        2.25,
        2.30,
        2.35,
        2.40,
        2.45,
        2.50,
        2.55,
        2.60,
        2.65,
        2.70,
        2.75,
        2.80,
        2.85,
        2.90,
        2.95,
        3.00,
        3.05,
        3.10,
        3.15,
        3.20,
        3.25,
        3.30,
        3.35,
        3.40,
        3.45,
        3.50,
        # 3. Zona de Ruptura y Valle de la Muerte (9 puntos, saltos expansivos)
        3.6,
        3.8,
        4.0,
        4.5,
        5.0,
        6.0,
        7.0,
        8.0,
        10.0,
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
