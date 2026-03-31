const fs = require('fs');

const filePath = "d:\\GitHub\\ALGARROBO_BASE2\\backend\\app21.py";
let code = fs.readFileSync(filePath, "utf-8");

// H-10: Exposed Excepcions
// replaces return jsonify({"detail": str(e)}), 500 or similar
code = code.replace(/return jsonify\(\{[\s\S]*?"detail":\s*str\(e\)[\s\S]*?\}\), 500/g, 'return jsonify({"message": "Error logueado para auditoria. Servidor no respondio."}), 500');
code = code.replace(/return jsonify\(\{[\s\S]*?"detail":\s*str\(e\)[\s\S]*?\}\)/g, 'return jsonify({"message": "Error logueado para auditoria. Servidor no respondio."})');

// H-09: Endpoints Sin Autenticacion
const routesToSecure = [
    '("/proyectos/<int:pid>/geomapas", methods=["GET"])',
    '("/proyectos/<int:pid>/observaciones", methods=["GET"])',
    '("/api/mobile/reportes/todos", methods=["GET"])',
    '("/api/mobile/reportes/<int:rid>/comentarios", methods=["GET"])',
    '("/api/mobile/reportes/<int:rid>/fotos", methods=["GET"])',
    '("/api/licitaciones/docs/<path:filename>")',
    '("/api/licitaciones/lib/<path:filename>")'
];

routesToSecure.forEach(route => {
    // Escape route for regex
    const escaped = route.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const rx = new RegExp(`(@app\\.route${escaped}\\s*\\n)(?!@session_required)(?!@admin_required)`, 'g');
    code = code.replace(rx, '$1@session_required\n');
});

// also mobile ones might just be <rid> instead of <int:rid>
const genericRoutes = [
    '("/api/mobile/reportes/<rid>/comentarios"',
    '("/api/mobile/reportes/<rid>/fotos"'
];
genericRoutes.forEach(route => {
    const escaped = route.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const rx = new RegExp(`(@app\\.route${escaped}[^\\n]*\\n)(?!@session_required)(?!@admin_required)`, 'g');
    code = code.replace(rx, '$1@session_required\n');
});


// H-20: Cleanup expired sessions
const cleanupOld = `def cleanup_expired_sessions():
    pass`
const cleanupStr2 = `    """Limpia sesiones expiradas - llamar periódicamente"""`;

const cleanupNew = `def cleanup_expired_sessions():
    """Limpia sesiones expiradas en base de datos"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn: return
        with conn.cursor() as cur:
            cur.execute("DELETE FROM jwt_blocklist WHERE created_at < NOW() - INTERVAL '48 hours'")
        conn.commit()
    except Exception as e:
        if conn: conn.rollback()
    finally:
        if conn: release_db_connection(conn)
`;

code = code.replace(cleanupOld, cleanupNew);
code = code.replace(cleanupStr2, ""); // removes orphan docstring

// H-07: Inyeccion SQL CRUD
const tablesList = `ALLOWED_TABLES_READ = {"areas", "financiamientos", "estados_postulacion", "sectores", "lineamientos_estrategicos", "etapas_proyecto", "estados_proyecto"}`;

const crudOld = `def crud_simple(tabla, current_user_id):
    conn = get_db_connection()`;

const crudNew = `${tablesList}

def crud_simple(tabla, current_user_id):
    if tabla not in ALLOWED_TABLES_READ:
        return jsonify({"message": "Tabla no permitida"}), 403
    conn = get_db_connection()`;

if (!code.includes("ALLOWED_TABLES_READ")) {
    code = code.replace(crudOld, crudNew);
}

['generic_create', 'generic_update', 'generic_delete'].forEach(func => {
    const rx = new RegExp(`(def ${func}\\(table_name[^\\)]*\\):\\n)`, 'g');
    code = code.replace(rx, `$1    if table_name not in ALLOWED_TABLES_READ:\\n        return jsonify({"message": "Tabla no permitida"}), 403\\n`);
});

fs.writeFileSync(filePath, code, "utf-8");
console.log("Refactoring complete");
