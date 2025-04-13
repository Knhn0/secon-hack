import cv2
import numpy as np
from ultralytics import YOLO
from fastapi import FastAPI, UploadFile, File
import easyocr

yolo = YOLO("../ai_model/best.pt")

reader = easyocr.Reader(['en'], gpu=False, recog_network="english_g2", user_network_directory="../ai-model")


class AIService:

    def detect_and_crop(self, image: np.ndarray, yolo_model: YOLO, conf_threshold: float = 0.5) -> np.ndarray:
        """
        Запускает YOLO для поиска объекта на изображении.
        Если найден один бокс с уверенностью >= conf_threshold, возвращает обрезанную область.
        Если ни один объект не найден, возвращает None.
        """
        results = yolo_model.predict(image)
        boxes = results[0].boxes.xyxy.detach().cpu().numpy()
        confidences = results[0].boxes.conf.detach().cpu().numpy()
        for box, conf in zip(boxes, confidences):
            if conf >= conf_threshold:
                x1, y1, x2, y2 = box.astype(int)
                h, w = image.shape[:2]
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                return image[y1:y2, x1:x2]
        return None  # Ничего не найдено

    def process_image_easyocr(self, img: np.ndarray) -> str:
        """
        Функция, которая пытается распознать текст на изображении в два этапа:
          1. Пробует OCR на исходном grayscale-изображении.
          2. Если результат недостаточный (короткая строка), выполняет легкую предобработку:
             - Увеличение изображения в 2 раза,
             - Применение CLAHE для улучшения контраста,
             - Адаптивная бинаризация (параметры оставлены стандартными),
             - Небольшое сглаживание с помощью GaussianBlur.
        Итогово возвращается тот вариант, результат которого длиннее.
        """
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        raw_results = reader.readtext(gray, detail=0, allowlist="0123456789")
        raw_text = " ".join(raw_results).strip()
        print(f"[DEBUG] Raw OCR: '{raw_text}'")

        scale_factor = 2
        scaled = cv2.resize(gray, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        equalized = clahe.apply(scaled)

        binarized = cv2.adaptiveThreshold(equalized, 255,
                                          cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 11, 2)

        lightly_processed = cv2.GaussianBlur(binarized, (3, 3), 0)

        processed_results = reader.readtext(lightly_processed, detail=0, allowlist="0123456789")
        processed_text = " ".join(processed_results).strip()
        print(f"[DEBUG] Processed OCR: '{processed_text}'")

        if len(processed_text) > len(raw_text):
            return processed_text
        else:
            return raw_text

    def best_rotation_for_easyocr(self, img: np.ndarray, yolo_model: YOLO, conf_threshold: float = 0.5) -> (
    str, np.ndarray):
        """
        Для изображения пробует несколько вариантов:
          1. Сначала выполняется детекция и обрезка через detect_and_crop.
          2. Если YOLO не нашёл объект, возвращается ("Номер не найден", исходное изображение).
          3. Если обрезанная область получена, для вариантов поворота (0°, 90°, 270°) выполняется OCR.
          4. Выбирается вариант с максимальной длиной распознанного текста.
        Возвращает кортеж: (распознанный текст, обработанное изображение).
        """
        cropped = self.detect_and_crop(img, yolo_model, conf_threshold)
        if cropped is None:
            print("[DEBUG] Объект не найден")
            return "Номер не найден", img
        h, w = cropped.shape[:2]
        candidates = []
        processed_imgs = {}

        if w < h:
            for angle in [0, 90, 270]:
                if angle == 0:
                    rotated = cropped
                elif angle == 90:
                    rotated = cv2.rotate(cropped, cv2.ROTATE_90_CLOCKWISE)
                elif angle == 270:
                    rotated = cv2.rotate(cropped, cv2.ROTATE_90_COUNTERCLOCKWISE)
                recognized = self.process_image_easyocr(rotated)
                candidates.append((angle, recognized))
                processed_imgs[angle] = rotated
                print(f"[DEBUG] Угол: {angle}°, OCR: '{recognized}'")
        else:
            recognized = self.process_image_easyocr(cropped)
            candidates.append((0, recognized))
            processed_imgs[0] = cropped
            print(f"[DEBUG] Вертикальное изображение, OCR: '{recognized}'")

        best_angle, best_text = max(candidates, key=lambda item: len(item[1]))
        print(f"[DEBUG] Выбрана ориентация: {best_angle}°, OCR результат: '{best_text}'")
        return best_text, processed_imgs[best_angle]

    async def handle_file(self, file: UploadFile = File(...), conf_threshold: float = 0.5):
        """
        Эндпоинт принимает файл, преобразует его в numpy-массив,
        затем вызывает best_rotation_for_easyocr для детекции/обрезки и OCR.
        Если YOLO не обнаруживает номер, возвращает JSON с информацией об ошибке.
        Иначе возвращает обрезанное изображение (без аннотации) в виде JPEG.
        """
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        recognized_text, processed_img = self.best_rotation_for_easyocr(image, yolo, conf_threshold)

        return recognized_text
