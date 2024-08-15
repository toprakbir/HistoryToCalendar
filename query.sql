SELECT urls.title AS TITLE, 
    last_visit_time as last_visited, 
    visits.visit_duration AS Duration
FROM urls LEFT JOIN visits ON urls.id = visits.url