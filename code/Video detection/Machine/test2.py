import glob
import time
import cv2  # OpenCV do obsługi kamery
import requests  # Biblioteka do wykonywania zapytań HTTP
import json  # Obsługa formatu JSON
import sys
from azure.cognitiveservices.vision.face import FaceClient  # Klient Face API z biblioteki Azure
from msrest.authentication import CognitiveServicesCredentials

GRUPY = []
OSOBY = []
ID = []

# Wczytanie poświadczeń z pliku JSON
credential = json.load(open(r'C:\INNE\STUDIA\INZYNIERKA\MyPyCode\code\Machine\json_key.json'))
KEY = credential['KEY']
ENDPOINT = credential['ENDPOINT']

# Inicjalizacja klienta Face API
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))


# Funkcja tworzenia grupy osób (jeśli nie istnieje)
def create_person_group(group_id):
    try:
        face_client.person_group.create(person_group_id=group_id, name=group_id)
        print(f"Grupa osób '{group_id}' została utworzona.")
    except Exception as e:
        print(f"Błąd podczas tworzenia grupy: {e}")

# Funkcja sprawdzania, czy grupa istnieje
def check_person_group(group_id):
    try:
        group = face_client.person_group.get(group_id)
        print(f"Grupa '{group_id}' istnieje.")
        return True
    except Exception:
        print(f"Grupa '{group_id}' nie istnieje.")
        return False

# Funkcja dodawania osoby do grupy
def add_person_to_group(group_id, person_name, image_paths):
    person = face_client.person_group_person.create(group_id, person_name)
    print(f"Osoba '{person_name}' dodana z ID: {person.person_id}")

    # Dodanie twarzy osoby na podstawie zdjęć
    for image_path in image_paths:
        with open(image_path, 'rb') as img_stream:
            face_client.person_group_person.add_face_from_stream(group_id, person.person_id, img_stream)
            print(f"Twarz dodana z pliku: {image_path}")

# Funkcja trenowania grupy osób
def train_person_group(group_id):
    face_client.person_group.train(group_id)
    print("Trwa trening grupy...")

    # Sprawdzanie statusu treningu
    while True:
        status = face_client.person_group.get_training_status(group_id)
        print(f"Status treningu: {status.status}")
        if status.status == 'succeeded':
            print("Trening zakończony pomyślnie.")
            break
        elif status.status == 'failed':
            print("Trening nie powiódł się.")
            break

# Funkcja rozpoznawania twarzy z kamery
def identify_faces_from_camera(group_id):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Uruchomienie kamery

    while True:
        ret, frame = cap.read()  # Pobranie obrazu z kamery
        if not ret:
            print("Nie udało się uzyskać obrazu z kamery.")
            break

        _, img_encoded = cv2.imencode('.jpg', frame)  # Kodowanie obrazu do formatu .jpg
        image_data = img_encoded.tobytes()

        # Wysyłanie obrazu do Azure Face API
        try:
            face_api_url = f"{ENDPOINT}/face/v1.0/detect"
            headers = {'Content-Type': 'application/octet-stream', 'Ocp-Apim-Subscription-Key': KEY}
            params = {'returnFaceId': 'true', 'returnFaceRectangle': 'true', 'detectionModel': 'detection_03'}
            response = requests.post(face_api_url, headers=headers, params=params, data=image_data)
            response.raise_for_status()
            faces = response.json()
        except Exception as e:
            print(f"Błąd podczas przetwarzania obrazu: {e}")
            break

        # Pobieranie faceId dla wykrytych twarzy
        face_ids = [face['faceId'] for face in faces]
        if not face_ids:
            print("Brak twarzy do identyfikacji.")
            continue

        # Identyfikacja twarzy
        try:
            results = face_client.face.identify(face_ids, group_id)
            for result in results:
                if result.candidates:
                    person_id = result.candidates[0].person_id
                    person = face_client.person_group_person.get(group_id, person_id)
                    print(f"Rozpoznano osobę: {person.name}")
                else:
                    print("Twarzy nie rozpoznano.")
        except Exception as e:
            print(f"Błąd podczas identyfikacji: {e}")
            break

        # Wyświetlanie prostokątów na wykrytych twarzach
        for face in faces:
            face_rect = face['faceRectangle']
            left, top = face_rect['left'], face_rect['top']
            width, height = face_rect['width'], face_rect['height']
            cv2.rectangle(frame, (left, top), (left + width, top + height), (0, 255, 0), 2)

        # Wyświetlanie obrazu z kamery
        cv2.imshow('Rozpoznawanie twarzy', frame)

        # Zatrzymanie po naciśnięciu klawisza ESC
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

