from shapely.geometry import Polygon

# 폴리곤 좌표 정의
polygon1_coords = [[0, 0], [3, 0], [6, 3], [3, 6], [0, 6]]
polygon2_coords = [[3, 0], [6, 0]]

# shapely Polygon 객체 생성
polygon1 = Polygon(polygon1_coords)
polygon2 = Polygon(polygon2_coords)

# 겹치는 영역(교집합)의 면적 계산
intersection_area = polygon1.intersection(polygon2).area

# 두 영역의 합집합 영역 계산
union_area = polygon1.union(polygon2).area

print("Intersection Area:", intersection_area)
print("Union Area:", union_area)
