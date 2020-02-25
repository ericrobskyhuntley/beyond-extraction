SELECT 
    f.name AS firm, 
    b.id AS booth, 
    fb.id AS id, 
    ST_MAKELINE(f.geom, ST_CENTROID(b.geom)) AS geom
FROM 
    firms_ix AS f
    INNER JOIN firms_ix_by_booth AS fb
	    ON f.name=fb.name
    INNER JOIN booths AS b
	    ON fb.booth=b.id;