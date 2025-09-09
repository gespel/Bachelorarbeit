import os
import numpy as np

def process_data_files_with_stddev(directory):
    """
    Liest alle .txt-Dateien, extrahiert die Messgröße und berechnet
    die Standardabweichung und den Variationskoeffizienten des Inhalts.
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
                    
                    # Berechne die Standardabweichung und Mittelwert mit numpy
                    std_dev = np.std(numbers)
                    mean = np.mean(numbers)
                    # Variationskoeffizient (in %)
                    if mean != 0:
                        coeff_var = (std_dev / mean) * 100
                    else:
                        coeff_var = float('nan')

                    # Speichere Ergebnis
                    results.append((filename, measure, std_dev, coeff_var))

                except Exception as e:
                    results.append((filename, "FEHLER", str(e), ""))

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
    print(f"{'Datei':<30} {'Messgröße':<15} {'StdAbw':>12} {'VarKoeff (%)':>15}")
    print("=" * 80)
    for filename, measure, std_dev, coeff_var in results:
        if measure == "FEHLER":
            print(f"{filename:<30} {measure:<15} {std_dev:>12} {coeff_var:>15}")
        else:
            print(f"{filename:<30} {measure:<15} {std_dev:>12.6f} {coeff_var:>15.2f}")

# Beispiel-Aufruf
data_folder = '../measurements/paper/pps'
process_data_files_with_stddev(data_folder)
