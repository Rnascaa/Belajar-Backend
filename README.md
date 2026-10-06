# To-Do List API

REST API sederhana dengan FastAPI + SQLite.

## Menjalankan

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Buka http://127.0.0.1:8000/docs untuk dokumentasi interaktif.

## Endpoint

| Method | Path | Fungsi |
|--------|------|--------|
| POST | /todos | Buat tugas |
| GET | /todos | Daftar tugas (opsional `?done=true/false`) |
| GET | /todos/{id} | Detail tugas |
| PATCH | /todos/{id} | Ubah sebagian data |
| DELETE | /todos/{id} | Hapus tugas |

## Contoh curl

```bash
curl -X POST localhost:8000/todos -H "Content-Type: application/json" \
  -d '{"title":"Belajar backend","description":"Selesaikan proyek 1"}'

curl localhost:8000/todos
curl -X PATCH localhost:8000/todos/1 -H "Content-Type: application/json" -d '{"done":true}'
curl -X DELETE localhost:8000/todos/1
```

## Tes

```bash
pytest
```
