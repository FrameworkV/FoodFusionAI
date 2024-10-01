import cv2
import pytesseract as tesser
import re


img_cv = cv2.imread('kassenbon.jpg')
img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)

cv2.imshow("Kassenbon", img_rgb)

roi = cv2.selectROI("Kassenbon", img_rgb, fromCenter=False, showCrosshair=True)

x, y, w, h = roi
cropped_img = img_rgb[int(y):int(y+h), int(x):int(x+w)]

#cv2.imshow("Cropped Image", cropped_img)
#cv2.waitKey(0)
cv2.destroyAllWindows()


# Bild in Graustufen umwandeln
cropped_img_rgb_gray = cv2.cvtColor(cropped_img, cv2.COLOR_RGB2GRAY)
# Bild glätten (Rauschreduktion)
cropped_img_rgb_gray_smooth = cv2.GaussianBlur(cropped_img_rgb_gray, (5, 5), 0)

# Schwellenwert setzen (threshold), um Text hervorzuheben
#_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

# Texterkennung mit Tesseract
custom_config = r'--oem 3 --psm 6'
text = tesser.image_to_string(cropped_img_rgb_gray_smooth, config=custom_config)


print("Rohtext:\n", text)

artikel = re.findall(r'([A-Za-z]+)', text)

print("Artikel:", artikel)