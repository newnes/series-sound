import numpy as np
import pandas as pd
import librosa as lr
import soundfile as sf
import os
import glob
import sys

from scipy.fft import fft, fftfreq
import logging
from tqdm import tqdm

# === CONFIGURACIÓN ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Parámetros de audio
SR = 44100  # Frecuencia de muestreo (calidad CD)
DURACION_NOTA = 0.15  # Duración de cada tono en segundos
RANGO_MIDI = (21, 108)  # Notas de piano estándar (A0 a C8)

# Proporciones armónicas optimizadas
HARMONIC_PROPS = [
    1.0,  # Unísono
    5 / 4,  # Tercera mayor justa
    3 / 2,  # Quinta justa
    9 / 8,  # Segunda mayor
    4 / 3,  # Cuarta justa
    8 / 5  # Sexta menor
]


# === FUNCIONES AUXILIARES ===
def analisis_espectral_mejorado(serie: np.ndarray) -> float:
    """Análisis espectral avanzado con detección robusta de frecuencia base."""
    n = len(serie)

    # Aplicar ventana de Hann para reducir fugas espectrales
    ventana = np.hanning(n)
    fft_vals = fft(serie * ventana)

    frecuencias = fftfreq(n, d=1)[:n // 2]
    espectro = np.abs(fft_vals[:n // 2]) ** 2  # Potencia espectral

    # Detección de picos con supresión de ruido
    umbral = 0.15 * np.max(espectro)
    picos = np.where(espectro > umbral)[0]

    if len(picos) == 0:
        logger.warning("No se detectaron picos significativos. Usando valor por defecto 440 Hz")
        return 440.0

    # Tomar la frecuencia más baja entre los picos significativos
    frecuencia_base = frecuencias[picos[np.argmin(frecuencias[picos])]]

    # Asegurar rango audible y valor mínimo
    return np.clip(abs(frecuencia_base), 80, 2000)


def normalizar_cambios(pct_series: pd.Series) -> np.ndarray:
    """Normalización avanzada con suavizado y escalado controlado."""
    # Suavizado con media móvil gaussiana
    suavizado = pct_series.rolling(
        window=5,
        min_periods=1,
        center=True,
        win_type='gaussian'
    ).mean(std=1.5).fillna(0)

    # Escalado asimétrico para mayor sensibilidad en subidas
    escalado = np.clip(suavizado, -0.08, 0.12)
    return (escalado + 0.08) / 0.2  # Normalizar a [0, 1]


# === PROGRAMA PRINCIPAL ===
def main(fecha: str):
    try:

        os.makedirs("MUSICA", exist_ok=True)

        logger.info(f"Iniciando procesamiento para {fecha}")

        # ===== CARGA Y PREPARACIÓN DE DATOS =====
        ruta_archivo = os.path.join("X_syntetic", f"{fecha}.parquet")
        df = pd.read_parquet(ruta_archivo)[['value']].reset_index(drop=True)

        if df['value'].isnull().all():
            raise ValueError("Serie temporal vacía o inválida")

        # ===== PROCESAMIENTO DE CAMBIOS PORCENTUALES =====
        df['pct_change'] = df['value'].pipe(lambda x: x.replace([np.inf, -np.inf], np.nan)) \
            .pct_change() \
            .fillna(0)

        # ===== ANÁLISIS ESPECTRAL MEJORADO =====
        frecuencia_base = analisis_espectral_mejorado(df['value'].values.astype(np.float64))
        logger.info(f"Frecuencia base detectada: {frecuencia_base:.2f} Hz")

        # ===== GENERACIÓN DE FRECUENCIAS MUSICALES =====
        normalized = normalizar_cambios(df['pct_change'])

        # Cálculo vectorizado de frecuencias
        indices = np.arange(len(df))
        props = np.array([HARMONIC_PROPS[i % len(HARMONIC_PROPS)] for i in indices])
        hz_values = frecuencia_base * props * (0.6 + 0.4 * normalized)  # Rango dinámico controlado
        hz_values = np.clip(hz_values, 20, 5000).round(2)

        # ===== CONVERSIÓN A NOTAS MUSICALES =====
        notas = []
        for hz in tqdm(hz_values, desc="Generando notas"):
            try:
                midi = lr.hz_to_midi(hz)
                midi_clip = np.clip(midi, *RANGO_MIDI)
                notas.append(lr.midi_to_note(int(midi_clip)))
            except Exception as e:
                logger.error(f"Error en conversión MIDI: {e}")
                notas.append("A4")

        # ===== GUARDADO DE RESULTADOS =====
        df_output = pd.DataFrame({
            'tiempo': df.index,
            'pct_change': df['pct_change'],
            'frecuencia_hz': hz_values,
            'nota': notas
        })

        df_output.to_csv(f"MUSICA/output_{fecha}.csv", index=False)
        logger.info(f"Archivo CSV guardado: output_{fecha}.csv")

        # ===== GENERACIÓN DE AUDIO MEJORADO =====
        audio = []
        for hz in tqdm(hz_values, desc="Generando audio"):
            if hz < 20:
                continue  # Ignorar frecuencias inaudibles
            try:
                tono = lr.tone(frequency=hz, sr=SR, duration=DURACION_NOTA)
                audio.append(tono)
            except Exception as e:
                logger.error(f"Error generando tono {hz} Hz: {e}")

        audio_full = np.concatenate(audio)
        sf.write(f'MUSICA/audio_{fecha}.wav', audio_full, SR)
        logger.info(f"Audio generado: audio_{fecha}.wav")

    except Exception as e:
        logger.error(f"Error procesando {fecha}: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        # Obtener lista de archivos .parquet
        carpeta = "X_syntetic"
        patron = os.path.join(carpeta, "*.parquet")
        archivos = glob.glob(patron)

        if not archivos:
            logger.error("No se encontraron archivos .parquet en la carpeta X_syntetic")
            sys.exit(1)

        # Extraer fechas
        fechas_disponibles = []
        for archivo in archivos:
            nombre = os.path.basename(archivo)
            fecha_str = nombre.replace(".parquet", "")
            try:
                fecha = pd.to_datetime(fecha_str).date()
                fechas_disponibles.append(fecha)
            except Exception as e:
                logger.warning(f"Nombre inválido: {nombre} - {e}")

        fechas_disponibles = sorted(set(fechas_disponibles))

        # Mostrar fechas numeradas
        print("\n📅 Fechas disponibles:")
        for i, f in enumerate(fechas_disponibles):
            print(f"  {i+1}. {f}")

        # Pedir al usuario que elija
        while True:
            try:
                opcion = input("\n👉 Ingresa el número de la fecha que quieres analizar (o 'q' para salir): ").strip()
                if opcion.lower() == 'q':
                    print("👋 Saliendo...")
                    sys.exit(0)
                idx = int(opcion) - 1
                if 0 <= idx < len(fechas_disponibles):
                    fecha_elegida = str(fechas_disponibles[idx])
                    break
                else:
                    print(f"❌ Número fuera de rango. Debe ser entre 1 y {len(fechas_disponibles)}.")
            except ValueError:
                print("❌ Por favor, ingresa un número válido.")

        print(f"\n🎯 Procesando fecha: {fecha_elegida}")
        main(fecha_elegida)

    except Exception as e:
        logger.critical(f"Error crítico: {str(e)}", exc_info=True)
        sys.exit(1)
