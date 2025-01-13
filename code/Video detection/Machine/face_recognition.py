import cv2
import requests
import time
import json
import glob
import sys
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials

# Wczytanie poświadczeń z pliku JSON
credential = json.load(open(r'C:\INNE\STUDIA\INZYNIERKA\MyPyCode\code\Machine\json_key.json'))
KEY = credential['KEY']
if KEY is None:
    print("KEY nie został znaleziony w pliku JSON.")
ENDPOINT = credential['ENDPOINT']

# Adres URL do API Face
face_api_url = f"{ENDPOINT}/face/v1.0/detect"
naglowki = {'Content-Type': 'application/octet-stream', 'Ocp-Apim-Subscription-Key': KEY}
parametry = {'detectionModel': 'detection_03', 'returnFaceId': 'true', 'returnFaceRectangle': 'true'}

GRUPY = []
OSOBY = []
ID = []

face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

def lista_grup():
    try:
        grupy = face_client.person_group.list()
        if not grupy:
            print("Nie znaleziono zadnych grup.")
        else:
            print("Lista grup:")
            for grupa in grupy:
                print(f"Group ID: {grupa.person_group_id}, Name: {grupa.name}")
    except Exception as e:
        print(f"Wystąpił błąd podczas pobierania grup: {e}")

def usun_grup():
    try:
        grupy = face_client.person_group.list()
        if not grupy:
            print("Nie znaleziono zadnych grup.")
        else:
            print("Lista grup do usuniecia:")
            for grupa in grupy:
                print(f"Group ID: {grupa.person_group_id}, Name: {grupa.name}")
                # Usuwanie grupy
                face_client.person_group.delete(person_group_id=grupa.person_group_id)
                print(f"Grupa {grupa.name} zostala usunieta.")
    except Exception as e:
        print(f"Wystąpił błąd podczas pobierania grup: {e}")

lista_grup()
usun_grup()

# Funkcje
def utworz_grupe(grupa):
    face_client.person_group.create(person_group_id=grupa, name=grupa)
    print('Utworzono grupę {}'.format(grupa))

face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

def utworz_osobe(osoba, grupa):
    globals()[osoba] = face_client.person_group_person.create(grupa, osoba)
    print('ID dla {}:', osoba, globals()[osoba].person_id)
    ID.append(globals()[osoba].person_id)

    lista_zdjec = [plik for plik in glob.glob('*.jpg') if plik.startswith(osoba)]
    time.sleep(1)
    for obraz in lista_zdjec:
        face_client.person_group_person.add_face_from_stream(
            GRUPY[0], globals()[osoba].person_id, open(obraz, 'r+b'))
        print('Dodano zdjecie {}'.format(obraz))
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

def rozpocznij():
    GRUPY.append(input('Podaj nazwę grupy -> ').lower())
    list(map(lambda x: utworz_grupe(x), GRUPY))

    lista_osob = []
    nazwa_osoby = None
    while nazwa_osoby != 'koniec':
        nazwa_osoby = input("Podaj imię osoby, którą chcesz dodać do grupy '{}', lub wpisz 'koniec', aby zakończyć -> ".format(GRUPY[0])).lower()
        if nazwa_osoby != 'koniec':
            OSOBY.append(nazwa_osoby)
            lista_osob.append(nazwa_osoby)

    if len(lista_osob) == 1:
        print('{} został dodany do grupy {}'.format(OSOBY[0], GRUPY[0]))
    else:
        ostatnie_imie = lista_osob.pop()
        imiona = ', '.join(lista_osob)
        print('{} i {} zostali dodani do grupy {}'.format(imiona, ostatnie_imie, GRUPY[0]))

    list(map(lambda x: utworz_osobe(x, GRUPY[0]), OSOBY))
    list(map(lambda x: trenuj(x), GRUPY))

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while True:
        global wyniki
        ret, frame = cap.read()
        obraz = cv2.imencode('.jpg', frame)[1].tobytes()

        odpowiedz = requests.post(face_api_url, params=parametry, headers=naglowki, data=obraz)
        odpowiedz.raise_for_status()
        twarze = odpowiedz.json()
        face_ids = [face['faceId'] for face in twarze]

        if not face_ids:
            print("Brak wykrytych twarzy do identyfikacji.")
        else:
            try:
                wyniki = face_client.face.identify(face_ids, person_group_id=GRUPY[0])
            except Exception as e:
                print(f"Wystąpił błąd przy identyfikacji: {e}")


        # Otrzymywanie informacji o twarzach
        for n, (face, osoba, id, imie) in enumerate(zip(twarze, wyniki, ID, OSOBY)):
            prostokat = face['faceRectangle']
            lewy, gorny = prostokat['left'], prostokat['top']
            prawy = int(prostokat['width'] + lewy)
            dolny = int(prostokat['height'] + gorny)

            rysuj_prostokat = cv2.rectangle(frame, (lewy, gorny), (prawy, dolny), (0, 255, 0), 3)
            atrybuty = face['faceAttributes']
            wiek = atrybuty['age']

            if len(osoba.candidates) > 0 and str(osoba.candidates[0].person_id) == str(id):
                print('Osoba o face ID {} została rozpoznana w {}.{}'.format(osoba.face_id, 'ramce', osoba.candidates[0].person_id))
                rysuj_tekst = cv2.putText(frame, 'Imię: {}'.format(imie), (lewy, dolny + 50), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                twarze[n]['imie'] = str(imie)
            else:
                rysuj_tekst = cv2.putText(frame, 'Imię: Nieznane', (lewy, dolny + 50), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                twarze[n]['imie'] = 'Nieznane'

        cv2.imshow('rysuj_prostokat', rysuj_prostokat)

        klawisz = cv2.waitKey(1) & 0xFF
        if klawisz == 27:
            print("Escape wciśnięty, zamykam...")
            break

def zakoncz(nazwa_grupy):
    cv2.destroyAllWindows()
    face_client.person_group.delete(person_group_id=nazwa_grupy)

# Rozpocznij działanie kodu
rozpocznij()
# Zakończ i wyczyść
zakoncz('nazwa_grupy')
