# Final Project — NYC Taxi Lakehouse (Starter)

Hạ tầng dựng sẵn cho đồ án cuối khoá **Big Data Engineering**. Học viên **tự thiết
kế và cài đặt toàn bộ ETL pipeline** theo **Medallion Architecture** trên **Delta
Lake**, orchestrate bằng **Airflow**.

> Repo này **chỉ cung cấp hạ tầng + luồng nạp dữ liệu**. Không có lời giải, không có
> khung code ETL, không có cấu trúc thư mục theo tầng bronze/silver/gold — phần đó
> là bài làm để chấm điểm.

---

## 1. Kiến trúc

```
                         ┌─────────────────────────────────────────────┐
   NYC TLC (download)    │                DELTA LAKE                   │
        │                │        file:///data/lakehouse/...           │
        ▼                │   (bạn tự thiết kế bronze / silver / gold)  │
  /data/raw/             └─────────────────────────────────────────────┘
   ├── yellow/*.parquet ──[trip-producer]──▶ Kafka topic  ──▶ [Spark Structured
   │      (FACT, nặng)         (replay)        "yellow_trips"      Streaming của BẠN]
   │
   └── dims/*.csv  ───────────────────────────────────────▶ [Spark batch của BẠN]
          (zone, payment_type, rate_code, vendor — nhẹ)

   Orchestration: Airflow   |   Khám phá tương tác: JupyterLab
```

