export function Locked({ shared = false }: { shared?: boolean }) {
  return (
    <main className="page narrow">
      <p className="kicker">Punto de vida</p>
      <h1>Este cuaderno es privado.</h1>
      <p className="lead">
        {shared
          ? "Si lo publicas para un equipo o para cualquiera, esta pantalla no carga el diario. Ábrelo como privado, solo con tu cuenta."
          : "Hace falta tu sesión para ver el punto en el que estás."}
      </p>
    </main>
  );
}
