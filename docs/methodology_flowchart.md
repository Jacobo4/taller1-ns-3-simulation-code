# Diagrama de Flujo de la Metodología

Este diagrama representa el proceso secuencial de la simulación implementado en `main.cc`, desde la configuración inicial hasta la obtención de resultados.

```mermaid
graph TD
    Start((Inicio)) --> Phase1[<b>Fase 1: Inicialización</b><br/>Procesamiento de argumentos<br/>simTime, macroSpeed]
    
    Phase1 --> Phase2[<b>Fase 2: Creación de Nodos</b><br/>Instanciación de 15 nodos<br/>División en Clústeres A, B y C]
    
    Phase2 --> Phase3[<b>Fase 3: Configuración Wi-Fi</b><br/>Estándar 802.11b Ad-hoc<br/>Habilitación de trazas .tr]
    
    Phase3 --> Phase4[<b>Fase 4: Red y Enrutamiento</b><br/>Instalación de pila IPv4<br/>Configuración de AODV]
    
    Phase4 --> Phase5[<b>Fase 5: Movilidad Jerárquica</b><br/>Acoplamiento Macro + Micro<br/>Separación física de grupos]
    
    Phase5 --> Phase6[<b>Fase 6: Tráfico de Aplicación</b><br/>UDP Echo (Voz)<br/>Nodo 0 -> Nodo 10]
    
    Phase6 --> Phase7[<b>Fase 7: Monitoreo</b><br/>Instalación de FlowMonitor]
    
    Phase7 --> Phase8[<b>Fase 8: Ejecución y Resultados</b><br/>Simulator::Run<br/>Extracción de PDR y Latencia]
    
    Phase8 --> End((Fin))

    subgraph "Ciclo de Simulación"
        Phase5
        Phase6
        Phase7
        Phase8
    end

    style Start fill:#f9f,stroke:#333,stroke-width:2px
    style End fill:#f9f,stroke:#333,stroke-width:2px
    style Phase8 fill:#dfd,stroke:#333,stroke-width:2px
```

## Descripción del Flujo
1.  **Configuración Base (Fases 1-4):** Se establece el hardware virtual, las reglas de comunicación y los parámetros globales.
2.  **Dinámica del Experimento (Fase 5):** Se activa el motor de movimiento que genera el "Efecto Elástico".
3.  **Carga de Trabajo (Fase 6):** Se inicia la transmisión de datos para medir el impacto.
4.  **Recolección y Cierre (Fases 7-8):** Se capturan las métricas en tiempo real y se procesan al finalizar la ejecución.
