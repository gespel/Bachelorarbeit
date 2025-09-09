import os
import numpy as np

def process_data_files_with_stddev(directory):
    """
    Liest alle .txt-Dateien, extrahiert die Messgröße und berechnet
    die Standardabweichung des Inhalts.
    """
    results = []

    for root, _, files in os.walk(directory):
        for filename in files:
            if '_2.txt' in filename:
                try:
                    # Extrahiere die Messgröße mit split()
                    measure = filename.split('b')[0]
                    file_path = os.path.join(root, filename)

                    # Lese die Zahlen aus der Datei
                    numbers = []
                    with open(file_path, 'r') as file:
                        for line in file:
                            if line.strip():  # Nur nicht-leere Zeilen
                                numbers.append(float(line.strip()))
                    
                    # Berechne die Standardabweichung mit numpy
                    std_dev = np.std(numbers)

                    # Speichere Ergebnis
                    results.append((filename, measure, std_dev))

                except Exception as e:
                    results.append((filename, "FEHLER", str(e)))

    # Versuch: Messgröße in Zahl umwandeln, sonst String verwenden
    def sort_key(item):
        measure = item[1]
        try:
            return float(measure)
        except ValueError:
            return measure  # Fallback: Stringsortierung

    results.sort(key=sort_key)

    # Ausgabe als Tabelle
    print("\n📊 Ergebnisübersicht (sortiert nach Messgröße)\n")
    print(f"{'Datei':<30} {'Messgröße':<15} {'Standardabweichung':>20}")
    print("=" * 70)
    for filename, measure, std_dev in results:
        if measure == "FEHLER":
            print(f"{filename:<30} {measure:<15} {std_dev:>20}")
        else:
            print(f"{filename:<30} {measure:<15} {std_dev:>20.6f}")

# Beispiel-Aufruf
data_folder = '../measurements/paper/pps'
process_data_files_with_stddev(data_folder)
