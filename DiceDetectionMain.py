import math
import sys
import cv2
import numpy as np
from statistics import mean

amount_of_pictures = 14
header = 'd'


def adjust_gamma(image, gamma):
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")

    return cv2.LUT(image, table)


def scale_contour(cnt, scale):
    M = cv2.moments(cnt)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])

    cnt_norm = cnt - [cx, cy]
    cnt_scaled = cnt_norm * scale
    cnt_scaled = cnt_scaled + [cx, cy]
    cnt_scaled = cnt_scaled.astype(np.int32)

    return cnt_scaled


def main():
    i = 0
    thresh = 195
    # min_threshold = 10  # these values are used to filter our detector.
    # max_threshold = 100  # they can be tweaked depending on the camera distance, camera angle, ...
    # min_area = 20  # ... focus, brightness, etc.
    # min_circularity = 0.3
    # min_inertia_ratio = 0.5

    while True:
        image_name = 'Dices nr ' + str(i + 1)
        cv2.namedWindow(image_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(image_name, 900, 600)
        cv2.moveWindow(image_name, 600, 100)

        image_name_original = 'Original dices nr ' + str(i + 1)
        cv2.namedWindow(image_name_original, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(image_name_original, 450, 300)
        cv2.moveWindow(image_name_original, 0, 100)

        original_image = cv2.imread('src\\' + header + str(i + 1) + '.jpg', cv2.IMREAD_COLOR)
        gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        blurred_image = cv2.GaussianBlur(gray_image, (15, 15), 0)
        thresh_image = cv2.adaptiveThreshold(blurred_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 1)
        kernel = np.ones((5, 5), np.uint8)
        eroded_image = cv2.erode(thresh_image, kernel, iterations=1)
        dilated_image = cv2.dilate(eroded_image, kernel, iterations=4)
        contours, hierarchy = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for j in range(len(contours)):
            area = cv2.contourArea(contours[j])
            perimeter = cv2.arcLength(contours[j], True)
            contours[j] = scale_contour(contours[j], 1.15)
            if perimeter == 0:
                break
            circularity = 4 * math.pi * (area / (perimeter * perimeter))
            if 0.6 < circularity and 1000 < area < 6000:
                x = []
                y = []
                color = []
                for k in range(len(contours[j])):
                    x.append(contours[j][k][0][1])
                    y.append(contours[j][k][0][0])
                    color.append(int(gray_image[contours[j][k][0][1], contours[j][k][0][0]]))
                if int(gray_image[mean(x), mean(y)]) < 150 and mean(color) > 100:
                    print(mean(color))
                    cv2.drawContours(original_image, contours, j, (0, 0, 255), 7)
                    if hierarchy[0][j][3] >= 0 > hierarchy[0][j][2]:
                        cv2.drawContours(original_image, contours, hierarchy[0][j][3], (255, 0, 0), 5)
                    # potential_dots.append(contours[j])
        contours2, hierarchy2 = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for j in range(len(contours)):
            area = cv2.contourArea(contours2[j])
            if area > 6000:
                cv2.drawContours(gray_image, contours2, j, (255, 0, 0), 5)
        cv2.imshow(image_name, original_image)
        cv2.imshow(image_name_original, dilated_image)
        key = cv2.waitKey(0)
        if key == 27:  # ESCAPE
            sys.exit()
        elif key == 100:  # D
            if i < amount_of_pictures - 1:
                i = i + 1
            else:
                i = 0
        elif key == 97:  # A
            if i != 0:
                i = i - 1
            else:
                i = amount_of_pictures - 1
        elif key == 101:  # E
            thresh = thresh + 5
            print('thresh = ', thresh)
        elif key == 113:  # Q
            thresh = thresh - 5
            print('thresh = ', thresh)
        else:
            print("A/D - change image ")
            print("-----------------------")
            (print("Q/E - change thresh"))

        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()