import "server-only";
import type { Profile } from "./types";

export function seedProfile(): Profile {
  return {
    fullName: "Jhon Carlos Acevedo Mendoza",
    birthDate: null,
    reportedAge: 27,
    reportedAgeAsOf: "2026-07-19",
    city: "Cúcuta, Norte de Santander",
    headline: "Ingeniería en curso · desarrollo y calidad de software",
    photoCaption: "7 de mayo de 2026",
    civilStatus: "relacion",
    partnerName: "Katerine Orjuela",
    relationshipSince: "2026-07-20",
    civilNote:
      "El diario la nombra como novia hasta el 14 de noviembre de 2026. El 20 de noviembre cumplían 4 meses. Si eso cambió, corrígelo.",
    healthStatus: "En seguimiento",
    healthDetail:
      "EPS Sanitas. En septiembre de 2026 te formularon fexofenadina por un sarpullido y quedaron exámenes pendientes. El 10 de noviembre fuiste a la cita médica de Nelumbo. En mayo cancelaste el gimnasio. El diario repite sueño corto, comidas a deshora y un antecedente de gastroenteritis.",
    studying: true,
    school: "Universidad Nacional Abierta y a Distancia (UNAD)",
    program: "Ingeniería de Sistemas",
    semester: "2026-2, atrasado",
    studyNote:
      "El CV pone la UNAD de enero de 2025 a febrero de 2030, y la UFPS de marzo de 2017 a marzo de 2025, sin título. En enero de 2026 escribiste que en febrero empezabas el 7.º semestre; LinkedIn decía 8.º. El 26 de mayo cerraste 2026-1: actividad física y salud, bases de datos, ciencia de datos con Python, inglés A2 y sistemas operativos. El 10 de noviembre la homologación UFPS → UNAD acababa de arrancar. En agosto la liquidación que viste era de 220.000, con plazo al 30 de septiembre. En noviembre seguías debiendo trabajos.",
    graduated: false,
    graduationNote:
      "Todavía no. La UFPS quedó sin título y la homologación hacia la UNAD iba empezando el 10 de noviembre de 2026.",
    employed: false,
    jobTitle: "Analista de calidad de software",
    employer: "Nelumbo Consultores",
    jobEndedOn: "2026-11-06",
    salaryCop: 0,
    lastSalaryCop: 2100000,
    salaryNote:
      "En 2025 el diario dice 2.100.000. En enero de 2026 calculaste cerca de 2.400.000. Un pago de nómina fue 1.859.928. El presupuesto usaba 2.100.000, entre nómina de 1.735.933 y dólares. Desde el 6 de noviembre el salario es 0.",
    otherWork:
      "Freelance con Café Marrón y, en la hoja de noviembre, Upwork. El proyecto SUMA con Julián, de gestión de ganado, todavía sin ingreso fijo. El 28 de julio dejaste el mesero en Fantasía Real.",
    otherIncomeCop: 0,
    english: "Inglés A2 visto en la UNAD durante 2026-1. En una nota del diario llevabas 26 prácticas.",
    skills: ["Node.js", "TypeScript", "Python", "PostgreSQL", "Oracle", "React", "Angular", "QA"],
    focus: "Orden, salud y constancia.",
    situationNote:
      "El 7 de noviembre escribiste que el 22 de noviembre era el límite para seguir en Cúcuta sin trabajo. Si no había empleo, el plan era volver a Arboledas. Actualiza la ciudad cuando sepas dónde quedaste.",
    situationOpen: true,
    liquidationStatus: "por_confirmar",
    liquidationExpectedCop: 6841150,
    liquidationExpectedOn: "2026-11-12",
    liquidationReceivedCop: null,
    reviewed: false,
    github: "jhoncarlosam-dev",
    linkedin: "jhon-carlos-acevedo-mendoza",
  };
}

