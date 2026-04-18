# Reporte Técnico: Simulación del "Efecto Elástico" en Redes MANET Jerárquicas

## 1. Contexto y Objetivo
Se investigó el comportamiento de una red móvil ad-hoc (**MANET**) con estructura jerárquica (clústeres) bajo condiciones de movilidad macroscópica. El objetivo principal fue validar el **"Efecto Elástico"**: el fenómeno donde el protocolo de enrutamiento genera una sobrecarga crítica de control intentando mantener enlaces que están a punto de romperse físicamente por la distancia.

## 2. Hipótesis Definidas
*   **H1 (Latencia):** Existe un incremento súbito en el retardo extremo a extremo justo antes de la ruptura total del enlace (umbral de cobertura).
*   **H2 (Costo de Enrutamiento/Overhead):** La sobrecarga del protocolo (AODV) aumenta exponencialmente en la zona crítica, compitiendo con el tráfico de datos.
*   **H3 (Ventana de Estabilidad):** El PDR (*Packet Delivery Ratio*) decae logarítmicamente respecto a la velocidad de separación, identificando un "punto de no retorno" físico.

## 3. Configuración Técnica (NS-3.47)
*   **Topología:** 15 nodos divididos en 3 clústeres (A, B y C).
*   **Protocolo de Enrutamiento:** AODV (*Ad hoc On-Demand Distance Vector*).
*   **Modelos de Movilidad:**
    *   **Micro-movilidad:** `RandomWalk2d` dentro de cada clúster.
    *   **Macro-movilidad:** `ConstantVelocity` para separar los clústeres a velocidades variables (0.5 m/s a 10.0 m/s).
*   **Tráfico:** Aplicación UDP Echo (Llamada de voz simulada) a 20 paquetes/segundo entre el Nodo 0 y el Nodo 10.
*   **Potencia de Antena:** Calibrada para un rango efectivo de ~150-250 metros.

## 4. Metodología de Experimentación
Se utilizó un Orquestador en Python para automatizar 18 escenarios de simulación.

*   **Control de Semilla:** Uso de `--RngRun` para garantizar que la aleatoriedad de los nodos fuera consistente en cada prueba (**Determinismo Científico**).
*   **Extracción de Datos:** Combinación de `FlowMonitor` (para PDR y Latencia) y análisis de archivos `.tr` mediante `grep` para diferenciar paquetes de datos (UDP) versus paquetes de control (AODV).

## 5. Resultados y Análisis de la "Zona Crítica"
Los datos revelaron que el punto de mayor estrés de la red ocurre a los **2.2 m/s** (aprox. 294 metros de separación):

*   **Colapso de AODV:** En este punto, los paquetes de control alcanzaron su pico (1117 mensajes) mientras que la entrega de voz cayó a su nivel más bajo antes de la ruptura.
*   **Gritar al Vacío:** A velocidades extremas (>6.0 m/s), la red registra 0% de PDR, pero el origen sigue intentando transmitir (1141 paquetes UDP generados), lo que demuestra el desperdicio de recursos (batería/ancho de banda) en nodos aislados.
