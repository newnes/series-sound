import numpy as np
import pandas as pd
import librosa as lr
import soundfile as sf


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
        logger.info(f"Iniciando procesamiento para {fecha}")

        # ===== CARGA Y PREPARACIÓN DE DATOS =====
        ruta_archivo = f'D:\\Features_Series\\X_syntetic\\{fecha}.parquet'
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
        # Cargar fechas disponibles
        all_weeks = pd.read_csv("XAUUSD.csv", parse_dates=["date"])
        fechas_disponibles = all_weeks["date"].dt.date.unique()

        print("Fechas disponibles:")
        print(", ".join(str(f) for f in fechas_disponibles))

        # Seleccionar fecha (ejemplo)
        fecha_ejemplo = "2022-05-12"
        main(fecha_ejemplo)

    except Exception as e:
        logger.critical(f"Error crítico: {str(e)}", exc_info=True)