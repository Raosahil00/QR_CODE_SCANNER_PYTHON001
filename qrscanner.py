import cv2
from pyzbar.pyzbar import decode
import numpy as np
import webbrowser 

def scan_qr_code():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    scanned_links = set() 
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        decoded_objects = decode(frame)
        for obj in decoded_objects:
            points = obj.polygon
            if len(points) == 4:
                cv2.polylines(frame, [np.array(points)], isClosed=True, color=(0, 255, 0), thickness=2)
                
                decoded_data = obj.data.decode('utf-8')
                print("Decoded Data:", decoded_data)

              
                if decoded_data.startswith("http://") or decoded_data.startswith("https://"):
                    if decoded_data not in scanned_links:
                        scanned_links.add(decoded_data)  
                        print(f"Opening link: {decoded_data}")
                        webbrowser.open(decoded_data) 

        cv2.imshow('QR Code Scanner', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    scan_qr_code()