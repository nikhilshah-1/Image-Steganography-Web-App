import streamlit as st
import cv2
import numpy as np
import os
from io import BytesIO
from PIL import Image
import base64

# ✅ Set Streamlit page configuration
st.set_page_config(page_title="🔒 Image Steganography", layout="centered")

# ✅ Apply single background color with centered layout
st.markdown(
    """
    <style>
    .stApp {
        background-color: #1e1e1e !important;
        color: white;
    }
    .stButton > button, .stTextInput > div > div > input, .stFileUploader > div {
        background-color: #333;
        color: white;
        border: 1px solid white;
        border-radius: 8px;
        padding: 10px;
    }
    .stButton > button:hover {
        background-color: #444;
        transform: scale(1.05);
    }
    .stTitle, .stSubheader, .stRadio, .stTextInput, .stFileUploader, .stButton {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ✅ Improved XOR Encryption using Base64 Encoding
def xor_encrypt_decrypt(message, key):
    encrypted_chars = [chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(message)]
    encrypted_text = ''.join(encrypted_chars)
    return base64.b64encode(encrypted_text.encode()).decode()  # Convert to base64

# ✅ Decryption with Base64 Decoding
def xor_decrypt(encrypted_message, key):
    try:
        encrypted_message = base64.b64decode(encrypted_message.encode()).decode()  # Decode base64
        decrypted_chars = [chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(encrypted_message)]
        return ''.join(decrypted_chars).strip()  # Remove extra spaces/newlines
    except Exception as e:
        return "❌ Decryption Failed: Invalid Password or Corrupted Image"

# ✅ Convert message to binary
def message_to_binary(message):
    return ''.join(format(ord(char), '08b') for char in message)

# ✅ Convert binary to message
def binary_to_message(binary):
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join(chr(int(char, 2)) for char in chars)

# ✅ Encrypt message into image
def encrypt(image, message, password):
    img = np.array(image)
    encrypted_msg = xor_encrypt_decrypt(message.strip(), password)  # Encrypt with password
    encrypted_msg += "|"  # Delimiter
    binary_msg = message_to_binary(encrypted_msg)
    msg_len = len(binary_msg)
    h, w, _ = img.shape
    total_pixels = h * w * 3

    if msg_len > total_pixels:
        st.error("Message is too long to hide in the image!")
        return None

    idx = 0
    for i in range(h):
        for j in range(w):
            for k in range(3):
                if idx < msg_len:
                    img[i, j, k] = (img[i, j, k] & ~1) | int(binary_msg[idx])
                    idx += 1
    return Image.fromarray(img)

# ✅ Decrypt message from image
def decrypt(image, password):
    img = np.array(image)
    binary_msg = ""

    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            for k in range(3):
                binary_msg += str(img[i, j, k] & 1)
    
    message = binary_to_message(binary_msg)
    message = message.split('|')[0]  # Stop at delimiter
    return xor_decrypt(message, password)  # Decrypt with password

# ✅ Streamlit UI
st.title("🔒 Image Steganography App")
st.subheader("Secure your messages inside images!")

option = st.radio("Choose an option:", ("Encrypt Message", "Decrypt Message"))

if option == "Encrypt Message":
    uploaded_image = st.file_uploader("📂 Upload an image", type=["png", "jpg", "jpeg"])
    message = st.text_area("📝 Enter secret message")
    password = st.text_input("🔑 Enter password", type="password", placeholder="Set a password")

    if st.button("🔒 Encrypt and Download"):
        if uploaded_image and message and password:
            image = Image.open(uploaded_image)
            encrypted_image = encrypt(image, message, password)
            if encrypted_image:
                buf = BytesIO()
                encrypted_image.save(buf, format="PNG")
                st.download_button(label="📥 Download Encrypted Image", data=buf.getvalue(), file_name="encrypted_image.png", mime="image/png")
        else:
            st.error("🚨 Please upload an image, enter a message, and set a password!")

elif option == "Decrypt Message":
    uploaded_image = st.file_uploader("📂 Upload the encrypted image", type=["png", "jpg", "jpeg"])
    password = st.text_input("🔑 Enter password", type="password", placeholder="Enter the password for decryption")

    if st.button("🔓 Decrypt"):
        if uploaded_image and password:
            image = Image.open(uploaded_image)
            decrypted_message = decrypt(image, password)
            st.success(f"🛡️ Decrypted Message: {decrypted_message}")
        else:
            st.error("🚨 Please upload an encrypted image and enter the password!")
