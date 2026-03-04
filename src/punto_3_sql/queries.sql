-- ============================================================
-- PRUEBA TÉCNICA SIMETRIK — Punto 3: Análisis SQL
-- Base: clientes, productos, ventas
-- Motor: SQLite (sqliteonline.com — seleccionar engine SQLite)
-- Algunas preguntas que se pueden responder con la data
-- ============================================================

-- QUERY 1: Total vendido por cliente
SELECT
    c.nombre,
    c.ciudad,
    COUNT(v.id_venta)          AS num_compras,
    SUM(v.cantidad)            AS unidades_totales,
    SUM(v.cantidad * p.precio) AS monto_total
FROM ventas v
JOIN clientes c ON c.id_cliente = v.id_cliente
JOIN productos p ON p.id_producto = v.id_producto
GROUP BY c.id_cliente, c.nombre, c.ciudad
ORDER BY monto_total DESC;


-- QUERY 2: Top 5 productos más vendidos (por unidades)
SELECT
    p.nombre_producto,
    SUM(v.cantidad)   AS unidades_vendidas,
    COUNT(v.id_venta) AS num_transacciones
FROM ventas v
JOIN productos p ON p.id_producto = v.id_producto
GROUP BY p.id_producto, p.nombre_producto
ORDER BY unidades_vendidas DESC
LIMIT 5;


-- QUERY 3: Ventas por ciudad y mes
SELECT
    c.ciudad,
    strftime('%Y-%m', v.fecha) AS mes,
    COUNT(v.id_venta)          AS transacciones,
    SUM(v.cantidad)            AS unidades
FROM ventas v
JOIN clientes c ON c.id_cliente = v.id_cliente
GROUP BY c.ciudad, mes
ORDER BY c.ciudad, mes;


-- QUERY 4: Clientes que NUNCA han comprado 
SELECT
    c.id_cliente,
    c.nombre,
    c.ciudad
FROM clientes c
WHERE NOT EXISTS (
    SELECT 1 FROM ventas v WHERE v.id_cliente = c.id_cliente
);


-- QUERY 5: Ticket promedio monetario por ciudad + ranking
-- ticket_promedio = monto total / número de transacciones
SELECT
    ciudad,
    total_compras,
    monto_total,
    ROUND(monto_total * 1.0 / NULLIF(total_compras, 0), 2) AS ticket_promedio,
    RANK() OVER (ORDER BY monto_total DESC)                AS ranking
FROM (
    SELECT
        c.ciudad,
        COUNT(v.id_venta)          AS total_compras,
        SUM(v.cantidad * p.precio) AS monto_total
    FROM ventas v
    JOIN clientes  c ON c.id_cliente  = v.id_cliente
    JOIN productos p ON p.id_producto = v.id_producto
    GROUP BY c.ciudad
) sub
ORDER BY ranking;