def utworz_grupe(grupa):
    face_client.person_group.create(person_group_id=grupa, name=grupa)
    print('Utworzono grupę {}'.format(grupa))

def utworz_osobe(osoba, grupa):
    globals()[osoba] = face_client.person_group_person.create(grupa, osoba)
    print('ID osoby:', globals()[osoba].person_id)
    ID.append(globals()[osoba].person_id)

    lista_zdjec = [plik for plik in glob.glob('*.jpg') if plik.startswith(osoba)]
    time.sleep(1)
    for obraz in lista_zdjec:
        face_client.person_group_person.add_face_from_stream(
            GRUPY[0], globals()[osoba].person_id, open(obraz, 'r+b'))
        print('Dodano zdjęcie {}'.format(obraz))
        time.sleep(1)

def trenuj(grupa):
    print('Rozpoczynanie treningu grupy {}'.format(grupa))
    face_client.person_group.train(grupa)
    while (True):
        status_treningu = face_client.person_group.get_training_status(grupa)
        print("Status treningu grupy {}: {}.".format(grupa, status_treningu.status))
        if (status_treningu.status == 'succeeded'):
            break
        elif (status_treningu.status == 'failed'):
            face_client.person_group.delete(person_group_id=grupa)
            sys.exit('Trening grupy osób nie powiódł się.')
        time.sleep(5)


# Główna logika z menu
def main_menu():

    while True:
        print("\nWybierz opcję:")
        print("1. Dodaj osoby do grupy")
        print("2. Włącz kamerę i rozpoznawanie twarzy")
        print("3. Wyjdź")
        choice = input("Wybór (1, 2 lub 3): ")
        # Pętla zabezpieczająca przed nieprawidłowym wyborem
        while not choice.isdigit() or int(choice) not in [1, 2, 3]:
            print("Nieprawidłowy wybór! Wprowadź 1, 2 lub 3.")
            choice = input("Wybór (1, 2 lub 3): ")

        if choice == '1':
            # Sprawdzenie, czy grupa istnieje
            
                grupy = face_client.person_group.list()
                # Użycie FaceClient do uzyskania listy osób w grupie
                grupa_id = grupy[0].name  # zastąp nazwą swojej grupy

                # Pobierz listę osób w grupie
                osoby = face_client.person_group_person.list(grupa_id)

                # Sprawdzenie zdjęć dla każdej osoby
                for osoba in osoby:
                # Uzyskanie szczegółowych informacji o osobie
                    szczegoly_osoby = face_client.person_group_person.get(grupa_id, osoba.person_id)
                    if szczegoly_osoby.persisted_face_ids:
                        print(f"Osoba {osoba.name} ma przypisane zdjęcia: {szczegoly_osoby.persisted_face_ids}")
                    else:
                        print(f"Osoba {osoba.name} nie ma przypisanych zdjęć.")

                if not grupy:
                    print("Nie znaleziono zadnych grup.")
                    GRUPY.append(input('Podaj nazwę grupy -> ').lower())
                    list(map(lambda x: utworz_grupe(x), GRUPY))
                else:
                    print("Lista grup:")
                    for group_id in grupy:
                        print(f"Group ID: {group_id.person_group_id}, Name: {group_id.name}")
                        szczegoly_osoby = face_client.person_group_person.get(grupa_id, osoba.person_id)
                        if szczegoly_osoby.persisted_face_ids:
                            print(f"Osoba {osoba.name} ma przypisane zdjęcia: {szczegoly_osoby.persisted_face_ids}")
                        else:
                            print(f"Osoba {osoba.name} nie ma przypisanych zdjęć.")
                        GRUPY.append(grupy[0].name)

                    lista_osob = []
                    nazwa_osoby = None
                    while nazwa_osoby != 'koniec':
                        nazwa_osoby = input("Podaj imię osoby, którą chcesz dodać do grupy '{}', lub wpisz 'koniec', aby zakończyć -> ".format(GRUPY[0])).lower()
                        if nazwa_osoby != 'koniec':
                            OSOBY.append(nazwa_osoby)
                            lista_osob.append(nazwa_osoby)
                    l = 0
                    while l < len(lista_osob):
                        print('{} został dodany do grupy {}'.format(OSOBY[l], GRUPY[0]))
                        l = l + 1
                    list(map(lambda x: utworz_osobe(x, GRUPY[0]), OSOBY))
                    list(map(lambda x: trenuj(x), GRUPY))
            #except Exception as e:
            #    print(f"Wystąpił błąd podczas pobierania grup: {e}")


        elif choice == '2':
            identify_faces_from_camera(group_id)

        elif choice == '3':
            print("Zamykanie programu.")
            break

        else:
            print("Nieprawidłowy wybór. Spróbuj ponownie.")

# Uruchomienie menu
main_menu()
