import cv2
from simple_facerec import SimpleFacerec
import os

# Funkcja do przetwarzania nazw plików
def get_name_before_underscore(name):
    if name.startswith("Unknown"):
        return name  # Zwraca pełną nazwę pliku dla Unknown
    return name.split("_")[0]  # Zwraca nazwę do pierwszego znaku "_"

# Ustawienie poprawnej ścieżki do folderu
encoding_folder = r"c:\INNE\STUDIA\INZYNIERKA\MyPyCode\code\images"

# Mapowanie oryginalnych nazw na obcięte nazwy
processed_names = {}
for file in os.listdir(encoding_folder):
    if file.endswith(('.jpg', '.jpeg', '.png')):  # Obsługuje obrazy
        original_name = os.path.splitext(file)[0]  # Nazwa pliku bez rozszerzenia
        
        # Sprawdzenie, czy nazwa zaczyna się od "Unknown"
        if original_name.startswith("Unknown"):
            processed_name = original_name  # Zachowaj pełną nazwę (w tym numer)
        else:
            processed_name = get_name_before_underscore(original_name)  # Obcięcie do pierwszego "_"
        
        processed_names[original_name] = processed_name

# Inicjalizacja SimpleFacerec
sfr = SimpleFacerec()
sfr.load_encoding_images(encoding_folder)

# Załaduj obraz z kamery
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

img_counter = 0
saved_images = []  # Lista do przechowywania ścieżek do zdjęć

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        print("Nie udało się odczytać klatki z kamery.")
        continue

    # Wykrywanie twarzy
    face_locations, face_names = sfr.detect_known_faces(frame)
    for face_loc, name in zip(face_locations, face_names):
        y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

        # Dopasowanie nazwy do obciętej wersji
        processed_name = processed_names.get(name, "Unknown")
        # Oblicz środek twarzy
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        # Sprawdź położenie na ekranie
        screen_height, screen_width = frame.shape[:2]
        vertical_position = "Gorna" if center_y < screen_height // 2 else "Dolna"
        horizontal_position = "Lewa" if center_x < screen_width // 2 else "Prawa"

        print(x1, x2, y1, y2, vertical_position, horizontal_position)

        # Zapis obrazu dla "Unknown"
        if name == "Unknown":
            img_name = os.path.join(encoding_folder, f"Unknown_{img_counter}.jpg")
            cropped_face = frame[y1:y2, x1:x2]
            cv2.imwrite(img_name, cropped_face)
            saved_images.append(img_name)  # Zapisz ścieżkę zdjęcia
            print("Screenshot taken")
            img_counter += 1
            sfr.load_encoding_images(encoding_folder)  # Przeładuj zakodowane obrazy
        
        # Wyświetl informacje na ekranie
        cv2.putText(frame, name.split("_")[0], (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)

    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1)
    if key == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()

# Obsługa zmiany nazw zdjęć Unknown
for filename in os.listdir(encoding_folder):
    if filename.startswith("Unknown"):
        img_path = os.path.join(encoding_folder, filename)
        image = cv2.imread(img_path)
        cv2.imshow(f"Zdjecie: {filename}", image)
        cv2.waitKey(0)  # Czeka na naciśnięcie klawisza przed zamknięciem okna
        new_name = input(f"Podaj nową nazwe dla {filename} (bez rozszerzenia): ")
        new_path = os.path.join(encoding_folder, new_name + ".jpg")
        os.rename(img_path, new_path)
        print(f"Zdjecie zostalo zapisane jako {new_path}")

print("Wszystkie zdjecia zostaly przetworzone.")
cv2.destroyAllWindows()
