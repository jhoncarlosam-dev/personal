# Conclusiones

El nodo diseñado para el centro cabe en una red de clase C y en un sitio IPv6 de documentación, y en los dos casos el direccionamiento se puede mostrar con cuentas cerradas. En IPv4, dos bits prestados parten 192.168.134.0/24 en cuatro subredes /26 de 62 hosts. Tres quedan asignadas de forma estática y la cuarta aloja el servidor DHCP, el registro IoT y los televisores. Los enlaces de firewall y de borde se sacaron a redes /30 para no gastar un bloque de 62 direcciones en un cable que solo tiene dos extremos. En IPv6, el sitio 2001:DB8:134::/48 presta tres subredes /64. Dos se calcularon hasta el último host. La tercera la numera el router por DHCPv6, que es la condición que la guía puso sobre esa subred.

La convergencia queda hecha en el sentido de Mejía Fajardo (2009): portal, correo, video e IoT usan la misma infraestructura IP. Queda también segmentada, porque compartir infraestructura no obliga a compartir dominio de difusión. Esa separación es la que permite poner el ASA delante de los usuarios sin apagar el ping entre servidores, red inalámbrica y subred DHCP.

El enrutamiento interior se evidencia con OSPF entre el núcleo y el borde. La decisión sobre el enrutamiento exterior queda argumentada y no simulada como un segundo sistema autónomo: con una sola salida, la ruta por defecto cumple, y BGP espera a que exista prefijo propio o una segunda relación con un proveedor (Zuluaga Alzate et al., 2021). Es una conclusión de diseño, no un componente que haya faltado.

El firewall demuestra política, no presencia. Hay tráfico que lo cruza, hay un eco que la lista de acceso niega entre dos equipos de la misma subred, y hay un ping desde fuera que se agota en el ASA porque la ruta sí existe. El correo en unad.edu.co y el portal con el nombre y el centro cubren el requisito de servicio y, junto con la subred inalámbrica, el escenario de acceso remoto y de trámite en línea que recorre Martín (2018). Los sensores y los tres televisores son la escala pequeña de la cadena que Camargo Ariza et al. (2020) describen para la ciudad: medir, registrar e informar. El simulador no responde por la privacidad de una cámara ni por el consumo de un despliegue urbano. El informe deja esa distancia explícita.

La doble pila de la red IPv6 es otra distancia que conviene conservar. El ping y el portal viajan en IPv6. El cliente de correo del simulador y parte de los objetos IoT siguen en IPv4. Decirlo evita presentar como red IPv6 pura un archivo que, en esos dos servicios, usa la otra pila porque la herramienta no da más.

El tercer ejercicio baja la misma pregunta al computador del estudiante. La máquina virtual, leída con Le et al. (2018), es hardware abstraído. El puente la pone en el segmento real. Nmap y PRTG convierten esa vecindad en inventario: hosts, versiones, sistemas y filtros. Abu Bakar y Kijsirikul (2023) muestran que un escáner de alta velocidad, apoyado en DPDK, puede duplicar la tasa y mantener una exactitud del 99,5 % en puertos abiertos dentro de su banco de pruebas. En un segmento de casa o de salón la herramienta proporcionada es Nmap, que los propios autores sitúan en redes pequeñas, seguida de una vigilancia continua con PRTG. El sondeo se queda en el prefijo autorizado. Un puerto filtered se interpreta como un cortafuegos haciendo su trabajo, y la acción siguiente es cerrar lo que no se usa, no evadir el filtro.

Queda por fuera de este documento, y es lo que el grupo tiene que completar antes del cierre de la fase, la ejecución grabada: las capturas de Packet Tracer, el escaneo real, los dos archivos `.pkt` y el video de cinco minutos por ejercicio. Sin esas piezas, el diseño está escrito y la evidencia de funcionamiento, que es el criterio alto de la rúbrica, todavía no.

# Referencias

Abu Bakar, R. & Kijsirikul, B. (2023). Enhancing network visibility and security with advanced port scanning techniques. *Sensors, 23*(17), Article 7541. https://doi.org/10.3390/s23177541

Camargo Ariza, L. L., Gómez Rojas, J. & Gasca, M. C. (2020). *La ciudad inteligente y la gestión de las TIC*. Editorial Unimagdalena.

Hinden, R. & Deering, S. (2006). *IP version 6 addressing architecture* (RFC 4291). Internet Engineering Task Force. https://www.rfc-editor.org/rfc/rfc4291

Huston, G., Lord, A. & Smith, P. (2004). *IPv6 address prefix reserved for documentation* (RFC 3849). Internet Engineering Task Force. https://www.rfc-editor.org/rfc/rfc3849

Le, D. N., Kumar, R., Nguyen, G. N. & Chatterjee, J. M. (2018). *Cloud computing and virtualization*. John Wiley & Sons.

Martín, P. (2018). *Teletrabajo y comercio electrónico*. Ministerio de Educación y Formación Profesional.

Mejía Fajardo, Á. M. (2009). *Redes convergentes*. Universidad Militar Nueva Granada.

Rekhter, Y., Moskowitz, B., Karrenberg, D., de Groot, G. J. & Lear, E. (1996). *Address allocation for private internets* (RFC 1918). Internet Engineering Task Force. https://www.rfc-editor.org/rfc/rfc1918

