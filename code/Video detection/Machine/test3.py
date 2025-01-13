import cv2
import requests
import json
import glob
import os
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials

# Wczytanie poświadczeń z pliku JSON
credential = json.load(open(r'C:\INNE\STUDIA\INZYNIERKA\MyPyCode\code\Machine\json_key.json'))
KEY = credential['KEY']
ENDPOINT = credential['ENDPOINT']

# Utworzenie instancji FaceClient
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

# Funkcja do dodawania zdjęć do istniejącej grupy
def dodaj_zdjecia_do_grupy(grupa_id, folder_zdjec):
    # Pobierz listę osób w grupie
    osoby = face_client.person_group_person.list(grupa_id)
    
    # Iteracja przez wszystkie zdjęcia w danym folderze
    for zdjecie in glob.glob(os.path.join(folder_zdjec, '*.jpg')):  # Zakładając, że zdjęcia mają rozszerzenie .jpg
        # Wyciąganie nazwy osoby na podstawie nazwy pliku
        nazwa_osoby = os.path.basename(zdjecie).split('.')[0]  # np. "janek.jpg" -> "janek"
        
        # Sprawdzenie, czy osoba już istnieje w grupie
        osoba = next((o for o in osoby if o.name == nazwa_osoby), None)
        
        if osoba:
            # Dodawanie zdjęcia do istniejącej osoby
            with open(zdjecie, 'r+b') as image:
                face_client.person_group_person.add_face_from_stream(grupa_id, osoba.person_id, image)
            print(f"Zdjęcie {zdjecie} dodane do osoby {nazwa_osoby}.")
        else:
            print(f"Osoba o nazwie {nazwa_osoby} nie istnieje w grupie.")

# Funkcja do sprawdzenia zdjęć w grupie
def sprawdz_zdjecia_w_grupie(grupa_id):
    osoby = face_client.person_group_person.list(grupa_id)
    
    for osoba in osoby:
        szczegoly_osoby = face_client.person_group_person.get(grupa_id, osoba.person_id)
        if szczegoly_osoby.persisted_face_ids:
            print(f"Osoba {osoba.name} ma przypisane zdjęcia: {szczegoly_osoby.persisted_face_ids}")
        else:
            print(f"Osoba {osoba.name} nie ma przypisanych zdjęć.")

# Główna logika
if __name__ == "__main__":
    grupa_id = "nazwa_grupy"  # Zmień na identyfikator swojej grupy
    folder_zdjec = r'C:\INNE\STUDIA\INZYNIERKA\MyPyCode\source code\Machine'  # Zmień na ścieżkę do folderu ze zdjęciami

    # Dodaj zdjęcia do grupy
    dodaj_zdjecia_do_grupy(grupa_id, folder_zdjec)

    # Sprawdź, czy zdjęcia zostały dodane
    sprawdz_zdjecia_w_grupie(grupa_id)
