SELECT 
	f.name AS firm, 
	ST_UNION(ST_MAKELINE(f.geom, ST_CENTROID(c.geom))) AS geom
FROM 
	firms_ix AS f
	INNER JOIN firms_ix_by_country AS fc
		ON f.name=fc.name
	INNER JOIN countries AS c
		ON fc.country=c.country
GROUP BY (f.name);