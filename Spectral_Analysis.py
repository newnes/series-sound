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

# === CONFIGURATION ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Audio parameters
SR = 44100  # Sampling rate (CD quality)
NOTE_DURATION = 0.15  # Duration of each tone in seconds
MIDI_RANGE = (21, 108)  # Standard piano notes (A0 to C8)

# Optimized harmonic proportions
HARMONIC_PROPS = [
    1.0,      # Unison
    5 / 4,    # Just major third
    3 / 2,    # Just fifth
    9 / 8,    # Major second
    4 / 3,    # Just fourth
    8 / 5     # Minor sixth
]


# === AUXILIARY FUNCTIONS ===
def enhanced_spectral_analysis(series: np.ndarray) -> float:
    """Advanced spectral analysis with robust fundamental frequency detection."""
    n = len(series)

    # Apply Hann window to reduce spectral leakage
    window = np.hanning(n)
    fft_vals = fft(series * window)

    frequencies = fftfreq(n, d=1)[:n // 2]
    spectrum = np.abs(fft_vals[:n // 2]) ** 2  # Spectral power

    # Peak detection with noise suppression
    threshold = 0.15 * np.max(spectrum)
    peaks = np.where(spectrum > threshold)[0]

    if len(peaks) == 0:
        logger.warning("No significant peaks detected. Using default 440 Hz")
        return 440.0

    # Take the lowest frequency among significant peaks
    fundamental_freq = frequencies[peaks[np.argmin(frequencies[peaks])]]

    # Ensure audible range and minimum value
    return np.clip(abs(fundamental_freq), 80, 2000)


def normalize_changes(pct_series: pd.Series) -> np.ndarray:
    """Advanced normalization with smoothing and controlled scaling."""
    # Smoothing with Gaussian moving average
    smoothed = pct_series.rolling(
        window=5,
        min_periods=1,
        center=True,
        win_type='gaussian'
    ).mean(std=1.5).fillna(0)

    # Asymmetric scaling for higher sensitivity to increases
    scaled = np.clip(smoothed, -0.08, 0.12)
    return (scaled + 0.08) / 0.2  # Normalize to [0, 1]


# === MAIN PROGRAM ===
def main(date: str):
    try:
        os.makedirs("MUSIC", exist_ok=True)

        logger.info(f"Starting processing for {date}")

        # ===== DATA LOADING AND PREPARATION =====
        file_path = os.path.join("X_synthetic", f"{date}.parquet")
        df = pd.read_parquet(file_path)[['value']].reset_index(drop=True)

        if df['value'].isnull().all():
            raise ValueError("Empty or invalid time series")

        # ===== PERCENTAGE CHANGE PROCESSING =====
        df['pct_change'] = df['value'].pipe(lambda x: x.replace([np.inf, -np.inf], np.nan)) \
            .pct_change() \
            .fillna(0)

        # ===== ENHANCED SPECTRAL ANALYSIS =====
        fundamental_freq = enhanced_spectral_analysis(df['value'].values.astype(np.float64))
        logger.info(f"Detected fundamental frequency: {fundamental_freq:.2f} Hz")

        # ===== MUSICAL FREQUENCY GENERATION =====
        normalized = normalize_changes(df['pct_change'])

        # Vectorized frequency calculation
        indices = np.arange(len(df))
        props = np.array([HARMONIC_PROPS[i % len(HARMONIC_PROPS)] for i in indices])
        hz_values = fundamental_freq * props * (0.6 + 0.4 * normalized)  # Controlled dynamic range
        hz_values = np.clip(hz_values, 20, 5000).round(2)

        # ===== CONVERSION TO MUSICAL NOTES =====
        notes = []
        for hz in tqdm(hz_values, desc="Generating notes"):
            try:
                midi = lr.hz_to_midi(hz)
                midi_clip = np.clip(midi, *MIDI_RANGE)
                notes.append(lr.midi_to_note(int(midi_clip)))
            except Exception as e:
                logger.error(f"Error in MIDI conversion for {hz} Hz: {e}")
                notes.append("A4")

        # ===== SAVE RESULTS =====
        df_output = pd.DataFrame({
            'time': df.index,
            'pct_change': df['pct_change'],
            'frequency_hz': hz_values,
            'note': notes
        })

        df_output.to_csv(f"MUSIC/output_{date}.csv", index=False)
        logger.info(f"CSV file saved: output_{date}.csv")

        # ===== ENHANCED AUDIO GENERATION =====
        audio = []
        for hz in tqdm(hz_values, desc="Generating audio"):
            if hz < 20:
                continue  # Ignore inaudible frequencies
            try:
                tone = lr.tone(frequency=hz, sr=SR, duration=NOTE_DURATION)
                audio.append(tone)
            except Exception as e:
                logger.error(f"Error generating tone for {hz} Hz: {e}")

        audio_full = np.concatenate(audio)
        sf.write(f'MUSIC/audio_{date}.wav', audio_full, SR)
        logger.info(f"Audio generated: audio_{date}.wav")

    except Exception as e:
        logger.error(f"Error processing {date}: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        # Get list of .parquet files in the X_synthetic folder
        folder = "X_synthetic"
        pattern = os.path.join(folder, "*.parquet")
        files = glob.glob(pattern)

        if not files:
            logger.error("No .parquet files found in X_synthetic folder")
            sys.exit(1)

        # Extract dates from filenames
        available_dates = []
        for file in files:
            filename = os.path.basename(file)  # e.g., "2022-05-12.parquet"
            date_str = filename.replace(".parquet", "")
            try:
                date = pd.to_datetime(date_str).date()
                available_dates.append(date)
            except Exception as e:
                logger.warning(f"Invalid filename format for date: {filename} - {e}")

        # Sort and remove duplicates
        available_dates = sorted(set(available_dates))

        # Display numbered dates
        print("\n📅 Available dates:")
        for i, d in enumerate(available_dates):
            print(f"  {i+1}. {d}")

        # Ask user to choose
        while True:
            try:
                choice = input("\n👉 Enter the number of the date you want to analyze (or 'q' to quit): ").strip()
                if choice.lower() == 'q':
                    print("👋 Exiting...")
                    sys.exit(0)
                idx = int(choice) - 1
                if 0 <= idx < len(available_dates):
                    selected_date = str(available_dates[idx])
                    break
                else:
                    print(f"❌ Number out of range. Must be between 1 and {len(available_dates)}.")
            except ValueError:
                print("❌ Please enter a valid number.")

        print(f"\n🎯 Processing date: {selected_date}")
        main(selected_date)

    except Exception as e:
        logger.critical(f"Critical error: {str(e)}", exc_info=True)
        sys.exit(1)
