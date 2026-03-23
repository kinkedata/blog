#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clasificador.py — Clasifica notas del blog Telcel por Solución y Servicio.
Lee notas_blog_telcel_con_visitas.xlsx, abre cada URL, busca keywords del
catálogo y escribe las columnas "solución" y "servicio".
Checkpoint: clasificador_checkpoint.json (guarda la última fila procesada).
"""

import sys
import json
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
EXCEL_IN  = os.path.join(BASE_DIR, "notas_blog_telcel_con_visitas.xlsx")
CHECKPOINT = os.path.join(BASE_DIR, "clasificador_checkpoint.json")
STOP_FILE  = os.path.join(BASE_DIR, "stop_signal.txt")

# ── Catálogo: Solución → { keywords, servicios: { nombre: [kws] } } ───────────
CATALOGO = {
    "Conectividad Telcel": {
        "keywords": [
            "esim", "e-sim", "m2m", "machine to machine",
            "redes privadas de datos", "red privada de datos",
            "conectividad avanzada", "conectividad telcel",
        ],
        "servicios": {
            "eSIM": ["esim", "e-sim"],
            "Conectividad Avanzada M2M": ["m2m", "machine to machine", "conectividad avanzada m2m"],
            "Redes Privadas de Datos": ["redes privadas de datos", "red privada de datos"],
        },
    },
    "Comunicación Empresarial": {
        "keywords": [
            "movilpyme", "movil pyme", "formularios verum", "verum",
            "sekurmessenger", "sekur messenger", "sekur",
            "push to talk", "agnet", "comunicación empresarial",
        ],
        "servicios": {
            "Control de Ventas MovilPyme": ["movilpyme", "movil pyme"],
            "Formularios Verum": ["formularios verum", "verum"],
            "SekurMessenger": ["sekurmessenger", "sekur messenger", "sekur"],
            "Push to Talk powered by Agnet": ["push to talk", "agnet"],
        },
    },
    "Seguridad": {
        "keywords": [
            "mdm", "control de dispositivos", "control movil empresarial",
            "control móvil empresarial", "norton empresas", "norton",
            "lookout", "secure mobile", "ciberseguridad",
        ],
        "servicios": {
            "Control de Dispositivos MDM": ["mdm", "control de dispositivos"],
            "Control Móvil Empresarial": ["control movil empresarial", "control móvil empresarial"],
            "Norton Empresas": ["norton"],
            "Lookout": ["lookout"],
            "Secure Mobile": ["secure mobile"],
        },
    },
    "Business Intelligence": {
        "keywords": [
            "geodata", "autenticación móvil", "autenticacion movil",
            "indicadores móviles", "indicadores moviles",
            "business intelligence", "inteligencia de negocios",
        ],
        "servicios": {
            "Geodata": ["geodata"],
            "Autenticación Móvil": ["autenticación móvil", "autenticacion movil"],
            "Indicadores Móviles": ["indicadores móviles", "indicadores moviles"],
        },
    },
    "Gestión de Fuerza de Campo": {
        "keywords": [
            "gfc", "fuerza de campo", "localización empresarial telcel",
            "localizacion empresarial telcel", "let telcel",
            "cobranza", "promotoria", "promotoría", "merchandising",
            "rondines", "vigilancia", "logística", "logistica",
            "operacion de servicio en campo", "control de sucursales",
        ],
        "servicios": {
            "Localización Empresarial Telcel": [
                "localización empresarial telcel", "localizacion empresarial telcel", "let telcel",
            ],
            "Cobranza": ["cobranza"],
            "Promotoría y merchandising": ["promotoria", "promotoría", "merchandising"],
            "Operación de servicio en campo": ["operacion de servicio en campo", "servicio en campo"],
            "Control de sucursales": ["control de sucursales"],
            "Seguridad (rondines/vigilancia)": ["rondines", "vigilancia"],
            "Logística": ["logística", "logistica"],
        },
    },
    "Mobile Marketing": {
        "keywords": [
            "internet patrocinado", "distribución de aplicaciones",
            "distribucion de aplicaciones", "recompensas",
            "mensajería masiva", "mensajeria masiva",
            "mensajes rcs", "rcs", "mobile marketing",
        ],
        "servicios": {
            "Internet Patrocinado": ["internet patrocinado"],
            "Distribución de Aplicaciones": ["distribución de aplicaciones", "distribucion de aplicaciones"],
            "Recompensas": ["recompensas"],
            "Mensajería Masiva Empresarial SMS y RCS": ["mensajería masiva", "mensajeria masiva", "sms masivo"],
            "Mensajes RCS": ["mensajes rcs", "rcs"],
        },
    },
    "Servicios Cloud": {
        "keywords": [
            "microsoft 365", "office 365", "hosting", "desarrollo web",
            "claro drive", "google workspace", "g suite", "aspel",
            "vmware", "workspace one", "servicios cloud", "nube empresarial",
        ],
        "servicios": {
            "Microsoft 365": ["microsoft 365", "office 365", "microsoft365"],
            "Hosting y Desarrollo Web": ["hosting", "desarrollo web"],
            "Claro Drive Negocio": ["claro drive"],
            "Google Workspace": ["google workspace", "g suite"],
            "Aspel": ["aspel"],
            "VMware Workspace ONE": ["vmware", "workspace one"],
        },
    },
    "Gestión Vehicular Telcel": {
        "keywords": [
            "gvt", "gestión vehicular", "gestion vehicular",
            "video a bordo", "cadena de frío", "cadena de frio",
            "hábitos de conducción", "habitos de conduccion",
            "medición de combustible", "medicion de combustible",
            "módulo de ruteo", "modulo de ruteo", "ruteo",
            "telemetría", "telemetria", "flota vehicular",
            "rastreo vehicular", "rastreo gps",
        ],
        "servicios": {
            "Video a bordo": ["video a bordo"],
            "Cadena de frío": ["cadena de frío", "cadena de frio"],
            "Hábitos de conducción": ["hábitos de conducción", "habitos de conduccion"],
            "Medición de combustible": ["medición de combustible", "medicion de combustible"],
            "Módulo de ruteo": ["módulo de ruteo", "modulo de ruteo", "ruteo"],
            "Telemetría": ["telemetría", "telemetria"],
        },
    },
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_checkpoint():
    if os.path.exists(CHECKPOINT):
        with open(CHECKPOINT, encoding="utf-8") as f:
            return json.load(f)
    return {"last_processed_row": -1}


def save_checkpoint(last_row):
    with open(CHECKPOINT, "w", encoding="utf-8") as f:
        json.dump({"last_processed_row": last_row}, f)


def fetch_text(url):
    """Descarga la página y devuelve su texto en minúsculas."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        return soup.get_text(separator=" ").lower()
    except Exception:
        return ""


