/**
 * Dashboard Enhancements v1.0
 * Mejoras UX compartidas para registro1, sexo1, edad1, profesion1
 * Excluye: Dark Mode (#14)
 */
(function () {
    'use strict';

    // ─── Utilidades ────────────────────────────────────────────
    function injectCSS(css) {
        const style = document.createElement('style');
        style.textContent = css;
        document.head.appendChild(style);
    }

    // ─── #1 Cursor pointer en celdas clickeables ──────────────
    // ─── #2 Indicador "clic para ver detalle" ─────────────────
    // ─── #3 Toast en exportaciones ────────────────────────────
    // ─── #5 Cerrar modal con Escape ───────────────────────────
    // ─── #8 Highlight columna al hover ────────────────────────
    // ─── #9 Skeleton loading ──────────────────────────────────
    // ─── #12 Sombra sticky column ─────────────────────────────
    // ─── #13 Animación metric cards ───────────────────────────
    // ─── #15 Scroll-to-top al cambiar filtros ─────────────────
    // ─── Aviso sin datos ──────────────────────────────────────

    const enhancementCSS = `
    /* #1 — Cursor pointer en celdas de datos */
    tbody td:not(:first-child) {
      cursor: pointer;
    }
    tbody td:not(:first-child):hover {
      filter: brightness(0.95);
    }

    /* #2 — Indicador visual de interactividad */
    .table-hint {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.6rem 1rem;
      margin-top: 0.75rem;
      font-size: 0.8125rem;
      color: #64748b;
      background: #f1f5f9;
      border-radius: 8px;
      border-left: 3px solid #3b82f6;
    }
    .table-hint i, .table-hint svg {
      color: #3b82f6;
      flex-shrink: 0;
    }

    /* #3 — Toast notification */
    .toast-notification {
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      color: white;
      padding: 0.875rem 1.5rem;
      border-radius: 12px;
      font-size: 0.875rem;
      font-weight: 600;
      box-shadow: 0 10px 30px rgba(5, 150, 105, 0.35);
      z-index: 9999;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transform: translateY(120%);
      opacity: 0;
      transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    .toast-notification.show {
      transform: translateY(0);
      opacity: 1;
    }
    .toast-notification.error {
      background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
      box-shadow: 0 10px 30px rgba(220, 38, 38, 0.35);
    }

    /* #4 — Conteo de resultados en modal */
    .results-count {
      font-size: 0.8125rem;
      color: #64748b;
      font-weight: 500;
      padding: 0.25rem 0;
    }
    .results-count strong {
      color: #0f172a;
    }

    /* #6 — Filtros activos (chips) */
    .active-filters-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      padding: 0;
      margin-top: 0.75rem;
      min-height: 0;
      transition: all 0.3s ease;
    }
    .active-filters-bar:empty {
      display: none;
    }
    .active-filter-chip {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.35rem 0.75rem;
      background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
      border: 1px solid #bfdbfe;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 600;
      color: #1e40af;
      cursor: pointer;
      transition: all 0.2s ease;
      user-select: none;
    }
    .active-filter-chip:hover {
      background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
      transform: scale(1.05);
    }
    .active-filter-chip .chip-remove {
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: #3b82f6;
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 10px;
      font-weight: bold;
      line-height: 1;
      transition: background 0.2s;
    }
    .active-filter-chip:hover .chip-remove {
      background: #1d4ed8;
    }

    /* #7 — Fila de totales (tfoot) */
    tfoot td {
      font-weight: 700 !important;
      border-top: 2px solid #cbd5e1 !important;
      background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
      color: #0f172a !important;
      font-size: 0.8rem !important;
      position: relative;
    }
    tfoot td:first-child {
      position: sticky;
      left: 0;
      z-index: 11;
      background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%) !important;
    }

    /* #8 — Highlight columna al hover */
    th[data-col-index] {
      cursor: pointer;
      user-select: none;
    }
    .col-highlight {
      background-color: rgba(59, 130, 246, 0.06) !important;
    }

    /* #9 — Skeleton loading */
    .skeleton-container {
      padding: 1.5rem;
    }
    .skeleton-row {
      display: flex;
      gap: 0.75rem;
      margin-bottom: 0.75rem;
    }
    .skeleton-cell {
      height: 36px;
      border-radius: 6px;
      background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%);
      background-size: 200% 100%;
      animation: skeletonPulse 1.5s ease-in-out infinite;
    }
    .skeleton-cell:first-child {
      flex: 0 0 200px;
    }
    .skeleton-cell:not(:first-child) {
      flex: 1;
    }
    .skeleton-header .skeleton-cell {
      height: 42px;
      background: linear-gradient(90deg, #cbd5e1 25%, #e2e8f0 50%, #cbd5e1 75%);
      background-size: 200% 100%;
      animation: skeletonPulse 1.5s ease-in-out infinite;
    }
    @keyframes skeletonPulse {
      0% { background-position: 200% 0; }
      100% { background-position: -200% 0; }
    }

    /* #10 — Breadcrumb */
    .breadcrumb-nav {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem 0;
      font-size: 0.8125rem;
      color: #94a3b8;
      margin-bottom: 0.5rem;
    }
    .breadcrumb-nav a {
      color: #64748b;
      text-decoration: none;
      transition: color 0.2s;
    }
    .breadcrumb-nav a:hover {
      color: #3b82f6;
    }
    .breadcrumb-nav .breadcrumb-sep {
      font-size: 0.7rem;
      color: #cbd5e1;
    }
    .breadcrumb-nav .breadcrumb-current {
      color: #0f172a;
      font-weight: 600;
    }

    /* #12 — Enhanced sticky column shadow */
    td:first-child,
    tbody td:first-child {
      box-shadow: 2px 0 6px rgba(0, 0, 0, 0.06);
    }

    /* #13 — Animación metric cards / stat items */
    @keyframes fadeSlideUp {
      from {
        opacity: 0;
        transform: translateY(16px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    .metric-card, .stat-item {
      animation: fadeSlideUp 0.5s ease-out both;
    }
    .metric-card:nth-child(1), .stat-item:nth-child(1) { animation-delay: 0s; }
    .metric-card:nth-child(2), .stat-item:nth-child(2) { animation-delay: 0.1s; }
    .metric-card:nth-child(3), .stat-item:nth-child(3) { animation-delay: 0.2s; }
    .metric-card:nth-child(4), .stat-item:nth-child(4) { animation-delay: 0.3s; }

    /* Aviso sin datos — Empty state mejorado */
    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 4rem 2rem;
      text-align: center;
      color: #94a3b8;
    }
    .empty-state-icon {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 1.5rem;
      font-size: 2rem;
    }
    .empty-state-title {
      font-size: 1.125rem;
      font-weight: 700;
      color: #475569;
      margin-bottom: 0.5rem;
    }
    .empty-state-desc {
      font-size: 0.875rem;
      color: #94a3b8;
      max-width: 320px;
      line-height: 1.5;
    }
  `;

    injectCSS(enhancementCSS);

    // ─── DOM Ready ─────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', () => {
        initBreadcrumb();
        initSkeletonLoading();
        initEscapeClose();
        initColumnHighlight();
        patchExportWithToast();
        injectTableHint();
        injectActiveFiltersBar();
        patchRenderForEnhancements();
        patchModalResultsCount();
    });

    // ─── #10 Breadcrumb ────────────────────────────────────────
    function initBreadcrumb() {
        const pageTitle = document.title || '';
        let breadcrumbLabel = 'Registros';

        if (pageTitle.includes('Edad')) breadcrumbLabel = 'Por Edad';
        else if (pageTitle.includes('Sexo') || pageTitle.includes('sexo')) breadcrumbLabel = 'Por Sexo';
        else if (pageTitle.includes('Homologado') || pageTitle.includes('Profesion') || pageTitle.includes('profesion')) breadcrumbLabel = 'Por Homologado';
        else if (pageTitle.includes('Base')) breadcrumbLabel = 'Por Base';

        // Obtener nombre del organismo del título dinámico
        const tituloEl = document.getElementById('titulo_principal');
        const orgName = tituloEl ? tituloEl.textContent.replace(/.*por\s*/i, '').split(' y ')[0].trim() : '';

        const breadcrumb = document.createElement('nav');
        breadcrumb.className = 'breadcrumb-nav';
        breadcrumb.innerHTML = typeof DOMPurify !== "undefined" ? DOMPurify.sanitize(`
      <a href="../landing_transparencia.html">Inicio</a>
      <span class="breadcrumb-sep">›</span>
      <a href="../landing_transparencia.html">Registros</a>
      <span class="breadcrumb-sep">›</span>
      ${orgName ? `<span>${orgName}</span><span class="breadcrumb-sep">›</span>` : ''}
      <span class="breadcrumb-current">${breadcrumbLabel}</span>
    `) : `
      <a href="../landing_transparencia.html">Inicio</a>
      <span class="breadcrumb-sep">›</span>
      <a href="../landing_transparencia.html">Registros</a>
      <span class="breadcrumb-sep">›</span>
      ${orgName ? `<span>${orgName}</span><span class="breadcrumb-sep">›</span>` : ''}
      <span class="breadcrumb-current">${breadcrumbLabel}</span>
    `;

        // Insertarlo después del header/nav
        const mainEl = document.querySelector('main.container') || document.querySelector('.main-content') || document.querySelector('.stats-bar');
        if (mainEl) {
            mainEl.parentNode.insertBefore(breadcrumb, mainEl);
        }
    }

    // ─── #9 Skeleton Loading ───────────────────────────────────
    function initSkeletonLoading() {
        const loadingEl = document.getElementById('loading');
        if (!loadingEl) return;

        const cols = 6;
        const rows = 5;
        let skeletonHTML = '<div class="skeleton-container">';
        skeletonHTML += '<div class="skeleton-row skeleton-header">';
        for (let c = 0; c < cols; c++) skeletonHTML += '<div class="skeleton-cell"></div>';
        skeletonHTML += '</div>';
        for (let r = 0; r < rows; r++) {
            skeletonHTML += `<div class="skeleton-row" style="animation-delay:${r * 0.1}s">`;
            for (let c = 0; c < cols; c++) skeletonHTML += '<div class="skeleton-cell"></div>';
            skeletonHTML += '</div>';
        }
        skeletonHTML += '</div>';

        loadingEl.innerHTML = typeof DOMPurify !== "undefined" ? DOMPurify.sanitize(skeletonHTML) : skeletonHTML;
    }

    // ─── #5 Cerrar modal con Escape ────────────────────────────
    function initEscapeClose() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const modal = document.getElementById('detailsModal');
                if (modal && modal.style.display === 'block') {
                    modal.style.display = 'none';
                }
            }
        });
    }

    // ─── #3 Toast de exportación ───────────────────────────────
    let toastEl = null;
    function showToast(message, isError = false) {
        if (!toastEl) {
            toastEl = document.createElement('div');
            toastEl.className = 'toast-notification';
            document.body.appendChild(toastEl);
        }
        toastEl.className = 'toast-notification' + (isError ? ' error' : '');
        toastEl.innerHTML = typeof DOMPurify !== "undefined" ? DOMPurify.sanitize(`${isError ? '⚠️' : '✓'} ${message}`) : `${isError ? '⚠️' : '✓'} ${message}`;

        requestAnimationFrame(() => {
            toastEl.classList.add('show');
        });

        setTimeout(() => {
            toastEl.classList.remove('show');
        }, 3000);
    }

    function patchExportWithToast() {
        const exportFns = { 'export-csv': 'CSV', 'export-excel': 'Excel', 'export-pdf': 'PDF' };

        Object.entries(exportFns).forEach(([id, label]) => {
            const btn = document.getElementById(id);
            if (btn) {
                // Agregar listener adicional que muestra toast
                btn.addEventListener('click', () => {
                    setTimeout(() => showToast(`Archivo ${label} exportado exitosamente`), 300);
                });
            }
        });
    }

    // ─── #2 Hint de interactividad ─────────────────────────────
    function injectTableHint() {
        // Solo inyectar si hay modal (registro1, sexo1)
        const modal = document.getElementById('detailsModal');

        const tableSection = document.querySelector('.table-section') || document.querySelector('.table-card');
        if (!tableSection) return;

        const hint = document.createElement('div');
        hint.className = 'table-hint';

        if (modal) {
            hint.innerHTML = typeof DOMPurify !== "undefined" ? DOMPurify.sanitize('<i class="fas fa-info-circle"></i> Haga clic en cualquier celda para ver el detalle de registros') : '<i class="fas fa-info-circle"></i> Haga clic en cualquier celda para ver el detalle de registros';
        } else {
            hint.innerHTML = typeof DOMPurify !== "undefined" ? DOMPurify.sanitize('<i class="fas fa-info-circle"></i> Pase el cursor sobre las celdas para ver el detalle estadístico') : '<i class="fas fa-info-circle"></i> Pase el cursor sobre las celdas para ver el detalle estadístico';
        }

        tableSection.appendChild(hint);
    }

    // ─── #6 Filtros activos (chips) ────────────────────────────
    function injectActiveFiltersBar() {
        const filtersContainer = document.querySelector('.filter-bar') || document.querySelector('.filters');
        if (!filtersContainer) return;

        const chipsBar = document.createElement('div');
        chipsBar.className = 'active-filters-bar';
        chipsBar.id = 'active-filters-chips';

        // Insertar después de la barra de filtros
        filtersContainer.parentNode.insertBefore(chipsBar, filtersContainer.nextSibling);

        // Observar cambios en los selects
        const selects = filtersContainer.querySelectorAll('select');
        selects.forEach(select => {
            select.addEventListener('change', () => updateActiveFiltersChips());
        });

        // Observar mutaciones para detectar cambios programáticos
        const observer = new MutationObserver(() => updateActiveFiltersChips());
        selects.forEach(select => {
            observer.observe(select, { attributes: true, attributeFilter: ['value'] });
        });
    }

    function updateActiveFiltersChips() {
        const chipsBar = document.getElementById('active-filters-chips');
        if (!chipsBar) return;

        chipsBar.innerHTML = typeof DOMPurify !== "undefined" ? DOMPurify.sanitize('') : '';

        const filterMap = {
            'sexo-filter': { label: 'Sexo', icon: '♀♂' },
            'homologado-filter': { label: 'Homologado', icon: '🎓' },
            'edad-filter': { label: 'Edad', icon: '👤' },
            'base-filter': { label: 'Base', icon: '📋' },
            'year-filter': { label: 'Año', icon: '📅' }
        };

        Object.entries(filterMap).forEach(([id, meta]) => {
            const select = document.getElementById(id);
            if (!select || !select.value) return;

            // Skip year filter si es el valor por defecto (maxYear)
            if (id === 'year-filter' && typeof maxYear !== 'undefined' && select.value == maxYear) return;

            const chip = document.createElement('span');
            chip.className = 'active-filter-chip';
            chip.innerHTML = typeof DOMPurify !== "undefined" ? DOMPurify.sanitize(`${meta.icon} ${meta.label}: ${select.selectedOptions[0]?.textContent || select.value} <span class="chip-remove">✕</span>`) : `${meta.icon} ${meta.label}: ${select.selectedOptions[0]?.textContent || select.value} <span class="chip-remove">✕</span>`;
            chip.addEventListener('click', () => {
                if (id === 'year-filter' && typeof maxYear !== 'undefined') {
                    select.value = maxYear;
                } else {
                    select.value = '';
                }
                select.dispatchEvent(new Event('change'));
                updateActiveFiltersChips();
            });
            chipsBar.appendChild(chip);
        });
    }

    // ─── #8 Column highlight ───────────────────────────────────
    function initColumnHighlight() {
        document.addEventListener('mouseover', (e) => {
            const th = e.target.closest('thead th');
            if (!th) return;

            const table = th.closest('table');
            if (!table || table.classList.contains('modal-table')) return;

            const colIndex = Array.from(th.parentNode.children).indexOf(th);
            if (colIndex <= 0) return; // No highlight en primera columna

            clearColumnHighlight(table);

            table.querySelectorAll(`tbody tr`).forEach(row => {
                const cell = row.children[colIndex];
                if (cell) cell.classList.add('col-highlight');
            });
            table.querySelectorAll(`tfoot tr`).forEach(row => {
                const cell = row.children[colIndex];
                if (cell) cell.classList.add('col-highlight');
            });
        });

        document.addEventListener('mouseout', (e) => {
            const th = e.target.closest('thead th');
            if (!th) return;
            const table = th.closest('table');
            if (table) clearColumnHighlight(table);
        });
    }

    function clearColumnHighlight(table) {
        table.querySelectorAll('.col-highlight').forEach(el => el.classList.remove('col-highlight'));
    }

    // ─── #7 Fila totales + #11 Formateo + #15 Scroll + Sin datos ──
    function patchRenderForEnhancements() {
        const originalRenderTable = window.renderTable;
        if (!originalRenderTable) return;

        window.renderTable = function () {
            originalRenderTable.call(this);

            const table = document.getElementById('data-table');
            if (!table) return;

            // Verificar si hay datos — Aviso sin datos
            if (typeof filteredData !== 'undefined' && filteredData.length === 0) {
                table.style.display = 'none';
                let emptyState = document.getElementById('empty-state-msg');
                if (!emptyState) {
                    emptyState = document.createElement('div');
                    emptyState.id = 'empty-state-msg';
                    emptyState.className = 'empty-state';
                    emptyState.innerHTML = typeof DOMPurify !== "undefined" ? DOMPurify.sanitize(`
            <div class="empty-state-icon">📊</div>
            <div class="empty-state-title">Sin datos disponibles</div>
            <div class="empty-state-desc">No se encontraron registros con los filtros seleccionados. Intente modificar los criterios de búsqueda.</div>
          `) : `
            <div class="empty-state-icon">📊</div>
            <div class="empty-state-title">Sin datos disponibles</div>
            <div class="empty-state-desc">No se encontraron registros con los filtros seleccionados. Intente modificar los criterios de búsqueda.</div>
          `;
                    table.parentNode.appendChild(emptyState);
                }
                emptyState.style.display = 'flex';

                // Ocultar hint si existe
                const hint = document.querySelector('.table-hint');
                if (hint) hint.style.display = 'none';
                return;
            } else {
                const emptyState = document.getElementById('empty-state-msg');
                if (emptyState) emptyState.style.display = 'none';
                table.style.display = 'table';

                const hint = document.querySelector('.table-hint');
                if (hint) hint.style.display = 'flex';
            }

            // #11 — Formateo consistente con Intl
            if (typeof formatter !== 'undefined' && typeof isPercentageMode !== 'undefined' && !isPercentageMode) {
                const tbody = table.querySelector('tbody');
                if (tbody) {
                    tbody.querySelectorAll('tr').forEach(tr => {
                        const cells = tr.children;
                        // Saltar primera y segunda columna (nombre + grupo), última (promedio)
                        for (let i = 2; i < cells.length - 1; i++) {
                            const td = cells[i];
                            const text = td.childNodes[0];
                            if (text && text.nodeType === Node.TEXT_NODE) {
                                const raw = text.textContent.trim().replace(/\./g, '').replace(/,/g, '');
                                const num = parseInt(raw, 10);
                                if (!isNaN(num) && num > 0) {
                                    text.textContent = formatter.format(num);
                                }
                            }
                        }
                    });
                }
            }

            // #7 — Agregar fila de totales
            addTotalsRow(table);

            // #15 — Scroll-to-top
            const tableSection = document.querySelector('.table-section') || document.querySelector('.table-card');
            if (tableSection) {
                tableSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }

            // Actualizar chips
            updateActiveFiltersChips();
        };
    }

    // ─── #7 Totales por columna ────────────────────────────────
    function addTotalsRow(table) {
        // Eliminar tfoot previo si existe
        const existingTfoot = table.querySelector('tfoot');
        if (existingTfoot) existingTfoot.remove();

        if (typeof filteredData === 'undefined' || typeof filteredMonths === 'undefined') return;
        if (typeof isPercentageMode !== 'undefined' && isPercentageMode) return; // No totales en modo %

        const tfoot = document.createElement('tfoot');
        const tr = document.createElement('tr');

        // Primera celda: "TOTAL"
        const tdLabel = document.createElement('td');
        tdLabel.textContent = '∑ TOTAL';
        tdLabel.style.fontWeight = '800';
        tr.appendChild(tdLabel);

        // Segunda celda (grupo/base/sexo/edad): vacía
        const tdGroup = document.createElement('td');
        tdGroup.textContent = '';
        tr.appendChild(tdGroup);

        // Calcular totales por mes
        let grandTotal = 0;
        let monthCount = 0;

        filteredMonths.forEach(month => {
            const td = document.createElement('td');
            let total = 0;
            filteredData.forEach(row => {
                const val = row[month];
                if (val && val > 0) total += val;
            });

            if (typeof formatter !== 'undefined') {
                td.textContent = total > 0 ? formatter.format(total) : '-';
            } else {
                td.textContent = total > 0 ? total.toLocaleString() : '-';
            }

            grandTotal += total;
            if (total > 0) monthCount++;
            tr.appendChild(td);
        });

        // Celda promedio de totales
        const tdAvg = document.createElement('td');
        const avgTotal = monthCount > 0 ? Math.round(grandTotal / monthCount) : 0;
        if (typeof formatter !== 'undefined') {
            tdAvg.textContent = avgTotal > 0 ? formatter.format(avgTotal) : '-';
        } else {
            tdAvg.textContent = avgTotal > 0 ? avgTotal.toLocaleString() : '-';
        }
        tdAvg.style.fontWeight = '800';
        tr.appendChild(tdAvg);

        tfoot.appendChild(tr);
        table.appendChild(tfoot);
    }

    // ─── #4 Conteo de resultados en modal ──────────────────────
    function patchModalResultsCount() {
        const originalDisplay = window.displayDetailedData;
        if (!originalDisplay) return;

        window.displayDetailedData = function (data) {
            originalDisplay.call(this, data);

            // Agregar conteo de resultados
            const paginationEl = document.getElementById('table-pagination');
            if (!paginationEl) return;

            let countEl = document.getElementById('results-count');
            if (!countEl) {
                countEl = document.createElement('div');
                countEl.id = 'results-count';
                countEl.className = 'results-count';
                paginationEl.parentNode.insertBefore(countEl, paginationEl);
            }

            const total = (typeof filteredTableData !== 'undefined') ? filteredTableData.length : (data ? data.length : 0);
            const rowsPerPageVal = (typeof rowsPerPage !== 'undefined') ? rowsPerPage : 10;
            const currentPageVal = (typeof currentPage !== 'undefined') ? currentPage : 1;
            const start = Math.min((currentPageVal - 1) * rowsPerPageVal + 1, total);
            const end = Math.min(currentPageVal * rowsPerPageVal, total);

            countEl.innerHTML = typeof DOMPurify !== "undefined" ? DOMPurify.sanitize(`Mostrando <strong>${start}-${end}</strong> de <strong>${total}</strong> registros`) : `Mostrando <strong>${start}-${end}</strong> de <strong>${total}</strong> registros`;
        };
    }

    // Exponer showToast para uso externo
    window.showToast = showToast;

})();
