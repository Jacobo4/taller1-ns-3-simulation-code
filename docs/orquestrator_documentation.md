# Documentación Técnica: `orquestrator.py`

Este documento detalla las funciones, variables y el flujo de trabajo del script de Python encargado de automatizar las simulaciones y procesar los resultados.

## 1. Funciones

### `ejecutar_experimento()`

- **Propósito:** Función principal que actúa como motor de la experimentación. Controla el ciclo de vida de cada prueba, desde la ejecución en NS-3 hasta la extracción de métricas mediante análisis de archivos.
- **Acciones:**
  1.  Itera sobre una lista predefinida de velocidades.
  2.  Ejecuta el comando de shell para correr `main.cc` con parámetros específicos.
  3.  Captura la salida de la consola (stdout).
  4.  Analiza el archivo de trazas `.tr` usando comandos `grep` de Linux.
  5.  Calcula distancias teóricas y organiza los datos en diccionarios.
  6.  Exporta los resultados consolidados a archivos CSV.

---

## 2. Diferenciación: Variables vs. Constantes

### 2.1 Parámetros de la Experimentación (Dinámicos)

Estas variables definen el diseño experimental y pueden ser ajustadas para cambiar el alcance de las pruebas:

| Variable            | Tipo    | Descripción                                                                                                                          |
| :------------------ | :------ | :----------------------------------------------------------------------------------------------------------------------------------- |
| `velocidades`       | `list`  | El conjunto de puntos de datos a probar. Dividido en: Zona de estabilidad, El Ojo del Huracán (alta precisión) y Valle de la Muerte. |
| `tiempo_simulacion` | `float` | Fijado en 60.0, pero actúa como el parámetro base para el cálculo de distancia y duración de la prueba.                              |

### 2.2 Variables de Proceso y Estado

Variables que cambian durante el bucle de ejecución:

- **Métricas de Rendimiento:** `pdr` (Packet Delivery Ratio) y `delay` (Latencia). Extraídas por Regex de la consola.
- **Contadores de Tráfico:** `paquetes_udp`, `paquetes_aodv`, `aodv_a`, `aodv_b`, `aodv_c`. Almacenan el conteo de paquetes filtrados.
- **Temporizadores:** `inicio_tiempo`, `fin_tiempo`, `tiempo_ejecucion`. Monitorean el rendimiento del simulador mismo.
- **Distancia:** `distancia_final`. Calculada como: $30.0 + (2 \times velocidad \times tiempo)$.

### 2.3 Constantes Estructurales (Fijas)

Valores que no deben cambiar a menos que se modifique la arquitectura del proyecto:

- **Rutas de Archivos:** `results/trazas_manet.tr`, `results/resultados_simulacion.csv`, `results/resultados_carga_clusteres.csv`.
- **Rangos de Nodos (Lógica de Grep):**
  - Cluster A: `[0-4]`
  - Cluster B: `[5-9]`
  - Cluster C: `1[0-4]` (Nodos 10-14).
- **Comando Base:** El path relativo al binario de ns3 (`../../ns3 run`).

---

## 3. Flujo de Trabajo del Orquestador

El script opera como una capa de abstracción sobre NS-3 siguiendo este orden:

1.  **Preparación de Contenedores:** Se inicializan las listas `resultados_globales` y `resultados_clusteres`.
2.  **Bucle de Simulación:** Por cada velocidad en la lista:
    - **Ejecución:** Se lanza el proceso NS-3 y se espera a que termine.
    - **Extracción Primaria:** Se usa Regex (`re.search`) sobre la salida de consola para obtener PDR y Latencia.
    - **Extracción Secundaria (Post-procesamiento):** Se ejecutan comandos `grep` directamente sobre el archivo `trazas_manet.tr` para contar paquetes de control (AODV) por clúster.
    - **Cálculo de Distancia:** Se determina la separación física final alcanzada.
3.  **Consolidación de Datos:** Los datos se estructuran en filas de diccionario.
4.  **Exportación Final:** Se generan dos reportes CSV:
    - `resultados_simulacion.csv`: Métricas generales de red.
    - `resultados_carga_clusteres.csv`: Desglose del overhead de enrutamiento por zona geográfica.