def classify(text, titulo=""):
    """Devuelve (solucion, servicio) con la mejor coincidencia del catálogo."""
    combined = (titulo + " " + text).lower()

    best_sol   = ""
    best_svc   = ""
    best_score = 0

    for solucion, data in CATALOGO.items():
        score = sum(1 for kw in data["keywords"] if kw in combined)
        if score > best_score:
            best_score = score
            best_sol   = solucion
            best_svc   = ""
            top_svc    = 0
            for svc_name, svc_kws in data["servicios"].items():
                s = sum(1 for kw in svc_kws if kw in combined)
                if s > top_svc:
                    top_svc  = s
                    best_svc = svc_name

    if best_score == 0:
        return "", ""
    return best_sol, best_svc


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  CLASIFICADOR DE NOTAS — SOLUCIÓN Y SERVICIO")
    print("=" * 60)
    sys.stdout.flush()

    # Limpiar stop signal previo
    if os.path.exists(STOP_FILE):
        os.remove(STOP_FILE)

    # Leer Excel
    df = pd.read_excel(EXCEL_IN)
    total = len(df)
    print(f"TOTAL:{total}")
    print(f"Total de notas: {total}")
    sys.stdout.flush()

    # Asegurar columnas destino
    if "solución" not in df.columns:
        df["solución"] = ""
    if "servicio" not in df.columns:
        df["servicio"] = ""

    # Detectar columna URL
    url_col = None
    for col in df.columns:
        sample = df[col].dropna().astype(str)
        if sample.str.contains("telcel.com", case=False).any():
            url_col = col
            break
    if url_col is None:
        print("❌ No se encontró columna de URL.")
        sys.exit(1)

    # Detectar columna Título
    titulo_col = None
    for col in df.columns:
        if col.lower() in ("título", "titulo", "title"):
            titulo_col = col
            break

    # Checkpoint
    ckpt      = load_checkpoint()
    start_row = ckpt["last_processed_row"] + 1

    if start_row > 0:
        print(f"⏩ Reanudando desde fila {start_row + 1} de {total}")
    else:
        print("🚀 Iniciando desde la primera fila")
    print("")
    sys.stdout.flush()

    clasificadas = 0
    sin_match    = 0

    for i in range(start_row, total):
        # Stop signal
        if os.path.exists(STOP_FILE):
            print("")
            print(f"⚠️  Proceso detenido en fila {i + 1}. Checkpoint guardado.")
            sys.stdout.flush()
            break

        row     = df.iloc[i]
        url     = str(row[url_col]) if pd.notna(row[url_col]) else ""
        titulo  = str(row[titulo_col]) if titulo_col and pd.notna(row[titulo_col]) else ""

        if not url or url == "nan":
            df.at[df.index[i], "solución"] = ""
            df.at[df.index[i], "servicio"] = ""
            df.to_excel(EXCEL_IN, index=False)
            save_checkpoint(i)
            print(f"PROGRESS:{i+1}/{total}")
            print(f"⏳ [{i+1}/{total}] — Sin URL, omitida")
            sys.stdout.flush()
            continue

        if not url.startswith("http"):
            url = "https://" + url

        page_text = fetch_text(url)
        solucion, servicio = classify(page_text, titulo)

        df.at[df.index[i], "solución"] = solucion
        df.at[df.index[i], "servicio"] = servicio

        # Guardar Excel y checkpoint tras cada fila
        df.to_excel(EXCEL_IN, index=False)
        save_checkpoint(i)

        if solucion:
            clasificadas += 1
            icon = "✅"
        else:
            sin_match += 1
            icon = "—"

        pct        = round(((i + 1) / total) * 100)
        slug       = url.rstrip("/").split("/")[-1][:45]
        svc_short  = servicio[:28] if servicio else "sin clasificar"

        print(f"PROGRESS:{i+1}/{total}")
        print(f"⏳ [{i+1}/{total}] {icon} {slug}")
        print(f"   → {solucion or 'sin match'} / {svc_short}")
        sys.stdout.flush()

    print("")
    print(f"📊 Clasificadas: {clasificadas}  |  Sin match: {sin_match}")
    print(f"💾 Archivo actualizado: {EXCEL_IN}")
    print("✅ PROCESO COMPLETADO")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
