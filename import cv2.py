import cv2
import os
import numpy as np

def encrypt(img_path, msg, password):
    img = cv2.imread(img_path)
    if img is None:
        print("Error: Image not found!")
        return

    h, w, _ = img.shape
    total_pixels = h * w * 3  # Considering all 3 channels

    if len(msg) > total_pixels:
        print("Message is too long to hide in the image!")
        return

    d = {chr(i): i for i in range(255)}  # ASCII mapping
    msg += "|"  # Delimiter to detect end during decryption

    idx = 0
    for i in range(h):
        for j in range(w):
            for k in range(3):
                if idx < len(msg):
                    img[i, j, k] = d[msg[idx]]  # Store ASCII value
                    idx += 1
                else:
                    break

    cv2.imwrite("encryptedImage.jpg", img)
    print("Encryption complete. Image saved as 'encryptedImage.jpg'.")
    os.system("start encryptedImage.jpg")  # Open image on Windows
    return password  # Storing password for decryption

def decrypt(img_path, stored_password):
    img = cv2.imread(img_path)
    if img is None:
        print("Error: Image not found!")
        return

    h, w, _ = img.shape
    c = {i: chr(i) for i in range(255)}  # Reverse ASCII mapping

    pas = input("Enter passcode for Decryption: ")
    if stored_password != pas:
        print("YOU ARE NOT AUTHORIZED!")
        return

    message = ""
    for i in range(h):
        for j in range(w):
            for k in range(3):
                char = c[img[i, j, k]]
                if char == "|":  # Stop at delimiter
                    print("Decrypted message:", message)
                    return
                message += char

    print("Decryption complete:", message)

# Usage
img_path = "1337253.jpeg"  # Replace with your image path
msg = input("Enter secret message: ")
password = input("Enter a passcode: ")

stored_password = encrypt(img_path, msg, password)
decrypt("encryptedImage.jpg", stored_password)
