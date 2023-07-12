
library(jsonlite)
library(httr)
key = "XXXXXXXXXXX"
options(scipen=999)


#  Descargamos el maestro de Valores construyendo diréctamente la url

  mercado = "IBEX"
  
  url = paste("https://miax-gateway-jog4ew3z3q-ew.a.run.app/data/ticker_master?",
              "competi=mia_11", "&market=", mercado, "&key=", key, sep = "")
  
  datos = fromJSON(url, flatten = TRUE)
  datos = as.data.frame(datos$master)

  #  Descargamos el maestro de Valores haciendo un GET

  url = "https://miax-gateway-jog4ew3z3q-ew.a.run.app/data/ticker_master"
  
  competi="mia_4"
  market="IBEX"
  
  datos <- GET(url, query = list(competi=competi, market=market, key=key))
  datos = content(datos, type = "application/json")
  
  datos = as.data.frame(matrix(unlist(datos$master), byrow=T, ncol = 4))
    colnames(datos) = c("ticker", "start_date", "end_date", "n_days")


# Descargamos la serie de precios
  
  url = "https://miax-gateway-jog4ew3z3q-ew.a.run.app/data/time_series"
  
  market="IBEX"
  ticker="SAN"
  
  datos <- GET(url, query = list(market=market, key=key, ticker=ticker, close = F))
  datos = content(datos, type = "application/json")
  
  datos = fromJSON(datos, flatten = TRUE)
  
  fechas = names(unlist(datos[[1]]))
  fechas = as.POSIXct(as.numeric(fechas)/1000, format = "%Y-%m-%d", origin = "1970-01-01")
  
  datos = as.data.frame(matrix(unlist(datos), byrow=F, ncol = 5))
    colnames(datos) = c("open", "high", "low", "close", "vol")
    rownames(datos) = fechas

  
# Descargamos la serie del índice

  url = "https://miax-gateway-jog4ew3z3q-ew.a.run.app/data/time_series"
  
  market="IBEX"
  ticker="benchmark"
  
  datos <- GET(url, query = list(market=market, key=key, ticker=ticker, close = F))
  datos = content(datos, type = "application/json")
  
  datos = fromJSON(datos, flatten = TRUE)
  
  fechas = names(unlist(datos[[1]]))
  fechas = as.POSIXct(as.numeric(fechas)/1000, format = "%Y-%m-%d", origin = "1970-01-01")
  
  datos = as.data.frame(matrix(unlist(datos), byrow=F, ncol = 5))
    colnames(datos) = c("open", "high", "low", "close", "vol")
    rownames(datos) = fechas


# Consulta algoritmos del usuario

  url = "https://miax-gateway-jog4ew3z3q-ew.a.run.app/participants/algorithms"
  
  competi = "mia_4"
  
  datos <- GET(url, query = list(competi = competi, key=key))
  datos = content(datos, type = "application/json")
  
  datos = as.data.frame(matrix(unlist(datos), byrow=T, ncol = 4))
    colnames(datos) = c("user_id", "algo_tag", "algo_name", "algo_type")


# Agregar una asignacion de pesos a un algoritmo

  url = paste("https://miax-gateway-jog4ew3z3q-ew.a.run.app/participants/allocation?key=",key,sep = "")
  
  competi = "mia_4"
  algo_tag = "gmelendez_algo1"
  market = "IBEX"
  date = Sys.Date()-7 # Introduce la fecha en la que quieras asignar los pesos con formato ("%Y-%m-%d")
  
  ticker <- c('TEF','SAN','ITX','REP','AMS')
  alloc <- rep(0.15, 5)
  
  allocation <- data.frame(ticker, alloc)
  toJSON(allocation)
  
  query = list(competi = competi, 
               algo_tag = algo_tag, 
               market = market, 
               date = date, 
               allocation = allocation)
  
  query_json = toJSON(query, auto_unbox = T)
  
  contenido = POST(url, body = query_json)
  contenido = content(contenido, type = "application/json")

  
# Consulta las asignaciones de pesos que has realizado

  url = "https://miax-gateway-jog4ew3z3q-ew.a.run.app/participants/algo_allocations"
  
  competi = "mia_4"
  key = key
  algo_tag = "gmelendez_algo1"
  market = "IBEX"
  
  asignaciones <- GET(url, query = list(competi = competi, key=key, algo_tag = algo_tag, market = market))
  asignaciones = content(asignaciones, type = "application/json")
  
  asignaciones = as.data.frame(matrix(unlist(asignaciones), byrow=T, ncol = 1))
  
  
# Verifica el resultado del backtesting
  
  url = paste("https://miax-gateway-jog4ew3z3q-ew.a.run.app/participants/exec_algo?key=",key,sep = "")
  
  query = list(competi = "mia_4", 
               algo_tag = "gmelendez_algo1", 
               market = "IBEX")
 
  query_json = toJSON(query, auto_unbox = T)
  
  resultado = POST(url, body = query_json)
  resultado = content(resultado, type = "application/json")
  
  
# Re-iniciar las asginaciones para un algoritmo
  
  url = paste("https://miax-gateway-jog4ew3z3q-ew.a.run.app/participants/delete_allocations?key=",key,sep = "")
  
  query = list(competi = "mia_4", 
               algo_tag = "gmelendez_algo1", 
               market = "IBEX")
  
  query_json = toJSON(query, auto_unbox = T)
  
  respuesta = POST(url, body = query_json)
  respuesta = content(respuesta, type = "application/json")
  
  

  