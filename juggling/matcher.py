from juggling.metric import euclidean


class MatchResult:
    def __init__(self, index_circle, position, next_color):
        self.index_circle = index_circle
        self.next_position = position
        self.next_color = next_color


class Matcher:
    def __init__(self, image_height, image_width, circles):
        self.__height = image_height
        self.__width = image_width

        self.__circles = circles

        self.__max_x = self.__width
        self.__max_y = self.__height
        self.__max_color = [255, 255, 255]
        self.__max_radius = min(self.__height, self.__width) / 2

    def _normalize_features(self, positions, colors):
        result = []
        for i in range(len(positions)):
            if colors is None:
                result.append(self._normalize_same_color_feature(positions[i]))
            else:
                result.append(self._normalize_common_feature(positions[i], colors[i]))

        return result

    def _normalize_feature(self, position, color):
        if color is None:
            return self._normalize_same_color_feature(position)
        else:
            return self._normalize_common_feature(position, color)

    def _normalize_common_feature(self, position, color):
        return [position[0] / self.__width,                          # x
                position[1] / self.__height,                         # y
                position[2] / min(self.__height, self.__width),      # radius
                color[0] / 255,  # R
                color[1] / 255,  # G
                color[2] / 255]  # B

    def _normalize_same_color_feature(self, position):
        return [position[0] / self.__width,                          # x
                position[1] / self.__height]                         # y

    def _check_point_in_area(self, pos_prev, pos, dx, dy, m, r):
        if dx is None or dy is None:
            return True

        if dx * m < r:
            dx = r
        if dy * m < r:
            dy = r

        x_prev, y_prev, x, y = pos_prev[0], pos_prev[1], pos[0], pos[1]
        if (abs(x_prev - x) < dx * m) and (abs(y_prev - y) < dy * m):
            return True
        return False

    def match(self, next_positions, next_colors=None):
        extracted_patterns = self._normalize_features(next_positions, next_colors)

        circle_dissimilarity = []

        for i in range(len(self.__circles)):
            current_circle = self.__circles[i]
            current_pattern = self._normalize_feature(current_circle.get_position(), current_circle.get_color())

            for index_pattern in range(len(extracted_patterns)):
                distance = euclidean(current_pattern, extracted_patterns[index_pattern])
                circle_dissimilarity.append((i, index_pattern, distance))

        circle_dissimilarity.sort(key=lambda descriptor: descriptor[2])

        assigned_patterns = set()
        updated_circles = set()

        result = []
        for item in circle_dissimilarity:
            index_circle = item[0]
            index_pattern = item[1]

            if (index_pattern in assigned_patterns) or (index_circle in updated_circles):
                continue

            # make sure that it is possible in line telemetry
            # if not self._check_point_in_area(self.__circles[index_circle].get_position(),
            #                                  next_positions[index_pattern],
            #                                  self.__circles[index_circle].get_x_telemetry().predict_distance_change(),
            #                                  self.__circles[index_circle].get_y_telemetry().predict_distance_change(),
            #                                  5,
            #                                  self.__circles[index_circle].get_radius()):
            #     continue

            assigned_patterns.add(index_pattern)
            updated_circles.add(index_circle)

            next_color = None
            if next_colors is not None:
                next_color = next_colors[index_pattern]

            result.append(MatchResult(index_circle, next_positions[index_pattern], next_color))

        return result
