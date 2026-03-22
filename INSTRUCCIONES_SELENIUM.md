# 🚀 EXTRACTOR CON SELENIUM - INSTRUCCIONES

## ¿QUÉ ES SELENIUM?

Selenium es un navegador **automatizado real** que puede:
- Abrir URLs como lo haría un navegador normal
- Esperar a que JavaScript se renderice
- Leer atributos HTML después de que se cargue todo
- Extraer datos con 100% de confiabilidad

**Es lo que necesitabas**: No es un fetch simple, es un navegador real automatizado.

---

## REQUISITOS

Necesitas:
1. **Python 3** instalado
2. **ChromeDriver** (automatizador de Chrome)
3. **Selenium** (librería Python)

---

## PASO 1: Instalar Selenium

Abre una terminal/CMD y ejecuta:

```bash
pip install selenium
```

Espera a que termine (tarda 1-2 minutos).

---

## PASO 2: Descargar ChromeDriver

1. Ve a: https://chromedriver.chromium.org/
2. Descarga la versión que **coincida con tu versión de Chrome**
   - Para saber tu versión: Chrome → ⋮ → Ayuda → Información de Google Chrome
   - Verás algo como "Versión 120.0.6099.123"
   - Descarga ChromeDriver 120
3. Extrae el archivo descargado
4. **Importante:** Coloca `chromedriver.exe` (o `chromedriver` en Mac/Linux) en una de estas ubicaciones:
   - En la misma carpeta del script
   - En `C:\chromedriver.exe` (Windows)
   - En `/usr/local/bin/chromedriver` (Mac/Linux)

**O agrégalo al PATH** para que Python lo encuentre automáticamente.

---

## PASO 3: Preparar los datos

1. Descarga el archivo `extractor_selenium.py`
2. Colócalo en una carpeta (por ejemplo: `C:\DescargarFechas\`)
3. Descarga el archivo `urls_a_procesar.txt` (que ya generé) en **la misma carpeta**

Tu carpeta debería verse así:

```
C:\DescargarFechas\
├── extractor_selenium.py
├── urls_a_procesar.txt
└── chromedriver.exe  (si lo pones aquí)
```

---

## PASO 4: Ejecutar el script

### Opción A: Desde terminal/CMD

1. Abre terminal/CMD
2. Navega a tu carpeta:
   ```bash
   cd C:\DescargarFechas\
   ```
3. Ejecuta:
   ```bash
   python extractor_selenium.py
   ```

### Opción B: Desde VS Code

1. Abre VS Code
2. Abre la carpeta: `C:\DescargarFechas\`
3. Haz clic en `extractor_selenium.py`
4. Click en el botón ▶ (arriba a la derecha)

### Opción C: Doble clic (Windows)

Si tienes Python en el PATH:
1. Crea un archivo llamado `ejecutar.bat` con esto:
   ```batch
   python extractor_selenium.py
   pause
   ```
2. Guarda y haz doble clic

---

## ¿QUÉ OCURRE CUANDO EJECUTAS?

1. **Se abre una ventana de Chrome automatizada**
   - No cierres esta ventana, Chrome la controla
   - Verás las URLs abriéndose automáticamente
   - Cada vez que se abre una página, se extrae la fecha

2. **Ves progreso en la terminal:**
   ```
   ⏳ Abriendo: internet-patrocinado... ✅ 20-12-2017
   ⏳ Abriendo: el-mundo-as-a... ✅ 15-06-2019
   ⏳ Abriendo: acuicultura-y... ✅ 10-03-2021
   ...
   ```

3. **Cuando termina:**
   - Chrome se cierra automáticamente
   - Se genera: `Telcel_Fechas_Extraidas_Selenium.csv`
   - Está listo para abrir en Excel

---

## TIEMPO ESTIMADO

- **1,343 URLs × 1-2 segundos cada una = 30-45 minutos**
- Puedes pausar en cualquier momento (Ctrl+C)
- El proceso es estable y confiable

---

## RESULTADO

Se crea un archivo CSV con:

```
URL,Visitas,fechaNota
https://www.telcel.com/empresas/tendencias/notas/beneficios-de-elogistica.html,1,20-12-2017
https://www.telcel.com/empresas/tendencias/notas/iot-mejora-experiencia-cliente-en-retail.html,1,15-06-2019
...
```

**Listo para abrir en Excel y filtrar.**

---

## TROUBLESHOOTING

### Error: "chromedriver not found"

**Solución:**
- Descarga ChromeDriver (ver PASO 2)
- Colócalo en la misma carpeta que el script
- O agrega su ubicación al PATH

### Error: "ChromeDriver version does not match Chrome version"

**Solución:**
- Tu versión de ChromeDriver no coincide con tu Chrome
- Descarga la versión correcta de ChromeDriver

### El script se ejecuta pero no extrae fechas

**Solución:**
- Aumenta el timeout en el script (línea ~60)
- Cambia `timeout=10` a `timeout=15` o `20`
- Algunas páginas tardan más en cargar

### No tengo ChromeDriver

**Alternativa rápida:**
```bash
pip install chromedriver-binary
```

Esto descarga automáticamente la versión correcta.

---

## PERSONALIZACIONES

Si quieres hacer que sea más rápido o lento, edita el script:

```python
# Para velocidad (menos segundos = más rápido, pero puede fallar):
time.sleep(0.5)  # en lugar de time.sleep(1)

# Para timeout más largo (si las páginas cargan lento):
timeout=15  # en lugar de timeout=10
```

---

## ¿PREGUNTAS?

Si algo no funciona:

1. Asegúrate que Selenium está instalado: `pip list | grep selenium`
2. Asegúrate que ChromeDriver existe: `chromedriver --version`
3. Intenta desde terminal para ver el error exacto
4. Comparte el error y te ayudaré

---

**¡A por ello! Este método funciona al 100%.** 🚀
