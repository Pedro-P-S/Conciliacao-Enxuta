@echo off
rem Gera dist\ConciliacaoEnxuta\ConciliacaoEnxuta.exe. Precisa do Python 3.11 ou mais novo instalado.
cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
    echo Criando o ambiente Python...
    python -m venv .venv || goto erro
)

echo Instalando os pacotes...
.venv\Scripts\python -m pip install --quiet -r requirements.txt pyinstaller==6.22.3 || goto erro

echo Gerando o executavel (leva uns 2 minutos)...
.venv\Scripts\python -m PyInstaller --noconfirm --clean --windowed --onedir --name ConciliacaoEnxuta --paths . conciliacao_enxuta\__main__.py || goto erro

echo.
echo Pronto: dist\ConciliacaoEnxuta\ConciliacaoEnxuta.exe
echo Leve a pasta dist\ConciliacaoEnxuta inteira, com a _internal junto.
pause
exit /b 0

:erro
echo.
echo Nao deu certo. Veja a mensagem acima.
pause
exit /b 1
