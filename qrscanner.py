import cv2
from pyzbar.pyzbar import decode
import numpy as np
import webbrowser
import time

def list_available_cameras():
    """List all available cameras and their details"""
    available_cameras = []
    for i in range(10): 
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
              
                width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                name = f"Camera {i}: {width}x{height}"
                print(name)
                available_cameras.append(i)
            cap.release()
    return available_cameras

def select_external_camera():
    """Select the external camera (usually index 1 or higher)"""
    cameras = list_available_cameras()
    if len(cameras) > 1:
        return cameras[1]  
    return cameras[0] if cameras else 0

def setup_camera(index):
    """Setup camera with proper configuration"""
    cap = cv2.VideoCapture(index)
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  
    
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    
    print(f"Camera Resolution: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
    
    return cap

def scan_qr_code():
    print("Scanning for cameras...")
    camera_index = select_external_camera()
    
    print(f"Selected camera index: {camera_index}")
    cap = setup_camera(camera_index)

    if not cap.isOpened():
        print("Error: Could not open external camera.")
        return

    cv2.namedWindow('QR Code Scanner (External Camera)', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('QR Code Scanner (External Camera)', 640, 480) 

       
    scanned_links = set()
    last_scan_time = 0
    scan_cooldown = 2

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from external camera.")
            time.sleep(1)
            continue

     
        frame = cv2.resize(frame, (640,480))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        try:
            decoded_objects = decode(blurred)
            current_time = time.time()

            for obj in decoded_objects:
                points = obj.polygon
                if len(points) == 4:
                    pts = np.array(points, np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(frame, [pts], True, (0, 255, 0), 3)

                    decoded_data = obj.data.decode('utf-8')
                    
                    if (decoded_data.startswith("http://") or 
                        decoded_data.startswith("https://")):
                        if (decoded_data not in scanned_links and 
                            current_time - last_scan_time >= scan_cooldown):
                            print(f"Found URL: {decoded_data}")
                            scanned_links.add(decoded_data)
                            last_scan_time = current_time
                            webbrowser.open(decoded_data)

                    cv2.putText(frame, f"Scanned: {decoded_data}", (10, 50),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                              (0, 255, 0), 2)

        except Exception as e:
            print(f"Error in QR detection: {e}")

        cv2.putText(frame, f"Camera Index: {camera_index}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (255, 255, 255), 2)

        cv2.imshow('QR Code Scanner (External Camera)', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            scanned_links.clear()
            print("Reset scanned links")
        elif key == ord('c'): 
            camera_index = (camera_index + 1) % 10
            cap.release()
            cap = setup_camera(camera_index)
            print(f"Switched to camera index: {camera_index}")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        scan_qr_code()
    except Exception as e:
        print(f"Program error: {e}")
        input("Press Enter to exit...")  
