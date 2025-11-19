# README_BUILD_DATASET.md

## 📋 Tổng quan

File `build_dataset.py` cung cấp các cấu trúc dữ liệu và hàm tiện ích để xử lý dữ liệu không gian cho thuật toán **Joinless Co-location Pattern Mining**. File này chuyển đổi dữ liệu CSV thành các cấu trúc dữ liệu phù hợp cho việc khai phá pattern co-location.

## 🎯 Mục đích

File này giúp bạn:

- Load dữ liệu từ file CSV (LasVegas dataset)
- Tổ chức dữ liệu thành các cấu trúc phù hợp với thuật toán
- Xây dựng quan hệ neighbors giữa các instances
- Xây dựng star neighborhoods (cấu trúc cốt lõi cho joinless algorithm)
- Cache kết quả để tránh tính toán lại

---

## 📦 Các Class và Cấu trúc Dữ liệu

### 1. **SpatialInstance**

Một điểm không gian (location point) trong dataset - tương ứng với 1 dòng trong CSV.

**Cấu trúc:**

```python
@dataclass
class SpatialInstance:
    feature: str      # Loại feature (VD: 'A', 'B', 'C')
    instance_id: int  # ID instance duy nhất trong feature đó
    x: float          # Tọa độ X (LocX)
    y: float          # Tọa độ Y (LocY)
    checkin: int      # Số lượng check-in (độ phổ biến)
```

**Ví dụ:**

```python
instance = SpatialInstance(
    feature='A',
    instance_id=1,
    x=23123.01,
    y=21373.436,
    checkin=151
)
```

**Phương thức:**

- `distance_to(other: SpatialInstance) -> float`: Tính khoảng cách Euclidean đến instance khác

---

### 2. **Feature**

Đại diện cho một loại feature và chứa tất cả các instances của loại đó.

**Cấu trúc:**

```python
@dataclass
class Feature:
    name: str                              # Tên feature (VD: 'A')
    instances: List[SpatialInstance]       # Danh sách tất cả instances của feature này
```

**Ví dụ:**

```python
feature_A = Feature(
    name='A',
    instances=[instance1, instance2, instance3, ...]  # Tất cả instances loại 'A'
)
```

**Phương thức:**

- `get_instance_count() -> int`: Trả về số lượng instances của feature này

---

### 3. **NeighborRelation**

Đại diện cho quan hệ láng giềng giữa 2 instances (hai instances gần nhau hơn ngưỡng khoảng cách).

**Cấu trúc:**

```python
@dataclass
class NeighborRelation:
    instance1: SpatialInstance  # Instance thứ nhất
    instance2: SpatialInstance  # Instance thứ hai
    distance: float             # Khoảng cách Euclidean giữa chúng
```

**Ví dụ:**

```python
relation = NeighborRelation(
    instance1=inst_A1,
    instance2=inst_B2,
    distance=150.5  # Khoảng cách < threshold
)
```

---

### 4. **StarNeighborhood** ⭐

Cấu trúc cốt lõi cho thuật toán joinless. Mỗi instance có một "star neighborhood" - tập hợp các neighbors của nó.

**Cấu trúc:**

```python
@dataclass
class StarNeighborhood:
    center_instance: SpatialInstance      # Instance làm tâm
    neighbors: List[SpatialInstance]      # Danh sách các neighbors
```

**Ví dụ:**

```python
star = StarNeighborhood(
    center_instance=inst_A1,
    neighbors=[inst_B2, inst_C3, inst_A5, ...]  # Tất cả neighbors của inst_A1
)
```

**Phương thức:**

- `add_neighbor(neighbor: SpatialInstance)`: Thêm một neighbor vào star
- `get_feature_types() -> Set[str]`: Lấy tập hợp các loại feature trong star neighborhood này

**Ý nghĩa:** Trong thuật toán joinless, thay vì phải join các bảng, ta chỉ cần xem xét star neighborhoods để tìm các clique.

---

### 5. **Clique**

Một clique là một tập các instances mà **mọi cặp** đều là neighbors với nhau. Trong co-location pattern mining, cliques đại diện cho các instances co-location.

**Cấu trúc:**

```python
@dataclass
class Clique:
    instances: List[SpatialInstance]  # Danh sách instances trong clique
```

**Ví dụ:**

```python
clique = Clique(instances=[inst_A1, inst_B2, inst_C3])
# Điều này có nghĩa: inst_A1, inst_B2, inst_C3 đều là neighbors với nhau
```

**Phương thức:**

- `get_feature_pattern() -> Tuple[str, ...]`: Lấy pattern (tập các feature types) trong clique này
- `size() -> int`: Trả về số lượng instances trong clique

---

### 6. **ColocationPattern**

Đại diện cho một pattern co-location - một tập các feature types thường xuất hiện cùng nhau.

**Cấu trúc:**

```python
@dataclass
class ColocationPattern:
    features: Tuple[str, ...]    # Tuple các feature names đã sắp xếp (VD: ('A', 'B', 'C'))
    cliques: List[Clique]        # Tất cả các cliques hỗ trợ pattern này
```

