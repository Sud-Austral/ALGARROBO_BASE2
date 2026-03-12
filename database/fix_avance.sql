-- Migración para normalizar avance_total_porcentaje de 0-1 a 0-100
-- Solo afecta a valores entre 0.001 y 1.0 (asumiendo que fueron ingresados como decimales)
-- Valores como 0.0 se quedan igual.

UPDATE proyectos 
SET avance_total_porcentaje = avance_total_porcentaje * 100 
WHERE avance_total_porcentaje > 0 
  AND avance_total_porcentaje <= 1.0;

-- Sincronizar avance_total_decimal para que siempre sea la fracción de 0-100
UPDATE proyectos
SET avance_total_decimal = avance_total_porcentaje / 100.0
WHERE avance_total_porcentaje IS NOT NULL;
