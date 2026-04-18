# Estructura del Código de Simulación

## Fase 1: Configuración Inicial (Setup y Parámetros)
Antes de crear nada, preparamos el entorno.

*   **Argumentos de línea de comandos:** Esto es vital para el método científico. Aquí definiremos variables que puedas cambiar desde la terminal (ej. la velocidad de los super-clústeres o el tiempo de simulación) sin tener que recompilar el código cada vez.
*   **Habilitar logs:** Encendemos los mensajes de depuración para ver qué está pasando por debajo si algo falla.

## Fase 2: Creación de la Materia Prima (Los Nodos)
En el mundo real, primero compras las computadoras. En NS-3, creamos los contenedores de nodos.

Aquí crearemos los 15 nodos base y los dividiremos lógicamente en nuestras agrupaciones (**Grupo A, B, C** y los **Super-clústeres X e Y**).

## Fase 3: La Capa Física y de Enlace (El Hardware de Red)
Ya tenemos las "computadoras", ahora les ponemos "tarjetas de red inalámbricas".

Configuraremos el estándar de **Wi-Fi** (por ejemplo, Wi-Fi 802.11b o 802.11n).

> **El detalle experto:** Aquí debemos especificar que las tarjetas operen en modo **Ad-hoc** (sin un router central), configurando la potencia de transmisión de la antena, lo cual determinará el rango de cobertura físico antes de que la señal empiece a estirarse.

## Fase 4: La Pila de Protocolos (Capa de Red y Enrutamiento)
Las tarjetas ya pueden emitir ondas, pero no saben "hablar" el idioma de internet.

Instalaremos la pila de protocolos (**Internet Stack**) para que cada nodo soporte IPv4.

**El corazón de la MANET:** Asignaremos el protocolo de enrutamiento dinámico (como OLSR o AODV). Este es el protocolo que sufrirá el **"Efecto Elástico"** y tratará de recalcular las rutas cuando los grupos se separen. Por último, les asignaremos direcciones IP a todos.

## Fase 5: El Modelo de Movilidad (El Core del Experimento)
Le daremos coordenadas iniciales a cada nodo.

*   **Configuraremos la micro-movilidad:** el movimiento aleatorio de los nodos dentro de sus grupos.
*   **Configuraremos la macro-movilidad:** el desplazamiento constante en direcciones opuestas de los Super-clústeres X e Y.

## Fase 6: Generación de Tráfico (Las Aplicaciones)
La red está lista y moviéndose, pero está en silencio. Necesitamos simular nuestra "llamada de voz".

Instalaremos una aplicación de cliente en un nodo del **Clúster A** que enviará ráfagas constantes de paquetes UDP (simulando voz) hacia un nodo servidor en el **Clúster C**.

Definimos a qué segundo exacto de la simulación empieza la llamada y a qué segundo termina.

## Fase 7: Monitoreo y Recolección de Datos (El Ojo del Científico)
Aquí preparamos las herramientas de medición antes de darle "Play".

Activaremos **FlowMonitor**, que es el módulo maestro de NS-3 para medir la latencia, los paquetes perdidos (PDR) y el Throughput de extremo a extremo de manera automática.

## Fase 8: Ejecución y Destrucción
Le decimos al simulador: `Simulator::Run()`. En este punto, el tiempo virtual comienza a correr y los nodos empiezan a moverse y a comunicarse.

Al finalizar el tiempo límite, llamamos a `Simulator::Destroy()` para limpiar la memoria de la computadora.
