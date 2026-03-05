

        let proyectos = [];
        let catalogData = {
            areas: [],
            financiamientos: [],
            estados_proyecto: [],
            etapas_proyecto: [],
            estados_postulacion: [],
            sectores: [],
            lineamientos_estrategicos: []
        };
        let editingId = null;
        let columnsVisible = false;

        async function loadCatalogData() {
            try {
                const resources = [
                    'areas', 'financiamientos', 'estados_proyecto',
                    'etapas_proyecto', 'estados_postulacion', 'sectores',
                    'lineamientos_estrategicos'
                ];

                const results = await Promise.all(
                    resources.map(res => api.get(`/${res}`).catch(() => []))
                );

                resources.forEach((res, index) => {
                    catalogData[res] = results[index].sort((a, b) =>
                        (a.nombre || '').localeCompare(b.nombre || '')
                    );
                });

                populateFormSelects();
                populateFilterSelects();
            } catch (error) {
                console.error('Error cargando catálogos:', error);
                showToast('Error al sincronizar datos', 'error');
            }
        }

        function populateFilterSelects() {

            populateSelectOptions('filterArea', catalogData.areas.map(a => a.nombre), 'Todas');
            populateSelectOptions('filterFinancing', catalogData.financiamientos.map(f => f.nombre), 'Todos');
            populateSelectOptions('filterStatus', catalogData.estados_proyecto.map(e => e.nombre), 'Todos');

        }

        function populateFormSelects() {
            const fillSelect = (elementId, data, defaultText) => {
                const select = document.getElementById(elementId);
                if (!select) return;

                const currentVal = select.value;

                select.innerHTML = `<option value="">${defaultText}</option>`;
                data.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item.id;
                    option.textContent = item.nombre;
                    select.appendChild(option);
                });

                if (currentVal) select.value = currentVal;
            };

            fillSelect('area_id', catalogData.areas, 'Seleccione Área');
            fillSelect('financiamiento_id', catalogData.financiamientos, 'Seleccione Financiamiento');
            fillSelect('estado_proyecto_id', catalogData.estados_proyecto, 'Seleccione Estado');
            fillSelect('etapa_proyecto_id', catalogData.etapas_proyecto, 'Seleccione Etapa');
            fillSelect('estado_postulacion_id', catalogData.estados_postulacion, 'Seleccione Estado Postulación');
            fillSelect('sector_id', catalogData.sectores, 'Seleccione Sector');
            fillSelect('lineamiento_estrategico_id', catalogData.lineamientos_estrategicos, 'Seleccione Lineamiento');
        }

        function formatDateForInput(dateString) {
            if (!dateString) return '';
            if (typeof dateString === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
                return dateString;
            }
            const dateObj = new Date(dateString);
            if (isNaN(dateObj.getTime())) return dateString;
            const year = dateObj.getFullYear();
            const month = String(dateObj.getMonth() + 1).padStart(2, '0');
            const day = String(dateObj.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        }

        function formatDisplayDate(dateString) {
            if (!dateString) return '-';
            try {
                const date = new Date(dateString);
                return date.toLocaleDateString('es-CL', {
                    year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
                });
            } catch (e) {
                return dateString;
            }
        }

        document.addEventListener('DOMContentLoaded', function () {
            checkLoginStatus();

            loadCatalogData().then(() => {
                loadProjects();
            });

            document.getElementById('searchInput').addEventListener('input', applyFilters);
            document.getElementById('filterArea').addEventListener('change', applyFilters);
            document.getElementById('filterFinancing').addEventListener('change', applyFilters);
            document.getElementById('filterStatus').addEventListener('change', applyFilters);
            document.getElementById('filterProfessional').addEventListener('change', applyFilters);

            document.getElementById('proyectoForm').addEventListener('submit', handleSubmit);
        });

        async function loadProjects() {
            try {
                const tableBody = document.getElementById('projectsTableBody');
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="8" class="text-center py-12">
                            <div class="flex flex-col items-center justify-center">
                                <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mb-4"></div>
                                <p class="text-gray-500 font-medium">Cargando proyectos...</p>
                            </div>
                        </td>
                    </tr>
                `;

                proyectos = await api.get('/proyectos');

                proyectos.sort((a, b) => {
                    const dateA = new Date(a.fecha_actualizacion || a.fecha_postulacion || 0);
                    const dateB = new Date(b.fecha_actualizacion || b.fecha_postulacion || 0);
                    const diff = dateB - dateA;
                    if (diff !== 0) return diff;
                    return (a.nombre || '').localeCompare(b.nombre || '');
                });

                updateFilterOptions();
                applyFilters();

                const today = new Date();
                const formattedDate = today.toLocaleDateString('es-ES', {
                    day: '2-digit', month: '2-digit', year: 'numeric'
                });
                document.getElementById('lastUpdate').textContent = formattedDate;
            } catch (error) {
                console.error('Error:', error);
                showToast('Error al cargar los proyectos', 'error');
            }
        }

        function populateSelectOptions(selectElementId, optionsList, defaultLabel, currentValue) {
            const select = document.getElementById(selectElementId);
            const previousValue = select.value;
            let html = `<option value="">${defaultLabel}</option>`;
            optionsList.forEach(opt => {
                html += `<option value="${opt}" ${opt === previousValue ? 'selected' : ''}>${opt}</option>`;
            });
            select.innerHTML = html;
            if (previousValue && !optionsList.includes(previousValue)) {
                select.value = "";
            } else if (previousValue) {
                select.value = previousValue;
            }
        }

        function getProfessionalsFromProject(p) {
            const profs = [
                p.profesional_1,
                p.profesional_2,
                p.profesional_3,
                p.profesional_4,
                p.profesional_5
            ].filter(Boolean);
            return profs;
        }

        function updateFilterOptions() {
            const selectedArea = document.getElementById('filterArea').value;
            const selectedFinancing = document.getElementById('filterFinancing').value;
            const selectedStatus = document.getElementById('filterStatus').value;
            const selectedProfessional = document.getElementById('filterProfessional').value;

            const dataForAreas = proyectos.filter(p => {
                const profs = getProfessionalsFromProject(p);
                const matchesPro = selectedProfessional === '' || profs.includes(selectedProfessional);
                return matchesPro &&
                    (selectedFinancing === '' || p.financiamiento_nombre === selectedFinancing) &&
                    (selectedStatus === '' || p.estado_nombre === selectedStatus);
            });
            const uniqueAreas = [...new Set(dataForAreas.map(p => p.area_nombre).filter(Boolean))].sort();
            populateSelectOptions('filterArea', uniqueAreas, 'Todas las áreas', selectedArea);

            const dataForFinancing = proyectos.filter(p => {
                const profs = getProfessionalsFromProject(p);
                const matchesPro = selectedProfessional === '' || profs.includes(selectedProfessional);
                return matchesPro &&
                    (selectedArea === '' || p.area_nombre === selectedArea) &&
                    (selectedStatus === '' || p.estado_nombre === selectedStatus);
            });
            const uniqueFinancing = [...new Set(dataForFinancing.map(p => p.financiamiento_nombre).filter(Boolean))].sort();
            populateSelectOptions('filterFinancing', uniqueFinancing, 'Todo el financiamiento', selectedFinancing);

            const dataForStatus = proyectos.filter(p => {
                const profs = getProfessionalsFromProject(p);
                const matchesPro = selectedProfessional === '' || profs.includes(selectedProfessional);
                return matchesPro &&
                    (selectedArea === '' || p.area_nombre === selectedArea) &&
                    (selectedFinancing === '' || p.financiamiento_nombre === selectedFinancing);
            });
            const uniqueStatus = [...new Set(dataForStatus.map(p => p.estado_nombre).filter(Boolean))].sort();
            populateSelectOptions('filterStatus', uniqueStatus, 'Todos los estados', selectedStatus);

            const dataForProfessionals = proyectos.filter(p =>
                (selectedArea === '' || p.area_nombre === selectedArea) &&
                (selectedFinancing === '' || p.financiamiento_nombre === selectedFinancing) &&
                (selectedStatus === '' || p.estado_nombre === selectedStatus)
            );
            const allProfessionalsList = dataForProfessionals.flatMap(getProfessionalsFromProject);
            const uniqueProfessionals = [...new Set(allProfessionalsList)].sort();
            populateSelectOptions('filterProfessional', uniqueProfessionals, 'Todos los profesionales', selectedProfessional);
        }

        function applyFilters() {
            updateFilterOptions();

            const selectedArea = document.getElementById('filterArea').value;
            const selectedFinancing = document.getElementById('filterFinancing').value;
            const selectedStatus = document.getElementById('filterStatus').value;
            const selectedProfessional = document.getElementById('filterProfessional').value;
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();

            const filteredData = proyectos.filter(proyecto => {
                const matchesSearch =
                    (proyecto.nombre && proyecto.nombre.toLowerCase().includes(searchTerm)) ||
                    (proyecto.codigo && proyecto.codigo.toLowerCase().includes(searchTerm)) ||
                    (proyecto.sector_nombre && proyecto.sector_nombre.toLowerCase().includes(searchTerm));

                const matchesArea = selectedArea === '' || proyecto.area_nombre === selectedArea;
                const matchesFinancing = selectedFinancing === '' || proyecto.financiamiento_nombre === selectedFinancing;
                const matchesStatus = selectedStatus === '' || proyecto.estado_nombre === selectedStatus;

                const projectProfessionals = getProfessionalsFromProject(proyecto);
                const matchesProfessional = selectedProfessional === '' || projectProfessionals.includes(selectedProfessional);

                return matchesSearch && matchesArea && matchesFinancing && matchesStatus && matchesProfessional;
            });

            renderProyectos(filteredData);
            updateKPIs(filteredData);
            updateCount(filteredData.length);
        }

        function clearFilters() {
            document.getElementById('searchInput').value = '';
            document.getElementById('filterArea').value = '';
            document.getElementById('filterFinancing').value = '';
            document.getElementById('filterStatus').value = '';
            document.getElementById('filterProfessional').value = '';
            applyFilters();
        }

        function renderSkeleton(container, rows = 5) {
            container.innerHTML = Array(rows).fill(0).map(() => `
                <tr class="animate-pulse">
                    ${Array(8).fill(0).map(() => `
                        <td class="py-4 px-4">
                            <div class="h-4 bg-gray-200 rounded w-full"></div>
                        </td>
                    `).join('')}
                </tr>
            `).join('');
        }

        function renderProyectos(proyectosToRender) {
            const tableBody = document.getElementById('projectsTableBody');
            if (proyectosToRender.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="8" class="text-center py-12">
                            <div class="flex flex-col items-center justify-center text-gray-400">
                                <i class="fas fa-folder-open text-5xl mb-4 text-gray-300"></i>
                                <p class="text-lg font-medium text-gray-500">No se encontraron proyectos</p>
                                <p class="text-sm">Intenta ajustar los filtros de búsqueda</p>
                            </div>
                        </td>
                    </tr>
                `;
                return;
            }

            const visibilityClass = columnsVisible ? 'toggle-column-visible' : '';

            tableBody.innerHTML = proyectosToRender.map(proyecto => {
                let statusClass = utils.getStatusClass(proyecto.estado_nombre || '');
                let statusText = proyecto.estado_nombre || 'Sin Estado';
                let badgeStyle = proyecto.estado_color ? `background-color: ${proyecto.estado_color}; color: white;` : '';

                let progressClass = '';
                const progress = proyecto.avance_total_porcentaje ? parseFloat(proyecto.avance_total_porcentaje) : 0;
                const displayProgress = (progress > 1 ? progress : progress * 100);

                if (displayProgress < 25) progressClass = 'bg-rose-500';
                else if (displayProgress < 50) progressClass = 'bg-amber-500';
                else if (displayProgress < 75) progressClass = 'bg-blue-500';
                else progressClass = 'bg-emerald-500';

                return `
                    <tr class="hover:bg-indigo-50/30 transition-colors duration-150 group">
                        <td class="toggle-column ${visibilityClass} font-medium text-gray-400 text-xs text-center">${proyecto.id || ''}</td>
                        <td class="font-semibold text-gray-700 group-hover:text-indigo-600 transition-colors">${proyecto.nombre || ''}</td>
                        <td class="text-gray-600 toggle-column ${visibilityClass}">${proyecto.area_nombre || ''}</td>
                        <td class="text-gray-600 toggle-column ${visibilityClass}">${proyecto.financiamiento_nombre || ''}</td>
                        <td class="font-mono text-gray-600 toggle-column ${visibilityClass}">${utils.formatCurrency(proyecto.monto)}</td>
                        <td class="toggle-column ${visibilityClass}">
                            <span class="status-badge ${statusClass}" style="${badgeStyle}">
                                ${statusText}
                            </span>
                        </td>
                        <td class="toggle-column ${visibilityClass}">
                            <div class="flex items-center gap-3">
                                <div class="w-full bg-gray-100 rounded-full h-2 shadow-inner overflow-hidden">
                                    <div class="${progressClass} h-2 rounded-full transition-all duration-500 relative" style="width: ${displayProgress}%">
                                        <div class="absolute inset-0 bg-white/20"></div>
                                    </div>
                                </div>
                                <span class="text-xs font-bold text-gray-500 w-9 text-right">${displayProgress.toFixed(0)}%</span>
                            </div>
                        </td>
                        <td>
                            <div class="flex items-center gap-1">
                                <button onclick="viewProject(${proyecto.id})" class="p-2 text-indigo-500 hover:bg-indigo-50 rounded-lg transition-colors tooltip" title="Ver detalles">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button onclick="editProject(${proyecto.id})" class="p-2 text-emerald-500 hover:bg-emerald-50 rounded-lg transition-colors tooltip" title="Editar">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button onclick="deleteProject(${proyecto.id})" class="p-2 text-rose-500 hover:bg-rose-50 rounded-lg transition-colors tooltip" title="Eliminar">
                                    <i class="fas fa-trash-alt"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        function updateKPIs(proyectosData) {
            document.getElementById('totalProjects').textContent = proyectosData.length;

            const executionCount = proyectosData.filter(p => p.estado_nombre === 'Ejecución').length;
            document.getElementById('executionProjects').textContent = executionCount;
            const totalAmount = proyectosData.reduce((sum, p) => sum + (parseFloat(p.monto) || 0), 0);
            document.getElementById('totalAmount').textContent = utils.formatCurrency(totalAmount);
            const avgProgress = proyectosData.length > 0
                ? proyectosData.reduce((sum, p) => sum + (parseFloat(p.avance_total_porcentaje) || 0), 0) / proyectosData.length
                : 0;
            document.getElementById('averageProgress').textContent = (avgProgress > 1 ? avgProgress : avgProgress * 100).toFixed(1) + '%';
        }

        function toggleColumns() {
            const toggleElements = document.querySelectorAll('.toggle-column');
            const toggleBtn = document.getElementById('toggleColumnsBtn');
            columnsVisible = !columnsVisible;

            toggleElements.forEach(el => {
                el.classList.toggle('toggle-column-visible', columnsVisible);
            });

            if (columnsVisible) {
                toggleBtn.innerHTML = '<i class="fas fa-eye-slash mr-2"></i>Mostrar menos';
            } else {
                toggleBtn.innerHTML = '<i class="fas fa-eye mr-2"></i>Mostrar más';
            }
        }

        function updateCount(count) {
            const countElement = document.getElementById('proyectoCount');
            if (countElement) {
                countElement.textContent = `${count} proyecto${count !== 1 ? 's' : ''} encontrados`;
            }
        }

        async function viewProject(id) {
            const proyecto = proyectos.find(p => p.id === id);
            if (!proyecto) {
                showToast('Proyecto no encontrado', 'error');
                return;
            }

            // Registrar actividad ver_proyecto (fire-and-forget)
            api.post('/control/registrar', {
                accion: 'ver_proyecto',
                modulo: 'proyectos',
                entidad_tipo: 'proyecto',
                entidad_id: id,
                entidad_nombre: proyecto.nombre || `Proyecto #${id}`,
                exitoso: true
            }).catch(() => { }); // silencioso — no interrumpe la UI

            let projectDocs = [];
            try {
                // Fetch documents for the project
                const docResponse = await api.get(`/proyectos/${id}/documentos`);
                projectDocs = docResponse.documentos || [];
            } catch (e) {
                console.error("Error fetching documents", e);
            }


            const formatTech = (v) => {
                if (!v || v.toLowerCase() === 'no aplica' || v.toLowerCase() === 'n/a') return v || '-';
                let n = parseFloat(v);
                if (!isNaN(n)) return (n * 100).toFixed(0) + '%';
                return v;
            };

            const detailsContainer = document.getElementById('viewProjectDetails');
            detailsContainer.innerHTML = '';

            let html = `
                <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden" id="printableProjectSheet">
                    
                    <div class="bg-gradient-to-r from-indigo-50 to-purple-50 p-6 border-b border-gray-200">
                        <div class="flex items-start justify-between">
                            <div class="flex-1">
                                <h3 class="text-2xl font-bold text-gray-900 mb-2">${proyecto.nombre || 'Sin nombre'}</h3>
                                <div class="flex flex-wrap gap-3">
                                    <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-700">
                                        <i class="fas fa-hashtag mr-1.5"></i> ${proyecto.codigo || 'N/A'}
                                    </span>
                                    <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                                        <i class="fas fa-folder mr-1.5"></i> ${proyecto.area_nombre || 'Sin área'}
                                    </span>
                                </div>
                            </div>
                            <div class="text-right flex flex-col items-end gap-3">
                                <div>
                                    <div class="text-sm text-gray-500 mb-1">Monto Total</div>
                                    <div class="text-2xl font-bold text-indigo-600">${utils.formatCurrency(proyecto.monto)}</div>
                                </div>
                                <button onclick="downloadProjectPDF(${proyecto.id})" class="px-4 py-2 bg-white text-rose-600 rounded-lg border border-rose-200 hover:bg-rose-50 transition-all text-xs font-bold flex items-center gap-2 shadow-sm no-print">
                                    <i class="fas fa-file-pdf"></i>
                                    DESCARGAR FICHA PDF
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="p-6">
                        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            
                            <div class="space-y-6">
                                
                                <div>
                                    <h4 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                                        <i class="fas fa-info-circle text-indigo-500"></i>
                                        Información General
                                    </h4>
                                    <div class="bg-gray-50 rounded-xl p-4 space-y-3">
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Estado de Proyecto:</span>
                                            <span class="text-sm font-semibold text-gray-900">${proyecto.estado_nombre || '-'}</span>
                                        </div>
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Etapa del Proyecto:</span>
                                            <span class="text-sm font-semibold text-gray-900">${proyecto.etapa_nombre || '-'}</span>
                                        </div>
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Estado de Postulación:</span>
                                            <span class="text-sm font-semibold text-gray-900">${proyecto.estado_postulacion_nombre || '-'}</span>
                                        </div>
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Avance Total:</span>
                                            <span class="text-sm font-semibold text-indigo-600">${proyecto.avance_total_porcentaje ? `${(parseFloat(proyecto.avance_total_porcentaje) > 1 ? parseFloat(proyecto.avance_total_porcentaje) : parseFloat(proyecto.avance_total_porcentaje) * 100).toFixed(1)}%` : '-'}</span>
                                        </div>
                                        <div class="flex justify-between py-2">
                                            <span class="text-sm font-medium text-gray-600">¿Es Prioridad?:</span>
                                            <span class="text-sm font-semibold ${proyecto.es_prioridad === 'SI' ? 'text-red-600' : 'text-gray-900'}">
                                                ${proyecto.es_prioridad === 'SI' ? '✓ Sí' : 'No'}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <!-- Documentación y Técnica ahora debajo de Información General -->
                                <div>
                                    <h4 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                                        <i class="fas fa-file-alt text-purple-500"></i>
                                        Documentación y Técnica
                                    </h4>
                                    <!-- Files List -->
                                    <div class="bg-gray-50 rounded-xl p-4 space-y-4">
                                        
                                        <!-- Documentos del Sistema -->
                                         <div class="no-print">
                                            <div class="flex justify-between items-center mb-2">
                                                <span class="text-sm font-medium text-gray-700">Archivos Adjuntos:</span>
                                                <label for="uploadDocInput-${proyecto.id}" class="cursor-pointer inline-flex items-center px-2 py-1 bg-indigo-50 text-indigo-600 rounded-md text-xs font-medium hover:bg-indigo-100 transition-colors">
                                                    <i class="fas fa-plus mr-1"></i> Agregar
                                                </label>
                                                <input type="file" id="uploadDocInput-${proyecto.id}" class="hidden" onchange="handleQuickUpload(event, ${proyecto.id})">
                                            </div>

                                             ${projectDocs.length > 0 ? `
                                                <div class="space-y-2 mt-2">
                                                    ${projectDocs.map(doc => `
                                                        <div class="flex items-center justify-between bg-white p-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
                                                            <div class="flex items-center gap-3 overflow-hidden">
                                                                <div class="flex-shrink-0 w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600">
                                                                     <i class="fas fa-${getFileIcon(doc.archivo_extension || doc.nombre?.split('.').pop())}"></i>
                                                                </div>
                                                                <div class="min-w-0">
                                                                    <a href="#" onclick="event.preventDefault(); window.open('${API_CONFIG.BASE_URL}/documentos/${doc.documento_id}/view?token=${API_CONFIG.token}', '_blank');" class="text-sm font-medium text-gray-900 hover:text-indigo-600 truncate block transition-colors" title="${doc.nombre}">
                                                                        ${doc.nombre || doc.archivo_nombre}
                                                                    </a>
                                                                    <div class="text-xs text-gray-500 truncate">${formatDisplayDate(doc.fecha_subida)}</div>
                                                                </div>
                                                            </div>
                                                            <div class="flex gap-2">
                                                                ${(doc.archivo_extension === 'pdf' || (doc.nombre && doc.nombre.toLowerCase().endsWith('.pdf'))) ? `
                                                                <button onclick="event.preventDefault(); openDocViewer(${doc.documento_id}, '${doc.nombre || doc.archivo_nombre}')" class="text-gray-400 hover:text-indigo-600 p-1 rounded-full hover:bg-indigo-50 transition-colors" title="Ver documento">
                                                                    <i class="fas fa-eye"></i>
                                                                </button>
                                                                ` : ''}
                                                                <a href="#" onclick="event.preventDefault(); window.open('${API_CONFIG.BASE_URL}/documentos/${doc.documento_id}/view?token=${API_CONFIG.token}', '_blank');" class="text-gray-400 hover:text-indigo-600 p-1 rounded-full hover:bg-indigo-50 transition-colors" title="Descargar">
                                                                    <i class="fas fa-download"></i>
                                                                </a>
                                                            </div>
                                                        </div>
                                                    `).join('')}
                                                </div>
                                            ` : `
                                                <div class="text-center py-6 border-2 border-dashed border-gray-200 rounded-lg mt-2">
                                                    <div class="text-gray-400 mb-2"><i class="fas fa-file-upload text-xl"></i></div>
                                                    <div class="text-xs text-gray-500 font-medium">No hay documentos adjuntos</div>
                                                    <div class="text-[10px] text-gray-400">Sube archivos usando el botón "Agregar"</div>
                                                </div>
                                            `}
                                         </div>

                                        <div class="border-t border-gray-200 my-2 no-print"></div>

                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Documentos (Estado):</span>
                                            <span class="text-sm font-semibold text-gray-900">${formatTech(proyecto.documentos)}</span>
                                        </div>
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Planimetrías (Estado):</span>
                                            <span class="text-sm font-semibold text-gray-900">${formatTech(proyecto.planimetrias)}</span>
                                        </div>
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Topografía (Estado):</span>
                                            <span class="text-sm font-semibold text-gray-900">${formatTech(proyecto.topografia)}</span>
                                        </div>
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Ingeniería:</span>
                                            <span class="text-sm font-semibold text-gray-900">${formatTech(proyecto.ingenieria)}</span>
                                        </div>
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Perfil Técnico Económico:</span>
                                            <span class="text-sm font-semibold text-gray-900">${formatTech(proyecto.perfil_tecnico_economico)}</span>
                                        </div>
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Aprobación DOM:</span>
                                            <span class="text-sm font-semibold text-gray-900">${formatTech(proyecto.aprobacion_dom)}</span>
                                        </div>
                                        <div class="flex justify-between py-2">
                                            <span class="text-sm font-medium text-gray-600">Aprobación SERVIU:</span>
                                            <span class="text-sm font-semibold text-gray-900">${formatTech(proyecto.aprobacion_serviu)}</span>
                                        </div>
                                    </div>
                                </div>

                                <div>
                                    <h4 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                                        <i class="fas fa-dollar-sign text-green-500"></i>
                                        Financiamiento
                                    </h4>
                                    <div class="bg-gray-50 rounded-xl p-4 space-y-3">
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Tipo:</span>
                                            <span class="text-sm font-semibold text-gray-900">${proyecto.financiamiento_nombre || '-'}</span>
                                        </div>
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Financiamiento Municipal:</span>
                                            <span class="text-sm font-semibold text-gray-900">${proyecto.financiamiento_municipal || '-'}</span>
                                        </div>
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Año de Elaboración:</span>
                                            <span class="text-sm font-semibold text-gray-900">${proyecto.anno_elaboracion || '-'}</span>
                                        </div>
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Año de Ejecución:</span>
                                            <span class="text-sm font-semibold text-gray-900">${proyecto.anno_ejecucion || '-'}</span>
                                        </div>
                                        <div class="flex justify-between py-2">
                                            <span class="text-sm font-medium text-gray-600">Fecha de Postulación:</span>
                                            <span class="text-sm font-semibold text-gray-900">${proyecto.fecha_postulacion ? formatDisplayDate(proyecto.fecha_postulacion) : '-'}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="space-y-6">
                                
                                <div>
                                    <h4 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                                        <i class="fas fa-map-marker-alt text-red-500"></i>
                                        Ubicación y Territorio
                                    </h4>
                                    <div class="bg-gray-50 rounded-xl p-4 space-y-3">
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Lineamiento Estratégico:</span>
                                            <span class="text-sm font-semibold text-gray-900">${proyecto.lineamiento_nombre || '-'}</span>
                                        </div>
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Sector:</span>
                                            <span class="text-sm font-semibold text-gray-900">${proyecto.sector_nombre || '-'}</span>
                                        </div>
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Unidad Vecinal:</span>
                                            <span class="text-sm font-semibold text-gray-900">${proyecto.unidad_vecinal || '-'}</span>
                                        </div>
                                        <div class="flex justify-between py-2">
                                            <span class="text-sm font-medium text-gray-600">Coordenadas:</span>
                                            <span class="text-sm font-mono text-gray-900">${proyecto.latitud && proyecto.longitud ? `${proyecto.latitud}, ${proyecto.longitud}` : '-'}</span>
                                        </div>
                                    </div>
                                </div>

                                <!-- Observaciones Generales arriba de Profesionales a Cargo -->
                                ${proyecto.observaciones ? `
                                <div>
                                    <h4 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                                        <i class="fas fa-comment-alt text-amber-500"></i>
                                        Observaciones Generales
                                    </h4>
                                    <div class="bg-amber-50 rounded-xl p-4 border border-amber-200">
                                        <p class="text-sm text-gray-700 leading-relaxed">${proyecto.observaciones}</p>
                                    </div>
                                </div>
                                ` : ''}

                                <div>
                                    <h4 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                                        <i class="fas fa-users text-blue-500"></i>
                                        Profesionales a Cargo
                                    </h4>
                                    <div class="bg-gray-50 rounded-xl p-4 space-y-3">
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Profesional 1:</span>
                                            <span class="text-sm font-semibold text-gray-900">${proyecto.profesional_1 || '-'}</span>
                                        </div>
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Profesional 2:</span>
                                            <span class="text-sm font-semibold text-gray-900">${proyecto.profesional_2 || '-'}</span>
                                        </div>
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Profesional 3:</span>
                                            <span class="text-sm font-semibold text-gray-900">${proyecto.profesional_3 || '-'}</span>
                                        </div>
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Profesional 4:</span>
                                            <span class="text-sm font-semibold text-gray-900">${proyecto.profesional_4 || '-'}</span>
                                        </div>
                                        <div class="flex justify-between py-2 border-b border-gray-200">
                                            <span class="text-sm font-medium text-gray-600">Profesional 5:</span>
                                            <span class="text-sm font-semibold text-gray-900">${proyecto.profesional_5 || '-'}</span>
                                        </div>
                                        <div class="flex justify-between py-2">
                                            <span class="text-sm font-medium text-gray-600">Dupla Profesionales:</span>
                                            <span class="text-sm font-semibold text-gray-900">${proyecto.dupla_profesionales || '-'}</span>
                                        </div>
                                    </div>
                                </div>

                            </div>
                        </div>
                    </div>
                </div>
            `;

            const hitos = proyecto.hitos_lista || [];
            html += `
                <div class="mt-8">
                    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                        <div class="bg-gradient-to-r from-blue-500 to-cyan-500 p-5">
                            <h3 class="text-xl font-bold text-white flex items-center gap-3">
                                <div class="bg-white bg-opacity-20 p-2 rounded-lg">
                                    <i class="fas fa-flag-checkered"></i>
                                </div>
                                Hitos del Proyecto
                                <span class="ml-auto bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm font-medium">${hitos.length} hito${hitos.length !== 1 ? 's' : ''}</span>
                            </h3>
                        </div>
                        <div class="p-6">
                            ${hitos.length > 0 ? `
                                <div class="space-y-4">
                                    ${hitos.map((h, index) => `
                                        <div class="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-xl p-5 border border-blue-100 hover:shadow-md transition-all">
                                            <div class="flex items-start gap-4">
                                                <div class="flex-shrink-0">
                                                    <div class="w-12 h-12 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold text-lg">
                                                        ${index + 1}
                                                    </div>
                                                </div>
                                                <div class="flex-1 space-y-2">
                                                    <div class="flex items-center gap-3 flex-wrap">
                                                        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-600 text-white">
                                                            <i class="fas fa-bookmark mr-1.5"></i>
                                                            ${h.tipo_hito || 'Sin tipo'}
                                                        </span>
                                                        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-white text-gray-700 border border-gray-300">
                                                            <i class="fas fa-calendar mr-1.5"></i>
                                                            ${formatDisplayDate(h.fecha)}
                                                        </span>
                                                    </div>
                                                    ${h.observacion ? `
                                                        <div class="bg-white rounded-lg p-3 mt-2">
                                                            <p class="text-sm text-gray-700 leading-relaxed">${h.observacion}</p>
                                                        </div>
                                                    ` : '<p class="text-sm text-gray-500 italic">Sin observación</p>'}
                                                    ${(h.nombre_creador || h.creado_por) ? `
                                                        <div class="text-xs text-gray-500 mt-2 flex items-center gap-1">
                                                            <i class="fas fa-user"></i>
                                                            Creado por: <span class="font-medium">${h.nombre_creador || 'Usuario #' + h.creado_por}</span>
                                                        </div>
                                                    ` : ''}
                                                </div>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            ` : `
                                <div class="text-center py-12">
                                    <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 text-gray-400 mb-4">
                                        <i class="fas fa-flag-checkered text-2xl"></i>
                                    </div>
                                    <p class="text-gray-500 font-medium">No hay hitos registrados</p>
                                    <p class="text-gray-400 text-sm mt-1">Los hitos del proyecto aparecerán aquí</p>
                                </div>
                            `}
                        </div>
                    </div>
                </div>
            `;

            const observaciones = proyecto.observaciones_lista || [];
            html += `
                <div class="mt-6">
                    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                        <div class="bg-gradient-to-r from-orange-500 to-amber-500 p-5">
                            <h3 class="text-xl font-bold text-white flex items-center gap-3">
                                <div class="bg-white bg-opacity-20 p-2 rounded-lg">
                                    <i class="fas fa-comments"></i>
                                </div>
                                Observaciones del Proyecto
                                <span class="ml-auto bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm font-medium">${observaciones.length} observación${observaciones.length !== 1 ? 'es' : ''}</span>
                            </h3>
                        </div>
                        <div class="p-6">
                            ${observaciones.length > 0 ? `
                                <div class="space-y-4">
                                    ${observaciones.map((o, index) => `
                                        <div class="bg-gradient-to-r from-orange-50 to-amber-50 rounded-xl p-5 border border-orange-100 hover:shadow-md transition-all">
                                            <div class="flex items-start gap-4">
                                                <div class="flex-shrink-0">
                                                    <div class="w-12 h-12 rounded-full bg-orange-500 text-white flex items-center justify-center font-bold text-lg">
                                                        ${index + 1}
                                                    </div>
                                                </div>
                                                <div class="flex-1">
                                                    <div class="flex items-center gap-3 mb-3">
                                                        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-white text-gray-700 border border-gray-300">
                                                            <i class="fas fa-calendar mr-1.5"></i>
                                                            ${formatDisplayDate(o.fecha)}
                                                        </span>
                                                        ${(o.nombre_creador || o.creado_por) ? `
                                                            <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-orange-600 text-white">
                                                                <i class="fas fa-user mr-1.5"></i>
                                                                ${o.nombre_creador || 'Usuario #' + o.creado_por}
                                                            </span>
                                                        ` : ''}
                                                    </div>
                                                    <div class="bg-white rounded-lg p-4">
                                                        <p class="text-sm text-gray-800 leading-relaxed">${o.observacion || 'Sin observación'}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            ` : `
                                <div class="text-center py-12">
                                    <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 text-gray-400 mb-4">
                                        <i class="fas fa-comments text-2xl"></i>
                                    </div>
                                    <p class="text-gray-500 font-medium">No hay observaciones registradas</p>
                                    <p class="text-gray-400 text-sm mt-1">Las observaciones del proyecto aparecerán aquí</p>
                                </div>
                            `}
                        </div>
                    </div>
                </div>
            `;

            html += `
                <div class="mt-8">
                    <div class="bg-gradient-to-r from-gray-700 to-gray-900 rounded-2xl shadow-lg p-6 text-white">
                        <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
                            <i class="fas fa-shield-alt"></i>
                            Auditoría del Sistema
                        </h3>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div class="bg-white bg-opacity-10 rounded-xl p-4 backdrop-blur">
                                <div class="flex items-center gap-3 mb-2">
                                    <div class="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center">
                                        <i class="fas fa-user-plus"></i>
                                    </div>
                                    <div>
                                        <div class="text-xs opacity-75">Creado por</div>
                                        <div class="font-semibold">${proyecto.user_nombre || 'Desconocido'}</div>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white bg-opacity-10 rounded-xl p-4 backdrop-blur">
                                <div class="flex items-center gap-3 mb-2">
                                    <div class="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center">
                                        <i class="fas fa-user-edit"></i>
                                    </div>
                                    <div>
                                        <div class="text-xs opacity-75">Actualizado por</div>
                                        <div class="font-semibold">${proyecto.actualizado_por_nombre || 'Desconocido'}</div>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white bg-opacity-10 rounded-xl p-4 backdrop-blur">
                                <div class="flex items-center gap-3 mb-2">
                                    <div class="w-10 h-10 rounded-full bg-purple-500 flex items-center justify-center">
                                        <i class="fas fa-clock"></i>
                                    </div>
                                    <div>
                                        <div class="text-xs opacity-75">Última actualización</div>
                                        <div class="font-semibold text-sm">${formatDisplayDate(proyecto.fecha_actualizacion)}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            detailsContainer.innerHTML = html;
            document.getElementById('viewProjectModal').classList.add('active');
        }

        function editProject(id) {
            const proyecto = proyectos.find(p => p.id === id);
            if (proyecto) openModal(proyecto);
        }

        async function deleteProject(id) {
            if (!confirm('¿Está seguro de que desea eliminar este proyecto? Esta acción no se puede deshacer.')) return;

            try {

                if (typeof showLoading === 'function') showLoading(true, 'Eliminando...');

                await api.delete(`/proyectos/${id}`);

                showToast('Proyecto eliminado exitosamente', 'success');
                loadProjects();
            } catch (error) {
                console.error('Error:', error);
                showToast(error.message || 'Error al eliminar el proyecto', 'error');
            } finally {
                if (typeof showLoading === 'function') showLoading(false);
            }
        }

        function exportData() {
            showToast('Función de exportación en desarrollo', 'warning');
        }

        function showAddProjectModal() {
            openModal();
        }

        function openModal(proyecto = null) {

            if (catalogData.areas.length === 0) {
                populateFormSelects();
            }

            const modal = document.getElementById('proyectoModal');
            const form = document.getElementById('proyectoForm');
            const titleText = document.getElementById('modalTitleText');
            const modalIcon = document.getElementById('modalIcon');
            const modalSubtitle = document.getElementById('modalSubtitle');
            const submitText = document.getElementById('submitText');

            if (proyecto) {

                titleText.textContent = 'Editar Proyecto';
                modalIcon.className = 'fas fa-edit';
                modalSubtitle.textContent = 'Modifique los campos necesarios para actualizar el proyecto';
                submitText.textContent = 'Actualizar';
                editingId = proyecto.id;

                form.reset();

                // Mapear campos del objeto proyecto a los nombres del formulario
                // El backend devuelve area_id, estado_proyecto_id, etc. que coinciden con los names del form
                const fieldMapping = {
                    // Los campos _nombre son de solo lectura, ignorar
                    'area_nombre': null,
                    'estado_nombre': null,
                    'etapa_nombre': null,
                    'estado_postulacion_nombre': null,
                    'financiamiento_nombre': null,
                    'lineamiento_nombre': null,
                    'sector_nombre': null,
                    'estado_color': null
                };

                Object.keys(proyecto).forEach(key => {
                    // Saltar campos marcados como null en el mapping (campos de solo lectura)
                    if (key in fieldMapping && fieldMapping[key] === null) return;
                    const fieldName = fieldMapping[key] || key;
                    const input = form.elements[fieldName];
                    if (input) {
                        if (input.type === 'checkbox') {
                            input.checked = (proyecto[key] === 'SI' || proyecto[key] === true);
                        } else if (input.type === 'date') {
                            input.value = formatDateForInput(proyecto[key]);
                        } else {
                            input.value = proyecto[key] || '';
                        }
                    }
                });
            } else {

                titleText.textContent = 'Nuevo Proyecto';
                modalIcon.className = 'fas fa-folder-plus';
                modalSubtitle.textContent = 'Complete los campos para registrar un nuevo proyecto';
                submitText.textContent = 'Guardar';
                editingId = null;
                form.reset();
            }
            modal.classList.add('active');
        }

        function closeModal() {
            document.getElementById('proyectoModal').classList.remove('active');
            document.getElementById('proyectoForm').reset();
            editingId = null;
        }

        function closeViewModal() {
            document.getElementById('viewProjectModal').classList.remove('active');
        }

        async function handleSubmit(e) {
            e.preventDefault();
            const form = e.target;
            const data = utils.serializeForm(form);

            // Checkbox: financiamiento_municipal es VARCHAR(50) en DB
            data.financiamiento_municipal = document.getElementById('financiamiento_municipal').checked ? 'SI' : 'NO';

            // FK IDs: parsear como enteros, eliminar si vacíos
            const fkFields = ['area_id', 'estado_proyecto_id', 'etapa_proyecto_id', 'estado_postulacion_id', 'financiamiento_id', 'lineamiento_estrategico_id', 'sector_id'];
            fkFields.forEach(f => {
                if (data[f]) data[f] = parseInt(data[f], 10);
                else delete data[f];
            });

            // Campos numéricos: parsear o eliminar si vacíos
            if (data.monto) data.monto = parseFloat(data.monto); else delete data.monto;
            if (data.avance_total_porcentaje) data.avance_total_porcentaje = parseFloat(data.avance_total_porcentaje); else delete data.avance_total_porcentaje;
            if (data.n_registro) data.n_registro = parseInt(data.n_registro, 10); else delete data.n_registro;
            if (data.anno_elaboracion) data.anno_elaboracion = parseInt(data.anno_elaboracion, 10); else delete data.anno_elaboracion;
            if (data.anno_ejecucion) data.anno_ejecucion = parseInt(data.anno_ejecucion, 10); else delete data.anno_ejecucion;
            if (data.latitud) data.latitud = parseFloat(data.latitud); else delete data.latitud;
            if (data.longitud) data.longitud = parseFloat(data.longitud); else delete data.longitud;

            // Eliminar campos que NO existen en la tabla proyectos
            delete data.codigo;
            delete data.es_prioridad;

            // Eliminar strings vacíos para campos opcionales
            Object.keys(data).forEach(k => {
                if (data[k] === '') delete data[k];
            });

            console.log('Sending payload (schema-aligned):', data);

            const submitBtn = document.getElementById('submitBtn');
            const submitText = document.getElementById('submitText');
            const originalText = submitText.innerHTML;

            try {
                submitBtn.disabled = true;
                submitText.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Procesando...';

                if (editingId) {
                    await api.put(`/proyectos/${editingId}`, data);
                } else {
                    await api.post('/proyectos', data);
                }

                showToast(editingId ? 'Proyecto actualizado' : 'Proyecto creado exitosamente');
                closeModal();
                loadProjects();
            } catch (error) {
                console.error('Submit Error:', error);
                showToast(error.message || 'Error al guardar el proyecto', 'error');
            } finally {
                submitBtn.disabled = false;
                submitText.innerHTML = originalText;
            }
        }

        window.onclick = function (event) {
            const editModal = document.getElementById('proyectoModal');
            const viewModal = document.getElementById('viewProjectModal');
            if (event.target === editModal) closeModal();
            if (event.target === viewModal) closeViewModal();
        }

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') { closeModal(); closeViewModal(); }
        });

        function getFileIcon(ext) {
            if (!ext) return 'file';
            const e = ext.toLowerCase().replace('.', '');
            if (['pdf'].includes(e)) return 'pdf';
            if (['doc', 'docx'].includes(e)) return 'word';
            if (['xls', 'xlsx'].includes(e)) return 'excel';
            if (['jpg', 'jpeg', 'png', 'gif'].includes(e)) return 'image';
            if (['zip', 'rar'].includes(e)) return 'archive';
            return 'file';
        }

        async function handleQuickUpload(event, projectId) {
            const file = event.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);
            formData.append('tipo_documento', 'Documento General');
            formData.append('descripcion', 'Subido desde visor de proyecto');

            const label = event.target.previousElementSibling;
            const originalText = label.innerHTML;
            label.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            label.classList.add('cursor-not-allowed', 'opacity-50');

            try {
                // Use api wrapper for automatic auth and error handling
                await api.post(`/proyectos/${projectId}/documentos/upload`, formData);

                showToast('Documento subido correctamente');
                // Refresh view
                viewProject(projectId);
            } catch (error) {
                console.error(error);
                showToast(error.message || 'Error al subir archivo', 'error');
            } finally {
                label.innerHTML = originalText;
                label.classList.remove('cursor-not-allowed', 'opacity-50');
                event.target.value = '';
            }
        }

        // PDF Viewer Modal Functions
        // PDF Viewer Modal Functions
        function openDocViewer(docId, docName) {
            let modal = document.getElementById('docViewerModal');

            if (modal) modal.remove();

            const modalHtml = `
            <div id="docViewerModal" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in" role="dialog" aria-modal="true" onclick="if(event.target === this) closeDocViewer()">
                <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-6xl h-[90vh] flex flex-col overflow-hidden" onclick="event.stopPropagation()">
                    
                    <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-white shadow-sm z-20">
                        <h3 class="text-lg font-bold text-gray-800 flex items-center gap-3">
                            <div class="w-8 h-8 rounded-lg bg-red-50 text-red-500 flex items-center justify-center">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <span class="truncate">${docName}</span>
                        </h3>
                        <button type="button" class="w-8 h-8 rounded-full bg-gray-50 text-gray-400 hover:bg-gray-100 hover:text-gray-600 flex items-center justify-center transition-colors focus:outline-none" onclick="closeDocViewer()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>

                    <div class="flex-1 bg-gray-100 relative w-full h-full">
                        <div id="docLoading" class="absolute inset-0 flex flex-col items-center justify-center bg-white z-10 transition-opacity duration-300">
                             <i class="fas fa-spinner fa-spin text-4xl text-indigo-600 mb-4"></i>
                            <p class="text-gray-500 font-medium">Cargando documento...</p>
                        </div>
                        <iframe id="docFrame" class="w-full h-full border-0" src=""></iframe>
                    </div>
                </div>
            </div>`;

            document.body.insertAdjacentHTML('beforeend', modalHtml);

            const frame = document.getElementById('docFrame');
            const loading = document.getElementById('docLoading');
            const url = `${API_CONFIG.BASE_URL}/documentos/${docId}/view?token=${API_CONFIG.token}`;

            frame.src = url;

            frame.onload = () => {
                loading.classList.add('opacity-0', 'pointer-events-none');
                setTimeout(() => loading.classList.add('hidden'), 300);
            };
        }

        function closeDocViewer() {
            const modal = document.getElementById('docViewerModal');
            if (modal) {
                modal.classList.add('opacity-0', 'pointer-events-none');
                setTimeout(() => modal.remove(), 200);
            }
        }

        function downloadProjectPDF(projectId) {
            const proyecto = proyectos.find(p => p.id === projectId);
            if (!proyecto) return;

            const printWindow = window.open('', '_blank');
            const sheet = document.getElementById('printableProjectSheet').cloneNode(true);
            sheet.querySelectorAll('.no-print').forEach(el => el.remove());

            const content = sheet.outerHTML;
            const html = [
                '<!DOCTYPE html>',
                '<html>',
                '<head>',
                '<meta charset="UTF-8">',
                '<title>Ficha de Proyecto - ' + (proyecto.nombre || '') + '</title>',
                '<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">',
                '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">',
                '<style>',
                'body { font-family: "Outfit", sans-serif; padding: 0; background: white; }',
                '.bg-gray-50 { background-color: #f9fafb !important; }',
                '.bg-indigo-50 { background-color: #eef2ff !important; }',
                '.bg-purple-50 { background-color: #faf5ff !important; }',
                '.bg-amber-50 { background-color: #fffbeb !important; }',
                '@page { margin: 1.5cm; size: letter; }',
                '* { print-color-adjust: exact; -webkit-print-color-adjust: exact; }',
                '</style>',
                '</head>',
                '<body onload="setTimeout(function(){ window.print(); setTimeout(function(){ window.close(); }, 500); }, 1000);">',
                '<div class="max-w-4xl mx-auto">',
                content,
                '</div>',
                '</body>',
                '</html>'
            ].join('\\n');

            printWindow.document.write(html);
            printWindow.document.close();
        }
    