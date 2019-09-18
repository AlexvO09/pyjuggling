import cv2
from juggling.circle_detector import ColorCircleDetector


images = ["../tests/samples/photo_reddish_ball_01.jpg",
          "../tests/samples/photo_reddish_ball_02.jpg",
          "../tests/samples/photo_reddish_ball_03.jpg",
          "../tests/samples/photo_reddish_ball_04.jpg"]

count = [1, 1, 1, 2]

for i in range(len(images)):
    path = images[i]
    amount = count[i]

    image = cv2.imread(path)
    circles = ColorCircleDetector(image).get(amount)
    if circles is not None:
        for circle in circles:
            x, y, r = circle[0], circle[1], circle[2] * 2
            cv2.rectangle(image, (x - r, y - r), (x + r, y + r), (0, 255, 0), thickness=2)

        cv2.imshow("Result", image)
        cv2.waitKey(0)