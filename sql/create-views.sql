
DROP VIEW IF EXISTS exhibitor_addresses;

CREATE VIEW exhibitor_addresses AS
    SELECT
        e.name, 
        MAX(e.add) AS add, 
        MAX(e.country) AS country, 
        STRING_AGG(b.type, ', ') AS types, 
        STRING_AGG(eb.booth_no, ', ') AS booths
    FROM exhibitors e
        LEFT JOIN exhibitor_by_booth eb 
        ON e.name = eb.name
            LEFT JOIN booths b 
            ON eb.booth_no=b.booth_no
    GROUP BY e.name
    ORDER BY types;