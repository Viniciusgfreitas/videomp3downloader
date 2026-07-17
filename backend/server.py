#!/usr/bin/env python3
"""Backend do Video MP3 Downloader.

Recebe um link do YouTube, extrai o áudio com yt-dlp, converte para MP3
com ffmpeg e devolve o arquivo para download. Implementado apenas com a
biblioteca padrão do Python (http.server) para não depender de pip.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8000"))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAX_DURATION_SECONDS = 20 * 60  # limite de 20 min por vídeo
SUBPROCESS_TIMEOUT = 300  # 5 min

ALLOWED_HOSTS = {
    "www.youtube.com", "youtube.com", "music.youtube.com",
    "youtu.be", "m.youtube.com",
}


def _ffmpeg_location():
    local_ffmpeg = os.path.join(BASE_DIR, "bin", "ffmpeg")
    if os.path.isfile(local_ffmpeg):
        return os.path.join(BASE_DIR, "bin")
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return os.path.dirname(system_ffmpeg)
    return None


def _yt_dlp_binary():
    # Prioriza o binário baixado por setup.sh: o YouTube muda com frequência
    # e a versão empacotada no sistema costuma ficar desatualizada e falhar
    # com "No video formats found!".
    local_bin = os.path.join(BASE_DIR, "bin", "yt-dlp")
    if os.path.isfile(local_bin) and os.access(local_bin, os.X_OK):
        return [local_bin]
    system_bin = shutil.which("yt-dlp")
    if system_bin:
        return [system_bin]
    return None


FFMPEG_LOCATION = _ffmpeg_location()
YT_DLP_BIN = _yt_dlp_binary()


def is_valid_youtube_url(url):
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme not in ("http", "https"):
        return False
    return parsed.netloc in ALLOWED_HOSTS


def safe_filename(name):
    name = re.sub(r"[^\w\-. ]", "_", name).strip()
    return name[:150] or "audio"


class DownloadError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def _run_yt_dlp(args, timeout=SUBPROCESS_TIMEOUT):
    try:
        return subprocess.run(
            YT_DLP_BIN + args,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise DownloadError("Tempo limite excedido ao processar o vídeo.", status=504)


def download_audio(url, workdir):
    if FFMPEG_LOCATION is None:
        raise DownloadError(
            "ffmpeg não encontrado no servidor. Rode backend/setup.sh.", status=500,
        )
    if YT_DLP_BIN is None:
        raise DownloadError(
            "yt-dlp não encontrado no servidor. Rode backend/setup.sh.", status=500,
        )

    info_proc = _run_yt_dlp(
        ["--no-playlist", "--no-warnings", "--dump-single-json", url]
    )
    if info_proc.returncode != 0:
        raise DownloadError(
            f"Não foi possível ler informações do vídeo: {info_proc.stderr.strip()[-500:]}"
        )

    try:
        info = json.loads(info_proc.stdout)
    except json.JSONDecodeError:
        raise DownloadError("Resposta inesperada do yt-dlp ao ler o vídeo.", status=500)

    duration = info.get("duration") or 0
    if duration and duration > MAX_DURATION_SECONDS:
        raise DownloadError(
            f"Vídeo muito longo ({duration // 60} min). "
            f"O limite é {MAX_DURATION_SECONDS // 60} min."
        )
    title = info.get("title") or info.get("id") or "audio"

    outtmpl = os.path.join(workdir, "%(id)s.%(ext)s")
    download_proc = _run_yt_dlp([
        "--no-playlist",
        "--no-warnings",
        "-f", "bestaudio/best",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--ffmpeg-location", FFMPEG_LOCATION,
        "-o", outtmpl,
        url,
    ])
    if download_proc.returncode != 0:
        raise DownloadError(
            f"Não foi possível baixar este vídeo: {download_proc.stderr.strip()[-500:]}"
        )

    for fname in os.listdir(workdir):
        if fname.endswith(".mp3"):
            return os.path.join(workdir, fname), safe_filename(title) + ".mp3"

    raise DownloadError("Falha ao gerar o arquivo MP3.", status=500)


class Handler(BaseHTTPRequestHandler):
    server_version = "VideoMP3Downloader/1.0"

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Expose-Headers", "Content-Disposition")

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/health":
            self._send_json(200, {
                "status": "ok",
                "ffmpeg": FFMPEG_LOCATION is not None,
                "yt_dlp": YT_DLP_BIN is not None,
            })
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/download":
            self._send_json(404, {"error": "not found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        if length <= 0 or length > 10_000:
            self._send_json(400, {"error": "Corpo da requisição inválido."})
            return

        try:
            data = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            self._send_json(400, {"error": "JSON inválido."})
            return

        url = (data.get("url") or "").strip()
        if not url or not is_valid_youtube_url(url):
            self._send_json(400, {"error": "Informe um link válido do YouTube."})
            return

        workdir = tempfile.mkdtemp(prefix="ytmp3_", dir=tempfile.gettempdir())
        try:
            filepath, filename = download_audio(url, workdir)
            filesize = os.path.getsize(filepath)

            self.send_response(200)
            self._set_cors_headers()
            self.send_header("Content-Type", "audio/mpeg")
            self.send_header("Content-Length", str(filesize))
            self.send_header(
                "Content-Disposition", f'attachment; filename="{filename}"'
            )
            self.end_headers()

            with open(filepath, "rb") as f:
                shutil.copyfileobj(f, self.wfile)
        except DownloadError as exc:
            self._send_json(exc.status, {"error": exc.message})
        except BrokenPipeError:
            pass
        except Exception as exc:  # noqa: BLE001
            self._send_json(500, {"error": f"Erro interno: {exc}"})
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    def log_message(self, fmt, *args):
        print(f"[{self.address_string()}] {fmt % args}")


def main():
    if FFMPEG_LOCATION is None or YT_DLP_BIN is None:
        print("AVISO: dependências ausentes. Rode ./setup.sh antes de usar o servidor.")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Servidor rodando em http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