export const seedAssets = [
  {
    name: "Laptop",
    kind: "equipo",
    detail: "ASUS VivoBook X1605VA · Intel i5-13420H · 16 GB RAM · SSD 477 GB · gráficos Intel UHD · Windows 11 Home",
    valueCop: 1700000,
    valueIsEstimate: true,
    owned: true,
    note: "Estimación de reventa, noviembre de 2026. En tiendas de Colombia el mismo modelo nuevo, con disco de 1 TB, se ve entre 2,3 y 2,6 millones. El tuyo tiene 477 GB. No es una tasación.",
  },
  {
    name: "Moto",
    kind: "vehiculo",
    detail: "TVS Raider 125 FI ABS, azul. Pico y placa los lunes. Licencia A2 vigente hasta el 24 de agosto de 2036.",
    valueCop: 8500000,
    valueIsEstimate: true,
    owned: true,
    note: "La compraste el 8 de agosto de 2026. El crédito fue de 10 millones y la deuda va aparte: este número es el valor de la moto, no lo que te queda libre.",
  },
  {
    name: "Monitor",
    kind: "equipo",
    detail: "Lenovo L27i-4A",
    valueCop: 550000,
    valueIsEstimate: true,
    owned: true,
    note: "Lo compraste en 2026. Estimación de reventa: ajústala con lo que pagaste.",
  },
  {
    name: "Celular",
    kind: "equipo",
    detail: "Motorola Moto G60 Fusion",
    valueCop: 250000,
    valueIsEstimate: true,
    owned: true,
    note: "Así está en el inventario del diario. En una conversación también dijiste un Motorola Edge: confirma cuál usas hoy.",
  },
  {
    name: "Auriculares",
    kind: "equipo",
    detail: "Sony WH-CH720N",
    valueCop: 280000,
    valueIsEstimate: true,
    owned: true,
    note: "Estimación de reventa.",
  },
  {
    name: "Nevera",
    kind: "hogar",
    detail: "Nevera del apartamento en Cúcuta",
    valueCop: null,
    valueIsEstimate: true,
    owned: true,
    note: "En el diario guardas comida ahí. No hay marca ni precio. Si es de doña Ligia y no tuya, márcala como no propia para que no entre al patrimonio.",
  },
  {
    name: "Teclado",
    kind: "equipo",
    detail: "MageGee MK-Box, mecánico",
    valueCop: 80000,
    valueIsEstimate: true,
    owned: true,
    note: "Estimación.",
  },
  {
    name: "Mouse",
    kind: "equipo",
    detail: "Trust Yuno, ergonómico",
    valueCop: 40000,
    valueIsEstimate: true,
    owned: true,
    note: "Estimación.",
  },
  {
    name: "Parlante",
    kind: "equipo",
    detail: "JBL Go 4 Bluetooth, azul",
    valueCop: 150000,
    valueIsEstimate: true,
    owned: true,
    note: "Estimación de reventa.",
  },
  {
    name: "Cascos",
    kind: "vehiculo",
    detail: "Dos cascos. En agosto seguían pendientes el chaleco y los guantes.",
    valueCop: 350000,
    valueIsEstimate: true,
    owned: true,
    note: "Estimación. Cambia el valor por lo que te costó el casco.",
  },
  {
    name: "Efectivo y cuentas",
    kind: "dinero",
    detail: "Lo que tienes disponible hoy en efectivo y en el banco",
    valueCop: null,
    valueIsEstimate: false,
    owned: true,
    note: "La liquidación de Nelumbo era 6.841.150 y debía llegar el 12 de noviembre de 2026. No la sumé: confirma cuánto quedó después de la cuota de la moto y de los gastos.",
  },
] as const;

export const seedLiabilities = [
  {
    name: "Crédito moto TVS · Banco de Bogotá",
    balanceCop: 9771842,
    monthlyCop: 354000,
    confirmed: false,
    note: "48 cuotas desde el 5 de octubre de 2026. Pagaste octubre y noviembre; en noviembre fueron 360.000. Si el préstamo fue de 10.000.000, el capital después de 2 cuotas queda cerca de 9.771.842. El banco tiene el saldo real. Quedan 46 cuotas, 16.284.000 si no abonas a capital. La próxima vence el 5 de diciembre de 2026 y el crédito termina hacia septiembre de 2030.",
  },
  {
    name: "Tarjeta de crédito Bancolombia",
    balanceCop: 2100000,
    monthlyCop: null,
    confirmed: false,
    note: "En el presupuesto del diario figuraban 2.100.000. En marzo la habías copado, en mayo pagaste 1.500.000 y en agosto volviste a abonar. Confirma el saldo de hoy.",
  },
  {
    name: "Deuda con Anderson",
    balanceCop: 1000000,
    monthlyCop: null,
    confirmed: false,
    note: "La hoja de noviembre dice 1.000.000. En agosto pensabas pagarle 900.000 en octubre. Confirma cuánto queda.",
  },
  {
    name: "Deuda con David Rozo",
    balanceCop: 13000,
    monthlyCop: null,
    confirmed: false,
    note: "13.000 del 10 de noviembre, después del ping pong.",
  },
] as const;

