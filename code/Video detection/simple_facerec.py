import face_recognition
import cv2
import os
import glob
import numpy as np

class SimpleFacerec:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.frame_resizing = 0.25

    def load_encoding_images(self, images_path):
        """
        Ładowanie obrazów i kodowanie twarzy.
        """
        images_path = glob.glob(os.path.join(images_path, "*.*"))

        print(f"Znaleziono {len(images_path)} obrazow.")

        for img_path in images_path:
            img = cv2.imread(img_path)
            if img is None:
                print(f"Nie udało się wczytac obrazu: {img_path}")
                continue

            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            basename = os.path.basename(img_path)
            filename, ext = os.path.splitext(basename)
            img_encoding = face_recognition.face_encodings(rgb_img)
            if img_encoding:
                img_encoding = img_encoding[0]
            else:
                print(f"Brak twarzy w obrazie: {basename}")
                os.remove(img_path)
                continue

            self.known_face_encodings.append(img_encoding)
            self.known_face_names.append(filename)
        print("Zakodowane obrazy zostały załadowane.")

    def detect_known_faces(self, frame):
        """
        Wykrywanie twarzy na podstawie wczytanego kadru.
        """
        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches and best_match_index < len(matches) and matches[best_match_index]:
                name = self.known_face_names[best_match_index]
            face_names.append(name)

        face_locations = np.array(face_locations)
        face_locations = face_locations / self.frame_resizing
        return face_locations.astype(int), face_names
