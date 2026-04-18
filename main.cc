#include "ns3/aodv-module.h"
#include "ns3/applications-module.h"
#include "ns3/core-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/network-module.h"
#include "ns3/wifi-module.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("Taller1Manet");

// ==========================================
// FASE 1: Configuración Inicial
// ==========================================
void
SetupEnvironment(int argc, char* argv[], double& simTime, double& macroSpeed)
{
    CommandLine cmd(__FILE__);
    cmd.AddValue("simTime", "Tiempo total de la simulación (segundos)", simTime);
    cmd.AddValue("macroSpeed", "Velocidad de separación de los super-clústeres (m/s)", macroSpeed);
    cmd.Parse(argc, argv);

    Time::SetResolution(Time::NS);
    LogComponentEnable("UdpEchoClientApplication", LOG_LEVEL_INFO);
    LogComponentEnable("UdpEchoServerApplication", LOG_LEVEL_INFO);
}

// ==========================================
// FASE 2: Creación de Nodos (Agrupaciones)
// ==========================================
void
CreateNodes(NodeContainer& allNodes,
            NodeContainer& clusterA,
            NodeContainer& clusterB,
            NodeContainer& clusterC)
{
    allNodes.Create(15);

    // Asignación lógica de Nivel 1
    for (uint32_t i = 0; i < 5; ++i)
    {
        clusterA.Add(allNodes.Get(i));
    }
    for (uint32_t i = 5; i < 10; ++i)
    {
        clusterB.Add(allNodes.Get(i));
    }
    for (uint32_t i = 10; i < 15; ++i)
    {
        clusterC.Add(allNodes.Get(i));
    }

    NS_LOG_UNCOND("Fase 2: 15 Nodos creados y divididos en Clústeres A, B y C.");
}

// ==========================================
// FASE 3: Capa Física y Enlace (Wi-Fi Ad-hoc)
// ==========================================
void
ConfigureWifi(NodeContainer& allNodes, NetDeviceContainer& devices)
{
    WifiMacHelper mac;
    mac.SetType("ns3::AdhocWifiMac"); // Modo Ad-hoc sin router

    YansWifiPhyHelper phy;
    YansWifiChannelHelper channel = YansWifiChannelHelper::Default();
    phy.SetChannel(channel.Create());

    // Configurar potencia de transmisión para un rango de ~100m
    // phy.Set("TxPowerStart", DoubleValue(7.5));
    // phy.Set("TxPowerEnd", DoubleValue(7.5));

    WifiHelper wifi;
    wifi.SetStandard(WIFI_STANDARD_80211b);
    wifi.SetRemoteStationManager("ns3::ConstantRateWifiManager",
                                 "DataMode",
                                 StringValue("DsssRate11Mbps"),
                                 "ControlMode",
                                 StringValue("DsssRate1Mbps"));

    devices = wifi.Install(phy, mac, allNodes);

    // Habilitar trazas para probar H2 (Costo del Efecto Elástico)
    AsciiTraceHelper ascii;
    phy.EnableAsciiAll(
        ascii.CreateFileStream("scratch/taller1-ns-3-simulation-code/results/trazas_manet.tr"));

    NS_LOG_UNCOND("Fase 3: Wi-Fi 802.11b Ad-hoc configurado con recolección de trazas.");
}

// ==========================================
// FASE 4: Pila de Protocolos (Enrutamiento y Red)
// ==========================================
void
ConfigureInternet(NodeContainer& allNodes,
                  NetDeviceContainer& devices,
                  Ipv4InterfaceContainer& interfaces)
{
    AodvHelper aodv; // Usamos AODV: ideal para observar el Overhead reactivo (RREQ/RREP)

    InternetStackHelper stack;
    stack.SetRoutingHelper(aodv);
    stack.Install(allNodes);

    Ipv4AddressHelper address;
    address.SetBase("10.1.1.0", "255.255.255.0");
    interfaces = address.Assign(devices);

    NS_LOG_UNCOND("Fase 4: Pila IPv4 y enrutamiento AODV instalados.");
}

