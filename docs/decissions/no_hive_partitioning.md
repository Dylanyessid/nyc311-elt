## No Hive Partitioning
Ya que hay una columna en la fuente llamada create_date, podria sobrescrbir el duckdb con el campo de las carpetas

Implicación: El DuckDB no podría "saltar" carpetas, sin embargo, en este caso no es un inconveniente mayor. El proyecto es de aprendizaje y la carga de datos no es lo suficientementa masiva que lo justifique.