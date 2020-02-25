SELECT c.country, f.name, st_makeline(c.geom, f.geom)
FROM countries AS c
INNER JOIN fc
	ON c.country=fc.country
INNER JOIN firms AS f
	ON fc.name=f.name;