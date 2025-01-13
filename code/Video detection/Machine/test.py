import cv2
import requests
import json
# import RPi.GPIO as GPIO
# import time

# # Konfiguracja GPIO dla serwomechanizmu
# SERVO_PIN = 17  # Pin GPIO, do którego podłączono sygnał serwa
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(SERVO_PIN, GPIO.OUT)

# # Inicjalizacja PWM dla serwomechanizmu (częstotliwość 50 Hz)
# servo = GPIO.PWM(SERVO_PIN, 50)
# servo.start(7.5)  # Ustawienie serwa w pozycji środkowej (7.5% wypełnienia)

# Wczytanie poświadczeń z pliku JSON
credential = json.load(open(r'C:\INNE\STUDIA\INZYNIERKA\MyPyCode\code\Machine\json_key.json'))
KEY = credential['KEY']
ENDPOINT = credential['ENDPOINT']

# Adres URL do API Face
face_api_url = f"{ENDPOINT}/face/v1.0/detect"
headers = {'Content-Type': 'application/octet-stream', 'Ocp-Apim-Subscription-Key': KEY}
params = {
    'returnFaceId': 'true',
    'returnFaceRectangle': 'true',
    'detectionModel': 'detection_03'   
}

# Użycie kamery do przechwycenia obrazu
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    # Czytanie ramki z kamery
    ret, frame = cap.read()

    if not ret:
        print("Nie udało się uzyskać obrazu z kamery.")
        break

    # Przekształcenie obrazu do formatu .jpg
    _, img_encoded = cv2.imencode('.jpg', frame)
    image_data = img_encoded.tobytes()

    # Wysyłanie obrazu do Azure Face API
    try:
        response = requests.post(face_api_url, params=params, headers=headers, data=image_data)
        response.raise_for_status()
        faces = response.json()
    except Exception as e:
        print(f"Błąd podczas przetwarzania obrazu: {e}")
        break

    # Rysowanie prostokąta wokół wykrytych twarzy
    for face in faces:
        face_rect = face['faceRectangle']
        left = face_rect['left']
        top = face_rect['top']
        width = face_rect['width']
        height = face_rect['height']

        # Obliczanie środka prostokąta
        center_x = left + width // 2
        center_y = top + height // 2

        # Rysowanie prostokąta na wykrytej twarzy
        cv2.rectangle(frame, (left, top), (left + width, top + height), (0, 255, 0), 2)

        # Wyświetlanie koordynatów środka na obrazie
        lewa = 0
        prawa = 0
        
        screen_height, screen_width = frame.shape[:2]
        if center_y < screen_height // 4:
            vertical_position = "Gorna"
        elif center_x > screen_height * 3/4:
            vertical_position = "Dolna"

        if center_x < screen_width // 4:
            horizontal_position = "Lewa"
            lewa = lewa+1
            prawa = 0
        elif center_x > screen_width* 3/4:
            horizontal_position = "Prawa"
            prawa = prawa+1
            lewa = 0 

        # if lewa > 2:
        #     while pos < 181: # ruch 0 -> 180 stopni
        #         SERVO_PIN.write(pos) #ustawienie pozycji
        #         sleep(1) # opóźnienie wykonania następnego ruchu
        #         pos = pos +1
        # elif prawa > 2:
        #     while pos > 0:
        #         SERVO_PIN.write(pos) #ustawienie pozycji
        #         sleep(1) # opóźnienie wykonania następnego ruchu
        #         pos = pos - 1

        #print(f"{top} {left + width} {top + height} {left} {vertical_position} {horizontal_position}")

    # Wyświetlanie obrazu z wykrytymi twarzami
    cv2.imshow('Wykrywanie twarzy Azure', frame)

    # Zatrzymanie działania po naciśnięciu klawisza "ESC"
    if cv2.waitKey(1) & 0xFF == 27:
        print("Zamykanie programu.")
        break

# Zamknięcie okna i zwolnienie zasobów kamery
cap.release()
cv2.destroyAllWindows()