// ==========================================
// FASE 5: Modelo de Movilidad Jerárquica
// ==========================================
void
ConfigureMobility(NodeContainer& clusterA,
                  NodeContainer& clusterB,
                  NodeContainer& clusterC,
                  double macroSpeed)
{
    // 5.1 Nodos Padre Invisibles (Macro-movilidad: Super-clústeres X e Y)
    Ptr<ConstantVelocityMobilityModel> parentX = CreateObject<ConstantVelocityMobilityModel>();
    parentX->SetPosition(Vector(0.0, 50.0, 0.0));
    parentX->SetVelocity(Vector(-macroSpeed, 0.0, 0.0)); // Se mueve hacia la izquierda

    Ptr<ConstantVelocityMobilityModel> parentY = CreateObject<ConstantVelocityMobilityModel>();
    parentY->SetPosition(Vector(30.0, 50.0, 0.0));      // Separación inicial de 30m
    parentY->SetVelocity(Vector(macroSpeed, 0.0, 0.0)); // Se mueve hacia la derecha

    // 5.2 Configuración de la Micro-movilidad (Caminata aleatoria)
    // Usamos ObjectFactory para crear los modelos sin instalarlos directamente en los nodos aún
    ObjectFactory microFactory;
    microFactory.SetTypeId("ns3::RandomWalk2dMobilityModel");
    microFactory.Set("Bounds", RectangleValue(Rectangle(-20, 20, -20, 20)));
    microFactory.Set("Distance", DoubleValue(2.0));
    microFactory.Set("Speed", StringValue("ns3::ConstantRandomVariable[Constant=1.0]"));

    // 5.3 Acoplar Micro y Macro movilidad (HierarchicalMobilityModel)

    // Super-clúster X (Clústeres A y B)
    NodeContainer clusterXNodes;
    clusterXNodes.Add(clusterA);
    clusterXNodes.Add(clusterB);

    for (uint32_t i = 0; i < clusterXNodes.GetN(); ++i)
    {
        Ptr<MobilityModel> child = microFactory.Create<MobilityModel>();
        Ptr<HierarchicalMobilityModel> hierarchical = CreateObject<HierarchicalMobilityModel>();

        // ¡IMPORTANTE! Establecer el padre ANTES que el hijo.
        // Esto evita que SetParent intente preservar una posición absoluta fuera de los límites del
        // hijo.
        hierarchical->SetParent(parentX);
        hierarchical->SetChild(child);

        // Solo agregamos el modelo jerárquico al nodo
        clusterXNodes.Get(i)->AggregateObject(hierarchical);
    }

    // Super-clúster Y (Clúster C)
    for (uint32_t i = 0; i < clusterC.GetN(); ++i)
    {
        Ptr<MobilityModel> child = microFactory.Create<MobilityModel>();
        Ptr<HierarchicalMobilityModel> hierarchical = CreateObject<HierarchicalMobilityModel>();

        hierarchical->SetParent(parentY);
        hierarchical->SetChild(child);

        clusterC.Get(i)->AggregateObject(hierarchical);
    }

    NS_LOG_UNCOND("Fase 5: Movilidad Jerárquica configurada (Efecto de separación activado).");
}

