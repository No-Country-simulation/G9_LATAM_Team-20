const API_BASE_URL = "http://127.0.0.1:8000";
let graficaCategorias = null;

// --- ELEMENTOS DE LAS PANTALLAS ---
const welcomeScreen = document.getElementById("welcomeScreen");
const appDashboard = document.getElementById("appDashboard");

const welcomePasswordInput = document.getElementById("welcomePasswordInput");
const obPassword = document.getElementById("obPassword");

// Botones de Navegación del Menú Inicial
const btnIrARegistrado = document.getElementById("btnIrARegistrado");
const btnIrANuevo = document.getElementById("btnIrANuevo");
const btnVolverMenu1 = document.getElementById("btnVolverMenu1");

// Acceso Registrado
const welcomeUserIdInput = document.getElementById("welcomeUserIdInput");
const btnAccederRegistrado = document.getElementById("btnAccederRegistrado");
const btnVerUsuarios = document.getElementById("btnVerUsuarios");
const btnVolverMenu2 = document.getElementById("btnVolverMenu2");
const usersListContainer = document.getElementById("usersListContainer");

// Registro Onboarding
const btnSiguienteSlide1 = document.getElementById("btnSiguienteSlide1");
const btnRegistrarNuevoUsuario = document.getElementById("btnRegistrarNuevoUsuario");
const lblNuevoUserId = document.getElementById("lblNuevoUserId");
const btnEntrarApp = document.getElementById("btnEntrarApp");
const btnCerrarSesion = document.getElementById("btnCerrarSesion");

// Elementos de captura en Onboarding
const obNombre = document.getElementById("obNombre");
const obMetaAhorro = document.getElementById("obMetaAhorro");
const obEdad = document.getElementById("obEdad");
const obSexo = document.getElementById("obSexo");
const obOcupacion = document.getElementById("obOcupacion");
const obCiudad = document.getElementById("obCiudad");
const obIngreso = document.getElementById("obIngreso");
const obDeuda = document.getElementById("obDeuda");

// Elementos del Header del Dashboard
const lblNombreUsuario = document.getElementById("lblNombreUsuario");
const lblIdUsuario = document.getElementById("lblIdUsuario");
const userAvatar = document.getElementById("userAvatar");

// Formulario de Usuario en Dashboard
const userIdInput = document.getElementById("userIdInput");
const userForm = document.getElementById("userForm");
const userNombre = document.getElementById("userNombre");
const userEdad = document.getElementById("userEdad");
const userSexo = document.getElementById("userSexo");
const userOcupacion = document.getElementById("userOcupacion");
const userCiudad = document.getElementById("userCiudad");
const userIngresoBase = document.getElementById("userIngresoBase");
const userIngresoVar = document.getElementById("userIngresoVar");
const userMetaAhorro = document.getElementById("userMetaAhorro");
const userDeuda = document.getElementById("userDeuda");
const btnEliminarUsuario = document.getElementById("btnEliminarUsuario");

// Dashboard Salud
const healthBadge = document.getElementById("healthBadge");
const valIngresos = document.getElementById("valIngresos");
const valAhorro = document.getElementById("valAhorro");
const valPorcAhorro = document.getElementById("valPorcAhorro");
const txtRecomendacion = document.getElementById("txtRecomendacion");
const saludEmptyState = document.getElementById("saludEmptyState");
const saludContent = document.getElementById("saludContent");

// Transacciones
const transactionForm = document.getElementById("transactionForm");
const txEditId = document.getElementById("txEditId");
const txDesc = document.getElementById("txDesc");
const txMonto = document.getElementById("txMonto");
const txFecha = document.getElementById("txFecha");
const txTipo = document.getElementById("txTipo");
const txCategoria = document.getElementById("txCategoria");
// escuchador de eventos inicio
const iaConfianzaBadge = document.getElementById("iaConfianzaBadge");

