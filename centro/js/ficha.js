(function () {
  var KEY = "centro.ficha.v1";
  var form = document.getElementById("ficha");
  var estado = document.getElementById("estado");
  var campos = ["oficio", "facebook", "instagram", "x", "frase"];

  function leer() {
    try {
      var crudo = localStorage.getItem(KEY);
      var datos = crudo ? JSON.parse(crudo) : {};
      if (!datos || typeof datos !== "object" || Array.isArray(datos)) return {};
      return datos;
    } catch (error) {
      return {};
    }
  }

  function llenar(datos) {
    campos.forEach(function (nombre) {
      if (typeof datos[nombre] === "string") form.elements[nombre].value = datos[nombre];
    });
  }

  function recoger() {
    var datos = {};
    campos.forEach(function (nombre) {
      datos[nombre] = form.elements[nombre].value.trim();
    });
    return datos;
  }

  function texto(datos) {
    return [
      "Mi ficha — centro de conocimiento",
      "Oficio: " + (datos.oficio || ""),
      "Facebook lo abro para: " + (datos.facebook || ""),
      "Instagram lo abro para: " + (datos.instagram || ""),
      "X lo abro para: " + (datos.x || ""),
      "El trato, en una frase mía: " + (datos.frase || "")
    ].join("\n");
  }

  function avisar(mensaje) {
    estado.textContent = mensaje;
    estado.classList.add("is-on");
    estado.scrollIntoView({ block: "center" });
  }

  llenar(leer());

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var datos = recoger();
    try {
      localStorage.setItem(KEY, JSON.stringify(datos));
      avisar("Guardada en este navegador.");
    } catch (error) {
      avisar("Este navegador no dejó guardar. Puedes copiar la ficha y pegarla en una nota.");
    }
  });

  document.getElementById("copiar").addEventListener("click", function () {
    var plano = texto(recoger());
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(plano).then(function () {
        avisar("Copiada. Pégala donde quieras conservarla.");
      }, function () {
        avisar(plano);
      });
      return;
    }
    avisar(plano);
  });
})();