// ==========================================
// FASE 6: Generación de Tráfico (Aplicaciones)
// ==========================================
void
InstallApplications(NodeContainer& clusterA,
                    NodeContainer& clusterC,
                    Ipv4InterfaceContainer& interfaces,
                    double simTime)
{
    uint16_t port = 9;

    // Servidor en el Clúster C (Nodo 10, índice 10 en las interfaces)
    UdpEchoServerHelper server(port);
    ApplicationContainer serverApps = server.Install(clusterC.Get(0));
    serverApps.Start(Seconds(1.0));
    serverApps.Stop(Seconds(simTime - 1.0));

    // Cliente en el Clúster A (Nodo 0) apuntando al Servidor
    UdpEchoClientHelper client(interfaces.GetAddress(10), port);
    client.SetAttribute("MaxPackets", UintegerValue(10000));
    client.SetAttribute("Interval",
                        TimeValue(Seconds(0.05)));         // 20 paquetes/segundo (Simulando voz)
    client.SetAttribute("PacketSize", UintegerValue(160)); // Payload típico de códec G.711

    ApplicationContainer clientApps = client.Install(clusterA.Get(0));
    clientApps.Start(Seconds(2.0));
    clientApps.Stop(Seconds(simTime - 1.0));

    NS_LOG_UNCOND("Fase 6: Tráfico UDP de voz simulado de Clúster A -> Clúster C.");
}

// ==========================================
// FASE 7 y 8: Ejecución y Monitoreo (Main)
// ==========================================
int
main(int argc, char* argv[])
{
    double simTime = 60.0;
    double macroSpeed = 1.0; // Velocidad relativa de separación será de 2 m/s

    SetupEnvironment(argc, argv, simTime, macroSpeed);

    NodeContainer allNodes, clusterA, clusterB, clusterC;
    CreateNodes(allNodes, clusterA, clusterB, clusterC);

    NetDeviceContainer devices;
    ConfigureWifi(allNodes, devices);

    Ipv4InterfaceContainer interfaces;
    ConfigureInternet(allNodes, devices, interfaces);

    ConfigureMobility(clusterA, clusterB, clusterC, macroSpeed);

    InstallApplications(clusterA, clusterC, interfaces, simTime);

    // Fase 7: Ojo del Científico (FlowMonitor)
    FlowMonitorHelper flowmon;
    Ptr<FlowMonitor> monitor = flowmon.InstallAll();

    NS_LOG_UNCOND("Fase 8: Iniciando Simulación por " << simTime << " segundos...");

    Simulator::Stop(Seconds(simTime));
    Simulator::Run();

    // Recolección de Datos Post-Simulación
    monitor->CheckForLostPackets();
    Ptr<Ipv4FlowClassifier> classifier = DynamicCast<Ipv4FlowClassifier>(flowmon.GetClassifier());
    std::map<FlowId, FlowMonitor::FlowStats> stats = monitor->GetFlowStats();

    for (std::map<FlowId, FlowMonitor::FlowStats>::const_iterator i = stats.begin();
         i != stats.end();
         ++i)
    {
        Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow(i->first);
        if (t.sourceAddress == "10.1.1.1" && t.destinationAddress == "10.1.1.11")
        {
            std::cout << "\n--- RESULTADOS DEL EXPERIMENTO ---" << std::endl;
            std::cout << "Paquetes Enviados: " << i->second.txPackets << std::endl;
            std::cout << "Paquetes Recibidos: " << i->second.rxPackets << std::endl;

            if (i->second.txPackets > 0)
            {
                std::cout << "Packet Delivery Ratio (PDR): "
                          << (i->second.rxPackets * 100.0 / i->second.txPackets) << "%"
                          << std::endl;
            }

            if (i->second.rxPackets > 0)
            {
                std::cout << "Latencia Promedio (Delay): "
                          << (i->second.delaySum.GetSeconds() / i->second.rxPackets) * 1000 << " ms"
                          << std::endl;
            }
            else
            {
                std::cout << "Latencia Promedio (Delay): 0.0 ms" << std::endl; // Ruptura total
            }
        }
    }

    monitor->SerializeToXmlFile("scratch/taller1-ns-3-simulation-code/results/resultados_flujo.xml",
                                true,
                                true);
    Simulator::Destroy();

    NS_LOG_UNCOND(
        "Simulación finalizada. Archivos generados: trazas_manet.tr y resultados_flujo.xml");
    return 0;
}
