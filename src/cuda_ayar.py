import os
import sys
from pathlib import Path

# pip ile kurulan NVIDIA kütüphanelerinin bulunduğu klasör
nvidia_klasoru = Path(sys.prefix) / "Lib" / "site-packages" / "nvidia"

# cublas ve cudnn'in DLL dosyalarını Windows'un arama yoluna (PATH) ekle
for kutuphane in ["cublas", "cudnn"]:
    dll_klasoru = nvidia_klasoru / kutuphane / "bin"
    if dll_klasoru.exists():
        os.environ["PATH"] = str(dll_klasoru) + os.pathsep + os.environ["PATH"]