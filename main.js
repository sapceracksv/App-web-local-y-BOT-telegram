// main.js
// Este archivo contiene toda la lógica del lado del cliente para la interfaz de búsqueda.

document.addEventListener("DOMContentLoaded", () => {
  // --- Selectores de elementos del DOM ---
  // Se obtienen referencias a todos los elementos interactivos de la página.
  const form = document.getElementById("search-form");
  const resultDiv = document.getElementById("results");
  const errorContainer = document.getElementById("error");
  const paginationDiv = document.getElementById("pagination");
  const searchBtn = document.getElementById("search-btn");
  const clearBtn = document.getElementById("clear-btn");
  const alphabetFilterContainer = document.getElementById("alphabet-filter-container");
  const alphabetFilterDiv = document.getElementById("alphabet-filter");
  const scrollToTopBtn = document.getElementById("scrollToTopBtn");
  const btnText = document.querySelector(".btn-text");
  const loader = document.getElementById("loader");

  // --- Estado de la aplicación ---
  // Variables para gestionar los resultados y la paginación.
  let currentResults = [];
  let currentPage = 1;
  const pageSize = 10; // Resultados por página
  let activeLetter = ''; // Para el filtro alfabético

  // --- Lógica de Búsqueda del Formulario ---
  form.addEventListener("submit", async (e) => {
    e.preventDefault(); // Previene que la página se recargue al enviar el formulario.
    clearUI(false); 
    
    // Muestra el indicador de carga y deshabilita el botón.
    btnText.classList.add("hidden");
    loader.classList.remove("hidden");
    searchBtn.disabled = true;

    // Recolecta los datos del formulario.
    const formData = new FormData(form);
    const params = Object.fromEntries(formData.entries());

    try {
      // Envía los datos al backend (app.py) usando el método POST.
      const res = await fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params) // Convierte los datos a una cadena JSON.
      });
      if (!res.ok) throw new Error((await res.json()).error || res.statusText);

      const data = await res.json();
      handleSearchResults(data); // Procesa la respuesta exitosa.
    } catch (err) {
      handleSearchError(err); // Maneja cualquier error en la petición.
    }
  });

  // --- Manejo de Resultados y Errores ---
  function handleSearchResults(data) {
    // Restaura el botón de búsqueda a su estado normal.
    btnText.classList.remove("hidden");
    loader.classList.add("hidden");
    searchBtn.disabled = false;
    form.reset(); // Limpia los campos del formulario.

    if (!data.length) {
      resultDiv.innerHTML = "<p>No se encontraron resultados para los criterios de búsqueda.</p>";
      alphabetFilterContainer.classList.add("hidden");
      return;
    }

    currentResults = data; // Almacena los resultados globalmente.
    activeLetter = ''; // Resetea el filtro de letra.
    alphabetFilterContainer.classList.remove("hidden"); // Muestra el filtro alfabético.
    renderFilteredResults();
  }

  function handleSearchError(err) {
    btnText.classList.remove("hidden");
    loader.classList.add("hidden");
    searchBtn.disabled = false;
    errorContainer.textContent = `Error al procesar la búsqueda: ${err.message}`;
  }

  // --- Renderizado de la Interfaz ---

  function renderPage(results) {
    resultDiv.innerHTML = "";
    if (!results.length) {
        resultDiv.innerHTML = `<p>No hay resultados que empiecen con la letra '${activeLetter}'.</p>`;
        return;
    }

    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;

    // Itera sobre la porción de resultados que corresponde a la página actual.
    results.slice(start, end).forEach(item => {
      /*
      COMENTARIO PARA EL USUARIO: ¡ATENCIÓN!
      Este código construye la tarjeta de resultados en la página web.
      Las propiedades del objeto 'item' (ej: item.NombreCompleto, item.Dui, item.Placa)
      son las claves del JSON que envía el servidor (app.py), las cuales a su vez
      dependen de los NOMBRES DE COLUMNA o ALIAS de tu consulta SQL en `database.py`.
      
      Si cambias un alias en el SQL (ej: 'SELECT Dui AS Documento'), aquí deberás usar 'item.Documento'.
      */
      const card = document.createElement("div");
      card.className = "result-card";

      // Construye el HTML para la imagen si la URL existe.
      let imageHtml = item.imagen_url ? `<img src="${item.imagen_url}" alt="Imagen del DUI" class="dui-image">` : '';
      
      // Construye el HTML para la información del vehículo si existe.
      let vehicleHtml = item.Placa ? `
        <div class="vehicle-info">
          <h4>Información del Vehículo</h4>
          <p><strong>Placa:</strong> ${item.Placa}</p>
          <p><strong>Marca:</strong> ${item.Marca || '-'}</p>
          <p><strong>Modelo:</strong> ${item.Modelo || '-'}</p>
          <p><strong>Año:</strong> ${item.Año || '-'}</p>
        </div>` : '';
      
      // Construye el HTML para la información laboral si existe.
      let workHtml = item.NombreEmpresa || item.Salario || item.DireccionEmpleadoIsegunSSS ? `
        <div class="work-info">
            <h4>Información Laboral segun ISSS</h4>
            <p><strong>Razon Social de la empresa:</strong> ${item.RasonSocialEmpresa || '-'}</p>
            <p><strong>Salario:</strong> ${item.Salario ? '$' + parseFloat(item.Salario).toFixed(2) : '-'}</p>
            <p><strong>Dirección segun ISSS:</strong> ${item.DireccionEmpleadoISSS || '-'}</p>
        </div>` : '';

      // Ensambla la tarjeta completa con todos los datos.
      card.innerHTML = `
        <button class="card-toggle">
          <span class="card-title">${item.NombreCompleto || 'Sin Nombre'}</span>
          <span class="arrow-icon">▶</span>
        </button>
        <div class="card-collapsible-content">
          <div class="card-header">
              ${imageHtml}
              <div class="result-text-content">
                <p><strong>DUI:</strong> ${item.Dui || '-'}</p>
                <p><strong>Sexo:</strong> ${item.Sexo || '-'}</p>
                <p><strong>Edad:</strong> ${item.Edad || '-'}</p>
                <p><strong>Profesión:</strong> ${item.Profesion || '-'}</p>
              </div>
          </div>
          <div class="card-body">
              <p><strong>Teléfono:</strong> ${item.Telefono || '-'}</p>
              <p><strong>Correo:</strong> ${item.Correo || '-'}</p>
              <p><strong>Dirección:</strong> ${item.Direccion || '-'}</p>
              <p><strong>Calle:</strong> ${item.Calle || '-'}</p>
              <p><strong>Nombre del Padre:</strong> ${item.NombredePadre || '-'}</p>
              <p><strong>Nombre de la Madre:</strong> ${item.NombredeMadre || '-'}</p>
              <p><strong>Cónyuge:</strong> ${item.NombreConyugue || '-'}</p>
          </div>
          ${workHtml}
          ${vehicleHtml}
        </div>
      `;
      
      // Añade el evento para hacer la tarjeta desplegable.
      const toggleButton = card.querySelector(".card-toggle");
      toggleButton.addEventListener("click", () => {
        toggleButton.classList.toggle("active");
        const content = toggleButton.nextElementSibling;
        if (content.style.maxHeight) {
          content.style.maxHeight = null;
        } else {
          content.style.maxHeight = content.scrollHeight + "px";
        }
      });
      
      resultDiv.appendChild(card);
    });
  }

  // --- Funciones de Utilidad y Eventos Adicionales ---
  // (El resto del código maneja la paginación, filtros y el botón de "ir arriba",
  // no depende directamente de la estructura de la base de datos).

  function clearUI(clearFormAndFilter) {
    resultDiv.innerHTML = "";
    paginationDiv.innerHTML = "";
    errorContainer.textContent = "";
    if (clearFormAndFilter) {
      form.reset();
      alphabetFilterContainer.classList.add("hidden");
      currentResults = [];
      activeLetter = '';
    }
    currentPage = 1;
  }

  function renderFilteredResults() {
    let resultsToDisplay = currentResults;
    if (activeLetter) {
      resultsToDisplay = currentResults.filter(item => 
        item.NombreCompleto && item.NombreCompleto.toUpperCase().startsWith(activeLetter)
      );
    }
    currentPage = 1; 
    renderPage(resultsToDisplay);
    renderPagination(resultsToDisplay);
    updateAlphabetButtons();
  }

  function renderPagination(results) {
    // ... (código de paginación)
  }
  
  // ... (resto de funciones auxiliares)
  
  clearBtn.addEventListener("click", () => clearUI(true));
  createAlphabetFilter();
});