txDesc.addEventListener("blur", async () => {
    const descripcion = txDesc.value.trim();
    if (!descripcion) {
        iaConfianzaBadge.style.display = "none";
        return;
    }

    try {
        const respuesta = await fetch(`${API_BASE_URL}/clasificar-gasto`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ descripcion: descripcion })
        });

        if (respuesta.ok) {
            const resultado = await respuesta.json();
            txCategoria.value = resultado.categoria;

            
            iaConfianzaBadge.style.display = "inline-block";

            if (resultado.requiere_revision) {
                iaConfianzaBadge.classList.add("baja-confianza");
                iaConfianzaBadge.innerText = `⚠️ Categoria Sugerida por IA — revisa la categoría`;
            } else {
                iaConfianzaBadge.classList.remove("baja-confianza");
                iaConfianzaBadge.innerText = `✨ Categoria Sugerida por IA)`;
            }
        }
    } catch (e) {
        iaConfianzaBadge.style.display = "none";
    }
});

// escuchador de eventos fin

const btnSubmitTx = document.getElementById("btnSubmitTx");
const btnCancelTxEdit = document.getElementById("btnCancelTxEdit");

// Pestaña Resumen Mensual (NUEVO)
const resIngresos = document.getElementById("resIngresos");
const resGastos = document.getElementById("resGastos");
const resumenCategoriasContainer = document.getElementById("resumenCategoriasContainer");

// Filtros Globales (NUEVO)
const filtroAnio = document.getElementById("filtroAnio");
const filtroMes = document.getElementById("filtroMes");
const btnFiltrar = document.getElementById("btnFiltrar");
const txTableBody = document.getElementById("txTableBody");


// --- CONTROL DE PESTAÑAS (TABS) ---
window.cambiarTab = function(tabName) {
    // 1. Ocultar todas las pestañas
    document.querySelectorAll(".tab-content").forEach(content => {
        content.classList.remove("active-tab");
    });
    
    // 2. Desactivar estilo activo de todos los botones de la barra flotante
    document.querySelectorAll(".nav-item").forEach(item => {
        item.classList.remove("active");
    });

    // 3. Mostrar la pestaña elegida y activar su botón
    document.getElementById(`tab-${tabName}`).classList.add("active-tab");
    
    // Encontrar el botón pulsado por su atributo onClick
    const btnActivo = Array.from(document.querySelectorAll(".nav-item")).find(btn => {
        return btn.getAttribute("onclick").includes(tabName);
    });
    if (btnActivo) btnActivo.classList.add("active");
};


// --- LÓGICA DE CONTROL DE DIAPOSITIVAS (ONBOARDING) ---
window.cambiarSlide = function(slideActualId, slideSiguienteId) {
    document.getElementById(slideActualId).classList.remove("active");
    document.getElementById(slideSiguienteId).classList.add("active");
};

btnIrARegistrado.addEventListener("click", () => cambiarSlide("slide-menu", "slide-login"));
btnVolverMenu1.addEventListener("click", () => cambiarSlide("slide-login", "slide-menu"));
btnIrANuevo.addEventListener("click", () => cambiarSlide("slide-menu", "slide-1"));

btnSiguienteSlide1.addEventListener("click", () => {
    if (!obNombre.value.trim()) {
        alert("Por favor, dinos tu nombre para poder continuar.");
        return;
    }
    if (!obPassword.value.trim()) {
        alert("Por favor, crea una contraseña para poder continuar.");
        return;
    }
    cambiarSlide("slide-1", "slide-2");
});


window.mostrarOcultarPassword = function(inputId, icono) {
    const input = document.getElementById(inputId);
    if (input.type === "password") {
        input.type = "text";
        icono.innerText = "🙈";
    } else {
        input.type = "password";
        icono.innerText = "👁️";
    }
};


btnAccederRegistrado.addEventListener("click", async () => {
    const id = parseInt(welcomeUserIdInput.value);
    const password = welcomePasswordInput.value;

    if (!id || !password) {
        alert("Por favor ingresa tu ID y tu contraseña.");
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: id, password: password })
        });

        if (response.ok) {
            userIdInput.value = id;
            await cargarUsuario(id);
            welcomeScreen.style.display = "none";
            appDashboard.style.display = "block";
            cambiarTab("salud");
        } else if (response.status === 401) {
            alert("❌ Contraseña incorrecta.");
        } else {
            alert("❌ ID de usuario no registrado.");
        }
    } catch (e) {
        alert("❌ Error al conectar con el servidor.");
    }
});


