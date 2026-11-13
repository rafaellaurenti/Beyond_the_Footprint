@echo off
REM Reproduces revision 1 end to end (Windows Command Prompt or Anaconda Prompt).
cd /d "%~dp0"
python scripts\revision_model.py data results || exit /b 1
python scripts\make_figures.py results figures || exit /b 1
python scripts\make_supplement.py . supplementary || exit /b 1
python scripts\check_run.py . || exit /b 1
