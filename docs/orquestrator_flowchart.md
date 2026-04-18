# Diagrama de Flujo del Orquestador

Este diagrama describe la lógica de automatización, ejecución paralela y procesamiento de datos implementada en `orquestrator.py`.

```mermaid
graph TD
    Start((Inicio)) --> Init[<b>Inicialización</b><br/>Definir velocidades y simTime<br/>Preparar listas de resultados]
    
    Init --> Loop{¿Hay más velocidades?}
    
    Loop -- Sí --> ExecNS3[<b>Ejecutar NS-3</b><br/>subprocess.run main.cc<br/>Capturar stdout]
    
    ExecNS3 --> CheckError{¿Error en ejecución?}
    CheckError -- Sí --> Abort[Abortar Experimentación]
    
    CheckError -- No --> ParseConsole[<b>Extracción Primaria (Regex)</b><br/>Extraer PDR y Latencia de stdout]
    
    ParseConsole --> GrepTraces[<b>Extracción Secundaria (Grep)</b><br/>Analizar trazas_manet.tr<br/>Contar paquetes UDP y AODV]
    
    GrepTraces --> AuditClusters[<b>Auditoría por Clúster</b><br/>Grep por rangos de nodos<br/>[0-4], [5-9], [10-14]]
    
    AuditClusters --> StoreData[<b>Consolidar Datos</b><br/>Guardar en resultados_globales<br/>Guardar en resultados_clusteres]
    
    StoreData --> Loop
    
    Loop -- No --> ExportCSV[<b>Exportación Final</b><br/>Escribir resultados_simulacion.csv<br/>Escribir resultados_carga_clusteres.csv]
    
    ExportCSV --> End((Fin))

    subgraph "Bucle de Experimentación"
        ExecNS3
        ParseConsole
        GrepTraces
        AuditClusters
        StoreData
    end

    style Start fill:#f9f,stroke:#333,stroke-width:2px
    style End fill:#f9f,stroke:#333,stroke-width:2px
    style Loop fill:#fff4dd,stroke:#d4a017,stroke-width:2px
    style Abort fill:#f66,stroke:#333,stroke-width:2px
```

## Descripción del Flujo
1.  **Iteración de Escenarios:** El script recorre 50 configuraciones de velocidad diferentes para capturar el comportamiento de la red en diversas condiciones.
2.  **Análisis Multi-Capa:**
    *   **Capa 1 (Consola):** Obtiene métricas agregadas de alto nivel proporcionadas por FlowMonitor.
    *   **Capa 2 (Trazas):** Realiza una "inspección profunda" de paquetes usando herramientas de bajo nivel (`grep`) para desglosar el tráfico por protocolos y ubicación geográfica (clústeres).
3.  **Persistencia:** Los datos se estructuran para facilitar su posterior análisis en herramientas como Excel, MATLAB o Python (Pandas).
