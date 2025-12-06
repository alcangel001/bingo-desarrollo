import qrcode

# Data for QR code
data = "https://bingoyrifajym.com"

# Create QR code instance
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)

# Add data
qr.add_data(data)
qr.make(fit=True)

# Create an image from the QR Code instance
img = qr.make_image(fill_color="black", back_color="white")

# Save it
img.save("bingo_jym_qr.png")
print("QR code generated: bingo_jym_qr.png")