**Ví dụ:**

```python
pattern = ColocationPattern(
    features=('A', 'B', 'C'),  # Pattern gồm 3 features: A, B, C
    cliques=[clique1, clique2, clique3, ...]  # Tất cả cliques chứa A, B, C
)
```

**Phương thức:**

- `participation_ratio(feature: str, total_instances: Dict[str, int]) -> float`: Tính participation ratio cho một feature
- `participation_index(total_instances: Dict[str, int]) -> float`: Tính participation index của pattern (PI = min của tất cả participation ratios)

---

### 7. **SpatialDataset** 📊

Container chính chứa toàn bộ dữ liệu và các cấu trúc đã được xây dựng.

**Cấu trúc:**

```python
@dataclass
class SpatialDataset:
    instances: List[SpatialInstance]                              # Tất cả instances
    features: Dict[str, Feature]                                  # Dict: feature_name -> Feature
    neighbor_relations: Set[NeighborRelation]                     # Tập tất cả quan hệ neighbors
    star_neighborhoods: Dict[SpatialInstance, StarNeighborhood]   # Dict: instance -> StarNeighborhood
    distance_threshold: float                                     # Ngưỡng khoảng cách đã dùng
```

**Phương thức chính:**

- `add_instance(instance: SpatialInstance)`: Thêm instance vào dataset
- `get_feature_instance_count(feature: str) -> int`: Lấy số lượng instances của một feature
- `build_neighbor_relations(threshold: float)`: Xây dựng quan hệ neighbors dựa trên ngưỡng khoảng cách
- `build_star_neighborhoods()`: Xây dựng star neighborhoods từ neighbor relations
- `save_to_file(filepath: str)`: Lưu dataset vào file pickle (để tái sử dụng)
- `load_from_file(filepath: str) -> SpatialDataset`: Load dataset từ file pickle

---

## 🚀 Cách sử dụng

### Cách 1: Sử dụng hàm `load_or_build_dataset` (Khuyến nghị)

Hàm này tự động kiểm tra cache và chỉ build lại khi cần thiết.

```python
from build_dataset import load_or_build_dataset

# Định nghĩa đường dẫn
csv_path = "data/LasVegas_x_y_alphabet_version_03_2.csv"
cache_path = "LasVegas_cache.pkl"
distance_threshold = 160.0  # Ngưỡng khoảng cách

# Load hoặc build dataset
dataset = load_or_build_dataset(
    csv_path=csv_path,
    cache_path=cache_path,
    distance_threshold=distance_threshold,
    force_rebuild=False  # Set True nếu muốn build lại
)

# Sử dụng dataset
print(f"Số lượng instances: {len(dataset.instances)}")
print(f"Số lượng features: {len(dataset.features)}")
print(f"Số lượng neighbor relations: {len(dataset.neighbor_relations)}")
print(f"Số lượng star neighborhoods: {len(dataset.star_neighborhoods)}")
```

**Lần chạy đầu tiên:**

- Load từ CSV
- Build neighbor relations
- Build star neighborhoods
- Lưu vào cache file (`.pkl`)

**Các lần chạy sau:**

- Load từ cache (nhanh hơn nhiều!)
- Chỉ rebuild nếu threshold thay đổi

---

### Cách 2: Tự build từ đầu

Nếu bạn muốn kiểm soát từng bước:

```python
from build_dataset import load_spatial_dataset, SpatialDataset

# 1. Load từ CSV
dataset = load_spatial_dataset("data/LasVegas_x_y_alphabet_version_03_2.csv")

# 2. Build neighbor relations
distance_threshold = 160.0
dataset.build_neighbor_relations(threshold=distance_threshold)

# 3. Build star neighborhoods
dataset.build_star_neighborhoods()

# 4. (Tùy chọn) Lưu vào file để tái sử dụng
dataset.save_to_file("LasVegas_cache.pkl")
```

---

### Cách 3: Load từ file đã lưu

```python
from build_dataset import SpatialDataset

# Load dataset đã được build sẵn
dataset = SpatialDataset.load_from_file("LasVegas_cache.pkl")

# Sử dụng ngay, không cần tính toán lại
print(f"Dataset đã có {len(dataset.star_neighborhoods)} star neighborhoods")
```

---

## 📝 Ví dụ Sử dụng Dataset

### Ví dụ 1: Truy cập instances theo feature

```python
# Lấy tất cả instances của feature 'A'
feature_A = dataset.features['A']
print(f"Feature A có {feature_A.get_instance_count()} instances")

for instance in feature_A.instances:
    print(f"  Instance {instance.instance_id}: ({instance.x}, {instance.y}) - {instance.checkin} check-ins")
```

### Ví dụ 2: Xem star neighborhood của một instance

