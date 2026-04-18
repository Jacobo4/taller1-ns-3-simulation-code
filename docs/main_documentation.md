# Documentación Técnica: `main.cc`

Este documento detalla las funciones, variables y el flujo de trabajo del programa principal de simulación NS-3 para el análisis del "Efecto Elástico" en redes MANET.

## 1. Funciones

### `SetupEnvironment`

- **Propósito:** Configura los parámetros iniciales de la simulación y el sistema de logs.
- **Parámetros:**
  - `int argc, char* argv[]`: Argumentos de línea de comandos.
  - `double& simTime`: Referencia para establecer el tiempo total de simulación.
  - `double& macroSpeed`: Referencia para establecer la velocidad de separación de los clústeres.
- **Acciones:** Define comandos de consola (`--simTime`, `--macroSpeed`), establece la resolución temporal a nanosegundos y habilita logs para aplicaciones UDP Echo.

### `CreateNodes`

- **Propósito:** Instancia los nodos de la red y los organiza en grupos lógicos.
- **Parámetros:**
  - `NodeContainer& allNodes`: Contenedor principal para los 15 nodos.
  - `NodeContainer& clusterA, clusterB, clusterC`: Contenedores para agrupar nodos en sub-clústeres.
- **Acciones:** Crea 15 nodos y los divide en 3 grupos de 5 (A: 0-4, B: 5-9, C: 10-14).

### `ConfigureWifi`

- **Propósito:** Configura la capa física (PHY) y de acceso al medio (MAC) usando el estándar 802.11b.
- **Parámetros:**
  - `NodeContainer& allNodes`: Nodos donde se instalará el hardware Wi-Fi.
  - `NetDeviceContainer& devices`: Contenedor para almacenar los dispositivos de red creados.
- **Acciones:** Configura el modo `AdhocWifiMac`, establece el canal inalámbrico y define el gestor de tasa constante (`ConstantRateWifiManager`). También habilita la generación de trazas ASCII en `results/trazas_manet.tr`.

### `ConfigureInternet`

- **Propósito:** Instala la pila de protocolos de red y el protocolo de enrutamiento.
- **Parámetros:**
  - `NodeContainer& allNodes`: Nodos donde se instalará la pila.
  - `NetDeviceContainer& devices`: Dispositivos a los que se asignarán IPs.
  - `Ipv4InterfaceContainer& interfaces`: Contenedor para las interfaces IP resultantes.
- **Acciones:** Instala el protocolo **AODV** como motor de enrutamiento, asigna la base de red `10.1.1.0/24` y vincula direcciones IP a los dispositivos.

### `ConfigureMobility`

- **Propósito:** Implementa el modelo de movilidad jerárquica (macro + micro).
- **Parámetros:**
  - `NodeContainer& clusterA, clusterB, clusterC`: Grupos de nodos a los que aplicar movilidad.
  - `double macroSpeed`: Velocidad de separación de los super-clústeres.
- **Acciones:**
  - Crea dos "nodos padre" invisibles (`parentX`, `parentY`) que se alejan linealmente.
  - Define una micro-movilidad `RandomWalk2d` para los nodos individuales dentro de un área de 40x40m.
  - Usa `HierarchicalMobilityModel` para acoplar el movimiento del grupo (macro) con el movimiento aleatorio individual (micro).

### `InstallApplications`

- **Propósito:** Genera el tráfico de datos para la simulación.
- **Parámetros:**
  - `NodeContainer& clusterA, clusterC`: Origen y destino del tráfico.
  - `Ipv4InterfaceContainer& interfaces`: Para obtener la dirección IP del servidor.
  - `double simTime`: Límite temporal para las aplicaciones.
- **Acciones:** Instala un servidor `UdpEcho` en el Nodo 10 (Cluster C) y un cliente en el Nodo 0 (Cluster A). Configura el tráfico a 20 paquetes/segundo con un tamaño de 160 bytes para simular tráfico de voz.

---

## 2. Diferenciación: Variables vs. Constantes

Para el rigor científico del experimento, el código separa lo que es ajustable (Variables) de lo que permanece fijo para garantizar la consistencia (Constantes).

