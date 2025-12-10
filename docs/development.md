# Development: Docker and Environment (EN & AR)

This document contains quick instructions to run the API locally using Docker, troubleshoot common problems and use a helper script to reset the environment.

## Quick English How-to

1. Choose DB mode
   - Use containerized Postgres (recommended for dev): set `POSTGRES_HOST=db`. This will use the `db` service defined in `docker-compose.yml`.
   - Use host Postgres (Windows): set `POSTGRES_HOST=host.docker.internal` and ensure a Postgres server runs on the host and accepts connections.

2. Bring the app up (containerized DB)
   ```powershell
   Copy-Item .env.new .env -Force   # (optional) copy default .env
   docker compose down -v
   docker compose up --build
   ```

3. Troubleshooting
   ```powershell
   docker compose config
   docker compose logs -f web db nginx
   docker compose run --rm web python -c "import os, psycopg2; print(os.environ['DATABASE_URL']); conn=psycopg2.connect(os.environ['DATABASE_URL']); print('connected:', conn.dsn); conn.close()"
   ```

4. Dev helper script
   - Use `./scripts/dev-up.ps1 -ForceReset` to reset volumes, rebuild images and start the stack.

## pgAdmin (optional)
If you prefer a GUI to view and manage the Postgres database, run pgAdmin in a container. The compose file includes a `pgadmin` service at port 5050 by default.

1) Start services (pgAdmin will start as well):
```powershell
docker compose up --build
```

2) Open pgAdmin in your browser:
```text
http://localhost:5050
```

3) Login credentials (defaults):
- Email: admin@local
- Password: admin
> Note: pgAdmin requires a valid email address (e.g., `admin@localhost` or `admin@example.com`).
> If you keep a short invalid value like `admin@local`, pgAdmin will exit with a validation error.
> To override defaults safely, add variables to `.env`:
```dotenv
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=StrongPass123
```

4) Add a new server in pgAdmin with the following settings:
 - Host: `db` (if using the containerized Postgres)
 - Port: `5432`
 - Maintenance DB: `kanban`
 - Username: `postgres` (or your `POSTGRES_USER`)
 - Password: `2318147` (or your `POSTGRES_PASSWORD`)

If you wish to connect to a Postgres instance running on your host (outside Docker), set `POSTGRES_HOST=host.docker.internal` in `.env` and update pgAdmin's connection host to that value.

---

# التعليمات بالعربي

إليك خطوات سريعة لتشغيل المشروع محلياً باستخدام Docker وحل المشاكل الشائعة:

1) اختيار مكان قاعدة البيانات
  - استخدام قاعدة بيانات داخل الحاويات (مستحسن للتطوير): اجعل `POSTGRES_HOST=db` في `.env`.
  - استخدام قاعدة بيانات على الجهاز المضيف (Windows): اجعل `POSTGRES_HOST=host.docker.internal` وتأكّد أن خدمة Postgres تعمل وتقبل الاتصالات.

2) لإعادة التشغيل والبدء مع قاعدة بيانات داخل الحاويات
```powershell
Copy-Item .env.new .env -Force
docker compose down -v
docker compose up --build
```

3) أوامر تشخيص سريعة
```powershell
docker compose config
docker compose logs -f web db nginx
docker compose run --rm web python -c "import os, psycopg2; print(os.environ['DATABASE_URL']); conn=psycopg2.connect(os.environ['DATABASE_URL']); print('connected:', conn.dsn); conn.close()"
```

4) سكربت للمطوّر (PowerShell)
```powershell
./scripts/dev-up.ps1 -ForceReset
```

ملاحظة مهمة: قد تحذف هذه الأوامر بياناتك المحلية إذا قمت بإزالة الـ volumes (`down -v`). استخدم ذلك فقط إذا لم تكن تحتاج إلى البيانات الحالية أو إن كنت تعمل في بيئة تطوير محلية.