```python
# Chọn một instance bất kỳ
some_instance = dataset.instances[0]

# Lấy star neighborhood của nó
star = dataset.star_neighborhoods[some_instance]

print(f"Instance {some_instance.feature}{some_instance.instance_id} có {len(star.neighbors)} neighbors:")
for neighbor in star.neighbors:
    print(f"  - {neighbor.feature}{neighbor.instance_id}")

# Xem các loại feature trong star neighborhood
feature_types = star.get_feature_types()
print(f"Các feature types trong star: {feature_types}")
```

### Ví dụ 3: Tìm các neighbor relations

```python
# Xem một số neighbor relations
print(f"Tổng số neighbor relations: {len(dataset.neighbor_relations)}")

# Lấy 5 relations đầu tiên
for i, relation in enumerate(list(dataset.neighbor_relations)[:5]):
    inst1 = relation.instance1
    inst2 = relation.instance2
    print(f"Relation {i+1}: {inst1.feature}{inst1.instance_id} <-> {inst2.feature}{inst2.instance_id} (distance: {relation.distance:.2f})")
```

### Ví dụ 4: Tính toán participation index cho pattern

```python
from build_dataset import ColocationPattern, Clique

# Giả sử bạn đã tìm được một pattern
pattern = ColocationPattern(
    features=('A', 'B', 'C'),
    cliques=[...]  # Danh sách các cliques hỗ trợ pattern này
)

# Tính participation index
total_instances = {
    'A': dataset.get_feature_instance_count('A'),
    'B': dataset.get_feature_instance_count('B'),
    'C': dataset.get_feature_instance_count('C')
}

pi = pattern.participation_index(total_instances)
print(f"Participation Index của pattern {pattern.features}: {pi:.4f}")
```

---

## ⚙️ Tham số quan trọng

### `distance_threshold`

Ngưỡng khoảng cách để xác định 2 instances có phải là neighbors hay không.

- **Giá trị nhỏ:** Ít neighbors hơn, pattern chặt chẽ hơn
- **Giá trị lớn:** Nhiều neighbors hơn, pattern lỏng hơn
- **Gợi ý:** Thử các giá trị như 100.0, 160.0, 200.0, 500.0 và so sánh kết quả

```python
# Ví dụ với các threshold khác nhau
for threshold in [100.0, 160.0, 200.0, 500.0]:
    dataset.build_neighbor_relations(threshold=threshold)
    dataset.build_star_neighborhoods()
    print(f"Threshold {threshold}: {len(dataset.neighbor_relations)} relations")
```

---

## 📂 Cấu trúc File

Sau khi chạy, bạn sẽ có:

```
papers/Joinless/
├── build_dataset.py          # File này
├── LasVegas_cache.pkl        # Cache file (tự động tạo)
└── ...
```

**Lưu ý:** Nên thêm `*.pkl` vào `.gitignore` vì đây là file cache, không cần commit.

---

## 🔍 Giải thích các Khái niệm

### Star Neighborhood là gì?

- Mỗi instance có một "star neighborhood" - tập hợp tất cả các instances khác nằm trong phạm vi `distance_threshold`
- Ví dụ: Nếu instance A có neighbors là B, C, D thì star neighborhood của A = {B, C, D}
- Trong thuật toán joinless, thay vì phải join nhiều bảng, ta chỉ cần xét các star neighborhoods

### Clique là gì?

- Một clique là một tập instances mà **mọi cặp** đều là neighbors
- Ví dụ: Nếu {A, B, C} là một clique thì:
  - A và B là neighbors
  - A và C là neighbors
  - B và C là neighbors
- Cliques đại diện cho các instances thực sự co-location với nhau

### Participation Index (PI) là gì?

- PI đo lường độ phổ biến của một pattern
- PI = min(participation_ratio của tất cả features trong pattern)
- Participation ratio của feature F = (số instances của F trong pattern) / (tổng số instances của F)
- PI càng cao, pattern càng phổ biến

---

## ⚠️ Lưu ý

1. **File cache (.pkl):** Khi bạn thay đổi threshold, file cache sẽ tự động được rebuild nếu threshold khác với cache cũ.

2. **Memory:** Dataset với nhiều instances và threshold lớn có thể tốn nhiều memory. Hãy kiểm tra trước khi chạy với dataset lớn.

3. **Distance threshold:** Giá trị threshold phụ thuộc vào scale của dữ liệu. Dataset LasVegas có tọa độ lớn (~20000-40000), nên threshold 160.0 là hợp lý.

4. **Tính toán neighbor relations:** Hàm `build_neighbor_relations()` có độ phức tạp O(n²), nên với dataset lớn (>10k instances) có thể mất thời gian. Đây là lý do tại sao nên dùng cache!

---

## 📚 Tài liệu tham khảo

- Paper: "A Clique-based Approach for Co-location Pattern Mining" (TKDE 2006)
- Thuật toán Joinless Co-location Pattern Mining
- Khái niệm Star Neighborhood trong spatial data mining

---

## 🤝 Hỗ trợ

Nếu có thắc mắc về cấu trúc dữ liệu hoặc cách sử dụng, hãy xem code comments trong file `build_dataset.py` hoặc liên hệ nhóm phát triển.
