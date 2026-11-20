# Introducción

La Fase 4 del curso Redes y comunicaciones pide comprobar, en un escenario simulado y en un segmento real controlado por el estudiante, que un conjunto de servicios de red funciona y que ese funcionamiento se puede revisar. El resultado de aprendizaje de la guía lo formula así: configurar servicios avanzados mediante simuladores, verificar mecanismos básicos de seguridad y diagnóstico, y comprobar que el diseño responde a un requisito operativo. La rúbrica añade el marco con el que esa comprobación se valora: redes convergentes, virtualización, computación en la nube y tendencias como la ciudad inteligente y el Internet de las cosas.

El escenario elegido es un nodo de servicios de un centro de la Universidad Nacional Abierta y a Distancia. El nodo publica un portal con el nombre del estudiante y el centro de matrícula, opera el correo del dominio unad.edu.co, muestra información en tres televisores, registra dispositivos IoT y separa a los usuarios detrás de un cortafuegos. Esa escena cabe en una sede pequeña: atención virtual, comunicación institucional, señalización en sala y un par de sensores del espacio. También cabe en la lectura pedida para la fase. Mejía Fajardo (2009) entrega el fundamento de la red que une datos y video. Zuluaga Alzate et al. (2021) sitúan esos servicios sobre enrutamiento interior y exterior. Martín (2018) aporta el teletrabajo y el trámite en línea. Camargo Ariza et al. (2020) llevan la misma idea a la escala de la ciudad. Le et al. (2018) explican por qué el servidor del laboratorio puede entenderse como una máquina virtual y, más adelante, como un servicio en la nube. Abu Bakar y Kijsirikul (2023) sostienen el tercer ejercicio: mirar la red para saber qué hay encendido, qué servicio responde y qué filtro se interpone.

El trabajo tiene tres piezas. La primera es una red IPv4 de clase C, partida en cuatro subredes, con una subred inalámbrica, un servidor DHCP, un portal, correo para tres usuarios, un firewall físico, IoT y tres televisores. La segunda es una red IPv6 con prefijo /64, tres subredes, una de ellas inalámbrica y otra con DHCPv6 entregado por el router, más portal, correo e IoT. La tercera es el escaneo del segmento donde conviven el computador anfitrión y una máquina virtual en modo puente, con Nmap y con la edición gratuita de PRTG Network Monitor.

Los cálculos, la topología, los comandos y la relación con las lecturas están escritos en este informe. Las capturas se reservan a los recuadros amarillos porque tienen que salir de la simulación y del computador del grupo. El video de sustentación, de cinco minutos por ejercicio, se graba con la red abierta y con el guion que cierra cada ejercicio.

# Objetivos

El objetivo general es dejar en funcionamiento dos redes simuladas, una IPv4 y otra IPv6, con servicios de portal, correo e Internet de las cosas, y contrastar ese diseño con un diagnóstico real de hosts, servicios y filtros sobre un segmento autorizado.

Los objetivos específicos son los siguientes.

- Calcular y asignar el direccionamiento de una red clase C dividida en cuatro subredes /26, y el de un sitio IPv6 2001:DB8:134::/48 dividido en tres subredes /64.
- Configurar en Packet Tracer el enrutamiento, el DHCP, el DNS, el portal, el correo, la red inalámbrica, el cortafuegos, la televisión y el registro IoT, y probar la conectividad entre subredes.
- Instalar una máquina virtual con un sistema operativo distinto al del anfitrión, unir ambos equipos en el mismo segmento mediante un adaptador en puente y documentar el inventario que produzcan Nmap y PRTG.
- Relacionar cada decisión de diseño con los referentes de la fase y señalar el límite de lo que el simulador alcanza a demostrar.

# Marco de referencia

## La red que concentra varios servicios

Mejía Fajardo (2009) desarrolla los fundamentos de la red convergente: voz, datos y video dejan de ocupar infraestructuras paralelas y pasan a ser aplicaciones sobre una misma red IP. El beneficio operativo es concreto. Una sede mantiene un plan de direccionamiento, un grupo de conmutadores y una política de seguridad, en lugar de una red de telefonía, otra de datos y otra de video. El costo de crecer se concentra en capacidad y en direcciones, y el usuario percibe un solo acceso.

