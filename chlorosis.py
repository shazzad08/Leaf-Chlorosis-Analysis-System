import cv2
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def analyze_image(image_path, output_folder="outputs"):
    os.makedirs(output_folder, exist_ok=True)

    image = cv2.imread(image_path)
    image = cv2.resize(image, (300, 300))

    blur = cv2.GaussianBlur(image, (5, 5), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

   
    # GREEN MASK (Leaf)
    
    lower_green = np.array([25, 40, 40])
    upper_green = np.array([90, 255, 255])
    leaf_mask = cv2.inRange(hsv, lower_green, upper_green)
    leaf = cv2.bitwise_and(image, image, mask=leaf_mask)

    
    # YELLOW MASK (Chlorosis)
   
    lower_yellow = np.array([15, 40, 40])
    upper_yellow = np.array([35, 255, 255])
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    yellow_region = cv2.bitwise_and(image, image, mask=yellow_mask)

    
    # PIXEL COUNT
    
    green_pixels = cv2.countNonZero(leaf_mask)
    yellow_pixels = cv2.countNonZero(yellow_mask)

    total = green_pixels + yellow_pixels
    if total == 0:
        return None

    chlorosis_index = yellow_pixels / total
    severity = int(chlorosis_index * 100)
    
    
    
    
    total_pixels = green_pixels + yellow_pixels

   
    if total_pixels == 0:
        return None

    
    green_ratio = (green_pixels / total_pixels) * 100
    yellow_ratio = (yellow_pixels / total_pixels) * 100

   
    affected_area = yellow_ratio  

   

    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    intensity_mean = np.mean(gray)

    
    image_pixels = image.shape[0] * image.shape[1]
    leaf_pixels = total_pixels

    confidence = ((leaf_pixels / image_pixels) * 100)-6
    confidence = min(100, confidence)


    
    # CLASSIFICATION
  
    if chlorosis_index < 0.2:
        condition = "Healthy Leaf 🌿"
        recommendation = "No action required ✅"
    elif chlorosis_index < 0.5:
        condition = "Mild Chlorosis  🟡"
        recommendation = "Apply nitrogen-rich fertilizer  🌱"
    else:
        condition = "Severe Chlorosis  🔴"
        recommendation = "Immediate treatment required ⚠️"


    # OVERLAY (RED HIGHLIGHT)
   
    overlay = image.copy()
    overlay[yellow_mask > 0] = [0, 0, 255]
    overlay = cv2.addWeighted(image, 0.7, overlay, 0.3, 0)

    
    # save files 
    
    leaf_path = os.path.join(output_folder, "leaf.png")
    yellow_path = os.path.join(output_folder, "yellow.png")
    hist_path = os.path.join(output_folder, "hist.png")
    overlay_path = os.path.join(output_folder, "overlay.png")

    cv2.imwrite(leaf_path, leaf)
    cv2.imwrite(yellow_path, yellow_region)
    cv2.imwrite(overlay_path, overlay)

    #histogram 
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])

    plt.figure(figsize=(4, 4))
    plt.plot(hist, color='green')
    plt.title("Histogram")
    plt.xlabel("Intensity")
    plt.ylabel("Pixels")

    plt.savefig(hist_path)
    plt.close()
    
   
    return{
    "green_pixels": int(green_pixels),
    "yellow_pixels": int(yellow_pixels),

    "index": round(chlorosis_index, 2),
    "severity": round(chlorosis_index * 100, 2),

   
    "green_ratio": round(green_ratio, 2),
    "yellow_ratio": round(yellow_ratio, 2),
    "affected_area": round(affected_area, 2),
    "intensity_mean": round(float(intensity_mean), 2),
    "confidence": round(confidence, 2),

    
    "condition": condition,
    "recommendation": recommendation,

    #output_images
    "leaf_img": leaf_path,
    "yellow_img": yellow_path,
    "overlay_img": overlay_path,
    "hist_img": hist_path
}