4주차 실습 정리

오늘의 목표:
원형 / AABB / OBB Bounding Box 시각화
세 방식의 충돌 판정 차이 관찰

관찰:

1.원형 vs AABB
(직접 관찰한 내용 작성)


2.AABB vs OBB
(직접 관찰한 내용 작성


3.AI와의 대화에서 배운 것:


4.내 게임에 적용한다면
(어떤 방식을 쓸 것인지, 이유는?)


+5.만드는 도중 발생한 오류와 해결방법

오류메시지 : 'float' object is not subscriptable

AI의 답변:sat_collision 함수에서 변수 이름이 겹쳐져서 발생하는 오류
points 리스트를 사용하고 있었으나 for문 내에서 tuple로 바뀌어서
오류가 발생함.

해결방안:변수 이름을 분리함으로서 해결함.