btnRegistrarNuevoUsuario.addEventListener("click", async () => {
    const objetivoSeleccionado = document.querySelector('input[name="objetivo"]:checked').value;
    const datosUsuario = {
        nombre: obNombre.value.trim(),
        password: obPassword.value,
        edad: parseInt(obEdad.value) || 25,
        sexo: obSexo.value,
        ocupacion: `${obOcupacion.value || "Estudiante"} (${objetivoSeleccionado})`,
        ciudad: obCiudad.value || "Desconocida",
        ingreso_base: parseFloat(obIngreso.value) || 1000.0,
        ingreso_variable: 0.0,
        meta_ahorro: parseFloat(obMetaAhorro.value) || 20.0,
        nivel_deuda_inicial: parseFloat(obDeuda.value) || 0.0
    };

    try {
        const response = await fetch(`${API_BASE_URL}/usuarios`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(datosUsuario)
        });
        if (response.ok) {
            const usuarioCreado = await response.json();
            lblNuevoUserId.innerText = usuarioCreado.id;
            userIdInput.value = usuarioCreado.id;
            cambiarSlide("slide-5", "slide-success");
        } else {
            alert("❌ Error en la base de datos.");
        }
    } catch (e) {
        alert("❌ Error al conectar.");
    }
});



btnEntrarApp.addEventListener("click", async () => {
    const id = parseInt(userIdInput.value);
    await cargarUsuario(id);
    welcomeScreen.style.display = "none";
    appDashboard.style.display = "block";
    cambiarTab("salud");
});

btnCerrarSesion.addEventListener("click", () => {
    welcomeUserIdInput.value = "";
    obNombre.value = "";
    userForm.reset();
    resetDashboard();
    appDashboard.style.display = "none";
    welcomeScreen.style.display = "flex";
    document.querySelectorAll(".onboarding-slide").forEach(s => s.classList.remove("active"));
    document.getElementById("slide-menu").classList.add("active");
});

btnVerUsuarios.addEventListener("click", () => {
    cambiarSlide("slide-menu", "slide-users-list");
    cargarListadoUsuarios();
});

btnVolverMenu2.addEventListener("click", () => {
    cambiarSlide("slide-users-list", "slide-menu");
});

async function cargarListadoUsuarios() {
    usersListContainer.innerHTML = `<p class="text-center">Cargando usuarios registrados...</p>`;
    try {
        const response = await fetch(`${API_BASE_URL}/usuarios`);
        if (!response.ok) throw new Error();
        const usuarios = await response.json();
        usersListContainer.innerHTML = "";
        
        if (usuarios.length === 0) {
            usersListContainer.innerHTML = `<p class="text-center">No hay usuarios registrados aún.</p>`;
            return;
        }

        usuarios.forEach(u => {
            const card = document.createElement("div");
            card.className = "user-list-card";
            card.setAttribute("onclick", `loginDirecto(${u.id})`);
            card.innerHTML = `
                <div class="avatar-circle" style="width:36px; height:36px; font-size:1rem;">
                    ${u.nombre.charAt(0).toUpperCase()}
                </div>
                <div class="user-badge-info" style="flex:1;">
                    <span class="user-welcome"><strong>${u.nombre}</strong></span>
                    <span class="user-id-capsule">ID: #${u.id}</span>
                </div>
                <span style="font-size:1.1rem; color:var(--text-secondary);">➡️</span>
            `;
            usersListContainer.appendChild(card);
        });
    } catch (e) {
        usersListContainer.innerHTML = `<p class="text-center" style="color:var(--status-danger);">Error de conexión.</p>`;
    }
}

window.loginDirecto = function(id) {
    welcomeUserIdInput.value = id;
    welcomePasswordInput.value = "";
    cambiarSlide("slide-users-list", "slide-login");
};

// --- LÓGICA CORE DE LA APLICACIÓN ---

