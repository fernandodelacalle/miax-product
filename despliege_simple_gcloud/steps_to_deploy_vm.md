---
marp: true
theme: default
paginate: true
---

<style>
img[alt~="center"] {
  display: block;
  margin: 0 auto;
}
</style>

#  Despliege simple en una máquina virtual

---


1. Crear instancia

2. Conenctar por SSH

3. Subimos el fichero del algo

4. Ejecutar
```bash
sudo apt update
sudo apt install python3-pip
pip3 install pandas requests
```

---

5. Crear el crontab

- Para ejecutar algo en un horario determinado existen múltiples opciones.
- Crontab es un comando para máquinas linux que nos permite ejecutar un comando a una hora determinada.
- El comando se ejecuta de la siguiente manera:
```bash  
  crontab -e
```

---

- Tenemos que editar en la pantalla que se abre para poner:
```bash 
* * * * * python /path/mi_algo.py
```
Donde * * * * *:
```bash
* * * * * command* - minute (0-59)
* - hour (0-23)
* - day of the month (1-31)
* - month (1-12)
* - day of the week (0-6, 0 is Sunday)
command - command to execute
```
- Se puede entender mejor en: https://crontab.guru/


---
- Por ejemplo:
```bash
01 9 * * 1-5 python /path/mi_algo.py
```
- Ejecutaria de lunes a viernes a las 9:01 el comando /path/mi_algo.py.

---

- Para editar con vim: i para entrar, editamos, salimos con esc y guardamos cons :wq
- Si queremos tener guardados los logs podemos poner:
```bash
01 9 * * 1-5 python /path/mi_algo.py > /path/mi_algo/logs/cron_`date +\%Y-\%m-\%d_\%H:\%M:\%S`.log 2>&1
```

---


- Si queremos ver nuestros crons utilizamos el comando:
```bash  
    crontab -l
```

- Ejemplo:
```bash  
    */1 * * * * python3 /home/fernando_decalle/test.py > /home/fernando_decalle/cron_`date +\%Y-\%m-\%d_\%H:\%M:\%S`.log 2>&1 
```



---

# Ejercico
- Ejecuta el programa python test.py cada minuto y guarda un log cada vez que se ejecuta.
- Ejecutar:
```bash
crontab -e
```
- Insertar la linea:
```bash
* * * * * python3 /home/fernando_decalle/algo_ew.py > /home/fernando_decalle/cron_`date +\%Y-\%m-\%d_\%H:\%M:\%S`.log 2>&1
```
Sustituir /home/fernando_decalle/ por lo que salga del comando pwd.
- Salir del editor con ctrl+x
- Guardar con yes


---

- Susituir por cuando quereis que se ejecute: 
```bash
    0 8 * * 1-5 -> 8 de la mañana  de lunes a viernes
```
- Por ejemplo ```* * * * *``` -> cada minuto
-Tener en cuenta que la hora puede ser distinta, Para ver la hora:
```bash
date
```