export const seedCosts = [
  {
    name: "Arriendo",
    amountCop: 600000,
    note: "Doña Ligia, Cúcuta. En julio pagaste 200.000 y después la cuota volvió a 600.000.",
  },
  {
    name: "Mercado",
    amountCop: 400000,
    note: "Presupuesto del diario: granos, pollo, frutas y verduras para el mes.",
  },
  {
    name: "Cuota de la moto",
    amountCop: 354000,
    note: "No negociable. El 7 de noviembre pagaste 360.000.",
  },
  {
    name: "Gasolina",
    amountCop: 80000,
    note: "Presupuesto. El uso completo de la moto, con mantenimiento y seguros, lo estimabas cerca de 250.000.",
  },
] as const;

export const seedMilestones = [
  {
    happenedOn: "2017-03-01",
    title: "Entras a la UFPS",
    detail: "Ingeniería de Sistemas, de marzo de 2017 a marzo de 2025, sin el título. La homologación va hacia la UNAD.",
  },
  {
    happenedOn: "2022-03-01",
    title: "Misión TIC",
    detail: "Diplomado de desarrollo de software en la Universidad Autónoma de Bucaramanga, hasta octubre de 2022.",
  },
  {
    happenedOn: "2023-02-01",
    title: "Inglés Para Todos",
    detail: "Desarrollador full stack con Angular y Laravel en Cúcuta, hasta junio de 2023.",
  },
  {
    happenedOn: "2025-03-01",
    title: "Café Marrón",
    detail: "Freelance. Sitio de la finca, desde marzo de 2025.",
  },
  {
    happenedOn: "2025-05-01",
    title: "Entras a Nelumbo",
    detail: "Analista de calidad de software. El CV cuenta el cargo desde mayo de 2025.",
  },
  {
    happenedOn: "2026-05-26",
    title: "Cierras el semestre 2026-1",
    detail: "Último trabajo de la UNAD. Viste actividad física y salud, bases de datos, ciencia de datos con Python, inglés A2 y sistemas operativos.",
  },
  {
    happenedOn: "2026-05-29",
    title: "Cancelas el gimnasio",
    detail: "Pagaste 1.500.000 de la tarjeta. La cancelación del gym, con esa gestión, te costó 270.000.",
  },
  {
    happenedOn: "2026-07-20",
    title: "Empieza la relación con Katerine",
    detail: "Se oficializó el 20 de julio de 2026.",
  },
  {
    happenedOn: "2026-07-28",
    title: "Dejas el mesero",
    detail: "Fantasía Real. El foco volvió a trabajar como desarrollador.",
  },
  {
    happenedOn: "2026-08-08",
    title: "Compras la TVS 125",
    detail: "Crédito en el Banco de Bogotá. 48 cuotas de 354.000 desde el 5 de octubre de 2026.",
  },
  {
    happenedOn: "2026-08-24",
    title: "Recibes la licencia A2",
    detail: "La reclamaste en los patios. Vigente hasta el 24 de agosto de 2036.",
  },
  {
    happenedOn: "2026-11-06",
    title: "Termina Nelumbo",
    detail: "Acordaron cerrar el contrato, que iba hasta diciembre. La liquidación prevista era 6.841.150, con llegada el 12 de noviembre.",
  },
  {
    happenedOn: "2026-11-10",
    title: "Arranca la homologación",
    detail: "Escribiste que por fin inició el proceso de la UFPS hacia la UNAD.",
  },
  {
    happenedOn: "2026-11-14",
    title: "Cesantías por reclamar",
    detail: "Quedó pendiente pasar el 16 de noviembre a Porvenir, con copia de la cédula y de la terminación del contrato. Confirma si ya las reclamaste.",
  },
] as const;