async function cargarUsuario(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/usuarios/${id}`);
        if (!response.ok) throw new Error();
        const usuario = await response.json();
        
        lblNombreUsuario.innerText = usuario.nombre;
        lblIdUsuario.innerText = `ID: #${usuario.id}`;
        userAvatar.innerText = usuario.nombre.charAt(0).toUpperCase();

        userNombre.value = usuario.nombre;
        userEdad.value = usuario.edad;
        userSexo.value = usuario.sexo;
        userOcupacion.value = usuario.ocupacion;
        userCiudad.value = usuario.ciudad;
        userIngresoBase.value = usuario.ingreso_base;
        userIngresoVar.value = usuario.ingreso_variable;
        userMetaAhorro.value = usuario.meta_ahorro;
        userDeuda.value = usuario.nivel_deuda_inicial;

        actualizarDashboard(id);
    } catch (error) {
        alert("Error al cargar los datos del usuario.");
    }
}

userForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = parseInt(userIdInput.value);
    const datosUsuario = {
        nombre: userNombre.value,
        edad: parseInt(userEdad.value),
        sexo: userSexo.value,
        ocupacion: userOcupacion.value,
        ciudad: userCiudad.value,
        ingreso_base: parseFloat(userIngresoBase.value),
        ingreso_variable: parseFloat(userIngresoVar.value),
        meta_ahorro: parseFloat(userMetaAhorro.value),
        nivel_deuda_inicial: parseFloat(userDeuda.value)
    };

    try {
        const response = await fetch(`${API_BASE_URL}/usuarios/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(datosUsuario)
        });
        if (response.ok) {
            alert("✅ Perfil modificado correctamente.");
            cargarUsuario(id);
        }
    } catch (e) {
        alert("Error al guardar.");
    }
});

btnEliminarUsuario.addEventListener("click", async () => {
    const id = parseInt(userIdInput.value);
    if (!confirm(`¿Eliminar usuario ${id}?`)) return;
    try {
        const response = await fetch(`${API_BASE_URL}/usuarios/${id}`, { method: "DELETE" });
        if (response.ok) {
            alert("Perfil borrado.");
            btnCerrarSesion.click();
        }
    } catch (e) {
        alert("Error.");
    }
});

async function actualizarDashboard(id) {
    const anio = parseInt(filtroAnio.value);
    const mes = parseInt(filtroMes.value);

    // 1. Obtener Perfil Salud
    try {
        const resPerfil = await fetch(`${API_BASE_URL}/perfil/${id}?anio=${anio}&mes=${mes}`);
        if (resPerfil.ok) {
            const perfil = await resPerfil.json();

            saludEmptyState.style.display = "none";
            saludContent.style.display = "block";

            healthBadge.innerText = perfil.perfil;
            healthBadge.className = "";
            if (perfil.perfil.toLowerCase() === "saludable") healthBadge.classList.add("badge-healthy");
            else if (perfil.perfil.toLowerCase() === "en observación" || perfil.perfil.toLowerCase() === "en observacion") healthBadge.classList.add("badge-warning");
            else healthBadge.classList.add("badge-danger");

            valIngresos.innerText = `$${perfil.ingreso_total.toFixed(2)}`;
            valAhorro.innerText = `$${perfil.ahorro_real.toFixed(2)}`;
            valPorcAhorro.innerText = `${perfil.porcentaje_ahorro_real}%`;
            txtRecomendacion.innerText = perfil.recomendacion;
        } else {
            saludEmptyState.style.display = "block";
            saludContent.style.display = "none";
        }
    } catch (e) {
        saludEmptyState.style.display = "block";
        saludContent.style.display = "none";
    }

    // 2. Obtener Historial de Transacciones
    try {
        const resTx = await fetch(`${API_BASE_URL}/transacciones/${id}`);
        if (resTx.ok) {
            const todas = await resTx.json();
            const filtradas = todas.filter(t => {
                const f = new Date(t.fecha);
                return f.getFullYear() === anio && (f.getMonth() + 1) === mes;
            });
            dibujarTabla(filtradas);
        }
    } catch (e) {}

    // 3. Obtener Resumen Mensual (Pestaña 3) (NUEVO)
    try {
        const resResumen = await fetch(`${API_BASE_URL}/resumen-mensual/${id}?anio=${anio}&mes=${mes}`);
        if (resResumen.ok) {
            const data = await resResumen.json();
            resIngresos.innerText = `$${data.ingresos_totales.toFixed(2)}`;
            resGastos.innerText = `$${data.gastos_totales.toFixed(2)}`;
            dibujarResumenCategorias(data.gastos_por_categoria, data.gastos_totales);
            dibujarGraficaCategorias(data.gastos_por_categoria);
           
        } else {
            resIngresos.innerText = "$0.00";
            resGastos.innerText = "$0.00";
            resumenCategoriasContainer.innerHTML = `<p class="text-center">No hay registros para este periodo.</p>`;
        }
    } catch (e) {
        resumenCategoriasContainer.innerHTML = `<p class="text-center">Error al cargar estadísticas.</p>`;
    }
}


 // se agrega codigo para las graficas
            function dibujarGraficaCategorias(gastosPorCategoria) {
            const etiquetas = Object.keys(gastosPorCategoria);
            const valores = Object.values(gastosPorCategoria);

            if (graficaCategorias) {
                graficaCategorias.destroy();
             }

            const contexto = document.getElementById("graficaCategorias").getContext("2d");

            if (etiquetas.length === 0) {
                return;
            }

            graficaCategorias = new Chart(contexto, {
                type: "doughnut",
                 data: {
                    labels: etiquetas.map(cat => cat.charAt(0).toUpperCase() + cat.slice(1)),
                    datasets: [{
                        data: valores,
                        backgroundColor: ["#38bdf8", "#818cf8", "#f43f5e", "#fbbf24", "#10b981", "#f472b6", "#22d3ee", "#fb923c"],
                        borderColor: "#111827",
                        borderWidth: 2
                    }]
                },
                options: {
                    plugins: {
                        legend: {
                            position: "bottom",
                            labels: { color: "#9ca3af", padding: 12, font: { family: "Outfit" } }
                        }
                    }
                }
            });
            }


            // fin codigo agregado

// Pintar barras de progreso por categoría de gasto (NUEVO)
function dibujarResumenCategorias(gastosPorCategoria, gastosTotales) {
    resumenCategoriasContainer.innerHTML = "";
    
    const llaves = Object.keys(gastosPorCategoria);
    if (llaves.length === 0) {
        resumenCategoriasContainer.innerHTML = `<p class="text-center">No hay gastos en este periodo.</p>`;
        return;
    }

    // Ordenar de mayor a menor gasto
    llaves.sort((a, b) => gastosPorCategoria[b] - gastosPorCategoria[a]);

    llaves.forEach(cat => {
        const monto = gastosPorCategoria[cat];
        const porcentaje = gastosTotales > 0 ? ((monto / gastosTotales) * 100) : 0;
        
        const row = document.createElement("div");
        row.className = "progress-row";
        
        // Emojis lúdicos según la categoría
        let emoji = "🏷️";
        if (cat === "alimentacion") emoji = "🍔";
        else if (cat === "transporte") emoji = "🚗";
        else if (cat === "salud") emoji = "⚕️";
        else if (cat === "vivienda") emoji = "🏠";
        else if (cat === "educacion") emoji = "🎓";
        else if (cat === "servicios") emoji = "💡";
        else if (cat === "deudas") emoji = "💳";
        else if (cat === "entretenimiento") emoji = "🎮";
        else if (cat === "compras") emoji = "🛍️";
        else if (cat === "finanzas") emoji = "💰";
        else if (cat === "otros") emoji = "🏷️";

        row.innerHTML = `
            <div class="progress-info">
                <span class="progress-cat-name">${emoji} ${cat.charAt(0).toUpperCase() + cat.slice(1)}</span>
                <span class="progress-cat-amount">$${monto.toFixed(2)} (${porcentaje.toFixed(0)}%)</span>
            </div>
            <div class="progress-bar-track">
                <div class="progress-bar-fill" style="width: ${porcentaje}%"></div>
            </div>
        `;
        resumenCategoriasContainer.appendChild(row);
    });
}

function dibujarTabla(lista) {
    txTableBody.innerHTML = "";
    if (lista.length === 0) {
        txTableBody.innerHTML = `<tr><td colspan="5" class="text-center">Sin transacciones registradas.</td></tr>`;
        return;
    }
    lista.forEach(t => {
        const fila = document.createElement("tr");
        const fechaLegible = new Date(t.fecha).toLocaleDateString('es-ES', {
            day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'
        });
        const esGasto = t.tipo.toLowerCase() === "gasto";
        fila.innerHTML = `
            <td>${fechaLegible}</td>
            <td>${t.descripcion}</td>
            <td>${t.categoria}</td>
            <td class="${esGasto ? 'monto-gasto' : 'monto-ingreso'}">${esGasto ? '-' : '+'} $${t.monto.toFixed(2)}</td>
            <td>
                <button class="btn-secondary" onclick="iniciarEdicionTransaccion(${t.id}, '${t.descripcion}', ${t.monto}, '${t.tipo}', '${t.categoria}', '${t.fecha}')" style="padding: 0.4rem 0.8rem; font-size: 0.8rem; margin-right: 4px;">Editar</button>
                <button class="btn-danger" onclick="eliminarTransaccion(${t.id})">Borrar</button>
            </td>
        `;
        txTableBody.appendChild(fila);
    });
}

btnSubmitTx.addEventListener("click", async () => {
    const id = parseInt(userIdInput.value);
    const editId = txEditId.value;
    const datosTransaccion = {
        usuario_id: id,
        categoria: txCategoria.value,
        tipo: txTipo.value,
        monto: parseFloat(txMonto.value),
        descripcion: txDesc.value,
        fecha: txFecha.value ? new Date(txFecha.value).toISOString() : null
    };

    try {
        const url = editId ? `${API_BASE_URL}/transacciones/${editId}` : `${API_BASE_URL}/transacciones`;
        const method = editId ? "PUT" : "POST";
        const response = await fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(datosTransaccion)
        });
        if (response.ok) {
            cancelarEdicion();
            actualizarDashboard(id);
        }
    } catch (e) {}
});

window.iniciarEdicionTransaccion = function(id, desc, monto, tipo, category, fechaStr) {
    // Al hacer clic en editar, cambiamos de pestaña a Movimientos automáticamente
    cambiarTab('transacciones');

    txEditId.value = id;
    txDesc.value = desc;
    txMonto.value = monto;
    txTipo.value = tipo;
    txCategoria.value = category;
    if (fechaStr) {
        const d = new Date(fechaStr);
        txFecha.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}T${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
    }
    btnSubmitTx.innerText = "Guardar Cambios";
    btnCancelTxEdit.style.display = "inline-block";
    transactionForm.scrollIntoView({ behavior: 'smooth' });
};

function cancelarEdicion() {
    txEditId.value = "";
    transactionForm.reset();
    btnSubmitTx.innerText = "Agregar Movimiento";
    btnCancelTxEdit.style.display = "none";
    iaConfianzaBadge.style.display = "none";
}
btnCancelTxEdit.addEventListener("click", cancelarEdicion);

async function eliminarTransaccion(txId) {
    if (!confirm("¿Deseas eliminar esta transacción?")) return;
    try {
        const res = await fetch(`${API_BASE_URL}/transacciones/${txId}`, { method: "DELETE" });
        if (res.ok) actualizarDashboard(parseInt(userIdInput.value));
    } catch (e) {}
}

function resetDashboard(mensaje = "Por favor, registra movimientos para analizar.") {
    healthBadge.innerText = "Sin Datos";
    healthBadge.className = "badge-loading";
    valIngresos.innerText = "$0.00";
    valAhorro.innerText = "$0.00";
    valPorcAhorro.innerText = "0%";
    txtRecomendacion.innerText = mensaje;
    txTableBody.innerHTML = `<tr><td colspan="5" class="text-center">Ingresa transacciones para ver el historial.</td></tr>`;
    
    // Resetear resumen
    resIngresos.innerText = "$0.00";
    resGastos.innerText = "$0.00";
    resumenCategoriasContainer.innerHTML = "";
}

btnFiltrar.addEventListener("click", () => actualizarDashboard(parseInt(userIdInput.value)));