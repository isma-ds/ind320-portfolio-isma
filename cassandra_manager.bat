@echo off
REM Cassandra Cluster Management Script for Windows
REM IND320 Assessment 4

echo ============================================================
echo Cassandra Cluster Manager - IND320 Assessment 4
echo ============================================================
echo.

if "%1"=="" goto :help
if "%1"=="start" goto :start
if "%1"=="stop" goto :stop
if "%1"=="status" goto :status
if "%1"=="logs" goto :logs
if "%1"=="shell" goto :shell
if "%1"=="init" goto :init
if "%1"=="upload" goto :upload
if "%1"=="clean" goto :clean
goto :help

:start
echo [ACTION] Starting Cassandra cluster...
docker-compose up -d
echo.
echo [INFO] Cluster starting. This may take 2-3 minutes.
echo [INFO] Check status with: cassandra_manager.bat status
goto :end

:stop
echo [ACTION] Stopping Cassandra cluster...
docker-compose stop
echo [OK] Cluster stopped
goto :end

:status
echo [STATUS] Checking Cassandra cluster...
echo.
docker-compose ps
echo.
echo [INFO] To see detailed logs: cassandra_manager.bat logs
goto :end

:logs
if "%2"=="" (
    docker-compose logs --tail=50 -f
) else (
    docker-compose logs --tail=50 -f %2
)
goto :end

:shell
echo [SHELL] Connecting to Cassandra node 1...
docker exec -it cassandra1 cqlsh
goto :end

:init
echo [INIT] Initializing Cassandra schema...
echo.
echo Waiting 10 seconds for cluster to be ready...
timeout /t 10 /nobreak >nul
echo.
docker exec -i cassandra1 cqlsh < cassandra-init\init.cql
echo.
echo [OK] Schema initialized
goto :end

:upload
echo [UPLOAD] Uploading data to Cassandra...
echo.
python scripts\upload_to_cassandra.py
goto :end

:clean
echo [WARNING] This will DELETE all Cassandra data and volumes!
echo.
set /p confirm="Are you sure? (yes/no): "
if /i "%confirm%"=="yes" (
    echo [ACTION] Stopping and removing cluster...
    docker-compose down -v
    echo [OK] Cluster and data removed
) else (
    echo [CANCELLED] No changes made
)
goto :end

:help
echo Usage: cassandra_manager.bat [command]
echo.
echo Commands:
echo   start    - Start the Cassandra cluster (3 nodes)
echo   stop     - Stop the Cassandra cluster
echo   status   - Show cluster status
echo   logs     - Show cluster logs (CTRL+C to exit)
echo   shell    - Open CQL shell on node 1
echo   init     - Initialize database schema
echo   upload   - Upload data to Cassandra
echo   clean    - Stop cluster and remove all data (WARNING: destructive)
echo.
echo Example workflow:
echo   1. cassandra_manager.bat start
echo   2. Wait 2-3 minutes for cluster to initialize
echo   3. cassandra_manager.bat status    (verify all nodes running)
echo   4. cassandra_manager.bat init      (create keyspace and tables)
echo   5. cassandra_manager.bat upload    (upload energy data)
echo   6. cassandra_manager.bat shell     (access CQL shell)
goto :end

:end
echo.