Zuluaga Alzate, I. D., Campo Muñoz, W. Y. & Chanchí Golondrino, G. E. (2021). *Despliegue de servicios sobre redes de datos implementadas con protocolos de enrutamiento de gateway interior y exterior*. Ediciones Elizcom.

# Apéndice A. Lista de capturas antes de comprimir

Se marca cada fila cuando el recuadro amarillo ya tiene la imagen propia del grupo.

| Listo | Ejercicio | Qué tiene que verse |
| --- | --- | --- |
| | 1 | Topología de Packet Tracer con los nombres de los equipos |
| | 1 | `show ip interface brief` y `show ip route` de R1 |
| | 1 | Laptop en el SSID UNAD-TELEMATICA con 192.168.134.150/26 |
| | 1 | Pool DHCP y `ipconfig /all` del cliente |
| | 1 | Portal con nombre, centro, foto real y tres imágenes |
| | 1 | Dominio unad.edu.co, tres usuarios, envío y recepción |
| | 1 | Ping permitido y ping negado por el ASA, más `show access-list` |
| | 1 | Tres televisores con el portal |
| | 1 | Objetos IoT controlados |
| | 1 | Ping entre subredes y vecino OSPF |
| | 2 | `show ipv6 interface brief` y binding DHCPv6 |
| | 2 | Ping IPv6 entre subredes |
| | 2 | Navegador en `http://[2001:db8:134:1::10]` |
| | 2 | Correo de tres usuarios en unad.edu.co |
| | 2 | IoT de la red IPv6 |
| | 3 | Adaptador puente |
| | 3 | Sistema invitado distinto, ya instalado |
| | 3 | Direcciones en el mismo prefijo |
| | 3 | Ping en los dos sentidos |
| | 3 | Nmap: hosts, versiones, sistema operativo y estado filtered |
| | 3 | PRTG con dispositivos y puertos |

# Apéndice B. Borradores para el foro

La rúbrica asigna hasta 20 puntos a la participación. Esos puntos salen de aportes publicados en el foro del curso, dentro del plazo, con el rol de cada integrante. Los textos de abajo son borradores técnicos para reescribir con las palabras de quien los publique. Copiarlos tal cual, o pegar una captura de un mensaje que no se envió, no constituye el aporte.

**Aporte de direccionamiento.** Propongo la red 192.168.134.0/24. Prestando dos bits quedan cuatro subredes /26, con salto de 64 y 62 hosts útiles: .0 servidores, .64 usuarios detrás del firewall, .128 inalámbrica y .192 DHCP, IoT y televisores. Los enlaces del ASA y de R2 los dejo en 172.16.1.0/30 y 172.16.1.4/30 para no gastar una subred de usuarios en un enlace de dos equipos. Quedo atento si el grupo prefiere otro tercer octeto.

**Aporte de servicios.** Dejo el portal en 192.168.134.10 y el correo en 192.168.134.20, dominio unad.edu.co, con un buzón por integrante que sí esté en el grupo. El DHCP de la cuarta subred arranca en .210 para no chocar con los televisores .200, .201 y .202. El HTML del portal está en la carpeta web; hay que cambiar el centro y la fotografía antes de pegarlo en el servidor.

**Aporte de IPv6.** Para la segunda red uso el sitio de documentación 2001:DB8:134::/48 y tres /64: :1 servidores, :2 inalámbrica y :3 entregada por DHCPv6 del router. El ping y el portal se prueban en IPv6. El correo y parte del IoT quedan en doble pila porque el cliente de Packet Tracer no sostiene esos servicios sobre IPv6. Conviene decirlo en el video para que no se lea como un olvido.

**Aporte de seguridad y escaneo.** El ASA niega solo el eco de 192.168.134.70 hacia el correo y niega el eco que entra desde fuera hacia la subred de usuarios. El resto de los ping de la guía van por el núcleo y no dependen del firewall. Para el tercer ejercicio propongo anfitrión Windows con PRTG e invitado Ubuntu en adaptador puente, Nmap vigente desde nmap.org, y el barrido limitado al prefijo de nuestro enrutador. Si alguien está en una red de campus que no controlamos, sondeamos solo el anfitrión y la virtual.

# Apéndice C. Videos y archivo comprimido

La entrega es un solo archivo `.zip`, subido por un integrante, con estos elementos.

| Elemento | Nombre sugerido | Estado |
| --- | --- | --- |
| Este informe, ya con capturas y sin recuadros vacíos | Informe_Fase4_Redes_y_Comunicaciones.docx | Falta pegar capturas, centro, código y foto |
| Red IPv4 | Simulacion_IPv4.pkt | Se crea en Packet Tracer |
| Red IPv6 | Simulacion_IPv6.pkt | Se crea en Packet Tracer |
| Enlaces de los videos | Enlaces_videos.txt | Se publican como no listados o con acceso del tutor |

Videos, máximo cinco minutos cada uno. Pueden ir separados o en un compilado de quince minutos, como indica la guía.

| Ejercicio | Enlace | Duración real |
| --- | --- | --- |
| Red IPv4 | [pegar enlace] | |
| Red IPv6 | [pegar enlace] | |
| Escaneo, Nmap y PRTG | [pegar enlace] | |

En `Enlaces_videos.txt` se copian las tres URL, el nombre de cada integrante que habla y la fecha de grabación. Un video donde solo se lee este informe, sin la topología en pantalla, no sustenta la simulación. El guion de cada ejercicio está minutado para que la grabación quepa en el límite.