- **FACT (nặng)**: đọc từ **Kafka** bằng **Spark Structured Streaming**.
- **DIM (nhẹ)**: để ở tầng raw, dùng **batch load** đọc từ CSV.
- Storage = **local shared volume** `./data`, mount vào Spark, Jupyter, Airflow tại `/data`.
- **Delta Lake VÀ Apache Iceberg** + Kafka connector đã **bake sẵn** trong image
  Spark/Jupyter/Airflow — không cần `--packages`. Học viên **tự chọn** dùng Delta
  hoặc Iceberg cho các bảng medallion (xem mục [Chọn Delta hay Iceberg](#table-format)).

## 2. Thành phần & cổng

| Service | URL / cổng | Ghi chú |
|---|---|---|
| Redpanda (Kafka API) | `localhost:19092` (host), `redpanda:9092` (trong mạng) | Broker Kafka-compatible |
| Redpanda Console | http://localhost:8080 | Xem topic / message |
| Spark Master UI | http://localhost:8081 | `spark://spark-master:7077` |
| Spark Worker UI | http://localhost:8082 | scale bằng `--scale spark-worker=N` |
| JupyterLab | http://localhost:8888 | không cần token |
| Airflow | http://localhost:8085 | đăng nhập `admin` / `admin` |

## 3. Yêu cầu

- Docker + Docker Compose v2 (macOS/Linux: Docker Engine/Desktop; **Windows: Docker Desktop với backend WSL2**)
- Cấp cho Docker tối thiểu ~6 GB RAM (Spark + Airflow + Kafka)
- Có mạng ở **lần build đầu** (kéo image + jar). Sau đó chạy offline được.

> **Windows** — đọc mục [Chạy trên Windows](#windows) trước khi bắt đầu.

## <a id="windows"></a>Chạy trên Windows

Toàn bộ thành phần nặng chạy trong container Linux, nên máy Windows chỉ cần Docker.
Chỉ cần tránh 3 điểm sau là chạy mượt như trên Linux/Mac:

**Khuyến nghị (mượt nhất): dùng WSL2**

1. Cài **Docker Desktop** và bật **Settings → General → Use the WSL 2 based engine**.
2. Cài một distro Linux: mở PowerShell → `wsl --install -d Ubuntu`.
3. **Đặt project TRONG filesystem của WSL2**, ví dụ `~/lakehouse-starter` (KHÔNG để trong
   `C:\Users\...` rồi truy cập qua `/mnt/c/...` — bind mount qua `/mnt/c` **chậm** và dễ
   lỗi khoá file khi Spark ghi Delta).
4. Trong terminal Ubuntu: `sudo apt install make` rồi dùng `make build`, `make up`, ...
   giống hệt hướng dẫn Linux/Mac bên dưới.

**Nếu chạy thẳng trên PowerShell (không vào WSL shell)**

- Không có `make` → dùng script kèm sẵn **`run.ps1`**:
  ```powershell
  .\run.ps1 build
  .\run.ps1 up
  .\run.ps1 download -Year 2024 -Month 01
  .\run.ps1 produce --limit 200000 --delay 0.2
  .\run.ps1 down        #  .\run.ps1 clean  để xoá volume
  ```
  Nếu PowerShell chặn chạy script: `Set-ExecutionPolicy -Scope Process RemoteSigned`.

**Line endings (CRLF)** — repo đã kèm `.gitattributes` ép LF. Nếu bạn `git clone`, Git sẽ
tự giữ LF cho script/compose. **Đừng** tự đổi các file `.sh`/`.conf`/`Dockerfile`/`.env`/
`docker-compose.yml`/`Makefile` sang CRLF (sẽ gây lỗi `$'\r': command not found`). Nếu tải
về dạng ZIP thì không cần lo.

**RAM** — mở Docker Desktop kiểm tra đã cấp đủ ~6 GB. Với WSL2 có thể giới hạn RAM trong
`C:\Users\<user>\.wslconfig` nếu máy yếu.

## 4. Bắt đầu

> Windows dùng PowerShell: thay `make <x>` bằng `.\run.ps1 <x>` (xem mục trên).

```bash
# 1) Build image (lần đầu hơi lâu do tải Spark/Delta/Kafka jar)
make build          # hoặc: docker compose build

# 2) Bật cluster
make up             # hoặc: docker compose up -d
make ps

# 3) Tải 1 tháng dữ liệu về /data/raw (đổi YEAR/MONTH tuỳ ý)
make download YEAR=2024 MONTH=01

# 4) Bơm dữ liệu FACT vào Kafka (giả lập stream). Mở terminal riêng:
make produce                              # tốc độ mặc định
make produce ARGS="--delay 0.2 --limit 200000"   # nhanh hơn / giới hạn số dòng

# Dừng / xoá
make down           # giữ dữ liệu
make clean          # xoá luôn volume (Airflow DB, Kafka)
```

Kiểm tra nhanh: mở **Redpanda Console** (http://localhost:8080) → thấy topic
`yellow_trips` có message; mở **Spark Master UI** (http://localhost:8081) → thấy 1
worker `ALIVE`.

## 5. Dataset

**NYC TLC — Yellow Taxi Trip Records** (nguồn: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

Sau khi `make download`, `/data/raw` gồm:

| Đường dẫn | Nội dung | Vai trò gợi ý |
|---|---|---|
| `yellow/yellow_tripdata_YYYY-MM.parquet` | ~3 triệu chuyến/tháng, 19 cột | **nguồn FACT** (được replay vào Kafka) |
| `dims/taxi_zone_lookup.csv` | 265 zone → Borough / Zone / service_zone | dimension |
| `dims/payment_type.csv` | mã hình thức thanh toán | dimension |
| `dims/rate_code.csv` | mã loại cước | dimension |
| `dims/vendor.csv` | mã nhà cung cấp thiết bị | dimension |

Cột chính của trip record: `tpep_pickup_datetime`, `tpep_dropoff_datetime`,
`passenger_count`, `trip_distance`, `PULocationID`, `DOLocationID`, `payment_type`,
`RatecodeID`, `VendorID`, `fare_amount`, `tip_amount`, `tolls_amount`,
`total_amount`, ...

**Lưu ý về chất lượng dữ liệu** (data thật, có nhiễu — bạn phải xử lý ở tầng làm
sạch): tồn tại `trip_distance <= 0`, `total_amount < 0`, `passenger_count` null,
pickup ngoài khoảng tháng, và các mã lạ (`payment_type = 0`, `RatecodeID = 99`).
Dữ liệu **không có** `driver_id` và **không có** khoá chính tự nhiên cho từng chuyến.

## <a id="table-format"></a>Chọn Delta hay Iceberg

Cả hai đã cấu hình sẵn trên cluster — chọn **một** (hoặc thử cả hai). Không cần
`--packages`, không cần chỉnh config.

**Delta Lake** — dùng catalog mặc định hoặc ghi theo đường dẫn:
```python
(df.write.format("delta")
   .mode("append")
   .save("file:///data/lakehouse/bronze/taxi_trips"))

spark.read.format("delta").load("file:///data/lakehouse/bronze/taxi_trips")
# SQL: CREATE TABLE t (...) USING delta LOCATION 'file:///data/lakehouse/...';
#      MERGE INTO ... ;  SELECT ... VERSION AS OF 3 ;
```

**Apache Iceberg** — dùng catalog tên `iceberg` (`iceberg.<db>.<table>`), kho lưu ở
`file:///data/lakehouse/iceberg`:
```python
df.writeTo("iceberg.bronze.taxi_trips").using("iceberg").createOrReplace()
spark.table("iceberg.bronze.taxi_trips")
# SQL: CREATE TABLE iceberg.silver.trips (...) USING iceberg;
#      MERGE INTO iceberg.silver.trips ... ;
#      SELECT ... FROM iceberg.silver.t VERSION AS OF <snapshot_id> ;
#      CALL iceberg.system.rewrite_data_files(table => 'silver.trips');
```

> Streaming ghi ra format nào cũng được: Delta hỗ trợ `writeStream.format("delta")`;
> Iceberg thường dùng `foreachBatch` để `MERGE`/ghi vào bảng Iceberg. Điểm chấm
> **không** ưu tiên format nào — chọn cái bạn hiểu rõ và dùng đúng.

## 6. Mục tiêu (mức khái niệm — bạn tự hiện thực hoá)

Xây dựng lakehouse theo **Medallion** trên Delta Lake, tối thiểu:

- **Bronze**: nạp thô, giữ nguyên bản ghi + metadata ingest.
- **Silver**: làm sạch, chuẩn hoá kiểu, khử trùng lặp, chuẩn hoá thành mô hình dùng được.
- **Gold**: mô hình **star schema** phục vụ phân tích, gồm bảng **fact** (grain = 1
  chuyến) và các bảng **dimension** (thời gian, khu vực/zone, hình thức thanh toán,
  loại cước, nhà cung cấp...), cùng vài bảng tổng hợp business-ready.

Ràng buộc kỹ thuật:

- Bảng **fact** phải được nạp qua **Spark Structured Streaming đọc từ Kafka** (topic
  `yellow_trips`), ghi ra bảng **Delta hoặc Iceberg** (bạn tự chọn).
- Các bảng **dimension** nạp bằng **batch** từ `/data/raw/dims`.
- Toàn bộ pipeline được điều phối bằng **Airflow** (DAG do bạn tự dựng trong `dags/`).
- Khuyến khích khai thác đặc tính của table format đã chọn: `MERGE INTO` (upsert),
  time travel / snapshot, compaction (`OPTIMIZE` của Delta hoặc `rewrite_data_files`
  của Iceberg), schema evolution.

## 7. Nộp bài & tiêu chí chấm

Đặt DAG trong `dags/`, notebook (nếu có) trong `notebooks/`, Spark job trong thư
mục con của `dags/` (được mount vào container airflow) hoặc nơi bạn tự tổ chức.

Gợi ý trọng số chấm:

1. **Kiến trúc Medallion** rõ ràng, đúng trách nhiệm từng tầng.
2. **Fact streaming** từ Kafka chạy đúng, ghi Delta, xử lý được trùng lặp/lỗi.
3. **Star schema** hợp lý (fact/dim, grain rõ, khoá thay thế).
4. **Chất lượng dữ liệu** ở Silver (làm sạch các case nhiễu nêu trên).
5. **Orchestration** trên Airflow: phụ thuộc giữa task, chạy lặp lại được (idempotent).
6. **Khai thác Delta**: upsert / time travel / compaction.
7. Tài liệu ngắn mô tả thiết kế & cách chạy.

## 8. Mẹo kết nối

- **Notebook → cluster**: chỉ cần
  ```python
  from pyspark.sql import SparkSession
  spark = SparkSession.builder.appName("explore").getOrCreate()
  ```
  Session tự nối `spark://spark-master:7077`, **Delta và Iceberg đều bật sẵn**. Đọc
  Kafka bằng `spark.readStream.format("kafka").option("kafka.bootstrap.servers","redpanda:9092")...`.
- **Airflow → Spark**: dùng `SparkSubmitOperator` với connection `spark_default`
  (đã cấu hình sẵn tới `spark://spark-master:7077`, client mode). File job đặt trong
  thư mục được mount vào `/opt/airflow/...`.
- **Đọc/ghi table**: Delta dùng đường dẫn `file:///data/lakehouse/...`; Iceberg dùng
  catalog `iceberg.<db>.<table>` (kho ở `file:///data/lakehouse/iceberg`). Mọi node
  đều thấy chung qua volume `/data`.

## 9. Cấu trúc repo

```
lakehouse-starter/
├── docker-compose.yml        # toàn bộ service
├── .env                      # tài nguyên spark-worker
├── .gitattributes            # ép LF (an toàn cho Windows)
├── Makefile                  # lệnh tắt Linux/Mac (build/up/down/download/produce)
├── run.ps1                   # lệnh tắt tương đương cho Windows PowerShell
├── images/
│   ├── spark/                # Spark 3.5.3 + Delta + Iceberg + Kafka connector
│   ├── jupyter/              # JupyterLab trên cùng base Spark
│   └── airflow/              # Airflow + spark-submit + Delta + Iceberg
├── ingestion/                # download_data.py + produce_trips.py (PROVIDED)
├── dags/                     # ← DAG của bạn (đang trống)
├── notebooks/                # ← notebook của bạn (đang trống)
└── data/                     # shared volume: raw/ + lakehouse/ (tạo lúc chạy)
```

## 10. Phiên bản

Spark 3.5.3 · Delta Lake 3.2.1 · Apache Iceberg 1.7.2 · Airflow 2.10.3 ·
Redpanda 24.2 (Kafka API) · PostgreSQL 18 · Python 3.11/3.12.
