from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd
from openpyxl import load_workbook
import os

##### TABLA DE POSICIONES #####

# Configuración opciones del navegador
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")  # Se abre la interfaz

path = "D:\OneDrive\\Escritorio\\proyectoGaby\\Python\\WebScraping\\chromedriver-win64\\chromedriver.exe"

# Utilizar el servicio para proporcionar la ruta del ejecutable
service = Service(path)

# Crear la instancia del objeto webdriver.Chrome
driver = webdriver.Chrome(service=service, options=chrome_options)

# Abrir la página web
driver.get("https://www.flashscore.es/futbol/ecuador/liga-pro/clasificacion/#/pKFG2zll/table/overall")
time.sleep(10)  # Esperar 10 segundos para que la página cargue

# Esperar hasta 30 segundos para que el botón de aceptar cookies esté presente
wait = WebDriverWait(driver, 30)
try:
    cookie_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')))
    cookie_button.click()
    time.sleep(1)
except TimeoutException:
    print("No se encontró el botón de cookies, continuando sin hacer clic...")

# Desplazarse gradualmente por la página
for _ in range(3):
    driver.execute_script("window.scrollBy(0, window.innerHeight);")
    time.sleep(1)

# Esperar hasta 30 segundos para que al menos un elemento esté presente
wait = WebDriverWait(driver, 30)

try:
    Posicion = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="table__cell table__cell--rank table__cell--sorted"]')))
    Nombre = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//a[@class="tableCellParticipant__name"]')))
    PJ_G_E_P = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//span[contains(@class, "table__cell--value") and not(contains(@class, "table__cell--score")) and not(contains(@class, "table__cell--goalsForAgainstDiff")) and not(contains(@class, "table__cell--points"))]')))
    DG = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//span[contains(@class, "table__cell--goalsForAgainstDiff")]')))
    Puntos = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//span[contains(@class, "table__cell--points")]')))
    Forma = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="table__cell table__cell--form"]')))
except TimeoutException:
    print("No se encontraron todos los elementos necesarios. Guardando el HTML para depuración.")
    with open("page_source.html", "w", encoding="utf-8") as file:
        file.write(driver.page_source)
    driver.quit()
    exit()

# Inicializar listas para los datos
Puestos = []
Nombre_Equipo = []
PJ = []
G = []
E = []
P = []
DG_List = []
PTS = []
Forma_Lista = []

# Extraer los datos de las posiciones
for i in Posicion:
    Puestos.append(i.text)

# Extraer los nombres de los equipos
for i in Nombre:
    Nombre_Equipo.append(i.text)

# Extraer los partidos jugados, ganados, empatados y perdidos
for index, i in enumerate(PJ_G_E_P):
    if index % 4 == 0:
        PJ.append(i.text)
    elif index % 4 == 1:
        G.append(i.text)
    elif index % 4 == 2:
        E.append(i.text)
    elif index % 4 == 3:
        P.append(i.text)

# Extraer la diferencia de goles
for i in DG:
    DG_List.append(i.text)

# Extraer los puntos
for i in Puntos:
    PTS.append(i.text)

# Extraer la forma de los últimos partidos
for form_cell in Forma:
    forms = form_cell.find_elements(By.XPATH, './/div[contains(@class, "tableCellFormIcon")]//span[@class="_simpleText_18bk2_4 _webTypeSimpleText01_18bk2_8"]')
    form_string = ''.join([f.text for f in forms])  # Tomar el texto de cada span
    Forma_Lista.append(form_string)

# Verificar las longitudes de las listas
print("Longitud de Puestos:", len(Puestos))
print("Longitud de Nombre_Equipo:", len(Nombre_Equipo))
print("Longitud de PJ:", len(PJ))
print("Longitud de G:", len(G))
print("Longitud de E:", len(E))
print("Longitud de P:", len(P))
print("Longitud de DG_List:", len(DG_List))
print("Longitud de PTS:", len(PTS))
print("Longitud de Forma:", len(Forma_Lista))

# Crear el DataFrame
df2 = pd.DataFrame({
    "Puestos": Puestos,
    "Nombre Equipo": Nombre_Equipo,
    "PJ": PJ,
    "G": G,
    "E": E,
    "P": P,
    "DG": DG_List,
    "PTS": PTS,
    "Forma": Forma_Lista
})

# Cerrar el navegador
driver.quit()

# Nombre del archivo Excel
archivo_excel = "D:\OneDrive\\Escritorio\\proyectoGaby\\Python\\WebScraping\\LigaEcuatorianaxlsx"

# Nombre de la hoja
nombre_hoja = "Tabla de posiciones"

# Guardar el DataFrame en el archivo Excel
with pd.ExcelWriter(archivo_excel, engine="openpyxl", mode="w") as writer:
    df2.to_excel(writer, sheet_name=nombre_hoja, index=False)

print(f"La información se ha guardado en el archivo '{archivo_excel}' en la hoja '{nombre_hoja}'.")