Esa unificación tiene una condición. Si todos los servicios comparten también el mismo dominio de difusión, la falla de un televisor o la tormenta de un sensor se vuelve falla del correo. La convergencia que se usa en este diseño es de infraestructura y de protocolo, con separación lógica por VLAN y por subred. El portal, el correo, la señalización y los sensores viajan sobre el mismo router y se atienden como servicios IP. Cada grupo ocupa su prefijo. Esa lectura aplica las páginas iniciales del texto de Mejía Fajardo al tamaño de un centro, que es el escenario que la guía pide relacionar con el sector productivo.

## Cómo se publican los servicios dentro y fuera del sitio

Zuluaga Alzate et al. (2021) estudian el despliegue de servicios cuando la red usa protocolos de puerta de enlace interior y de puerta de enlace exterior. Dentro de un sistema autónomo, un protocolo interior construye el mapa de las redes propias. RIP cuenta saltos y converge despacio. OSPF arma un árbol de caminos más cortos a partir del costo de los enlaces y escala mejor dentro de un área. EIGRP combina distancia y una métrica compuesta, con la restricción de ser tecnología de un fabricante. Entre sistemas autónomos, BGP intercambia prefijos y aplica política: qué se anuncia, a quién y con qué preferencia. BGP no elige el camino más corto en milisegundos. Elige la relación entre organizaciones.

El nodo de este trabajo es un solo sitio. El mapa interior sale de las redes conectadas al router de núcleo y de OSPF en el área 0 hacia un router de borde. La ruta de la subred que queda detrás del firewall se inyecta en OSPF como ruta estática, porque el cortafuegos no habla OSPF en esta práctica. En el borde, la salida hacia un proveedor se resuelve con una ruta por defecto. Con una sola salida y sin un prefijo público propio que anunciar, esa ruta cumple la función de llegar a otras redes. BGP entra en una etapa posterior: cuando el centro tenga prefijo delegado y necesite política entre dos proveedores, o cuando deba publicar sus redes a la malla exterior. Dejar BGP fuera de la simulación es una decisión de diseño, alineada con el tamaño del sitio que describen Zuluaga Alzate et al. (2021) al distinguir el gateway interior del exterior.

## Teletrabajo y trámite en línea

Martín (2018) recorre, en las páginas asignadas, el teletrabajo y el comercio electrónico como transformaciones de la organización del trabajo y de la economía digital. El teletrabajo desplaza parte de la jornada fuera de la sede y la apoya en el acceso remoto a los servicios institucionales. El comercio electrónico, leído aquí en la escala de un trámite universitario, convierte el portal en el punto donde la persona consulta, solicita y recibe respuesta sin estar en la ventanilla.

De esa lectura salen tres requisitos para la red del centro. El servicio tiene que ser alcanzable desde un acceso que no es el escritorio fijo: de ahí la subred inalámbrica. La comunicación entre personas tiene que quedar en un dominio institucional: de ahí el correo unad.edu.co con tres buzones. El canal público tiene que mostrar información verificable del sitio: de ahí el portal con el nombre y el centro. También sale un riesgo. Un servicio útil y mal cerrado queda expuesto. El firewall de la subred de usuarios y el inventario de puertos del tercer ejercicio responden a ese riesgo. Martín (2018) permite nombrar el beneficio y la exposición al mismo tiempo: flexibilidad laboral y superficie de ataque crecen juntas si la red no segmenta.

## La ciudad y la gestión de las TIC

Camargo Ariza et al. (2020) plantean la ciudad inteligente como un uso de las TIC para la planeación urbana, la sostenibilidad y la calidad de vida. La ciudad deja de ser solo obra física y pasa a ser también un sistema que mide, comunica y decide: movilidad, ambiente, seguridad, servicios públicos. Las TIC son el instrumento de esa gestión, y el dato del sensor es tan relevante como la vía o la red de acueducto.

El laboratorio no simula una ciudad. Simula la cadena mínima que una ciudad inteligente repite en cada cuadra: un objeto con dirección, una plataforma que lo registra y una superficie que informa a las personas. La lámpara, la cámara y el sensor cumplen el primer papel. El servidor de registro y la puerta de enlace IoT cumplen el segundo. Los tres televisores cumplen el tercero, con la fotografía del estudiante y tres imágenes de telemática. El límite hay que decirlo con claridad. Packet Tracer muestra conectividad y control básico. No mide consumo energético, ni interoperabilidad entre fabricantes, ni el régimen de los datos personales que una cámara recoge. Esos son los problemas duros del texto de Camargo Ariza et al. (2020), y quedan como criterio para juzgar la simulación, no como algo que la simulación haya resuelto.

## Virtualización y nube

