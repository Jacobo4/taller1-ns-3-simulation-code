# Documento de Definición de Proyecto: Simulación MANET Jerárquica

## Tema de Investigación

Determinación del umbral crítico de ruptura por latencia en redes MANET con movilidad jerárquica ("El Efecto Elástico").

## 1. Observación (Planteamiento del Problema)

En situaciones de despliegue en terreno, como misiones de búsqueda y rescate, los equipos de trabajo operan en formaciones agrupadas. A medida que estos grupos se desplazan para cubrir más terreno, la distancia física entre ellos aumenta.

En una Red Móvil Ad hoc (MANET), la comunicación entre dos grupos separados depende de que los dispositivos (nodos) en los bordes de cada grupo actúen como "puentes" inalámbricos. Si los grupos se alejan demasiado, la señal se debilita. Antes de que la conexión se pierda por completo, la red experimenta un **"efecto elástico"**: el sistema de enrutamiento intenta desesperadamente encontrar caminos alternativos para enviar los datos, lo que provoca que los paquetes de información tarden mucho tiempo en llegar a su destino. Si este tiempo de retraso (latencia) supera los 200ms, las aplicaciones en tiempo real, como las comunicaciones de voz bidireccionales, se vuelven incomprensibles e inútiles para la misión.

## 2. Indagación Newtoniana

¿Cómo impacta el incremento continuo de la distancia de separación entre dos super-clústeres (Nivel 2) sobre la latencia de extremo a extremo y la estabilidad del enrutamiento en una MANET jerárquica antes de alcanzar la ruptura total del enlace?

## 3. Planteamiento de Hipótesis

Para responder a la indagación, se someterán a experimentación mediante simulación las siguientes tres hipótesis:

### 3.1 H1 (El límite de Latencia):

La latencia promedio experimentará un crecimiento exponencial, superando el umbral crítico de los 200ms para comunicaciones en tiempo real, cuando la distancia física de separación entre los super-clústeres exceda el rango de los 80 a 100 metros, provocado por la pérdida de enlaces de línea de vista directa.

### 3.2 H2 (El costo del "Efecto Elástico"):

La sobrecarga (overhead) de los paquetes de control del protocolo de enrutamiento aumentará de forma drástica a medida que la separación física se acerque al límite de la cobertura Wi-Fi, debido a los esfuerzos continuos de los "nodos puente" por descubrir y recalcular rutas alternativas que se están rompiendo.

### 3.3 H3 (La Ventana de Estabilidad):

Existirá una "zona de tolerancia" inicial (aproximadamente en el primer 50% del rango máximo de la antena) en la cual el Packet Delivery Ratio (PDR) se mantendrá estable y cercano al 100%, para luego colapsar abruptamente una vez que el protocolo de enrutamiento agote sus tiempos de espera (timeouts).

## 4. Justificación Técnica para la Simulación

Estas tres hipótesis son ideales tenemos que recolectar las tres métricas más importantes en el análisis de redes, dandonos un informe muy completo:

### 4.1 H1

se comprueba midiendo el End-to-End Delay (Latencia): Verás cómo el tiempo sube en la gráfica a medida que avanza la simulación.

### 4.2 H2

se comprueba analizando el archivo de trazas (.tr): Contaremos cuántos paquetes de datos útiles (Data) viajaron versus cuántos paquetes de control (ej. mensajes HELLO o RREQ si usamos AODV) inundaron la red tratando de salvar la conexión.

### 4.3 H3

se comprueba midiendo el PDR (% de paquetes entregados con éxito): Te permitirá dibujar una curva perfecta donde se vea una meseta plana al principio y una caída libre al final.

## 5. Diseño de la Experimentación (Escenario de Simulación)

Para probar esta hipótesis en el simulador de eventos discretos, se establecerá el siguiente entorno lógico y físico:

### 5.1 Topología de la Red

Se simulará un total de 15 nodos, organizados estrictamente en dos niveles jerárquicos:

- **Nivel 1 (Clústeres Base):** Tres grupos independientes (Clúster A, Clúster B y Clúster C), compuestos por 5 nodos cada uno.
- **Nivel 2 (Super-clústeres):**
  - **Super-clúster X:** Agrupa a los Clústeres A y B.
  - **Super-clúster Y:** Agrupa únicamente al Clúster C.

### 5.2 Modelo de Movilidad

El escenario implementará movilidad jerárquica para reflejar el comportamiento humano realista:

- **Movilidad Interna (Micro-movilidad):** Los 5 nodos dentro de cada clúster de Nivel 1 tendrán un movimiento local y aleatorio en un radio pequeño (simulando a personas caminando en una zona de búsqueda).
- **Movilidad Global (Macro-movilidad):** El Super-clúster X y el Super-clúster Y se desplazarán en direcciones opuestas a una velocidad constante (ej. 2 m/s, velocidad de caminata rápida).

### 5.3 Variables del Experimento

- **Variable Independiente (Lo que se controla):** La distancia física de separación entre el centro geométrico del Super-clúster X y el Super-clúster Y. Esta distancia aumentará a medida que avance el tiempo de simulación.
- **Variable Dependiente (Lo que se mide):** El retraso de extremo a extremo (End-to-End Delay o Latencia) de los paquetes de datos enviados desde un nodo en el Clúster A hacia un nodo en el Clúster C.

## 6. Análisis de Datos y Métricas de Evaluación

Durante la simulación, se monitorizará el tráfico de red mediante herramientas de trazado de eventos. La evaluación de la hipótesis se basará en la recolección e interpretación de las siguientes métricas:

- **End-to-End Delay (Latencia Promedio):** Métrica principal. Se graficará la latencia en función de la distancia. Se busca identificar el punto exacto en el eje X (distancia) donde la curva de latencia cruza la barrera de los 200ms en el eje Y.
- **Packet Delivery Ratio (PDR):** Métrica secundaria. Porcentaje de paquetes enviados que llegan exitosamente. Ayudará a confirmar si el aumento de latencia coincide con una pérdida masiva de datos.
- **Routing Overhead (Sobrecarga de Enrutamiento):** Se medirá el volumen de mensajes de control que la red genera intentando reparar las rutas rotas a medida que los grupos se alejan.