### 2.1 Variables Configurables (Dinámicas)

Estas variables pueden ser modificadas en cada ejecución para observar diferentes comportamientos:

| Variable     | Ubicación   | Método de Cambio | Impacto                                                                 |
| :----------- | :---------- | :--------------- | :---------------------------------------------------------------------- |
| `simTime`    | `main`      | `--simTime=X`    | Determina la duración de la observación.                                |
| `macroSpeed` | `main`      | `--macroSpeed=X` | **Variable independiente principal.** Controla la velocidad de ruptura. |
| `RngRun`     | NS-3 Global | `--RngRun=X`     | Cambia la semilla aleatoria para validar la consistencia estadística.   |

### 2.2 Constantes de la Arquitectura (Fijas)

Valores "hardcoded" que definen el entorno base del experimento y no cambian entre pruebas:

- **Topología:** 15 nodos totales (5 por clúster). Esta densidad es fija para mantener el mismo nivel de contención.
- **Protocolo de Red:** AODV. No se cambia para que el análisis del "Efecto Elástico" sea específico a este protocolo reactivo.
- **Capa Física:** Estándar 802.11b con tasas de 11Mbps (Data) y 1Mbps (Control).
- **Tráfico de Voz:**
  - Intervalo: 0.05s (20 pps).
  - Tamaño: 160 bytes.
  - Puerto: 9.
- **Límites de Movilidad:** Área de micro-movilidad fija en un cuadrado de 40x40 metros (`Rectangle(-20, 20, -20, 20)`).

---

## 3. Variables Principales (en `main`)

| Variable     | Tipo                     | Descripción                                                                      |
| :----------- | :----------------------- | :------------------------------------------------------------------------------- |
| `simTime`    | `double`                 | Duración total de la simulación en segundos (por defecto 60.0).                  |
| `macroSpeed` | `double`                 | Velocidad individual de cada super-clúster (separación total = 2 \* macroSpeed). |
| `allNodes`   | `NodeContainer`          | Objeto que gestiona la memoria y acceso a los 15 nodos creados.                  |
| `devices`    | `NetDeviceContainer`     | Almacena las tarjetas de red virtuales (PHY/MAC).                                |
| `interfaces` | `Ipv4InterfaceContainer` | Almacena la configuración lógica de red (IPs).                                   |
| `flowmon`    | `FlowMonitorHelper`      | Herramienta para recolectar estadísticas de flujo (PDR, Latencia).               |
| `stats`      | `std::map`               | Mapa que contiene las estadísticas finales procesadas por flujo.                 |

---

## 3. Flujo de Trabajo del Programa

El programa sigue una estructura lineal dividida en fases para garantizar la consistencia de la simulación:

1.  **Fase 1: Inicialización:** Se procesan los argumentos de entrada y se preparan los componentes de logging.
2.  **Fase 2: Creación de Nodos:** Se reserva memoria para los 15 nodos y se crean los subgrupos lógicos (Clústeres A, B y C).
3.  **Fase 3: Configuración Inalámbrica:** Se define el estándar 802.11b y el modo Ad-hoc. Se establece el archivo de salida de trazas.
4.  **Fase 4: Red y Enrutamiento:** Se instala la pila IPv4. Se activa **AODV**, crucial para observar el overhead de control cuando los enlaces se estiran.
5.  **Fase 5: Movilidad Jerárquica:** Se configuran los modelos de movimiento. Es la parte central del experimento donde se produce la separación física de los nodos.
6.  **Fase 6: Tráfico:** Se inyecta la carga de trabajo (Voz sobre UDP) para medir el impacto de la movilidad en el rendimiento.
7.  **Fase 7: Monitoreo:** Se activa `FlowMonitor` justo antes de iniciar para capturar cada paquete que transita por la red.
8.  **Fase 8: Ejecución y Resultados:**
    - Se ejecuta `Simulator::Run()`.
    - Al finalizar, se extraen estadísticas de flujo (PDR y Latencia).
    - Se exportan los resultados a `resultados_flujo.xml` y se destruye el simulador para liberar recursos.