Le et al. (2018) presentan, en el tramo asignado, los fundamentos de la computación en la nube y de la virtualización. La virtualización separa el servicio del servidor físico: varias máquinas lógicas comparten CPU, memoria y disco, cada una con su sistema y su interfaz de red. La nube entrega esa capacidad como servicio, con elasticidad, aprovisionamiento rápido y un costo asociado al uso. El beneficio es de aprovechamiento: se consolida hardware, se clona un servidor, se aísla una prueba. El costo es de dependencia: hay un hipervisor de por medio, y en la nube también un proveedor, un enlace y una jurisdicción sobre los datos.

En esta fase la virtualización aparece de dos maneras. En Packet Tracer, cada servidor es un equipo lógico que concentra DNS, HTTP, correo o DHCP. En el tercer ejercicio, la máquina virtual es virtualización real sobre el computador del estudiante: otro sistema operativo, otro núcleo de red, el mismo hardware. El modo puente hace que esa máquina sea un vecino de capa 2 del anfitrión y no un cliente escondido detrás de una traducción de direcciones del hipervisor. La nube queda como lectura de destino. El portal y el correo de la simulación son el tipo de carga que una sede puede mover a máquinas virtuales propias o a un proveedor. Moverlos exige conservar el direccionamiento, el nombre unad.edu.co y la política del firewall. La simulación comprueba la lógica del servicio. Le et al. (2018) sirven para no confundir esa comprobación con una migración ya hecha.

## Visibilidad y escaneo de puertos

Abu Bakar y Kijsirikul (2023) estudian cómo las técnicas avanzadas de escaneo mejoran la visibilidad y la seguridad de la red. Su punto de partida es una limitación práctica: el escáner tradicional se queda corto en velocidad, exactitud y eficiencia cuando la red crece y el perímetro se vuelve poroso. Combinan técnicas activas, entre ellas los escaneos SYN, ACK y XMAS, con técnicas pasivas como la lectura de banners y la huella del servicio. Sobre esa base construyen un escáner apoyado en DPDK, pensado para procesar paquetes a alta tasa con tarjetas y entornos de 40 y 100 GbE. En su evaluación reportan el doble de velocidad de escaneo frente a otros escáneres del experimento, una exactitud del 99,5 % al identificar puertos abiertos y un uso de CPU y de memoria cercano a un 40 % menos.

Ese resultado pertenece a un laboratorio de alta velocidad. La red de un computador doméstico o de un salón no necesita DPDK para verse. Lo que sí se traslada es la pregunta del artículo: qué se gana, en seguridad, al saber con precisión qué hosts responden, qué aplicación y qué versión escuchan, qué sistema operativo aparece y qué filtro descarta sondas. Los autores recuerdan además que Nmap está optimizado para segmentos pequeños, mientras ZMap y Masscan apuntan a barridos de escala de Internet. Para el segmento del tercer ejercicio, Nmap es la herramienta coherente con esa distinción.

El mismo artículo describe, como antecedentes, técnicas de evasión: sondas lentas, retardos para no disparar un IDS, fragmentación o decoys. Esas técnicas buscan que un defensor no note el sondeo. Este trabajo no las usa. El escaneo de la fase es un inventario autorizado del segmento propio, con el adaptador en puente, para cerrar lo que sobre y para vigilarlo después con PRTG. Usar evasión contra una red que no es del grupo invertiría el sentido preventivo que la guía le da a PRTG y al artículo.

## Decisiones que salen del marco

| Decisión | Lectura que la sostiene | Dónde se ve en la práctica |
| --- | --- | --- |
| Una infraestructura IP para portal, correo, televisión e IoT, con una subred por función | Mejía Fajardo (2009) | Ejercicio 1, cuatro subredes /26 |
| OSPF dentro del sitio y ruta por defecto en el borde, sin BGP | Zuluaga Alzate et al. (2021) | Vecindad R1-R2 y loopback 10.255.255.2 |
| Acceso inalámbrico, correo institucional y portal con el nombre del centro | Martín (2018) | SSID UNAD-TELEMATICA, dominio unad.edu.co, index.html |
| Sensores registrados y televisores como superficie de información | Camargo Ariza et al. (2020) | Home Gateway, tres televisores |
| Máquina virtual en puente como forma local de abstraer el servidor | Le et al. (2018) | Ejercicio 3 |
| Inventario de hosts, versiones, sistemas y filtros, sin técnicas de evasión | Abu Bakar y Kijsirikul (2023) | Nmap y PRTG sobre el segmento propio |

<!-- salto -->
