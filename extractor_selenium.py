#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para extraer fechaNota de URLs de Telcel usando Selenium
Usa un navegador real para renderizar JavaScript y obtener el atributo correctamente
"""

import time
import csv
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    print("✅ Selenium instalado correctamente")
except ImportError:
    print("❌ Selenium no está instalado")
    print("Instálalo con: pip install selenium")
    print("También necesitas descargar ChromeDriver: https://chromedriver.chromium.org/")
    exit(1)


def extract_fecha_from_url(driver, url, timeout=10):
    """
    Abre una URL con Selenium y extrae el atributo fechaNota
    
    Args:
        driver: WebDriver instance
        url: URL to open
        timeout: Timeout en segundos
        
    Returns:
        fecha (str) o None si no encuentra
    """
    try:
        print(f"⏳ Abriendo: {url.split('/')[-1][:50]}...", end="", flush=True)
        
        # Navegar a la URL
        driver.get(url)
        
        # Esperar a que cargue el elemento con fechaNota (máximo 10 segundos)
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, "//*[@fechaNota]"))
            )
            # Extraer el atributo fechaNota
            fecha = element.get_attribute("fechaNota")
            print(f" ✅ {fecha}")
            return fecha
        except TimeoutException:
            print(f" ❌ Timeout (elemento no encontrado en {timeout}s)")
            return None
            
    except Exception as e:
        print(f" ❌ Error: {str(e)[:40]}")
        return None


def main():
    """Función principal"""
    
    print("🔍 EXTRACTOR DE FECHAS - USANDO SELENIUM")
    print("=" * 80)
    print()
    
    # Leer URLs
    urls_data = []
    try:
        with open('urls_a_procesar.txt', 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 2:
                    slug = parts[0]
                    visits = int(parts[1])
                    url = f"https://www.telcel.com/empresas/tendencias/notas/{slug}"
                    urls_data.append({
                        'url': url,
                        'visits': visits
                    })
    except FileNotFoundError:
        print("❌ No se encontró urls_a_procesar.txt")
        return
    
    print(f"📊 Total de URLs a procesar: {len(urls_data)}")
    print(f"⏱️ Esto puede tardar 30-40 minutos")
    print()
    
    # Configurar Selenium
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Descomenta para modo headless (sin ventana)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
    
    print("🌐 Iniciando navegador Chrome...")
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"❌ Error al iniciar Chrome: {e}")
        print("Asegúrate de tener ChromeDriver instalado en el PATH")
        print("Descárgalo de: https://chromedriver.chromium.org/")
        return
    
    results = []
    successful = 0
    failed = 0
    
    try:
        print(f"✅ Navegador iniciado")
        print()
        print("🔄 PROCESANDO URLs...")
        print("=" * 80)
        print()
        
        for i, item in enumerate(urls_data, 1):
            url = item['url']
            visits = item['visits']
            
            # Extraer fecha
            fecha = extract_fecha_from_url(driver, url)
            
            # Guardar resultado
            result = {
                'url': url,
                'visits': visits,
                'fecha': fecha or ''
            }
            results.append(result)
            
            if fecha:
                successful += 1
            else:
                failed += 1
            
            # Mostrar progreso cada 10 URLs
            if i % 10 == 0:
                percent = round((i / len(urls_data)) * 100)
                print(f"\n✅ Procesadas {i}/{len(urls_data)} ({percent}%)...")
                print()
            
            # Delay entre requests (1 segundo)
            time.sleep(1)
        
        # Cerrar navegador
        print()
        print("=" * 80)
        print("🔌 Cerrando navegador...")
        driver.quit()
        
        # Guardar resultados en CSV
        print()
        print("💾 GUARDANDO RESULTADOS...")
        
        csv_filename = 'Telcel_Fechas_Extraidas_Selenium.csv'
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['url', 'visits', 'fecha'])
            writer.writeheader()
            writer.writerows(results)
        
        print(f"✅ Archivo guardado: {csv_filename}")
        print()
        
        # Mostrar estadísticas
        print("📊 ESTADÍSTICAS FINALES:")
        print(f"   Total procesadas: {len(results)}")
        print(f"   ✅ Con fecha: {successful}")
        print(f"   ❌ Sin fecha: {failed}")
        print()
        print("✅ ¡PROCESO COMPLETADO!")
        print()
        print(f"El archivo CSV está listo para abrir en Excel: {csv_filename}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
        driver.quit()
    except Exception as e:
        print(f"\n\n❌ Error durante el proceso: {e}")
        driver.quit()


if __name__ == '__main__':
    main()
