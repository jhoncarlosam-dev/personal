(function () {
  var form = document.getElementById("recibo-form");
  var recibo = document.getElementById("recibo");
  var cuerpo = document.getElementById("recibo-cuerpo");
  var filtro = document.getElementById("glosario-q");
  var vacio = document.getElementById("glosario-vacio");

  var plataformas = {
    facebook: "Facebook",
    instagram: "Instagram",
    x: "X"
  };

  var acciones = {
    comprar: {
      nombre: "una compra",
      meta: "El anunciante suele optimizar para una compra. Meta estima la probabilidad de que compres y convierte la puja por compra en el valor de mostrarte el anuncio una vez.",
      x: "En X el anunciante puede pagar por una acción, y una compra suele exigir un clic hacia afuera. El S-1 describe cobro por acciones como clics o interacciones, y también inventario reservado a precio fijo."
    },
    mensaje: {
      nombre: "un mensaje o un dato",
      meta: "La acción elegida suele ser un mensaje, un formulario o un WhatsApp. Meta cobra por producir ese contacto o por la probabilidad de producirlo. Si escribes, la conversación es la conversión.",
      x: "Escribir o dejar un dato en X es una respuesta o un clic. Esa interacción es justo el tipo de acción que el informe dice que el anunciante puede pagar."
    },
    instalar: {
      nombre: "una instalación",
      meta: "La campaña de apps optimiza para la instalación o para una acción dentro de la app. Si instalas, la tienda de aplicaciones y el anunciante le devuelven a Meta la señal de que ocurrió.",
      x: "En X, instalar casi siempre pasa por un clic hacia la tienda. El clic es la acción que la subasta sabe contar con facilidad."
    },
    seguir: {
      nombre: "un seguimiento o un me gusta",
      meta: "Seguir es barato para ti y útil para el anunciante: pasas a ser audiencia de mañana, más fácil de volver a encontrar. Muchas de estas campañas optimizan por interacción, no por una venta de hoy.",
      x: "Un seguimiento en X le da al anunciante una audiencia y le da a la subasta una interacción. También alarga el tiempo en que tu texto y el de otros se cruzan en el mismo lugar."
    },
    mirar: {
      nombre: "una mirada o una reproducción",
      meta: "Hay campañas que pagan por el alcance o por el video visto. En ese caso el anunciante compra la exposición, y la probabilidad que Meta estima es la de que mires, no la de que compres.",
      x: "Ver un video o detenerte en un post promocionado puede ser la acción comprada. El informe dice que buscan anuncios que se sientan como contenido."
    }
  };

  var hechos = {
    nada: "Lo viste y seguiste. Aun así ocupaste un hueco: alguien ganó esa subasta contigo. Si la campaña paga por impresión o por alcance, tu paso ya pudo haber sido el resultado. Si paga por una acción posterior, el anunciante pagó la oportunidad y no obtuvo el resultado.",
    mire: "Te detuviste. En una campaña de video o de alcance, esa pausa puede ser exactamente lo que compraron. En una campaña de ventas, es una señal de atención y todavía no es la conversión.",
    clic: "Hiciste clic. Entregaste una visita: de qué anuncio viniste, a qué hora, y muchas veces desde qué dispositivo. Si del otro lado hay un pixel, la página del anunciante puede contarle a la plataforma que llegaste.",
    converti: "Completaste la acción. El anunciante recibió el resultado por el que pujó. La plataforma recibió la señal de éxito y va a usar gente parecida a ti en la siguiente subasta. Ese círculo es el negocio."
  };

  function parrafo(titulo, texto) {
    var p = document.createElement("p");
    var strong = document.createElement("strong");
    strong.textContent = titulo + " ";
    p.appendChild(strong);
    p.appendChild(document.createTextNode(texto));
    return p;
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var data = new FormData(form);
    var plataforma = String(data.get("plataforma"));
    var accion = String(data.get("accion"));
    var hice = String(data.get("hice"));
    var esMeta = plataforma === "facebook" || plataforma === "instagram";
    var pieza = acciones[accion];
    var nombre = plataformas[plataforma];

    cuerpo.replaceChildren();
    cuerpo.appendChild(parrafo(
      "Dónde.",
      nombre + ". " + (esMeta
        ? "El dinero cae en Meta. Facebook e Instagram son vitrinas de la misma caja."
        : "El dinero del anuncio cae en X, hoy dentro del segmento de inteligencia artificial de SpaceX.")
    ));
    cuerpo.appendChild(parrafo(
      "Qué estaban comprando.",
      pieza.nombre.charAt(0).toUpperCase() + pieza.nombre.slice(1) + ". " + (esMeta ? pieza.meta : pieza.x)
    ));
    cuerpo.appendChild(parrafo("Qué hiciste.", hechos[hice]));
    cuerpo.appendChild(parrafo(
      "Quién es el cliente en este recibo.",
      esMeta
        ? "El anunciante. Tú eres el cliente solo si, aparte, pagas una suscripción como Meta Verified."
        : "El anunciante, si no pagas. Si pagas X Premium, en la suscripción sí eres el cliente, y el anuncio que el plan no quite sigue teniendo otro cliente."
    ));
    cuerpo.appendChild(parrafo(
      "Si quisieras estar del lado que cobra.",
      "Haría falta una oferta con precio, un solo pedido claro y un conteo de cuántas veces ocurre esta misma acción. Los seguidores no son ese conteo."
    ));
    cuerpo.appendChild(parrafo(
      "En inglés.",
      esMeta
        ? "Advertiser bid, estimated action rate, ad quality. Esas tres deciden el hueco."
        : "Advertisers bid to have their ads shown. They can pay for clicks or engagements."
    ));

    recibo.hidden = false;
    recibo.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });

  document.getElementById("filtro").addEventListener("submit", function (event) {
    event.preventDefault();
  });

  filtro.addEventListener("input", function () {
    var needle = filtro.value.trim().toLowerCase();
    var visibles = 0;
    document.querySelectorAll("#glosario div").forEach(function (fila) {
      var coincide = needle === "" || fila.textContent.toLowerCase().indexOf(needle) !== -1;
      fila.hidden = !coincide;
      if (coincide) visibles += 1;
    });
    vacio.hidden = visibles !== 0;
  });
})();
