ENDPOINT=127.0.0.1
# API
# Get recently played stations
curl "http://${ENDPOINT}/api/stations?category=recently"
# Get highest rated stations
curl "http://${ENDPOINT}/api/stations?category=voted"
# Get stations by language, specify by language paramter (default=german)
curl "http://${ENDPOINT}/api/stations?category=language&language=dutch"
# Get stations by country, specify by country paramter (default=Germany)
curl "http://${ENDPOINT}/api/stations?category=country&country=The%20Netherlands"

# Ycast XML calls
curl "http://${ENDPOINT}/setupapp"
# Search by name
curl "http://${ENDPOINT}/ycast/search/?search=Pinguin"
# List top directories (Genres, Countries, Languages, Most Popular).
curl "http://${ENDPOINT}/ycast/radiobrowser/"
# Play station
curl "http://${ENDPOINT}/ycast/play?id=stationid"
# Get station info
curl "http://${ENDPOINT}/ycast/station?id=stationid"
curl "http://${ENDPOINT}/ycast/icon?id=stationid"
# Get station icon

